import os
import json
import pandas as pd
from ggplot import *
import statsmodels.formula.api as sm
from statsmodels.sandbox.regression.predstd import wls_prediction_std
import cPickle as pickle


def read_series(throw_away, exclude=[]):
    dfs = []
    series = 0
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

            data = pd.read_csv(directory + '/aggregate_household.csv')[throw_away:]
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
    with open('cache_systematic_household_graphs.json', 'rb') as jfile:
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

def plot_with_confidence_interval(variable, title, ylim=None):
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
    if ylim is not None:
        graph += ylim
    print(graph)
    ggsave(plot=graph, filename=variable + ".pdf")
    ggsave(plot=graph, filename=variable + ".png")


if __name__ == '__main__':
    throw_away = 1
    policy_change = 10 + throw_away
    dfs = read_series(throw_away, exclude=[10])
    # dfs = load_series()
    dfs = dfs[:int(len(dfs) / 51) * 51]

    print('num simulations', len(dfs))

    df = pd.DataFrame()
    df['index'] = vector(dfs, 'utitily', index=True)
    df['series'] = vector(dfs, 'utitily', color=True)
    df['index2'] = df['index'] ** 2

# coef_variation_price
    df['max_utility'] = vector(dfs, 'utility', func=max)
    df['before_utility'] = vector(dfs, 'utility', time=policy_change)
    df['percentage_change_utility'] = (df['max_utility'] - df['before_utility']) / df['before_utility']
    plot_with_confidence_interval('percentage_change_utility', title='Short-Run Percentage Change in Utility')

    df['long_run_utility'] = vector(dfs, 'utility', time=49)
    df['long_run_percentage_change_utility'] = (df['long_run_utility'] - df['before_utility']) / df['before_utility']
    plot_with_confidence_interval('long_run_percentage_change_utility', title='Long-Run Percentage Change in Utility',
                                  ylim=scale_y_continuous(limits=(-0.02, 0.08),
                                                          breaks=[-0.02, 0, 0.02, 0.04, 0.06, 0.08],
                                                          labels=(-0.02, 0, 0.02, 0.04, 0.06, 0.08)))

    df.to_csv('systematic_utility.csv')
