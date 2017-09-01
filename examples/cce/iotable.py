import pandas as pd
import numpy as np



def to_iotable(name, rounds=None):
    pd.set_option('expand_frame_repr', False)
    pd.set_option('precision', 3)
    pd.set_option('display.float_format', lambda x: '%.3f' % x)
    df = pd.read_csv(name + '/trade___trade.csv')
    if rounds is None:
        rounds = [max(df['round'])]
    q = []
    p = []
    for round in rounds:
        table = df[df['round'] == round]
        table.drop(['round', 'index'], axis=1, inplace=True)
        grouped_table = table.groupby(['seller', 'buyer'])
        quantities = grouped_table.sum()['quantity']
        prices = grouped_table.mean()['price']
        value = quantities * prices
        quantities = quantities.unstack()
        quantities = quantities.reindex_axis(['col', 'ele', 'gas', 'o_g', 'oil', 'eis', 'trn', 'roe', 'lab', 'cap', 'government', 'household', 'inv', 'netexport'], axis=1)
        quantities = quantities.reindex_axis(['col', 'ele', 'gas', 'o_g', 'oil', 'eis', 'trn', 'roe', 'lab', 'cap', 'government', 'household', 'inv', 'netexport'], axis=0)
        quantities = quantities.replace(np.NaN, 0)
        quantities['netexport'] = quantities['netexport'] - quantities.ix['netexport']
        quantities['sum'] = sum([quantities[name] for name in quantities.columns])
        quantities.ix['sum'] = sum([quantities.ix[name] for name in quantities.T.columns])
        prices = prices.unstack()
        prices = prices.reindex_axis(['col', 'ele', 'gas', 'o_g', 'oil', 'eis', 'trn', 'roe', 'lab', 'cap', 'government', 'household', 'inv', 'netexport'], axis=0)
        prices = prices.reindex_axis(['col', 'ele', 'gas', 'o_g', 'oil', 'eis', 'trn', 'roe', 'lab', 'cap', 'government', 'household', 'inv', 'netexport'], axis=1)
        prices = prices.replace(np.NaN, 0)

        table['value'] = table['quantity'] * table['price']
        #vtable.drop(['round', 'index'], axis=1, inplace=True)
        vgrouped_table = table.groupby(['seller', 'buyer'])
        values = vgrouped_table.sum()['value']
        values = values.unstack()
        values = values.reindex_axis(['col', 'ele', 'gas', 'o_g', 'oil', 'eis', 'trn', 'roe', 'lab', 'cap', 'government', 'household', 'inv', 'netexport'], axis=1)
        values = values.reindex_axis(['col', 'ele', 'gas', 'o_g', 'oil', 'eis', 'trn', 'roe', 'lab', 'cap', 'government', 'household', 'inv', 'netexport'], axis=0)
        values = values.replace(np.NaN, 0)
        print('***\tvalues\t***')
        print(values)
        print('***\tprice\t***')
        print(prices)
        p.append(prices)
        print('***\tquantities\t***')
        print(quantities)
        q.append(quantities)
        print('***\trelative\t***')
        print
    pd.set_option('display.float_format', lambda x: '%.1f' % (x * 100))
    print('p')
    print(p[1] / p[0] - 1)
    print('q')
    print(q[1] / q[0] - 1)
    return value


def average_price(name, round=99):
    pd.set_option('display.float_format', lambda x: '%.25f' % x)
    df = pd.read_csv(name + '/trade___trade.csv')
    table = df[df['round'] == round]
    table.drop(['round', 'index'], axis=1, inplace=True)
    grouped_table = table.groupby(['seller', 'buyer'])
    prices = grouped_table.mean()['price']
    prices = prices.unstack()
    prices = prices.replace(0, np.NaN)
    mean = prices.mean()
    mean = mean.mean()
    return mean






if __name__ == '__main__':
    value = to_iotable('./result/cce_2016-01-04_11-30')
