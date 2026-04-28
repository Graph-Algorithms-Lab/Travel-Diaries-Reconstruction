
import random
import geopandas as gpd
from pyproj import Transformer
from shapely.geometry import Point

# TODO: promote them as ENV variables.
EPSG_LON_LAT = "EPSG:4326"
EPSG_X_Y = "EPSG:32632"

transformer = Transformer.from_crs(EPSG_LON_LAT, EPSG_X_Y, always_xy=True)

lon_lat_to_x_y = transformer.transform

def read_gis_shape_file(filename):

    gdf = gpd.read_file(filename).to_crs(EPSG_LON_LAT)

    if 'lon' in gdf and 'lat' in gdf:

        xs, ys = [], []

        for lon, lat in zip(gdf["lon"], gdf["lat"]):
            x, y = lon_lat_to_x_y(lon, lat)
            xs.append(x)
            ys.append(y)

        gdf["x"] = xs
        gdf["y"] = ys

    return gdf

  
def random_point_in_polygon(polygon):
    
    minx, miny, maxx, maxy = polygon.bounds
    
    while True:
        x = random.uniform(minx, maxx)
        y = random.uniform(miny, maxy)
        p = Point(x, y)
        if polygon.contains(p): return p