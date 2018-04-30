import pickle
import collections
import gurobipy as gp
import scipy as sp
import numpy as np
import re
from Crypto.Random import random

#################
#Define functions for importing and exporting pickle files
#################
def importPickle(fileName, mode = 'rb'):
    """
    Imports a pickle object. By default it reads as binary (rb). Setting
    mode allows other ways of opening the file (e.g. mode = 'r')
    """
    f = open(fileName, mode)
    return pickle.load(f)

def exportPickle(obj, fileName, mode = 'wb', protocol = -1):
    """
    Exports an object as a pickle file. By default it writes as binary (wb).
    Setting mode allows other ways of opening the file (e.g. mode = 'w')
    """
    f = open(fileName, mode)
    pickle.dump(obj, f, protocol = -1)
    f.close()

#################
#Define classes used by models
#################
class CbModel():
    """
    Constraint-based model class
    """
    def __init__(self, S, idSp, idRs, lb, ub, rxns = {}, genes = set(),
                 descrip = ''):
        """
        S should be a sparse coo_matrix
        """
        self.S = S
        self.idSp = idSp
        self.idRs = idRs
        self.lb = lb
        self.ub = ub
        self.rxns = rxns
        self.descrip = descrip
        self.genes = genes
        self.gene2rxn = {}
        for rxn in self.rxns:
            self.gene2rxn[rxn] = self.rxns[rxn]['genes']

    def separateFwdRevRxns(self):
        """
        Returns
        modelSep [CbModel instance] reversible reactions separated into 
            fwd and rev
        """
        indRev = [i for i, rxn in enumerate(self.idRs) if (self.lb[i] < 0.) 
                and (self.ub[i] > 0.)]
        indIrrev = [i for i in range(self.S.shape[1]) if i not in indRev]
        # augmenting the stoichiometric matrix
        S = self.S.toarray()
        Srev = -S[:, indRev]
        Saug = np.concatenate((S, Srev), axis = 1)
        # updating idRs, lb and ub
        idRs = self.idRs + [rxn + '_rev' for i, rxn in enumerate(self.idRs) 
                if i in indRev]
        lb = [0. if val <= 0. else val for val in self.lb] + [0.]*len(indRev)
        ub = self.ub + [abs(val) for i, val in enumerate(self.lb) 
                if i in indRev]
        cbmNew = CbModel(sp.sparse.coo_matrix(Saug), self.idSp, idRs, lb, ub,
                descrip = self.descrip + '_fwdAndRevSeparated')
        #species dictionary (unchanged)
        if 'species' in dir(self):
            cbmNew.species = self.species
        #genes set (unchanged)
        if 'genes' in dir(self):
            cbmNew.genes = self.genes
        #reactions dictionary
        if 'rxns' in dir(self):
            rxns = {}
            for rxn in cbmNew.idRs:
                if '_rev' in rxn[-4:]:
                    rxns[rxn] = {}
                    rxns[rxn].update(self.rxns[rxn[:-4]])
                    rxns[rxn]['id'] = rxn
                    rs = rxns[rxn]['reactants']
                    ps = rxns[rxn]['products']
                    rxns[rxn]['reactants'] = ps
                    rxns[rxn]['products'] = rs
                else:
                    rxns[rxn] = self.rxns[rxn]
            cbmNew.rxns = rxns
        return cbmNew 

    def initLp(self, name = 'unnamed'):
        self.guro = gp.Model(name)
        #turning off the writing of the gurobi.log file
        self.guro.setParam('OutputFlag', 0) 
        for i, rxn in enumerate(self.idRs):
            exec('self.{0} = self.guro.addVar(lb = {1}, ub = {2},vtype = gp.GRB.CONTINUOUS, name = "{0}")'.format(rxn, self.lb[i], self.ub[i]))
        self.guro.update()
        # adding constraints
        for i, row in enumerate(self.S.toarray()):
            nz = row.nonzero()[0]
            pair = zip(row[nz], np.array(self.idRs)[nz])
            s = ['({} * self.{})'.format(p[0], p[1]) for p in pair]
            s = ' + '.join(s)
            s += ' == 0.'
            exec('self.guro.addConstr( {}, "{}")'.format(s, self.idSp[i]))

    def setObjective(self, obj, optSense = 'max'):
        s = 'self.{}'.format(obj)
        if optSense == 'max':
            exec('self.guro.setObjective({}, gp.GRB.MAXIMIZE)'.format(s))
        elif optSense == 'min':
            exec('self.guro.setObjective({}, gp.GRB.MINIMIZE)'.format(s))
    
    def solveLp(self):
        self.guro.optimize()
        if self.guro.getAttr('status') == 2:
            self.solObjective = self.guro.objVal
            self.solution = [v.x for v in self.guro.getVars()]
        else:
            self.solObjective = None
            self.solution = []

    def fva(self, rl = []):
        """
        Performs flux variability analysis (FVA)
        """
        if not rl:
            rl = self.idRs
        fv = []
        fvMax = []
        # maximizing each
        for rxn in rl:
            # reseting the objective
            self.guro.setObjective(0)
            exec('self.guro.setObjective(self.{}, gp.GRB.MAXIMIZE)'.format(rxn))
            self.guro.optimize()
            fvMax.append(self.guro.objVal)
        # minimizing each
        fvMin = []
        for rxn in rl:
            # reseting the objective
            self.guro.setObjective(0)
            exec('self.guro.setObjective(self.{}, gp.GRB.MINIMIZE)'.format(rxn))
            self.guro.optimize()
            fvMin.append(self.guro.objVal)
        # getting the lists together
        for i, rxn in enumerate(rl):
            fv.append([rxn, fvMin[i], fvMax[i]])
        return fv

class MetabGeneExpModel(object):

    def __init__(self, idSp, idRs, S, lb, ub, rH, rL, eps = 1E-10):
        """
        idSp [list] strings with the names of species
        idRs [list] strings with the names of reactions
        S [array or coo_matrix] stoichiometry matrix
        lb [list] floats with lower bound values
        ub [list] floats with upper bound values
        rH [list] names of reactions classified as highly expressed
        rL [list] names of reactions classified as lowly expressed
        """
        self.S = sp.sparse.coo_matrix(S)
        self.Srows = [int(i) for i in self.S.row]
        self.Scols = [int(i) for i in self.S.col]
        self.Svals = [float(i) for i in self.S.data]
        self.idSp = idSp
        self.idRs = idRs
        self.lb = lb
        self.lb = lb
        self.ub = ub
        self.eps = eps
        #copying the S for the construction of the lhs
        self.lhsRows = self.Srows[:]
        self.lhsCols = self.Scols[:]
        self.lhsVals = self.Svals[:]
        self.rowNames = self.idSp[:]
        self.colNames = self.idRs[:]
        self.rH = rH
        self.rL = rL
        self.rHrev = [rxn for i, rxn in enumerate(self.idRs) if 
                (self.lb[i] < 0.) and (self.ub[i] > 0.) and (rxn in self.rH)]

    def rowAndColNames(self):
        """
        Adds names for the integer variables and constraints
        """
        for rxn in self.rH:
            self.colNames.append('yp_{}'.format(rxn))
            self.rowNames.append('cp_{}'.format(rxn))
            if rxn in self.rHrev:
                self.colNames.append('ym_{}'.format(rxn))
                self.rowNames.append('cm_{}'.format(rxn))
                #yp + ym <= 1
                self.rowNames.append('cYsum_{}'.format(rxn))        
        for rxn in self.rL:
            self.colNames.append('y_{}'.format(rxn))
            self.rowNames.append('cl_{}'.format(rxn))
            self.rowNames.append('cu_{}'.format(rxn))

    def buildLhsMatrix(self):
        for rxn in self.rH:
            self.lhsRows.append(self.rowNames.index('cp_{}'.format(rxn)))
            self.lhsCols.append(self.colNames.index('yp_{}'.format(rxn)))
            self.lhsVals.append(self.lb[self.colNames.index(rxn)] - self.eps)   
            self.lhsRows.append(self.rowNames.index('cp_{}'.format(rxn)))
            self.lhsCols.append(self.colNames.index(rxn))
            self.lhsVals.append(1)
            if rxn in self.rHrev: 
                self.lhsRows.append(self.rowNames.index('cm_{}'.format(rxn)))
                self.lhsCols.append(self.colNames.index('ym_{}'.format(rxn)))
                self.lhsVals.append(self.ub[self.colNames.index(rxn)] + self.eps)
                self.lhsRows.append(self.rowNames.index('cm_{}'.format(rxn)))
                self.lhsCols.append(self.colNames.index(rxn))
                self.lhsVals.append(1)
                # yp + ym <= 1
                self.lhsRows.append(self.rowNames.index('cYsum_{}'.format(rxn)))
                self.lhsCols.append(self.colNames.index('yp_{}'.format(rxn)))
                self.lhsVals.append(1)
                self.lhsRows.append(self.rowNames.index('cYsum_{}'.format(rxn)))
                self.lhsCols.append(self.colNames.index('ym_{}'.format(rxn)))
                self.lhsVals.append(1)
        
        for rxn in self.rL:
            self.lhsRows.append(self.rowNames.index('cl_{}'.format(rxn)))
            self.lhsCols.append(self.colNames.index('y_{}'.format(rxn)))
            self.lhsVals.append(self.lb[self.colNames.index(rxn)])
            self.lhsRows.append(self.rowNames.index('cl_{}'.format(rxn)))
            self.lhsCols.append(self.colNames.index(rxn))
            self.lhsVals.append(1)
        
            self.lhsRows.append(self.rowNames.index('cu_{}'.format(rxn)))
            self.lhsCols.append(self.colNames.index('y_{}'.format(rxn)))
            self.lhsVals.append(self.ub[self.colNames.index(rxn)])
            self.lhsRows.append(self.rowNames.index('cu_{}'.format(rxn)))
            self.lhsCols.append(self.colNames.index(rxn))
            self.lhsVals.append(1)

    def buildRhsAndSenses(self):
        self.senses = 'E'*len(self.idSp)
        self.rhsRows = []
        self.rhsCols = []
        self.rhsVals = []
        for rxn in self.rH:
            self.rhsRows.append(self.rowNames.index('cp_{}'.format(rxn)))
            self.rhsCols.append(0)
            self.rhsVals.append(self.lb[self.colNames.index(rxn)])
            self.senses += 'G'
            if rxn in self.rHrev: 
                self.rhsRows.append(self.rowNames.index('cm_{}'.format(rxn)))
                self.rhsCols.append(0)
                self.rhsVals.append(self.ub[self.colNames.index(rxn)])
                self.senses += 'L'        
                # yp + ym <= 1
                self.rhsRows.append(self.rowNames.index('cYsum_{}'.format(rxn)))
                self.rhsCols.append(0)
                self.rhsVals.append(1)
                self.senses += 'L'

        for rxn in self.rL:
            self.rhsRows.append(self.rowNames.index('cl_{}'.format(rxn)))
            self.rhsCols.append(0)
            self.rhsVals.append(self.lb[self.colNames.index(rxn)])
            self.senses += 'G'
        
            self.rhsRows.append(self.rowNames.index('cu_{}'.format(rxn)))
            self.rhsCols.append(0)
            self.rhsVals.append(self.ub[self.colNames.index(rxn)])
            self.senses += 'L'
        self.rhs = list(sp.sparse.coo_matrix((self.rhsVals, (self.rhsRows, self.
            rhsCols)), shape = (len(self.rowNames), 1)).toarray().flatten())

class MetabGeneExpModel_gurobi(MetabGeneExpModel):
    """
    Uses gurobi as its milp solver
    """
    def initGurobi(self):
        self.guro = gp.Model('imge')
        #turning off the writing of the gurobi.log file
        self.guro.setParam('OutputFlag', 0) 
        # Initializing variables
        for i, rxn in enumerate(self.idRs):
            exec('self.{0} = self.guro.addVar(lb = {1}, ub = {2}, vtype = gp.GRB.CONTINUOUS, name = "{0}")'.format(rxn, self.lb[i], self.ub[i]))
        for var in [v for v in self.colNames if v not in self.idRs]:
            exec('self.{0} = self.guro.addVar(vtype = gp.GRB.BINARY, name = "{0}")'.format(var))
        self.guro.update()
        # adding constraints
        lhs = sp.sparse.coo_matrix((self.lhsVals, (self.lhsRows, self.lhsCols))).toarray()
        for i, row in enumerate(lhs):
            nz = row.nonzero()[0]
            pair = zip(row[nz], np.array(self.colNames)[nz])
            s = ''
            for p in pair:
                s += '(%s * self.%s) + ' % (p[0], p[1]) 
            s = s.rstrip(' + ')
            if self.senses[i] == 'E':
                s += ' == %s' % self.rhs[i]
            elif self.senses[i] == 'G':
                s += ' >= %s' % self.rhs[i]
            elif self.senses[i] == 'L':
                s += ' <= %s' % self.rhs[i]
            exec('self.guro.addConstr( %s, "%s")' % (s, self.rowNames[i]))     
        #setting the objective
        s = ''
        for name in self.colNames:
            if name.startswith('y'):
                s += 'self.{} + '.format(name)
        s = s.rstrip(' + ')
        exec('self.guro.setObjective({}, gp.GRB.MAXIMIZE)'.format(s))

    def solve(self):
        self.rowAndColNames()
        self.buildLhsMatrix()
        self.buildRhsAndSenses()
        self.initGurobi()
        self.guro.optimize()
        self.initialized = 1

    def modulateEnzymeActivityAndDirection(self, rxn):
        """
        """
        try:
            dummy =  self.initialized
        except AttributeError:
            self.solve()
        # 1. forcing rxn to be inactive reaction
        # The original bounds are saved in self.d before changing them
        self.d = {}
        exec('self.d["{0}.lb"] = self.{0}.lb'.format(rxn))
        exec('self.d["{0}.ub"] = self.{0}.ub'.format(rxn))
        exec("self.{}.setAttr('lb', 0.)".format(rxn))
        exec("self.{}.setAttr('ub', 0.)".format(rxn))
        if rxn in self.rH:
            exec('self.d["yp_{0}.ub"] = self.yp_{0}.ub'.format(rxn))
            exec("self.yp_{}.setAttr('ub', 0)".format(rxn))
            if rxn in self.rHrev:
                exec('self.d["ym_{0}.ub"] = self.ym_{0}.ub'.format(rxn))
                exec("self.ym_{}.setAttr('ub', 0)".format(rxn))
        elif rxn in self.rL:
            exec('self.d["y_{0}.lb"] = self.y_{0}.lb'.format(rxn)) #saving lb
            exec("self.y_{}.setAttr('lb', 1)".format(rxn)) #changing lb
        self.guro.update()
        self.guro.optimize()
        status = self.guro.getAttr('status')
        if status == 2:
            scoreZero = int(round(self.guro.objVal))
            solZero = [v.x for v in self.guro.getVars()]
        else:
            scoreZero = -1
            solZero = []
        # restoring the original bounds
        for key in self.d:
            try:
                l = key.split('.')
                exec("self.{}.setAttr('{}', {})".format(l[0], l[1], self.d[key]))
            except AttributeError:
                pass
        self.guro.update()
        del self.d

        # 2. forcing forward direction
        exec('self.fwd = self.{}.ub'.format(rxn)) 
        if self.fwd == 0: #if irreversible in the rev dir
            scoreFwd = 0
            solFwd = []
            del self.fwd
        else:
            self.d = {}
            exec('self.d["{0}.lb"] = self.{0}.lb'.format(rxn))
            exec("self.{}.setAttr('lb', self.eps)".format(rxn))
            if rxn in self.rH:
                exec('self.d["yp_{0}.lb"] = self.yp_{0}.lb'.format(rxn))
                exec("self.yp_{}.setAttr('lb', 1)".format(rxn))
                if rxn in self.rHrev:
                    exec('self.d["ym_{0}.ub"] = self.ym_{0}.ub'.format(rxn))
                    exec("self.ym_{}.setAttr('ub', 0)".format(rxn))
            elif rxn in self.rL:
                    exec('self.d["y_{0}.ub"] = self.y_{0}.ub'.format(rxn))
                    exec("self.y_{}.setAttr('ub', 0)".format(rxn))
        self.guro.update()
        self.guro.optimize()
        status = self.guro.getAttr('status')
        if status == 2:
            scoreFwd = int(round(self.guro.objVal))
            solFwd = [v.x for v in self.guro.getVars()]
        else:
            scoreFwd = -1
            solFwd = []
        # restoring the original bounds
        for key in self.d:
            try:
                l = key.split('.')
                exec("self.{}.setAttr('{}', {})".format(l[0], l[1], self.d[key]))
            except AttributeError:
                pass
        self.guro.update()
        del self.d

        # 3. forcing reverse direction
        # forcing reverse direction
        exec('self.rev = self.{}.lb'.format(rxn))
        if self.rev == 0: #if irreversible
            scoreRev = 0
            solRev = []
            del self.rev
        else:
            self.d = {}
            exec('self.d["{0}.ub"] = self.{0}.ub'.format(rxn))
            exec("self.{}.setAttr('ub', -self.eps)".format(rxn))
            if rxn in self.rH:
                exec('self.d["yp_{0}.ub"] = self.yp_{0}.ub'.format(rxn))
                exec("self.yp_{}.setAttr('ub', 0)".format(rxn))
                if rxn in self.rHrev:
                    exec('self.d["ym_{0}.lb"] = self.ym_{0}.lb'.format(rxn))
                    exec("self.ym_{}.setAttr('lb', 1)".format(rxn))
            elif rxn in self.rL:
                exec('self.d["y_{0}.ub"] = self.y_{0}.ub'.format(rxn))
                exec("self.y_{}.setAttr('ub', 0)".format(rxn))
            self.guro.update()
            self.guro.optimize()
            status = self.guro.getAttr('status')
            if status == 2:
                scoreRev = int(round(self.guro.objVal))
                solRev = [v.x for v in self.guro.getVars()]
            else:
                scoreRev = -1
                solRev = []
            # restoring the original bounds
            for key in self.d:
                try:
                    l = key.split('.')
                    exec("self.{}.setAttr('{}', {})".format(l[0], l[1], self.d[key]))
                except AttributeError:
                    pass
            self.guro.update()
            del self.d
        return scoreZero, scoreFwd, scoreRev, (solZero, solFwd, solRev)

    def exploreAlternativeOptima(self, idRs):
        """
        """
        self.solve()
        wtSol = int(round(self.guro.objVal))
        scores = []
        imgeSols = {}
        scores.append(['wildType'] + [wtSol, '', ''])
        for rxn in idRs:
            try:
                s = self.modulateEnzymeActivityAndDirection(rxn)
                scores.append([rxn] + list(s)[:3])
                imgeSols[rxn] = s[3]
            except:
                scores.append([rxn] + [-1]*3)
                imgeSols[rxn] = ([], [], [])
        return scores, imgeSols

class MipSeparateFwdRev(object):
    """
    03 May 2012
    Creates a version of a cbModel in which reversible reactions into their
    fwd and rev components. Integer variables ensure that only one of the
    fwd, rev pair can carry a flux.
    """
    def __init__(self, cbm, mfr = [], eps = 1E-10):
        self.m0 = cbm
        self.mfr = mfr
        self.eps = eps
        # identify mfr that are reversible
        self.mfrRev = [rxn for i, rxn in enumerate(self.m0.idRs) if 
                (self.m0.lb[i] < 0.) and (self.m0.ub[i] > 0.) and
                (rxn in self.mfr)]
        #NOTE assumes that irreversible rxns have lb = 0 (true in all
        #models I've come across)
        # Modify lb of irreversible mfr
        for rxn in set(self.mfr) - set(self.mfrRev):
            ind = self.m0.idRs.index(rxn)
            self.m0.lb[ind] = self.eps
        # 3. separate reversible rxns into fwd and rev reactions
        self.m = self.m0.separateFwdRevRxns()     
        #copying the S for the construction of the lhs
        self.lhsRows = [int(i) for i in self.m.S.row]   
        self.lhsCols = [int(i) for i in self.m.S.col]   
        self.lhsVals = [float(i) for i in self.m.S.data]
        self.rowNames = self.m.idSp[:]
        self.colNames = self.m.idRs[:]
    
    def rowAndColNames(self):
        for rxn in self.mfrRev:
            self.rowNames.append('cfl_{}'.format(rxn)) #constraint fwd lb
            self.rowNames.append('cfu_{}'.format(rxn)) #constraint fwd ub
            self.rowNames.append('crl_{}'.format(rxn)) #constraint rev lb
            self.rowNames.append('cru_{}'.format(rxn)) #constraint rev ub
            self.colNames.append('y_{}'.format(rxn)) #integer variable    
    
    def buildLhs(self):
        for rxn in self.mfrRev:
            #fwd lowerbound constrain
            self.lhsRows.append(self.rowNames.index('cfl_{}'.format(rxn)))
            self.lhsCols.append(self.colNames.index(rxn))
            self.lhsVals.append(1)
            self.lhsRows.append(self.rowNames.index('cfl_{}'.format(rxn)))
            self.lhsCols.append(self.colNames.index('y_{}'.format(rxn)))
            self.lhsVals.append(-self.eps)
            #fwd upperbound constrain
            self.lhsRows.append(self.rowNames.index('cfu_{}'.format(rxn)))
            self.lhsCols.append(self.colNames.index(rxn))
            self.lhsVals.append(1)
            self.lhsRows.append(self.rowNames.index('cfu_{}'.format(rxn)))
            self.lhsCols.append(self.colNames.index('y_{}'.format(rxn)))
            self.lhsVals.append(-self.m.ub[self.colNames.index(rxn)])
            #rev lowerbound constrain
            self.lhsRows.append(self.rowNames.index('crl_{}'.format(rxn)))
            self.lhsCols.append(self.colNames.index(rxn + '_rev'))
            self.lhsVals.append(1)
            self.lhsRows.append(self.rowNames.index('crl_{}'.format(rxn)))
            self.lhsCols.append(self.colNames.index('y_{}'.format(rxn)))
            self.lhsVals.append(self.eps)
            #rev upperbound constrain
            self.lhsRows.append(self.rowNames.index('cru_{}'.format(rxn)))
            self.lhsCols.append(self.colNames.index(rxn + '_rev'))
            self.lhsVals.append(1)
            self.lhsRows.append(self.rowNames.index('cru_{}'.format(rxn)))
            self.lhsCols.append(self.colNames.index('y_{}'.format(rxn)))
            self.lhsVals.append(self.m.ub[self.colNames.index(rxn + '_rev')])

    def buildRhsAndSenses(self):
        self.senses = 'E' * len(self.m.idSp)
        self.rhsRows = []
        self.rhsCols = []
        self.rhsVals = []
        for rxn in self.mfrRev:
            #fwd ub
            self.rhsRows.append(self.rowNames.index('cfl_{}'.format(rxn)))
            self.rhsCols.append(0)
            self.rhsVals.append(0)
            self.senses += 'G'
            #fwd lb
            self.rhsRows.append(self.rowNames.index('cfu_{}'.format(rxn)))
            self.rhsCols.append(0)
            self.rhsVals.append(0)
            self.senses += 'L'
            #
            #rev ub
            self.rhsRows.append(self.rowNames.index('crl_{}'.format(rxn)))
            self.rhsCols.append(0)
            self.rhsVals.append(self.eps)
            self.senses += 'G'
            #rev lb
            self.rhsRows.append(self.rowNames.index('cru_{}'.format(rxn)))
            self.rhsCols.append(0)
            self.rhsVals.append(self.m.ub[self.colNames.index(rxn + '_rev')])
            self.senses += 'L'

        self.rhs = list(sp.sparse.coo_matrix((self.rhsVals, (self.rhsRows, self.rhsCols)), 
                                   shape = (len(self.rowNames), 1)).toarray().flatten())    
        #}}}

class MipSeparateFwdRev_gurobi(MipSeparateFwdRev):
    def initMipGurobi(self):
        self.rowAndColNames()
        self.buildLhs()
        self.buildRhsAndSenses()
        self.guro = gp.Model('minSumFluxes')
        #turning off the writing of the gurobi.log file
        self.guro.setParam('OutputFlag', 0) 
        # adding variables
        for i, rxn in enumerate(self.m.idRs):
            exec('self.{0} = self.guro.addVar(lb = {1}, ub = {2}, vtype = gp.GRB.CONTINUOUS, name = "{0}")'.format(rxn, self.m.lb[i], self.m.ub[i])) 
        for var in [v for v in self.colNames if v not in self.m.idRs]:
            exec('self.{0} = self.guro.addVar(lb = 0, ub = 1, vtype = gp.GRB.BINARY, name = "{0}")'.format(var))
        self.guro.update()
        # adding constraints
        lhs = sp.sparse.coo_matrix((self.lhsVals, (self.lhsRows, self.lhsCols))).toarray()
        for i, row in enumerate(lhs):
            nz = row.nonzero()[0]
            pair = zip(row[nz], np.array(self.colNames)[nz])
            s = ''
            for p in pair:
                s += '({} * self.{}) + '.format(p[0], p[1]) 
            s = s.rstrip(' + ')
            if self.senses[i] == 'E':
                s += ' == {}'.format(self.rhs[i])
            elif self.senses[i] == 'G':
                s += ' >= {}'.format(self.rhs[i])
            elif self.senses[i] == 'L':
                s += ' <= {}'.format(self.rhs[i])
            exec('self.guro.addConstr( {}, "{}")'.format(s, self.rowNames[i]))

    def minSumFluxes_gurobi(self):
        # setting the objective
        s = 'self.linobj = gp.LinExpr([1.0] * len(self.m.idRs), ['
        for var in self.guro.getVars():
            if not var.varName.startswith('y_'): #excluding binary variables
                s += 'self.{}, '.format(var.varName)
        s = s.rstrip(', ')
        s += '])'
        exec(s)
        self.guro.setObjective(self.linobj, gp.GRB.MINIMIZE)#1 for minimize
        self.guro.optimize()
        self.initialized = 1

#################
#Define functions needed to classify reaction activity based off of abundance. 
#################

def orderGeneNamesByLength(geneList):
    """
    Group gene names by their lengths
    RETURNS byLengthDict [dict]: {stringLength : [list of gene ids that are
        that long]
    """
    byLengthDict = collections.defaultdict(list)
    for gn in geneList:
        byLengthDict[len(gn)].append(gn)
    
    return byLengthDict

def substituteGeneNamesByCalls(g2r, geneList, geneCalls, callTranslationDict):
    """
    ACCEPTS
    g2r [str] Boolean gene-to-reaction mapping
    geneLists [list] list of genes who's calls will be subsitituted in g2r
    geneCalls [dict] {geneId : geneCall}
    callTranslationDict [dict] : {geneCall : rxnCall} rules for translating a
        geneCall to a rxnCall (see createRxnGeneCalls)
    RETURNS:
    gs [str] string with gene names substituted by their expression calls
    """    
    for gn in geneList:
        try:
            if geneCalls[gn] == -1:#lowly expressed
                g2r = g2r.replace(gn, callTranslationDict[-1])
            elif geneCalls[gn] == 0:#undecided expression
                g2r = g2r.replace(gn, callTranslationDict[0])
            elif geneCalls[gn] == 1:#highly expressed
                g2r = g2r.replace(gn, callTranslationDict[1])
        except KeyError:# gene expression unavailable
            g2r = g2r.replace(gn, callTranslationDict[0])#undecided expression
    return g2r

def createRxnGeneCalls(geneCalls, gene2rxn, modelGenes):
    """
    creates a dictionary of reaction calls {rxn : call}, where call may be
    -1 (lowly expressed), 0 (moderate expression) or 1 (highly expressed).
    ACCEPTS
    geneCalls [dict]: {geneName : call} where calls are as explained above
    gene2rxn [dict]: {rxn : Boolean gene to rxn mapping (string)} 
    modelGenes [set]: gene names included in the model
    RETURNS
    rxnGeneCalls [dict] : {rxn : calls}, where calls may be -1, 0 or 1
    """
    orphanRxns = set([rxn for rxn in gene2rxn if not gene2rxn[rxn]])
    #ordering gene names by their lenghts (some gene names are part of others
    # e.g. 'YCR024C' and 'YCR024C-A' in yeast). Hence long names should be 
    # replaced before short ones
    geneNamesByLength = orderGeneNamesByLength(modelGenes)
    orderedGeneLengths = list(geneNamesByLength)
    orderedGeneLengths.sort(reverse = True)
    rxnGeneCalls = {}
    for rxn in set(gene2rxn.keys()) - orphanRxns:
        # lowly expressed genes are evaluated to -1 while higly expressed genes are evaluated to 1. Lowly expressed reactions are those for which their Boolean expression evaluates to -1
        g2r = gene2rxn[rxn]
        for length in orderedGeneLengths:
            g2r = substituteGeneNamesByCalls(g2r, geneNamesByLength[length], 
                    geneCalls, {-1 : '-1', 0 : '0', 1 : '1'})
        g2r = str(g2r)
        i = g2r.split('or')
        countdict = {}
        countdict_calls = {}
        for count, j in enumerate(i):
            j = j.split('and')
            genelist = []
            for k in j:
                k = k.replace(" ", "")
                k = k.replace("(", "")
                k = k.replace(")", "")
                if not k:
                    continue
                else:
                    genelist.append(k)
            countdict[count] = genelist
        for i in countdict:
            one_count = 0
            negative_one_count = 0
            for j in countdict[i]:
                if int(j) == 1:
                    one_count += 1
                if int(j) == -1:
                    negative_one_count += 1
            if len(countdict[i]) == one_count:
                countdict_calls[i] = 1
            elif negative_one_count > 0:
                countdict_calls[i] = -1
            else:
                countdict_calls[i] = 0
        call_one = 0
        call_zero = 0
        call_negative_one = 0
        for i in countdict_calls:
            if countdict_calls[i] == 1:
                call_one += 1
            elif countdict_calls[i] == 0:
                call_zero += 1
            else:
                call_negative_one += 1
        if call_one >= 1:
            rxnGeneCalls[rxn] = 1
        elif call_zero >= 1:	
            rxnGeneCalls[rxn] = 0
        else:
            rxnGeneCalls[rxn] = -1 
    return rxnGeneCalls

def classifyRxnsByExpression(geneCalls, gene2rxn, modelGenes):
    """
    Classifies reactions with gene associations as  highly, uncertain or 
    lowly expressed. 
    rxnDict [dict]: {rxn : rxnObject} cbModel.rxns or cbModel.reactions (old)
    geneCalls [dict]: {geneName : call} where calls are as explained above
    modelGenes [set]: gene names included in the model
    RETURNS
    d [dict]: {'rL' : lowlyExpressed, 'rU' : uncertainExpression, 
        'rH' : highlyExpressed}
    """
    rxnCalls = createRxnGeneCalls(geneCalls, gene2rxn, modelGenes)
    lowlyExpressed = set()
    highlyExpressed = set()
    uncertainExpression = set()
    for rxn in rxnCalls:
        if rxnCalls[rxn] == -1:
            lowlyExpressed.add(rxn)
        elif rxnCalls[rxn] == 0:
            uncertainExpression.add(rxn)
        elif rxnCalls[rxn] == 1:
            highlyExpressed.add(rxn)
    d = {'rL' : lowlyExpressed, 'rU' : uncertainExpression, 
            'rH' : highlyExpressed}
    return d

def getZeroAndHighFrequencyRxns(scores, imgeSols, idRs, activityThreshold = 1E-10):
    wtScore = scores[0][1]
    numSols = 0
    actDict = {}#counts for active reactions
    inactDict = {}#counts for inactive reactions
    for i, rxn in enumerate(idRs):
        row = scores[i+1][1:4]
        sol = imgeSols[rxn]
        for j, val in enumerate(row):
            if val >= wtScore:#select only max agreement scores
                numSols += 1
                for k, r in enumerate(idRs):
                    if abs(sol[j][k]) > activityThreshold:
                        try:
                            actDict[r] += 1
                        except KeyError:
                            actDict[r] = 1
                    else:
                        try:
                            inactDict[r] += 1
                        except KeyError:
                            inactDict[r] = 1
    
    zfr = set()#zero frequency reactions
    for rxn in inactDict:
        if inactDict[rxn] == numSols:# rxn inactive in all optimal solutions
            zfr.add(rxn)
    
    hfr = set()#high frequency reactions
    for rxn in actDict:
        if actDict[rxn] == numSols:# rxn active in all optimal solutiosn
            hfr.add(rxn)
    return zfr, hfr

#################
#Define functions needed to delete reactions from model and reduce. 
#################

def deleteCbmRxns(cbm, rl):
    """
    09 Dec 2011
    Deletes a list of reactions (or a single reaction) in rl from a
    CbModel instance.
    cbm [CbModel instance]
    rl [list or str] reaction(s) to be deleted
    RETURNS
    cbmNew [CbModel instance] model with the reaction(s) in rl deleted
    """
    if type(rl) == str:
        rl = [rl]
    indRs = [i for i, rxn in enumerate(cbm.idRs) if rxn not in rl]
    idRs =  [rxn for i, rxn in enumerate(cbm.idRs) if rxn not in rl]
    S = cbm.S.toarray()[:, indRs]
    actSpInd = [i for i, row in enumerate(S) if sum(abs(row)) > 1E-10]
    S = S[actSpInd]
    idSp = [met for i, met in enumerate(cbm.idSp) if i in actSpInd]
    lb = [val for i, val in enumerate(cbm.lb) if i in indRs]
    ub = [val for i, val in enumerate(cbm.ub) if i in indRs]
    cbmNew = CbModel(sp.sparse.coo_matrix(S), idSp, idRs, lb, ub)
    #reactions dictionary
    if 'rxns' in dir(cbm):
        rxns = {}
        for key in cbm.rxns:
            if key in idRs:
                rxns[key] = cbm.rxns[key]
        cbmNew.rxns = rxns
    #species dictionary
    if 'species' in dir(cbm):
        species = {}
        for key in cbm.species:
            if key in idSp:
                species[key] = cbm.species[key]
        cbmNew.species = species
    #model genes
    if 'genes' in dir(cbm):
        import re
        reGenes = re.compile('[a-zA-Z0-9_\-\.]*')
        genes = set()
        for rxn in rxns:
            gl = reGenes.findall(rxns[rxn]['genes'])
            genes.update(gl)
        genes = genes - set(['', 'and', 'or'])
        cbmNew.genes = genes
    return cbmNew

def findActiveRxns(cbm, thresh, rl = []):
    act = set()
    arrayIdRs = np.array(cbm.idRs[:])
    init = cbm.initLp()
    init 
    if rl:
        idRs = rl
    else:
        idRs = cbm.idRs[:]
    # maximizing
    for rxn in idRs:
        if rxn not in act:
            # reseting the objective
            cbm.guro.setObjective(0)
            exec('cbm.guro.setObjective(cbm.%s, gp.GRB.MAXIMIZE)' % rxn)
            cbm.guro.optimize()
            sol = abs(np.array([v.x for v in cbm.guro.getVars()]))
            indices = (sol > thresh).nonzero()[0]
            act.update(arrayIdRs[indices])
    idRs = list(set(idRs) - act)
    # minimizing
    for rxn in idRs:
        if rxn not in act:
            # reseting the objective
            cbm.guro.setObjective(0)
            exec('cbm.guro.setObjective(cbm.%s, gp.GRB.MINIMIZE)' % rxn)
            cbm.guro.optimize()
            sol = abs(np.array([v.x for v in cbm.guro.getVars()]))
            indices = (sol > thresh).nonzero()[0]
            act.update(arrayIdRs[indices])
    return act

def pruneRxn(cbm, cH, rxn, thresh, eps, activityThreshold, fOutFreqBasedRxns, 
             repetition, biomassRxn, lb_biomass):
######Change description and pickle_model_name to fOutFreqBasedRxns
    try:
        #Prune a reaction. If a flux solution cannot be obtained
        #or if the biomass flux becomes inactive, stop pruning.
        rxntodelete = rxn
        m0 = deleteCbmRxns(cbm, rxntodelete)
        act = findActiveRxns(m0, thresh)
        cH_act = cH & act
        if (len(cH - cH_act) != 0):#not all cH rxns are active
            return cbm
        hfr = importPickle(fOutFreqBasedRxns)['hfr']
        hfr_new = hfr & set(m0.idRs)
        #forcing biomass production
        m0.lb[m0.idRs.index(biomassRxn)] = lb_biomass
        #minimizing the sum of fluxes
        mtry1result = MipSeparateFwdRev_gurobi(m0, hfr_new, eps)
        mtry1result.initMipGurobi()
        mtry1result.minSumFluxes_gurobi()
        nz = getNzRxnsGurobi(mtry1result, activityThreshold, m0.rxns)[1]
    except:
        return cbm
    try:
        #Identify the reactions that became inactive after the
        #reaction was deleted. If extra deleted reactions cause the
        #model to be unsolvable, or if extra deleted inactive reactions
        #cause any of the hfrs to become inactive, or if a solution
        #cannot be obtained with a biomass flux, only delete the one
        #reaction. Otherwise, delete the inactive reactions.
        inact = set(m0.idRs) - act - cH
        m1 = deleteCbmRxns(m0, inact)
        act2 = findActiveRxns(m1, thresh)
        cH_act2 = cH & act2
        if (len(cH - cH_act2) != 0):#not all cH rxns are active
            return m0
        hfr = importPickle(fOutFreqBasedRxns)['hfr']
        hfr_new = hfr & set(m1.idRs)
        #forcing biomass production
        m1.lb[m1.idRs.index(biomassRxn)] = lb_biomass
        #minimizing the sum of fluxes
        mtry2result = MipSeparateFwdRev_gurobi(m1, hfr_new, eps)
        mtry2result.initMipGurobi()
        mtry2result.minSumFluxes_gurobi()
        nz = getNzRxnsGurobi(mtry2result, activityThreshold, m1.rxns)[1]
        return m1
    except:
        return m0

def iterativePrunning(i, m, cH, fOutFreqBasedRxns, biomassRxn, lb_biomass,
                      repetition, thresh = 1E-10, eps = 1E-10, activityThreshold = 1E-10, EXrxns = [],
                      EXtrrxns = [], Othertrrxns = []):
######Change description and pickle_model_name to fOutFreqBasedRxns
    if len(EXrxns) > 0:
        EXrxnsprune = list(set(list(EXrxns)) - cH)
        random.shuffle(EXrxnsprune)
        while EXrxnsprune:
            rxn1 = EXrxnsprune.pop()
            try:
                mTemp1 = pruneRxn(mTemp1, cH, rxn1, thresh, eps, activityThreshold, fOutFreqBasedRxns,
                                  repetition, biomassRxn, lb_biomass)
                EXrxnsprune2 = []
                for k in mTemp1.idRs:
                    if k in EXrxnsprune:
                        EXrxnsprune2.append(k)
                random.shuffle(EXrxnsprune2)
                EXrxnsprune = EXrxnsprune2
            except NameError:
                mTemp1 = pruneRxn(m, cH, rxn1, thresh, eps, activityThreshold, fOutFreqBasedRxns,
                                  repetition, biomassRxn, lb_biomass)
                EXrxnsprune2 = []
                for k in mTemp1.idRs:
                    if k in EXrxnsprune:
                        EXrxnsprune2.append(k)
                random.shuffle(EXrxnsprune2)
                EXrxnsprune = EXrxnsprune2
    if len(EXtrrxns) > 0:
        EXtrrxnsprune = list(set(list(EXtrrxns)) - cH)
        EXtrrxnsprunelist = []
        for j in EXtrrxnsprune:
            if j in mTemp1.idRs:
                EXtrrxnsprunelist.append(j)
        random.shuffle(EXtrrxnsprune)
        while EXtrrxnsprune:
            rxn2 = EXtrrxnsprune.pop()
            try:
                mTemp1 = pruneRxn(mTemp1, cH, rxn2, thresh, eps, activityThreshold, fOutFreqBasedRxns,
                                  repetition, biomassRxn, lb_biomass)
                EXtrrxnsprune2 = []
                for k in mTemp1.idRs:
                    if k in EXtrrxnsprune:
                        EXtrrxnsprune2.append(k)
                random.shuffle(EXtrrxnsprune2)
                EXtrrxnsprune = EXtrrxnsprune2
            except NameError:
                mTemp1 = pruneRxn(m, cH, rxn2, thresh, eps, activityThreshold, fOutFreqBasedRxns,
                                  repetition, biomassRxn, lb_biomass)
                EXtrrxnsprune2 = []
                for k in mTemp1.idRs:
                    if k in EXtrrxnsprune:
                        EXtrrxnsprune2.append(k)
                random.shuffle(EXtrrxnsprune2)
                EXtrrxnsprune = EXtrrxnsprune2

    prunableRxns = []
    try:
        for j in mTemp1.idRs:
            if j not in list(cH):
                if j not in EXrxns:
                    if j not in EXtrrxns:
                        if j not in Othertrrxns:
                            prunableRxns.append(j)
    except NameError:
        for j in m.idRs:
            if j not in list(cH):
                if j not in EXrxns:
                    if j not in EXtrrxns:
                        if j not in Othertrrxns:
                            prunableRxns.append(j)
    random.shuffle(prunableRxns)
    while prunableRxns:
        rxn3 = prunableRxns.pop()
        try:
            mTemp1 = pruneRxn(mTemp1, cH, rxn3, thresh, eps, activityThreshold, fOutFreqBasedRxns,
                              repetition, biomassRxn, lb_biomass)
            prunableRxns2 = []
            for k in mTemp1.idRs:
                if k in prunableRxns:
                    prunableRxns2.append(k)
            random.shuffle(prunableRxns2)
            prunableRxns = prunableRxns2
        except NameError:
            mTemp1 = pruneRxn(m, cH, rxn3, thresh, eps, activityThreshold, fOutFreqBasedRxns,
                              repetition, biomassRxn, lb_biomass)
            prunableRxns2 = []
            for k in mTemp1.idRs:
                if k in prunableRxns:
                    prunableRxns2.append(k)
            random.shuffle(prunableRxns2)
            prunableRxns = prunableRxns2
    return mTemp1.idRs

#################
#Define function for minimizing the sum of fluxes.
#################

def getNzRxnsGurobi(mg, actThreshold, md):
    #computing the fluxes for reversible reactions
    revRxns = [i.varName for i in mg.guro.getVars() if i.varName.endswith('_rev')]
    revRxnsSols = []
    revRxnsIds = []
    for rxn in revRxns:
        fwd = rxn[:-4]
        exec('valRev = mg.{}.x'.format(rxn))
        exec('valFwd = mg.{}.x'.format(fwd))
        revRxnsSols.append(valFwd - valRev)
        revRxnsIds.append(fwd)
    sols = []
    for var in mg.guro.getVars():
        if not var.varName.startswith('y_'):# skip integer variables:
            if var.varName in revRxnsIds:
                sols.append([var.varName, revRxnsSols[revRxnsIds.index(var.varName)]])
            elif var.varName.endswith('_rev'):
                continue
            else:
                sols.append([var.varName, var.x])

    nzSols = [[i[0], i[1], abs(i[1]), md[i[0]]['reactants'],
               md[i[0]]['products'], md[i[0]]['lb'],
               md[i[0]]['ub']] for i in sols]
    return [i[0] for i in nzSols], nzSols
