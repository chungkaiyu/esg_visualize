import pandas as pd
import numpy as np

import plotly.graph_objects as go
import plotly.express as px
import math


class Chart:
    def __init__(self):
        self.p_color = {'Environment':'#99EEC1', 'Social':'#99B5EE', 'Governance':'#EE9F99'}

    def set_pillar_color(self,color_dict:dict):
        self.p_color = color_dict

    def trend(self, data:dict, x='year', y='Percentage', size='Weight', show_num=3, sort_name='Percentage'):

        df = pd.DataFrame()

        for name, year in data.items():
            tmp = pd.read_csv(name)
            tmp['year']=year
            tmp = tmp.sort_values(sort_name,ascending=False).groupby('Pillar').head(show_num)
            df = pd.concat([df,tmp],axis=0,ignore_index=True)


        sizeref = 2.*max(tmp[size])/(100**2)

        # Dictionary with dataframes for each category
        category_names = list(df['Pillar'].unique())
        category_data = {category:df.query("Pillar == '%s'" %category) for category in category_names}

        # Create figure
        fig = go.Figure()

        for category_name, category in category_data.items(): 
            fig.add_trace(go.Scatter(
                x=category[x], y=category[y],
                name=category_name, text=category['Key_issue'],
                marker_size=category[size],marker=dict(color=[self.p_color[category_name]]*show_num*3)
                ))

        # Tune marker appearance and layout
        # fig.update_traces(mode='markers', marker=dict(sizemode='area',sizeref=sizeref, line_width=2))
        fig.update_traces(mode='markers+text', marker=dict(sizemode='area',sizeref=sizeref,line_width=2))

        fig.update_layout(
            title='Apply 2018-2020 trend',
            xaxis=dict(
                title=x,
                gridcolor='white',
                type='category',
                gridwidth=2,
                categoryarray=list(data.values()),
        #         tickformat=".0%",
                
            ),
            yaxis=dict(
                title=y,
                gridcolor='white',
                gridwidth=2,
                categoryorder='category descending',
            ),
            paper_bgcolor='rgb(243, 243, 243)',
            plot_bgcolor='rgb(243, 243, 243)',
            legend=dict(
                itemsizing="constant",
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            ),
        )
        
        fig.show()