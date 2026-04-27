
import json
import pandas as pd
from geoutils import lon_lat_to_x_y

def parse_blackboxes(home_chains_filename, staypoints_filename, trips_filename, selector_tuple):

    home_chains = pd.read_csv(home_chains_filename, delimiter=',')
    staypoints = pd.read_csv(staypoints_filename, delimiter=',')
    trips = pd.read_csv(trips_filename, delimiter=',')

    home_chains['info'] = list(map(json.loads, home_chains['info']))
    staypoints['parkingtime_s'] = list(map(json.loads, staypoints['parkingtime_s']))
    staypoints['info'] = list(map(json.loads, staypoints['info']))
    trips['info'] = list(map(json.loads, trips['info']))
    trips['dt_o'] = pd.to_datetime(trips['dt_o'])
    trips['dt_d'] = pd.to_datetime(trips['dt_d'])
    trips['dt_o_unixtime'] = trips['dt_o'].apply(lambda t: int(t.timestamp()))
    trips['dt_d_unixtime'] = trips['dt_d'].apply(lambda t: int(t.timestamp()))

    how_many, w_colname = selector_tuple

    for index, row in home_chains.sample(n=how_many, weights=w_colname).iterrows():

        local_trips = []
        chain = {'id': row['id_chain'], 'trips': local_trips, 'type': 'blackbox'}

        for id_trip in row['info']['id_trips']:
            trip = trips[trips['id'] == id_trip].iloc[0].to_dict()

            staypoint_o = staypoints[staypoints['id_staypoint'] == trip['id_staypoint_o']].iloc[0].to_dict()
            staypoint_d = staypoints[staypoints['id_staypoint'] == trip['id_staypoint_d']].iloc[0].to_dict()

            x_o, y_o = lon_lat_to_x_y(staypoint_o['lon'], staypoint_o['lat'])
            x_d, y_d = lon_lat_to_x_y(staypoint_d['lon'], staypoint_d['lat'])
            
            local_trips.append({
                'id': trip['id'],
                'dt_o': str(trip['dt_o']),
                'dt_d': str(trip['dt_d']),
                'dt_o_unixtime': trip['dt_o_unixtime'],
                'dt_d_unixtime': trip['dt_d_unixtime'],
                'staypoint_o': { 'id': trip['id_staypoint_o'], 'lon': staypoint_o['lon'], 'lat': staypoint_o['lat'], 'x': x_o, 'y': y_o },
                'staypoint_d': { 'id': trip['id_staypoint_d'], 'lon': staypoint_d['lon'], 'lat': staypoint_d['lat'], 'x': x_d, 'y': y_d },
            })
            

        yield chain


