import os
import json
import pandas as pd
from ggplot import *
import statsmodels.formula.api as sm
from statsmodels.sandbox.regression.predstd import wls_prediction_std
import cPickle as pickle

# nonsensicle seris bank_2015-12-24_16-12 is the strange series 10

def read_series(throw_away, exclude=[]):
    dfs = []
    series = 0
    # index = []
    before_injection_percentage = -1

    directory = os.path.abspath('./result/')
    all_subdirs = [os.path.join(directory, name)
                   for name in os.listdir(directory)
                   if os.path.isdir(os.path.join(directory, name))]

    for directory in all_subdirs:
        try:
            with open(directory + '/description.txt', 'r') as myfile:
                desc = myfile.read()
            try:
                desc = json.loads(desc)
            except ValueError:
                print(desc)
                print(directory)
                continue

            injection_percentage = desc['percentage_injection']

            data = pd.read_csv(directory + '/aggregate_firm.csv')[throw_away:]
            data['injection_percentage'] = injection_percentage
            if desc['percentage_injection'] < before_injection_percentage:  # color groups
                series += 1
            data['series'] = series
            if series not in exclude:
                dfs.append(data)
            before_injection_percentage = injection_percentage
        except IOError:
            print('IOError:', directory)
    with open('cache_systematic_graphs.json', 'wb') as jfile:
        pickle.dump(dfs, jfile)
    return dfs

def load_series():
    with open('cache_systematic_graphs.json', 'rb') as jfile:
        dfs = pickle.load(jfile)
    return dfs


def vector(dfs, column, time=None, time_vector=None, func=None, index=None, color=None):
    series = []
    i = 0
    for df in dfs:
        if time is not None:
            series.append(df[column][time])
        elif func is not None:
            series.append(func(df[column]))
        elif time_vector is not None:
            series.append(df[column][time_vector[i]])
        elif index is not None:
            series.append(df['injection_percentage'][1])
        elif color is not None:
            series.append(df['series'][1])
        i += 1
    return series

def plot_with_confidence_interval(variable, title):
    result = sm.ols(formula=variable + " ~ 1 + index + index2", data=df).fit()
    print(result.summary())
    df['fittedvalues'] = result.fittedvalues
    prstd, iv_l, iv_u = wls_prediction_std(result)
    df['iv_u'] = iv_u
    df['iv_l'] = iv_l

    graph = (ggplot(aes(x='index', ymax='iv_u', ymin='iv_l'), data=df) +
             geom_area(alpha=0.2) +
             geom_line(aes(x='index', y='fittedvalues')) +
             geom_point(aes(x='index', y=variable)) +
             ggtitle(title) +
             ylab(title) +
             xlab("Injection of Money as a Percentage of Total Money in the Economy"))
    if variable == 'long_run_percentage_output':
        graph += ylim(-0.01, 0.06)
    print(graph)
    # ggsave(graph, file_name=variable + ".pdf")


if __name__ == '__main__':
    throw_away = 1
    policy_change = 10 + throw_away
    dfs = read_series(throw_away, exclude=[10])
    # dfs = load_series()
    print('num simulations', len(dfs))
    for df in dfs:
        df['coef_variation_price'] = df['price_std'] / df['price']

    df = pd.DataFrame()
    df['index'] = vector(dfs, 'price_std', index=True)
    df['series'] = vector(dfs, 'price_std', color=True)
    df['index2'] = df['index'] ** 2

# coef_variation_price
    df['max_coef_variation_price'] = vector(dfs, 'coef_variation_price', func=max)
    df['before_coef_variation_price'] = vector(dfs, 'coef_variation_price', time=policy_change)
    df['percentage_change_coef_variation_price'] = (df['max_coef_variation_price'] - df['before_coef_variation_price']) / df['before_coef_variation_price']
    plot_with_confidence_interval('percentage_change_coef_variation_price', title='Short-Run Percentage Change in the Coefficient of Variation of Price')

    df['long_run_coef_variation_price'] = vector(dfs, 'coef_variation_price', time=49)
    df['long_run_percentage_change_coef_variation_price'] = (df['long_run_coef_variation_price'] - df['before_coef_variation_price']) / df['before_coef_variation_price']
    plot_with_confidence_interval('long_run_percentage_change_coef_variation_price', title='Long-Run Percentage Change in the Coefficient of Variation of Price')

# price level
    df['max_price'] = vector(dfs, 'price', func=max)
    df['before_price'] = vector(dfs, 'price', time=policy_change)
    df['percentage_change_price'] = (df['max_price'] - df['before_price']) / df['before_price']
    plot_with_confidence_interval('percentage_change_price', title="Short-Run Percentage Change in Price")

    df['long_run_price'] = vector(dfs, 'price', time=49)
    df['long_run_percentage_change_price'] = (df['long_run_price'] - df['before_price']) / df['before_price']
    plot_with_confidence_interval('long_run_percentage_change_price', title="Long-Run Percentage Change in Price")
# output
    df['max_output'] = vector(dfs, 'produced', func=max)
    df['before_output'] = vector(dfs, 'produced', time=policy_change)
    df['percentage_change_output'] = (df['max_output'] - df['before_output']) / df['before_output']
    graph = (ggplot(aes(x='index', y='percentage_change_output'), data=df) + geom_point() + geom_smooth() +
             ggtitle("Short-Run Percentage Change of Output") +
             ylab("Percentage Change of Output") +
             xlab("Injection of Money as a Percentage of Total Money in the Economy"))
    print(graph)
    # ggsave(graph, 'percentage_change_output.pdf' )

    df['long_run_output'] = vector(dfs, 'produced', time=49)
    df['long_run_percentage_output'] = (df['long_run_output'] - df['before_output']) / df['before_output']
    graph = (ggplot(aes(x='index', y='long_run_percentage_output'), data=df) + geom_point() + geom_smooth() +
             ggtitle("Long-Run Percentage Change in Output") +
             ylab("Percentage Change of Output") +
             xlab("Injection of Money as a Percentage of Total Money in the Economy"))
    print(graph)
    df.to_csv('systematic.csv')
