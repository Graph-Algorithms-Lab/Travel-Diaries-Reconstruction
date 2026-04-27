
import csv
import geopandas as gpd
import pandas as pd

def parse_censo(file_path, legend_filename, gis_filename):

    # gdf = gpd.read_file(gis_filename).set_crs("EPSG:3857").to_crs("EPSG:4326")    
    gdf = gpd.read_file(gis_filename).to_crs("EPSG:4326")    

    rows = []
    sections = {}
    
    with open(file_path, "r") as csvfile:

        for row in pd.read_csv(csvfile, delimiter=',', thousands=".", decimal=",").to_dict(orient='records'):
            sez = row['SEZIONE CENSIMENTO']
            sections[sez] = gdf[gdf['SEZ21_ID'] == int(sez)].iloc[0]
            rows.append(row)

    legend = {}

    with open(legend_filename, "r") as csvfile:

        for row in csv.DictReader(csvfile, delimiter=','):
            
            legend[row['NOME_CAMPO']] = row['DEFINIZIONE']

    return rows, legend, sections
