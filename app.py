import plotly.express as px
from jupyter_dash import JupyterDash
from dash import Dash, html, dcc, Input, Output, State
import dash_bootstrap_components as dbc
import pandas as pd
import os
import base64
import requests
from contextlib import closing
import csv
import statistics


px.set_mapbox_access_token("pk.eyJ1IjoiemlxaW50aWFuIiwiYSI6ImNsMWdzb2JkNjFlZm4zcG54NWhzaWVtdXkifQ.Bewl0ISItyYwAGSAFPOQRA")


sim_url="https://raw.githubusercontent.com/KiLiG-fcx/design-clinic/main/revised_sim.csv"

'''
A simulation for hotspot
If there are already hotspot information in the given dataset, this part can be neglected
Create some hotspots based on the simulation data, and collect the information in the 'dropdown' list
'''

dropdown=[[],[],[],[]]
with closing(requests.get(sim_url, stream=True)) as r:
    f = (line.decode('utf-8') for line in r.iter_lines())
    reader = csv.reader(f, delimiter=',', quotechar='"')
    next(reader,None)
    for row in reader:
        for i in range(2,12):
            row[i]=int(row[i])
        row[-1]=float(row[-1])
        row[-2]=float(row[-2])
        monitorid=int(row[1])
        if (monitorid<13250):
            dropdown[0].append(row)
        elif (13250<=monitorid<13500):
            dropdown[1].append(row)
        elif (13500<=monitorid<13750):
            dropdown[2].append(row)
        else:
            dropdown[3].append(row)

def readcols(url):
    df=pd.read_csv(url)
    fields=[] # fields used for all dropdown choices
    for col in df.columns:
        fields.append(col)
    return (fields)


def hotspotcsv(hotspot):
    '''
        hotspot: int
        number chosen by dropdown (in simulated data: 1-4)
        create new csv to generate a new range of latitude, longitude
    '''
    fields=readcols(sim_url)
    rows_data=dropdown[hotspot-1] # the list of data that will be used to create the csv
    df=pd.DataFrame(rows_data,columns=fields)
    #print(type(df['latitude'][1]))
    return df

def hotspot_plot(hotspot):
    df = hotspotcsv(hotspot)
    hotspot_fig = px.scatter_mapbox(df, lat="latitude", lon="longitude", color="NO2 (ppb)",
                        center={'lat':statistics.median(df['latitude']),'lon':statistics.median(df['longitude'])},
                                    # center is used to change the map center position
                      color_continuous_scale=px.colors.cyclical.IceFire, zoom=10, width=700, height=800)
    #hotspot_fig.show()
    return hotspot_fig

airQual = pd.read_csv(sim_url)
fig = px.scatter_mapbox(airQual, lat="latitude", lon="longitude", color="NO2 (Plume AQI)",
                    color_continuous_scale=px.colors.cyclical.IceFire, zoom=10, width=700, height=800)

# Application

app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

server = app.server


logo = os.getcwd() + '/assets/EHRA_logo.jpeg'
encoded_image = base64.b64encode(open(logo, 'rb').read())

SIDEBAR_STYLE = {
    "top": 0,
    "left": 0,
    "bottom": 0,
    "width": "16rem",
    "height": "100%",
    "padding": "1rem 1rem",
    "background-color": "#f8f9fa",
    'display': 'inline-block',
    "border":"1.5px #e6e6e6 solid",
}

FIGURE_STYLE = {
    "top": 0,
    "left": 0,
    "bottom": 0,
    "margin-left": "-14rem",
    "margin-right": "-1.5rem",
    'display': 'inline-block',
    "height": "100%"
}

NEWS_STYLE = {
    "top": "0rem",
    "padding-top": "1rem",
    "padding-left": "1rem",
    "padding-right": "1rem",
    "height": "100%",
    "left": 0,
    "bottom": 0,
    "background-color": "#f8f9fa",
    'display': 'inline-block',
    "border":"1.5px #e6e6e6 solid",
}

FAQ_STYLE = {
    "margin-top" : "3rem",
    "padding-top": "1rem",
    "padding-left": "1rem",
    "padding-right": "1rem",
    "min-height": "150px",
    "height": "120%",
}

sidebar = html.Div(
    [
        html.Img(src='data:image/png;base64,{}'.format(encoded_image.decode()), style={'width': '220px'}),
        html.H4('Pollutant'),
        dcc.RadioItems(id = 'radio-item-1',
                        options = [dict(label = ' NO2', value = 'A'),
                                    dict(label = ' VOC', value = 'B'),
                                    dict(label = ' PM1', value = 'C'),
                                    dict(label = ' PM10', value = 'D'),
                                    dict(label = ' PM25', value = 'E')],
                        value = 'A',
                        labelStyle={'display': 'block'}),

        html.P(['Abbreviations', html.Br(),\
            'PM: Particulate Matter', html.Br(),\
            'NO2: Nitrogen Dioxide', html.Br(),\
                'VOC: Volatine Organic Compound', html.Br(),\
                    'PM10: PM<10um diameter', html.Br(),\
                        'PM25: PM<2.5um diameter']),
       
        html.H4(['Select locations:']),

        # dcc.Dropdown(
        #     # ['Elementary School', 'Factory', 'Middle School', 'Park'], 'Select hotspots', 
        #     id='hotspot-dropdown',
        # ),
        # dcc.Dropdown(["NYC", "MTL", "SF"], "NYC", id="demo-dropdown"),
        dcc.Dropdown(id='hotspot-dropdown', 
                    options=[{'label':'Elementary School', 'value':'Elementary School'}, {'label': 'Factory', 'value':'Factory'}, {'label': 'Middle School', 'value':'Middle School'}, {'label': 'Park', 'value':'Park'}], 
                    value="Select hotspots"),

        html.P('These hotspots were selected based on the air quality pollutant data released to the government.'),
        dbc.Button("Upload my Flow Monitor Data", color="primary", className="me-1", 
        href='https://docs.google.com/forms/d/e/1FAIpQLSeO__LGt9egJ8AEhVXB5YlO5YOEwjl9NYudUqe7H_MyvJ-MGQ/viewform?usp=pp_url', target='_blank'),
    ],
    style=SIDEBAR_STYLE,
)

news = html.Div(
    [
        html.H4('Related News & Information'),
        dbc.ButtonGroup(
            [
                html.P('Click the links below to read more articles: '),
                dbc.Button('Environmental injustice and racism in Michigan: A new MLive documentary', size="lg", outline=True, color="primary", className="me-1", 
                href='https://www.mlive.com/news/2021/07/environmental-injustice-and-racism-in-michigan-a-new-mlive-documentary.html', target='_blank'),
        
                dbc.Button('It’s time to change the way we measure pollution', size="lg", outline=True, color="primary", className="me-1", 
                href='https://thehill.com/opinion/energy-environment/529601-its-time-to-change-the-way-we-measure-pollution/', target='_blank'),

                dbc.Button('UM-D summer academy on environmental health empowers students to take action', size="lg", outline=True, color="primary", className="me-1", 
                href='https://www.secondwavemedia.com/metromode/features/summer-academy-081718.aspx?utm_source=Emma&utm_medium=Email&utm_term=UM-D+summer+academy+on+environmental+health+empowers+students+to+take+action&utm_content=Custom+Email&utm_campaign=Solutions+for+a+healthy+Michiga', target='_blank'),
            ],
                vertical=True,
        )  
    ],
    style= NEWS_STYLE,
)

content = html.Div(dcc.Graph(id = 'main-graph', figure=fig), style = FIGURE_STYLE)

FAQ = html.Div(
    [
        html.H4("Frequently Asked Questions"),
        dbc.ButtonGroup(
            [
                dbc.Button(
                    "How was this data collected?",
                    id="collapse-button1",
                    className="mb-3",
                    color="primary",
                    n_clicks=0,
                    outline=True,
                ),
                dbc.Collapse(
                    dbc.Card(dbc.CardBody("These data were collected my community members using AirFlow2 monitors from PlumeLab.")),
                    id="collapse1",
                    is_open=False,
                ),

                dbc.Button(
                    "Can I help with the collection of this data?",
                    color="primary",
                    id="collapse-button2",
                    className="mb-3",
                    n_clicks=0,
                    outline=True,
                ),
                dbc.Collapse(
                    dbc.Card(dbc.CardBody("If you own an AirFlow2 monitor and would like to add your data onto our map, please upload your data using the 'Upload My Flow Monitor Data' above.")),
                    id="collapse2",
                    is_open=False,
                ),
            ],
             vertical=True,
        )
      
    ],
    style = FAQ_STYLE,
)

row = html.Div(
    [
        dbc.Row(
            [
                dbc.Col(sidebar),
                dbc.Col(content),
                dbc.Col(news),
            ]
        ),
        dbc.Row(
             dbc.Col(
                FAQ,
             #   width={"size": 8, "offset": 2},
    )
),
    ]
)

app.layout = row
@app.callback(
    Output('main-graph', 'figure'),
    Input('hotspot-dropdown','value'),
    Input('radio-item-1', 'value'))
def update_figure(hotspot, pollutant):
    airQual = pd.read_csv(sim_url)

    hotspot_id = { 'Elementary School': 1,
                'Factory': 2,
                'Middle School': 3,
                'Park': 4}
    if hotspot != 'Select hotspots':
        airQual = hotspotcsv(hotspot_id[hotspot])

    air_measures = {'A': "NO2 (Plume AQI)",
            'B': "VOC (Plume AQI)",
            'C': "pm 1 (Plume AQI)",
            'D': "pm 10 (Plume AQI)",
            'E': "pm 25 (Plume AQI)"}

    fig = px.scatter_mapbox(airQual, lat="latitude", lon="longitude", color=air_measures[pollutant],
                        center={'lat':statistics.median(airQual['latitude']),'lon':statistics.median(airQual['longitude'])},
                      color_continuous_scale=px.colors.cyclical.IceFire, zoom=10, width=700, height=800)

    fig.update_layout(coloraxis_colorbar=dict(title=air_measures[pollutant],))
    return fig 

@app.callback(
    Output("collapse1", "is_open"),
    [Input("collapse-button1", "n_clicks")],
    [State("collapse1", "is_open")],
)
def toggle_collapse(n, is_open):
    if n:
        return not is_open
    return is_open

@app.callback(
    Output("collapse2", "is_open"),
    [Input("collapse-button2", "n_clicks")],
    [State("collapse2", "is_open")],
)
def toggle_collapse(n, is_open):
    if n:
        return not is_open
    return is_open

## Deploy app -------------------------------------------------------------
if __name__ == '__main__':
    app.run_server(debug=True)