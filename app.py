from dash import Dash, html, dcc, Input, Output, dash_table
import plotly.graph_objects as go
import dash_bootstrap_components as dbc
from dash.dependencies import State
import pandas as pd
import plotly.express as px
import json

def load_data():
    data = pd.read_csv("deer_tick_surveillance.csv", sep=",")

    counties_json = json.load(open("new-york-counties.geojson", "r"))
    counties_json["features"][0]

    for i in range(len(counties_json["features"])):
        counties_json["features"][i]['properties']['name'] = counties_json["features"][i]['properties']['name'].replace(" County", "")

    counties = []

    for feature in counties_json["features"]:
        counties.append(feature["properties"]["name"])

    counties = [*set(counties)]
    counties.sort()

    data.rename(columns={"Total Ticks Collected": "y",
                         "Total Sites Visited": "n",
                         "Total Tested": "t"}, inplace=True)

    data['Year'] = data['Year'].astype('category')

    county_df = pd.DataFrame(counties, columns =['County'])
    year_df = pd.DataFrame(list(range(2008, 2023)), columns =['Year'])
    data_df = county_df.merge(year_df, how='cross')

    data_df = data_df.merge(data[['County', 'Year', 'y', 'n', 't', 'B. burgdorferi (%)', 'A. phagocytophilum (%)',
                                  'B. microti (%)', 'B. miyamotoi (%)']],
                            on=['County', 'Year'],
                            how='left')

    data_df['MLE'] = (data_df['y'] / data_df['n']).round(3)
    data_df['MLE'] = data_df['MLE'].fillna(0)

    for attr in ['y', 'n', 't', 'B. burgdorferi (%)', 'A. phagocytophilum (%)', 'B. microti (%)', 'B. miyamotoi (%)']:
        data_df[attr] = data_df[attr].fillna(0)

    return data_df, counties_json


data_df, counties_json = load_data()


app = Dash(__name__, external_stylesheets=[
    'https://fonts.googleapis.com/css2?family=Jura:wght@200&display=swap', 
    dbc.themes.BOOTSTRAP
])

server = app.server

#*******APP LAYOUT**************

app.layout = html.Div(
    style={
        'backgroundColor':'#F1F6F1',
        'height': '100%',
        'color': '#1F6357',
        'margin': 0,
        'padding': 0 , 
    }, 
    
    children=[
        #****************************HEADER*************************************
        html.Div(
            style={
                'fontFamily': 'Jura',  
                'backgroundColor': '#1e453e',
                'padding': '10px',
                'margin': 0,  
                'display': 'flex',
                'flexDirection': 'column',
            },
            children=[
                html.H1(
                    children='Tick Surveillance',
                    style={
                        'fontFamily': 'Jura',  
                        'fontSize': '36px',  
                        'fontWeight': '400',      
                        'color': 'white'              
                    }
                ),
                html.H1(
                    children='Monitoring of Black-Legged Tick Nymphs in the New York State (2008-2022)',
                    style={
                        'fontFamily': 'Jura',  
                        'fontSize': '20px',  
                        'fontWeight': '350',      
                        'color': 'white'              
                    }
                ),
            ]
        ),
        #****************************Map*************************************   
        
        html.Div(
            dcc.Graph(id='map'), 
            style={'width': '90%', 'margin': '0 auto', 'display': 'block', 'padding':'0'}
        ),

        #****************************Slider*************************************   
        html.Div([
            'Years',
            dcc.Slider(2008, 2022, step = 1, value=2022, id='slider',
                    marks={i: f"{i}" for i in range(2008,2023,1)},
                    tooltip={'placement': 'bottom', 'always_visible': True})
            ], 
            style={'width': '90%', 
                   'margin': '0 auto', 
                   'display': 'block', 
                   'height': '50px',
                   'paddingLeft': '20px',
                   'paddingRight':'20px'   
                  } ),       
        #****************************Controls with Info Button*************************************
        html.Div([
            html.Div([
                'Disease: ',
                dcc.RadioItems(
                    ['All', 'A. phagocytophilum', 'B. burgdorferi', 'B. microti', 'B. miyamotoi'],
                    'All',
                    id='disease',
                    inline=True,
                    style={
                        'display': 'flex', 
                        'gap': '10px',
                        'maxWidth': '100%', 
                        'overflow': 'hidden'
                    }
                ),
            ],
                style={
                    'display': 'flex',
                    'fontFamily': 'Jura',
                    'height': '50px',
                    'paddingLeft': '18px',
                    'paddingTop': '20px',
                    'gap': '11px',
                    'maxWidth': '100%',
                }
            ),
            
            html.Div(
                children=[
                    dbc.Button(
                        "ℹ️",
                        id="open_modal",
                        color="success", 
                        style={"padding": "1px 3px", "marginTop": "5px", "fontSize": "15px"}
                    ),
                ],
                style={
                    'display': 'flex',
                    'alignItems': 'center',
                    'marginLeft': '10px',  
                    'paddingTop': '10px',
                }
            ),
        ],
            style={
                'display': 'flex',
                'alignItems': 'center', 
                'width': '50%',
                'paddingLeft': '18px',
                'paddingTop': '28px',
                'gap': '11px',
            }
        ),

        dbc.Modal(
            [
                dbc.ModalHeader("Information"),
                dbc.ModalBody(                    
                    html.Div([
                        html.P("A. phagocytophilum: The bacteria that causes anaplasmosis, also known as tick-borne fever."),
                        html.P("B. burgdorferi: The bacteria that causes Lyme disease."),
                        html.P("B. microti: A parasitic blood-borne piroplasm responsible for the disease babesiosis."),
                        html.P("B. miyamotoi: The bacteria that causes the Borrelia miyamotoi disease."),
                    ])
                ),
                dbc.ModalFooter(
                    dbc.Button("Close", id="close_modal", className="ml-auto")
                ),
            ],
            id="modal",
            is_open=False,
        ),
        #****************************Barplot*************************************   
        html.Div(
            [dcc.Graph(id='barplot')], 
            style={'width': '50%', 'display': 'inline-block'},), 
        
        #****************************Timeline*************************************   
        html.Div(
            [dcc.Graph(id='timeline')], 
            style={'width': '50%', 'display': 'inline-block'},), 

        #****************************Footer*************************************   
        html.Footer(
            [
                "Data provided by ",
                html.A(
                    "New York State Department of Health",
                    href="https://health.data.ny.gov/Health/Deer-Tick-Surveillance-Nymphs-May-to-Sept-excludin/kibp-u2ip/data",
                    target="_blank", 
                    style={'color': 'black', 'textDecoration': 'none'} 
                ),
                "."
            ],
            style={'textAlign': 'center', 'marginTop': '20px', 'color': 'gray', 'fontSize': '15px'}
        )
    ]
 )


#**************FUNCTIONS*****************************

def get_map(year, county=None):
    stats_map = data_df[data_df["Year"] == year]
    
    fig = px.choropleth(
        stats_map,
        geojson=counties_json,
        featureidkey='properties.name',
        locations='County',
        color='MLE',
        color_continuous_scale='OrRd',
        projection='equirectangular',
        title='',
        labels={
            'y': 'Total Ticks Collected',
            'n': 'Total Sites Visited',
            'MLE': 'Max Likelihood Estimate'
        },
        hover_data=['County', 'MLE', 'n', 'y']
    )
    
    fig.update_geos(visible=False)
    fig.update_layout(
        margin={"r": 0, "t": 50, "l": 0, "b": 0},
        geo_bgcolor="#F1F1F1",
        geo_showlakes=False,
        geo_fitbounds="locations",
        geo_resolution=110,
        geo_landcolor="#F1F6F1",
        geo_showcountries=True,
        paper_bgcolor="#F1F6F1",
        font_color="black",
    )
    
    if county:
        county_geojson = {
            "type": "FeatureCollection",
            "features": [
                feature for feature in counties_json["features"]
                if feature["properties"]["name"] == county
            ]
        }
        
        outline_coords = county_geojson["features"][0]["geometry"]["coordinates"]
        
        for polygon in outline_coords:
            if isinstance(polygon[0][0], list):  
                polygons = polygon
            else:
                polygons = [polygon] 
            
            for poly in polygons:
                lons, lats = zip(*poly)
                fig.add_trace(
                    go.Scattergeo(
                        lon=lons,
                        lat=lats,
                        mode="lines",
                        line=dict(color="#32CD32", width=3),
                        name=f"Selected County: {county}",
                        hoverinfo="skip",
                        showlegend=False,
                    )
                )

    return fig


def get_county_graph(county):
      timeline = data_df[data_df['County'] == county]
      bars = px.bar(timeline,
                    x="Year",
                    y='MLE',
        title= "Barplot of the mean number of ticks in " + county + " over the years",
                    )
      bars.update_layout(plot_bgcolor= "#F1F6F1", paper_bgcolor= "#F1F6F1", font_color="black", xaxis=dict(dtick=1))
      bars.update_traces(marker_color="#7CDF7C")
      bars.update_layout(margin={"r":20,"t":55,"l":20,"b":0})
      return bars


def get_county_graph2(disease, county):
    timeline = data_df[data_df['County'] == county]
    
    if disease == 'All':
        diseases = ['A. phagocytophilum (%)', 'B. burgdorferi (%)', 'B. microti (%)', 'B. miyamotoi (%)']
        
        stacked_data = timeline[diseases + ['t']].copy()       
        stacked_data['Year'] = timeline['Year']
        
        bars = px.bar(
            stacked_data, 
            x="Year", 
            y=diseases, 
            title= f"Stacked Barplot of the percentage of positively tested ticks in {county} over the Years",
            labels={'t': 'Total Ticks Tested'},
            hover_data=['Year', 't']
        )
        
        colors = ["#FF7F50", "#FFD700", "#ADFF2F", "#32CD32"]
        tested = [timeline[timeline['Year'] == i]['t'].iloc[0] for i in range(2008, 2023)]

        for i, trace in enumerate(bars.data):
            trace.marker.color = colors[i]

        bars.update_layout(
            barmode='stack',
            plot_bgcolor="#F1F6F1", 
            paper_bgcolor="#F1F6F1", 
            font_color="black",  
            xaxis=dict(dtick=1),
            yaxis=dict(range=[0, 100])
        )
    
    else:
        bars = px.bar(
            timeline, 
            x="Year", 
            y=disease + ' (%)',
            title=f"Barplot of the percentage of positively tested ticks for {disease} in {county} over the years",
            labels={'t': 'Total Ticks Tested'},
            hover_data=['Year', 't']
        )
        
        bars.update_layout(
            plot_bgcolor="#F1F6F1", 
            paper_bgcolor="#F1F6F1", 
            font_color="black",  
            yaxis=dict(range=[0, 100]),
            xaxis=dict(dtick=1)
        )
        
        bars.update_traces(marker_color="#7CDF7C")
    
    bars.update_layout(margin={"r":20,"t":60,"l":20,"b":0})
    
    return bars



#*************CALLBACKS*****************************************

#slider->map
@app.callback(
    Output('map', 'figure'),
    Input('slider', 'value'),
    Input('map', 'clickData')
)

def update_map(year, clickData):
    county = "Washington"
    if clickData:
        county = clickData['points'][0]['location']
    fig = get_map(year, county)
    return fig

#map->bars
@app.callback(
    Output('timeline', 'figure'),
    Input('map', 'clickData')
)
def update_timeline(clickData):
    county = "Washington"
    if clickData is not None:
        county= clickData['points'][0]["location"]
    bars = get_county_graph(county)
    return bars

#timeline->slider
@app.callback(
    Output("slider", "value"),
    Input('timeline', 'clickData')
)
def update_year(clickData):
    year = 2022
    if clickData is not None:
        year = clickData['points'][0]["x"]
    return year

#radio,map->barplot
@app.callback(
    Output('barplot', 'figure'),
    Input('disease', 'value'),
    Input('map', 'clickData')
)
def update_barplot(disease, clickData):
    county = "Washington"
    if clickData is not None:
        county= clickData['points'][0]["location"]
    bars = get_county_graph2(disease, county)
    return bars

#data dump
@app.callback(
    Output('click-data', 'children'),
    Input('map', 'clickData')
)
def update_data(clickData):
    if clickData is not None:
        country= clickData['points'][0]["location"]
        return json.dumps(clickData, indent=2)


@app.callback(
    Output("modal", "is_open"),
    [Input("open_modal", "n_clicks"), Input("close_modal", "n_clicks")],
    [State("modal", "is_open")]
)
def toggle_modal(n1, n2, is_open):
    if n1 or n2:
        return not is_open
    return is_open



# ********RUNNING THE APP*************************************************
if __name__ == '__main__':
    app.run_server(debug=False)