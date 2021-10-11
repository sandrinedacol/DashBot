import matplotlib.pyplot as plt
import matplotlib.cm as cm
import csv
from scipy.stats import norm
import matplotlib.mlab as mlab
import numpy as np
import pandas as pd
import itertools

class Plots:

	def __init__(self, experiment_type, run_on_serveur=True):
		self.experiment_type = experiment_type
		if run_on_serveur:
			self.root_path = f'experiment/results/{experiment_type}/'
		else:
			self.root_path = f'/home/sandrine/DashBot/bandits-and-applications/code/DashBot/experiment/results/{experiment_type}/'
		
	def get_plots(self):
		summary_file = self.root_path + 'summary.csv'

		if self.experiment_type == 'paper_plots':
			columns = [
			'strategy', 'n_attributes', 'dashboard_size',
			'n_iterations_mean', 'n_iterations_std',
			'time_mean', 'time_std',
			'n_iterations_budgets', 'n_iterations_F1scores_mean', 'n_iterations_F1scores_std',
			'time_budgets', 'time_F1scores_mean', 'time_F1scores_std'
			]
			summary = self.put_summary_into_dataframe(summary_file, columns)
			self.get_paper_plots(summary)

		elif self.experiment_type == 'MAB_params':
			columns = [
			'strategy', 'n_attributes', 'dashboard_size',
			'epsilon', 'exploration_bounding', 'sigma', 'temperature',
			'n_iterations_mean', 'n_iterations_std',
			'time_mean', 'time_std'
			]
			summary = self.put_summary_into_dataframe(summary_file, columns)
			self.get_MAB_plots(summary)


		elif self.experiment_type == 'test':
			pass


	# *********************************************************
	# 				Summary to dataframe
	# *********************************************************

	def put_summary_into_dataframe(self, summary_file, columns):
		summary = pd.DataFrame(columns=columns)
		with open(summary_file, 'r') as f:
			reader = csv.DictReader(f)
			for row in reader:
				new_row = dict()
				for col in columns:
					if col == 'strategy':
						new_row['strategy'] = self.define_strategy(row)
					elif col == 'n_attributes':
						new_row['n_attributes'] = int(row['n_attributes'])
					elif col == 'dashboard_size':
						new_row['dashboard_size'] = len(row['target'].split('_'))
					elif col in ['epsilon', 'exploration_bounding', 'sigma', 'temperature']:
						if row[col] == 'None':
							new_row[col] = row[col]
						else:
							new_row[col] = float(row[col])
					elif col in ['n_iterations_mean', 'n_iterations_std', 'time_mean', 'time_std']:
						new_row[col] = float(row[col])
					elif 'budgets' in col or 'F1scores' in col:
						new_row[col] = row[col].strip('][').split(', ')
						new_row[col] = [float(elem) for elem in new_row[col]]
					
				summary = summary.append(new_row, ignore_index=True)
		return summary

	def define_strategy(self, row):
		strategy = ""
		for param in ['strategy', 'algos_ratio', 'MAB_algo', 'exploration_type']:
			if row[param] != 'None':
				strategy += row[param] + ' '
		return strategy[:-1]

	# *********************************************************
	# 				Plots
	# *********************************************************

	def get_paper_plots(self, summary):
		# https://matplotlib.org/stable/tutorials/colors/colormapnorms.html https://matplotlib.org/stable/tutorials/colors/colorbar_only.html
		# n_plots = summary[continuous_parameter].nunique()
		# color_map = cm.get_cmap('magma', n_plots)
		color_map = cm.get_cmap("Set1")
		for prop in ('n_iterations', 'time'):

			# fixed dashboard and fixed relation
			for param_1_name, param_2_name in [('n_attributes', 'dashboard_size'), ('dashboard_size', 'n_attributes')]:
				for param_1 in summary[param_1_name].unique():
					df_1 = summary[summary[param_1_name]==param_1]
					for i, strategy in enumerate(df_1['strategy'].unique()):
						df_2 = df_1[df_1['strategy']==strategy]
						x, y, yerr = [], [], []
						for param_2 in sorted(list(df_2[param_2_name].unique())):
							df_3 = df_2[df_2[param_2_name]==param_2]
							if df_3.shape[0] > 1:
								print(f'too many experiments for strategy {strategy}, {param_1_name} = {param_1} and {param_2_name} = {param_2}')
								break
							x.append(param_2)
							y.append(float(df_3[f'{prop}_mean']))
							yerr.append(float(df_3[f'{prop}_std']))
						plt.plot(x, y, 'o-', label=strategy, color = color_map(i))
						plt.errorbar(x, y, yerr=yerr, capsize=5, color = color_map(i))
					if param_1_name == 'dashboard_size':
						title = f'fixed dashboard ({param_1} panels)'
					else:
						title = f'fixed relation ({param_1} attributes)'
					plt.xlabel(param_2_name)
					# plt.xscale('log')
					if prop == 'time':
						plt.ylabel('time (s)')
					else:
						plt.ylabel('n_iterations')
					plt.yscale('log')
					plt.legend(title='strategy')
					plt.title(title)
					plt.savefig(f'{self.root_path}/{param_2_name}_{prop}_{param_1}.png')
					plt.clf()

			# F1 scores
			for n_attributes in summary['n_attributes'].unique():
				df_1 = summary[summary["n_attributes"]==n_attributes]
				for dashboard_size in summary['dashboard_size'].unique():
					df_2 =  df_1[df_1["dashboard_size"]==dashboard_size]
					for i, strategy in enumerate(df_1['strategy'].unique()):
						df_3 = df_2[df_2['strategy']==strategy]
						if df_3.shape[0] > 1:
							print(f'too many experiments for strategy {strategy}, n_attributes = {n_attributes} and dashboard_size = {dashboard_size}')
							continue
						elif df_3.shape[0] == 0:
							continue
						x = df_3.iloc[0].at[f"{prop}_budgets"]
						y = df_3.iloc[0].at[f"{prop}_F1scores_mean"]
						yerr = df_3.iloc[0].at[f"{prop}_F1scores_std"]
						plt.plot(x, y, 'o-', label=strategy, color = color_map(i))
						plt.errorbar(x, y, yerr=yerr, capsize=5, color = color_map(i))
					
					title = f'F1 score (dashboard = {dashboard_size} panels / relation = {n_attributes} attributes)'
					if prop == 'time':
						plt.xlabel('computing time budget (s)')
					else:
						plt.xlabel('iteration budget')
					plt.ylabel(f"F1 score")
					plt.legend(title='strategy')
					plt.title(title)
					plt.savefig(f'{self.root_path}/{prop}_F1score_{dashboard_size}_{n_attributes}.png')
					plt.clf()

	def get_MAB_plots(self, summary):
		# https://matplotlib.org/stable/tutorials/colors/colormapnorms.html https://matplotlib.org/stable/tutorials/colors/colorbar_only.html
		for prop in ('n_iterations', 'time'):

			for strategy in summary['strategy'].unique():
				df1 = summary[summary['strategy']==strategy]
				dashboard_size_n_attributes_values = [list(df1['dashboard_size'].unique()), list(df1['n_attributes'].unique())]

				for dashboard_size, n_attributes in itertools.product(*dashboard_size_n_attributes_values):
					title = f'{strategy}\n(dashboard = {dashboard_size} panels / relation = {n_attributes} attributes)'
					df2 = df1[df1['dashboard_size']==dashboard_size]
					df2 = df2[df2['n_attributes']==n_attributes]
					p1 = 'epsilon'
					if 'softmax' in strategy:
						p2 = 'temperature'
					elif 'e-greedy' in strategy:
						if 'far-panel' in strategy:
							p2 = 'exploration_bouding'
						elif 'hybrid' in strategy:
							p2 = 'sigma'
					# for param_1_name, param_2_name in [('epsilon', 'exploration_bounding'), ('exploration_bounding', 'epsilon')]:
					for param_1_name, param_2_name in [(p1, p2), (p2, p1)]:
						n_plots = df2[param_2_name].nunique()
						color_map = cm.get_cmap('viridis', n_plots)
						# https://matplotlib.org/stable/tutorials/colors/colormapnorms.html https://matplotlib.org/stable/tutorials/colors/colorbar_only.html
						for i, param_2 in enumerate(sorted(list(df2[param_2_name].unique()))):
							df3 = df2[df2[param_2_name]==param_2].sort_values(by=[param_1_name])
							x = df3[param_1_name].to_list()
							y = df3[f"{prop}_mean"].to_list()
							yerr = df3[f"{prop}_std"].to_list()
							plt.plot(x, y, 'o-', label=param_2, color = color_map(i))
							plt.errorbar(x, y, yerr=yerr, capsize=5, color = color_map(i))
						plt.xlabel(param_1_name)
						plt.xscale('log')
						plt.ylabel(prop)
						# plt.yscale('log')
						plt.legend(title=param_2_name)
						plt.title(title)
						plt.savefig(f'{self.root_path}/{strategy}_{param_1_name}-{prop}.png')
						plt.clf()


if __name__ == '__main__':
	plots = Plots('MAB_params', run_on_serveur=False)
	plots.get_plots()

# params_names = ['dataset_name', 'target', 'n_attributes', 'numeric_ratio', 'attribute_threshold', 'diversity', 'inclusion', 'strategy', 'algos_ratio', 'explanation_type', 'epsilon', 'MAB_algo', 'exploration_type', 'exploration_bounding']


