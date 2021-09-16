import base64
import datetime
import io

import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.express as px
import plotly.graph_objects as go
from dash.dependencies import Input, Output, State
import pandas as pd
import numpy as np
from flask_security import current_user
from flask import url_for

from .models import add_report_data, export_report_data, export_filenames


# for adding items to Dropdowns
def change_options(opts):
    options = []
    for opt in opts:
        dictionary = {'label': opt, 'value': opt}
        options.append(dictionary)
    return options


# adding items to subdivision dropdown
def change_options_man(df):
    options = []
    cols = list(df.columns)
    cols.remove(cols[0])
    for col in cols:
        if df[col].sum() != 0:
            dictionary = {'label': col, 'value': col}
            options.append(dictionary)
    return options


# preprocess data for pie diagram
def for_graph_pie1(df, value):
    labels = []
    values = []
    cols = df.columns
    for col in cols:
        if value in col and 'incl.' not in col:
            labels.append(col)
            sum_col = df[col].sum()
            values.append(sum_col)
    return labels, values


# for creating graph for one var
def func_for_graph1(name, x, y, yaxis_name, val):
    fig = go.Figure(go.Bar(name=name, x=x, y=y))
    fig.update_layout(barmode='group',
                    transition_duration=200,
                    yaxis=dict(
                        title=yaxis_name,
                        titlefont_size=16,
                        tickfont_size=14,
                    ), paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)', font_color='#7FDBFF',
                    font_size=14, title='Graph for 1 year')
    if val and 'hide' in val:
        fig.update_yaxes(visible=False, showticklabels=False)
    return fig


# for creating graph for 2 vars
def func_for_graph2(name1, name2, x, y1, y2, yaxis_name, val):
    # for adding percentage to compare items from 2 years
    dif_ = []
    for i in range(len(x)):
        if y1[i] != 0:
            dif = round(((y1[i]-y2[i])/max(y1[i], y2[i]))*100, 1)
            dif_.append(dif)
        else:
            dif_.append(100.0)
    lbls = []
    for d in dif_:
        lbls.append('{}%'.format(d))

    if val and 'show' in val:
        fig = go.Figure([
            go.Bar(name=name1, x=x, y=y1, hovertext=lbls, text=lbls,
                textposition='inside', textfont={'size': 9}),
            go.Bar(name=name2, x=x, y=y2)])
    else:
        fig = go.Figure([
            go.Bar(name=name1, x=x, y=y1, hovertext=dif_, text=y1),
            go.Bar(name=name2, x=x, y=y2)])
    
    fig.update_layout(barmode='group',
                    transition_duration=200,
                    yaxis=dict(
                        title=yaxis_name,
                        titlefont_size=16,
                        tickfont_size=14,),
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    font_color='#7FDBFF',
                    font_size=14, title='Comparing bars',
                    legend=dict(
                        orientation="h",
                        y=1.1, yanchor='top',
                        x=0.5))
    if val and 'hide' in val:
        fig.update_yaxes(visible=False, showticklabels=False)
    return fig


# creating graph for pie
def graph_pie(labels, values, name):
    fig = go.Figure(data=[go.Pie(labels=labels, values=values)])
    fig.update_traces(hole=.6, hoverinfo="label+percent+value+name")
    fig.update_layout(annotations=[dict(text=name, x=0.5, y=0.5, font_size=20, showarrow=False)],
                    legend=dict(
        orientation="h",
        x=-0.2), paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)', font_color='#7FDBFF',
        font_size=12, title='Pie graph for 1 year')
    return fig


# creating func to compare years
def func_for_comparing(x, y1, y2, yaxis_name, val):
    dif_ = []
    for i in range(len(x)):
        if y1[i] != 0:
            dif = round(((y1[i]-y2[i])/max(y1[i], y2[i]))*100, 1)
            dif_.append(dif)
        else:
            dif_.append(100.0)
    lbls = []
    for d in dif_:
        lbls.append('{}%'.format(d))

    if val and 'show' in val:
        fig = go.Figure(go.Bar(
            x=x,
            y=dif_,
            text=lbls,
            textposition='auto'
        ))
    else:
        fig = go.Figure(go.Bar(
            x=x,
            y=dif_
        ))
    fig.update_layout(transition_duration=200,
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    font_color='#7FDBFF', font_size=14, title='Comparing diagramm',
                    yaxis=dict(
                        title=yaxis_name,
                        titlefont_size=16,
                        tickfont_size=14,
                    ))

    return fig


# function for changing break-even states
def br_even_state_drop(value):
    if value == 'FRW':
        br_arr = ['Revenue - Forwarding',
                'Op. Exp. - Forwarding', 'Units - Forwarding']
    elif value == 'TRK':
        br_arr = ['Revenue - Trucking (brokerage)',
                'Op. Exp. - Trucking (brokerage)', 'Units - Trucking']
    elif value == 'AIR':
        br_arr = ['Revenue - Air', 'Op. Exp. - Air', 'Units - Air']
    elif value == 'TTL':
        br_arr = ['Total Revenue', 'Total Operating expenses', 'Units - Forwarding', 'Units - Liner',
       'Units - Trucking', 'Units - Air', 'Units - Other']
    else:
        br_arr = []
    return br_arr


# creating func to calculate breakeven
def breakeven_calc(df, month, arr, range_slider):
    # vars for calculation
    revenue = df.loc[df.index[month]][arr[0]]
    tot_expences = df.loc[df.index[month]][arr[1]]
    ind_expences = df.loc[df.index[month]]['Total indirect expenses']
    if len(arr) == 3:
        units = df.loc[df.index[month]][arr[2]]
    else:
        if 'Units - Air' in df.columns:
            units = df.loc[df.index[month]][arr[2:]].sum()
        else:
            arr.remove('Units - Air')
            units = df.loc[df.index[month]][arr[2:]].sum()
    min_x_val = range_slider[0]
    max_x_val = range_slider[1]
    # print('Revenue: {}, Expences: {}, Units: {}'.format(revenue, tot_expences, units))
    # calculation
    x = np.linspace(min_x_val, max_x_val, num=1000)
    exp = ind_expences + tot_expences/units * x
    sales = revenue/units * x
    # ===============================
    # break even point calculation
    br_arr = []
    sl_br_arr = []
    br_even_point = round((ind_expences/(revenue/units - tot_expences/units)))
    br_arr.append(br_even_point)
    sales_br_even_point = revenue/units * br_even_point
    sl_br_arr.append(sales_br_even_point)
    # ===============================
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=x, y=sales, name='Revenue'))
    fig.add_trace(go.Scatter(x=x, y=exp, name='Expences'))
    fig.add_trace(go.Scatter(mode='markers+text', 
    marker_symbol='x',
    marker_size=14,
    text=[br_arr[0]],
    textposition="bottom center", 
    x=br_arr, 
    y=sl_br_arr, 
    name='Break Event Point'))
    fig.update_layout(transition_duration=200,
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='#05050f',
                    font_color='#7FDBFF', font_size=14, title='Break-Even',
                    yaxis=dict(
                        title='USD, $',
                        titlefont_size=16,
                        tickfont_size=14,
                    ), xaxis=dict(
                        title='Units',
                        titlefont_size=16,
                        tickfont_size=14,
                    ))
    return fig


def register_callbacks(app):
    # uploading filenames fm database
    @app.callback(Output('upl_drop', 'options'),
                Output('comp_drop', 'options'),
                Output('upl_drop', 'value'),
                Output('prof-link', 'href'),
                Output('logout', 'href'),
                Input('submit_val', 'n_clicks'))
    def load_to_upl_and_comp_drops(n_clicks):
        if n_clicks > 0:
            try:
                user_id = current_user.get_id()
                opts = export_filenames(user_id)
                options = change_options(opts)
                upl_val = options[0]['value']
            except Exception as e:
                print(e)
                options = []
                upl_val = None
            href = url_for('profile.profile', user_id=user_id)
            href_logout = url_for('security.logout')
            return options, options, upl_val, href, href_logout
        return [], [], None, '#', '#'

    # uploading data from database
    @app.callback(Output('sel_man_drop', 'options'),
                Output('drop-month', 'options'),
                Output('drop-month', 'value'),
                Input('upl_drop', 'value'),)
    def load_from_database(upl_drop):
        if upl_drop:
            # exporting data from database
            if current_user.is_authenticated:
                user_id = current_user.get_id()
                try:
                    file = export_report_data(upl_drop, user_id)
                    df = file.data
                except:
                    print('Something goes wrong!')
            # creating options to changing month in break-even graph
            months = df['Months']
            opt_month = []
            for i, m in enumerate(months):
                dictionary = {'label': m, 'value': i}
                opt_month.append(dictionary)
            mon_value = opt_month[0]['value']
            # change drop down to choose subdivision
            opt = change_options_man(df)
            return opt, opt_month, mon_value
        return [], [], None

    # Callback for creating graph
    @app.callback(Output('profit-graph', 'figure'),
                Output('profit-graph2', 'figure'),
                Output('div-for-graphs', 'style'),
                Output('break-even', 'figure'),
                Output('br-even-div', 'style'),
                Output('dr-select', 'style'),
                Input('upl_drop', 'value'),
                Input('comp_drop', 'value'),
                Input('drop_sel_it', 'value'),
                Input('sel_man_drop', 'value'),
                Input('fig_check', 'value'),
                Input('drop-br-even', 'value'),
                Input('br-even-range-slider', 'value'),
                Input('drop-month', 'value'))
    def update_graph(sel_upl_drop, sel_comp_drop, drop_sel_it, sel_man_drop1,
                    fig_check, drop_br_even, br_even_range_slider, dr_month):
        if sel_upl_drop is not None:
            # exporting data from database
            if current_user.is_authenticated:
                user_id = current_user.get_id()
                try:
                    file = export_report_data(sel_upl_drop, user_id)
                    df = file.data
                except:
                    print('Something goes wrong!')
            # ==========================================================================
            # check for displaying pie graph and graph for 1 variable
            if sel_upl_drop == sel_comp_drop or sel_comp_drop == None:
                # checking for choosed division, for graph with 1 var
                if sel_man_drop1 is not None:
                    fig = func_for_graph1(sel_upl_drop, df['Months'],
                                        df[sel_man_drop1], sel_man_drop1, fig_check)
                else:
                    fig = {'data': [], 'layout': {}, 'frames': [], }
                # checking for pie graph
                if drop_sel_it is not None:
                    labels, values = for_graph_pie1(df, drop_sel_it)
                    fig_pie = graph_pie(labels, values, drop_sel_it)
                else:
                    fig_pie = {'data': [], 'layout': {}, 'frames': [], }
            # ==========================================================================
                # style for graph containers, to change whether one var graph, or 2 var graph
                st1 = {'grid-template-columns': '45% 55%'}
                # opacity for dropdown for pie graph
                st2 = {'opacity': '100'}
            # ==========================================================================
                # checking for break even graph
                if fig_check and 'br-even' in fig_check:
                    br_arr = br_even_state_drop(drop_br_even)
                    st3 = {'display': 'grid',
                        'grid-template-columns': '200px 1fr', 'width': '100%'}
                    fig_break = breakeven_calc(
                        df, dr_month, br_arr, br_even_range_slider)
                else:
                    st3 = {'display': 'none'}
                    fig_break = {'data': [], 'layout': {}, 'frames': [], }
                # return for pie graph, 1 var graph and break-even graph
                return fig_pie, fig, st1, fig_break, st3, st2
            # ==========================================================================
            # check for displaying comparing graph with 2 vars
            elif sel_upl_drop != sel_comp_drop:
                df1 = df
                # exporting data from database
                if current_user.is_authenticated:
                    user_id = current_user.get_id()
                    try:
                        file = export_report_data(sel_comp_drop, user_id)
                        df2 = file.data
                    except:
                        print('Something goes wrong!')
                # checking for dropdown not empty
                if sel_man_drop1 is not None:
                    fig = func_for_graph2(name1=sel_upl_drop,
                                        name2=sel_comp_drop,
                                        x=df1['Months'],
                                        y1=df1[sel_man_drop1],
                                        y2=df2[sel_man_drop1],
                                        yaxis_name=sel_man_drop1,
                                        val=fig_check)
                    fig2 = func_for_comparing(x=df1['Months'],
                                            y1=df1[sel_man_drop1],
                                            y2=df2[sel_man_drop1],
                                            yaxis_name=sel_man_drop1,
                                            val=fig_check)
                    st1 = {'grid-template-columns': '55% 45%'}
                    st2 = {'opacity': '0'}
                    st3 = {'display': 'none'}
                    fig_break = {'data': [], 'layout': {}, 'frames': [], }
                else:
                    st1 = {'grid-template-columns': '55% 45%'}
                    st2 = {'opacity': '0'}
                    st3 = {'display': 'none'}
                    fig_break = {'data': [], 'layout': {}, 'frames': [], }
                    fig = {'data': [], 'layout': {}, 'frames': [], }
                    fig2 = {'data': [], 'layout': {}, 'frames': [], }
                # return for 2 var graph
                return fig, fig2, st1, fig_break, st3, st2
            # ==========================================================================
        st1 = {'grid-template-columns': '50% 50'}
        st2 = {'opacity': '100'}
        st3 = {'display': 'none'}
        default_value_graph = {'data': [], 'layout': {}, 'frames': [], }
        return default_value_graph, default_value_graph, st1, default_value_graph, st3, st2
