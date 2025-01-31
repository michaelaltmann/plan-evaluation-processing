
import geopandas as gpd
from evaltools import dualgraph

vtds = gpd.read_file("./test-resources/test-precincts")
vtds = vtds.to_crs("epsg:4326")
vtds["LAT"] = vtds["geometry"].apply(lambda g: g.representative_point().coords[0][1]).astype(float)
vtds["LON"] = vtds["geometry"].apply(lambda g: g.representative_point().coords[0][0]).astype(float)
vtds = vtds[[
    "COUNTYFP", "PRECINCT", "TOTPOP", "PRES16D", "CD", "geometry", "LAT", "LON"
]]

dg = dualgraph(vtds, "PRECINCT")
dg.to_json("./test-resources/test-graph.json")
