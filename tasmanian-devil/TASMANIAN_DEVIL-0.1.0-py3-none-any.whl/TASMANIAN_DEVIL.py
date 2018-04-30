from __future__ import print_function
from builtins import range
import argparse
import cobra
import csv
import decimal
import os
import shutil
import time
import multiprocessing as mp
import Crypto.Random
from . import gene as gene_class
from . import model as model_class
from . import flux as flux_class
from . import visualization as visualization_class

def model(args):
    #Make sure there is a way to check if model is carbon balanced
    metFormulas_list = []
    if ((args.metabolitemappingcomplexes or args.nucleotideconversions or args.adaptation or args.zerocarbons or args.removeinactiverxnsandbalance) and not args.metabolite2carbon):
        if args.sbml:
            cobra_model = cobra.io.read_sbml_model(args.model)	
        if args.cobra:
            cobra_model = cobra.io.mat.load_matlab_model(args.model)
        metFormulas = cobra.io.mat._cell([str(m.formula) for m in cobra_model.metabolites])
        metFormulas_list = filter(None, metFormulas.tolist())
        if not metFormulas_list:
            raise RuntimeError("Must supply -d argument as well. Look at the help documetation.")

    #Import other arguments and change name of exported model file
    model_desc = ''
    if args.lowerbound:
        model_desc = model_desc + 'l'
    if args.upperbound:
        model_desc = model_desc + 'u'
    if args.gene2rxn:
        model_desc = model_desc + 'g'
    if args.metabolitemappingcomplexes:
        model_desc = model_desc + 'm'
    if args.nucleotideconversions:
        model_desc = model_desc + 'n'
    if args.removeinactiverxnsandbalance:
        model_desc = model_desc + 'c'
    if args.adaptation:
        model_desc = model_desc + 'mod'
    #Perhaps consider if OS is Windows or Linux for file structure
    name = args.model.split('/')[-1]
    model_desc = model_desc + "_" + name


    ##Make the changes to the model
    model, cobra_specific_objects, mets_to_extracellular_comp, rxns_original, biomass_rxn = model_class.set_parameter(args.model, args.sbml, args.cobra, args.extracellular, args.lowerbound, args.upperbound, args.gene2rxn)
    model, cobra_specific_objects = model_class.modify(model, cobra_specific_objects, args.adaptation)    
    model, cobra_specific_objects = model_class.metabolite_mapping(model, cobra_specific_objects, args.metabolitemappingcomplexes)
    model, cobra_specific_objects = model_class.nucleotide_conversion(model, cobra_specific_objects, args.nucleotideconversions)
    model, cobra_specific_objects, unbalanced_rxns_mets_unique_list, unbalanced_rxns_mets_potential_list = model_class.balance_reactions(model, cobra_specific_objects, mets_to_extracellular_comp, rxns_original, biomass_rxn, args.metabolite2carbon, metFormulas_list, args.zerocarbons)
    model, cobra_specific_objects = model_class.metabolite_cleanup(model,cobra_specific_objects)
    model_class.model_export(model, cobra_specific_objects, model_desc)
    model_class.remove_inactive_rxns_and_account_for_biomass(model_desc,args.removeinactiverxnsandbalance, args.extracellular, args.metabolite2carbon, metFormulas_list) 
    

def gene(args):
    #Import model if provided
    if args.model:         
        if not (args.sbml or args.cobra):
            raise RuntimeError("Must specify model type if providing model. Use -c or -s")
    cobra_model = None
    if args.sbml: 
        cobra_model = cobra.io.read_sbml_model(args.model)
    if args.cobra:
        cobra_model = cobra.io.mat.load_matlab_model(args.model)	    
    gene_class.gene_classify(args.expression_set, args.upper, args.lower, args.output, cobra_model)


def flux(args):
    #Import the model, adjust the biomass production, and create the names for the exported files
    description = args.description.name
    if args.sbml:
        cobra_model = cobra.io.read_sbml_model(args.model)	
    if args.cobra:
        cobra_model = cobra.io.mat.load_matlab_model(args.model)
    
    if args.biomassprod:
        lb_biomass = args.biomassprod
    else:
        solution = cobra_model.optimize()
        decimal.getcontext().rounding = decimal.ROUND_DOWN
        decimal.getcontext().prec = 4
        lb_biomass = decimal.Decimal(solution.objective_value) + decimal.Decimal('0.0')
    #Perhaps consider if OS is Windows or Linux for file structure
    name_split = os.path.splitext(args.model)[0].split("/")[-1]
    description_split = os.path.splitext(description)[0].split("/")[-1]
    model_desc = ''
    if args.EXrxns:
        model_desc = model_desc + 'EXrxns'
    if args.EXtrrxns:
        model_desc = model_desc + 'EXtrrxns'
    if args.Othertrrxns:
        model_desc = model_desc + 'Othertrrxns'

    fOutRxnsByExpression = 'RxnsClassifiedByExpression_' + model_desc + description_split + '_' + name_split + '.pkl'
    fOutFreqBasedRxns = 'freqBasedRxns_' + model_desc + description_split + '_' + name_split + '.pkl' 
    model_desc = model_desc + description_split + '_' + name_split

    ######Perform iMAT
    # 0. Import model dictionary
    args_lowerbound = None
    args_upperbound = None
    args_gene2rxn = None
    model, cobra_specific_objects, mets_to_extracellular_comp, rxns_original, biomass_rxn = model_class.set_parameter(args.model, args.sbml, args.cobra, args.extracellular, args_lowerbound, args_upperbound, args_gene2rxn)
    m = flux_class.CbModel(model['S'], model['idSp'], model['idRs'], model['lb'], model['ub'], model['rxns'], model['genes'])

    #copy of rxns identifiers
    idRs = m.idRs[:]
    idRs.remove(biomass_rxn)
    #forcing non-zero biomass production
    m.lb[m.idRs.index(biomass_rxn)] = lb_biomass

    #Not including this would cause the model to fail the iMAT if reactions are included in the model that have the following boundary constraints 
    for i in m.idRs:
        if ((model['rxns'][i]['lb'] <= 0) and (model['rxns'][i]['ub'] == 0)):
            m.ub[m.idRs.index(i)] = 1000

    # 1. Classify reactions by expression
    ## Importing gene calls as a dictionary
    geneCalls = {}
    csv_file = csv.reader(args.description)
    for line in csv_file:
        geneCalls[line[0]] = int(line[1])

    ## Classifying reactions by expression
    rxnDict = flux_class.classifyRxnsByExpression(geneCalls, m.gene2rxn, m.genes)
    flux_class.exportPickle(rxnDict, fOutRxnsByExpression)

    # 2. Maximizing agreement score and exploring alternative optima
    rH = rxnDict['rH']
    rL = rxnDict['rL']

    #Added eps to arguments
    model_mgem = flux_class.MetabGeneExpModel_gurobi(m.idSp, m.idRs, m.S, m.lb, m.ub, rH, rL, args.epsearly)
    scores, imgeSols = model_mgem.exploreAlternativeOptima(idRs)

    # 3. identifying zero and high frequency reactions
    zfr, hfr = flux_class.getZeroAndHighFrequencyRxns(scores, imgeSols, idRs, args.epsidentifyingfrequencies)
    flux_class.exportPickle({'zfr' : zfr, 'hfr' : hfr}, fOutFreqBasedRxns)

    #Pint the number of HFR and ZFR genes
    print ('zfr ', len(zfr))
    print ('hfr ', len(hfr))

    ######Prune model
    repetitions = args.repetitionsoffluxstates
    eps = args.epsirreversiblerxns
    thresh = args.epspruning
    activityThreshold = args.espsolving

    #Create lists of extracellular reactions, extracellular transport reactions, and other compartmental transport reactions, so that the reactions can be pruned in that order first.
    EXrxns = []
    EXtrrxns = []
    Othertrrxns = []
    if args.EXrxns:
        csv_file = csv.reader(args.EXrxns)
        for line in csv_file:
            EXrxns.append(line[0])
    if args.EXtrrxns:
        csv_file = csv.reader(args.EXtrrxns)
        for line in csv_file:
            EXtrrxns.append(line[0])
    if args.Othertrrxns:
        csv_file = csv.reader(args.Othertrrxns)
        for line in csv_file:
            Othertrrxns.append(line[0])
    for repetition in range(repetitions): 
    ################################################################################
    # originally _02_minimizeNetwork_part_A.py in EXAMO
    ################################################################################

        number_concurrent_processes = args.concurrentprocesses
        reps = args.repetitionsofconcurrentprocesses

        #Making subdirectories for candidate reactions
        mbaCandRxnsDirectory = 'data/mbaCandRxns/{}_{}/'.format(model_desc, repetition)
        if os.path.exists(mbaCandRxnsDirectory):
            shutil.rmtree(mbaCandRxnsDirectory)
            os.makedirs(mbaCandRxnsDirectory)
        else:
            os.makedirs(mbaCandRxnsDirectory)

        fOutMbaCandRxns = ''.join((mbaCandRxnsDirectory, "mbaCandRxns_%s.pkl"))

	################################################################################
        # STATEMENTS
        # Instantiating CbModel 
        m0 = flux_class.CbModel(model['S'], model['idSp'], model['idRs'], model['lb'], model['ub'], model['rxns'],model['genes'])
        #Changed the minimum biomass flux to be the maximum amount with default boundary constraints 
        m0.lb[m0.idRs.index(biomass_rxn)] = lb_biomass

        for i in m0.idRs:
            if ((model['rxns'][i]['lb'] <= 0) and (model['rxns'][i]['ub'] == 0)):
                m0.ub[m0.idRs.index(i)] = 1000

        biomass_set = {biomass_rxn}
        new_hfr = hfr.union(biomass_set)

        zfr_check = 0
        try:
            m = flux_class.deleteCbmRxns(m0, zfr)
            act = flux_class.findActiveRxns(m, thresh, new_hfr)
            cH = new_hfr & act
            act = flux_class.findActiveRxns(m, thresh, cH)
            cH2 = cH & act
            #######################################################################
            # STATEMENTS
            new_hfr2 = hfr & set(m.idRs)
            #minimizing the sum of fluxes
            mtry1result = flux_class.MipSeparateFwdRev_gurobi(m, new_hfr2, eps)
            mtry1result.initMipGurobi()
            mtry1result.minSumFluxes_gurobi()
            #Added activityThreshold and the m0.rxns dictionary to the
            #function, so that the reactants and products could be written out
            nz = flux_class.getNzRxnsGurobi(mtry1result, activityThreshold, m.rxns)[1]
        except:
            zfr_check = 1
	
        if zfr_check == 1:
            zfr_list = []
            for i in zfr:
                try:
                    m1 = flux_class.deleteCbmRxns(m0, i)
                    act = flux_class.findActiveRxns(m1, thresh, new_hfr)
                    #######################################################################
                    # STATEMENTS
                    new_hfr2 = hfr & set(m0.idRs)
                    #minimizing the sum of fluxes
                    mtry1result = flux_class.MipSeparateFwdRev_gurobi(m1, new_hfr2, eps)
                    mtry1result.initMipGurobi()
                    mtry1result.minSumFluxes_gurobi()
                    #Added activityThreshold and the m0.rxns dictionary to the
                    #function, so that the reactants and products could be written out
                    nz = flux_class.getNzRxnsGurobi(mtry1result, activityThreshold, m1.rxns)[1]
                    m0 = m1
                    zfr_list.append(i)
                except:
                    continue
            m = flux_class.deleteCbmRxns(m0, zfr_list)
            act = flux_class.findActiveRxns(m, thresh, new_hfr)
            cH = new_hfr & act
            act = flux_class.findActiveRxns(m, thresh, cH)
            cH2 = cH & act		

        #Make a directory for temporary files for every time a rxn is pruned
        mbaCandRxnsDirectorySubset = 'data/temp/{}_{}/'.format(model_desc, repetition)
        if not os.path.exists(mbaCandRxnsDirectorySubset):
            os.makedirs(mbaCandRxnsDirectorySubset)

        def pruneReps():
            locTime = time.localtime()
            pid = os.getpid()
            Crypto.Random.atfork()
            for x in range(reps):
                timeStr = '%i%02i%02i%02i%02i%02i' % locTime[:6]
                tag = '%s_%s_%s_%s' % (model_desc, pid, x, timeStr)
                #Added despricription, repetition, and lists of compartmental reactions to the function
                cr = flux_class.iterativePrunning(i, m, cH2, fOutFreqBasedRxns, biomass_rxn, lb_biomass, repetition, thresh, eps, activityThreshold, EXrxns, EXtrrxns, Othertrrxns)
                flux_class.exportPickle(cr, fOutMbaCandRxns % tag)

        processes = []
        for _ in range(number_concurrent_processes):
            p = mp.Process(target = pruneReps)
            p.start()
            processes.append(p)
   
        for p in processes:
            p.join()

        #Delete the temporary files generated for every time a rxn is pruned
        shutil.rmtree(mbaCandRxnsDirectorySubset)

	################################################################################
        # _03_minimizeNetwork_part_B_new.py 
	################################################################################
        # STATEMENTS
        #Create file to export
        fOutModel = 'examo_%s_%s.pkl'

        # Instantiating CbModel 
        m = flux_class.CbModel(model['S'], model['idSp'], model['idRs'], model['lb'], model['ub'], model['rxns'], model['genes'])

        # Retrieving MBA candidate reaction lists
        files = os.popen('ls {} | grep {}'.format(mbaCandRxnsDirectory, model_desc)).read().splitlines()

        rxnSets = []
        for fn in files:
            l = set(flux_class.importPickle(mbaCandRxnsDirectory + fn)) - hfr
            rxnSets.append(flux_class.importPickle(mbaCandRxnsDirectory + fn))

        # Quantifying the number of times a rxn is among the candidate models
        rxnFreq = {}
        for rs in rxnSets:
            for rxn in rs:
                try:
                    rxnFreq[rxn] += 1
                except KeyError:
                    rxnFreq[rxn] = 1

        freq = {}#{frequency : list of reactions}
        for rxn in rxnFreq:
            try:
                freq[rxnFreq[rxn]].add(rxn)
            except KeyError:
                freq[rxnFreq[rxn]] = set([rxn])
        orderedFreq = list(freq)
        orderedFreq.sort(reverse = True)

        #Making sure that all hfr reactions are active.
        act = flux_class.findActiveRxns(m, thresh, hfr)
        mRxns = hfr & act
        #Rather than identifying which reactions need to be added to make all of the hfrs active, reactions will be added until the a flux can be achieved for the biomass reaction 
        for num in orderedFreq:
            mRxns.update(freq[num])
            excRxns = set(m.idRs) - mRxns
            try:
                m1 = flux_class.deleteCbmRxns(m, excRxns)
                flux_class.exportPickle(m1, fOutModel % (model_desc, str(repetition)))
                rev = [0 if val >= 0 else 1 for val in m1.lb]
                gene2rxn = {}
                rxns = {}
                for rxn in m1.rxns:
                    gene2rxn[rxn] = m1.rxns[rxn]['genes']
                    rxns[rxn] = m1.rxns[rxn]
                mDict = {
                    'S' : m1.S,
                    'idSp' : m1.idSp,
                    'idRs' : m1.idRs,
                    'lb' : m1.lb,
                    'ub' : m1.ub,
                    'rev' : rev,
                    'genes' : m1.genes,
                    'gene2rxn' : gene2rxn,
                    'rxns' : rxns,
	            'descrip' : 'examo %s' % model_desc}
                flux_class.exportPickle(mDict, fOutModel % (model_desc, str(repetition) + '_dict'))
                ################################################################################                
                # _04_predictMetabolicState.py
		################################################################################
                # OUTPUT
                fOutMetabState = 'metabolicState_%s_%s.csv'
		################################################################################
                # STATEMENTS

                md = flux_class.importPickle(fOutModel % (model_desc, str(repetition) + '_dict'))
                mtry = flux_class.CbModel(md['S'], md['idSp'], md['idRs'], md['lb'], md['ub'], md['rxns'], md['genes'])
                hfr = hfr & set(mtry.idRs)
                #forcing biomass production
                mtry.lb[mtry.idRs.index(biomass_rxn)] = lb_biomass
                for i in mtry.idRs:
                    if ((md['rxns'][i]['lb'] <= 0) and (md['rxns'][i]['ub'] == 0)):
                        mtry.ub[mtry.idRs.index(i)] = 1000

                #minimizing the sum of fluxes
                mprod = flux_class.MipSeparateFwdRev_gurobi(mtry, hfr, eps)
                mprod.initMipGurobi()
                mprod.minSumFluxes_gurobi()
                #Added activityThreshold and the md['rxns'] dictionary to the function, so that the reactants and products could be written out
                nz = flux_class.getNzRxnsGurobi(mprod, activityThreshold, md['rxns'])[1]

                # reporting the flux distribution obtained		
                f = open(fOutMetabState % (model_desc, str(repetition)), 'w')
                csv.writer(f).writerows(nz)
                f.close()
                break
            except:
                mprod = flux_class.MipSeparateFwdRev_gurobi(mtry, hfr, eps)
                mprod.initMipGurobi()
                mprod.minSumFluxes_gurobi()
                continue

def visualization(args):
    if (args.geneCalls2 or args.fluxState2 or args.rxnsClassifiedByExpression2 or args.freqBasedRxns2):  
        if not args.model2:
            raise RuntimeError("Must supply -m2 if going to use -g2, -f2, -c2, or -b2 for second condition")
    #Import model1
    args_lowerbound = None
    args_upperbound = None
    args_gene2rxn = None
    pickle_model1, cobra_specific_objects, mets_to_extracellular_comp, rxns_original, biomass_rxn = model_class.set_parameter(args.model1, args.sbml, args.cobra, args.extracellular, args_lowerbound, args_upperbound, args_gene2rxn)
    md_model1 = flux_class.CbModel(pickle_model1['S'], pickle_model1['idSp'], pickle_model1['idRs'], pickle_model1['lb'], pickle_model1['ub'], pickle_model1['rxns'], pickle_model1['genes'])

    #Import model2
    model2 = None
    pickle_model2 = None
    if args.model2: 
        pickle_model2, cobra_specific_objects, mets_to_extracellular_comp, rxns_original, biomass_rxn = model_class.set_parameter(args.model2, args.sbml, args.cobra, args.extracellular, args_lowerbound, args_upperbound, args_gene2rxn)
        md_model2 = flux_class.CbModel(pickle_model2['S'], pickle_model2['idSp'], pickle_model2['idRs'], pickle_model2['lb'], pickle_model2['ub'], pickle_model2['rxns'], pickle_model2['genes'])

    #Store number of repetitions
    repetitions = args.repetitionsoffluxstates

    #Import the gene rules and create dictionaries
    csvreader1 = csv.reader(args.geneCalls1)
    geneCalls1 = {}
    for row in csvreader1:
        geneCalls1[row[0]] = int(row[1])

    
    geneCalls2 = None
    if args.geneCalls2:
        csvreader2 = csv.reader(args.geneCalls2)
        geneCalls2 = {}
        for row in csvreader2:
            geneCalls2[row[0]] = int(row[1])


    #Declare the names of the flux states
    fluxstate1 = args.fluxState1
    prepend_split = fluxstate1.split('/')
    if len(prepend_split) > 2:
        prepend = '/'.join(prepend_split[0:-1])
        fluxstate1 = prepend_split[-1]
    elif len(prepend_split) == 2:
        prepend = prepend_split[0]
        fluxstate1 = prepend_split[-1]
    elif len(prepend_split) == 1:
        prepend = ''
        fluxstate1 = prepend_split[0]
    fluxstate2 = args.fluxState2
    if fluxstate2:
        prepend_split = fluxstate2.split('/')
        fluxstate2 = prepend_split[-1]

    #Classify the rxns as being in rH, rL or neither and hfr, zfr, or neither
    gbr1_rH = None
    if args.rxnsClassifiedByExpression1:
        gbr1 = flux_class.importPickle(args.rxnsClassifiedByExpression1) 
        gbr1_rH = {}
        for t in md_model1.rxns.keys():
            if t in gbr1['rH']:
                gbr1_rH[t] = 2
            elif t in gbr1['rL']:
                gbr1_rH[t] = 0
            else:
                gbr1_rH[t] = 1
    
    fbr1_hfr = None
    if args.freqBasedRxns1:
        fbr1 = flux_class.importPickle(args.freqBasedRxns1)
        fbr1_hfr = {}
        for t in md_model1.rxns.keys():
            if t in fbr1['hfr']:
                fbr1_hfr[t] = 2
            elif t in fbr1['zfr']:
                fbr1_hfr[t] = 0
            else:
                fbr1_hfr[t] = 1

    gbr2_rH = None
    if args.rxnsClassifiedByExpression2:
        gbr2 = flux_class.importPickle(args.rxnsClassifiedByExpression2)
        gbr2_rH = {} 
        for t in md_model2.rxns.keys():
            if t in gbr2['rH']:
                gbr2_rH[t] = 2
            elif t in gbr2['rL']:
                gbr2_rH[t] = 0
            else:
                gbr2_rH[t] = 1
    
    fbr2_hfr = None
    if args.freqBasedRxns2:
        fbr2 = flux_class.importPickle(args.freqBasedRxns2)
        fbr2_hfr = {}
        for t in md_model2.rxns.keys():
            if t in fbr2['hfr']:
                fbr2_hfr[t] = 2
            elif t in fbr2['zfr']:
                fbr2_hfr[t] = 0
            else:
                fbr2_hfr[t] = 1

    #Define which pathways are going to be visualized
    pathway_list = []
    for pathway in args.pathways:
        pathway_list.append(pathway)

    #Create the necessary objects to map the models accordingly
    rxngenesandor1, cond1freqavg, cond1fluxavg, fluxavgdict1 = visualization_class.cond(pickle_model1, md_model1, fluxstate1, prepend, geneCalls1, gbr1_rH, fbr1_hfr, repetitions)
    if args.fluxState2: 
        rxngenesandor2, cond2freqavg, cond2fluxavg, fluxavgdict2 = visualization_class.cond(pickle_model2, md_model2, fluxstate2, prepend, geneCalls2, gbr2_rH, fbr2_hfr, repetitions)
    else: 
        fluxavgdict2 = {}
    #Scale the fluxes between conditions, if appropriate
    cond1fluxavgscaled, cond2fluxavgscaled = visualization_class.scaleflux(fluxavgdict1, fluxavgdict2, pickle_model1, pickle_model2)
    #Create the rule, frequency, and flux maps
    if gbr1_rH:
        visualization_class.visualizeRules(pathway_list, md_model1, fluxstate1, prepend, gbr1_rH, rxngenesandor1)
    if gbr2_rH:
        visualization_class.visualizeRules(pathway_list, md_model2, fluxstate2, prepend, gbr2_rH, rxngenesandor2)
    if fbr1_hfr:       
        visualization_class.visualizeFrequency(pathway_list, md_model1, cond1freqavg, fluxstate1, prepend, fbr1_hfr)
    if fbr2_hfr:
        visualization_class.visualizeFrequency(pathway_list, md_model2, cond2freqavg, fluxstate2, prepend, fbr2_hfr)
    visualization_class.visualizeFlux(pathway_list, md_model1, cond1fluxavg, fluxavgdict1, cond1fluxavgscaled, fluxstate1, prepend)
    if args.fluxState2:
        visualization_class.visualizeFlux(pathway_list, md_model2, cond2fluxavg, fluxavgdict2, cond2fluxavgscaled, fluxstate2, prepend)
    

def main():
    parser = argparse.ArgumentParser(prog="tas")
    subparsers = parser.add_subparsers(help="sub-command help")
    
    # model subcommand parser
    parser_model = subparsers.add_parser("model", help='Make modifications to SBML or COBRA models. Look at iMM904 example in test_data folder of installation for examples of formatting files')
    model_group = parser_model.add_mutually_exclusive_group(required=True)
    parser_model.add_argument("model", type=str, 
                              help='Necessary variable: metabolic reconstruction file')
    parser_model.add_argument("extracellular", type=str,
                             help="Necessary variable: extracellular compartment abbreviation. Instead of brackets or parentheses, use underscores (ex: '_e')")
    parser_model.add_argument("-o", "--output", type=argparse.FileType("w"),
                              help='Name of model to be written out')
    model_group.add_argument("-c", "--cobra", action="store_true",
                             help='Flag to specify whether model is a COBRA Toolbox (.mat) file type; must have either -xml or -mat flag')
    model_group.add_argument("-s", "--sbml", action="store_true",
                             help='Flag to specify whether model is a SBML (.xml) file type; must have either -xml or -mat flag')
    parser_model.add_argument("-l", "--lowerbound", type=argparse.FileType("r"), default=None,
                              help='lower boundary constraints file')
    parser_model.add_argument("-u", "--upperbound", type=argparse.FileType("r"), default=None,
                              help='upper boundary constraints file')
    parser_model.add_argument("-g", "--gene2rxn", type=argparse.FileType("r"), default=None,
                              help='gene2rxn file')
    parser_model.add_argument("-d", "--metabolite2carbon", type=str, default=None,
                              help='Tab-delimited file to specify dicitonary mappings of number of carbons in every metabolite. This is to check whether the model is carbon balanced. See iMM904 example for documentation')
    parser_model.add_argument("-m", "--metabolitemappingcomplexes", type=argparse.FileType("r"), default=None,
                              help='Tab-delimited metabolite mapping complexes file. See iMM904 example for documentation. Make sure model is carbon balanced if you use this; must have -d argument as well to use this if metFormulas is not in model')
    parser_model.add_argument("-n", "--nucleotideconversions", type=argparse.FileType("r"), default=None,
                              help='Tab-delimited nucleotide conversions file. See iMM904 example for documentation. Make sure model is carbon balanced if you use this; must have -d argument as well to use this if metFormulas is not in model')
    parser_model.add_argument("-a", "--adaptation",  type=argparse.FileType("r"), default=None, 
                              help='Tab delimited file to change specific reaction stoichiometries or to remove metabolites from reactions. See iMM904 example for documentation; must have -d argument as well to use this if metFormulas is not in model') 
    parser_model.add_argument("-z", "--zerocarbons", action="store_true",
                              help='Flag to specify whether to remove metabolites wihtout any carbons. Must have -d argument as well to use this if metFormulas is not in model')
    parser_model.add_argument("-r", "--removeinactiverxnsandbalance", action="store_true",
                              help='Flag to specify whether to remove inactive reactions from final model and remove carbon unbalanced reactions. Recommend using only after first inspecting reactions to be removed. Must have -d argument as well to use this if metFormulas is not in model')	
    parser_model.set_defaults(func=model)

    # gene subcommand parser
    parser_gene = subparsers.add_parser("gene", help="Classify gene activity in the context of a model")
    parser_gene.add_argument("expression_set", type=argparse.FileType("r"), help='Name of tab delimited gene file with counts')
    parser_gene.add_argument("-m", "--model", type=str, help='Metabolic reconstruction file')
    parser_gene.add_argument("-c", "--cobra", action="store_true",
                             help='Flag to specify whether model is a COBRA Toolbox (.mat) file type; must have either -xml or -mat flag')
    parser_gene.add_argument("-s", "--sbml", action="store_true", 
                             help='Flag to specify whether model is a SBML (.xml) file type; must have either -xml or -mat flag')
    parser_gene.add_argument("-o", "--output", type=argparse.FileType("w"), 
                             default="gene_classification.csv", help='Name of csv gene rule file to be written out')
    parser_gene.add_argument("-u", "--upper", type=float, default=0.75,
                             help='upper threshold by which to define genes as being active; default value: upper 25% of genes mapped to reactions')
    parser_gene.add_argument("-l", "--lower", type=float, default=0.25,
                             help='lower threshold by which to define genes as being inactive; default value: lower 25% of genes mapped to reactions')
    parser_gene.set_defaults(func=gene)
    
    # flux subcommand parser
    parser_flux = subparsers.add_parser("flux", help='Predict condition-specific fluxes')
    flux_group = parser_flux.add_mutually_exclusive_group(required=True)
    parser_flux.add_argument("model", help='Necessary variable: metabolic reconstruction file')
    parser_flux.add_argument("description", type=argparse.FileType("r"), help='Necessary variable: comma separated gene rule file')
    parser_flux.add_argument("extracellular", type=str,
                             help="Necessary variable: extracellular compartment abbreviation. Instead of brackets or parentheses, use underscores (ex: '_e')")
    parser_flux.add_argument("concurrentprocesses", type=int, help='Necessary variable: number of concurrent processes for creating pruned models')
    parser_flux.add_argument("repetitionsofconcurrentprocesses", type=int, help='Necessary variable: number of times to repeat the chosen number of processes to create the profile of models')
    parser_flux.add_argument("repetitionsoffluxstates", type=int, 
                             help='Necessary variable: number of repetitions to produce final flux states (csv files)')
    flux_group.add_argument("-c", "--cobra", action="store_true",
                             help='Flag to specify whether model is a COBRA Toolbox (.mat) file type; must have either -xml or -mat flag')
    flux_group.add_argument("-s", "--sbml", action="store_true",
                             help='Flag to specify whether model is a SBML (.xml) file type; must have either -xml or -mat flag')
    parser_flux.add_argument("-e", "--epsearly", type=float, default=1E-1, 
                             help='Minimum value for fluxes forced to be non-zero (for the implementation of the pathway algorithm created by Shlomi); default value: 1E-1')
    parser_flux.add_argument("-z", "--epsidentifyingfrequencies", type=float, default=1E-10,
                             help='Activity threshold when classifying HFR and ZFR reactions from gene rules') 
    parser_flux.add_argument("-i", "--epsirreversiblerxns", type=float, default=1E-10,
                             help='Minimum value for active flux of reversible reactions in an irreversible model; default value: 1E-10')
    parser_flux.add_argument("-t", "--epspruning", type=float, default=1E-10, 
                             help='Activity threshold for finding active reactions when pruning a model')
    parser_flux.add_argument("-a", "--espsolving", type=float, default=1E-10, 
                             help='Activity threshold (above which a flux is considered to be larger than 0 when minimizing the sum of fluxes); default value: 1E-10')
    parser_flux.add_argument("-b", "--biomassprod", type=float, help='Defined biomass production') 
    parser_flux.add_argument("-EXrxns", type=argparse.FileType("r"), help='Comma separated file containing extracellular reactions')
    parser_flux.add_argument("-EXtrrxns", type=argparse.FileType("r"), help='Comma separated file containing extracellular transport reactions')
    parser_flux.add_argument("-Othertrrxns", type=argparse.FileType("r"), help='Comma separated file containing other compartmental transport reactions')
    parser_flux.set_defaults(func=flux)
    
    #vizualization subcommand parser
    parser_visualization = subparsers.add_parser("visualization", help='Visualize fluxes on predefined maps. Look to help page on website for more detailed instructions for creating predefined maps')
    visualization_group = parser_visualization.add_mutually_exclusive_group(required=True)
    parser_visualization.add_argument("model1", type=str, help='Necessary variable: metabolic reconstruction file 1')
    parser_visualization.add_argument("geneCalls1", type=argparse.FileType("r"), help='Necessary variable: comma separated gene rule file 1')
    parser_visualization.add_argument("fluxState1", type=str, help='Necessary variable: Name of flux state 1')
    parser_visualization.add_argument("pathways", nargs="+", type=str, help='Necessary variable: name of pathway(s)')
    parser_visualization.add_argument("repetitionsoffluxstates", type=int, help='Necessary variable: number of repetitions to produce final flux states (csv files)')
    parser_visualization.add_argument("extracellular", type=str,
                             help="Necessary variable: extracellular compartment abbreviation. Instead of brackets or parentheses, use underscores (ex: '_e').")
    visualization_group.add_argument("-c", "--cobra", action="store_true",
                             help='Flag to specify whether model is a COBRA Toolbox (.mat) file type; must have either -xml or -mat flag.')
    visualization_group.add_argument("-s", "--sbml", action="store_true",
                             help='Flag to specify whether model is a SBML (.xml) file type; must have either -xml or -mat flag.')
    parser_visualization.add_argument("-c1", "--rxnsClassifiedByExpression1", type=str, help='Reactions classified by expression pickle file 1 from flux module')
    parser_visualization.add_argument("-b1", "--freqBasedRxns1", type=str, help='Reactions classified by frequency pickle file 1 from flux module')
    parser_visualization.add_argument("-m2", "--model2", type=str, help='Metabolic reconstruction file 2')
    parser_visualization.add_argument("-g2", "--geneCalls2", type=argparse.FileType("r"), help='Comma separated gene rule file 2')
    parser_visualization.add_argument("-f2", "--fluxState2", type=str, help='Name of flux state 2')
    parser_visualization.add_argument("-c2", "--rxnsClassifiedByExpression2", type=str, help='Reactions classified by expression pickle file 2 from flux module')
    parser_visualization.add_argument("-b2", "--freqBasedRxns2", type=str, help='Reactions classified by frequency pickle file 2 from flux module')
    parser_visualization.set_defaults(func=visualization)
    
    #parse args
    args = parser.parse_args()
    try:
        args.func(args)
    except AttributeError:
        print("ERROR: Missing subcommand. Try tas -h")
