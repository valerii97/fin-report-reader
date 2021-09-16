from random import randint

import plotly.graph_objects as go
from dash.dependencies import Input, Output, State
import pandas as pd
import numpy as np 
from flask_security import current_user
from flask import url_for

from .models import export_report_data, export_filenames


# for creating graph for one var
def func_for_graph1(x, df, yaxis_name, val):
    sales = df[df.columns[0]]
    epxpences = df[df.columns[1]]
    profits = df[df.columns[2]]
    margins = []
    for item in zip(profits, sales):
        if item[1] != 0:
            margins.append(round((item[0]/item[1]*100), 0))
        else:
            margins.append(0)
    
    if val and 'figs' in val:
        fig = go.Figure(data=[
        go.Bar(name=df.columns[0], x=x, y=df[df.columns[0]], text=['{}'.format(int(sale)) for sale in sales], textposition='outside'),
        go.Bar(name=df.columns[1], x=x, y=df[df.columns[1]], text=['{}'.format(int(expence)) for expence in epxpences], textposition='outside'), 
        go.Bar(name=df.columns[2], x=x, y=df[df.columns[2]], text=['{}/{}'.format(int(profits[i]), int(margins[i])) for i in range(len(margins))], textposition='outside')
        ])
    else:
        fig = go.Figure(data=[
        go.Bar(name=df.columns[0], x=x, y=df[df.columns[0]]),
        go.Bar(name=df.columns[1], x=x, y=df[df.columns[1]]), 
        go.Bar(name=df.columns[2], x=x, y=df[df.columns[2]])
        ])
    
    fig.update_layout(barmode='group',
            transition_duration=200,
            height=800,
            yaxis=dict(
                title=yaxis_name,
                titlefont_size=16,
                tickfont_size=14,
    ),paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',font_color='#7FDBFF',
            font_size=14, legend=dict(
            orientation="h",
            y=1.1, yanchor='top', x=0.5))
    
    return fig


def register_callbacks(app):
    # loading filenames to choose file
    @app.callback(Output('files', 'options'),
    Output('files', 'value'),
    Output('prof-link', 'href'),
    Output('logout', 'href'),
    Input('load-files', 'n_clicks'))
    def load_filename(clicks):
        if clicks > 0:
            user_id = current_user.get_id()
            filenames = export_filenames(user_id)
            # creating options for filename dropdown
            if filenames:
                options = []
                for filename in filenames:
                    dicitonary = {'label':filename, 'value':filename}
                    options.append(dicitonary)
                value = options[0]['value']
            else:
                options = []
                value = None
            href = url_for('profile.profile', user_id=user_id)
            href_logout = url_for('security.logout')
            return options, value, href, href_logout
        return [], None, '#', '#'

    # loading list of managers to choose manager
    @app.callback(Output('managers', 'options'),
    Output('managers', 'value'),
    Input('submit_value', 'n_clicks'),
    Input('files', 'value'))
    def load_data(clicks, filename):
        user_id = current_user.get_id()
        if clicks > 0:
            if filename:
                df = export_report_data(filename, user_id).data             
                # creating list of managers
                managers = list(df['Manager'].unique())
                # creating options for manager dropdown
                options = []
                for manager in managers:
                    dicitonary = {'label':manager, 'value':manager}
                    options.append(dicitonary)
                value = options[0]['value']
                return options, value
        return [], None
    
    # building graphs
    @app.callback(Output('man_graph', 'figure'),
    Output('man_graph', 'style'),
    Input('managers', 'value'),
    Input('files', 'value'),
    Input('fig_check', 'value'))
    def create_graph(manager_name, filename, figs):
        user_id = current_user.get_id()
        if manager_name and filename:
            df = export_report_data(filename, user_id).data
            # grouping by managers
            by_manager = df.groupby(df['Manager'])
            # dataframe to choose clients by manager
            newData2 = df.loc[by_manager.groups[manager_name]][df.columns[2:6]]
            newData2_indexes = list(newData2['Client'])
            newData2 = newData2[newData2.columns[1:]]
            newData2.index = newData2_indexes

            fig = func_for_graph1(newData2.index, newData2, 'USD, $', figs)
            style = {'height':'{}px'.format(randint(750,800))}
            return fig, style
        else:
            default_value_graph = { 'data': [], 'layout': {}, 'frames': [], }
            return default_value_graph, {'height':'800px'}