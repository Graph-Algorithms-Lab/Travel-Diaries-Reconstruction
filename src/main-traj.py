import networkx as nx
import random
from odparser import *
from censoparser import *
from traveldiary import *


# 4. Funzione per punto casuale
def random_point_in_polygon(polygon):
    minx, miny, maxx, maxy = polygon.bounds
    
    while True:
        x = random.uniform(minx, maxx)
        y = random.uniform(miny, maxy)
        p = Point(x, y)
        if polygon.contains(p):
            return p

# Esempio d'uso:
if __name__ == "__main__":
    
    random.seed(31)
    
    EXACT=False
    EDGE=True
    UNIFORM=False
    GO_BACK_HOME=True

    HOW_MANY_DIARIES=100
    
    # t = 30
    t = len(range(0, 7)) # see the shared doc about fasce orarie lookup. TODO: fix that later.
    n = 50
    N = 200

    def F(x): return is_weekday(x, 3) and is_recurrent(x) and not is_hidden(get_time_window(x)) and is_in_florence(x)
    
    G, parts, locations, V, Vinv = build_t_partite_graph_from_od_matrix(t, '../data/fs/Output Matrice Fondamentale Firenze.csv', F)
    
    if VERBOSE:
        print("nodes", G.nodes())
        print("edges", G.edges())

    for i in range(t):
        s=0
        for u in parts[i]:
            s0 = G.nodes[u].get("count", 0)
            s += s0
            if DEBUG: print("Vertex", u, "with count", s0)
        if DEBUG: print(f"Somma etichette dei vertici partizione {i}: {s}")

    # Verifica: stampiamo la somma delle etichette per ogni coppia di partizioni consecutive
    if EDGE and DEBUG:
        for i in range(t - 1):
            s = 0
            for u in parts[i]:
                for v in parts[i + 1]:
                    w = G[u].get(v, {'weight': 0})['weight']
                    s += w
                    print("edge from", u, "to", v ,"with label", w)
            
            print(f"Somma etichette tra partizione {i} e {i+1}: {s}")

    sol_iterable = get_travel_diaries(G, parts, UNIFORM, EDGE, EXACT, GO_BACK_HOME)

    res = list(sol_iterable) if EXACT else [next(sol_iterable) for _ in range(HOW_MANY_DIARIES)]

    print("Found", len(res), "travel diaries")

    if DEBUG:
        for diary in res:
            print([locations[V[u]].zone_name for t, u in diary])

    # let's try to join censo data for the diaries found.
    rows, legend, sections = parse_censo( '../data/censo/censo-2021.csv', '../data/censo/censo-legenda.csv', '../data/zonizzazione/Sez censimento Toscana_riparate.shp')

    special = {}
    special['Rifredi'] = 'Firenze'
    special['Campo di Marte'] = 'Firenze'
    special['Firenze Centro Storico'] = 'Firenze'
    special["Barberino Val d'Elsa"] = 'Barberino Tavarnelle'
    special["Incisa in Val d'Arno"] = 'Figline e Incisa Valdarno'
    special["Figline Valdarno"] = 'Figline e Incisa Valdarno'

    age_codes = list(map(lambda x: 'P' + str(x), list(range(30, 46)) + list(range(67, 83))))

    geo_travel_diaries = []

    for diary in res:

        geo_travel_diary = []

        origin = diary[0]
        origin_location = locations[V[origin[1]]].zone_name
        print(f"Origin location {origin_location}")
        filtered_rows = list(filter(lambda x: x['COMUNE'] == special[origin_location] if origin_location in special else x['COMUNE'] == origin_location, rows))
        weights = list(map(lambda x: int(x['P1']), filtered_rows))
        choosen = random.choices(filtered_rows, weights=weights, k=1)[0]
        age_weights = list(map(lambda age_code: int(choosen[age_code]), age_codes))
        age_code_choosen = random.choices(age_codes, weights=age_weights, k=1)[0]
        point = random_point_in_polygon(sections[choosen['SEZIONE CENSIMENTO']].geometry)
        # print(f"Origin {origin_location} choosen {choosen['COMUNE']} age_code {age_code_choosen} age {legend[age_code_choosen]}")
        # print(f"Choosen point {point} for its home.")

        geo_travel_diary.append((origin_location, point))

        for rest in diary[1:]:
            loc = locations[V[rest[1]]]
            dest_location = loc.zone_name
            point = random_point_in_polygon(loc.geometry)
            # print(f"Destination {dest_location} choosen point {point} for its destination.")
            geo_travel_diary.append((dest_location, point))

        if GO_BACK_HOME: geo_travel_diary[-1] = geo_travel_diary[0]

        geo_travel_diaries.append(geo_travel_diary)
    
    print(f"Generated geo travel diaries: {geo_travel_diaries}")

    if VERBOSE:
        print("Checking correctness of travel diaries found")
        print(check_result(G,parts,res, EDGE))

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


