
from setuptools import setup, find_packages

requirements = [
    "maup==1.0.6",  "scipy", "networkx",   "matplotlib",
    "gerrychain", "sortedcontainers", "gurobipy", "jsonlines", "opencv-python",
    "imageio", "us", "pydantic", "censusdata", "seaborn", "python-dotenv"
]

setup(
    name="evaltools",
    author="MGGG Redistricting Lab",
    author_email="engineering@mggg.org",
    description="Tools for processing and visualizing districting plans.",
    url="https://github.com/mggg/plan-evaluation-processing",
    packages=find_packages(exclude=["tests"]),
    install_requires=requirements,
    extras_require={
        "dev": [
            "pdoc3"
        ]
    }
)
