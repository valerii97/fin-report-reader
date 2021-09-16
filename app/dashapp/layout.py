import dash_html_components as html
import dash_core_components as dcc

marks = {}
for i in range(-200, 1001, 50):
    marks[i] = {'label': '{} unt'.format(i), 'style': {'color': 'white'}}

layout = html.Div([  # Main div
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
    html.Div([  # header
        html.H1('FINANCIAL REPORTING'),

    ], className='div_h1'),
    html.Div([  # Div upload and drop in main
        html.Div([
                dcc.Checklist(
                    options=[
                        {'label': 'Show figures on graphs', 'value': 'show'},
                        {'label': 'Show break-even', 'value': 'br-even'},
                        {'label': 'Hide y labels', 'value': 'hide'},
                    ],
                    id='fig_check',
                    labelStyle={'display': 'block'}
                )
        ], className='check-div'),
        html.Div(className='div_drop',  # Dropdown div in main
                 children=[
                     html.H4('Select report:'),
                     dcc.Dropdown(
                         options=[],
                         id='upl_drop')
                 ]),
        html.Div([
            html.H4('Select report to compare:'),
            dcc.Dropdown(
                options=[],
                id='comp_drop')],
            className='comp_drop'),
        html.Div([
            html.Button(['Reload'], id='submit_val',
                        n_clicks=1, className='button')
        ], className='button_div'),
    ], className='div_upload_and_drop'),
    html.Div(children=[  # Div for graph in main
        html.Div(className='div_graph',  # graph div
                 children=[
                     html.Div(className='drop_select',  # div for drop select
                              id='dr-select',
                              children=[
                                  html.H4('Select dimension:'),
                                  dcc.Dropdown(
                                      options=[
                                          {'label': u'Revenue',
                                           'value': 'Revenue '},
                                          {'label': 'Total Operational Expences',
                                           'value': 'Op. Exp.'},
                                          {'label': 'Gross Profit',
                                           'value': 'GP -'},
                                          {'label': 'Units',
                                           'value': 'Units '},
                                          {'label': 'GP per Unit',
                                           'value': 'GP p.u. '},
                                      ],
                                      id='drop_sel_it',
                                      value='Revenue '),
                              ]),
                     dcc.Graph(
                         id='profit-graph',
                     )], id='div_profit_graph'
                 ),
        html.Div(className='div_graph2',  # graph div
                 children=[
                     html.Div([
                         html.H4('Select division:'),
                         dcc.Dropdown(
                             options=[],
                             id='sel_man_drop',
                             value='Revenue - Forwarding'),
                     ], className='drop_man_sel'),
                     dcc.Graph(
                         id='profit-graph2',
                     )], id='div_profit_graph2'
                 ),
    ],
        className='div_graph_and_drop',
        id='div-for-graphs'),
    html.Div([
        html.Div([
            html.Div([
                html.H4('Select div:'),
                dcc.Dropdown(
                    options=[
                        {'label': u'Total', 'value': 'TTL'},
                        {'label': 'Forwarding', 'value': 'FRW'},
                        {'label': 'Trucking',
                         'value': 'TRK'},
                        {'label': 'Air', 'value': 'AIR'},
                    ],
                    value='TTL',
                    id='drop-br-even'
                )
            ]),
            html.Div([
                html.H4('Select month:'),
                dcc.Dropdown(
                    options=[],
                    id='drop-month'
                )
            ]),
        ], className='br-drops'),
        html.Div([
            html.Div([
                dcc.Graph(
                    id='break-even'
                )
            ], className='break-graph'),
            html.Div([
                html.H4('Range units:'),
                dcc.RangeSlider(
                    id='br-even-range-slider',
                    min=-200,
                    max=1000,
                    step=50,
                    value=[0, 500],
                    marks=marks
                )
            ]),
        ], className='slider-and-br-graph'),
    ], className='third-row-div', id='br-even-div')
], className='main_div')
