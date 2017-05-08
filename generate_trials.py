import networkx as nx
import numpy as np
import random
import pandas as pd
import datetime
import json
import time

from network_formation_game import *


# dry run
timetext = datetime.datetime.now().isoformat()
rounds = 400
start = 0
finish = 0

for trial in (1,2,3,4,5):
    for p1 in (0, 0.02, 0.05, 0.1, 0.2, 0.5, 1):
        for p2 in (0, 0.02, 0.05, 0.1, 0.2, 0.5, 1):
            p1print = 100*p1
            p2print = 100*p2
            print("Begin p1 %d / p2 %d / trial %d (%.1fs)"
                  % (p1print, p2print, trial, finish - start));

            start = time.time()
            # todo - this is named very wrong
            rows = same_graph_degree_competition(rounds, p1, p2)
            df = pd.read_json(json.dumps(rows))
            finish = time.time()

            df.to_csv('trials/t%s_p1:%d_p2%:d_rounds%d_%s.dat' %
                      (trial, p1print, p2print, rounds, 'e'))


