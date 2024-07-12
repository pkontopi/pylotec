from setuptools import setup, find_packages

setup(
    name='pylotec',
    version='1.0',
    packages=find_packages(include=['pylotec', 'pylotec.*']),
    install_requires=['numpy', 'matplotlib', 'pillow', 'tqdm', 'scipy', 'pandas', 'plotly'],
)