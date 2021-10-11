import pandas as pd
import numpy as np
from scipy.stats import entropy
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans

from .attribute import *
from implem.dataset.datasets import *

class DataPreprocessor:

    def __init__(self, dataset_name, attribute_threshold, discretize_K):
        """ create dataset, attributes"""
        self.attribute_threshold = attribute_threshold
        self.discretize_K = discretize_K
        cache_pkl, cache_found, dataset = load_datasets(dataset_name)

        if cache_found:
            attributes_info, dataset_info = dataset
            self.dataset = dataset_info['preprocessed_dataset']
            self.n_rows = dataset_info['n_rows']
            self.attributes = list()

            
            # attributes = ['PSG_AHI', 'gender', 'age', 'BMI', 'cephalgia', 'NYHA']
            # new_dataset_info = dataset_info
            # df = pd.DataFrame()
            # for col in new_dataset_info['preprocessed_dataset'].columns:
            #     for att in attributes:
            #         if att in col:
            #             df[col] = new_dataset_info['preprocessed_dataset'][col]
            # new_dataset_info['preprocessed_dataset'] = df           
            # new_attributes_info = list()
            for att_info in attributes_info:
                att = Attribute()
                att.name = att_info['name']
                att.type = att_info['type']
                att.is_numeric = att_info['is_numeric']
                att.variance = att_info['variance']
                att.adomSize = att_info['adomSize']
                att.classe = att_info['classe']
                att.discretized = att_info['discretized']
                att.discretized_adomSize = att_info['discretized_adomSize']
                att.entropy = att_info['entropy']
                self.attributes.append(att)
            #     if att_info['name'] in attributes:
            #         new_attributes_info.append(att_info)
            # with open(cache_pkl, 'wb') as f:
            #     preprocessing = new_attributes_info, new_dataset_info
            #     pickle.dump(preprocessing, f)
            
            
        else:
            dataset_file = dataset
            self.raw_dataset = pd.read_csv(dataset_file, header=0)
            self.n_rows = self.raw_dataset.shape[0]
            self.attributes = [Attribute(self.raw_dataset, column_index, cache_found) for column_index in range(self.raw_dataset.shape[1])]

            # preprocess data
            self.preprocess_attributes(self.attributes)
            self.attributes = [at for at in self.attributes if at.classe != 'd']
            self.dataset = self.generate_preprocessed_dataset(self.attributes)
            print(f"pre-process done, copy to {cache_pkl}...")
            attributes_info = list()
            for att in self.attributes:
                att_info = {"name": att.name, "type" : att.type, "is_numeric": att.is_numeric, "variance": att.variance, "adomSize": att.adomSize, "classe": att.classe, "discretized": att.discretized,  "discretized_adomSize": att.discretized_adomSize, "entropy": att.entropy}
                attributes_info.append(att_info)
            dataset_info = {'preprocessed_dataset': self.dataset, 'n_rows': self.n_rows}
            with open(cache_pkl, 'wb') as f:
                preprocessing = attributes_info, dataset_info
                pickle.dump(preprocessing, f)
                

    def define_class(self, att):
        """
        Define attribute.classe and attribute.discretized
        """
        if att.adomSize <= self.attribute_threshold:
            att.classe = 'a'
        else:
            if att.is_numeric == True:
                att.discretized = True
                att.classe = 'b'
            else:
                if att.adomSize == self.n_rows:
                    att.classe = 'd'
                else:
                    att.classe = 'c'

    def discretize(self, att):
        """
        Calculate attribute.discretized_data : data to use for GROUP BY attribute
        """

        if att.discretized == True:
                
            # # -----------------------------------------
            # # OPTION 1 : cut in equal intervals
            # # -----------------------------------------
            # at.discretized_data = pd.cut(at.data, attribute_threshold)

            # # -----------------------------------------
            # OPTION 2 : clustering K-means
            # # -----------------------------------------
            index_of_non_nan = [i for i in att.data.index if att.data.notna()[i]]
            values = np.array(att.data.dropna()).reshape(-1, 1)
            
            # a) Choice of K
            if self.discretize_K: # if U wants to choose K for each attribute to discretize
                inertias = []
                space_of_k = list(range(2,min(30, int(att.data.size/10))))
                for k in space_of_k:
                    kmeans = KMeans(n_clusters=k).fit(values)
                    inertias.append(kmeans.inertia_)
                plt.plot(space_of_k, inertias)
                plt.xlabel("K")
                plt.ylabel("inertia")
                plt.title(att.name)
                print(f"Choose a number K for clustering of attribute '{att.name}' :")
                plt.show()
                att.discretized_adomSize = int(input())
            else:  # if U doesn't want to choose K, K = attribute_threshold for all attributes to discretize
                att.discretized_adomSize = self.attribute_threshold

            # b) K-means clustering
            kmeans = KMeans(n_clusters = att.discretized_adomSize).fit(values)
            
            # c) Discretize data
            att.discretized_data = att.data.copy()

            # # -----------------------------------------
            # # OPTION 1 : discretized value = centroid
            # # -----------------------------------------
            # centroids = kmeans.cluster_centers_
            # at.discretized_data = at.data.copy()
            # for non_nan_index, true_index in enumerate(index_of_non_nan):
            #         classe = kmeans.labels_[non_nan_index]
            #         at.discretized_data[true_index] = centroids[classe]

            # -----------------------------------------
            # OPTION 2 : discretized value = interval
            # -----------------------------------------
            df = pd.DataFrame(att.data.dropna())
            df['Kmeans_class'] = kmeans.labels_
            mini = df.groupby(by=['Kmeans_class']).min()
            maxi = df.groupby(by=['Kmeans_class']).max()
            interval = list()
            for k in range(att.discretized_adomSize):
                # interval.append(pd.Interval(float(mini.loc[k]), float(maxi.loc[k]), closed='both'))
                mini_k = str(mini.at[k,mini.columns[0]])
                maxi_k = str(maxi.at[k,maxi.columns[0]])
                interval.append(f"{mini_k}_{maxi_k}")
            new_column = att.discretized_data.to_list()
            for non_nan_index, true_index in enumerate(index_of_non_nan):
                classe = kmeans.labels_[non_nan_index]
                new_column[true_index] = interval[classe]
            att.discretized_data = pd.Series(new_column)

    def calculate_entropy(self, att):
        if not att.discretized:
            list_of_prop = att.data.value_counts(normalize = True)  # proportion of tuples that have value x
        else:
            list_of_prop = att.discretized_data.value_counts(normalize = True)
        att.entropy = entropy(list_of_prop, base = 2)

    def preprocess_attributes(self):
        for att in self.attributes:
            self.define_class(att)
            self.discretize(att)
            self.calculate_entropy(att)

    def generate_preprocessed_dataset(self):
        preprocessed_dataset = pd.DataFrame()
        for att in self.attributes:
            preprocessed_dataset[att.name] = att.data
        for att in self.attributes:
            if att.discretized:
                preprocessed_dataset[f"discretized_{att.name}"] = att.discretized_data
        print(preprocessed_dataset)
        return preprocessed_dataset



    