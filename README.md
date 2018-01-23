# eqplots
_python tools to plot local and global earthquake events, gathered from the IRIS earthquake repository_

#### requirements:
```
matplotlib==1.5.3
numpy==1.11.3
scipy==0.19.0
obspy==1.1.0
basemap==1.1.0
```

#### installation
_via [Anaconda](https://www.anaconda.com/)_
```
conda create --name obspy --python=2
source activate obspy
conda install matplotlib==1.5.3
conda install basemap basemap-data-hires obspy

# to verify the installation:
obspy-runtests
```
