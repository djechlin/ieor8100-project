
trials_directory = 'trials/rounds400/'

import pandas as pd
import numpy as np

def  count_p1_wins(files, rounds):

    dfs = [ pd.read_csv(trials_directory + filex) for filex in files ]
    win_counts = [ df['p1WinCount'][2*rounds - 1] for df in dfs]
    return win_counts

def score_array(files, rounds):
    wins = count_p1_wins(files, rounds)
    adjusted = [np.sign(win - 400) for win in wins]
    return sum(adjusted)
