from setuptools import setup, find_packages

setup(
    name='weo_library',
    version='0.1.0',
    packages=find_packages(),
    install_requires=[
        'pandas',
        'numpy',
        'matplotlib'
    ],
    author='Dean Roggenbauer',
)