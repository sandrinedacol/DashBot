from implem.dashbot import *
from implem.modules.panel import *
from experiment.modules.eval import *

import os
import numpy as np
import copy

class Experiment(DashBot):

    def __init__(self, i_expe, varying_parameters):
        DashBot.__init__(self, mode='experiment')
        self.i_expe = i_expe
        self.args.process_parameters(varying_parameters)
        print('\n', self.args.get_summary())
        
        if not self.args.error:
            
            # iter algo
            self.iter_algos = []
            if not self.args.algos_ratio_list:
                self.iter_algos += self.args.algos_list
            else:
                for i, algo in enumerate(self.args.algos_list):
                    self.iter_algos += [algo] * self.args.algos_ratio_list[i]
            
            # data
            self.preprocess_data()                                                    
            self.selected_attributes = self.select_attributes()
            
            # initialize dashboard and target_dashboard
            self.dashboard = Dash(self.attributes_and_star)
            self.instanciate_target_dashboard()
            
            # initialize result_file
            self.initialize_result_file()
            
            # eval
            self.eval = Eval(self.result_file_path)
            if self.args.check_history:
                self.dashbot_history = []
            self.generation_counter = 0

    # --------------------------------------------
    #       functions for __init__
    # --------------------------------------------

    def select_attributes(self):
        selected_attributes = []
        
        # select attributes on target dashboard
        for i in range(len(self.args.target_dashboard)):
            selected_attributes += self.args.target_dashboard[i]['groupBy']
            selected_attributes += list(self.args.target_dashboard[i]['aggregates'].keys())
        selected_attributes = list(set([at for at in selected_attributes if at != '*']))
        # choose others randomly, according to ratio
        if self.args.numeric_ratio:
            n_num = self.args.n_attributes * self.args.numeric_ratio
            n_target_num = len([at for at in self.attributes if at.name in selected_attributes and at.is_numeric])
            n_nom = self.args.n_attributes - n_num
            n_nom = n_nom - len(selected_attributes) + n_target_num
            n_num = n_num - n_target_num
            selected_attributes += random.sample([at.name for at in self.attributes if (at.name not in selected_attributes) and (at.is_numeric)], k=int(n_num))
            selected_attributes += random.sample([at.name for at in self.attributes if (at.name not in selected_attributes) and (not at.is_numeric)], k=int(n_nom))
            # if ratio*n_attributes is not int, select one randomly with acurate densities of probability
            num_proba = n_num - int(n_num)
            if num_proba != 0:
                num_or_nom = np.random.choice(['num', 'nom'], size=1, p=[num_proba, 1 - num_proba])
                if num_or_nom == 'num':
                    selected_attributes.append(random.choice([at.name for at in self.attributes if at.name not in selected_attributes and at.is_numeric]))
                else:
                    selected_attributes.append(random.choice([at.name for at in self.attributes if at.name not in selected_attributes and not at.is_numeric]))
        # choose others randomly (no constraint on ratio)
        else:
            n_others = self.args.n_attributes - len(selected_attributes)
            selected_attributes += random.sample([at.name for at in self.attributes if at.name not in selected_attributes], k=n_others)
        # restrict attributes of instance experiment with selected attributes
        self.dataset = self.dataset[selected_attributes]
        self.ranking.preprocessed['groupBy'] = [at for at in self.ranking.preprocessed['groupBy'] if at.name in selected_attributes]
        self.ranking.preprocessed['aggregation'] = [at for at in self.ranking.preprocessed['aggregation'] if at.name in selected_attributes]
        self.ranking.preprocessed['aggregation'] += [self.star]
        self.attributes = [at for at in self.attributes if at.name in selected_attributes]
        self.attributes_and_star = self.attributes + [self.star]
        self.numeric_at = [at for at in self.attributes if at.is_numeric]
        print(f"selection of {self.args.n_attributes} attributes: {[at.name for at in self.attributes]}")
        if self.args.numeric_ratio:
            print(f"including {int(100*len(self.numeric_at)/self.args.n_attributes)}% numeric attributes (asked:{int(self.args.numeric_ratio * 100)}%)\n")
        return selected_attributes

    def instanciate_target_dashboard(self):
        self.target = Dash(self.attributes_and_star)
        for index, panel in enumerate(self.args.target_dashboard):
            target_panel = Panel(self.attributes_and_star)
            for attribute in panel['groupBy']:
                target_panel.vector[attribute, 'groupBy'] = 2
            for attribute, functions in panel['aggregates'].items():
                for f in functions:
                    target_panel.vector[attribute, f] += 1
            self.target.add_panel(target_panel, index)
        self.found_panels = set()      # where index of found target panels will be stored

    def initialize_result_file(self):
        sep = '****************************\n'
        self.directory_path = "experiment/results/results_files/"
        self.create_directory()
        for param_name in self.args.params_names:
            if param_name == 'target':
                self.directory_path += f"{ ('_').join(self.args.target)}/"
            else:
                self.directory_path += f"{getattr(self.args, param_name)}/"
            self.create_directory()
        date = f"{time.localtime().tm_year}-{time.localtime().tm_mon}-{time.localtime().tm_mday}_{time.localtime().tm_hour}:{time.localtime().tm_min}"
        self.result_file_path = f"{self.directory_path}/{self.i_expe}_{date}.csv"
        result_file_header = f'{sep}{self.args.get_summary()}'
        result_file_header += f'* SELECTED_ATTRIBUTES: {self.selected_attributes}\n'
        if self.args.numeric_ratio:
            result_file_header += f'* TRUE_NUMERIC_RATIO: {len(self.numeric_at)/self.args.n_attributes}\n{sep}'
        result_file_header += "n_iter,algo,panel_nb,suggestion_nb,distances,iteration_time,total_time,found_target,n_generations"
        with open(self.result_file_path, 'w') as result_file:
            result_file.write(result_file_header)

    def create_directory(self):
        try:
            os.mkdir(f"{self.directory_path}")
        except FileExistsError:
            pass   

    # --------------------------------------------
    #       functions for dashboard generation
    # --------------------------------------------

    def initialize_dashboard_generation(self):
        super().initialize_dashboard_generation()
        if self.args.algos_list[0] == 'random':
            self.algo = ['random']
        else:
            self.algo = ['new-panel']

    def find_next_suggestion(self):
        if self.algo[0] == 'random':
            self.generation_counter = 0
            if self.user_feedback:
                self.panel_number[0] += 1
                self.panel_number[1] = 0
            else:
                self.panel_number[1] += 1
            if self.print_things:
                print(f"\nPanel {self.panel_number}: {self.algo} ")
            self.find_random_panel()
            if self.print_things:
                print(f"{self.generation_counter} panel(s) generated")
        else:
            super().find_next_suggestion()

    def validate_panel(self):
        self.found_panels.add(self.eval.target_found)
        super().validate_panel()

    # --------------------------------------------
    #       functions for modelling user feedback
    # -------------------------------------------- 

    def model_user_feedback(self):
        self.eval.evaluate_distances(self.panel.vector.tolist(), self.target.dict, self.found_panels)
        self.check_in_target()
        self.update_feedback_variables()

    def check_in_target(self):
        if not self.args.inclusion:
            self.eval.target_found = None
            self.user_feedback = False
            for index, distance in self.eval.distances.items():
                if distance == 0:
                    self.eval.target_found = index
                    self.user_feedback = True
        else:
            self.eval.target_found = self.is_panel_included_by_panel_in_target()

    def is_panel_included_by_panel_in_target(self):
        target_found = None
        panel_list = self.panel.vector.tolist()
        unfound_target_panels = self.target.dataframe.loc[list(set(self.target.dataframe.index)-self.found_panels)]
        for index, target_panel in unfound_target_panels.iterrows():
            target_panel_list = target_panel.tolist()
            product = list(map(lambda x,y: math.sqrt(x*y), target_panel_list, panel_list))
            if product == panel_list:
                if self.print_things:
                    print(f"\nPanel {self.panel_number}: last panel included by panel in target ")
                self.algo.append('inclusion')
                self.eval.write_iteration_in_result_storage(self.panel_number, self.algo.pop(0), self.generation_counter)
                self.panel_number[1] += 1
                self.generation_counter = 1
                self.eval.evaluate_distances(target_panel_list, self.target.dict, self.found_panels)
                target_found = index
                self.dashbot_history.append(target_panel_list)
                break
        return target_found

    def update_feedback_variables(self):
        """
        add next algo to self.algo
        update self.user_feedback and self.explanations_to_apply
        """
        if self.eval.target_found is not None:
            self.user_feedback = True
            if self.args.algos_list[0] == 'random':
                self.algo.append('random')
            else:
                self.algo.append('new-panel')
            self.explanations_to_apply = None
        else:
            self.user_feedback = False
            self.algo.append(self.iter_algos[(self.panel_number[1] + 1) % len(self.iter_algos) - 1])
            if self.algo[-1] == 'explanation':
                self.explanations_to_apply = self.eval.find_explanation(self.attributes_and_star, self.panel, self.target, self.found_panels, self.args.explanation_type)
            else:
                self.explanations_to_apply = None



    



# super().validate_panel()
