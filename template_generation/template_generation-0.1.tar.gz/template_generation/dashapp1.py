import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import traceback
import pandas as pd
from template_generation import processfile as pf, template
import constant
import flask
from configparser import ConfigParser

app = dash.Dash()
'''use local css'''
# app.css.config.serve_locally = True
# app.scripts.config.serve_locally = True
# stylesheets = ['local-css.css', 'pure.css']
# for stylesheet in stylesheets:
#     app.css.append_css({"external_url": "/css/{}".format(stylesheet)})

'''use flask to publish local css'''
css_path = pf.get_path_from_current(constant.os_path,'css')
@app.server.route('/css/<resource>')
def serve_static(resource):
    return flask.send_from_directory(css_path, resource)

app.css.append_css({
    'external_url': '/css/local-css.css',
})
'''use external css'''
css_url = 'https://unpkg.com/purecss@1.0.0/build/pure-min.css'
app.css.append_css({
    "external_url": css_url
})
def init_batch():
    config = ConfigParser()
    batch_num = template.get_batch_num(config, constant.SETTING)
    return batch_num

app.layout = html.Div([
    html.Div(className='pure-g cssheader', children=[
        html.Div(className='pure-u-1-24'),
        html.Div(className='pure-u-22-24', children=[html.H2(children='Template Generation Tool')]),
        html.Div(className='pure-u-1-24 cssversion', children=[html.Span(className='csssp', children='V1.0')]),
    ]),
    html.Form(className='pure-form pure-form-aligned cssform', children=[

        html.Div(className='pure-control-group', children=[
                html.Label('Batch'),
                dcc.Input(placeholder='Batch Number',type='text', id='batch-value')
            ]),
        html.Div(className='pure-control-group', children=[
            html.Label('User Name'),
            dcc.Input(placeholder='User Name', type='text', id='user-value')
        ]),
        html.Div(className='pure-control-group', children=[
            html.Label('Description', className='csslb'),
            dcc.Textarea(placeholder='Please input description', rows='5', cols='40', id='comment-value')
        ]),
        html.Div(className='pure-controls', children=[
                html.Button('Submit', id='convert-btn', className='pure-button pure-button-primary cssbt')
            ])
        ]),
    html.Div(id='my-div'),
    html.Div(className='pure-g', children=[
        html.Div(className='pure-u-1-24'),
        html.Div(className='pure-u-22-24', id='live-update-text'),
        html.Div(className='pure-u-1-24')
    ]),
    # dcc.Graph(id='live-update-graph-scatter', animate=True),
    dcc.Interval(
        id='interval-component',
        interval=1 * 1000
    )
])
@app.callback(
    Output('my-div', 'children'),
    [Input('convert-btn', 'n_clicks')],
     state=[State('batch-value', 'value'),
            State('user-value', 'value'),
            State('comment-value', 'value')]
)
def clicks(n_clicks, batch_value, user_value, comment_value):
    try:
        if n_clicks is not None:
            template.generate_new_template('source', 'target', batch_value)
            template.generate_log('log', batch_value, user_value, comment_value)
            return []
    except Exception:
        traceback.print_exc()


@app.callback(Output('live-update-text', 'children'),

              [Input('interval-component', 'n_intervals')])
def generate_table(n):
    history_file = pf.get_path_from_current(constant.os_path, 'log', 'history.csv')
    df = pd.read_csv(history_file).applymap(str)
    df['Batch'] = df['Batch'].apply(lambda x: x.zfill(3))
    return html.Div(children=[
        html.H3(children='History Log'),
        html.Table(className='pure-table', children=
            # Header
            [html.Tr([html.Th(col) for col in df.columns])] +

            # Body
            [html.Tr([
                html.Td(df.iloc[i][col]) for col in df.columns
            ]) for i in range(min(len(df), 100))]
        )
    ])



if __name__ == '__main__':
    app.run_server(debug=True)