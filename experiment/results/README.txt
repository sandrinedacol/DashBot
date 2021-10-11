*****************************
			DATA
*****************************

Each run of an experiment generates a run_file stored in experiment_path.

----------------------------
		run_file
----------------------------

named:
<run_id>_<date>_<time>.csv

storing:
1) header : summary of parameters under which experiment is done (as in experiment_path)
2) data : row = 1 iteration, with:
	* iteration_number: number of iterations since dashboard generation started (start = 0)
	* algo: algorithm used to find suggested panel ("random", "new-panel", "MAB" or "explanation")
	* panel_number: number of target panels found - 1
	* suggestion_number: number of panels suggested (start = 0) since a target panel have been found (for the first one: since the dashboard generation started)
	* distances: distances between suggested panel and target panels (ordered with their indexes), separated with '/'
	* iteration_time: computing time (ms) if interation
	* total_time: computing time (ms) since dashboard generation start
	* found_target: if suggested panel is validated, index of target panel found
					if not, 'None' 
	* #generations: number of panels generated until one matches all requirements for being suggested
	
----------------------------
		experiment_path
----------------------------	

results/
results_files/
<experiment_type>/		--> type of experiment in "MAB parameters", "paper_plots" or "test"
<dataset name>/			--> name of dataset as in <dataset_name>.pkl
<target>/				--> names of target panels separated with '_'
<n_attributes>/			--> number of attributes selected in relation table
<numeric_ratio>/		--> ratio of numerical attributes
<attribute_threshold>/	--> preprocess parameter
<diversity>/				--> 'True' or 'False'
<inclusion>/			--> 'True' or 'False'
<startegy>/				--> strategy used to suggest panels ('random', 'MAB', 'explanation', or combination of two of the latter separated with '_')
<algos_ratio>/			--> 'hybrid' strategy: #algo1_#algo2
							others: 'None'
<explanation type>/		--> type of explanation modelisation:
								'one': one in 'remove groupBy', 'remove aggregation', 'change functions' (priority order as listed),
								'all': all types can be given at once,
								'None': if strategy is not 'hybrid' or 'explanation'
<MAB algorithm>/		--> 'e-greedy' or 'softmax', if strategy is 'MAB' or 'hybrid',
							'None', otherwise
<epsilon>/				--> epsilon, if strategy is 'MAB' or 'hybrid',
							'None', otherwise
<exploration type>/		--> 'far-panel' or 'new-panel', if MAB algorithm is 'e-greedy',
							'None', otherwise
<exploration bounding>/	--> exploration bounding, if exploration type is 'far-panel',
							'None', otherwise
							
							
							
*****************************
			PLOTS
*****************************

Once all runs of an experiment are done, plots are generated as following:

----------------------------
	1) get summary
----------------------------
script results/modules/get_summary.py

* checks if parameters in header are consistent with experiment_path

* summarizes all runs of the experiment, stored as a row in results/<experiment_type>/summary.csv file:
	- parameters, as described in data path:
		--> dataset_name, target, n_attributes, numeric_ratio, attribute_threshold, diversity, inclusion, startegy, algos_ratio, explanation_type, MAB_algo, epsilon, exploration_type, exploration bounding
	- results of experiment:
		#iterations		--> mean of number of iterations to find target dashboard
		#itertions_std	--> standard deviation of number of iterations to find target dashboard
		time			--> mean of computing time to find target dashboard
		time_std		--> standard deviation of computing time to find target dashboard
<experiment_type> can be:
	- 'MAB_params', if experiment is run to look at the influence of MAB parameters
	- 'paper_plots', if experiment is run to plot 'fixed dashboard', 'fixed relation'
	- 'test', otherwise

* plots some info and stores them in experiment_path:
	- time = f(#iterations)
	- distribution of '#iterations'
	- distribution of 'time'
	- distribution of '#generations per iteration'
	- distibution of 'time per iteration'
	
----------------------------
	2) plot summary
----------------------------
script results/modules/plot_summary.py


----------------------------
	3) plot F1 scores
----------------------------
script results/modules/plot_F1scores.py



