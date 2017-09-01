import csv
from pprint import pprint
from collections import defaultdict
from copy import copy
import numpy as np

def float_or_zero(value):
    try:
        return float(value)
    except ValueError:
        return 0.0

class Sam():
    def __init__(self, name, inputs, outputs, output_tax, consumption, consumers):
        """ read the sam matrix into self.entries column sums in self.column_sum

        Table must have index as upper left title, column sum titled sum are not
        read. Everything in and after the row that begin with sum is ignored """
        self.inputs, self.outputs, self.output_tax = inputs, outputs, output_tax
        self.consumption, self.consumers = consumption, consumers

        entries = defaultdict(dict)
        with open(name,'rU') as csvfile:
            reader = csv.DictReader(csvfile)
            fields = copy(reader.fieldnames)
            fields.remove('index')
            fields.remove('sum')
            for row in reader:
                rowindex = row['index']
                if rowindex == 'sum':
                    break
                for cellindex, cell in row.items():
                    if cellindex not in ['index', 'sum']:
                        entries[rowindex][cellindex] = float_or_zero(cell)

        column_sum = {}
        for col in fields:
            column_sum[col] = sum(item[col] for item in entries.values())

        self.entries, self.column_sum = dict(entries), column_sum

    def utility_function(self):
        """ the utility functions exponents as values in a dict """
        entries, column_sum = self.entries, self.column_sum
        output_tax_shares = self.output_tax_shares()

        utility_functions = {}
        for consumer in self.consumers:
            alphas = {}
            for input in self.consumption:
                alphas[input] = entries[input][consumer] / column_sum[consumer]
            utility_functions[consumer] = alphas

        return utility_functions

    def production_functions(self):
        """ returns the the tax adjusted cobb-douglas parameters as a per firm
        dictionary of tuples, the
        tuple contains the scalar b and a dictionary with the cobb-douglas
        coefficients """
        entries, column_sum = self.entries, self.column_sum
        output_tax_shares = self.output_tax_shares()
        betas = defaultdict(dict)
        b = {}
        production_functions = {}

        for firm in self.outputs:

            for input in self.outputs:
                betas[firm][input] = entries[input][firm] / ((1 - output_tax_shares[firm]) * column_sum[firm])

            for input in ['cap', 'lab']:
                betas[firm][input] = entries[input][firm] / ((1 - output_tax_shares[firm]) * column_sum[firm])


            b[firm] = (column_sum[firm]
                       / np.prod([entries[input][firm] ** betas[firm][input]
                                  for input in self.inputs]))

            production_functions[firm] = (b[firm], dict(betas[firm]))

        return production_functions

    def output_tax_shares(self):
        """ returns how much of each firms output is taxed in an output tax """
        entries, column_sum, output_tax = self.entries, self.column_sum, self.output_tax
        output_tax_shares = {}
        for firm in self.outputs:
            output_tax_shares[firm] = (entries[output_tax][firm]
                                       / (sum([entries[input][firm]
                                              for input in self.inputs]) + entries[output_tax][firm]))
        output_tax_shares['cap'] = output_tax_shares['lab'] = 0
        return output_tax_shares

    def endowment(self, name):
        """ returns the endowment of the whole economy for each factor """
        assert name in self.inputs
        return self.column_sum[name]

    def endowment_vector(self, column):
        """ return the each row entry for a column """
        return {row_name: self.entries[row_name][column] for row_name in self.entries}

    def investment_share(self, von, zu):
        """ returns """
        return self.column_sum[zu] / sum(self.entries[von].values())

    def initial_investment(self, zu):
        return self.column_sum[zu]

    def money(self):
        return sum([self.column_sum[input] for input in self.inputs])

    def balance_of_payment(self, netexport, investment):
        return self.entries[investment][netexport]



