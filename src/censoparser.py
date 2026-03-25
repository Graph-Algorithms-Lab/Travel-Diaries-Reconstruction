
import csv
import geopandas as gpd
import pandas as pd

def load_gis(filename):

    gdf = gpd.read_file(filename)

    # (opzionale ma consigliato) lavora in metri
    gdf = gdf.to_crs("EPSG:3857")

    return gdf


def parse_censo(file_path, legend_filename, gis_filename):

    gdf = load_gis(gis_filename)

    rows = []
    sections = {}
    
    with open(file_path, "r") as csvfile:

        spamreader = pd.read_csv(csvfile, delimiter=',', thousands=".", decimal=",").to_dict(orient='records')

        for row in spamreader:
            sez = row['SEZIONE CENSIMENTO']
            sections[sez] = gdf[gdf['SEZ21_ID'] == int(sez)].iloc[0]
            rows.append(row)

    legend = {}

    with open(legend_filename, "r") as csvfile:

        spamreader = csv.DictReader(csvfile, delimiter=',')

        for row in spamreader:
            
            legend[row['NOME_CAMPO']] = row['DEFINIZIONE']

    return rows, legend, sections


# rows, legend = parse_censo('../data/censo/censo-2021-grouped.csv', '../data/censo/censo-legenda.csv')

# print(rows[0])
# print(legend)

# import pandas as pd

# df = pd.read_csv('../data/censo/censo-2021.csv', delimiter=',', thousands=".", decimal=",")

# df_grouped = df.groupby("COMUNE").sum(numeric_only=True)

# df_grouped

# df_grouped.to_csv('../data/censo/censo-2021-grouped.csv', sep=',', decimal=',', index=True)