import json
import logging as log
import spm2olca.mappings as maps
import spm2olca.model as model
from .util import as_path
import zipfile as zipf


class Pack(object):

    def __init__(self, methods, skip_unmapped_flows=False, unit_map=None,
                 flow_map=None):
        self.methods = methods
        self.unit_map = maps.UnitMap.create() if unit_map is None else unit_map
        self.flow_map = maps.FlowMap() if flow_map is None else flow_map
        self.skip_unmapped_flows = ((flow_map is not None) and
                                    skip_unmapped_flows)
        self._gen_categories = {}
        self._gen_flows = {}

    def to(self, zip_file):
        pack = zipf.ZipFile(zip_file, mode='a', compression=zipf.ZIP_DEFLATED)
        for method in self.methods:
            self._method(method, pack)
        pack.close()

    def _method(self, method: model.Method, pack: zipf.ZipFile):
        obj = {'@type': 'ImpactMethod',
               '@id': method.uid,
               'name': method.name,
               'description': method.comment,
               'impactCategories': [],
               'nwSets': []}
        for category in method.impact_categories:
            ref = {'@type': 'ImpactCategory', '@id': category.uid}
            obj['impactCategories'].append(ref)
            self._impact_category(category, pack)
        for nw_set in method.nw_sets:
            ref = {'@type': 'NwSet', '@id': nw_set.uid}
            obj['nwSets'].append(ref)
            self._nw_set(nw_set, method, pack)
        dump(obj, 'lcia_methods', pack)

    def _nw_set(self, nw_set: model.NwSet, method: model.Method, pack):
        obj = {'@type': 'NwSet',
               '@id': nw_set.uid,
               'name': nw_set.name,
               'weightedScoreUnit': method.weighting_unit,
               'factors': []}
        for impact in method.impact_categories:
            n_factor = None
            w_factor = None
            dam_category, dam_factor = method.get_damage_factor(impact)
            if dam_category is not None:
                w_factor = nw_set.get_weighting_factor(dam_category)
                if w_factor is not None:
                    w_factor *= dam_factor
                n_factor = nw_set.get_normalisation_factor(dam_category)
                if n_factor is not None:
                    n_factor = dam_factor / n_factor
            else:
                w_factor = nw_set.get_weighting_factor(impact.name)
                n_factor = nw_set.get_normalisation_factor(impact.name)
            f = {'@type': 'NwFactor',
                 'impactCategory': {'@type': 'ImpactCategory',
                                    '@id': impact.uid},
                 'normalisationFactor': n_factor,
                 'weightingFactor': w_factor}
            obj['factors'].append(f)
        dump(obj, 'nw_sets', pack)

    def _impact_category(self, category: model.ImpactCategory, pack):
        obj = {'@type': 'ImpactCategory',
               '@id': category.uid,
               'name': category.name,
               'referenceUnitName': category.ref_unit,
               'impactFactors': []}
        for factor in category.factors:
            f_obj = self._factor(factor, pack)
            if f_obj is None:
                continue
            obj['impactFactors'].append(f_obj)
        dump(obj, 'lcia_categories', pack)

    def _factor(self, factor: model.ImpactFactor, pack):
        flow = self.flow_map.get(factor.flow_uid)

        # create LCIA factor for mapped flow
        if flow is not None:
            val = factor.value / flow.factor
            obj = {'@type': 'ImpactFactor',
                   'value': val,
                   'flow': {'@type': 'Flow', '@id': flow.olca_flow_id,
                            'name': flow.olca_flow_name},
                   'unit': {'@type': 'Unit', '@id': flow.olca_unit_id},
                   'flowProperty': {'@type': 'FlowProperty',
                                    '@id': flow.olca_property_id}}
            return obj

        path = as_path(factor.category, factor.sub_category, factor.name,
                       factor.unit)

        # skip unmapped flow
        if self.skip_unmapped_flows:
            log.warning('skip unmapped flow ' + path)
            return None

        # get the unit mapping
        unit_entry = self.unit_map.get(factor.unit)
        if unit_entry is None:
            log.error('unknown unit %s: skipped factor for %s' %
                      (factor.unit, path))
            return None

        # create a new flow
        if factor.flow_uid not in self._gen_flows:
            log.info('Create flow: %s -> %s' % (path, factor.flow_uid))
            self._create_flow(factor, unit_entry, pack)
            self._gen_flows[factor.flow_uid] = True

        obj = {'@type': 'ImpactFactor',
               'value': factor.value,
               'flow': {'@type': 'Flow', '@id': factor.flow_uid},
               'unit': {'@type': 'Unit', '@id': unit_entry.unit_id},
               'flowProperty': {'@type': 'FlowProperty',
                                '@id': unit_entry.property_id}}
        return obj

    def _create_flow(self, factor: model.ImpactFactor,
                     unit_entry: maps.UnitEntry, pack):
        category_id = self._flow_category(factor, pack)
        obj = {'@type': 'Flow',
               '@id': factor.flow_uid,
               'name': factor.name,
               'category': {'@type': 'Category', '@id': category_id},
               'flowType': 'ELEMENTARY_FLOW',
               'cas': factor.cas,
               'flowProperties': [{
                   '@type': 'FlowPropertyFactor',
                   'referenceFlowProperty': True,
                   'flowProperty': {
                       '@type': 'FlowProperty',
                       '@id': unit_entry.property_id}
               }]}

        dump(obj, 'flows', pack)

    def _flow_category(self, factor: model.ImpactFactor, pack) -> str:
        sub_uid = factor.flow_sub_category_uid
        if sub_uid in self._gen_categories:
            return sub_uid
        parent_uid = factor.flow_category_uid
        if parent_uid not in self._gen_categories:
            obj = {'@type': 'Category', '@id': parent_uid,
                   'name': factor.category, 'modelType': 'FLOW',
                   'category': {'@type': 'Category',
                                '@id': 'elementary-flows'}}
            dump(obj, 'categories', pack)
            self._gen_categories[parent_uid] = True
        obj = {'@type': 'Category',
               '@id': sub_uid,
               'name': factor.sub_category,
               'modelType': 'FLOW',
               'category': {'@type': 'Category', '@id': parent_uid}}
        dump(obj, 'categories', pack)
        self._gen_categories[sub_uid] = True
        return sub_uid


def dump(obj, folder, pack):
    path = '%s/%s.json' % (folder, obj['@id'])
    s = json.dumps(obj)
    pack.writestr(path, s)
