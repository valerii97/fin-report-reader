import dash_html_components as html
import dash_core_components as dcc
from flask import url_for

menu = [
        {'name': 'Manager Efficiency', 'url':'/dash2'},
        {'name': 'Client reports', 'url':'/dash_cli'},
        {'name': 'General reports', 'url':'/dash'},
       ]

layout = html.Div([
    html.Div([  # Nav Bar
		html.A('Reports', id='prof-link'),
		html.Div('', className='vertline'),
		html.A('Manager efficiency', href='/dash2'),
        html.Div('', className='vertline'),
		html.A('Client reports', href='/dash-cli'),
		html.Div('', className='vertline'),
		html.A('General reports', href='/dash'),
		html.Div('', className='vertline'),
		html.A('Logout', id='logout'),
	], className='nav-bar'), 
    html.Div([
        html.Div([
            html.H1('REPORTING BY CLIENTS')
        ], className='top-div')
    ]), 
    html.Div([
        dcc.Checklist(
            options=[
                {'label': 'Show figures', 'value': 'figs'}
            ],
            id='fig_check',
            labelStyle={'display': 'block', 'color': 'white'}
        )
    ]),
    html.Div([
        html.Div([
            html.H4('Choose report:',
            style={'color': 'white'}),
            dcc.Dropdown(id='files',
            options=[], 
            value=None)
        ]),
        html.Div([
            html.H4('Choose manager:',
            style={'color': 'white'}),
            dcc.Dropdown(id='managers',
            options=[], 
            value=None)
        ]),
        html.Div([
            html.Button('Load reports', id='submit_value', n_clicks=1, className='button')
        ], className='but-div'),
        html.Div([
            html.Button('Load files', id='load-files', n_clicks=1, className='load-files')
        ], className='but-div')
    ], className='control-div'), 
    html.Div([
        html.Div([
            dcc.Graph(id='man_graph', style={'height':'800px'})
        ], className='graph_div'),
    ], className='graphs'),
], className='gen_div')