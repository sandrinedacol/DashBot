import pandas as pd
import numpy as np
import math

from .attribute import *

def print_value(value, n):
    if value == 0:
        printed_value = 0
    else:
        printed_value = round(value, n - int(math.floor(math.log10(abs(value)))) - 1)
        printed_value = str(printed_value)
        if printed_value[-2:] == '.0':
            printed_value = printed_value[:-2]
        if len(printed_value) > 5:
            if len(printed_value.split('e')) == 2:
                vals = printed_value.split('e')
                vals[1] = str(int(vals[1]))
                printed_value = ("&times10<sup>").join(vals) + "</sup>"
            else:
                val = str(printed_value).split('.')
                if len(val) == 1:
                    v = val[0]
                    order_of_magnitude = len(v) - 1
                    entier = v[0]
                    dec = v[1:n]
                    printed_value = f"{entier}.{dec}&times10<sup>{order_of_magnitude}</sup>"
                else:
                    v = val[1]
                    order_of_magnitude = - len(v) + n - 1
                    printed_value = f"{v[-n]}.{v[-n+1:]}&times10<sup>{order_of_magnitude}</sup>"
    return printed_value

class Panel():
    """
    A panel can either be described by:
    1) a vector : self.vector
       and a list of all Attribute objects
    2) a list of Attribute objects for GROUP BY : self.groupBy
       and a dict (with key = Attribute object, value = list of function) for aggregates : self.aggregates
    """

    def __init__(self, attributes_and_star):
        self.attributes = attributes_and_star[:-1]
        self.star = attributes_and_star[-1]

        # self.groupBy : list of Attribute objects
        self.groupBy = list()

        # self.aggregates : dict with key = Attribute object, value = list of functions
        self.aggregates = dict()

        # self.columns : MultiIndex of tuples (attribute_name, function)
        all_functions = ['groupBy', 'min', 'max', 'sum', 'avg']
        numeric_functions = ['min', 'max', 'sum', 'avg']
        attributes_names = [at.name for at in self.attributes]
        index = pd.MultiIndex.from_product( \
            (attributes_names, all_functions), names=["attribute", "function"])
        non_numeric_names = [at.name for at in self.attributes if not at.is_numeric]
        to_remove = [ (at,f) for f in numeric_functions for at in non_numeric_names ]
        self.columns = index.copy().drop(to_remove)
        self.columns = self.columns.insert(0, ('*','count'))
        self.size = len(self.columns)

        # self.vector : Series with index = self.columns
        self.vector = pd.Series(np.zeros( shape = self.columns.size, dtype = 'int'), index = self.columns )

    def __len__(self):
        return len(self.groupBy) + len(self.aggregates)

    def show(self):
        return print(pd.DataFrame([self.vector]))

    # put values in self.vector from self.groupBy and self.aggregates
    def attributes_to_vector(self):
        # Just in case...
        self.vector = pd.Series(np.zeros( shape = self.columns.size, dtype = 'int'), index=self.columns )

        for attribute in self.groupBy:
            self.vector[attribute.name, 'groupBy'] = 2 # TODO : gérer le cas = 1
        for attribute, functions in self.aggregates.items():
            for f in functions:
                self.vector[attribute.name, f] += 1

    # put Attribute objects in self.groupBy
    # in self.aggregates : put items 'Attribute object : [function]' or add function in functions list if key already exists
    def vector_to_attributes(self):
        # Just in case...
        self.groupBy = list()
        self.aggregates = dict()

        for attribute_name, function in self.vector[lambda n : n > 0].index:
            if (attribute_name, function) == ('*', 'count'):
                self.aggregates[self.star] = ['count']
            else:
                attribute = [at for at in self.attributes if at.name == attribute_name][0]
                if function == 'groupBy':
                    self.groupBy.append(attribute)
                else:
                    self.aggregates.setdefault(attribute, []).append(function)
                    # try:
                    #     self.aggregates[attribute].append(function)
                    # except KeyError:
                    #     self.aggregates[attribute] = [function]

    def get_attributes_names(self):    
        groupBy_names = [at.name for at in self.groupBy]
        groupBy_discretized_names = [f'discretized_{at.name}' if at.discretized else at.name for at in self.groupBy]
        aggregate_names = dict()
        for attribute, functions in self.aggregates.items():
            aggregate_names[attribute.name] = functions[:]
        return groupBy_names, groupBy_discretized_names, aggregate_names

    # generate table from self.groupBy and self.aggregates
    def to_table(self, dataset):
        groupBy_names, groupBy_discretized_names, aggregate_names = self.get_attributes_names()
        for functions in aggregate_names.values():
            for func in functions:
                if func == 'avg':
                    functions.remove('avg')
                    functions.append('mean')
        grouped_dataset = dataset.groupby(by = groupBy_discretized_names)
        if '*' in aggregate_names:
            if len(aggregate_names)>1:
                del aggregate_names['*']
                table_agg = grouped_dataset.agg(aggregate_names)
                table_count = grouped_dataset.size().reset_index(name=('*','count')).set_index(groupBy_discretized_names)
                table = pd.concat([table_count, table_agg], axis=1)
            else:
                table = grouped_dataset.size().reset_index(name=('*','count')).set_index(groupBy_discretized_names)
        else:
            table = grouped_dataset.agg(aggregate_names)
        table.index.names = groupBy_names
        return table

    def table_to_list(self, dataset):
        table = self.to_table(dataset)
        table.fillna('', inplace=True)
        n_rows = table.shape[0]
        values = list()
        for row in range(n_rows):
            sub_dict = dict()
            # groupBy
            for i, at_name in enumerate(table.index.names):
                if len(self.groupBy) == 1:
                    at = self.groupBy[0]
                    value = table.index[row]
                else:
                    at = [at for at in self.groupBy if at.name == at_name][0]
                    value = table.index[row][i]
                if at.discretized:
                    if at.type == 'int':
                        value = [int(x) for x in value.split('_')]
                    else:
                        value = [float(x) for x in value.split('_')]
                sub_dict[at.name] = value
            # aggregation
            for att, functions in self.aggregates.items():
                for func in functions:
                    if func == 'avg':
                        func_ = 'mean'
                    else:
                        func_ = func
                    value = table[att.name][func_].iloc[row]
                    try:
                        if value.dtype == 'int':
                            value = int(value)
                        else:
                            value = float(value)
                    except AttributeError:
                        pass
                    sub_dict[f'{att.name}_{func}'] = value
            values.append(sub_dict)
        
        return values
       
    def to_result_table(self, dataset):
        table = self.to_table(dataset)
        # groupBy_attributes = [at for at in attributes if at.name in table.index.names]
        # new_values = dict()
        # for at in groupBy_attributes:
        #     if at.discretized:
        #         new_values[at.name]=[]
        #         new_values = list()
        #         for value in table.index:
        #             new_values.append(f"[{('-').join(value.split('_'))}]")
        table = table.applymap(lambda x: print_value(x,2), na_action='ignore')
        table = table.reset_index()
        result_table = table.to_html(
            na_rep='-', 
            escape=False, 
            justify='justify-all', 
            index=False, 
            border=0,
            classes=["table-striped",  "table-sm"])
        result_table = ('''"table''').join(result_table.split('''"dataframe'''))
        return result_table
    
    # write query from self.vector
    def to_query(self):
        groupBy_names, _, aggregate_names = self.get_attributes_names()
        groupBy = str()
        select = str()
        for attribute in groupBy_names:
            groupBy += f'{attribute}, '
            select += f'{attribute}, '
        groupBy = groupBy[:-2]
        for attribute, functions in self.aggregates.items():
            aggregate_names[attribute.name] = functions
        for attribute, functions in aggregate_names.items():
            for f in functions:
                select += f"{f}({attribute}), "
        select = select[:-2]
        return {'select': select, 'groupBy': groupBy}

    def to_content(self):
        
        groupBy_bool = dict()
        for att in self.attributes:
            if att in self.groupBy:
                groupBy_bool[att.name] = True
            else:
                groupBy_bool[att.name] = False
        
        aggregates_bool = {'*': {'count': False}}
        for att in [at for at in self.attributes if at.is_numeric]:
            aggregates_bool[att.name] = dict()
            for func in ['min', 'max', 'avg', 'sum']:
                aggregates_bool[att.name][func] = False
        for att, functions in self.aggregates.items():
            for func in functions:
                aggregates_bool[att.name][func] = True
        return {'groupBy': groupBy_bool, 'aggregates': aggregates_bool}


        
    def reset(self):
        self.vector = pd.Series(np.zeros( shape = self.columns.size, dtype = 'int'), index=self.columns )
        self.groupBy = list()
        self.aggregates = dict()

    def copy_from_vector(self):
        new_panel = Panel(self.attributes + [self.star])
        new_panel.vector = self.vector.copy()
        new_panel.vector_to_attributes()
        return new_panel




class Dash(Panel):
    """
    Objects containing several panels.
    e.g. : dashboard (both modes) and target dashboard (experiment mode)
    """

    def __init__(self, attributes_and_star):
        super().__init__(attributes_and_star)
        self.index = pd.MultiIndex(levels=[[],[]], codes=[[],[]], names=[u'panel', u'suggestion'])
        self.dataframe = pd.DataFrame(columns=self.columns, index=self.index )
        self.dict = dict()
        self.attributes_on = set()

    def __len__(self):
        return self.dataframe.shape[0]

    def show(self):
        return print(self.dataframe)

    def add_panel(self, panel, index):
        if type(index) == int:
            self.dataframe.loc[index] = panel.vector.copy()
        elif type(index) == tuple:
            self.dataframe.loc[index,:] = panel.vector.copy()
        self.dataframe = self.dataframe.astype(int)
        self.dict[index] = panel.vector.tolist()