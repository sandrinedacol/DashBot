from implem.dashbot import *
from implem.modules.panel import *
from experiment.dashbot_experiment import *
from experiment.modules.eval import *
from experiment.modules.get_summary import *
from experiment.modules.get_plots import *

import time
from multiprocessing import Pool
import itertools
from collections import *




# ---------------------------------------
#         Parameters to change          |
# --------------------------------------------------------------
experiment_type = "MAB_params" # "MAB_params" / "paper_plots" (if influence of n_attributes, dashboard_size, explanation_ratio) / 'test'
run_on_serveur = False
n_expe = 10
changing_parameters = OrderedDict({
    # 'dataset_name': [MovieLens, MovieLens_numeric],
    # 'target': [['A'], ["A", "A2", "D1", "D2"]] # ['A'], ["A", "A2"], ["A", "A2", "D1"], ["A", "A2", "D1", "D2"], ["A", "D1", "D2", "D3"], ["A", "D1", "D2", "D3", "D4"]],
    # 'n_attributes': [4],
    # 'numeric_ratio': [0.5, 1],
    # 'diversity': [True, False]
    # 'inclusion': [True, False],
    # 'strategy': ['MAB'], # ['random', 'MAB', 'explanation', 'MAB_explanation', 'explanation_MAB', ...]
    # 'algos_ratio': ['1_1', '4_1', '9_1', '19_1', '49_1', '99_1'],
    # 'explanation_type': ['one', 'all'],
    # 'MAB_algo': ['e-greedy', 'softmax'],
    # 'epsilon': [0.1, 0.2, 0.3],
    # 'exploration_type': ['far-panel', 'new-panel'] # ['far-panel', 'new-panel', 'hybrid'],
    # 'sigma': [5, 10, 20, 30, 40]
    # 'exploration_bounding': [0.01, 0.1, 0.2]
    'temperature' : [0.1]
})
# --------------------------------------------------------------

def launch_1_experiment(n_expe, experiment_type, parameters, run_on_serveur):
    # run experiment 'n_expe' times
    if run_on_serveur:
        with Pool() as pool:
            res = pool.starmap(launch_experiment, zip(list(range(n_expe)), itertools.repeat(experiment_type), itertools.repeat(parameters), itertools.repeat(False)))
    else:
        for i_expe in list(range(n_expe)):
            directory_path, params_names = launch_experiment(i_expe, parameters, print_things=True)
    # save summary of n_expe runs
    summary = Summary(n_expe, directory_path, params_names, experiment_type)
    summary.get_summary()
    # update paper plots
    plots = Plots(experiment_type)
    plots.get_plots()

def launch_experiment(i_expe, parameters, print_things):
    print(f'\n**********************************************\n\                 EXPE {i_expe}\n**********************************************')
    experiment = Experiment(i_expe, parameters)
    if experiment.args.error:
        print(experiment.args.error_message)
    else:
        experiment.print_things = print_things
        experiment.initialize_dashboard_generation()
        while len(experiment.found_panels) < len(experiment.target.dict):
            experiment.eval.start_chrono()
            experiment.find_next_suggestion()
            experiment.show_to_U()
            experiment.eval.stop_chrono()
            experiment.model_user_feedback()
            experiment.eval.start_chrono()
            experiment.update_system()
            experiment.eval.stop_chrono()
            experiment.eval.write_iteration_in_result_storage(experiment.panel_number, experiment.algo.pop(0), experiment.generation_counter)
        experiment.eval.end_experiment()
    return experiment.directory_path, experiment.args.params_names





if __name__ == '__main__':
    for tuple_of_values in itertools.product(*changing_parameters.values()):
        parameters = dict(zip(changing_parameters.keys(), tuple_of_values))
        launch_1_experiment(n_expe, experiment_type, parameters, run_on_serveur)