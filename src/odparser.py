
import csv
import geopandas as gpd
from geoutils import lon_lat_to_x_y

# The OD matrix is in the form of a CSV file with the following columns:
SOURCE_REGION_KEY = 'REGIONE_ORIGINE'
DESTINATION_REGION_KEY = 'REGIONE_DESTINAZIONE'
SOURCE_PROVINCE_KEY = '\ufeffPROVINCIA_ORIGINE'
DESTINATION_PROVINCE_KEY = 'PROVINCIA_DESTINAZIONE'
SOURCE_ZONE_KEY = 'ZONA_ORIGINE'
DESTINATION_ZONE_KEY = 'ZONA_DESTINAZIONE'
SOURCE_ID_KEY = 'COD_ORIGINE'
DESTINATION_ID_KEY = 'COD_DESTINAZIONE'
WEEKDAY_KEY = 'GIORNO_SETTIMANA_ID'
RECURRENT_KEY = 'SISTEMATICITA_ID'
TIME_WINDOW_KEY = 'FASCIA_ORARIA_MACRO_ID'
WEIGHT_KEY = 'VIAGGI'

def is_hidden(v): return v == '-1' or v == -1
def is_weekday(row, weekday): return row[WEEKDAY_KEY] == str(weekday)
def is_recurrent(row): return row[RECURRENT_KEY] == '1'

def get_time_window(row): return int(row[TIME_WINDOW_KEY])
def is_in_tuscany(row): return row[SOURCE_REGION_KEY] == 'Toscana' and row[DESTINATION_REGION_KEY] == 'Toscana'
def is_in_florence(row): return row[SOURCE_PROVINCE_KEY] == 'Firenze' and row[DESTINATION_PROVINCE_KEY] == 'Firenze'
def get_source_zone(row): return row[SOURCE_ZONE_KEY]
def get_destination_zone(row): return row[DESTINATION_ZONE_KEY]
def get_source_id(row): return row[SOURCE_ID_KEY]
def get_destination_id(row): return row[DESTINATION_ID_KEY]
def get_weight(row): return int(row[WEIGHT_KEY])

def parse_od_matrix(fundamental_matrix_filename, gis_filename):

    count = {}
    V = []
    locations = {}
    rows = []
    
    gdf = gpd.read_file(gis_filename).to_crs("EPSG:4326")

    xs, ys = [], []
    for lon, lat in zip(gdf["lon"], gdf["lat"]):
        x, y = lon_lat_to_x_y(lon, lat)
        xs.append(x)
        ys.append(y)
    gdf["x"] = xs
    gdf["y"] = ys

    def count_node_if_new(n):
        if n not in count:
            c = len(count)
            count[n] = c
            V.append(n)
            locations[n] = gdf[gdf.area_id == n].iloc[0]

    with open(fundamental_matrix_filename, "r") as csvfile:

        for row in csv.DictReader(csvfile, delimiter=';'):

            rows.append(row)

            count_node_if_new(get_source_id(row))
            count_node_if_new(get_destination_id(row))

    return rows, locations, V, count

