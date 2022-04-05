
import pandas as pd
import stumpy
import matplotlib.pyplot as plt
import pandas_flavor as pf
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np


@pf.register_dataframe_accessor('stumpy')
class PandasStumpy():
    def __init__(self, df):
        self._df = df
        self.window = None
        self.mp = None #matrix profile array
        self.ts_column = None

    def stump(self, ts_column:str, window=None):
        """
        applies the matrix profile technique, using window on the time-series column"""
        
        df = self._df
        self.ts_column = ts_column
        
        if isinstance(self.window, type(None)):
            self.window = window
       #perform matrix profile
        mp = stumpy.stump(df[ts_column], self.window)
        self.mp = mp 
        return self._df

    def motifs(self, **kwargs):
        '''Finds all motifs based on the stumpy motifs function
        Returns distances and indicies'''

        if isinstance(self.mp, type(None)):
            print('Run stump first to generate matrix profile')
        else:
            df = self._df

            self.motif_distances, self.motif_indicies = stumpy.motifs(df[self.ts_column], self.mp[:,0], **kwargs)

        return self._df

    def plot(self):
        self.fig = make_subplots(rows=2, cols=1, shared_xaxes=True, subplot_titles=("Data", "Matrix Profile Distances"))
        self.fig.add_trace(
            go.Scatter(x=self._df.index, y = self._df[self.ts_column]),
            row=1, col=1
        )
        self.fig.add_trace(
            go.Scatter(x=self._df.index, y = self.mp[:,0]),
            row=2,
            col=1
        )
        self.fig.update_layout(showlegend=False)
        self.fig.show()

    def _get_dataframe_index(self, n):
        '''sometimes dataframe indicies are not integers, they may be timestamps
        This returns the index value, needed if plotting where x axis is a time'''

        return self._df.index[n]
    
    def _get_anomaly_index(self, n):
        '''returns the  index of the n-th anomaly'''
        #need to add 1 to n as counts from 1 from back of array
        n += 1
        return np.argsort(self.mp[:,0])[-n]
        

    def _get_motif_index(self, n):
        '''returns the intger index of the n-th motif'''

    def _add_vrectangle(self, x0, **kwargs):
        '''adds a vertical rectangle to the plotly figure'''

        x0_new = self._get_dataframe_index(x0)
        x1 = self._get_dataframe_index(x0 + self.window)

        self.fig.add_vrect(x0 = x0_new, x1 = x1, **kwargs)

    def _add_vline(self, x0, **kwargs):
        '''adds a vertical line to the chart'''
        x0 = self._get_dataframe_index(x0)

        self.fig.add_vline(x=x0, **kwargs)

    def add_anomaly(self, n:int):
        '''Adds n anomalies to the plot'''

        for i in range(n):
            x0 = self._get_anomaly_index(i)
            self._add_vrectangle(x0,
            fillcolor='red',
            opacity=0.25,
            annotation_text = 'a ' + str(i+1),
            row=1,
            line_width=0)
            self._add_vline(x0, line={'dash':'dot'}, row=2)

        self.fig.show()

    def add_motifs(self, n:int):
        'adds n motifs to the plot'

        if n > len(self.motif_indicies[0]):
            print('n is bigger than the number of motifs, reducing it')
            n = len(self.motif_distances[0])-1

        for i in range(n):
            x0 = self.motif_indicies[0][i]
            self._add_vrectangle(x0,
                    fillcolor='green',
                    opacity=0.25,
                    annotation_text = 'm ' + str(i+1),
                    row=1,
                    line_width=0)
            self._add_vline(x0, line={'dash':'dash'}, row=2)

        self.fig.show()