import json
import random
import sys

LINE_LENGTH_MIN = 1
LINE_LENGTH_MAX = 7
POINTS_MIN = 20
POINTS_MAX = 200
ARGS = sys.argv

def generateGraph(name, idx):
    length = random.randint(POINTS_MIN, POINTS_MAX)
    points = [{'idx': i+1, 'post_idx': None} for i in range(length)]
    lines = []
    line_idx = 1
    sparsity = int(length*2/3)
    for i in range(length):
        for j in range(i+1, length):
            if(random.randint(1, sparsity) == 1):
                two_points = [i+1, j+1]
                line = {
                    'idx': line_idx,
                    'length': random.randint(LINE_LENGTH_MIN, LINE_LENGTH_MAX),
                    'points': two_points}
                lines.append(line)
                line_idx += 1
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
