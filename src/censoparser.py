
import csv


def parse_censo(file_path):

    rows = []
    
    with open(file_path, "r") as csvfile:

        spamreader = csv.DictReader(csvfile, delimiter=',')

        for row in spamreader:
            
            rows.append(row)

    return rows


rows = parse_censo('../data/censo/censo-2021.csv')

print(rows[0])

    