
from evaltools.scoring import (
    deviations, splits, pieces, unassigned_units, unassigned_population,
    contiguous, reock
)
from evaltools.geometry import Partition
from gerrychain.graph import Graph
from pathlib import Path
import geopandas as gpd
from gerrychain.grid import Grid
from shapely.geometry import box
import math
import os

root = Path(os.getcwd()) / Path("tests/test-resources/")

def test_splits():
    # Read in an existing dual graph.
    dg = Graph.from_json(root / "test-graph.json")
    P = Partition(dg, "CONGRESS")
    units = ["COUNTYFP20"]
    geometricsplits = splits(P, ["COUNTYFP20"])
    geometricsplitsnames = splits(P, ["COUNTYFP20"], names=True)

    split = {'005', '135', '085', '067', '091', '045', '097', '017'}

    # Assert that we have a dictionary and that we have the right keys in it.
    assert type(geometricsplits) is dict
    assert set(units) == set(geometricsplits.keys())

    # Make sure that we're counting the number of splits correctly – Indiana's
    # enacted Congressional plan should split counties 8 times.
    assert geometricsplits["COUNTYFP20"] == 8
    assert len(geometricsplitsnames["COUNTYFP20"]) == 8
    assert set(geometricsplitsnames["COUNTYFP20"]) == split


def test_pieces():
    # Read in an existing dual graph.
    dg = Graph.from_json(root / "test-graph.json")
    P = Partition(dg, "CONGRESS")
    units = ["COUNTYFP20"]
    geometricpieces = pieces(P, ["COUNTYFP20"])
    geometricpiecesnames = pieces(P, ["COUNTYFP20"], names=True)

    split = {'005', '135', '085', '067', '091', '045', '097', '017'}

    # Assert that we have a dictionary and that we have the right keys in it.
    assert type(geometricpieces) is dict
    assert set(units) == set(geometricpieces.keys())
    
    # Make sure that we're counting the number of splits correctly – Indiana's
    # enacted Congressional plan should split counties 8 times.
    assert geometricpieces["COUNTYFP20"] == 16
    assert set(geometricpiecesnames["COUNTYFP20"]) == split


def test_deviations():
    dg = Graph.from_json(root / "test-graph.json")
    P = Partition(dg, "CONGRESS")
    devs = deviations(P, "TOTPOP")

    assert type(devs) is dict
    assert set(data["CONGRESS"] for _, data in dg.nodes(data=True)) == set(devs.keys())


def test_contiguity():
    dg = Graph.from_json(root / "test-graph.json")
    P = Partition(dg, "CONGRESS")
    contiguity = contiguous(P)

    # This plan should *not* be contiguous, as some VTDs are discontiguous
    # themselves.
    assert not contiguity


def test_unassigned_units():
    dg = Graph.from_json(root / "test-graph.json")
    P = Partition(dg, "CONGRESS")
    bads = unassigned_units(P)
    wholebads = unassigned_units(P, raw=True)

    # This plan shouldn't have any unassigned units.
    assert bads == 0

    # These two things should report the same number, since none are unassigned.
    assert bads == wholebads


def test_reock_score_squares_geodataframe():
    grid = Grid((10, 10))
    gdf = gpd.GeoDataFrame([
        {'node': (x, y), 'geometry': box(x, y, x + 1, y + 1)}
        for (x, y) in grid.graph
    ]).set_index('node')
    score_fn = reock(gdf)

    # The Reock score of a square inscribed in a circle is
    # area(square) / area(circle) = 2/π.
    expected_dist_score = 2/ math.pi
    scored = score_fn(grid)

    assert scored.keys() == grid.parts.keys()
    for dist_score in scored.values():
        assert abs(dist_score - expected_dist_score) < 1e-4

def test_reock_score_squares_graph():
    grid = Grid((10, 10))
    for (x, y), data in grid.graph.nodes(data=True):
        data['geometry'] = box(x, y, x + 1, y + 1)
    score_fn = reock(grid.graph)

    # The Reock score of a square inscribed in a circle is
    # area(square) / area(circle) = 2/π.
    expected_dist_score = 2 / math.pi
    scored = score_fn(grid)

    assert scored.keys() == grid.parts.keys()
    for dist_score in scored.values():
        assert abs(dist_score - expected_dist_score) < 1e-4


def test_reock_score_disconnected():
    grid = Grid((10, 10))
    for (x, y), data in grid.graph.nodes(data=True):
        data['geometry'] = box(x, y, x + 1, y + 1)
    score_fn = reock(grid.graph)

    # Break district 0 into two disconnected pieces 
    # (while preserving convex hull perimeter),
    # adding a disconnected component to district 3
    # (quadrupling convex hull perimeter).
    grid_disconnected = grid.flip({(0, 1): 3, (1, 0): 3})

    scored = score_fn(grid_disconnected)
    assert scored.keys() == grid_disconnected.parts.keys()
    assert abs(scored[0] - ((23 / 25) * (2 / math.pi))) < 1e-4
    assert abs(scored[1] - (2 / math.pi)) < 1e-4
    assert abs(scored[2] - (2 / math.pi)) < 1e-4
    assert abs(scored[3] == (27 / 25) * (math.pi / 2)) < 1e-4

if __name__ == "__main__":
    root = Path(os.getcwd()) / Path("test-resources/")
    test_pieces()
