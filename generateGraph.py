import json
import random
import sys
import networkx as nx
LINE_LENGTH_MIN = 1
LINE_LENGTH_MAX = 7
ARGS = sys.argv


def generateGraph(name, idx):
    G=nx.connected_watts_strogatz_graph(25, 3, 5)
    edges= nx.edges(G)
    lines=[]
    i=1
    for edge in edges:
        line = {
            'idx': i,
            'length': random.randint(LINE_LENGTH_MIN, LINE_LENGTH_MAX),
            'points': edge }
        lines.append(line)
        i+=1
    n = nx.number_of_nodes(G) -1
    points = [{'idx': i+1, 'post_idx': None} for i in range(n)]
    graph = {
        'name': name,
        'points': points,
        'lines': lines,
        'idx': idx
    }
    with open('generatedGraphs/%s.json' % name, 'w') as outfile:
        json.dump(graph, outfile)


if(len(ARGS) == 3):
    generateGraph(ARGS[1], ARGS[2])
elif(len(ARGS) == 2):
    generateGraph(ARGS[1], 1)
elif(len(ARGS) == 1):
    generateGraph('first', 1)
