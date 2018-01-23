# eqplots
_python tools to plot local and global earthquake events, gathered from the IRIS earthquake repository_

#### requirements:
```
numpy==1.11.3
scipy==0.19.0
obspy==1.1.0
pyproj==1.9.5.1
basemap==1.1.0
matplotlib==1.5.3
Pillow==4.3.0
```

#### installation
_via Anaconda_
```
conda create --name obspy --python=2
source activate obspy
conda install matplotlib==1.5.3
conda install basemap obspy

# to verify the installation:
obspy-runtests
```
