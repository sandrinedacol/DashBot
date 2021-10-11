import pandas as pd 
import pickle
import os

def load_datasets(dataset_name):

    dataset_name_ = ""
    if dataset_name == 'MARS':
        dataset_name_ = 'MARS_EN_total'
    elif dataset_name == "MARS (demo)":
        dataset_name_ = 'MARS_EN_reduced'
    else:
        dataset_name_ = dataset_name

    cache_pkl = f'implem/preprocessing_cache/{dataset_name_}.pkl'

    try:
        with open(cache_pkl, 'rb') as f:
            preprocessing = pickle.load(f)
        cache_found = True
        print(f'load preprocess from {cache_pkl}\n')
        return cache_pkl, cache_found, preprocessing
        
    except IOError:
        print(f'{cache_pkl} not found, start pre-processing...')
        cache_found = False
        try:
            os.mkdir('implem/preprocessing_cache/')
        except FileExistsError:
            pass
        # load dataset
        if dataset_name == 'test':
            dataset_file = "implem/dataset/data.csv"
        if dataset_name == 'MARS':
            dataset_file = "implem/dataset/MARS/MARS.csv"
        if dataset_name == 'MARS (demo)':
            dataset_file = "implem/dataset/MARS/MARS.csv"
        if dataset_name == 'NBA':
            dataset_file = "https://media.geeksforgeeks.org/wp-content/uploads/nba.csv"
        if dataset_name == "Country":
            dataset_file = "implem/dataset/Country-data.csv" # https://www.kaggle.com/rohan0301/unsupervised-learning-on-country-data
        if dataset_name == "Data Avalanche":
            dataset_file = "implem/dataset/ANENA/ANENA.csv"
        if dataset_name == "SERAC":
            dataset_file = "implem/dataset/SERAC/SERAC.csv" 
        if dataset_name == "MovieLens":
            dataset_file = "implem/dataset/MovieLens/MovieLens.csv"
        return cache_pkl, cache_found, dataset_file