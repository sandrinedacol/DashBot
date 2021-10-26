import pandas as pd
import yaml
import sys
sys.setrecursionlimit(10000)
import itertools
import copy

from .modules.parameters import *
from .dataset.datasets import *
from .modules.attribute import *
from .modules.panel import *
from .modules.ranking import *
from .modules.data_preprocessor import *
from .modules.explanation import *

def choose_functions(agg_att):
    if agg_att.name == '*':
        functions = ['count']
    else:
        functions = ['avg', 'sum', 'max', 'min']   # ordered list for choice of aggregate if visu = 'word cloud'
        functions_ = functions[:]
        for func in agg_att.bad_func:
            functions_.remove(func)
        if len(functions_) > 0:
            functions = functions_
    return functions 

def powerset(iterable):
    """
    powerset([1,2,3]) --> (1,) (2,) (3,) (1,2) (1,3) (2,3) (1,2,3)
    from https://docs.python.org/3/library/itertools.html
    """
    s = list(iterable)
    return itertools.chain.from_iterable(itertools.combinations(s, r) for r in range(0, len(s)))

def gaussian(x, mu, sigma):
    return 1/(sigma * math.sqrt(2 * math.pi)) * math.exp( - (x-mu)**2 / (2 * sigma**2) )


class DashBot():

    def __init__(self, mode):
        self.mode = mode
        self.print_things = True
        # deal with config file
        with open(f'{self.mode}/parameters_{self.mode}.yaml', 'r') as cfile:
                yml = yaml.load(cfile, Loader=yaml.FullLoader)
                self.args = Parameters(yml, self.mode)
        # set some properties
        self.diversity = {'asked': self.args.diversity, 'achieved': False}
        self.MAB_algo = self.args.MAB_algo.split(' ')[0]
        self.star = Attribute()
        self.star.name = '*'
        
    def preprocess_data(self, dataset_name=None):
        if not dataset_name:
            dataset_name = self.args.dataset_name
        self.data_preprocessor = DataPreprocessor(dataset_name, self.args.attribute_threshold, self.args.discretize_K)
        self.attributes = self.data_preprocessor.attributes
        self.numeric_ratio = len([at for at in self.attributes if at.is_numeric])/len(self.attributes)
        self.attributes_and_star = self.attributes + [self.star]
        self.dataset = self.data_preprocessor.dataset
        self.ranking = AttributesRanking(self.attributes, self.star)

    def initialize_dashboard_generation(self):
        """
        create panel, panel_number, dashboard, dashbot_history, generation_counter
        """
        # initializating system variables
        self.diversity = {'asked': self.args.diversity, 'achieved': False}
        self.dashboard = Dash(self.attributes_and_star)
        self.dashbot_history = []
        self.panel = Panel(self.attributes_and_star)
        self.panel_number = [0,0]
        self.user_feedback = True
        self.explanations_to_apply = dict()
        self.explanation_type = None
        # to monitor each iteration
        self.generation_counter = 0
        self.pairwise_panels_cycle = 0
        self.pairwise_panels_functions_to_remove = list(powerset(['sum', 'min', 'max', 'avg']))
        # initializing MAB algorithm
        if "e-greedy" in self.args.MAB_algo:
            if self.args.exploration_type in ["far-panel", 'new-panel']:
                self.exploration_type = self.args.exploration_type
            if self.args.exploration_type == 'hybrid':
                self.exploration_type = "far-panel"
        if "softmax" in self.args.MAB_algo:
            self.explanations = []
            for (remove_or_add, dimension) in itertools.product(('-', '+'), ('groupBy', 'aggregation', 'min', 'max', 'avg', 'sum')):
                self.explanations.append(Explanation(remove_or_add, dimension))
            self.explanations_initialization = self.explanations[:]
            random.shuffle(self.explanations_initialization)
            self.applied_explanations = []

        
    # At each iteration :

    # #####################################################
    #       1) Update DashBot according to user_feedback
    # #####################################################

    def update_system(self):
        if self.user_feedback:
            self.validate_panel()
        if "softmax" in self.args.MAB_algo and self.applied_explanations:
            self.update_explanations_scores()
        if self.explanations_to_apply:
            self.update_bad_list()

    def validate_panel(self):
        """
        update dashboard, diversity, attributes_on_dashboard
        prepare next suggestion
        """
        # put last suggestion on dashboard 
        self.dashboard.add_panel(self.panel, tuple(self.panel_number))
        # update objects needed for diversity
        if self.diversity['achieved'] == False :
            agg_attributes = [at for at in self.panel.aggregates.keys() if at != self.star]
            for attribute in self.panel.groupBy + agg_attributes:
                attribute.on_dashboard = True
                self.dashboard.attributes_on.add(attribute)
                if len(self.dashboard.attributes_on) == len(self.attributes):
                    self.diversity['achieved'] = True

    def update_explanations_scores(self):
        # TODO : idea: use distance to next found panel to compute score instead of 'give yes feedback'
        for expl in self.applied_explanations:
            expl.occurence[1] += 1
            if self.user_feedback:
                expl.occurence[0] += 1
            expl.score = math.exp(expl.occurence[0]/expl.occurence[1]/self.args.temperature)
        self.applied_explanations = []

    def update_bad_list(self):
        # bad groupBy
        max_bad_groupBy = max([at.bad_groupBy for at in self.attributes])
        groupBy_to_remove = []
        if 'groupBy_to_remove' in self.explanations_to_apply:
            groupBy_to_remove = self.explanations_to_apply['groupBy_to_remove']
            for gb_at in groupBy_to_remove:
                gb_at.bad_groupBy = max_bad_groupBy + 1
        # bad agg
        if 'aggregation_to_remove' in self.explanations_to_apply:
            for agg_at in self.explanations_to_apply['aggregation_to_remove']:
                for gb_at in [at for at in self.panel.groupBy if at not in groupBy_to_remove]:
                    if agg_at in gb_at.bad_agg:
                        gb_at.bad_agg.remove(agg_at)
                    gb_at.bad_agg.append(agg_at)
        # bad functions
        if 'functions_to_change' in self.explanations_to_apply:
            for agg_at, functions in self.explanations_to_apply['functions_to_change'].items():
                for func in functions:
                    if self.panel.vector[(agg_at.name, func)] == 1:
                        if func in agg_at.bad_func:
                            agg_at.bad_func.remove(func)
                        agg_at.bad_func.append(func)
                    else:
                        if func in agg_at.bad_func:
                            agg_at.bad_func.remove(func)


    # #####################################################
    #       2) Find next suggestion according to user_feedback
    # #####################################################

    def find_next_suggestion(self):
        self.generation_counter = 0
        if self.user_feedback:
            self.panel_number[0] += 1
            self.panel_number[1] = 0
            if self.print_things:
                print(f"\nPanel {self.panel_number}: NEW PANEL ")
            self.generate_new_panel()
        else:
            self.panel_number[1] += 1
            if self.explanations_to_apply:
                if self.print_things:
                    print(f"\nPanel {self.panel_number}: EXPLANATION ")
                self.apply_explanation()
            else:
                if self.print_things:
                    print(f"\nPanel {self.panel_number}: MAB ")
                self.perform_MAB()
        if self.print_things:
            print(f"{self.generation_counter} panel(s) generated")

    # -----------------------------------------------------
    #                     2.a) NEW PANEL
    # -----------------------------------------------------

    def generate_new_panel(self):
        self.panel.reset()
        self.ranking.calculate_ranking('groupBy', self.panel, self.diversity)
        self.ranking.calculate_ranking('aggregation', self.panel, self.diversity)
        self.find_both_attributes()

    def find_both_attributes(self, forbidden_groupBy=list(), forbidden_agg=list()):
        """
        Add attributes to self.panel so that it is recommandable.
        !!! ranking.groupBy has to be calculated before !!!
        forbidden_list are lists of attributes that have to be discarded
            (in contrast to 'avoided') --> when U has recently reported them
        """
        if len(self.panel) == 0:
            self.panel.aggregates[self.star] = ['count']
            self.panel.attributes_to_vector()
        for groupBy_quality, agg_quality in self.ranking.pairwise_qualities_2:
            next_panel = self.try_find_attributes(self.panel, forbidden_groupBy, forbidden_agg, groupBy_quality, agg_quality)
            if next_panel:
                break
        if not next_panel:
            self.pairwise_panels_cycle += 1
            # if all pairwise panels with all combinations of functions have been tried,
            if self.pairwise_panels_cycle > len(self.pairwise_panels_functions_to_remove) - 1:
                # generate random panel
                if self.args.exploration_type == 'new-panel':
                    self.args.epsilon = 0
                return self.find_random_panel()
            else:
                return self.find_both_attributes(forbidden_groupBy, forbidden_agg)
        self.panel = next_panel

    def try_find_attributes(self, in_panel, forbidden_groupBy, forbidden_agg, groupBy_quality, agg_quality):
        """
        Loop on GROUP BY and/or aggregation attributes to add to in_panel,
        so that out_panel is recommendable
        in_panel is a panel on which attributes will be added
            can be empty
        forbidden_list are lists of attributes that have to be discarded
            in contrast to 'avoided'
        X_ quality can be :
            - None, if no attributes has to be added to X
            - 'good', if attribute is searched on good ranking for X
            - 'bad', if attribute is searched on bad ranking for X
        """
        if groupBy_quality != None:                                                         # if 1 GROUP BY attribute has to be added,
            self.ranking.calculate_ranking('groupBy', in_panel, self.diversity, forbidden_groupBy)    # prepare for looping on GROUP BY attribute
            ranking_groupBy = self.ranking.local['groupBy'][groupBy_quality][:]
            if len(ranking_groupBy) == 0:                                                   # if no GROUP BY attribute is available,
                out_panel = None                                                            # get out with nothing
                return out_panel
        else:                                                                               # if no GROUP BY attribute has to be added,
            ranking_groupBy = list()                                                        # len(ranking_groupBy) = 0
        try:                                                       
            out_panel  = self.loop_on_attributes(in_panel, ranking_groupBy, agg_quality, forbidden_agg)
        except IndexError:
            out_panel = None
        return out_panel

    def loop_on_attributes(self, in_panel, ranking_groupBy, agg_quality, forbidden_agg):
        """
        returns a recommendable panel or None
        """
        out_panel = in_panel.copy_from_vector()
        if len(ranking_groupBy) > 0:                                                                    # if a GROUP BY attribute has to be added,
            gb_at = ranking_groupBy.pop(0)                                                              # take the first one in ranked attributes
            out_panel.groupBy.append(gb_at)     
            out_panel.attributes_to_vector()
        if agg_quality != None:                                                                         # if aggregation attribute has to be added,
            self.ranking.calculate_ranking('aggregation', out_panel, self.diversity, forbidden_agg)     # prepare for looping on aggregation
            ranking_aggregation = self.ranking.local['aggregation'][agg_quality][:]
            if len(ranking_aggregation) == 0:                                                           # if no aggregation attribute is available,
                out_panel = None                                                                        # get out with nothing
                return out_panel
            out_panel  = self.loop_on_aggregation_attributes(out_panel, ranking_aggregation)
        else:                                                                                           # if no aggregation attribute has to be added,
            self.generation_counter += 1
            out_panel, recommendable = self.check_if_recommendable(out_panel)                                      # check here if the panel is new
            if not recommendable:                                                                       # if not,
                out_panel = None                                                                        # get out with nothing
        if not out_panel:                                                                               # if last try is not new,
            if len(ranking_groupBy) != 0:                                                               # and if there still are GROUP BY attributes to try
                return self.loop_on_attributes(in_panel, ranking_groupBy, agg_quality, forbidden_agg)   # do it again
        return out_panel                                                                                # go out with new panel or nothing

    def loop_on_aggregation_attributes(self, in_panel, ranking_aggregation):
        """
        returns a recommendable panel or None
        """
        out_panel = in_panel.copy_from_vector()
        agg_at = ranking_aggregation.pop(0)                                                     # first, choose attribute in ranked list
        out_panel.aggregates[agg_at] = choose_functions(agg_at)                            # then, choose functions to aggregate on it
        func_to_remove = self.pairwise_panels_functions_to_remove[self.pairwise_panels_cycle]
        for func in func_to_remove:
            if func in out_panel.aggregates[agg_at]:
                out_panel.aggregates[agg_at].remove(func)
        out_panel.attributes_to_vector()
        self.generation_counter += 1
        out_panel, recommendable = self.check_if_recommendable(out_panel)                                  # check if panel is new
        if not recommendable:                                                                   # if it's not,
            if len(ranking_aggregation) == 0:               
                out_panel = None                                                                # get out with nothing
            else:
                return self.loop_on_aggregation_attributes(in_panel, ranking_aggregation)       # or try a new one
        return out_panel                                                                        # get out with new panel or nothing
            
    # -----------------------------------------------------
    #                     2.b) RANDOM
    # -----------------------------------------------------

    def generate_random_panel(self):

        self.generation_counter += 1
        self.panel.reset()
        # Choose groupby_attributes
        groupBy_bits = [bit_name for bit_name in self.panel.vector.index if bit_name[1] == 'groupBy' ]
        for bit in groupBy_bits:
            self.panel.vector.loc[bit] = random.choice([0,2])
        if len(self.panel) == 0:
            groupby_bit = random.choice(groupBy_bits)
            self.panel.vector.loc[groupby_bit] = 2
        self.panel.vector_to_attributes()
        # Choose aggregation attributes
        groupBy_names = [at.name for at in self.panel.groupBy]
        agg_bits = [bit_name for bit_name in self.panel.vector.index if bit_name[1] != 'groupBy' and bit_name[0] not in groupBy_names]
        for bit in agg_bits:
            self.panel.vector.loc[bit] = random.choice([0,1])
        self.panel.vector_to_attributes()
        if len(self.panel.aggregates) == 0:
            agg_bit = random.choice(agg_bits)
            self.panel.vector.loc[agg_bit] = 1
            self.panel.vector_to_attributes()

    def find_random_panel(self):
        print('Finding RANDOM panel...')
        if self.generation_counter == 10000:
            print("STUCK IN RECURSIVE FUNCTION <find_panel_satisfying_criteria> !!!")
            self.eval.end_experiment("\nSTUCK IN RECURSIVE FUNCTION <find_panel_satisfying_criteria> !!!")
            return None
        # generate random panel
        self.generate_random_panel()
        # check if already in history
        # if self.args.check_history:
        found = self.check_in_history(self.panel.vector)
        if found:
            return self.find_random_panel()

    # -----------------------------------------------------
    #                     2.c) MAB
    # -----------------------------------------------------

    def perform_MAB(self):
        """
        find next_panel:
            update panel_number, panel, ranking, dashbot_history
        """
        # to avoid to be stuck in recursive function
        if self.generation_counter == 9998:
            print("\n\n\n!!!!!! STUCK IN RECURSIVE FUNCTION <perform_MAB> !!!!!!!!!\n\n\n")
            # print(f"Continue with second to last panel")
            # last_panel.vector = dashbot_history[-1] # TODO
            self.panel = None
            return self.panel
        # refine panel
        if self.MAB_algo == 'e-greedy':
            backup_panel = self.panel.copy_from_vector()
            # choose exploit/explore
            random_number = random.random()
            if random_number > self.args.epsilon:
                exploit = True
                if self.print_things:
                    print("... exploit ...")
            else:
                exploit = False
                if self.print_things:
                    print("... explore ...")
            # apply changes  
            if self.args.exploration_type == "hybrid" and not exploit:
                proba_far_panel = gaussian(self.panel_number[1], 0, self.args.sigma) * self.args.sigma * math.sqrt(2*math.pi)
                self.exploration_type = np.random.choice(['far-panel', 'new-panel'], size=1, p=[proba_far_panel, 1-proba_far_panel])
            if self.exploration_type == 'new-panel' and not exploit:
                return self.generate_new_panel()
            else:
                self.refine_by_egreedy(exploit)
            self.generation_counter += 1
            # fix panel
            self.fix_panel_for_MAB()
            # check if in history
            self.panel, recommendable = self.check_if_recommendable(self.panel)
            if not recommendable:
                self.panel = backup_panel.copy_from_vector()
                return self.perform_MAB()
        elif self.MAB_algo == 'softmax':
            self.refine_by_softmax()
        

    # ------------- e-GREEDY ---------------------------

    def refine_by_egreedy(self, exploit):
        # switching probabilities vector
        attributes = self.panel.attributes
        bad_groupBy_names = [at.name for at in attributes if at.bad_groupBy > 0]
        if len(bad_groupBy_names) != len(attributes):
            switching_probabilities = [self.agree_switch(bit, self.panel.vector[bit], bad_groupBy_names) for bit in self.panel.columns]
            switch_sum = sum(switching_probabilities)
            switching_probabilities = [agreement/switch_sum for agreement in switching_probabilities]
        else:
            switching_probabilities = [1/len(self.panel.columns)] * len(self.panel.columns)
        # exploit
        if exploit:
            number_of_bits = 1
        else:
            # try:
            #     number_of_bits = int(self.args.exploration_bounding * len(self.panel.columns))
            # except TypeError:           # in case of <apply_strategy_if_all_pairwise_panels_have_been_shown>
            #     number_of_bits = 1
            number_of_bits = int(self.args.exploration_bounding * len(self.panel.columns))
        self.change_bits(switching_probabilities, number_of_bits)
        self.panel.vector_to_attributes()

    def agree_switch(self, bit, bit_value, bad_groupBy_names):
        if bit[0] in bad_groupBy_names and bit_value == 0:
            switch_agreement = 0
        else:
            switch_agreement = 1
        return switch_agreement

    def change_bits(self, switching_probabilities, number_of_bits):
        change_bits_index = np.random.choice(range(len(self.panel.columns)), size=number_of_bits, p=switching_probabilities)
        change_bits = [ self.panel.columns[i] for i in change_bits_index]
        for bit in change_bits:
            self.invert_bit(bit)

    def invert_bit(self, bit):
        old_value = self.panel.vector[bit]
        attribute, function = bit
        if old_value == 0:
            if function == 'groupBy':
                self.panel.vector[attribute, function] = 2
            else:
                self.panel.vector[attribute, function] = 1
        else:
            self.panel.vector[attribute, function] = 0
    
    def fix_panel_for_MAB(self):
        aggregation_attributes = [at for at in self.attributes if at.is_numeric] + [self.star]
        # No GROUP BY attribute
        if len(self.panel.groupBy) == 0:
            self.panel.groupBy.append(random.choice(self.attributes))
            return self.fix_panel_for_MAB()
        # No aggregates
        elif len(self.panel.aggregates.keys()) == 0:
            agg_at = random.choice(aggregation_attributes)
            if agg_at == self.star:
                functions = ['count']
            else:
                functions = ['min', 'max', 'sum', 'avg'] 
            self.panel.aggregates[agg_at] = [random.choice(functions)]
            return self.fix_panel_for_MAB()
        # same attribute on the 2 dimensions
        same_attributes = list(set(self.panel.groupBy) & set(self.panel.aggregates.keys()))
        if len(same_attributes) > 0:
            # if only one aggregation attribute
            if len(self.panel.aggregates) == 1 and len(self.panel.groupBy) > 1:
                self.panel.groupBy.remove(same_attributes[0])
            # if only one GROUP BY attribute
            elif len(self.panel.aggregates) > 1 and len(self.panel.groupBy) == 1:
                del self.panel.aggregates[same_attributes[0]]
            # remove a random attribute on a random dimension
            else:
                dimension = random.choice(['groupBy', 'aggregation'])
                at = random.choice(same_attributes)
                if dimension == 'groupBy':
                    self.panel.groupBy.remove(at)
                else:
                    del self.panel.aggregates[at]
            return self.fix_panel_for_MAB()
        self.panel.attributes_to_vector()

    # ------------- SOFTMAX ---------------------------
    
    def refine_by_softmax(self):
        self.compute_probas(self.find_forbidden_explanations())
        self.explanation_type = self.choose_explanation_type()
        if self.print_things:
            print(f"apply explanation : ({self.explanation_type.remove_or_add}, {self.explanation_type.dimension})")
        attribute = self.choose_attribute()
        if self.print_things:
            print(f"on : {attribute.name}")
        self.update_explanations_to_apply(attribute)
        self.apply_explanation()

    def find_forbidden_explanations(self):
        forbidden_explanations = []
        agg_att_in_panel = [agg_att for agg_att in self.panel.aggregates.keys() if agg_att.name != '*']
        possible_att_for_aggregation = [att for att in self.attributes_and_star if att.is_numeric or att.name == "*"]
        possible_att_for_aggregation = [att for att in possible_att_for_aggregation if att not in self.panel.groupBy + list(self.panel.aggregates.keys())]
        print(f"possible att for +agg: {[at.name for at in possible_att_for_aggregation]}")
        if len(self.panel.groupBy) + len(agg_att_in_panel) >= len(self.attributes):
            # add groupBy attribute when all of them are already used
            forbidden_explanations.append(('+', 'groupBy'))
            if len(self.panel.groupBy) == 1:
                # remove the only possible groupBy attribute
                forbidden_explanations.append(('-', 'groupBy'))
        if len(possible_att_for_aggregation) == 0:
            # add aggregation attribute when all of them are already used
            forbidden_explanations.append(('+', 'aggregation'))
            if len(self.panel.aggregates) == 1:
                # remove the only possible aggregation attribute
                forbidden_explanations.append(('-', 'aggregation'))

        for func in ['min', 'max', 'avg', 'sum']:
            if len(agg_att_in_panel) == 0:
                # add or remove function if count is the only aggregate (--> add/remove aggregation)
                forbidden_explanations += [('-', func), ('+', func)]
            else:
                att_with_func = [agg_att for (agg_att, functions) in self.panel.aggregates.items() if func in functions]
                if len(att_with_func) == 0:
                    # remove not used function
                    forbidden_explanations.append(('-', func))
                else:
                    if len(att_with_func) == len(agg_att_in_panel):
                        # add function used in all aggregation attributes
                        forbidden_explanations.append(('+', func))
                    # remove a func that is only used alone on aggregation attributes (--> remove aggregation)
                    alone_func = True
                    for (agg_att, functions) in self.panel.aggregates.items():
                        if func in functions and len(functions) > 1:
                            alone_func = False
                    if alone_func:
                        forbidden_explanations.append(('-', func))
        print('forbidden_explanations:', forbidden_explanations)
        return forbidden_explanations
    
    def compute_probas(self, forbidden_explanations):
        # put proba to 0 or score
        for expl in self.explanations:
            if (expl.remove_or_add, expl.dimension) in forbidden_explanations:
                expl.proba = 0
            else:
                expl.proba = expl.score
        print([expl.score for expl in self.explanations])
        # normalize scores
        denom = sum([expl.proba for expl in self.explanations if expl.proba != None])
        if denom:                       # when all proba are not None
            for expl in self.explanations:
                try:
                    expl.proba = expl.proba / denom
                except TypeError:       # when score or denom is None
                    pass

    def choose_explanation_type(self):
        if len(self.explanations_initialization):
            for counter in range(len(self.explanations_initialization)):
                explanation_type = self.explanations_initialization.pop()
                if explanation_type.proba == 0:
                    self.explanations_initialization = [explanation_type] + self.explanations_initialization
                else:
                    return explanation_type
        probas = list()
        for expl in self.explanations:
            if expl.proba == None:
                probas.append(0)
            else:
                probas.append(expl.proba)
        return np.random.choice(self.explanations, size=1, p=probas)[0]

    def choose_attribute(self):
        if self.explanation_type.remove_or_add == '-':
            if self.explanation_type.dimension == 'groupBy':
               possible_attributes = self.panel.groupBy
            elif self.explanation_type.dimension == 'aggregation':
                possible_attributes = [agg_at for agg_at in self.panel.aggregates.keys()]
            else:
                possible_attributes = [agg_at for (agg_at, func) in self.panel.aggregates.items() if self.explanation_type.dimension in func]
        else:
            if self.explanation_type.dimension == 'groupBy':
               possible_attributes = [att for att in self.attributes if att not in self.panel.groupBy + list(self.panel.aggregates.keys())]
            elif self.explanation_type.dimension == 'aggregation':
                possible_attributes = [att for att in self.attributes_and_star if att.is_numeric or att.name == '*']
                possible_attributes = [att for att in possible_attributes if att not in list(self.panel.aggregates.keys()) + self.panel.groupBy]
            else:
                possible_attributes = [agg_at for (agg_at, func) in self.panel.aggregates.items() if self.explanation_type.dimension not in func and agg_at.name != '*']
        return random.choice(possible_attributes)

    def update_explanations_to_apply(self, attribute):
        if self.explanation_type.dimension == 'groupBy':
            if self.explanation_type.remove_or_add == '-':
                self.explanations_to_apply['groupBy_to_remove'] = [attribute]
            else:
                self.explanations_to_apply['groupBy_to_add'] = [attribute]
        elif self.explanation_type.dimension == 'aggregation':
            if self.explanation_type.remove_or_add == '-':
                self.explanations_to_apply['aggregation_to_remove'] = [attribute]
            else:
                self.explanations_to_apply['aggregation_to_add'] = [attribute]
        else:
            self.explanations_to_apply['functions_to_change'] = {attribute : [self.explanation_type.dimension]}


    # -----------------------------------------------------
    #                     2.d) EXPLANATION
    # -----------------------------------------------------

    def apply_explanation(self):
        forbidden_groupBy, forbidden_aggregation = self.clean_panel()
        self.fix_panel_for_explanation()                # in case of same attribute in GROUP BY and aggregation
        next_panel = self.add_up_to_1_attribute(forbidden_groupBy, forbidden_aggregation)       # find next_panel, as it is or with one more attribute
        if next_panel:
            next_panel.attributes_to_vector()
            self.panel = next_panel
        else:                                           # if not found before, add attributes on GROUP BY and aggregation dimension
            self.find_both_attributes(forbidden_groupBy, forbidden_aggregation)
        self.explanations_to_apply = dict()

    def clean_panel(self):
        """
        strictly apply explanations to last panel
        """
        if 'softmax' in self.args.MAB_algo and not self.explanation_type:
            expl_tuples = set()
        forbidden_groupBy = list()
        forbidden_aggregation = list()
        for expl, attributes_list in self.explanations_to_apply.items():
            if 'groupBy' in expl:
                if 'remove' in expl:
                    forbidden_groupBy = attributes_list
                    self.panel.groupBy = [att for att in self.panel.groupBy if att not in attributes_list]
                    if 'softmax' in self.args.MAB_algo and not self.explanation_type:
                        expl_tuples.add(('-', 'groupBy'))
                else:
                    self.panel.groupBy += attributes_list
                    if 'softmax' in self.args.MAB_algo and not self.explanation_type:
                        expl_tuples.add(('+', 'groupBy'))
            elif 'aggregation' in expl:
                if 'remove' in expl:
                    forbidden_aggregation = attributes_list
                    for att in attributes_list:
                        del self.panel.aggregates[att]
                    if 'softmax' in self.args.MAB_algo and not self.explanation_type:
                        expl_tuples.add(('-', 'aggregation'))
                else:
                    for agg_att in self.explanations_to_apply['aggregation_to_add']:
                        functions = choose_functions(agg_att)
                        # if 'sum' in functions and len(functions) > 1:
                        #     functions.remove('sum')
                        self.panel.aggregates[agg_att] = functions
                    if 'softmax' in self.args.MAB_algo and not self.explanation_type:
                        expl_tuples.add(('+', 'aggregation'))
            else:
                for agg_att, functions in attributes_list.items():
                    for func in functions:
                        if func in self.panel.aggregates[agg_att]:
                            self.panel.aggregates[agg_att].remove(func)
                            if 'softmax' in self.args.MAB_algo and not self.explanation_type:
                                expl_tuples.add(('-', func))
                        else:
                            self.panel.aggregates[agg_att].append(func)
                            if 'softmax' in self.args.MAB_algo and not self.explanation_type:
                                expl_tuples.add(('+', func))
        self.panel.attributes_to_vector()
        self.ranking.calculate_ranking('groupBy', self.panel, self.diversity, forbidden_groupBy)
        self.ranking.calculate_ranking('aggregation', self.panel, self.diversity, forbidden_aggregation)
        if 'softmax' in self.args.MAB_algo:
            if self.explanation_type:           # if MAB iteration
                self.applied_explanations = [self.explanation_type]
                self.explanation_type = None
            else:                               # if user_explanation iteration
                self.applied_explanations = [expl for expl in self.explanations if (expl.remove_or_add, expl.dimension) in expl_tuples]
        
        return forbidden_groupBy, forbidden_aggregation

    def fix_panel_for_explanation(self):
        same_attributes = list(set(self.panel.groupBy) & set(self.panel.aggregates.keys()))
        if len(same_attributes) > 0:
            random.shuffle(same_attributes)
            try:
                added_groupBy = self.explanations_to_apply['groupBy_to_add']
            except KeyError:
                added_groupBy = list()
            try:
                added_aggregation = self.explanations_to_apply['aggregation_to_add']
            except KeyError:
                added_aggregation = list()
            for att in same_attributes:
                if att in added_groupBy:
                    del self.panel.aggregates[att]
                elif att in added_aggregation:
                    self.panel.groupBy.remove(att)
                else:
                    if random.choice([0,1]):
                        del self.panel.aggregates[att]
                    else:
                        self.panel.groupBy.remove(att)
                    
            self.panel.attributes_to_vector()

    def add_up_to_1_attribute(self, forbidden_groupBy, forbidden_aggregation):
        # if no need for GROUP BY and aggregation attributes
        if len(self.panel.groupBy) != 0 and len(self.panel.aggregates) != 0:
            next_panel = self.panel.copy_from_vector()
            self.generation_counter += 1
            next_panel, recommendable = self.check_if_recommendable(next_panel)
            if not recommendable:
                for groupBy_quality, agg_quality in self.ranking.pairwise_qualities_1:
                    next_panel = self.try_find_attributes(self.panel,
                        forbidden_groupBy, forbidden_aggregation,
                        groupBy_quality, agg_quality)
                    if next_panel:
                        break
        # if need for a GROUP BY attribute only
        elif len(self.panel.groupBy) == 0 and len(self.panel.aggregates) != 0:
            for groupBy_quality in self.ranking.qualities:
                next_panel = self.try_find_attributes(self.panel,
                    forbidden_groupBy, forbidden_aggregation,
                    groupBy_quality, None)
                if next_panel:
                    break
        # if need for an aggregation attribute only
        elif len(self.panel.groupBy) != 0 and len(self.panel.aggregates) == 0:
            groupBy_quality = None
            for agg_quality in self.ranking.qualities:
                next_panel = self.try_find_attributes(self.panel,
                    forbidden_groupBy, forbidden_aggregation,
                    None, agg_quality)
                if next_panel:
                    break
        # if need for GROUP BY and aggregation attributes
        else:
            next_panel = None
        return next_panel

    # -----------------------------------------------------
    #                     HISTORY
    # -----------------------------------------------------

    def check_if_recommendable(self, panel):
        recommendable = not self.check_in_history(panel.vector)
        return panel, recommendable

    def check_in_history(self, panel_vector):
        if self.args.inclusion == False:
            found = panel_vector.tolist() in self.dashbot_history
        else:
            found = self.is_included_panel_in_history(panel_vector)
        return found
    
    def is_included_panel_in_history(self, panel_vector):
        found = False
        panel_list = panel_vector.tolist()
        for already_shown_panel in self.dashbot_history:
            product = list(map(lambda x,y: math.sqrt(x*y), already_shown_panel, panel_list))
            if product == already_shown_panel:
                found = True
                break
        return found

    # #####################################################
    #       3) Show suggestion to user
    # #####################################################

    def show_to_U(self):
        self.dashbot_history.append(self.panel.vector.tolist())
        if self.print_things:
            self.panel.show()




 
    











