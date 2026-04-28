
import random, pprint
from traveldiary import *

# Esempio d'uso:
if __name__ == "__main__":
    
    EXACT=False
    EDGE=True
    UNIFORM=False
    GO_BACK_HOME=True

    HOW_MANY_DIARIES=100

    random.seed(561)

    diaries = travel_diaries_iter('../data/fs/Output Matrice Fondamentale Firenze.csv',
                                     '../data/gis/mavfa-fs-3000_zone.shp',
                                     '../data/censo/censo-2021.csv',
                                     '../data/censo/censo-legenda.csv',
                                     '../data/zonizzazione/Sez censimento Toscana_riparate.shp',
                                     EXACT, EDGE, UNIFORM, GO_BACK_HOME, HOW_MANY_DIARIES)
    
    geo_travel_diaries = list(diaries)
    
    print("Generated geo travel diaries:")
    pprint.pp(geo_travel_diaries)