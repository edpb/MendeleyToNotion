from setuptools import setup, find_packages


setup(
    name='MendeleyToNotion', # name of the git repo
    description='A package to port Mendeley data to Notion',
    author='edpb',
    author_email='edevpb@outlook.com',
    version='1.0.0',
    packages=find_packages(include=['src', 'globalStore', 'lib']) # folders to be installed as a pkg
)
