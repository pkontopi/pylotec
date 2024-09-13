from setuptools import setup, find_packages

setup(
    name='pylotec',
    version='1.0',
    author = "Simon Linke, Patrick Kontopidis",
    package_dir={"": "pylotec"},
    include_package_data=True,
    packages=["pylotec"],
    package_data = {"pylotec": ["./pylotec/*.py"], "pylotec": ["./Functions/*.py"], "pylotec": ["./old/*.ipynb"]},
    install_requires=['numpy', 'matplotlib', 'pillow', 'tqdm', 'scipy', 'pandas', 'plotly'],
)
