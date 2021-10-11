from numpy.core.arrayprint import str_format
import pandas as pd
import random

from .attribute import *
from .panel import *
class AttributesRanking():

    def __init__(self, attributes, star):
        # preprocessed groupBy_ranking
        class_ab = [at for at in attributes if at.classe == 'a']
        class_ab += [at for at in attributes if at.classe == 'b'] # function sorted() stable : if 2 equal values, the lowest indiced-element is put first
        class_c = [at for at in attributes if at.classe == 'c']
        self.preprocessed = dict()
        self.preprocessed['groupBy'] = sorted(class_ab, key=lambda at : at.entropy, reverse = True) 
        self.preprocessed['groupBy'] += sorted(class_c, key=lambda at : at.adomSize, reverse = False)

        # preprocess_aggregation_ranking
        numeric = [at for at in attributes if at.is_numeric]
        self.preprocessed['aggregation'] = sorted(numeric, key=lambda at : at.variance, reverse = True)
        self.preprocessed['aggregation'].append(star)

        # initialize general and local dict that will be updated during dashboard generation
        self.general = dict()
        self.general['groupBy'] = {'good': self.preprocessed['groupBy'], 'less_good': [], 'bad': [], 'very_bad':[]}
        self.general['aggregation'] = {'good': self.preprocessed['aggregation'], 'less_good': [], 'bad': [], 'very_bad':[]}
        self.local = dict()
        self.local['groupBy'] = {'good': self.preprocessed['groupBy'], 'less_good': [], 'bad': [], 'very_bad':[]}
        self.local['aggregation'] = {'good': self.preprocessed['aggregation'], 'less_good': [], 'bad': [], 'very_bad':[]}
        self.qualities = ['good', 'less_good', 'bad', 'very_bad']
        self.pairwise_qualities_1 = []
        for quality in self.qualities:
            self.pairwise_qualities_1 += [(None, quality), (quality, None)]
        self.pairwise_qualities_2 = [ ('good', 'good'), ('good', 'less_good'), ('less_good', 'good'), ('less_good', 'less_good'), ('less_good', 'bad'), ('bad', 'less_good'), ('bad', 'bad'), ('bad', 'very_bad'), ('very_bad', 'bad'), ('very_bad', 'very_bad') ]

    def calculate_general_ranking(self, gb_or_agg, diversity):
        """ 
        calculate global ranking for gb_or_agg = 'groupBy' ou 'aggregation'
        (depending only on:
        - history of interactions (report bad GROUP BY)
        - potential diversity (if not achieved)
        """
        # calculate ordered bad_list for groupBy (no bad list for aggregation, because bad aggregation attributes depend on the current panel)
        if gb_or_agg == 'groupBy':
            bad_list = [at for at in self.preprocessed['groupBy'] if at.bad_groupBy > 0]
            if len(bad_list) != 0:
                bad_list = sorted(bad_list, key=lambda at : at.bad_groupBy)
            good_list = [at for at in self.preprocessed[gb_or_agg] if at not in bad_list]
        else:
            good_list = self.preprocessed['aggregation']
        # deal with diversity
        if diversity['asked'] and not diversity['achieved']:
            self.general[gb_or_agg]['less_good'] = [at for at in good_list if at.on_dashboard]
            self.general[gb_or_agg]['good'] = [at for at in good_list if not at.on_dashboard]
            if gb_or_agg == 'groupBy':
                self.general[gb_or_agg]['very_bad'] = [at for at in bad_list if at.on_dashboard]
                self.general[gb_or_agg]['bad'] = [at for at in bad_list if not at.on_dashboard]
        else:
            self.general[gb_or_agg]['good'] = good_list
            self.general[gb_or_agg]['less_good'] = []
            if gb_or_agg == 'groupBy':
                self.general[gb_or_agg]['bad'] = bad_list
                self.general[gb_or_agg]['very_bad'] = []

    def dict_to_list(self, gb_or_agg, diversity):
        """
        translate general ranking in list (for interface)
        """
        self.calculate_general_ranking(gb_or_agg, diversity)
        dico = self.general[gb_or_agg]
        liste = []
        for quality in self.qualities:
            liste += [at.name for at in dico[quality]]
        if '*' in liste:
            liste.remove('*')
        return liste

    def calculate_ranking(self, gb_or_agg, panel, diversity, forbidden_attributes=list()):
        """
        calculate local ranking (depending on current panel, history of interactions, diversity)
        bad_list :
            - for GROUP BY : bad GROUP BY attributes + the ones that are already on dashboard (if diversity asked but not achieved)
            - for aggregation : if GROUP BY attributes already chosen, bad aggregation attributes + the ones that are already on dashboard (if diversity asked but not achieved)
        forbidden_list :
            - if U reported bad attributes, the ones that have just been reported
            + the ones that are already on GROUP BY or aggregation for this panel
        ranking = dict() with
            key 'bad' for attributes in bad_list
            key 'good' for others
        """
        self.calculate_general_ranking(gb_or_agg, diversity)
        # calculate list of forbidden attributes
        forbidden_list = forbidden_attributes + [at for at in panel.groupBy + list(panel.aggregates.keys())]
        # calculate lists of bad attributes
        if gb_or_agg == 'aggregation':
            if len(forbidden_list) == len(self.preprocessed['groupBy']):    # in case all attributes are forbidden 
                forbidden_list = list(panel.aggregates.keys())              # allow forbidden except already_on_same
            bad_list = [agg_at for gb_at in panel.groupBy for agg_at in gb_at.bad_agg]
            bad_list = [at for at in bad_list if at not in forbidden_list]
            if diversity['asked'] and not diversity['achieved']:
                self.local['aggregation']['bad'] = [at for at in bad_list if not at.on_dashboard]
                self.local['aggregation']['very_bad'] = [at for at in bad_list if at.on_dashboard]
        else:
            if len(forbidden_list) == len(self.preprocessed['groupBy']):    # in case all attributes are forbidden,
                forbidden_list = panel.groupBy                              # allow forbidden except already_on_same
            self.local['groupBy']['bad'] = [at for at in self.general['groupBy']['bad'] if at not in forbidden_list]
            self.local['groupBy']['very_bad'] = [at for at in self.general['groupBy']['very_bad'] if at not in forbidden_list]
        # calculate list of good attributes
        self.local[gb_or_agg]['less_good'] = [at for at in self.general[gb_or_agg]['less_good'] if at not in forbidden_list]
        self.local[gb_or_agg]['good'] = [at for at in self.general[gb_or_agg]['good'] if at not in forbidden_list]
        