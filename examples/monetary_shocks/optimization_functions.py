from scipy.optimize import minimize
from numba import jit


# on the next cython update try cdef double F(..)
@jit
def F(xx, prices_non_labor, wage, gamma, one_by_gamma, l, one_minus_l):
    price_labor = xx[-1]

    summation = ((xx[:-1] / prices_non_labor) ** gamma).sum()

    non_labor = summation ** one_by_gamma
    labor = price_labor / wage
    # labor and non-labor inputs together
    value = (labor ** l) * (non_labor ** one_minus_l)
    value = value / 1000000000
    return - float(value)


def optimization(seed_weights,
                 input_prices,
                 wage,
                 gamma,
                 one_by_gamma,
                 l,
                 one_minus_l):

    args = (input_prices,
            wage,
            gamma,
            one_by_gamma,
            l,
            one_minus_l)

    cons = ({'type': 'eq', 'fun': lambda x: 1 - x.sum()})
    bnds = [(0, 1) for _ in range(len(seed_weights))]

    return minimize(F, seed_weights, args=args, constraints=cons, bounds=bnds, method='SLSQP',
                    options={'maxiter': 100000})
