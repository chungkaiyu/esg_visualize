import pandas as pd
import json
from os import listdir
import os

import plotly.graph_objects as go
import plotly
import pandas as pd
import numpy as np
import math

this_dir, this_filename = os.path.split(__file__)
static_path = os.path.join(this_dir, "static")


class Sentence_Level:
    def __init__(self):
        # read all json file
        with open(static_path + '/2020_report_map.json') as f:
            self.report_dict = json.load(f)
        with open(static_path + '/industry_map.json') as f:
            self.industry_dict = json.load(f)
        with open(static_path + '/subindustry_map.json') as f:
            self.subindustry_dict = json.load(f)

    def show_report_type(self):
        print(list(self.report_dict.keys()))

    def show_industry_type(self):
        print(list(self.industry_dict.keys()))

    def show_subindustry_type(self):
        print(list(self.subindustry_dict.keys()))

    def industry_weight(self, report_type='', industry_type='', subindustry_type=''):
        # check argument
        if industry_type != '':
            try:
                report_list = set(self.report_dict[report_type]) & set(
                    self.industry_dict[industry_type])
            except:
                print('Invalid Industry Type')
        elif subindustry_type != '':
            try:
                report_list = set(self.report_dict[report_type]) & set(
                    self.industry_dict[subindustry_type])
            except:
                print('Invalid Industry Type')
        else:
            print('Not Enough Argument')

        # calcuate industry relevance
        industry_df = pd.DataFrame()
        for i in report_list:
            df = pd.read_csv(
                f'{this_dir}/../static/tmp/weight/{i}.csv', index_col=0)
            if industry_df.empty:
                industry_df = df[f'2020-{i}-{report_type}'].to_frame(name=i)
            else:
                industry_df[i] = df[f'2020-{i}-{report_type}'].values

        industry_df['mean'] = industry_df.mean(axis=1)

        return industry_df

    def plot_graph(self, company_name, data):
        use_data = data[[company_name, 'mean']]
        use_data = use_data[(use_data['mean'] > 20) & (use_data['mean'] < 500)]

        bubble_num = len(list(use_data[company_name].values))
        bubble_size = 1
        sizeref = 0.009

        # Create figure
        fig = go.Figure()

        fig.add_trace(go.Scatter(
            x=list(use_data[company_name].values), y=list(use_data['mean'].values),
            name='Key Issue', text=list(use_data.index), textposition="top center",
            marker_size=[bubble_size]*bubble_num, marker=dict(color=['#99B5EE']*bubble_num)
        ))

        # Tune marker appearance and layout
        fig.update_traces(
            mode='markers+text', marker=dict(sizemode='area', sizeref=sizeref, line_width=2))

        fig.update_layout(
            title=company_name,
            width=1000,
            height=1000,
            xaxis=dict(
                title='Importance to Company',
                gridcolor='white',
                gridwidth=1,
                categoryorder='category descending',
            ),
            yaxis=dict(
                title='Importance to Stackholder',
                gridcolor='white',
                gridwidth=1,
                categoryorder='category descending',
            ),
            paper_bgcolor='rgb(243, 243, 243)',
            plot_bgcolor='rgb(243, 243, 243)',
            title_font_size=20,
            font=dict(
                family="Times New Roman",
                size=12,
                color="black"
            )
        )

        # 序列化
        graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

        return graphJSON
