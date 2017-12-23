__author__ = 'taghawi'
import pandas as pd
import seaborn as sb
import matplotlib.pyplot as plt
from ggplot import *


def graph():
    # centralbank = pd.read_csv('aggregate_centralbank.csv').ix[20:]
    firm = pd.read_csv('aggregate_firm.csv').ix[400:600]
    hh = pd.read_csv('aggregate_household.csv').ix[400:600]

    fig, ax = plt.subplots(nrows=3, ncols=3)

    ax[0][0].set_title('money / dead (red)')
    ax2 = ax[0][0].twinx()
    sb.tsplot(data=firm['dead'], ax=ax2)
    sb.tsplot(data=firm['money'], ax=ax[0][0], color='r')

    ax[0][1].set_title('price (mean) / money (red)')
    ax2 = ax[0][1].twinx()
    sb.tsplot(data=firm['price_mean'], ax=ax2)
    sb.tsplot(data=firm['money'], ax=ax[0][1], color='r')

    ax[1][1].set_title('produced')
    ax2 = ax[1][1].twinx()
    sb.tsplot(data=firm['produced'], ax=ax2)
    sb.tsplot(data=firm['money'], ax=ax[1][1], color='r')

    ax[1][0].set_title('price_std')
    ax2 = ax[1][0].twinx()
    sb.tsplot(data=firm['price_std'], ax=ax2)
    sb.tsplot(data=firm['money'], ax=ax[1][0], color='r')

    ax[2][0].set_title('price coef of variation')
    ax2 = ax[2][0].twinx()
    sb.tsplot(data=firm['price_std'] / firm['price_mean'], ax=ax2)
    sb.tsplot(data=firm['money'], ax=ax[2][0], color='r')

    ax[2][1].set_title('inventory_change')
    ax2 = ax[2][1].twinx()
    sb.tsplot(data=firm['inventory'], ax=ax2)
    sb.tsplot(data=firm['money'], ax=ax[2][1], color='r')

    ax[0][2].set_title('household money / firm money')
    ax2 = ax[0][2].twinx()
    sb.tsplot(data=hh['money'], ax=ax2)
    sb.tsplot(data=firm['money'], ax=ax[0][2], color='r')

    ax[1][2].set_title('firm rationing / firm money')
    ax2 = ax[1][2].twinx()
    sb.tsplot(data=firm['rationing_mean'], ax=ax2)
    sb.tsplot(data=firm['money'], ax=ax[1][2], color='r')

    ax[2][2].set_title('hh rationing / firm money')
    ax2 = ax[2][2].twinx()
    sb.tsplot(data=hh['rationing_mean'], ax=ax2)
    sb.tsplot(data=firm['money'], ax=ax[2][2], color='r')


    try:
        firm = pd.read_csv('panel_firm.csv')[200:]
        print(ggplot(aes('round', 'price'), data=firm[firm['id'] < 100]) + geom_line() + facet_wrap('id'))
        print(ggplot(aes('round', 'price'), data=firm[firm['id'] > 100]) + geom_line() + facet_wrap('id'))
    except IOError:
        pass

    try:
        sb.plt.savefig('/Users/taghawi/Desktop/foo.png', bbox_inches='tight', dpi=300)
    except IOError:
        pass
    try:
        sb.plt.savefig('/home/taghawi/Desktop/foo.png', bbox_inches='tight', dpi=300)
    except IOError:
        pass
    sb.plt.show()

if __name__ == '__main__':
    graph()
