
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

    geo_travel_diaries = entrypoint('../data/fs/Output Matrice Fondamentale Firenze.csv',
                                    '../data/gis/mavfa-fs-3000_zone.shp',
                                    '../data/censo/censo-2021.csv',
                                    '../data/censo/censo-legenda.csv',
                                    '../data/zonizzazione/Sez censimento Toscana_riparate.shp',
                                    EXACT, EDGE, UNIFORM, GO_BACK_HOME, HOW_MANY_DIARIES)
    
    print("Generated geo travel diaries:")
    pprint.pp(geo_travel_diaries)

    

#    count=0
#    while True:
#        count+=1
#        path=get_next_travel_diary(G, parts)
#        if path==None:
#            break
#        print(path)
#        for edge in path:
#            u=edge[0]
#            v=edge[1]
#            G[u][v]['label']-=1
#            if G[u][v]['label']==0:
#                G.remove_edge(u,v)
#    print("count", count)
#    residualEdges=G.edges()
#    print(residualEdges)

#TODO genera istanze dove per ogni nodo indegree(v)==outdegree(v) 
#per ogni nodo v nelle partizioni intermedie
#TODO far tornare a casa
#TODO genera primo nodo non a caso ma prop a  grado pesato
#TODO genera prossimo arco prop ai pesi


