"""
Update
======

This module updates BOFsc in the model.

"""
#def change_gam():
def get_biomass_objective_function(model):
    from cobra.util.solver import linear_reaction_coefficients
    return linear_reaction_coefficients(model).keys()[0]

def remove_biomass_metab(dict_of_metab, biomass):
    biomass.add_metabolites(dict_of_metab)
    # print('The actual model %s solves in %s and its biomass contains %s metabolites'
    #      % (model.name, model.optimize(), len(biomass.metabolites)))

def add_biomass_metab(dict_of_metab, biomass):
    biomass.add_metabolites(dict_of_metab)
    # print('The actual model %s solves in %s and its biomass contains %s metabolites'
    #      % (model.name, model.optimize(), len(biomass.metabolites)))
    # print(biomass.reaction)

def find_in_biomass(biomass, dict_of_coefficients):
    # 1- Find metabolites in BIOMASS
    for k, v in dict_of_coefficients.iteritems():
        metab = k
        dict_addition = {k: -v}
        for r in biomass.reactants:
            if metab.id == r.id:
                #print('Found %s in biomass reaction' % (metab.id,))
                # Get the current coefficient for metab in biomass
                current_coefficient = biomass.get_coefficient(r.id)
                dict_removal = {r: -current_coefficient}
                remove_biomass_metab(dict_removal, biomass)
                add_biomass_metab(dict_addition, biomass)

def find_metabolites_in_biomass(biomass, dict_of_coefficients):
    # 1- Find metabolites in BIOMASS
    for k, v in dict_of_coefficients.iteritems():
        metab = k
        dict_addition = {k: -v}
        for r in biomass.reactants:
            if metab.id[:-2] == r.id[:-2]:
                print('Found %s in biomass reaction' % (metab.id,))
                # Get the current coefficient for metab in biomass
                current_coefficient = biomass.get_coefficient(r.id)
                dict_removal = {r: -current_coefficient}
                remove_biomass_metab(dict_removal, biomass)
                add_biomass_metab(dict_addition, biomass)

def update_biomass(dict_of_coefficients, model):
    """
    Updates the biomass coefficients given the input dictionary.

    :param dict_of_coefficients: a dictionary of metabolites and coefficients

    :param model: the model to be modified

    :return: none
    """
    biomass = get_biomass_objective_function(model)
    find_in_biomass(biomass, dict_of_coefficients)

def update_biomass_metabolites(dict_of_coefficients, model):
    """
    Updates the biomass coefficients given the input dictionary.

    :param dict_of_coefficients: a dictionary of metabolites and coefficients

    :param model: the model to be modified

    :return: none
    """
    biomass = get_biomass_objective_function(model)
    find_metabolites_in_biomass(biomass, dict_of_coefficients)

def update_maintenance(gams,model,RNA_atp):
    #Get the biomass objective function
    biomass = get_biomass_objective_function(model)
    # GAM is updated in the BOF as the new ATP coefficient in the BOF
    dict_of_coefficients = {biomass.metabolites.get_by_id('atp_c'):gams['GAM'] + RNA_atp}
    find_in_biomass(biomass,dict_of_coefficients)
    #NGAM is the new objective value of the ATP maintenance reaction
    model.reactions.ATPM.lower_bound = abs(gams['NGAM'])