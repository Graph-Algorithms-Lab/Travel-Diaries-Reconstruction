
import random, pprint
from blackboxparser import *

# Esempio d'uso:
if __name__ == "__main__":
    
    blackboxes_iter = parse_blackboxes('../data/blackboxes/firenze/home_chains.csv',
                                       '../data/blackboxes/firenze/staypoints.csv',
                                       '../data/blackboxes/firenze/trips.csv',
                                       (100, 'n_trips'))
    
    blackboxes = list(blackboxes_iter)
    
    print("Chosen blackboxes:")
    pprint.pp(blackboxes)