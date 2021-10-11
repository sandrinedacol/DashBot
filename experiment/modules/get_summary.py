import matplotlib.pyplot as plt
import csv
import os
from scipy.stats import norm
import matplotlib.mlab as mlab
import numpy as np

class Param():
	def __init__(self, name_value):
		self.name = name_value[0]
		self.value = name_value[1]
class Summary:
	
	def __init__(self, n_expes, experiment_path, params_names, experiment_type):

		self.n_expes = n_expes
		self.experiment_path = experiment_path
		self.params_names = params_names
		self.experiment_type = experiment_type
		self.header = (',').join(self.params_names)
		self.root_path = 'experiment/results/'
		self.path = self.root_path + self.experiment_type
		self.directory_path = experiment_path.replace(self.root_path + 'results_files/','')
		self.params_values = self.directory_path.split('/')
		self.parameters = [Param(name_value) for name_value in zip(self.params_names, self.params_values)]
		
		# check if parameters in header are consistent
		# TODO
		
		# calculate max_dist for F1 scores calculation
		n_attributes = int([param.value for param in self.parameters if param.name=='n_attributes'][0])
		numeric_ratio = float([param.value for param in self.parameters if param.name=='numeric_ratio'][0])
		self.max_dist = 0.25 + n_attributes * (numeric_ratio + 1) # TODO : put true_numeric_ratio
		
		# get all csv files
		self.files = []
		for root, dirs, files_ in os.walk(experiment_path):
			for file in files_:
				if file.endswith(".csv"):
					self.files.append((os.path.join(root, file)))

	def get_summary(self):
		summary_header = self.header + ",n_iterations_mean,n_iterations_std,time_mean,time_std,n_iterations_budgets,n_iterations_F1scores_mean,n_iterations_F1scores_std,time_budgets,time_F1scores_mean,time_F1scores_std"
		self.summary_row = '\n' + (',').join(self.params_values[:-1]) 
		
		# get iter and time
		n_generations_per_iter = []
		time_per_iter = []
		n_iter = []
		t = []
		for file in self.files:
			with open(file) as csvfile:
				reader = csv.DictReader(filter(lambda row: row[0]!='*', csvfile))
				for row in reader:
					n_generations_per_iter.append(row['n_generations'])
					time_per_iter.append(row['iteration_time'])
				n_iter.append(int(row['n_iter']) + 1)
				t.append(float(row['total_time']))
		if (len(n_iter), len(t)) != (self.n_expes, self.n_expes):
			n_iter = n_iter[-self.n_expes:]
			t = t[-self.n_expes:]
			print(f"\n!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!\n!!  This experiment have already been done!  !!\n!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!\n")
		n_iterations = {'mean': np.mean(n_iter), 'std': np.std(n_iter)}
		time = {'mean': np.mean(t), 'std': np.std(t)}
		self.min_max = {'n_iter': {'min': np.min(n_iter), 'max': np.max(n_iter)}, 'total_time': {'min': np.min(t), 'max': np.max(t)}}
		self.summary_row += f",{n_iterations['mean']},{n_iterations['std']},{time['mean']},{time['std']}"
		
		# plot iter and time
		self.title = self.get_plots_title()
		self.title = self.title + f' ({len(n_iter)} runs)'
		plt.scatter(n_iter, t)
		plt.xlabel("iterations")
		plt.ylabel("time (s)")
		plt.title(self.title, fontsize=10)
		plt.savefig(f'{self.experiment_path}/iter_time.png')
		plt.clf()
		self.get_histogram(n_iter, "iterations", 'iter', ylog=False)
		self.get_histogram(t, "time (s)", 'time', ylog=False)
		self.get_histogram(n_generations_per_iter, "#generations/iteration", 'gen_per_iter', ylog=True)
		self.get_histogram(time_per_iter, "time/iteration (s)", 'time_per_iter', ylog=True)
		
		# get and plot F1 scores
		self.get_F1_scores_mean_std('n_iter')
		self.get_F1_scores_mean_std('total_time')

		# write in summary file
		if not os.path.isfile(self.path + "/summary.csv"):
			with open(self.path + "/summary.csv", 'w') as f:
				f.write(summary_header)
		with open(self.path + "/summary.csv", 'a') as f:
			f.write(self.summary_row)

	def get_histogram(self, prop, prop_label_long, prop_label_short, ylog):
		plt.hist(prop, bins=50)
		plt.xlabel(prop_label_long)
		plt.ylabel("count")
		if ylog:
			plt.yscale('log')
		plt.title(self.title, fontsize=10)
		plt.savefig(f'{self.experiment_path}/{prop_label_short}_hist.png')
		plt.clf()

	def get_plots_title(self):
		title = ""
		for (name, value) in zip(self.params_names, self.params_values):
			if value != 'None':
				if name == 'target':
					title += f"target_size={len(value.split('_'))} / "
				elif name == 'n_attributes':
					title += f"{value} attributes "
				elif name == 'numeric_ratio':
					title += f"({int(100*float(value))}% numeric)\n"
				elif name == 'attribute_threshold':
					pass
				elif value == 'False':
					title += f'no {name} / '
				elif value == 'True':
					title += f'{name} / '
				elif name == 'epsilon':
					title += f'\u03B5={value} /'
				elif name == 'exploration_bounding':
					title += f'\u03B4={value}'
				else:
					title += f"{value} / "
		return title

	def get_F1_scores_mean_std(self, prop_str):
		
		# get budgets list
		budgets = list(np.linspace(0, self.min_max[prop_str]['max'], num=10, endpoint=True))
		F1_scores_dict = dict()
		for budget in budgets:
			F1_scores_dict[budget] = []
		
		# get F1 scores
		for file in self.files:
			distances_for_budgets = [None] * len(budgets)
			with open(file) as csvfile:
				reader = csv.DictReader(filter(lambda row: row[0]!='*', csvfile))
				for row in reader:
					for i, budget in enumerate(budgets):
						if (prop_str == 'n_iter' and budget >= int(row[prop_str])+1) or (prop_str == 'total_time' and budget >= float(row[prop_str])):
							distances_for_budgets[i] = row['distances']
			while None in distances_for_budgets:
				index = distances_for_budgets.index(None)
				del distances_for_budgets[index]
				del F1_scores_dict[budgets[index]]
				del budgets[index]
			for i, dist in enumerate(distances_for_budgets):
				distances = dist.split('/')
				distances_ = [float(dist) for dist in distances if dist != 'None']
				distance = sum(distances_)/self.max_dist
				F1_score = 1 - distance/len(distances)
				F1_scores_dict[budgets[i]].append(F1_score)
		
		# plot F1 scores
		for i in range(self.n_expes):
			y = [F1_scores_dict[budget][i] for budget in budgets]
			plt.plot(budgets, y, 'o-')
		plt.ylabel("F1 score")
		plt.xlabel(f"{prop_str} budget")
		plt.title(self.title, fontsize=10)
		plt.savefig(f'{self.experiment_path}/{prop_str}_F1_scores.png')
		plt.clf()
		
		# get summary of F1 scores
		F1_scores = {'mean': [], 'std': []}
		for budget in budgets:
			F1_scores['mean'].append(np.mean(F1_scores_dict[budget]))
			F1_scores['std'].append(np.std(F1_scores_dict[budget]))
		self.summary_row += f",\"{budgets}\",\"{F1_scores['mean']}\",\"{F1_scores['std']}\""