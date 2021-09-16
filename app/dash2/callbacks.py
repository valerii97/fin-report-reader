import plotly.graph_objects as go
from dash.dependencies import Input, Output, State
import pandas as pd
import numpy as np 
from flask_security import current_user
from flask import url_for

from .models import export_report_data, export_filenames


# creating graph for pie
def graph_pie(labels, values, name, val=False):
    fig = go.Figure(data=[go.Pie(labels=labels, values=values)])

    if val and 'figs' in val:
        fig.update_traces(hole=.6, hoverinfo="label+percent+name", textinfo="value", textfont_size=12)
    else:
        fig.update_traces(hole=.6, hoverinfo="label+percent+name+value")
    
    fig.update_layout(annotations=[dict(text=name, x=0.5, y=0.5, font_size=20, showarrow=False)],
    legend=dict(
            orientation="v",
            x=-0.2),paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',font_color='#7FDBFF',
            font_size=12)
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
    @app.callback(
    Output('cat', 'options'),
    Output('cat', 'value'),
    Input('submit_value', 'n_clicks'),
    Input('files', 'value'))
    def load_data(clicks, filename):
        user_id = current_user.get_id()
        if clicks > 0:
            if filename:
                df = export_report_data(filename, user_id).data             
                cats = df.columns[3:6]
                opts_cat = []
                for cat in cats:
                    dicitonary = {'label':cat, 'value':cat}
                    opts_cat.append(dicitonary)
                val_cat = opts_cat[0]['value']
                return opts_cat, val_cat
        return [], None
    
    # building graphs
    @app.callback(
    Output('pie_graph', 'figure'),
    Input('files', 'value'), 
    Input('cat', 'value'),
    Input('fig_check', 'value'))
    def create_graph(filename, val_cat, pie_value):
        user_id = current_user.get_id()
        if filename:
            df = export_report_data(filename, user_id).data
            # grouping by managers
            by_manager = df.groupby(df['Manager'])

            managers = list(df['Manager'].unique())
            man_dict = {}
            for manager in managers:
                man_dict[manager] = df.loc[by_manager.groups[manager]][df.columns[3:6]].sum()
            newData = pd.DataFrame(man_dict)
            newData = newData.drop([newData.columns[-1]], axis=1)
            newData = newData.T
            fig2 = graph_pie(newData.index, newData[val_cat], val_cat, pie_value)

            return fig2
        else:
            default_value_graph = { 'data': [], 'layout': {}, 'frames': [], }
            return default_value_graph