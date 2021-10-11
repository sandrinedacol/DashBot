import pandas as pd
import dateutil.parser as dparser
import math

def replace_binary_value(old_value):
    if old_value == 0:
        new_value = False
    elif old_value == 1:
        new_value = True
    else:
        new_value = old_value
    return new_value

def replace_date_value(date):
    return dparser.parse(str(date),fuzzy=True)

class Attribute:

    def __init__(self, dataset=None, column_index=None, cache_found=True):
        
        # calculated when created
        if not cache_found:
            self.data = dataset.iloc[:,column_index] # object pd.Series
            self.name = self.data.name.strip()
            # date
            if 'date' in self.name:
                print(f"Do you think these data are date type ? (y/n):\n{self.data.dropna().unique()}")
                U_answer = input()
                if U_answer == 'y':
                    data = self.data.apply(replace_date_value)
                    print(f"Do you think it is now in the right format ? (y/n):\n{data.dropna().unique()}")
                    U_answer = input()
                    if U_answer == 'y':
                        self.data = data
            # id are not int
            if '_id' in self.name:
                self.data = self.data.astype(str)
            # bool
            if set(self.data.dropna().unique().tolist()) == {0,1}:
                self.data = self.data.apply(replace_binary_value)
            self.type = self.data.dtype
            self.is_numeric = False
            self.variance = None
            if self.type in ['int', 'float','<M8[ns]']:
                self.is_numeric = True
                
                # # variance on raw data
                # self.variance = self.data.var(ddof=0)
                
                # variance on data normalized between min and max
                mini = self.data.min()
                maxi = self.data.max()
                normalize = lambda x: (x-mini)/(maxi-mini)
                normalized_data = self.data.apply(normalize)
                self.variance = normalized_data.var(ddof=0)
                self.variance = normalized_data.var(ddof=0)
                
                # # variance on data normalized with mean
                # mean = self.data.mean()
                # normalize = lambda x: x/mean
                # normalized_data = self.data.apply(normalize)
                # self.variance = normalized_data.var(ddof=0)
                
            
            if self.type == object:
                self.data = self.data.map(lambda x: str(x).strip(),  na_action='ignore')
            self.adomSize = len(self.data.value_counts())
        else:
            self.name = None
            self.type = None
            self.is_numeric = None
            self.variance = None
            self.adomSize = None

        # calculated during preprocessing
        self.classe = str()
        self.discretized = False
        self.discretized_data = pd.Series()
        self.discretized_adomSize = None
        self.entropy = float()
        
        # used during panel generation
        self.bad_groupBy = 0
        self.on_dashboard = False
        self.bad_agg = list()  # list of bad aggregation attributes if self is GROUP BY attribute
        self.bad_func = list()  # list of bad functions if self is aggregation attribute

