import pandas as pd
import pickle
import os



cache_pkl = './implem/preprocessing_cache/MARS_EN_total.pkl'

with open(cache_pkl, 'rb') as f:
    preprocessing = pickle.load(f)
    attributes_info, dataset_info = preprocessing # attributes_info : # name, type_, is_numeric, variance, adomSize, classe, distretized, entropy

# # /// change columns names ///
# for att_info in attributes_info:
#     att_name = att_info['name']
#     if att_name == 'alcool (g/j)':
#         att_name = "quantite alcool"
#     else:
#         att_name = att_name.split(' (')[0]
#     att_info['name'] = att_name
# col_names = list(dataset_info['preprocessed_dataset'].columns)
# for i,col_name in enumerate(col_names):
#     if col_name == 'alcool (g/j)':
#         col_names[i] = "quantite alcool"
#     elif col_name == 'discretized_alcool (g/j)':
#         col_names[i] = "discretized_quantite alcool"
#     else:
#         col_names[i] = col_name.split(' (')[0]
# dataset_info['preprocessed_dataset'].columns = col_names


# /// modify values in dataframe ///
def switch_F_to_M(value):
    new_value = ''
    if value == 'F':
        new_value = 'M'
    elif value == 'M':
        new_value = 'F'
    return new_value
dataset_info['preprocessed_dataset']['gender'] = dataset_info['preprocessed_dataset']['gender'].apply(switch_F_to_M)
dataset_info['preprocessed_dataset'] = dataset_info['preprocessed_dataset'].drop(columns=['sexe'])


# # /// modify values in dataframe ///
# def switch_NSP_to_DNA(value):
#     new_value = ''
#     if value == 'NSP':
#         new_value = 'DNA'
#     else:
#         new_value = value
#     return new_value
# dataset_info['preprocessed_dataset'] = dataset_info['preprocessed_dataset'].applymap(switch_NSP_to_DNA)

# # /// change columns names ///
# for att_info in attributes_info:
#     att_name = att_info['name']
#     if att_name == 'PSG-PST':
#         att_name = "PSG_PST"
#     att_info['name'] = att_name
# col_names = list(dataset_info['preprocessed_dataset'].columns)
# for i,col_name in enumerate(col_names):
#     if col_name == 'PSG-PST':
#         col_names[i] = "PSG_PST"
#     elif col_name == 'discretized_PSG-PST':
#         col_names[i] = "discretized_PSG_PST"
# dataset_info['preprocessed_dataset'].columns = col_names


# # /// select some attributes ///
# attributes_names = ['gender', 'age', 'BMI', 'PSG_AHI', 'sleep_duration', 'cephalgia']
# attributes_info = [at for at in attributes_info if at['name'] in attributes_names]
# attributes_names_extended = attributes_names
# for at in attributes_info:
#     if at['discretized']:
#         attributes_names_extended.append(f"discretized_{at['name']}")
# dataset_info['preprocessed_dataset'] = dataset_info['preprocessed_dataset'][attributes_names_extended]






with open(cache_pkl, 'wb') as f:
    preprocessing = attributes_info, dataset_info
    pickle.dump(preprocessing, f)
            
