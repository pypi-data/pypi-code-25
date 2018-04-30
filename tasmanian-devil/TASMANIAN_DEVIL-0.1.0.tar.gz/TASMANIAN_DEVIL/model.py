from __future__ import print_function
import re
import cobra
from cobra.core.arraybasedmodel import ArrayBasedModel
from cobra.manipulation.delete import prune_unused_metabolites
import scipy as sp
import numpy as np
import csv
import itertools

def set_parameter(args_model, args_sbml, args_cobra, args_extracellular, args_lowerbound, args_upperbound, args_gene2rxn):    
    #Import the model.
    if args_sbml:
        cobra_model = cobra.io.read_sbml_model(args_model)
    if args_cobra:
        cobra_model = cobra.io.mat.load_matlab_model(args_model)
    idRs = []
    lb = []
    ub = []
    genes_genes2rxn = []
    pathway = []
    rxn2lb = {}
    rxn2ub = {}
    gene2rxn = {}
    rxns = {}
    rxns_original = {}

    idSp = []
    for i in cobra_model.metabolites:
        name = name_sub(i.id, "M_")
        idSp.append(name)

    cobra_model = ArrayBasedModel(cobra_model)
    S = sp.sparse.coo_matrix(cobra_model.S)
    S = sp.sparse.lil_matrix(S)

    #Import lower boundary adjustments if the argument is supplied from the command line. 
    if args_lowerbound:
        lb_dict = {}        
        csv_file = csv.reader(args_lowerbound)        
        for row in csv_file:
            name = row[0]
            name = name_sub(name, "R_")
            rxn2lb[name] = float(row[1])

    #Import upper boundary adjustments if the argument is supplied from the command line. 
    if args_upperbound:
        ub_dict = {}        
        csv_file = csv.reader(args_upperbound)        
        for row in csv_file:
            name = row[0]
            name = name_sub(name, "R_")
            rxn2ub[name] = float(row[1])

    #Import gene rule adjustments if the argument is supplied from the command line. 
    if args_gene2rxn:
        genes_dict = {}
        csv_file = csv.reader(args_gene2rxn)
        for row in csv_file:
            name = row[0]
            name = name_sub(name, "R_")
            gene2rxn[name] = row[1]

    #Create the necesssary rxn dictionaries for EXAMO.
    mets_to_extracellular_comp = []    
    for i in cobra_model.reactions:
        reaction_name = name_sub(i.id, "R_")
        reactants = {}
        reactants_original = {}
        products = {}
        products_original = {}
        idRs.append(reaction_name)
        if not args_lowerbound:
            rxn2lb[reaction_name] = i.lower_bound
            lb.append(float(i.lower_bound))
        if not args_upperbound:
            rxn2ub[reaction_name] = i.upper_bound
            ub.append(float(i.upper_bound))
        if not args_gene2rxn:
            gene2rxn[reaction_name] = i.gene_reaction_rule
        pathway.append(i.subsystem)
        for j in i.metabolites:
            if i.metabolites[j] < 0:
                metabolite_name = name_sub(j.id, "M_")
                reactants[metabolite_name] = -1*i.metabolites[j]
                reactants_original[metabolite_name] = -1*i.metabolites[j]
            if i.metabolites[j] > 0:
                metabolite_name = name_sub(j.id, "M_")
                products[metabolite_name] = i.metabolites[j]
                products_original[metabolite_name] = i.metabolites[j]
        if len(products) == 0:
            for j in reactants:
                extracellular_string = args_extracellular + '\Z'
                idSp_e = re.search(extracellular_string, j)
                if idSp_e:
                    if args_extracellular[-1:] == '_':
                        products[j[:-2]+'b_'] = reactants[j]
                        products_original[j[:-2]+'b_'] = reactants[j]
                        mets_to_extracellular_comp.append(j[:-2]+str("b_"))
                    else:
                        products[j[:-1]+'b'] = reactants[j]
                        products_original[j[:-1]+'b'] = reactants[j]
                        mets_to_extracellular_comp.append(j[:-1]+str("b"))
        if (rxn2lb[reaction_name] < 0 and rxn2ub[reaction_name] > 0):
            reversible = True
        else:
            reversible = False
        rxns[reaction_name] = {'name': i.name, 'id': reaction_name, 'reactants': reactants, 'products': products, 'reversible': reversible, 'genes': gene2rxn[reaction_name], 'lb': rxn2lb[reaction_name], 'ub': rxn2ub[reaction_name], 'pathway': i.subsystem}
        rxns_original[reaction_name] = {'name': i.name, 'id': reaction_name, 'reactants': reactants_original, 'products': products_original, 'reversible': reversible, 'genes': gene2rxn[reaction_name], 'lb': rxn2lb[reaction_name], 'ub': rxn2ub[reaction_name], 'pathway': i.subsystem}  

    #Create gene set
    genes = set()
    genes_list = []
    for t in rxns:
        values = rxns[t]['genes']
        values_split = values.split('or')
        for j in values_split:
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
                    if k not in genes_list:
                        genes.add(k)
                        genes_list.append(k)

    #Create list/sets/matlab cells of genes using cobrapy and array based model for reacitons
    genes_cobra = cobra.io.mat._cell(cobra_model.genes.list_attr('id'))
    grRules = cobra.io.mat._cell(cobra_model.reactions.list_attr('gene_reaction_rule'))
    c = np.array(cobra_model.reactions.list_attr('objective_coefficient')) * 1
    count = 0
    check_objective = 0    
    for i in c:
        count += 1
        if i == 1:
            check_objective += 1
            if check_objective == 1:
                biomass_rxn = idRs[count-1]
            else:
                print ("More than one objective being optimized for. Change objective to be only one reaction before attempting to convert.")
                raise SystemExit
    subsystem = cobra.io.mat._cell(cobra_model.reactions.list_attr('subsystem'))
    metNames = cobra.io.mat._cell(cobra_model.metabolites.list_attr('name'))
    metFormulas = cobra.io.mat._cell([str(m.formula) for m in cobra_model.metabolites])
    b = np.array(cobra_model.metabolites.list_attr('_bound')) * 1.
    
    #Create the model and cobra specific objects dictionaries to be able to export to other functions
    model = {'idSp' : idSp, 'idRs' : idRs, 'lb' : lb, 'ub' : ub, 'genes': genes, 'S' : S, 'rxns' : rxns }
    cobra_specific_objects = {'grRules': grRules, 'c': c, 'subsystem': subsystem, 'metNames': metNames, 'metFormulas': metFormulas, 'b': b}    
    return model, cobra_specific_objects, mets_to_extracellular_comp, rxns_original, biomass_rxn


def name_sub(string, prepend):
    #Make sure names from imported files all match
    name = string.replace("LPAREN","").replace("RPAREN","").replace("(","_").replace(")","_").replace("[","_").replace("]","_").replace("-","_").replace("__","_")
    if name[:2] != prepend:
        name = prepend+name
    return name

def name_sub_back(string):
    #Make names exported for COBRA compliant with SBML    
    name = string    
    if ((string[-3] == '_') and (string[-1] == '_')):    
        list1 = list(string)
        list1[-3] = '('
        list1[-1] = ')'
        name = ''.join(list1)
    if ((string[-2] == '_') and (string[-1].islower())):
        list1 = list(string)
        list1[-2] = '('
        name = ''.join(list1)
        name = name+')'
    if ((string[-1].isdigit()) and (string[-3] == '_')):
        list1 = list(string)
        list1[-3] = '('
        name = ''.join(list1[0:-1]) + ')' + list1[-1]
    name = name[2:]
    return name

def modify(model, cobra_specific_objects, args_adaptation):
    #Allow for changing the stoichiometry of any reactant or product for a reaction
    if args_adaptation:
        modifications = {}
        csv_file = csv.reader(args_adaptation)
        for row in csv_file:
            rxn = name_sub(row[0], "R_")
            met = name_sub(row[1], "M_")
            stoich = float(row[2])
            if rxn not in modifications:
                modifications[rxn] = {}
            modifications[rxn][met] = stoich
        rxn_index = 0
        for t in model['idRs']:
            rxn_index += 1
            met_index = 0
            rxn_index_change = []
            met_index_0 = []
            if t in modifications:
                rxn_index_change = rxn_index - 1
                for j in model['idSp']:
                    met_index += 1
                    if j in modifications[t]:
                        met_index_change = met_index - 1
                        model['S'][met_index_change, rxn_index_change] = modifications[t][j]
                        if modifications[t][j] < 0:
                            model['rxns'][t]['reactants'][j] = -1*modifications[t][j]
                            if ((j in model['rxns'][t]['products']) or (modifications[t][j] == 0 and j in model['rxns'][t]['reactants'])):
                                del model['rxns'][t]['products'][j]
                        if modifications[t][j] > 0:
                            model['rxns'][t]['products'][j] = modifications[t][j]
                            if ((j in model['rxns'][t]['reactants']) or (modifications[t][j] == 0 and j in model['rxns'][t]['products'])):
                                del model['rxns'][t]['reactants'][j]
                        if (modifications[t][j] == 0 and j in model['rxns'][t]['reactants']):
                            del model['rxns'][t]['reactants'][j]
                        if (modifications[t][j] == 0 and j  in model['rxns'][t]['products']):
                            del model['rxns'][t]['products'][j]
                    
    return model, cobra_specific_objects


def metabolite_mapping(model, cobra_specific_objects, args_metabolitemappingcomplexes):
    #Adjust for reactions that have metabolite mappings
    if args_metabolitemappingcomplexes:
        metabolite_mappings = {}        
        csv_file = csv.reader(args_metabolitemappingcomplexes)
        for row in csv_file:
            met1 = name_sub(row[0], "M_")
            met2 = name_sub(row[1], "M_")
            metabolite_mappings[met1] = met2
            metabolite_mappings[met2] = met1                
        met_rxns = []
        for t in model['rxns']:
            reactant_count = 0
            secondary_check = 0
            product_count = 0
            for i in metabolite_mappings.keys():
                if ((i in model['rxns'][t]['reactants']) and (metabolite_mappings[i] in model['rxns'][t]['products'])):            
                    met_rxns.append(t)
        #Remove mets from reactions with metabolite mappings
        rxn_index = 0
        for i in model['idRs']:
            rxn_index += 1
            met_index = 0
            rxn_index_0 = []
            met_index_0 = []
            if i in met_rxns:
                rxn_index_0.append(rxn_index - 1)
                for j in model['idSp']:
                    met_index += 1
                    if j in metabolite_mappings.keys():
                        met_index_0.append(met_index - 1)
                        if j in model['rxns'][i]['reactants']:
                            del model['rxns'][i]['reactants'][j]
                        if j in model['rxns'][i]['products']:
                            del model['rxns'][i]['products'][j]
            model['S'][met_index_0, rxn_index_0] = 0
    return model, cobra_specific_objects


def nucleotide_conversion(model, cobra_specific_objects, args_nucleotideconversions):
    #Remove repetitive nucleotides that share a carbon source 
    if args_nucleotideconversions:
        nucleotide_conversions = {}        
        csv_file = csv.reader(args_nucleotideconversions)
        for row in csv_file:
            met1 = name_sub(row[0], "M_")
            nucleotide_conversions[met1] = []
            for i in range(1,len(row)):
                met = name_sub(row[i], "M_")
                if met != "":
                    nucleotide_conversions[met1].append(met)
        for repetitivemet in nucleotide_conversions:
            mets_to_delete = []
            for i in nucleotide_conversions[repetitivemet]:
                met_index = 0
                mets_to_delete.append(i)
                met_index_to_change = []
                met_index_to_delete = []
                for j in model['idSp']:
                    met_index += 1
                    metabolite = repetitivemet
                    if j == metabolite:
                        met_index_to_change.append(met_index - 1) 
                met_index = 0    
                for j in model['idSp']:
                    num = 0
                    met_index += 1        
                    if j == i:
                        met_index_to_delete.append(met_index - 1)
                        rxn_index = 0
                        for t in model['idRs']:
                            rxn_index_to_change = []
                            rxn_index += 1
                            if i in model['rxns'][t]['reactants']:
                                rxn_index_to_change.append(rxn_index - 1)
                                if metabolite not in model['rxns'][t]['reactants']:
                                    model['rxns'][t]['reactants'].update({metabolite : model['rxns'][t]['reactants'][i]})
                                    num = -1*model['rxns'][t]['reactants'][metabolite]
                                    model['S'][met_index_to_change, rxn_index_to_change] = num            
                                else:                                            
                                    model['rxns'][t]['reactants'].update({metabolite : model['rxns'][t]['reactants'][metabolite] + model['rxns'][t]['reactants'][i]})
                                    num = -1*model['rxns'][t]['reactants'][metabolite]
                                    model['S'][met_index_to_change, rxn_index_to_change] = num
                                model['S'][met_index_to_delete, rxn_index_to_change] = 0
                                del model['rxns'][t]['reactants'][i]
                            if i in model['rxns'][t]['products']:
                                rxn_index_to_change.append(rxn_index - 1)
                                if metabolite not in model['rxns'][t]['products']:
                                    model['rxns'][t]['products'].update({metabolite : model['rxns'][t]['products'][i]})
                                    model['S'][met_index_to_change, rxn_index_to_change] = model['rxns'][t]['products'][metabolite]
                                else:                                            
                                    model['rxns'][t]['products'].update({metabolite : model['rxns'][t]['products'][metabolite] + model['rxns'][t]['products'][i]})
                                    model['S'][met_index_to_change, rxn_index_to_change] = model['rxns'][t]['products'][metabolite]
                                model['S'][met_index_to_delete, rxn_index_to_change] = 0
                                del model['rxns'][t]['products'][i]

    #Remove metabolites that appear as both a product and a reactant. 
    rxns_to_remove = []    
    rxn_count = 0
    for t in model['idRs']:
        rxn_count += 1
        rxn_index = []
        met_count = 0
        for i in model['idSp']:
            met_index = []
            met_count += 1
            if i in model['rxns'][t]['reactants']:
                if i in model['rxns'][t]['products']:
                    reactants_amount = model['rxns'][t]['reactants'][i]
                    products_amount = model['rxns'][t]['products'][i]
                    num = 0
                    met_index.append(met_count - 1)
                    rxn_index.append(rxn_count - 1)
                    if reactants_amount > products_amount:
                        model['rxns'][t]['reactants'][i] = model['rxns'][t]['reactants'][i] - products_amount
                        model['rxns'][t]['products'][i] = 0
                        del model['rxns'][t]['products'][i]
                        num = -1*model['rxns'][t]['reactants'][i]
                        model['S'][met_index, rxn_index] = num                
                    if products_amount > reactants_amount:
                        model['rxns'][t]['products'][i] = model['rxns'][t]['products'][i] - reactants_amount
                        model['rxns'][t]['reactants'][i] = 0
                        del model['rxns'][t]['reactants'][i]
                        model['S'][met_index, rxn_index] = model['rxns'][t]['products'][i]                
                    if reactants_amount == products_amount:
                        model['rxns'][t]['reactants'][i] = model['rxns'][t]['reactants'][i] - products_amount
                        model['rxns'][t]['products'][i] = model['rxns'][t]['products'][i] - reactants_amount
                        del model['rxns'][t]['reactants'][i]
                        del model['rxns'][t]['products'][i]
                        model['S'][met_index, rxn_index] = 0                
        if len(model['rxns'][t]['reactants']) == 0:
            if len(model['rxns'][t]['products']) == 0:
                rxns_to_remove.append(t)

    rxn_index = 0
    rxn_index_list = []
    rxn_index_list_to_delete = []
    for i in model['idRs']:
        rxn_index += 1
        if i not in rxns_to_remove:
            rxn_index_list.append(rxn_index-1)
        else:
            rxn_index_list_to_delete.append(rxn_index-1)
    cobra_specific_objects['grRules'] = np.delete(cobra_specific_objects['grRules'], rxn_index_list_to_delete)
    cobra_specific_objects['c'] = np.delete(cobra_specific_objects['c'], rxn_index_list_to_delete)
    cobra_specific_objects['subsystem'] = np.delete(cobra_specific_objects['subsystem'], rxn_index_list_to_delete)

    for t in rxns_to_remove:
        del model['rxns'][t]
        model['idRs'].remove(t)

    model['S'] = sp.sparse.lil_matrix(sp.sparse.csr_matrix(model['S'])[:,rxn_index_list])

    return model, cobra_specific_objects


def balance_reactions(model, cobra_specific_objects, mets_to_extracellular_comp, rxns_original, biomass_rxn, args_metabolite2carbon, metFormulas_list, args_zerocarbons, removed_inactive_rxns_and_balance = False):
    #Create empty lists for use later.
    unbalanced_rxns_mets_unique_list = []
    unbalanced_rxns_mets_potential_list = []
    if (args_metabolite2carbon or metFormulas_list or args_zerocarbons):
        #Import metabolite dictionary mapped to carbons if the argument is supplied from the command line.
        if args_metabolite2carbon:
            f = open(args_metabolite2carbon, 'r')
            csv_file = csv.reader(f)
            metabolite_dict = {}
            metabolite_dict_pre = {}
            metabolite_dict_csv = []
            for row in csv_file:
                metabolite_dict_csv.append(row[0])
                metabolite_dict_pre[row[0]] = row[1]
            f.close()

            #Account for possibility of every metabolite coming from any compartment, including transport into extracellular compartment
            last_string_list = []
            for i in model['idSp']:
                if i[-1] == '_':
                    b_name = '_b_'
                    if b_name not in last_string_list:
                        last_string_list.append(b_name)
                    last_string = i[-3:]
                    if last_string not in last_string_list:
                        last_string_list.append(last_string)
                else:
                    b_name = '_b'
                    if b_name not in last_string_list:
                        last_string_list.append(b_name)
                    last_string = i[-2:]
                    if last_string not in last_string_list:
                        last_string_list.append(last_string)
            for i in metabolite_dict_csv:
                for j in last_string_list:
                    met_name = i
                    met_name += j
                    metabolite_dict[met_name] = metabolite_dict_pre[i]
    
            #Remove metabolites in the metabolite dictionary that are not in the model
            metabolite_dict_to_delete = []
            for i in metabolite_dict:
                if i not in model['idSp']:
                    if i not in mets_to_extracellular_comp:
                        metabolite_dict_to_delete.append(i)
            for i in metabolite_dict_to_delete:
                del metabolite_dict[i]    
    
        #If metFormulas_list is not empty (if metabolite mapping complexes, nucleotide conversions, adaptations, balancing, or zerocarbons arguments were supplied from the command line), then use the metFormulas from the model.         
        if metFormulas_list:
            metFormulas_list = filter(None, cobra_specific_objects['metFormulas'].tolist())
            metabolite_dict = {}
            for count, met in enumerate(model['idSp']):
                try:
                    metnum = int(re.findall("C(\d+)",metFormulas_list[count])[0])
                except:
                    metnum = 0
                metabolite_dict[met] = metnum
            for met in mets_to_extracellular_comp:
                for key in metabolite_dict.keys():
                    if met[:-1] == key[:-1]:
                        metabolite_dict[met] = metabolite_dict[key]
        #Idenitfy metabolites with 0 carbons. They will be removed from the model    
        met_exception_list = []        
        if args_zerocarbons:
            rxns_to_remove = []    
            for i in metabolite_dict:
                if int(metabolite_dict[i]) == 0:
                    met_exception_list.append(i)
            #Remove reactions that only contain metabolites with 0 carbons for either reactants or products            
            for t in model['rxns']:
                reactant_count = 0
                product_count = 0    
                for reactant in model['rxns'][t]['reactants']:
                    if reactant in met_exception_list:
                        reactant_count += 1
                if reactant_count == len(model['rxns'][t]['reactants']):
                    if t != biomass_rxn:    
                        rxns_to_remove.append(t)
                for met in met_exception_list:
                    if met in model['rxns'][t]['reactants']:
                        del model['rxns'][t]['reactants'][met]
                for product in model['rxns'][t]['products']:
                    if product in met_exception_list:
                        product_count += 1
                if product_count == len(model['rxns'][t]['products']):
                    if t not in rxns_to_remove:
                        if t != biomass_rxn:
                            rxns_to_remove.append(t)
                for met in met_exception_list:
                    if met in model['rxns'][t]['products']:
                        del model['rxns'][t]['products'][met]
                            
            rxn_index = 0
            rxn_index_list = []
            rxn_index_list_to_delete = []
            for i in model['idRs']:
                rxn_index += 1
                if i not in rxns_to_remove:
                    rxn_index_list.append(rxn_index-1)
                else:
                    rxn_index_list_to_delete.append(rxn_index-1)
            cobra_specific_objects['grRules'] = np.delete(cobra_specific_objects['grRules'], rxn_index_list_to_delete)
            cobra_specific_objects['c'] = np.delete(cobra_specific_objects['c'], rxn_index_list_to_delete)
            cobra_specific_objects['subsystem'] = np.delete(cobra_specific_objects['subsystem'], rxn_index_list_to_delete)

            met_index = 0
            met_index_list = []
            met_index_list_to_delete = []
            for i in model['idSp']:
                met_index += 1
                if i not in met_exception_list:
                    met_index_list.append(met_index-1)
                else:
                    met_index_list_to_delete.append(met_index-1)
            cobra_specific_objects['metNames'] = np.delete(cobra_specific_objects['metNames'], met_index_list_to_delete)
            cobra_specific_objects['metFormulas'] = np.delete(cobra_specific_objects['metFormulas'], met_index_list_to_delete)
            cobra_specific_objects['b'] = np.delete(cobra_specific_objects['b'], met_index_list_to_delete)

            model['S'] = sp.sparse.lil_matrix(sp.sparse.csr_matrix(model['S'])[met_index_list, :])
            model['S'] = sp.sparse.lil_matrix(sp.sparse.csr_matrix(model['S'])[:,rxn_index_list])

            for met in met_exception_list:
                if ((met[-2:] != '_b') and (met[-3:] != '_b_')):
                    model['idSp'].remove(met)

            #Delete reactions and gene2rxn dictionary entries for reactions that cannot be carried out due to cofactor presence
            for t in rxns_to_remove:
                del model['rxns'][t]
                model['idRs'].remove(t)

        #Identify unbalanced rxns
        metabolite_dict_rxns = {}
        metabolite_dict_rxns_original = {}
        unbalanced_rxns = []
        balanced_rxns = []
        for t in model['rxns']:
            metabolite_dict_reactants = {}
            metabolite_dict_products = {}
            for i in model['rxns'][t]['reactants']:
                metabolite_dict_reactants[i] = metabolite_dict[i]
            for i in model['rxns'][t]['products']:
                metabolite_dict_products[i] = metabolite_dict[i]
            rxnmetlist = {'met_reactants': metabolite_dict_reactants, 'met_products': metabolite_dict_products}
            metabolite_dict_rxns[t] = rxnmetlist 
            metabolite_dict_reactants_original = {}
            metabolite_dict_products_original = {}
            for j in rxns_original[t]['reactants']:
                metabolite_dict_reactants_original[j] = metabolite_dict[j]
            for j in rxns_original[t]['products']:
                metabolite_dict_products_original[j] = metabolite_dict[j]
            rxnmetlist = {'met_reactants': metabolite_dict_reactants_original, 'met_products': metabolite_dict_products_original}
            metabolite_dict_rxns_original[t] = rxnmetlist

        if not removed_inactive_rxns_and_balance:
            print ("Unbalanced rxns:")
        for t in model['rxns']:
            reactants_count = 0
            products_count = 0
            for i in model['rxns'][t]['reactants']:
                reactants_count += int(metabolite_dict[i])*model['rxns'][t]['reactants'][i]
            for i in model['rxns'][t]['products']:
                products_count += int(metabolite_dict[i])*model['rxns'][t]['products'][i]
            for i in rxns_original[t]['reactants']:
                if i in met_exception_list:
                    products_count -= int(metabolite_dict[i])*rxns_original[t]['reactants'][i]
            for i in rxns_original[t]['products']:
                if i in met_exception_list:
                    reactants_count -= int(metabolite_dict[i])*rxns_original[t]['products'][i]    
            if round(reactants_count,3) != round(products_count,3):
                if not removed_inactive_rxns_and_balance:
                    print ("\n")
                    print (t)
                    print ("carbons in original model: %s" % metabolite_dict_rxns_original[t])
                    print ("stoichiometry in original model: %s" % rxns_original[t])
                    print ("carbons in adapted model: %s" % metabolite_dict_rxns[t])
                    print ("stoichiometry in adapted model: %s" % model['rxns'][t])        
                    print ("carbons in reactants in adapted model: %s" % reactants_count)
                    print ("cabons in products in adapted model: %s" % products_count)
                if t != biomass_rxn:
                    unbalanced_rxns.append(t)
            else:
                balanced_rxns.append(t)
    #Argument from the command line
    #Will be run at the end of model.py script to identify metabolites that need to be removed from the biomass rxn to make the model optimizable
    if removed_inactive_rxns_and_balance:
        balanced_rxns_mets_list = []
        for t in balanced_rxns:
            for met in model['rxns'][t]['reactants']:
                if ((met not in balanced_rxns_mets_list) and (met in model['rxns'][biomass_rxn]['reactants'])):
                    balanced_rxns_mets_list.append(met)
            for met in model['rxns'][t]['products']:
                if ((met not in balanced_rxns_mets_list) and (met in model['rxns'][biomass_rxn]['reactants'])):
                    balanced_rxns_mets_list.append(met)
        for t in unbalanced_rxns:
            for met in model['rxns'][t]['reactants']:
                if ((met not in unbalanced_rxns_mets_potential_list) and (met in model['rxns'][biomass_rxn]['reactants'])):
                    unbalanced_rxns_mets_potential_list.append(met)
            for met in model['rxns'][t]['products']:
                if ((met not in unbalanced_rxns_mets_potential_list) and (met in model['rxns'][biomass_rxn]['reactants'])):
                    unbalanced_rxns_mets_potential_list.append(met)
        for met in unbalanced_rxns_mets_potential_list:
            if met not in balanced_rxns_mets_list:
                unbalanced_rxns_mets_unique_list.append(met)
        #The rxns identified as not being balanced need to be verified whether they are due to a discrepancy in the metabolite_dict or whether the reactions are really not balanced due to an error in original model. 
        #If verified, then the rxns can be deleted, but other adjustments may need to be made to the model.
        #If a metabolite is not in a balanced rxn and only in an unbalanced rxn, it will be removed from the model.
        potential_unbalanced_mets = []
        for i in unbalanced_rxns:
            for k in model['rxns'][i]['reactants']:
                if k not in potential_unbalanced_mets:        
                    potential_unbalanced_mets.append(k)
            for k in model['rxns'][i]['products']:
                if k not in potential_unbalanced_mets:
                    potential_unbalanced_mets.append(k)

        balanced_rxns = list(set(model['idRs']) - set(unbalanced_rxns))

        mets_to_remove_from_potential_unbalanced_mets = []
        for i in potential_unbalanced_mets:
            for j in balanced_rxns:
                if j != biomass_rxn:
                    if i in model['rxns'][j]['reactants']:
                        if i not in mets_to_remove_from_potential_unbalanced_mets:
                            mets_to_remove_from_potential_unbalanced_mets.append(i)
                    if i in model['rxns'][j]['products']:
                        if i not in mets_to_remove_from_potential_unbalanced_mets:
                            mets_to_remove_from_potential_unbalanced_mets.append(i)
        mets_to_remove = list(set(potential_unbalanced_mets) - set(mets_to_remove_from_potential_unbalanced_mets))

        met_index = 0
        met_index_list = []
        met_index_list_to_delete = []
        for i in model['idSp']:
            met_index += 1
            if i not in mets_to_remove:
                met_index_list.append(met_index-1)
            else:
                met_index_list_to_delete.append(met_index-1)
        cobra_specific_objects['metNames'] = np.delete(cobra_specific_objects['metNames'], met_index_list_to_delete)
        cobra_specific_objects['metFormulas'] = np.delete(cobra_specific_objects['metFormulas'], met_index_list_to_delete)
        cobra_specific_objects['b'] = np.delete(cobra_specific_objects['b'], met_index_list_to_delete)

        model['S'] = sp.sparse.lil_matrix(sp.sparse.csr_matrix(model['S'])[met_index_list, :])

        for met in mets_to_remove:
            if ((met[-2:] != '_b') and (met[-3:] != '_b_')):
                model['idSp'].remove(met)

        #Remove unbalanced reactions
        rxn_index = 0
        rxn_index_list = []
        rxn_index_list_to_delete = []
        for i in model['idRs']:
            rxn_index += 1
            if i not in unbalanced_rxns:
                rxn_index_list.append(rxn_index-1)
            else:
                rxn_index_list_to_delete.append(rxn_index-1)
        cobra_specific_objects['grRules'] = np.delete(cobra_specific_objects['grRules'], rxn_index_list_to_delete)
        cobra_specific_objects['c'] = np.delete(cobra_specific_objects['c'], rxn_index_list_to_delete)
        cobra_specific_objects['subsystem'] = np.delete(cobra_specific_objects['subsystem'], rxn_index_list_to_delete)

        for i in unbalanced_rxns:
            del model['rxns'][i]
            model['idRs'].remove(i)

        model['S'] = sp.sparse.lil_matrix(sp.sparse.csr_matrix(model['S'])[:,rxn_index_list])
    return model, cobra_specific_objects, unbalanced_rxns_mets_unique_list, unbalanced_rxns_mets_potential_list



def metabolite_cleanup(model, cobra_specific_objects):
    #Remove mets that do not appear in any rxns
    idSp_to_remove = []
    met_index = 0
    met_index_list = []
    for i in model['idSp']:
        met_index += 1
        met_occurrence = 0
        for t in model['rxns']:
            if i in model['rxns'][t]['reactants']:
                met_occurrence += 1
            if i in model['rxns'][t]['products']:    
                met_occurrence += 1
        if met_occurrence == 0:
            idSp_to_remove.append(i)
        else:
            met_index_list.append(met_index - 1)

    model['S'] = sp.sparse.lil_matrix(sp.sparse.csr_matrix(model['S'])[met_index_list,:])

    met_index = 0
    met_index_to_delete = []
    for i in model['idSp']:
        met_index += 1
        if i in idSp_to_remove:
            met_index_to_delete.append(met_index-1)
    cobra_specific_objects['metNames'] = np.delete(cobra_specific_objects['metNames'], met_index_to_delete)
    cobra_specific_objects['metFormulas'] = np.delete(cobra_specific_objects['metFormulas'], met_index_to_delete)
    cobra_specific_objects['b'] = np.delete(cobra_specific_objects['b'], met_index_to_delete)

    for i in idSp_to_remove:
        model['idSp'].remove(i)
    return model, cobra_specific_objects


def account_for_duplicate_entries(seq, dups):
    count_dict = {}
    seq_copy = []
    for i in seq:
        if i in dups:
            if i not in count_dict:
                count_dict[i] = 1
            else:
                count_dict[i] += 1
            seq_copy.append(i+str(count_dict[i]))
        else:
            seq_copy.append(i)
    return seq_copy


def find_duplicate_entries(seq):
    seen = set()
    seen_add = seen.add
    seen_dups = set(x for x in seq if x in seen or seen_add(x))
    return list(seen_dups) 


def model_export(model, cobra_specific_objects, model_desc):
    #Convert EXAMO data structures into COBRA compliant data structures
    dups = find_duplicate_entries(model['idRs'])
    rxns_copy = account_for_duplicate_entries(model['idRs'],dups)
    rxns_list = []
    for i in rxns_copy:
        rxn = name_sub_back(i)
        rxns_list.append(rxn)
    rxns_matlab = np.zeros((len(rxns_list),), dtype=np.object)
    rxns_matlab[:] = rxns_list
    rxns_matlab = rxns_matlab[np.newaxis].T

    dups = find_duplicate_entries(model['idSp'])
    mets_copy = account_for_duplicate_entries(model['idSp'],dups)
    mets_list = []
    for i in mets_copy:
        met = name_sub_back(i)
        mets_list.append(met)
    mets_matlab = np.zeros((len(mets_list),), dtype=np.object)
    mets_matlab[:] = mets_list
    mets_matlab = mets_matlab[np.newaxis].T

    #Create gene list for COBRA model
    genes_list = []
    for t in model['idRs']:
        values = model['rxns'][t]['genes']
        values_split = values.split('or')
        for j in values_split:
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
                    if k not in genes_list:
                        genes_list.append(k)

    #Create dictionary for gene occurrence to replace genes with their index in grRules for creation of rules object
    genes_list_dict = {}
    for i, j in enumerate(genes_list):
        genes_list_dict[j] = i

    #Create reaction gene matrix and rules object
    rxnGeneMat = sp.sparse.csr_matrix((len(model['idRs']),len(genes_list)))
    rxnGeneMat = sp.sparse.lil_matrix(rxnGeneMat)
    rxn_index = 0
    rules = cobra_specific_objects['grRules'].copy()
    for i in range(0,len(model['idRs'])):
        rxn_index += 1
        gene_index = 0
        rxn_index_0 = []
        gene_index_0 = []    
        for j in genes_list:
            gene_index += 1
            genes_search = re.search(str(j), str(cobra_specific_objects['grRules'][i]))
            if genes_search is not None: 
                rxn_index_0.append(rxn_index - 1)
                gene_index_0.append(gene_index - 1)
            rules[i] = re.sub(j,'x(%s)' % genes_list_dict[j],str(rules[i]))
            rules[i] = re.sub('or','|',str(rules[i]))
            rules[i] = re.sub('and','&',str(rules[i]))
        rxnGeneMat[rxn_index_0, gene_index_0] = 1

    genes_matlab = np.zeros((len(genes_list),), dtype=np.object)
    genes_matlab[:] = genes_list
    genes_matlab = genes_matlab[np.newaxis].T

    ub = []
    for t in model['idRs']:
        ub.append(model['rxns'][t]['ub'])
    ub_matlab = np.zeros((len(ub),), dtype=np.float64)
    ub_matlab[:] = ub
    ub_matlab = ub_matlab[np.newaxis].T

    lb = []
    for t in model['idRs']:
        lb.append(model['rxns'][t]['lb'])    
    lb_matlab = np.zeros((len(lb),), dtype=np.float64)
    lb_matlab[:] = lb
    lb_matlab = lb_matlab[np.newaxis].T

    rev = []
    for t in model['idRs']:
        rev.append(model['rxns'][t]['reversible'])
    rev_cobra = np.zeros((len(rev),), dtype=np.float64)
    rev_cobra[:] = rev
    rev_cobra = rev_cobra[np.newaxis].T

    grRules = cobra_specific_objects['grRules'][np.newaxis].T

    rules = rules[np.newaxis].T

    c = cobra_specific_objects['c'][np.newaxis].T

    subsystem = cobra_specific_objects['subsystem'][np.newaxis].T

    metNames = cobra_specific_objects['metNames'][np.newaxis].T

    metFormulas = cobra_specific_objects['metFormulas'][np.newaxis].T

    b = cobra_specific_objects['b'][np.newaxis].T

    S = sp.sparse.coo_matrix(model['S'],dtype=np.float64)

    rxnGeneMat = sp.sparse.coo_matrix(rxnGeneMat,dtype=np.float64)

    model_matlab = {'rxns': rxns_matlab, 'mets': mets_matlab, 'ub': ub_matlab, 'lb': lb_matlab, 'S': S, 'grRules': grRules, 'rules': rules, 'genes': genes_matlab, 'rxnGeneMat': rxnGeneMat, 'rev': rev_cobra, 'c': c, 'subsystem': subsystem, 'metNames': metNames, 'metFormulas': metFormulas, 'b': b, 'description': model_desc[:-4].split('/')[-1]}
    sp.io.savemat('%s' % model_desc[:-4], {model_desc[:-3].replace('.','').split('/')[-1]: model_matlab}, appendmat=True)
    #sp.io.savemat('%s' % model_desc[:-4], {model_desc[:-4].split('/')[-1]: model_matlab}, appendmat=True, oned_as="column")

def remove_inactive_rxns_and_account_for_biomass(model_desc, args_removeinactiverxnsandbalance, args_e, args_metabolite2carbon, metFormulas_list):
    #Remove inactive rxns if supplied from command line, and remove mets only associated with those rxns. This will then allow easier balancing of the final model and be able to account for biomass.
    if args_removeinactiverxnsandbalance:
        #Import the model and convert to an array based model.
        cobra_model = cobra.io.load_matlab_model('%s.mat' % model_desc[:-4])
        cobra_model = ArrayBasedModel(cobra_model)

        #Remove inactive rxns and unused metabolites and export the COBRA model.
        solution = cobra.flux_analysis.flux_variability_analysis(cobra_model, solver='gurobi')
        rxn_list = []
        for i in cobra_model.reactions:
            if ((solution.loc[i.id,'maximum'] == 0) and (solution.loc[i.id,'minimum'] == 0)):
                rxn_list.append(i)
        for rxn in rxn_list:
            rxn.remove_from_model(cobra_model)
        mets_removed = prune_unused_metabolites(cobra_model)
        cobra.io.save_matlab_model(cobra_model, '%s.mat' % model_desc[:-4], varname=model_desc[:-4].split('/')[-1])

        #Import back into EXAMO format to make additional changes and identify metabolites in the biomass rxn that are in unbalanced rxns. Then export back out as a COBRA model.  
        model, cobra_specific_objects, mets_to_extracellular_comp, rxns_original, biomass_rxn = set_parameter('%s.mat' % model_desc[:-4], False, True, '_e_', None, None, None)
        model, cobra_specific_objects, unbalanced_rxns_mets_unique_list, unbalanced_rxns_mets_potential_list = balance_reactions(model, cobra_specific_objects, mets_to_extracellular_comp, rxns_original, biomass_rxn, args_metabolite2carbon, metFormulas_list, False, removed_inactive_rxns_and_balance = True)
        model, cobra_specific_objects = metabolite_cleanup(model,cobra_specific_objects)
        model_export(model, cobra_specific_objects, model_desc)
        
        #Import the model and convert into an array based model. First try to remove metabolites from the biomass rxn that are only in unbalanced rxns. 
        cobra_model = cobra.io.load_matlab_model('%s.mat' % model_desc[:-4])
        cobra_model = ArrayBasedModel(cobra_model)
        unbalanced_rxns_mets_unique_dict = {}
        for met in unbalanced_rxns_mets_unique_list:
            met_sub = name_sub_back(met)
            unbalanced_rxns_mets_unqiue_dict[met_sub] = -1*model['rxns'][biomass_rxn]['reactants'][met]
        solution = cobra_model.optimize(solver='gurobi')
        with cobra_model:
            for i in cobra_model.reactions:
                if i.id == biomass_rxn[2:]:
                    i.subtract_metabolites(unbalanced_rxns_mets_unique_dict)
                    solution = cobra_model.optimize(solver='gurobi')
                    if solution.f != 0:
                        if len(unbalanced_rxns_mets_unique_list) == 0:
                            print ("\n")
                            print ("Biomass rxn was accounted for in balancing, and no additional metabolites needed to be removed as reactants")
                        else:
                            print ("\n")
                            print ("Biomass rxns was accounted for in balancing by removing the following metabolites")
                            print (unbalanced_rxns_mets_unique_list) 
                        solution = cobra.flux_analysis.flux_variability_analysis(cobra_model, solver='gurobi')
                        rxn_list = []
                        for i in cobra_model.reactions:
                            if ((solution.loc[i.id,'maximum'] == 0) and (solution.loc[i.id,'minimum'] == 0)):
                                rxn_list.append(i)
                        for rxn in rxn_list:
                            rxn.remove_from_model(cobra_model)
                        mets_removed = prune_unused_metabolites(cobra_model)
                        cobra.io.save_matlab_model(cobra_model, '%s.mat' % model_desc[:-4], varname=model_desc[:-4].split('/')[-1])
                        return


        #If a solution was not optimizable upon removing unbalanced and inactive rxns, remove metabolites from the biomass rxn based off of mets appearing in unbalanced rxns
        unbalanced_rxns_mets_potential_dict = {}
        for met in unbalanced_rxns_mets_potential_list:
            met_sub = name_sub_back(met)
            unbalanced_rxns_mets_potential_dict[met_sub] = -1*model['rxns'][biomass_rxn]['reactants'][met]
        combs_unbalanced_rxns_mets_potential_dict = {}
        for n in range(len(unbalanced_rxns_mets_potential_dict)):
            combs_unbalanced_rxns_mets_potential_dict[n+1] = {}
        for n in range(len(unbalanced_rxns_mets_potential_dict)):
            for combs in itertools.combinations(sorted(unbalanced_rxns_mets_potential_dict),n+1):
                combs_list = list(combs)
                string = ''.join(combs_list)
                combs_unbalanced_rxns_mets_potential_dict[n+1][string] = {}
                for key in combs:
                    combs_unbalanced_rxns_mets_potential_dict[n+1][string][key] = unbalanced_rxns_mets_potential_dict[key] 
        solution = cobra_model.optimize(solver='gurobi')
        for n in range(len(unbalanced_rxns_mets_potential_dict)):
            for key in combs_unbalanced_rxns_mets_potential_dict[n+1].keys():
                with cobra_model:
                    for i in cobra_model.reactions:
                        if i.id == biomass_rxn[2:]:
                            i.subtract_metabolites(combs_unbalanced_rxns_mets_potential_dict[n+1][key])
                            solution = cobra_model.optimize(solver='gurobi')
                            if solution.f != 0:
                                print ("\n")
                                print ("Biomass rxns was accounted for in balancing by removing the following metabolites")
                                print (key) 
                                solution = cobra.flux_analysis.flux_variability_analysis(cobra_model, solver='gurobi')
                                rxn_list = []
                                for i in cobra_model.reactions:
                                    if ((solution.loc[i.id,'maximum'] == 0) and (solution.loc[i.id,'minimum'] == 0)):
                                        rxn_list.append(i)
                                for rxn in rxn_list:
                                    rxn.remove_from_model(cobra_model)
                                mets_removed = prune_unused_metabolites(cobra_model)
                                cobra.io.save_matlab_model(cobra_model, '%s.mat' % model_desc[:-4], varname=model_desc[:-4].split('/')[-1])
                                return
        
        #Subfunction to return what metabolites need to be removed from the biomass rxn in additon to the metabolites in unbalanced rxns.     
        def unbalanced_rxns_mets_potential_dict_2_function():
            unbalanced_rxns_mets_potential_dict_2 = {}
            not_in_unbalanced_rxns_mets_potential_list = []
            for met in model['rxns'][biomass_rxn]['reactants']:
                if met not in unbalanced_rxns_mets_potential_list:
                    met_sub = name_sub_back(met)
                    unbalanced_rxns_mets_potential_dict_2[met_sub] = -1*model['rxns'][biomass_rxn]['reactants'][met]
            combs_unbalanced_rxns_mets_potential_dict_2 = {}
            combs_combined = {}
            for n in range(len(unbalanced_rxns_mets_potential_list),len(unbalanced_rxns_mets_potential_dict_2.keys())+len(unbalanced_rxns_mets_potential_list)+1):
                combs_unbalanced_rxns_mets_potential_dict_2[n] = {}
                combs_combined[n] = {}
            #Add the possibility of adding 5 more additional metabolites. If add more than this, can time out in creating dictionaries depending on number of metabolites already being removed. 
            for n in range(len(unbalanced_rxns_mets_potential_list),len(unbalanced_rxns_mets_potential_list)+5):
                for combs in itertools.combinations(sorted(unbalanced_rxns_mets_potential_dict_2),n-len(unbalanced_rxns_mets_potential_list)):
                    combs_list = list(combs)
                    string2 = ''.join(combs_list)
                    combs_unbalanced_rxns_mets_potential_dict_2[n][string2] = {}
                    combs_combined[n][string2] = {}
                    for key in combs:
                        combs_unbalanced_rxns_mets_potential_dict_2[n][string2][key] = unbalanced_rxns_mets_potential_dict_2[key]
                    combs_combined[n][string2] = dict(list(combs_unbalanced_rxns_mets_potential_dict_2[n][string2].items())+list(combs_unbalanced_rxns_mets_potential_dict[len(unbalanced_rxns_mets_potential_list)][string].items()))  
            unbalanced_rxns_mets_potential_list_2 = list(unbalanced_rxns_mets_potential_list)
            for n in range(len(unbalanced_rxns_mets_potential_list),len(unbalanced_rxns_mets_potential_dict_2.keys())+len(unbalanced_rxns_mets_potential_list)+1):
                for key in combs_combined[n].keys():
                    with cobra_model:
                        for i in cobra_model.reactions:
                            if i.id == biomass_rxn[2:]:
                                i.subtract_metabolites(combs_combined[n][key])
                                solution = cobra_model.optimize(solver='gurobi')
                                if solution.f != 0:
                                    for met in combs_combined[n][key].keys():
                                        met = name_sub(met, "M_") 
                                        unbalanced_rxns_mets_potential_list_2.append(met)    
                                    return unbalanced_rxns_mets_potential_list_2

        #If a solution was still not optimizable, remove more metabolites from the biomass reaction 
        unbalanced_rxns_mets_potential_list_2 = unbalanced_rxns_mets_potential_dict_2_function()

        unbalanced_rxns_mets_potential_dict_3 = {}
        for met in unbalanced_rxns_mets_potential_list_2:
            met_sub = name_sub_back(met)
            unbalanced_rxns_mets_potential_dict_3[met_sub] = -1*model['rxns'][biomass_rxn]['reactants'][met]
        combs_unbalanced_rxns_mets_potential_dict_3 = {}
        for n in range(len(unbalanced_rxns_mets_potential_dict_3)):
            combs_unbalanced_rxns_mets_potential_dict_3[n+1] = {}
        for n in range(len(unbalanced_rxns_mets_potential_dict_3)):
            for combs in itertools.combinations(sorted(unbalanced_rxns_mets_potential_dict_3),n+1):
                combs_list = list(combs)
                string = ''.join(combs_list)
                combs_unbalanced_rxns_mets_potential_dict_3[n+1][string] = {}
                for key in combs:
                    combs_unbalanced_rxns_mets_potential_dict_3[n+1][string][key] = unbalanced_rxns_mets_potential_dict_3[key] 
        solution = cobra_model.optimize(solver='gurobi')
        for n in range(len(unbalanced_rxns_mets_potential_dict_3)):
            for key in combs_unbalanced_rxns_mets_potential_dict_3[n+1].keys():
                with cobra_model:
                    for i in cobra_model.reactions:
                        if i.id == biomass_rxn[2:]:
                            i.subtract_metabolites(combs_unbalanced_rxns_mets_potential_dict_3[n+1][key])
                            solution = cobra_model.optimize(solver='gurobi')
                            if solution.f != 0:
                                print ("\n")
                                print ("Biomass rxns was accounted for in balancing by removing the following metabolites")
                                print (key) 
                                solution = cobra.flux_analysis.flux_variability_analysis(cobra_model, solver='gurobi')
                                rxn_list = []
                                for i in cobra_model.reactions:
                                    if ((solution.loc[i.id,'maximum'] == 0) and (solution.loc[i.id,'minimum'] == 0)):
                                        rxn_list.append(i)
                                for rxn in rxn_list:
                                    rxn.remove_from_model(cobra_model)
                                mets_removed = prune_unused_metabolites(cobra_model)
                                cobra.io.save_matlab_model(cobra_model, '%s.mat' % model_desc[:-4], varname=model_desc[:-4].split('/')[-1])
                                return
