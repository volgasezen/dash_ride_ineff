import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import psycopg2 as ps

import geopandas as gp
import geoplot as gpl
import geoplot.crs as gcrs

from dash import Dash, html, dcc, callback, Output, Input
from dash.exceptions import PreventUpdate
import plotly.express as px

conn_string = "host='localhost' dbname='di722' user='postgres'"
conn = ps.connect(conn_string)
cursor = conn.cursor()

def ineff(x):
    return x.loc[:,'trip_distance']/x.loc[:,'bird_dist']

def get_ineff_per(datehr, limit=0):
    try:
        date, hr = datehr.split('@')
        hr2 = hr
    except:
        date = datehr
        hr, hr2 = ['00','23']

    if limit != 0:
        query = f'''
        SELECT d.*, c.objectid as pickup_zone, t.objectid as dropoff_zone
        FROM nyczones as c, yellow146m as d, nyczones as t
        WHERE ST_Intersects(d.l_pickup,c.geom) and 
              ST_Intersects(d.l_dropoff,t.geom) and
              d.t_pickup BETWEEN '{date} {hr}:00:00' AND '{date} {hr2}:59:59'
        LIMIT {limit}
        '''
    else:
        query = f'''
        SELECT d.*, c.objectid as pickup_zone, t.objectid as dropoff_zone
        FROM nyczones as c, yellow146m as d, nyczones as t
        WHERE ST_Intersects(d.l_pickup,c.geom) and 
              ST_Intersects(d.l_dropoff,t.geom) and
              d.t_pickup BETWEEN '{date} {hr}:00:00' AND '{date} {hr2}:59:59'
        '''

    cursor.execute(query)
    dd = pd.DataFrame(cursor.fetchall())
    dd.columns = [column[0] for column in cursor.description]
    dd['ineff'] = ineff(dd)
    
    return dd

nyc = gp.read_file(r'C:\Users\speed\Downloads\nyctaxizones\geo_export_f6a85905-5cc8-4d55-8e8c-c09adb18ee30.shp')
gej = gp.read_file('NYC Taxi Zones.geojson')
gej = gej.set_geometry("geometry").set_index("objectid")

app = Dash(__name__)

app.layout = html.Div([
    html.H1('New York City Ride Inefficiency Map', style={'textAlign':'center'}),
    html.P('Enter a date from 2015 between January and June to get a map of median inefficiency per borough.',
            style={'textAlign':'center'}),
    html.Div("Enter a date and hour:", className='output-example-loading'),
    dcc.Input(id='input', debounce = True, 
                    style={'textAlign':'center'}, 
                    placeholder="YYYY-MM-DD@HH"),
    html.Div(dcc.Graph(id='graph-content'))
    ]
)

@callback(
    Output('graph-content', 'figure'),
    Input('input', 'value')
)

def update_graph(input):
    if input is None:
        raise PreventUpdate
    else:
        data = get_ineff_per(input)
        ineff = data.groupby('pickup_zone').median('ineff')
        count = data.groupby('pickup_zone').count()['vendorid']
        count.name = 'count'
        final = nyc.join([ineff,count])

        final['ineff'] = final.ineff.fillna(-1)
        final['count'] = final['count'].fillna(-1)

        return px.choropleth(final, geojson=gej, locations='location_i', color='ineff',
                               color_continuous_scale="Portland",
                               range_color=(-1, 3),
                               projection="mercator",
                               hover_data=['borough','zone','count']
                              ).update_geos(fitbounds="locations", visible=False).update_layout(margin={"r":0,"t":0,"l":0,"b":0})

if __name__ == '__main__':
    app.run_server(debug=True)
