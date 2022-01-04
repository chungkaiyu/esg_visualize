import pandas as pd
import numpy as np
import random

import plotly.io as pio
import plotly.graph_objects as go
import math


class Chart:
    def __init__(self):
        self.p_color = {'Environment': '#99EEC1',
                        'Social': '#99B5EE', 'Governance': '#EE9F99'}

    def set_pillar_color(self, color_dict: dict):
        self.p_color = color_dict

    def trend(self, data: dict, x='year', y='Percentage', size='Weight', title='Trend', show_num=3, sort_name='Percentage', weite_img=False, output_path='', show_chart=True):

        df = pd.DataFrame()

        for name, year in data.items():
            tmp = pd.read_csv(name)
            tmp['year'] = year
            tmp = tmp.sort_values(sort_name, ascending=False).groupby(
                'Pillar').head(show_num)
            df = pd.concat([df, tmp], axis=0, ignore_index=True)

        randlist = []
        for i in range(len(df['year'])):
            randlist.append(random.uniform(-0.3, 0.3))
        df['year'] = df['year']+randlist

        sizeref = 2.*max(df[size])/(100**2)

        # Dictionary with dataframes for each category
        category_names = list(df['Pillar'].unique())
        category_data = {category: df.query(
            "Pillar == '%s'" % category) for category in category_names}

        # Create figure
        fig = go.Figure()

        for category_name, category in category_data.items():
            fig.add_trace(go.Scatter(
                x=category[x], y=category[y],
                name=category_name, text=category['Key_issue'],
                marker_size=category[size], marker=dict(
                    color=[self.p_color[category_name]]*show_num*3)
            ))

        # Tune marker appearance and layout
        # fig.update_traces(mode='markers', marker=dict(sizemode='area',sizeref=sizeref, line_width=2))
        fig.update_traces(
            mode='markers+text', marker=dict(sizemode='area', sizeref=sizeref, line_width=2))

        x_categoryarray = list(data.values())
        x_categoryarray.sort()

        fig.update_layout(
            title=title,
            xaxis=dict(
                title=x,
                gridcolor='white',
                type='-',
                gridwidth=2,
                dtick=1,
                categoryorder='category descending',
                tickformat=',d',

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

        if weite_img:
            width_in_mm = 600
            width_default_px = 1450
            height_default_px = 525
            dpi = 300
            scale = (width_in_mm / 25.4) / (width_default_px / dpi)
            pio.write_image(fig, output_path+title+".png", width=width_default_px,
                            height=height_default_px, scale=scale, engine="kaleido")

        if show_chart:
            fig.show()
