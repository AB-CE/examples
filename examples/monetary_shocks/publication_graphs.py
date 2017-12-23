__author__ = 'taghawi'
import pandas as pd
import seaborn as sb
import matplotlib.pyplot as plt
from ggplot import *
import numpy as np
from os import chdir
import os

directory = './result'
all_subdirs = [os.path.join(directory, name)
               for name in os.listdir(directory)
               if os.path.isdir(os.path.join(directory, name))]

files = dict(zip(all_subdirs, all_subdirs))

def graph(name, show):
    # centralbank = pd.read_csv('aggregate_centralbank.csv').ix[20:]
    firm = pd.read_csv('aggregate_firm.csv').ix[100:300]

    fig, ax = plt.subplots(nrows=3)
    fig.set_size_inches(18.5, 10.5)
    fig.suptitle(name, fontsize=20)
    for x in range(len(ax)):
        ax[x].get_xaxis().get_major_formatter().set_useOffset(False)
        ax[x].get_xaxis().get_major_formatter().set_scientific(False)

        ax[x].get_yaxis().get_major_formatter().set_useOffset(False)
        ax[x].get_yaxis().get_major_formatter().set_scientific(False)

    ax[0].set_title('Price Level')
    sb.tsplot(data=firm['price_mean'], ax=ax[0])

    ax[1].set_title('Output')
    sb.tsplot(data=firm['produced'], ax=ax[1])

    ax[2].set_title('Coefficient of Variation - Price')
    sb.tsplot(data=firm['price_std'] / firm['price_mean'], ax=ax[2])

    try:
        sb.plt.savefig('../%s.png' % name, bbox_inches='tight', dpi=150)
    except IOError:
        pass
    try:
        sb.plt.savefig('../%s.png' % name, bbox_inches='tight', dpi=150)
    except IOError:
        pass
    if show:
        sb.plt.show()

def bins(name, show):
    firms = pd.read_csv('panel_firm.csv').ix[100:]
    agg = pd.read_csv('aggregate_firm.csv').ix[100:]
    agg['cof'] = agg['price_std'] / agg['price_mean']
    agg['cof'] = agg['price_std'] / agg['price_mean']
    bin_before_n = 99
    bin_after_n = np.argmax(agg['cof'])

    bin_before = firms[firms['round'] == bin_before_n]
    bin_after = firms[firms['round'] == bin_after_n]

    bin_before = np.array(bin_before['price'].tolist())
    bin_after = np.array(bin_after['price'].tolist())

    bin = bin_after - bin_before

    bin = pd.DataFrame(bin)

    plt = ggplot(bin, aes(0)) + stat_bin() + ggtitle(name)
    if show:
        print(plt)
    ggsave(filename='../bin_%s.png' % name, plot=plt, dpi=150)

if __name__ == '__main__':
    show = True

    for directory, name in files.iteritems():
        chdir(directory)
        print(directory)
        graph(name, show)
        # bins(name, show)
        chdir('../..')
