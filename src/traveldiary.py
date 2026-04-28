import networkx as nx
import random
import copy
from odparser import *
from censoparser import *
from geoutils import *
from shapely.geometry import Point

MALE_SEX_CODE = 'C1M'
FEMALE_SEX_CODE = 'C1F'
SEX_CODES = [MALE_SEX_CODE, FEMALE_SEX_CODE]
def sex_code_to_value(code, male='m', female='f'): return male if code == MALE_SEX_CODE else female

AGE_CODES = {
    MALE_SEX_CODE: list(map(lambda x: 'P' + str(x), list(range(33, 43)))),
    FEMALE_SEX_CODE: list(map(lambda x: 'P' + str(x), list(range(70, 80)))),
}
AGE_CODES_TO_INTERVALS = {
    'P17': (15, 20),
    'P18': (20, 25),
    'P19': (25, 30),
    'P20': (30, 35),
    'P21': (35, 40),
    'P22': (40, 45),
    'P23': (45, 50),
    'P24': (50, 55),
    'P25': (55, 60),
    'P26': (60, 65),
    'P33': (15, 20),
    'P34': (20, 25),
    'P35': (25, 30),
    'P36': (30, 35),
    'P37': (35, 40),
    'P38': (40, 45),
    'P39': (45, 50),
    'P40': (50, 55),
    'P41': (55, 60),
    'P42': (60, 65),
    'P70': (15, 20),
    'P71': (20, 25),
    'P72': (25, 30),
    'P73': (30, 35),
    'P74': (35, 40),
    'P75': (40, 45),
    'P76': (45, 50),
    'P77': (50, 55),
    'P78': (55, 60),
    'P79': (60, 65),
}
def age_code_to_value(code):
    a, b = AGE_CODES_TO_INTERVALS[code]
    return random.randint(a, b-1)

EMPLOYED_CODES = {
    MALE_SEX_CODE: ['P102', 'UP102'],
    FEMALE_SEX_CODE: ['P103', 'UP103'],
}
def employed_code_to_value(code, employed='yes', unemployed='no'):
    return employed if code == 'P102' or code == 'P103' else unemployed

VERBOSE=False
DEBUG=False
TRACE=False

def build_t_partite_graph_from_od_matrix(instants, od_matrix_tuple, F):

    rows, locations, V, Vinv = od_matrix_tuple

    def M(x):
        u = get_time_window(x) - 1, Vinv[get_source_id(x)]
        v = get_time_window(x), Vinv[get_destination_id(x)]
        w = get_weight(x)
        return u, v, w

    G = nx.DiGraph()
    
    discovered_nodes = set()

    for u, v, w in map(M, filter(F, rows)):

        src, dst = u[1], v[1]

        src_loc, dst_loc = locations[V[src]], locations[V[dst]]

        src_point = Point(*lon_lat_to_x_y(src_loc.lon, src_loc.lat))
        dst_point = Point(*lon_lat_to_x_y(dst_loc.lon, dst_loc.lat))

        # d = locations[V[src]].geometry.centroid.distance(locations[V[dst]].geometry.centroid)
        d = src_point.distance(dst_point)
        G.add_edge(u, v, weight=w, distance=d)

        # to guarantee uniqueness
        discovered_nodes.add(src)
        discovered_nodes.add(dst)

    discovered_nodes = list(discovered_nodes)
    discovered_nodes.sort() # just to have a deterministic order for debugging and testing
    
    partitions = []
    
    for t in range(instants):
        
        part = []
        
        for j in discovered_nodes:

            node = t, j

            if node not in G.nodes: G.add_node(node)
            
            nn = G.nodes[node]
            
            j_loc = locations[V[j]]

            x, y = lon_lat_to_x_y(j_loc.lon, j_loc.lat)

            nn['count'] = 0
            nn['part'] = t
            nn['idx'] = j
            nn['lat'] = j_loc.lat
            nn['lon'] = j_loc.lon
            nn['x'] = x
            nn['y'] = y
            nn['centroid'] = j_loc.geometry.centroid
            nn['zone_name'] = j_loc.zone_name

            part.append(node)
        
        partitions.append(part)
    
    for part in partitions:
        
        for tpart_u in part:
            
            tpart, u = tpart_u

            w_in = sum(w for _, _, w in G.in_edges(tpart_u, data='weight'))
            w_out = sum(w for _, _, w in G.out_edges(tpart_u, data='weight'))

            if tpart == 0: G.nodes[tpart_u]['count'] = w_out
            elif tpart == instants - 1: G.nodes[tpart_u]['count'] = w_in
            else: # 0 < tpart < t - 1:
                d = w_in - w_out

                if d < 0:
                    dd = -d
                    for j in range(tpart):
                        ju = j, u
                        j1u = j + 1, u
                        if G.has_edge(ju, j1u): G[ju][j1u]['weight'] += dd
                        else: G.add_edge(ju, j1u, weight=dd, distance=0)
                        G.nodes[ju]['count'] += dd
                elif d > 0: G.add_edge((tpart, u), (tpart + 1, u), weight=d, distance=0)

                G.nodes[tpart_u]['count'] = max(w_in, w_out)

    if VERBOSE:

        c = 0
        for v in discovered_nodes:

            count_start = G.nodes[(0, v)]['count']
            count_end = G.nodes[(instants - 1, v)]['count']

            d = abs(count_start - count_end) / max(count_start, count_end)

            if d > 0.1:
                c += 1
                print(f"Warning: node {v} ({locations[V[v]]['zone_name']}) has count {count_start} in partition 0 and count {count_end} in partition {t-1}, with relative difference {d:.2%}")

        print(len(discovered_nodes), "nodes discovered in the OD matrix, with", c, "nodes having a relative difference in count greater than 1% between partition 0 and partition", t-1)

    return G, partitions

def build_t_partite_graph(t: int, n: int, N: int, Edge = True, go_back_home=False):
    """
    Costruisce un grafo t-partito con t partizioni di n vertici ciascuna.
    Tra la partizione i ed i+1 il grafo è completo (K_{n,n}).
    Assegna ad ogni arco un'etichetta intera >= 0 in modo che la somma
    delle etichette degli archi tra partizione i e i+1 sia N (per ogni i).

    Restituisce un networkx.Graph con attributo d'arco 'label' (int),
    e una lista `partitions` dove partitions[i] è la lista dei nodi nella partizione i.
    """
    if t < 2:
        raise ValueError("t deve essere almeno 2 (altrimenti non ci sono archi tra partizioni).")
    if n < 1:
        raise ValueError("n deve essere almeno 1.")
    if N < 0:
        raise ValueError("Questa implementazione richiede N >= 0 (etichette non negative).")

    G = nx.DiGraph()
    partitions = []

    # Creazione nodi: li etichettiamo come (i, j) dove i = indice partizione, j = indice dentro la partizione
    for i in range(t):
        part = []
        for j in range(n):
            node = (i, j)
            G.add_node(node, part=i, idx=j)
            part.append(node)
        partitions.append(part)

    countersVertex={}
    countersEdge={}
    allTraj=[]
    for traj in range(N):
        S=[]
        for i in range(t):

            randomj=random.randint(0,n-1)

            if go_back_home and i == t-1: randomj=S[0][1]

            new_node = i, randomj
            S.append(new_node)
            countersVertex[new_node] = countersVertex.get(new_node,0) + 1
            if len(S) != 1 and Edge:
                edge=(S[-2], new_node)
                countersEdge[edge] = countersEdge.get(edge,0) + 1

        if TRACE: print("Generated trajectory", S)

        allTraj.append(S)

    for node,vcount in countersVertex.items():
        G.nodes[node]["count"] = vcount

    if Edge:
        for (u, v), ecount in countersEdge.items():
            # ensure nodes exist even if not already added (defensive)
            if u not in G:
            #    G.add_node(u, count=0, label="0")
                print("Error u not in G")
                exit()
            if v not in G:
                print("Error v not in G")
                exit()
            #    G.add_node(v, count=0, label="0")

            # store edge count, plus label/weight
            G.add_edge(u, v, weight=ecount)
    else:
        for i in range(t-1):
            for u in partitions[i]:
                for v in partitions[i+1]:
                    G.add_edge(u, v)

    # print ("Built graph with", G.number_of_nodes(), "nodes and", G.number_of_edges(), "edges")
    
    return G, partitions

def get_next_vertex(G, vertex, uniform, weighted): 
    return choose_destination(G, vertex, list(G.successors(vertex)), uniform, weighted)

def choose_destination(G, source, part, uniform, weighted):

    sum_count = sum(G.nodes[v].get("count", 0) for v in part) if weighted.get('vertex', False) else 0
    sum_weight = sum(G.edges[source, v]['weight'] for v in part if G.has_edge(source, v)) if weighted.get('edge', False) and source else 0
    sum_distance = sum(1 / (G.edges[source, v]['distance'] or 1) for v in part if G.has_edge(source, v)) if weighted.get('distance', False) and source else 0

    candidates, weights = [], []
    
    for v in part:

        w = 0

        w += (G.nodes[v].get("count", 0) / sum_count) * weighted.get('vertex', 0)

        if source: w += (G.edges[source, v]['weight'] / sum_weight) * weighted.get('edge', 0)

        if source: w += ((1 / (G.edges[source, v]['distance'] or 1)) / sum_distance) * weighted.get('distance', 0)

        if G.nodes[v].get("count", 0) > 0:
            candidates.append(v)
            weights.append(w)

    if candidates: return random.choice(candidates) if uniform else random.choices(candidates, weights=weights)[0]
    
#Edge implica Vertex, Vertex non implica Edge
def get_next_travel_diary(G, partitions, uniform, edge, exact, weighted, go_back_home):
    
    u = choose_destination(G, None, partitions[0], uniform, weighted)
    
    if not u: return None
    
    path = [u]

    for i in range(len(partitions)-1):

        v = (i + 1, path[0][1]) if i == len(partitions)-2 and go_back_home else get_next_vertex(G, u, uniform, weighted)
        
        if v == None: break
        
        if TRACE: print("next vertex", v)

        path.append(v)
        u = v

    if DEBUG: print("Found a path ", path)

    if exact: 
        
        #Aggiorniamo per vertice
        for u in path:

            assert G.nodes[u].get("count", 0) > 0, f"Error: node {u} has count {G.nodes[u].get('count', 0)} but should be > 0"
            G.nodes[u]["count"]-=1

        #Aggiorniamo gli archi
        if edge:
            for i in range(len(path)-1):
                u=path[i]
                v=path[i+1]
                
                if G[u].get(v, {"weight":0})['weight'] <= 0:
                    print("G[u][v][weight]<=0")
                    print ("Error: edge from", u, "to", v, "has weight", G[u].get(v, {"weight":-1})['weight'], "but should be > 0")
                    exit(1)

                G[u][v]["weight"] -= 1
                
                if G[u][v]["weight"]==0: #Quando arco va a zero va rimosso
                    G.remove_edge(u, v)

    return path

def get_travel_diaries(G, partitions, uniform=True, edge=True, exact=True,  go_back_home=False, 
                       weighted={'vertex': 1, 'edge': 1, 'distance': 1}):
    
    copyG = copy.deepcopy(G)
    
    while True:

        partialsol = get_next_travel_diary(copyG, partitions, uniform, edge, exact, weighted, go_back_home)

        if not partialsol: break

        yield partialsol

def check_result(G, partitions, travel_diaries, Edge=True):
    #Gprime=copy.deepcopy(G)
    Gprime = nx.DiGraph()
    for t in range(len(partitions)):
        for v in partitions[t]:
            Gprime.add_node(v, part=v[0], idx=v[1])
    for traj in travel_diaries:
        for v in traj:
            Gprime.nodes[v]["count"]=0
    for traj in travel_diaries:
        for v in traj:
            Gprime.nodes[v]["count"] += 1
        if Edge:
            for j in range(len(traj)-1):
                u=traj[j]
                v=traj[j+1]
                if not Gprime.has_edge(u, v):
                    Gprime.add_edge(u, v, weight=0)
                Gprime[u][v]["weight"]+=1
    
    #check whether G and Gprime are equal
    same_nodes = set(G.nodes()) == set(Gprime.nodes())

    if Edge:
        print(G.edges())
        print(Gprime.edges())
    
        #check whether G and Gprime are equal
        same_edges = set(G.edges()) == set(Gprime.edges())

    same_counts=True
    for n in G.nodes():
        if G.nodes[n].get("count", 0) != Gprime.nodes[n].get("count", 0):
            print ("Node", n, "has count", G.nodes[n].get("count", 0), "in G and count", Gprime.nodes[n].get("count", 0), "in Gprime")
            same_counts=False
            break
    
    if Edge:
        weights_G = nx.get_edge_attributes(G, "weight")
        weights_Gprime = nx.get_edge_attributes(Gprime, "weight")
        same_weights = weights_G == weights_Gprime
        print("same_nodes and same_edges and same_counts and same_weights", same_nodes , same_edges , same_counts , same_weights)
        return same_nodes and same_edges and same_counts and same_weights
    else:
        print("same_nodes and same_counts", same_nodes, same_counts)
        return same_nodes and same_counts

def travel_diaries_iter(
        fundamental_matrix_filename, 
        gis_filename, 
        censo_filename, 
        censo_legend_filename, 
        zones_filename,
        exact_required=False, 
        EDGE=True, 
        UNIFORM=False, 
        go_back_home=True, 
        how_many_diaries=100,
        how_many_instants=7,
        weekday=3,
        recurrent=True,
    ):
    
    def F(x): return is_weekday(x, weekday) and ((not recurrent) or is_recurrent(x)) and not is_hidden(get_time_window(x)) and is_in_florence(x)
    
    gdf = read_gis_shape_file(gis_filename)

    rows, locations, V, Vinv = od_matrix_tuple = parse_od_matrix(fundamental_matrix_filename, gdf)

    G, parts = build_t_partite_graph_from_od_matrix(how_many_instants, od_matrix_tuple, F)

    sol_iterable = get_travel_diaries(G, parts, UNIFORM, EDGE, exact_required, go_back_home)

    res = list(sol_iterable) if exact_required else [next(sol_iterable) for _ in range(how_many_diaries)]

    rows, legend, sections = parse_censo(censo_filename, censo_legend_filename, zones_filename)

    special = {}
    special['Rifredi'] = 'Firenze'
    special['Campo di Marte'] = 'Firenze'
    special['Firenze Centro Storico'] = 'Firenze'
    special["Barberino Val d'Elsa"] = 'Barberino Tavarnelle'
    special["Incisa in Val d'Arno"] = 'Figline e Incisa Valdarno'
    special["Figline Valdarno"] = 'Figline e Incisa Valdarno'

    def make_path_step(loc, point):
        lon, lat = point.x, point.y
        x, y = lon_lat_to_x_y(lon, lat)
        return {'zone': loc, 'lon': point.x, 'lat': point.y, 'x': x, 'y': y}

    for diary in res:

        path = []

        _, v0 = diary[0]

        origin_location = locations[V[v0]].zone_name
        
        def F(x): 
            loc = x['COMUNE']
            return loc == special[origin_location] if origin_location in special else loc == origin_location
        
        filtered_rows = list(filter(F, rows))

        def weighted_sample(row, keys):
            ws = list(map(lambda k: row[k], keys))
            key = random.choices(keys, weights=ws, k=1)[0]
            return key
        
        weights = list(map(lambda x: x['C1'], filtered_rows))
        choosen_row = random.choices(filtered_rows, weights=weights, k=1)[0]

        # sex_weights = list(map(lambda age_code: choosen_row[age_code], SEX_CODES))
        # sex_code_choosen = random.choices(SEX_CODES, weights=sex_weights, k=1)[0]
        sex_code_choosen = weighted_sample(choosen_row, SEX_CODES)

        # age_weights = list(map(lambda age_code: choosen_row[age_code], AGE_CODES[sex_code_choosen]))
        # age_code_choosen = random.choices(AGE_CODES[sex_code_choosen], weights=age_weights, k=1)[0]
        age_code_choosen = weighted_sample(choosen_row, AGE_CODES[sex_code_choosen])

        employed_code_choosen = weighted_sample(choosen_row, EMPLOYED_CODES[sex_code_choosen])

        section = sections[choosen_row['SEZIONE CENSIMENTO']]
        point = random_point_in_polygon(section.geometry)
        
        path.append(make_path_step(origin_location, point))

        for rest in diary[1:]:
            loc = locations[V[rest[1]]]
            dest_location = loc.zone_name
            point = random_point_in_polygon(loc.geometry)
            path.append(make_path_step(dest_location, point))

        if go_back_home: path[-1] = path[0]

        yield {
            'path': path,
            'age': age_code_to_value(age_code_choosen),
            'age_def': legend[age_code_choosen],
            'comune': choosen_row['COMUNE'],
            'type': 'diary',
            'id': random.randint(0, int(1e9)),
            'sex': sex_code_to_value(sex_code_choosen),
            'employed': employed_code_to_value(employed_code_choosen),
        }
    
    if VERBOSE:
        print("Checking correctness of travel diaries found")
        print(check_result(G,parts,res, EDGE))

    