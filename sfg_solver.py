import numpy as np
import networkx as nx
import sympy as sym
import pandas as pd

# Problem 2-1

D = nx.DiGraph()

nodes = ['Y{0}'.format(i) for i in range(1,6)]
D.add_nodes_from(nodes)

edges = [('Y1', 'Y2', {'label': 1}),
         ('Y2', 'Y3', {'label':'G1'}),
         ('Y3', 'Y4', {'label':'G2'}),
         ('Y4', 'Y5', {'label':'G3'}),
         ('Y2', 'Y4', {'label':'G4'}),
         ('Y3', 'Y2', {'label':'H1'}),
         ('Y5', 'Y2', {'label':'H3'}),
         ('Y5', 'Y4', {'label':'H2'})]

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
loopset = loopset.apply(lambda x: [x.isdisjoint(i) for i in loopset.values]).apply(pd.Series)
nontouching_ix = list(zip(*np.where(np.triu(loopset.values.astype(int)))))

nontouching_loop_edges = np.asarray(loop_edges)[nontouching_ix]


LS1 = sum([np.prod([g[edge] for edge in loop]) for loop in loop_edges])
LS2 = np.prod([np.prod([g[i] for i in nontouching_loop_edges[j]])
               for j in range(len(nontouching_loop_edges))])

delta = 1 - LS1 + LS2
delta_terms =[str(i) for i in delta.free_symbols] 

out_expr = 0

for path in path_edges:
    S = np.prod([g[i] for i in path if isinstance(i, str)])
    drop_terms = set(path).intersection(set(delta_terms))
    Di = delta.subs([(g[i], 0) for i in drop_terms])
    expr_i = S * Di / delta
    out_expr += expr_i

sym.pprint(out_expr)
