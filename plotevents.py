# -*- coding: utf-8 -*-

###########################################################
#             Ian Nesbitt's EQ event plotter              #
###########################################################
#      NOTE: This scrpit is extremely resource-heavy.     #
#    It's a good idea not to run it on RaspberryPi or     #
# other machines with limited available system resources. #
###########################################################
#               Copyleft Ian Nesbitt, 2018                #
###########################################################

###########################################################
#             Begin easily editable variables             #
###########################################################
#                 YOUR STATION(S) GO HERE:                #
###########################################################
# This variable below tells obspy which Raspberry Shake station(s) to look for.
# Your station code should be a 5-character alphanumeric sequence available on your raspberryshake's local web page.
# If you do not know your station code, please contact the forums, or the Raspberry Shake team for help.

# NOTE: all station names should be strings separated by commas (i.e. enclosed in quotation marks)
# a single station will look like: YOUR_STATIONS = ('RCB43')
# multiple stations will look like: YOUR_STATIONS = ('RCB43', 'R06AC', 'R35E7')

YOUR_STATIONS = ('RCB43', 'R4989', 'R6A3B')#, 'R35E7')

###########################################################
#               YOUR LAT AND LONG GO HERE:                #
###########################################################
# you don't need to be exact, just general lat/lon to center your maps and gather local earthquake data
# if you don't know them, you can go to google maps and click on an uninhabited area near your town, away from roads

# negative latitude indicates southern hemisphere
YOUR_LATITUDE = 44.0
# negative longitude indicates western hemisphere
YOUR_LONGITUDE = -70.0

###########################################################
#                  OTHER USEFUL KNOBS:                    #
###########################################################
# Things to adjust and play with
DURATION = 35 # earthquake search in days before now

LOCAL_RADIUS = 10 # IRIS search radius for local eqs, in degrees 
LOCAL_MAG = -1 # minimum local eq magnitude

REGIONAL_RADIUS = 30 # search radius for regional eqs, in degrees
REGIONAL_MAG = 4.0 # minimum regional eq magnitude

NRCAN_RADIUS = 1300 # EarthquakesCanada search radius kilometers
NRCAN_DEG = NRCAN_RADIUS / 110

GLOBAL_MIN_MAG = 5.59 # minimum global eq magnitude

###########################################################
#             End of easily editable variables            #
###########################################################

# progress definitions
p0, p1, p2, p3, p4, p5, p6, p7, p8, p9, p10 = 0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100


print('#########################')
print('#       PLOTEVENTS      #')
print('# (ɔ) 2018 Ian Nesbitt  #')
print('#########################')

print('Using lat %s and lon %s as home.' % (YOUR_LATITUDE, YOUR_LONGITUDE))
print('Parameters:')
print('Local earthquakes larger than M%s within %s degrees' % (LOCAL_MAG, LOCAL_RADIUS))
print('Regional earthquakes larger than M%s within %s and %s degrees' % (REGIONAL_MAG, LOCAL_RADIUS, REGIONAL_RADIUS))
print('Canadian earthquakes within %s km' % (NRCAN_RADIUS))
print('Global earthquakes larger than M%s' % (GLOBAL_MIN_MAG))
print('Stations:')
print(YOUR_STATIONS)
print('')
print('%s%% - Importing resources...' % (p0))

from obspy import read_inventory, read_events
from requests.exceptions import ConnectionError
from obspy.clients.fdsn.client import Client
from obspy.clients.fdsn.header import FDSNNoDataException
from obspy.core.event.catalog import Catalog
from obspy.core.event import Event
from obspy.core.event.event import EventDescription
from obspy.core.event.origin import Origin
from obspy.core.event.magnitude import Magnitude
from obspy.core.event.base import QuantityError, CreationInfo
from obspy.core.inventory.network import Network
from obspy.core.inventory.inventory import Inventory
from obspy.core import UTCDateTime
from datetime import datetime, timedelta
from mpl_toolkits.basemap import Basemap
import pandas as pd
import matplotlib
matplotlib.use('agg')
import matplotlib.pyplot as plt
import csv
import urllib2
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import pickle

import re                       # Import the regular expression library
 
Exclusions = [
    'a', 'an', 'the',                                                                                                                                                           # Articles
    'and', 'but', 'or',  'by', 'nor', 'yet', 'so',                                   # Conjunctions
    'from', 'near', 'off', 'upon', 'of',                                             # Prepositions
    'region', 'reg',
    'km',
]

AllCaps = [
    'SW', 'SE', 'NW', 'NE',                                                          # Sub-cardinal directions
    'QC', 'NB', 'NS', 'ON', 'AB', 'BC', 'MB', 'NL', 'NT', 'NU', 'PE', 'SK', 'YT',    # Canadian territories
    'US', 'U.', 'S.',                                                                # United States
]
 
def TitleCase(curText=str):
    """ Take a string and return it in a fashion that follows proper title case guidelines """
 
    outString = ""
    fragments = re.split( r'(\".*?\")|(\'.*?\')|(“.*?”)|(‘.*?’)', curText )     # Extract titles in quotation marks from string
 
    for fragment in fragments:                                                                  # Treat and re-assemble all fragments
        if fragment:                                                                                            # skip empty matches generated by the OR in regex   
            fragString = ""
            tokens = fragment.split();                                                          # Break string into individual words
 
            if tokens:
                for word in tokens:                                                                     # Check each word
 
                    punct = word[-1]                                                                        # Check for trailing punctuation mark
                    if punct.isalpha():
                        punct = ""
                    else:
                        word = word[:-1]
 
                    if word.lower() in Exclusions:                                          # if it is excluded,
                        fragString += word.lower() + punct + " "                    # make it lowercase
                    elif word.upper() in AllCaps:
                        fragString += word.upper() + punct + " "
                    else:                                                                                               # otherwise,
                        fragString += word.capitalize() + punct + " "           # capitalize it

                cap = 1
                if not fragString[0].isalpha():
                    cap = 2
 
                outString += ( fragString[:cap].upper() + fragString[cap:]).strip() + " "
 
    return (outString[:1].upper() + outString[1:]).strip()          # Capitalize first letter and strip trailing space


print('%s%% - Importing IRIS FDSN client...' % (p1))
iris = Client("IRIS")
t2 = UTCDateTime.now()
t2str = t2.strftime('%Y-%m-%d %H:%M UTC')
t1 = t2 - timedelta(days=DURATION)

cat = Catalog()
nrcat = Catalog()
cat2 = Catalog()

####### LOCAL ########

try:
    print('%s%% - Getting local earthquakes within %s degrees from IRIS...' % (p2, LOCAL_RADIUS))
    cat += iris.get_events(starttime=t1, endtime=t2, latitude=YOUR_LATITUDE,
        longitude=YOUR_LONGITUDE, minmagnitude=LOCAL_MAG, maxradius=LOCAL_RADIUS)
    for evt in cat:
        evt['event_descriptions'][0]['text'] = TitleCase(evt['event_descriptions'][0]['text'].split('/')[0])
        try:
            evt['magnitudes'][0]['creation_info']['author'] = evt['origins'][0]['creation_info']['author'].split(',')[0]
        except TypeError as e:
            au = evt['origins'][0]['creation_info']['author'].split(',')[0]
            tm = evt['origins'][0]['time']
            evt['magnitudes'][0]['creation_info'] = CreationInfo(author=au, time=tm)
            print("%s%% - Warning: manually assigned a quake CreationInfo (author: %s, time: %s)" % (p5, au, tm))
        evt['origins'][0]['depth'] = evt['origins'][0]['depth'] / 1000
    cat += nrcat
    print('%s%% - Found %s NRCan events. Catalog now contains %s events.' % (p5, nrcat.count(), cat.count()))
except FDSNNoDataException:
    print('%s%% - No local earthquakes found in IRIS database within %s degree radius.' % (p2, LOCAL_RADIUS))
except Exception as e:
    print('%s%% - Error: %s' % (p2, e))

try:
    print('%s%% - Connecting to NRCan...' % (p5))
    url = 'http://www.earthquakescanada.nrcan.gc.ca/api//fdsnws/event/1/query?earthquaketypes=L&starttime=%s&endtime=%s&latitude=%s&longitude=%s&minradius=0&maxradius=%s&onlyfelt=0' % (t1.strftime('%Y%%2F%m%%2F%d+%H%%3A%M%%3A%S'), t2.strftime('%Y%%2F%m%%2F%d+%H%%3A%M%%3A%S'), YOUR_LATITUDE, YOUR_LONGITUDE, NRCAN_DEG)
    nrcat += read_events(pathname_or_url=url, format='QUAKEML')
    print('%s%% - Query url: %s' % (p5, url))
    for evt in nrcat:
        evt['event_descriptions'][0]['text'] = TitleCase(evt['event_descriptions'][0]['text'].split('/')[0])
        evt['magnitudes'][0]['creation_info'] = CreationInfo(author='cn', time=evt['origins'][0]['time'])
        #evt['origins'][0]['depth'] = evt['origins'][0]['depth'] * 1000
    cat += nrcat
    print('%s%% - Found %s NRCan events. Catalog now contains %s events.' % (p5, nrcat.count(), cat.count()))
# except ConnectionError:
#     print('%s%% - Could not connect to NRCan.' % (p5))
except Exception as e:
    print('%s%% - An error occurred parsing data from NRCan. Error: %s' % (p5, e))

print('%s%% - Local IRIS/NRCAN catalog:' % (p4))
print(cat.__str__(print_all=True))

####### REGIONAL ########
try:
    print('%s%% - Getting regional earthquakes above M%s between %s and %s degrees...' % (p3, REGIONAL_MAG, LOCAL_RADIUS, REGIONAL_RADIUS))
    cat2 += iris.get_events(starttime=t1, endtime=t2, latitude=YOUR_LATITUDE,
        longitude=YOUR_LONGITUDE, minmagnitude=REGIONAL_MAG, minradius=LOCAL_RADIUS, maxradius=REGIONAL_RADIUS)
except FDSNNoDataException:
    print('%s%% - No %s+ earthquakes found between %s and %s degree radii.' % (p3, REGIONAL_MAG, LOCAL_RADIUS, REGIONAL_RADIUS))
except Exception as e:
    print('%s%% - Error: %s' % (p3, e))

try:
    for evt in cat2:
        evt['event_descriptions'][0]['text'] = TitleCase(evt['event_descriptions'][0]['text'])
        evt['origins'][0]['depth'] = evt['origins'][0]['depth']
        try:
            evt['magnitudes'][0]['creation_info']['author'] = evt['origins'][0]['creation_info']['author'].split(',')[0]
        except TypeError as e:
            au = evt['origins'][0]['creation_info']['author'].split(',')[0]
            tm = evt['origins'][0]['time']
            evt['magnitudes'][0]['creation_info'] = CreationInfo(author=au, time=tm)
            print("%s%% - Warning: manually assigned a quake CreationInfo (author: %s, time: %s)" % (p5, au, tm))
except Exception as e:
    print('%s%% - Error parsing IRIS local/regional catalog: %s' % (p5, e))

####### GLOBAL ########

try:
#    cat2 += iris.get_events(starttime=t1, endtime=t2, latitude=YOUR_LATITUDE,
#                           longitude=YOUR_LONGITUDE, minmagnitude=5, maxmagnitude=5.59, minradius=12, maxradius=50)
    print('%s%% - Getting global earthquakes larger than M%s...' % (p5, GLOBAL_MIN_MAG))
    cat2 += iris.get_events(starttime=t1, endtime=t2, minmagnitude=GLOBAL_MIN_MAG)

except FDSNNoDataException:
    print('%s%% - No %s+ earthquakes in global database.' % (p5, GLOBAL_MIN_MAG))
except Exception as e:
    print('%s%% - Error querying IRIS database: %s' % (p5, e))

try:
    for evt in cat2:
        evt['event_descriptions'][0]['text'] = TitleCase(evt['event_descriptions'][0]['text'])
        evt['origins'][0]['depth'] = evt['origins'][0]['depth'] / 1000.
        try:
            evt['magnitudes'][0]['creation_info']['author'] = evt['origins'][0]['creation_info']['author'].split(',')[0]
        except TypeError as e:
            au = evt['origins'][0]['creation_info']['author'].split(',')[0]
            tm = evt['origins'][0]['time']
            evt['magnitudes'][0]['creation_info'] = CreationInfo(author=au, time=tm)
            print("%s%% - Warning: manually assigned a quake CreationInfo (author: %s, time: %s)" % (p5, au, tm))
except Exception as e:
    print('%s%% - Error parsing IRIS global catalog: %s' % (p5, e))

print('%s%% - Regional/global IRIS catalog:' % (p6))
print(cat2.__str__(print_all=True))

####### CATALOG WRITING ########

print('%s%% - Writing catalogs. Local count: %s; global count: %s' % (p6, cat.count(), cat2.count()))
cat.write('evtlocal30days.xml', format='QUAKEML')
cat2.write('evtmajor30days.xml', format='QUAKEML')


# put into pandas dataframe and plot seismicity rate
print('%s%% - Creating DataFrame...' % (p6))
times = []
lats = []
lons = []
note = []
deps = []
magnitudes = []
magnitudestype = []
for event in cat:
    if len(event.origins) != 0 and len(event.magnitudes) != 0:
        times.append(event.origins[0].time.datetime)
        lats.append(event.origins[0].latitude)
        lons.append(event.origins[0].longitude)
        note.append(event.event_descriptions[0].text)
        deps.append(event.origins[0].depth)
        magnitudes.append(event.magnitudes[0].mag)
        magnitudestype.append(event.magnitudes[0].magnitude_type)

df = pd.DataFrame({'lat':lats, 'lon':lons, 'depth':deps, 'desc':note, 'mag':magnitudes, 'type':magnitudestype,}, index = times)
df.to_csv('evtlocal30days.csv')

print('%s%% - Creating activity rate figure...' % (p6))
try:
    bins = np.arange(-1,7)
    labels = np.array(["%i - %i"%(i,i+1) for i in bins])
    colors = [cm.hsv(float(i+1)/(len(bins)-1)) for i in bins]
    df['Magnitude_Range'] = pd.cut(df['mag'], bins=bins, labels=False)
    df['Magnitude_Range'] = labels[df['Magnitude_Range']]
    df['Week'] = [di.strftime('%U') for di in df.index]

    rate = pd.crosstab(df.Week, df.Magnitude_Range)
    rate.plot(kind='bar',stacked=True,color=colors)

    plt.tight_layout()
    plt.savefig('evtrate.png',dpi=150)
except Exception as e:
    print('Activity rate figure failed: %s' % e)

##############################################
############# Inventory Creation #############
##############################################

print('%s%% - Creating inventory...' % (p7))
inv = Inventory((Network('AM'),), 'AM')
i = True

try:
    if all(isinstance(stn, basestring) for stn in YOUR_STATIONS): # check iterable for stringiness of all items. Will catch TypeError if some_object is not iterable
        for stn in YOUR_STATIONS:
            stn = stn.upper()
            print('%s%% - Retrieving %s station inventory data from RaspberryShake...' % (p7, stn))
            try:
                sta = read_inventory('https://fdsnws.raspberryshakedata.com/fdsnws/station/1/query?network=AM&station=%s&level=resp&format=xml' % (stn))
                sta.write('sta%s.xml' % stn.upper(), 'STATIONXML')
                print('%s%% - Success. Inventory saved to sta%s.xml for future use.' % (p7, stn))
            except ConnectionError:
                print('%s%% - Could not connect to RaspberryShake FDSN service to download station %s inventory. Using local inventory instead.' % (p7, stn))
            except ValueError:
                print('%s%% - It looks like the online STATIONXML inventory is the wrong version. Trying local sta%s.xml instead...' % (p7, stn))
            except:
                print('%s%% - Unknown error with inventory data. Now looking for sta%s.xml instead...' % (p7, stn))

            try:
                sta = read_inventory('sta%s.xml' % (stn))
                print('%s%% - Found local xml.' % (p7))
            except:
                print('%s%% - No local file found for station %s. Station will not be plotted.' % (p7, stn))
            if i:
                inv = sta
            else:
                inv = inv + sta
            i = False
except Exception as e:
    print('%s%% - Error reading inventory data: %s' % (e))

if inv:
    print(inv)
    inv.write('stainv.xml', 'STATIONXML')
else:
    print('%s%% - No inventory data exists yet. No stations will be plotted' % (p7))
    # must download inventory data in a sc3ml version 0.9 or less, and name it like staRCB43.xml
    # or wait for obspy upgrade that can parse sc3ml version 0.10.
    # You could always download another station's sc3ml in 0.9 format and input your station's specs instead


#############################################################################################################
# LOCAL
# set up a custom basemap, example is taken from basemap users' manual
print('%s%% - Creating local map figure...' % (p8))
fig, ax = plt.subplots(figsize=(12, 12), dpi=150)

# setup albers equal area conic basemap (local)
# lat_1 is first standard parallel.
# lat_2 is second standard parallel.
# lon_0, lat_0 is central point.
m = Basemap(width=1500000, height=1500000,
            resolution='i', projection='tmerc',
            lat_1=YOUR_LATITUDE-10., lat_2=YOUR_LONGITUDE-10, lon_0=YOUR_LONGITUDE, lat_0=YOUR_LATITUDE, ax=ax)

m.drawmapboundary(fill_color='skyblue')
print('%s%% - Drawing coastlines...' % (p8))
m.drawcoastlines(linewidth=0.5)
print('%s%% - Drawing countries...' % (p8))
m.drawcountries()
print('%s%% - Drawing states...' % (p8))
m.drawstates()
m.fillcontinents(color='linen', lake_color='skyblue') # colors
# draw parallels and meridians.
print('%s%% - Drawing grid...' % (p8))
m.drawparallels(np.arange(-80., 81., 10.))
m.drawmeridians(np.arange(-180., 181., 10.))
ax.set_title(u"%s-day seismicity within %s\N{DEGREE SIGN}, colored by date - generated %s" % (DURATION, LOCAL_RADIUS, t2str))

# we need to attach the basemap object to the figure, so that obspy knows about it and reuses it
fig.bmap = m

# now let's plot some data on the custom basemap:
print('%s%% - Generating figure...' % (p8))
cat.plot(fig=fig, show=False, title="", colorbar=False, color='date', legend='lower right', linewidths=0.3, edgecolors='k')
if inv:
    inv.plot(fig=fig, show=False, color_per_network={'AM': (0, 0, 1, 0.2)}, size=80, legend='lower right')

fig.tight_layout()
print('%s%% - Exporting...' % (p8))
plt.savefig('evtlocal30days.png')


############################################################################################################
# GLOBAL
# set up the global map
print('%s%% - Creating global map figure...' % (p9))
fig, ax = plt.subplots(figsize=(16,12), dpi=150)

# hammer global projection, low resolution coastlines and features
m = Basemap(resolution='l', projection='hammer',
            lat_1=0, lat_2=0, lon_0=YOUR_LONGITUDE, lat_0=0, ax=ax)

m.drawmapboundary(fill_color='skyblue')
print('%s%% - Drawing coastlines...' % (p9))
m.drawcoastlines(linewidth=0.3)
print('%s%% - Drawing countries...' % (p9))
m.drawcountries()
m.fillcontinents(color='linen', lake_color='skyblue')
# draw parallels and meridians.
print('%s%% - Drawing grid...' % (p9))
m.drawparallels(np.arange(-90., 90., 30.))
m.drawmeridians(np.arange(-180., 180., 30.))
fig.bmap = m

# plot data on the global map
print('%s%% - Generating figure...' % (p9))
if inv:
    inv.plot(method='basemap', show=False, color_per_network={'AM': (0, 0, 1, 0.2)}, label=False, size=70,
             water_fill_color='skyblue', continent_fill_color='wheat', fig=fig, linewidths=0.3, edgecolors='k')

glbl_title = '%s-day regional and world seismicity, colored by date - generated %s' % (DURATION, t2str)
cat2.plot(method='basemap', color='date', title=glbl_title, fig=fig, linewidths=0.3, edgecolors='k')

fig.autofmt_xdate()

plt.subplots_adjust(top=0.95) # keeping the top of the plot looking okay
print('%s%% - Exporting...' % (p9))
plt.savefig('evtmajor30days.png', bbox_inches='tight') # tight formatting to cut off giant margins

print('%s%% - Done.' % (p10))
