import pandas as pd
import stumpy
import matplotlib.pyplot as plt
import pandas_flavor as pf
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np


@pf.register_dataframe_method
def stump(df, window, ts_column):
    mp = stumpy.stump(df[ts_column], window)
    df_mp = pd.DataFrame(mp, index = df.iloc[0:-window+1].index, columns=['score','index','left_index','right_index'])
    df_mp = df_mp.add_prefix('stump_')
    df = df.join(df_mp)
    return df

def add_rectangles(df, fig, x, window, **kwargs):
    """runs the vrect function to create rectangles on a plotly express figure from x to x + window and
    if x is a list, then it loops through it, otherwise x should be an integer position of the index
    
    It also adds a dashed vertical line on the subplot of the matrix profile score"""
    
    def get_x1(idx):
        if idx + window > len(df) -1:
            return len(df) - 1
        else:
            return idx + window

    def add_rectangle(x, window, **kwargs):
        fig.add_vrect(x0 = df.index[x], x1 = df.index[get_x1(x)], **kwargs)

    def add_line(x, **kwargs):
        fig.add_vline(x=df.index[x], **kwargs)
    
    if type(x) == list:
        for idx in x:
            add_rectangle(idx, window, **kwargs)
            add_line(idx, line={'dash': 'dash'}, row=2)
    else:
        add_rectangle(x, window, **kwargs)
        add_line(x, line={'dash': 'dash'}, row=2)
        
@pf.register_dataframe_method
def stump_plot(df, window, ts_column, stump_score='stump_score'):
    
    motif_idx = np.argsort(df[stump_score])[0] #minimum value
    nearest_neighbour_index = df.iloc[motif_idx, df.columns.get_loc('stump_index')]

    anomaly_idx = np.argsort(df[stump_score].dropna()).iloc[-1]
    
    fig = make_subplots(rows=2, cols=1, shared_xaxes=True, subplot_titles=("Data", "Matrix Profile"))

    fig.add_trace(
        go.Scatter(x=df.index, y=df[ts_column]),
        row=1, col=1)

    fig.add_trace(
        go.Scatter(x=df.index, y=df[stump_score], name='score'),
        row=2,
        col=1)

    add_rectangles(df, fig,  [motif_idx, nearest_neighbour_index], window, fillcolor='green', opacity=0.25, line_width=0,
                annotation_text = 'motif', row=1)

    add_rectangles(df, fig, anomaly_idx, window, fillcolor='red', opacity=0.20, line_width=0, annotation_text = 'anomaly', row=1)

    fig.update_layout(showlegend=False)

    fig.show()
    return df
#get example data
