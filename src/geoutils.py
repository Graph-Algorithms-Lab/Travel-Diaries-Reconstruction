

from pyproj import Transformer

transformer = Transformer.from_crs(
    "EPSG:4326",
    "EPSG:32632",
    always_xy=True
)

lon_lat_to_x_y = transformer.transform