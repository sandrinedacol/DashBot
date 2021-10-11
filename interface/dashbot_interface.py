import pandas as pd
import json

from implem.dashbot import *

class Interface(DashBot):

    def __init__(self, print_things = True):
        mode = "interface"
        DashBot.__init__(self, mode)
        self.args.process_parameters()

    def do_preprocess_data(self, dataset_name):
        
        self.preprocess_data(dataset_name)
        # get info
        attributes_characteristics = self.attributes_characteristics_to_html()
        attributes_info = self.attributes_info_to_json()
        value_distributions, attributes_names = self.get_value_distributions()
        return {'dataset' : {
                    'n_attributes': len(self.attributes),
                    'n_rows': self.dataset.shape[0]
                    },
                'attributes' : {
                    'names' : attributes_names,
                    'characteristics' : attributes_characteristics,
                    'info' : attributes_info,
                    'numeric' : [at.name for at in self.attributes if at.is_numeric],
                    'value_distributions' : value_distributions,
                    'rankings' : {
                        'groupBy': [at.name for at in self.ranking.preprocessed['groupBy']],
                        'aggregation': [at.name for at in self.ranking.preprocessed['aggregation'] if at.name != '*']
                    }
                },
                'vizu': {
                    'pie_cloud_threshold': self.args.pie_cloud_threshold
                    }
            }

    def set_diversity(self, boolean, start_generation):
        self.diversity['asked'] = boolean
        if not start_generation:
            self.panel = Panel(self.attributes_and_star)
        return {
            'attributes' : {
                'rankings': {
                    'groupBy': self.ranking.dict_to_list('groupBy', self.diversity),
                    'aggregation': self.ranking.dict_to_list('aggregation', self.diversity)
                }
            },
            'diversity': self.diversity
        }

    # def replace_slash(string):
    #     new_string = string.replace('-encoded_slash-', "/")
    #     return new_string

    def translate_user_feedback(self, user_feedback, refinement_info):
        self.user_feedback = user_feedback
        if refinement_info == 'null':
            self.explanations_to_apply = dict()
        elif refinement_info == 'softmax' or refinement_info == 'e-greedy':
            self.MAB_algo = refinement_info
            self.explanations_to_apply = dict()
        else:
            self.explanations_to_apply = {
            'groupBy_to_add': [],
            'aggregation_to_add': [],
            'groupBy_to_remove': [],
            'aggregation_to_remove': [],
            'functions_to_change': dict()
        }
            groupBy_to_add_string, aggregation_to_add_string, groupBy_to_remove_string, aggregation_to_remove_string, functions_to_change_string = tuple(refinement_info.split('_AND_'))
            # add attributes
            if groupBy_to_add_string != '':
                groupBy_to_add_names = groupBy_to_add_string.split('_add_')[1:]
                self.explanations_to_apply['groupBy_to_add'] = [att for att in self.attributes if att.name in groupBy_to_add_names]
            if  aggregation_to_add_string != '':
                aggregation_to_add_names = aggregation_to_add_string.split('_add_')[1:]
                self.explanations_to_apply['aggregation_to_add'] = [att for att in self.attributes_and_star if att.name in aggregation_to_add_names]
            # change functions
            if functions_to_change_string != '':
                functions_to_change_names = dict()
                functions_to_change_list = functions_to_change_string.split('_change_')[1:]
                for agg_at in functions_to_change_list:
                    agg_att_name = agg_at.split('_with-func-')[0]
                    agg_att_functions = agg_at.split('_with-func-')[1:]
                    functions_to_change_names[agg_att_name] = agg_att_functions
                functions_to_change = dict()
                agg_att_list = [att for att in self.attributes if att.name in functions_to_change_names.keys()]
                for agg_att in agg_att_list:
                    functions_to_change[agg_att] = functions_to_change_names[agg_att.name]
                self.explanations_to_apply['functions_to_change'] = functions_to_change
            # remove_attributes
            if groupBy_to_remove_string != '':
                groupBy_to_remove_names = groupBy_to_remove_string.split('_remove_')[1:]
                self.explanations_to_apply['groupBy_to_remove'] = [att for att in self.attributes if att.name in groupBy_to_remove_names]
            if aggregation_to_remove_string != '':
                aggregation_to_remove_names = aggregation_to_remove_string.split('_remove_')[1:]
                self.explanations_to_apply['aggregation_to_remove'] = [att for att in self.attributes_and_star if att.name in aggregation_to_remove_names]
            # clean explanations_to_apply
            keys_to_delete = []
            for expl, attributes in self.explanations_to_apply.items():
                if not attributes:
                    keys_to_delete.append(expl)
            for key in keys_to_delete:
                del self.explanations_to_apply[key]

    # #############################################
    #       functions for do_preprocess_data
    # #############################################

    def print_value(self, value, n):
        if value == 0:
            printed_value = '0'
        else:
            printed_value = round(value, n - int(math.floor(math.log10(abs(value)))) - 1)
            printed_value = str(printed_value)
            if printed_value[-2:] == '.0':
                printed_value = printed_value[:-2]
            if len(printed_value) > 5:
                if len(printed_value.split('e')) == 2:
                    vals = printed_value.split('e')
                    vals[1] = str(int(vals[1]))
                    printed_value = ("&times10<sup>").join(vals) + "</sup>"
                else:
                    val = str(printed_value).split('.')
                    if len(val) == 1:
                        v = val[0]
                        order_of_magnitude = len(v) - 1
                        entier = v[0]
                        dec = v[1:n]
                        printed_value = f"{entier}.{dec}&times10<sup>{order_of_magnitude}</sup>"
                    else:
                        v = val[1]
                        order_of_magnitude = - len(v) + n - 1
                        printed_value = f"{v[-n]}.{v[-n+1:]}&times10<sup>{order_of_magnitude}</sup>"
        return printed_value

    def get_value_distributions(self):
        discretized_names = []
        for att in self.attributes:
            if att.discretized:
                discretized_names.append(f'discretized_{att.name}')
            else:
                discretized_names.append(att.name)
        attributes_dataset = self.dataset[discretized_names]  # .transpose().to_json()
        # for att in attributes:
        #     if att.discretized:
        #         column = attributes_dataset[[f'discretized_{att.name}']]
        #         for i in range(len(column)):
        #             if not column.isna().loc[i,f'discretized_{att.name}']:
        #                 interval = attributes_dataset.loc[i,f'discretized_{att.name}']
        #                 new_interval = f'{interval.left}_{interval.right}'
        #             attributes_dataset.at[i,f'discretized_{att.name}'] = new_interval
        attributes_names = []
        for discretized_name in discretized_names:
            liste = discretized_name.split('_')
            if liste[0] == 'discretized':
                attributes_names.append('_'.join(liste[1:]))
            else:
                attributes_names.append(discretized_name)
        attributes_dataset.columns = attributes_names
        value_distributions = dict()
        for att in self.attributes :
            serie = attributes_dataset.loc[:,att.name]
            value_count = serie.value_counts().to_dict()
            name = att.name
            value_count_list = list()
            for value, count in value_count.items():
                if att.discretized:
                    if att.type == 'int':
                        value = [int(x) for x in value.split('_')]
                    elif att.type == 'float':
                        value = [float(x) for x in value.split('_')]
                    elif att.type == '<M8[ns]':
                        pass
                value_count_list.append( {'value' : value, 'count' : count} )
            value_distributions[name] = value_count_list
        return value_distributions, attributes_names

    def attributes_characteristics_to_html(self):
        dataframe = pd.DataFrame()
        for att in self.attributes:
            dataframe.loc['discretized', att.name] = att.discretized
            dataframe.loc['is numeric', att.name] = att.is_numeric
            if att.is_numeric:
                dataframe.loc['variance', att.name] = self.print_value(att.variance, 2)
            dataframe.loc['adomSize', att.name] = att.adomSize
            dataframe.loc['classe', att.name] = att.classe
            dataframe.loc['entropy', att.name] = self.print_value(att.entropy, 2)
        dataframe = dataframe.transpose()
        # attributes_characteristics = json.loads(dataframe.to_json())
        dataframe = dataframe.to_html(na_rep='-', escape=False, justify ='left')
        attributes_characteristics = ('\n').join(dataframe.split('\n')[1:])
        attributes_characteristics = '<table class="table table-striped table-sm">\n' + attributes_characteristics  # table-hover
        return attributes_characteristics

    def attributes_info_to_json(self):
        dataframe = pd.DataFrame()
        for att in self.attributes:
            dataframe.loc['discretized', att.name] = att.discretized
            dataframe.loc['is numeric', att.name] = att.is_numeric
            if att.is_numeric:
                dataframe.loc['variance', att.name] = att.variance
            dataframe.loc['adomSize', att.name] = att.adomSize
            dataframe.loc['classe', att.name] = att.classe
            dataframe.loc['entropy', att.name] = att.entropy
        # dataframe = dataframe.transpose()
        attributes_info = json.loads(dataframe.to_json())
        return attributes_info

    # #############################################
    #       functions for dashboard_generation
    # #############################################

    def check_if_recommendable(self, panel):
        """
        rewrite <check_if_recommendable> from class DashBot
        dealing with word cloud vizualisation
        """
        if self.args.pie_cloud_threshold:
            panel = self.deal_with_visu(panel)
            recommendable = panel != None
        else:
            recommendable = not self.check_in_history(panel.vector)
        return panel, recommendable

    def deal_with_visu(self, in_panel):
        """
        modify in_panel if conditions for visualization are not fulfilled
        return new panel statisfying requirements or None
        """
        # check if panel visualization might be a word cloud
        cloud_attributes = []
        for groupBy_at in in_panel.groupBy:
            if groupBy_at.adomSize >= self.args.pie_cloud_threshold:
                if not groupBy_at.is_numeric:
                    cloud_attributes.append(groupBy_at)
                else:
                    if groupBy_at.discretized_adomSize >= self.args.pie_cloud_threshold:
                        cloud_attributes.append(groupBy_at)
        # if vizu might be a word cloud
        if len(cloud_attributes) > 0:
            # restrict the panel
            random.shuffle(in_panel.groupBy)
            for gb_at in in_panel.groupBy:
                out_panel = in_panel.copy_from_vector()
                # vizu is word cloud
                if gb_at in cloud_attributes:
                    # modify panel
                    out_panel.groupBy = [gb_at]
                    panel_aggregation = list(in_panel.aggregates.keys())
                    random.shuffle(panel_aggregation)
                    for func in ['avg', 'max', 'min', 'sum', 'count']:
                        for agg_at in panel_aggregation:
                            if func in in_panel.aggregates[agg_at]:
                                out_panel.aggregates = {agg_at: [func]}
                                out_panel.attributes_to_vector()
                                # check if new
                                found = self.check_in_history(out_panel.vector)
                                # if yes, return the panel
                                if not found:
                                    return out_panel
                    out_panel = None
                # vizu is not word cloud
                else:
                    # modify panel
                    out_panel.groupBy = [at for at in out_panel.groupBy if at not in cloud_attributes]
                    out_panel.attributes_to_vector()
                    # check if vizualization might be a two_groupby and modify it if necessary
                    out_panel = self.deal_with_groupby(out_panel)
                    if out_panel:
                        return out_panel
        # if visu is not a word cloud
        else:
            # check if vizualization might be a two_groupby and modify it if necessary
            out_panel = self.deal_with_groupby(in_panel)

        return out_panel

    def deal_with_groupby(self, in_panel):
        """
        check if vizualization might be a two_groupby and modify it if necessary
        return new panel statisfying requirements or None
        """
        out_panel = in_panel.copy_from_vector()
        checked = False
        if len(in_panel.groupBy) > 1:
            if len(in_panel.groupBy) == 2:
                out_panel, checked = self.deal_with_2_groupby(out_panel)
            else:
                if 'groupBy_to_add' in self.explanations_to_apply:
                    if len(self.explanations_to_apply['groupBy_to_add']) == 1:
                        out_panel.groupBy.remove(self.explanations_to_apply['groupBy_to_add'][0])
                        out_panel.groupBy = random.sample(out_panel.groupBy, 1)
                        out_panel.groupBy += self.explanations_to_apply['groupBy_to_add']
                    else:
                        out_panel.groupBy = random.sample(self.explanations_to_apply['groupBy_to_add'], 2)
                else:
                    out_panel.groupBy = random.sample(out_panel.groupBy, 2) # TODO func de tous les paiwises attributes
                out_panel, checked = self.deal_with_2_groupby(out_panel)
        if not checked:
            found = self.check_in_history(out_panel.vector)
            if found:
                out_panel = None
        return out_panel

    def deal_with_2_groupby(self, in_panel):
        """
        select 2 aggregates if in_panel (with 2 group by) has more
        return ( panel or None, bool for 'it has been checked in history' )
        """
        # check if more than 2 aggregates
        # n_aggregates = len([f for functions in in_panel.aggregates.values() for f in functions])
        n_aggregates = 0
        for functions in in_panel.aggregates.values():
            n_aggregates += len(functions)
        # if yes, restrict the panel
        if n_aggregates > 2:
            out_panel = self.deal_with_multiple_groupbys_and_too_many_aggregates(in_panel)
            return out_panel, True
        else:
            return in_panel, False

    def deal_with_multiple_groupbys_and_too_many_aggregates(self, in_panel):
        """
        modify panels that does not meet requirements for visualization
        return new panel or None
        """
        # count or not count?
        count = False
        if self.star in in_panel.aggregates.keys():
            count = True
        # find priority aggregates
        priority_aggregates = []
        if 'functions_to_change' in self.explanations_to_apply:
            for agg_at, functions in self.explanations_to_apply['functions_to_change'].items():
                if 'sum' in set(functions) & set(in_panel.aggregates[agg_at]):
                    priority_aggregates.append((agg_at, 'sum'))
                if len({'avg', 'min', 'max'} & set(functions) & set(in_panel.aggregates[agg_at])):
                    priority_aggregates.append((agg_at, 'num'))
        if 'aggregation_to_add' in self.explanations_to_apply:
            for agg_att in self.explanations_to_apply['aggregation_to_add']:
                if 'sum' in in_panel.aggregates[agg_att]:
                    priority_aggregates.append((agg_att, 'sum'))
                if len({'avg', 'min', 'max'} & set(in_panel.aggregates[agg_att])) > 0:
                    priority_aggregates.append((agg_att, 'num'))
        # choose among priority aggregates
        random.shuffle(priority_aggregates)
        possible_aggregates = priority_aggregates
        while len(possible_aggregates) > 0:
            chosen_aggregate = possible_aggregates.pop()
            out_panel, found = self.try_1_possible_aggregate(in_panel, chosen_aggregate, count)
            if not found:
                return out_panel
        # find non priority aggregates
        non_priority_aggregates = []
        for agg_att, functions in in_panel.aggregates.items():
            if 'sum' in functions:
                non_priority_aggregates.append((agg_att, 'sum'))
            if len({'avg', 'min', 'max'} & set(functions)):
                non_priority_aggregates.append((agg_att, 'num'))
        # choose among non priority aggregates
        random.shuffle(non_priority_aggregates)
        possible_aggregates = non_priority_aggregates
        while len(possible_aggregates) > 0:
            chosen_aggregate = possible_aggregates.pop()
            out_panel, found = self.try_1_possible_aggregate(in_panel, chosen_aggregate, count)
            if not found:
                return out_panel
        # return nothing
        return None

    def try_1_possible_aggregate(self, in_panel, chosen_aggregate, count):
        out_panel = in_panel.copy_from_vector()
        if chosen_aggregate[1] == 'sum':
            out_panel.aggregates = {chosen_aggregate[0]: ['sum']}
        else:
            chosen_functions = {'avg', 'min', 'max'} & set(in_panel.aggregates[chosen_aggregate[0]])
            out_panel.aggregates = {chosen_aggregate[0]: list(chosen_functions)}
        if count:
            out_panel.aggregates[self.star] = ['count']
        out_panel.attributes_to_vector()
        found = self.check_in_history(out_panel.vector)
        return out_panel, found

    # ---------------------------------------------------------

    def show_to_U(self):
        """
        overrides method in Parent class
        """
        super().show_to_U()
        # ---------------------------------
        # choice of visualization(s)
        # ---------------------------------
        visus = []
        # type of attributes
        agg_num = []
        agg_count = False
        agg_sum = []
        for at, functions in self.panel.aggregates.items():
            intersection = {'min', 'max', 'avg'} & set(functions)
            if len(intersection) > 0:
                agg_num.append(at)
            if 'count' in functions:
                agg_count = True
            if 'sum' in functions:
                agg_sum.append(at)
        # choice of visu type
        if len(self.panel.groupBy) == 1:                        # if only 1 groupBy
            if self.panel.groupBy[0].is_numeric:                # if groupBy numeric
                if len(agg_num) > 0:                            # if at least 1 aggregation attribute is aggregated with min/max/avg
                    visus.append('histogram_numeric')
                    # TODO : gérer cas où d'autres attributs d'aggrégation n'ont pas de min/max/avg
                elif len(agg_sum) == 0:                         # if the only aggregate is count
                        visus.append('histogram_count')
                        visus.append('radial_plot_count')
                elif not agg_count:                             # if aggregation attribute(s) is(are) aggregated only with sum
                    if len(agg_sum) == 1:                       # if only 1 aggregation attribute
                            visus.append('histogram_sum')
                            visus.append('radial_plot_sum')
                    else:                                       # if multiple attributes
                        visus.append('histogram_multiple_sum')
                else:                                           # if aggregation is done with sum AND count
                    
                    if len(self.panel.aggregates.keys()) > 2:   # if multiple aggregation attributes
                        # TODO: gérer cas où certains att ne sont pas agrégés avec sum
                        visus.append('histogram_multiple_sum')  # TODO: dans js : gérer cas sum(A), count(B), sum(B)
                    else:                                       # if aggregation is : count(A), sum(A)
                        visus.append('histogram_sum')
                        visus.append('radial_plot_sum')         # TODO facile/rapide !!!
            else:                                               # if groupBy nominal

                # check if panel visualization might be a word cloud : TODO function ou même classe visu ?
                cloud_attributes = []
                for groupBy_at in self.panel.groupBy:
                    if groupBy_at.adomSize >= self.args.pie_cloud_threshold:
                        if not groupBy_at.is_numeric:
                            cloud_attributes.append(groupBy_at)
                        else:
                            if groupBy_at.discretized_adomSize >= self.args.pie_cloud_threshold:
                                cloud_attributes.append(groupBy_at)

                if len(cloud_attributes) == 0:                      # if nb of groups < pie_cloud_threshold
                    if len(agg_num) > 0:                            # if at least 1 aggregation attribute is aggregated with min/max/avg
                        visus.append('histogram_numeric')
                    elif len(agg_sum) == 0:                         # if the only aggregate is count
                        visus.append('radial_plot_count')
                        visus.append('histogram_count')
                    elif not agg_count:                             # if sum is the only aggregation function
                        if len(agg_sum) == 1:                       # if only 1 aggregation attribute
                                visus.append('radial_plot_sum')
                                visus.append('histogram_sum')
                        else:                                       # if multiple attributes
                            visus.append('histogram_multiple_sum')
                    else:                                           # if aggregation is done with sum AND count
                        
                        if len(self.panel.aggregates.keys()) > 1:   # if multiple aggregation attributes
                            # TODO: gérer cas avec uniquement count(A) et sum(B)
                            # TODO: gérer cas avec count(A), count(B), sum(B)
                            visus.append('histogram_multiple_sum')
                        else:                                       # if aggregation is : count(A), sum(A)
                            visus.append('histogram_sum')
                            # visus.append('pie_1_agg_at')   # TODO
            if len(self.panel.aggregates) == 1 and len(list(self.panel.aggregates.values())[0]) == 1:   
                visus.append('word_cloud')                      # if only 1 aggregate         
        else:                                                   # if multiple groupBys
            visus.append('two_groupBy')
        
        # ---------------------------------
        # choice of visualization(s)
        # ---------------------------------
        softmax_scores = []
        for expl in self.explanations:
            if expl.occurence[1]:
                score = expl.occurence[0]/expl.occurence[1]
            else:
                score = None
            softmax_scores.append({'add_remove': expl.remove_or_add, 'dimension': expl.dimension, 'score': score})

        # ---------------------------------
        # return infos
        # ---------------------------------
                    # self.dashbot_history.add_panel(self.panel, self.panel_number)
        print(f"Available visus : {visus}")
        print(self.panel.to_table(self.dataset))
        return {
            'panel' : {
                'result_table' : self.panel.to_result_table(self.dataset),
                'values_list' : self.panel.table_to_list(self.dataset),
                'content' : self.panel.to_content(),
                'visus' : visus
                },
            'attributes' : {
                'rankings': {
                    'groupBy': self.ranking.dict_to_list('groupBy', self.diversity),
                    'aggregation': self.ranking.dict_to_list('aggregation', self.diversity)
                }
            },
            'diversity' : self.diversity,
            'softmax_scores' : softmax_scores
        }

