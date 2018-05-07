# -*- coding: utf-8 -*-

"""ComPath HGNC extension to Bio2BEL HGNC."""

import itertools as itt
from collections import Counter

from bio2bel_hgnc.models import GeneFamily, HumanGene
from compath_utils import CompathManager


class Manager(CompathManager):
    """An minimized version of the Bio2BELManager manager adapted for ComPath"""

    def query_gene_set(self, gene_set):
        """Returns pathway counter dictionary

        :param list[str] gene_set: gene set to be queried
        :rtype: dict[str,dict]]
        :return: Enriched pathways with mapped pathways/total
        """
        proteins = self._query_proteins_in_hgnc_list(gene_set)

        pathways_lists = [
            protein.get_pathways_ids()
            for protein in proteins
        ]

        # Flat the pathways lists and applies Counter to get the number matches in every mapped pathway
        pathway_counter = Counter(itt.chain(*pathways_lists))

        enrichment_results = dict()

        for hgnc_family, proteins_mapped in pathway_counter.items():
            pathway = self.get_pathway_by_pathway_id(hgnc_family)

            pathway_gene_set = pathway.get_gene_set()  # Pathway gene set

            enrichment_results[pathway.hgnc_family] = {
                "pathway_id": pathway.hgnc_family,
                "pathway_name": pathway.name,
                "mapped_proteins": proteins_mapped,
                "pathway_size": len(pathway_gene_set),
                "pathway_gene_set": pathway_gene_set,
            }

        return enrichment_results

    def _query_proteins_in_hgnc_list(self, gene_set):
        """Returns the proteins in the database within the gene set query

        :param list[str] gene_set: hgnc symbol lists
        :rtype: list[compath_neurommsig_ad.models.Protein]
        :return: list of proteins
        """
        return self.session.query(HumanGene).filter(HumanGene.symbol.in_(gene_set)).all()

    def get_pathway_by_name(self, name):
        """Gets all Gene symbols in gene families

        :rtype: Optional[GeneFamily]
        """
        return self.session.query(GeneFamily).filter(GeneFamily.family_name == name).one_or_none()

    def get_all_hgnc_symbols(self):
        """Gets Gene Family by name

        :rtype: set[str]
        """
        return {
            gene.symbol
            for family in self.session.query(GeneFamily)
            for gene in family.hgncs
        }

    def query_pathway_by_name(self, query, limit=None):
        """Returns all pathways having the query in their names

        :param query: query string
        :param Optional[int] limit: limit result query
        :rtype: list[GeneFamily]
        """

        q = self.session.query(GeneFamily).filter(GeneFamily.family_name.contains(query))

        if limit:
            q = q.limit(limit)

        return q.all()

    def autocomplete_gene_families(self, q, limit=None):
        """Wraps the query_pathway_by_name method to return autocompletion in compath

        :param str q: query
        :param int limit: limit of matches
        :rtype: list[str]
        :return:
        """
        return list({
            gene_family.family_name
            for gene_family in self.query_pathway_by_name(q, limit=limit if limit else 10)
            # Limits the results returned to 10
            if gene_family
        })

    def get_families_gene_sets(self):
        """Gets all Gene symbols in gene families

        :rtype: dict[str,set]
        """
        return {
            family.family_name: {gene.symbol for gene in family.hgncs}
            for family in self.session.query(GeneFamily)
        }
