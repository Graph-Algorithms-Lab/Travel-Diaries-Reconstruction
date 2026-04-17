
import csv
import geopandas as gpd
from shapely.geometry import Point

# This file is used to parse the OD matrix and extract the relevant information for the analysis.

# The OD matrix is in the form of a CSV file with the following columns:
SOURCE_REGION_KEY = 'REGIONE_ORIGINE'
DESTINATION_REGION_KEY = 'REGIONE_DESTINAZIONE'
SOURCE_PROVINCE_KEY = '\ufeffPROVINCIA_ORIGINE'
DESTINATION_PROVINCE_KEY = 'PROVINCIA_DESTINAZIONE'
SOURCE_ZONE_KEY = 'ZONA_ORIGINE'
DESTINATION_ZONE_KEY = 'ZONA_DESTINAZIONE'
SOURCE_ID_KEY = 'COD_ORIGINE'
SOURCE_ID_NORM_KEY = SOURCE_ID_KEY + '_NORM'
DESTINATION_ID_KEY = 'COD_DESTINAZIONE'
DESTINATION_ID_NORM_KEY = DESTINATION_ID_KEY + '_NORM'
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
def get_source_id(row): return int(row[SOURCE_ID_KEY])
def get_source_id_norm(row): return row[SOURCE_ID_NORM_KEY]
def get_destination_id(row): return int(row[DESTINATION_ID_KEY])
def get_destination_id_norm(row): return row[DESTINATION_ID_NORM_KEY]
def get_weight(row): return int(row[WEIGHT_KEY])

def parse_od_matrix(fundamental_matrix_filename, gis_filename):

    count = {}
    V = []
    locations = {}
    rows = []

    # gdf = gpd.read_file(gis_filename).set_crs("EPSG:3857").to_crs("EPSG:4326")
    gdf = gpd.read_file(gis_filename).to_crs("EPSG:4326")

    with open(fundamental_matrix_filename, "r") as csvfile:

        spamreader = csv.DictReader(csvfile, delimiter=';')

        for row in spamreader:

            rows.append(row)

            n = get_source_id(row)
            if n not in count: 
                c = len(count)
                count[n] = c
                V.append(n)
                locations[n] = gdf[gdf.area_id == str(n)].iloc[0]

            n = get_destination_id(row)
            if n not in count:
                c = len(count)
                count[n] = c
                V.append(n)
                locations[n] = gdf[gdf.area_id == str(n)].iloc[0]

    return rows, locations, V, count

# rows, locations = parse_od_matrix('../data/fs/Output Matrice Fondamentale Firenze.csv')

# filtered = list(filter(lambda x: is_weekday(x, 3) and is_recurrent(x) and not is_hidden(get_time_window(x)), rows))
# print(locations)
# print(len(locations))
# print (f"Count of rows {len(rows)} filtered {len(filtered)} ")

# edges = []
# edges = list(map(lambda x: ((get_time_window(x), get_source_id(x)), (get_time_window(x) + 1, get_destination_id(x)), get_weight(x)), filtered))
# edges
# print(f"Count of edges {len(edges)}")    
