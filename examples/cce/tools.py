def transform(sp):
    ret = {}
    ret['tax_change_time'] = sp['tax_change_time']
    ret['tax'] = {}
    for key, value in sp.items():
        if key.startswith('tax_'):
            ret['tax'][key[4:]] = value
        else:
            ret[key] = value
    return ret
