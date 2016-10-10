import numpy as np
import networkx as nx
import sympy as sym
import pandas as pd

# Problem 2-1

D = nx.DiGraph()

nodes = ['Y{0}'.format(i) for i in range(1,8)]
D.add_nodes_from(nodes)

edges = [('Y1', 'Y2', {'label': 1}),
         ('Y2', 'Y3', {'label':'G1'}),
         ('Y3', 'Y4', {'label':'G2'}),
         ('Y4', 'Y5', {'label':'G3'}),
         ('Y2', 'Y4', {'label':'G4'}),
         ('Y3', 'Y2', {'label':'H1'}),
         ('Y5', 'Y2', {'label':'H3'}),
         ('Y5', 'Y4', {'label':'H2'}),
         ('Y5', 'Y6', {'label':'G5'}),
         ('Y6', 'Y5', {'label':'H4'}),
         ('Y4', 'Y3', {'label':'H5'}),
         ('Y6', 'Y7', {'label':'G6'}),
         ('Y7', 'Y6', {'label':'H6'})
]

D.add_edges_from(edges)

loops = list(nx.simple_cycles(D))
DP = list(nx.all_simple_paths(D, 'Y1', 'Y5'))

n = 2  # group size
m = 1  # overlap size

def edge_pairs(x, group_size, overlap_size, loop=True):
    if loop:
        y = x + [x[0]]
    else:
        y = x
    return [y[i:i+group_size-overlap_size+1]
            for i in range(0,len(y), group_size - overlap_size)][:-1] #hacky

loop_edges = [[D.get_edge_data(*edge)['label'] for edge in edge_pairs(loop, 2, 1, loop=True)] for loop in loops]

path_edges = [[D.get_edge_data(*edge)['label'] for edge in edge_pairs(path, 2, 1, loop=False)] for path in DP]

gains = [j for j in [edges[i][2]['label'] for i in range(len(edges))]
 if isinstance(j, str)]

g = {symbol: sym.symbols(symbol) for symbol in gains}

for gain in g:
    if gain.startswith('H'):
        g[gain] = -1*g[gain]

loopset = pd.Series([set(loop) for loop in loops])
loopmat = loopset.apply(lambda x: [x.isdisjoint(i) for i in loopset.values]).apply(pd.Series)
loopmat.iloc[:,:] = np.triu(loopmat.values)

loopmats = []
loopmats.append(loopmat)

tuples = []
tuples.append(np.column_stack(np.where(loopmat)))

loopmat_new = loopmat

for order in range(5):
    r, c = np.where(loopmat_new)
    r = loopmat_new.index[r]
    if any([hasattr(elem, '__len__') for elem in r]):
        l1 = pd.Series([set(loopset[list(i)].apply(lambda x: list(x)).sum())
                        for i in r], index=r)
        l2 = loopset[c]
    else:
        l1, l2 = loopset[r], loopset[c]
    lu = pd.Series([l1.iloc[i].union(l2.iloc[i]) for i in range(len(l1))])
    lu.index = list(zip(l1.index, l2.index))
    loopmat_new = lu.apply(lambda x: [x.isdisjoint(i) for i in loopset.values]).apply(pd.Series)
    # TODO TRIU DOESN'T WORK
    # loopmat_new.iloc[:,:] = np.triu(loopmat_new.values)
    if loopmat_new.values.any():
        print (order + 2)
        nr, nc = np.where(loopmat_new)
        nr = loopmat_new.index[nr]
        n_ix = np.column_stack([np.array(nr.tolist()), nc])
        n_ix = np.unique(n_ix)
        loopmats.append(loopmat_new)
        tuples.append(n_ix)
    else:
        break


nontouching_loop_edges = [np.asarray(loop_edges)[tup] for tup in tuples]


LS = {}

LS[1] = -1 * sum([np.prod([g[edge] for edge in loop]) for loop in loop_edges])

g = pd.Series(g)

for order in range(len(tuples)):
    loop_order = nontouching_loop_edges[order]
    if loop_order.ndim > 1:
        LSi = sum([np.prod([g[i].product() for i in loop_order[j]]) for j in range(len(loop_order))])
    else:
        LSi = np.prod([np.prod([g[i] for i in loop_order[j]]) for j in range(len(loop_order))])
    if ((order + 2) % 2) != 0:
        LSi = -1 * LSi
    LS[order + 2] = LSi

delta = 1 + sum(LS.values())

delta_terms =[str(i) for i in delta.free_symbols]

out_expr = 0

for path in path_edges:
    S = np.prod([g[i] for i in path if isinstance(i, str)])
    drop_terms = set(path).intersection(set(delta_terms))
    Di = delta.subs([(g[i], 0) for i in drop_terms])
    expr_i = S * Di / delta
    out_expr += expr_i

sym.pprint(out_expr)
