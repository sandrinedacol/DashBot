from implem.dashbot import *
from implem.modules.panel import *

import time


class Eval:
    def __init__(self, result_file_path):
        self.result_file_path = result_file_path
        self.file_storage = ""
        self.iteration_number = 0
        self.iteration_time = 0
        self.total_time = 0
        self.start_iteration_time = None
        self.end_iteration_time = None
        self.target_found = "first"

    # -----------------
    # COMPUTING TIME
    # -----------------
    def start_chrono(self):
        self.start_time = time.time()

    def stop_chrono(self):
        self.stop_time = time.time()
        self.iteration_time += self.stop_time - self.start_time

    def reset_chrono(self):
        self.iteration_time = 0


    # -----------------
    # DISTANCES
    # -----------------

    def evaluate_distances(self, suggested_panel_list, target_dashboard_dict, found_panels):
        self.distances = dict()
        for index, target_panel in target_dashboard_dict.items():
            if index in found_panels:
                self.distances[index] = None
            else:
                dist = self.distance(suggested_panel_list, target_panel)
                self.distances[index] = dist

    def distance(self, panel_1, panel_2): 
        """
        Metric for distance between 2 panels
        option 1 : 1 for each different bit in vector representation
        option 2 : 1 for each different group By / 1 for each different aggregation (i.e. 1/4 for each different aggregate)
        """
        # #  OPTION 1
        # differences = list(map(lambda x,y: (x-y), panel_1, panel_2))
        # distance = len([diff for diff in differences if diff !=0])
        
        #  OPTION 2
        differences = list(map(lambda x,y: ((x-y)/2)**2, panel_1, panel_2))
        distance = sum(differences)

        return distance
    
    # -----------------
    # EXPLANATION
    # -----------------

    def find_explanation(self, attributes_and_star, suggested_panel, target, found_panels, explanation_type):
        # find closest panel in target dashboard
        closest_panel = Panel(attributes_and_star)
        target_to_find = dict([(index, dist) for (index, dist) in self.distances.items() if index not in found_panels])
        closest_panel_index = min(target_to_find, key = target_to_find.get) 
        closest_panel.vector = target.dataframe.loc[closest_panel_index,:]
        closest_panel.vector_to_attributes()

        explanation = dict()
        groupBy_to_remove = self.generate_attributes_to_remove(suggested_panel.groupBy, closest_panel.groupBy)
        if groupBy_to_remove:
            explanation['groupBy_to_remove'] = groupBy_to_remove
            if explanation_type == 'one':
                return explanation
        aggregation_to_remove = self.generate_attributes_to_remove(list(suggested_panel.aggregates.keys()), closest_panel.aggregates.keys())
        if aggregation_to_remove:
            explanation['aggregation_to_remove'] = aggregation_to_remove
            if explanation_type == 'one':
                return explanation
        good_aggregation = [at for at in suggested_panel.aggregates.keys() if at not in aggregation_to_remove]
        if good_aggregation:
            functions_to_change = dict()
            for agg_at in good_aggregation:
                suggested_functions = set(suggested_panel.aggregates[agg_at])
                closest_functions = set(closest_panel.aggregates[agg_at])
                functions_to_change[agg_at] = list( (suggested_functions | closest_functions) - (suggested_functions & closest_functions) ) 
            explanation['functions_to_change'] = functions_to_change
        return explanation

    def generate_attributes_to_remove(self, att_in_suggested, att_in_closest):
        attributes_to_remove = []
        for at in att_in_suggested:
            if at not in att_in_closest:
                attributes_to_remove.append(at)
        return attributes_to_remove

    # -----------------
    # RESULT FILE
    # -----------------

    def write_iteration_in_result_storage(self, panel_number, algo, generation_counter):
        distances = sorted(list(self.distances.items()), key = lambda item: item[0])
        distances = [str(item[1]) for item in distances]
        distances = ('/').join(distances)
        self.total_time += self.iteration_time
        self.file_storage += f'\n{self.iteration_number},{algo},{panel_number[0]},{panel_number[1]},{distances},{self.iteration_time},{self.total_time},{str(self.target_found)},{generation_counter}'
        self.iteration_number += 1

    def end_experiment(self, message=""):
        self.file_storage += message
        with open(self.result_file_path, 'a') as result_file:
            result_file.write(self.file_storage)

    