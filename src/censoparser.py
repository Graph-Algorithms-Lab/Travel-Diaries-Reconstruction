
import csv


def parse_censo(file_path, legend_filename):

    rows = []
    
    with open(file_path, "r") as csvfile:

        spamreader = csv.DictReader(csvfile, delimiter=',')

        for row in spamreader:
            
            rows.append(row)

    legend = {}

    with open(legend_filename, "r") as csvfile:

        spamreader = csv.DictReader(csvfile, delimiter=',')

        for row in spamreader:
            
            legend[row['NOME_CAMPO']] = row['DEFINIZIONE']

    return rows, legend


rows, legend = parse_censo('../data/censo/censo-2021-grouped.csv', '../data/censo/censo-legenda.csv')

print(rows[0])
# print(legend)

# import pandas as pd

# df = pd.read_csv('../data/censo/censo-2021.csv', delimiter=',', thousands=".", decimal=",")

# df_grouped = df.groupby("COMUNE").sum(numeric_only=True)

# df_grouped

# df_grouped.to_csv('../data/censo/censo-2021-grouped.csv', sep=',', decimal=',', index=True)