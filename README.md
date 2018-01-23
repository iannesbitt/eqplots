# eqplots
_python tools to plot local and global earthquake events, gathered from the IRIS earthquake repository_

### requirements
```
matplotlib==1.5.3
numpy==1.11.3
scipy==0.19.0
obspy==1.1.0
basemap==1.1.0
```

### installation
_via [Anaconda](https://www.anaconda.com/)_
```
conda create --name obspy --python=2
source activate obspy
conda install matplotlib==1.5.3
conda install basemap basemap-data-hires obspy

# to verify the installation:
obspy-runtests
```

### customization
Change `YOUR_STATIONS`, `YOUR_LATITUDE`, and `YOUR_LONGITUDE` to reflect where in the world you'd like to plot and which Raspberry Shake stations you'd like to appear on your plots.

First, start by editing the file
```
nano plotevents_universal.py
```

#### _stations_
To define which stations to plot, change the line
```
YOUR_STATIONS = ('RCB43', 'R06AC', 'R35E7')
```
to reflect the stations you'd like to appear. Multiple stations can be put in a tuple (list) as seen above, or a single station can be defined in a manner similar to the following:
```
YOUR_STATIONS = ('RCB43')
```

#### _latitude and longitude-based plot centralization_
You'll have two lines:
```
YOUR_LATITUDE = 45.0
YOUR_LONGITUDE = -70.0
```
You don't need to be exact. Just one decimal place ususally is enough to center the map properly. Negative latitude indicates southern hemisphere, and negative longitude indicates western hemisphere.

### usage
#### _command line_
```
cd eqplots/
source activate obspy
python plotevents_universal.py
```
#### _example using cron_
Cron is how I keep my website's images up-to-date. Here's a sample cron entry.
```
SHELL=/bin/bash
OBSPYTHON=/home/user/anaconda2/envs/obspy/bin
PRDIR=/home/user/bin/eqplots    ## or wherever your eqplots installation happens to be
*/10 * * * * cd $PRDIR/obspyevents; source activate obspy; $OBSPYTHON/python plotevents.py
```
Since eqplots will create plots in the same directory as the source files, you may want to include a script that moves them to whatever directory you'd like your website's media files to reside in, in which case the last line of your cron entry would look like this
```
*/10 * * * * cd $PRDIR/obspyevents; source activate obspy; $OBSPYTHON/python plotevents.py; mv *.png /var/www/website/media/plots
```
