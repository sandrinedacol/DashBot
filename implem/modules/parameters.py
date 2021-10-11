from collections import *


def convert_string_to_parameter(value):
    if value in ['None', 'none', 'NONE', 'NA', 'nan', 'NaN']:
        parameter = None
    else:
        parameter = value
    return parameter

class Parameters():

    def __init__(self, dico, mode):
        """
        get parameters from config file
        """
        self.mode = mode
        self.error = False
        self.error_message = '\n*********************\nERROR in CONFIG file\n*********************\n'
        self.params_names = [
            'dataset_name', 'target', 'n_attributes', 'numeric_ratio', 'attribute_threshold', 'discretize_K',
            'diversity', 'check_history', 'inclusion', 'strategy', 'algos_ratio',
            'explanation_type', 'epsilon', 'MAB_algo', 'exploration_type', 'exploration_bounding', 'sigma', 'temperature',
            'pie_cloud_threshold'
            ]
        if self.mode == 'experiment':
            self.params_names.remove('pie_cloud_threshold')
        else:
            for param_name in ['target', 'n_attributes', 'numeric_ratio', 'check_history', 'strategy', 'algos_ratio', 'explanation_type']:
                self.params_names.remove(param_name)
        self.params = OrderedDict()
        for param_name in self.params_names:
            setattr(self, param_name, convert_string_to_parameter(dico[param_name]))

    def process_parameters(self, parameters_to_change=None):
        """
        instanciate usefull parameters
        """
        if parameters_to_change:
            for param_name, param_value in parameters_to_change.items():
                setattr(self, param_name, param_value)
        self.params_names.remove('discretize_K')
        if self.mode == 'experiment':
            self.params_names.remove('check_history')
        #-------------------
        # DATA
        #-------------------
        if self.mode == 'experiment':
            self.target_str = ('_').join(self.target)
            self.target_dashboard = []
            if "MovieLens" in self.dataset_name:
                self.possible_panels = {
                    'A': { 'groupBy': ['rating'], 'aggregates': {'*': ['count'], 'age': ['avg']} },
                    'A2': { 'groupBy': ['age'], 'aggregates': {'rating': ['avg']} },
                    'B1': { 'groupBy': ['gender'], 'aggregates': {'*': ['count'], 'age': ['avg'], 'rating': ['avg']} },
                    'B2': { 'groupBy': ['occupation'], 'aggregates': {'*': ['count'], 'age': ['avg'], 'rating': ['avg']} },
                    'B3': { 'groupBy': ['gender', 'occupation'], 'aggregates': {'*': ['count'], 'age': ['avg'], 'rating': ['avg']} },
                    'C1': { 'groupBy': ['release_date', 'g_Comedy'], 'aggregates': {'*': ['count'], 'age': ['avg'], 'rating': ['avg']} },
                    'C2': { 'groupBy': ['release_date', 'g_Action'], 'aggregates': {'*': ['count'], 'age': ['avg'], 'rating': ['avg']} },
                    'C3': { 'groupBy': ['release_date', 'g_Animation'], 'aggregates': {'*': ['count'], 'age': ['avg'], 'rating': ['avg']} },
                    'C4': { 'groupBy': ['release_date', 'g_Documentary'], 'aggregates': {'*': ['count'], 'age': ['avg'], 'rating': ['avg']} },
                    'C5': { 'groupBy': ['release_date', 'g_Fantasy'], 'aggregates': {'*': ['count'], 'age': ['avg'], 'rating': ['avg']} },
                    'C6': { 'groupBy': ['release_date', 'g_Sci_Fi'], 'aggregates': {'*': ['count'], 'age': ['avg'], 'rating': ['avg']} },
                    'D1': { 'groupBy': ['g_Comedy'], 'aggregates': {'*': ['count'], 'age': ['avg'], 'rating': ['avg']} },
                    'D2': { 'groupBy': ['g_Action'], 'aggregates': {'*': ['count'], 'age': ['avg'], 'rating': ['avg']} },
                    'D3': { 'groupBy': ['g_Animation'], 'aggregates': {'*': ['count'], 'age': ['avg'], 'rating': ['avg']} },
                    'D4': { 'groupBy': ['g_Documentary'], 'aggregates': {'*': ['count'], 'age': ['avg'], 'rating': ['avg']} },
                    'D5': { 'groupBy': ['g_Fantasy'], 'aggregates': {'*': ['count'], 'age': ['avg'], 'rating': ['avg']} },
                    'D6': { 'groupBy': ['g_Sci_Fi'], 'aggregates': {'*': ['count'], 'age': ['avg'], 'rating': ['avg']} }
                }
                for (name, panel) in self.possible_panels.items():
                    if name in self.target:
                        self.target_dashboard.append(panel)
        #-------------------
        # STRATEGY
        #-------------------
        if self.mode == 'experiment':
            # algo
            self.algos_list = self.strategy.split('_')
            for algo in self.algos_list:
                if algo not in ['random', 'MAB', 'newpanel', 'explanation']:
                    self.error = True
                    self.error_message += "Algo(s) must be 'random', 'MAB', 'newpanel' or 'explanation' separated with '_'\n"
                    break
            # algos ratio
            if len(self.algos_list) > 1:
                self.algos_ratio_list = self.algos_ratio.split('_')
                if len(self.algos_ratio_list) != len(self.algos_list):
                    self.error = True
                    self.error_message += "You must specify frequency for each algo separated with '_'\n"
                else:
                    try:
                        self.algos_ratio_list = [int(ratio) for ratio in self.algos_ratio_list]
                    except ValueError:
                        self.error = True
                        self.error_message += "Algos ratios must be int\n"
            else:
                self.algos_ratio = None
                self.algos_ratio_list = None
            # check_history
            if 'random' not in self.algos_list:
                self.check_history = True
        #-------------------
        # ALGOS PARAMETERS
        #-------------------
        # explanation parameters
        if self.mode == 'experiment' and 'explanation' in self.algos_list:
            if self.explanation_type not in ['all', 'one']:
                self.error = True
                self.error_message += "You must specify explanation type: 'all' or 'one'\n"
        else:
            self.explanation_type = None
        # MAB parameters
        # if not MAB (or explanation)
        if self.mode == 'experiment' and 'MAB' not in self.strategy and 'explanation' not in self.strategy:
            self.epsilon = None
            self.MAB_algo = None
            self.exploration_bounding = None
            self.exploration_type = None
            self.sigma = None
            self.temperature = None
        # if MAB (or explanation)
        else:
            # if not MAB_algo or bad epsilon
            if not [algo for algo in ['e-greedy', 'softmax'] if algo in self.MAB_algo]:
                self.error = True
                self.error_message += "When choosing MAB, you must specify MAB algo ('egreedy' or 'softmax') '/'\n"
            elif self.epsilon < 0 or self.epsilon > 1:
                self.error = True
                self.error_message += "epsilon must be in [0,1] '/'\n"
            # if MAB_algo and good epsilon
            else:
                # if egreedy
                if 'e-greedy' in self.MAB_algo:
                    if self.epsilon == 0:
                        self.exploration_type, self.exploration_bounding, self.sigma = None, None, None
                    # if not exploration_type
                    elif self.exploration_type not in ['far panel', 'farpanel', 'far-panel', 'far_panel', 'new panel', 'newpanel', 'new-panel', 'new_panel', 'hybrid']:
                        self.error = True
                        self.error_message += "When choosing e-greedy, you must specify exploration type ('farpanel' or 'newpanel') '/'\n"
                    # if exploration_type
                    else:
                        # if far panel
                        if self.exploration_type in ['far panel', 'farpanel', 'far-panel', 'far_panel']:
                            self.exploration_type = 'far-panel'
                            self.sigma = None
                        # if new panel
                        elif self.exploration_type in ['new panel', 'newpanel', 'new-panel']:
                            self.exploration_type = 'new-panel'
                            self.exploration_bounding, self.sigma = None, None
                        # if hybrid
                        else:
                            if not self.sigma:
                                self.error = True
                                self.error_message += "When choosing MAB e-greedy hybrid, you must specify sigma\n"
                        # if far panel or hybrid
                        if self.exploration_type in ['far-panel', 'hybrid']:
                            if not self.exploration_bounding or self.exploration_bounding > 1 or self.exploration_bounding < 0:
                                self.error = True
                                self.error_message += f"When choosing MAB e-greedy {self.exploration_type}, you must specify exploration bounding (in [0,1]) '/'\n"
                    if 'softmax' not in self.MAB_algo:
                        self.temperature = None

                # if softmax
                if 'softmax' in self.MAB_algo:
                    if not self.temperature:
                    	self.error = True
                    	self.error_message += f"When choosing 'softmax', you must specify temperature '/'\n"
                    if 'e-greedy' not in self.MAB_algo:
                        self.exploration_type = None
                        self.exploration_bounding = None
                        self.sigma = None
        #-------------------
        # VIZU
        #-------------------
        if self.mode == 'experiment':
            self.pie_cloud_threshold = None

    def get_summary(self):
        summary = ""
        for param_name in self.params_names:
            if param_name == 'target':
                summary += f"* {param_name.upper()}: {getattr(self, param_name)}\n"
                for panel in getattr(self, param_name):
                    summary += f"* \t{self.possible_panels[panel]}\n"
            else:
                summary += f"* {param_name.upper()}: {getattr(self, param_name)}\n"
        return summary




# queries_file = "/home/sandrine/DashBot/bandits-and-applications/datasets/movielens/movielens-queries.sql"
# target_dashboard = []
# with open(queries_file, 'r') as queries:
#     rows = queries.readlines()
#     i = 0
#     while i < len(rows):
#         row = rows[i]
#         if row.split(' ')[0] == "select":
#             print("Target query:\n",row[:-1])
#             query = {'groupBy' : [], 'aggregates' : {}}
#             select = row[7:-1].split(', ')[1:]
#             for aggregate in select:
#                 if len(aggregate.split('(')) == 2:
#                     attribute = aggregate.split('(')[1][:-1]
#                     func = aggregate.split('(')[0]
#                     query['aggregates'].setdefault(attribute, []).append(func)
#             i += 2
#             row = rows[i]
#             print(row)
#             groupby = row.split('group by ')[1][:-2].split(', ')
#             for attribute in groupby:
#                 query['groupBy'].append(attribute)
#             target_dashboard.append(query)
#         i += 1
