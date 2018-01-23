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

YOUR_STATIONS = ('RCB43', 'R06AC', 'R35E7')

###########################################################
#               YOUR LAT AND LONG GO HERE:                #
###########################################################
# you don't need to be exact, just general lat/lon to center your maps and gather local earthquake data
# if you don't know them, you can go to google maps and click on an uninhabited area near your town, away from roads

# negative latitude indicates southern hemisphere
YOUR_LATITUDE = 45.0
# negative longitude indicates western hemisphere
YOUR_LONGITUDE = -70.0

###########################################################
#             End of easily editable variables            #
###########################################################




from obspy import read_inventory, read_events
from obspy.clients.fdsn.client import Client
from obspy.core.event.catalog import Catalog
from obspy.core.inventory.network import Network
from obspy.core.inventory.inventory import Inventory
from obspy.core import UTCDateTime
from datetime import timedelta
from mpl_toolkits.basemap import Basemap
import numpy as np
import matplotlib
matplotlib.use('agg')
import matplotlib.pyplot as plt


iris = Client("IRIS")
t2 = UTCDateTime.now()
t1 = t2 - timedelta(days=30)

cat = Catalog()
cat2 = Catalog()

try:
    cat += iris.get_events(starttime=t1, endtime=t2, latitude=YOUR_LATITUDE,
                           longitude=YOUR_LONGITUDE, maxradius=15)
except:
    pass


try:
    cat2 += iris.get_events(starttime=t1, endtime=t2, minmagnitude=6)
except:
    pass
print(cat.__str__(print_all=True))
print(cat2.__str__(print_all=True))

cat.write('evtlocal30days.xml', format='QUAKEML')
cat2.write('evtmajor30days.xml', format='QUAKEML')

inv = Inventory((Network('AM'),), 'AM')
i = 0

if all(isinstance(stn, basestring) for stn in YOUR_STATIONS): # check iterable for stringiness of all items. Will raise TypeError if some_object is not iterable
    for stn in YOUR_STATIONS:
        try:
            sta = read_inventory('http://raspberryshake.net:8080/fdsnws/station/1/query?network=AM&station=%s&level=resp&format=sc3ml' % stn.upper())
            sta.write('sta%s.xml' % stn.upper(), 'STATIONXML')
            if i < 1:
                inv = sta
            else:
                inv += sta
        except:
            try:
                sta = read_inventory('sta%s.xml' % stn.upper())
                if i < 1:
                    inv = sta
                else:
                    inv += sta
            except:
                pass
    i += 1
else:
    raise TypeError

if inv:
    print(inv)
    inv.write('stainv.xml', 'STATIONXML')
else:
    print('Unable to retrieve inventory data from Raspberry Shake fdsn server. No stations will be plotted')

# LOCAL
# set up a custom basemap, example is taken from basemap users' manual
fig, ax = plt.subplots(figsize=(12, 12), dpi=150)

# setup albers equal area conic basemap (local)
# lat_1 is first standard parallel.
# lat_2 is second standard parallel.
# lon_0, lat_0 is central point.
m = Basemap(width=2500000, height=2500000,
            resolution='i', projection='tmerc',
            lat_1=YOUR_LATITUDE-10., lat_2=YOUR_LONGITUDE-10, lon_0=YOUR_LONGITUDE, lat_0=YOUR_LATITUDE, ax=ax)

m.drawmapboundary(fill_color='skyblue')
m.drawcoastlines(linewidth=0.5)
m.drawcountries()
m.drawstates()
m.fillcontinents(color='wheat', lake_color='skyblue') # colors
# draw parallels and meridians.
m.drawparallels(np.arange(-80., 81., 10.))
m.drawmeridians(np.arange(-180., 181., 10.))
ax.set_title("30-day local M 0.1+ seismicity, colored by date - %s" % t2)

# we need to attach the basemap object to the figure, so that obspy knows about it and reuses it
fig.bmap = m

# now let's plot some data on the custom basemap:
cat.plot(fig=fig, show=False, title="", colorbar=False, color='date', legend='lower right')
if inv:
    inv.plot(fig=fig, show=False, color_per_network={'AM': (0, 0, 1, 0.2)}, size=80, legend='lower right')

fig.tight_layout()
plt.savefig('evtlocal30days.png')


# GLOBAL
# set up the global map
fig, ax = plt.subplots(figsize=(16,12), dpi=150)

# hammer global projection, low resolution coastlines and features
m = Basemap(resolution='l', projection='hammer',
            lat_1=YOUR_LATITUDE-10., lat_2=YOUR_LONGITUDE-10, lon_0=YOUR_LONGITUDE, lat_0=YOUR_LATITUDE, ax=ax)

m.drawmapboundary(fill_color='skyblue')
m.drawcoastlines(linewidth=0.5)
m.drawcountries()
m.fillcontinents(color='wheat', lake_color='skyblue')
# draw parallels and meridians.
m.drawparallels(np.arange(-80., 81., 30.))
m.drawmeridians(np.arange(-180., 181., 30.))
fig.bmap = m

# plot data on the global map
if inv:
    inv.plot(method='basemap', show=False, color_per_network={'AM': (0, 0, 1, 0.2)}, label=False, size=70, water_fill_color='skyblue', continent_fill_color='wheat', fig=fig)

cat2.plot(method='basemap', color='date', title='30-day world M 6.0+ seismicity, colored by date - %s' % t2, fig=fig)

fig.autofmt_xdate()

plt.subplots_adjust(top=0.95) # keeping the top of the plot looking okay
plt.savefig('evtmajor30days.png', bbox_inches='tight') # tight formatting to cut off giant margins
