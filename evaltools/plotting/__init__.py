
"""
Makes pretty pictures of districting plans, dual graphs, histograms, boxplots,
and violin plots 🎻.
"""

from .drawplan import drawplan
from .drawgraph import drawgraph
from .colors import redbluecmap, flare, purples, districtr
from .specification import PlotSpecification
from .histogram import histogram
from .violin import violin
from .boxplot import boxplot
from .scatterplot import scatterplot
from .sealevel import sealevel
from .multidimensional import multidimensional
from .gifs import gif_multidimensional
from .bins import bins
from .annotation import arrow, ideal

__all__ = [
    "drawplan",
    "drawgraph",
    "redbluecmap",
    "PlotSpecification",
    "flare",
    "purples",
    "districtr",
    "histogram",
    "violin",
    "boxplot",
    "scatterplot",
    "sealevel",
    "multidimensional",
    "gif_multidimensional",
    "arrow",
    "ideal",
    "bins"
]
