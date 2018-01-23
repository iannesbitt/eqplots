from obspy import read_inventory, read_events
from obspy.clients.fdsn.client import Client
from obspy.core.event.catalog import Catalog
from obspy.core import UTCDateTime
from datetime import timedelta
from mpl_toolkits.basemap import Basemap
import numpy as np
import matplotlib
matplotlib.use('agg')
import matplotlib.pyplot as plt


###########################################################
#                YOUR LAT AND LONG GO HERE                #
###########################################################
# you don't need to be exact, just general lat/lon to center your maps and gather local earthquake data
# if you don't know them, you can go to google maps and click on an uninhabited area near your town, away from roads
# negative latitude indicates southern hemisphere,
# negative longitude indicates western hemisphere.
YOUR_LATITUDE = 45.0
YOUR_LONGITUDE = -70.0
###########################################################
###########################################################


iris = Client("IRIS")
#rpis = Client("https://fdsnws.raspberryshakedata.com/")
t2 = UTCDateTime.now()
#t2 = UTCDateTime(now.year, now.month, now.day)
t1 = t2 - timedelta(days=30)

cat = Catalog()
cat2 = Catalog()
try:
    cat += iris.get_events(starttime=t1, endtime=t2, latitude=YOUR_LATITUDE, longitude=YOUR_LONGITUDE,
                             maxradius=15)
except:
    pass

# the raspberryshake network fdsn
#try:
#    cat += rpis.get_events(starttime=t1, endtime=t2, latitude=44.036114, longitude=-70.439856, maxradius=15)
#except:
#    pass

try:
    cat2 += iris.get_events(starttime=t1, endtime=t2, minmagnitude=6)
except:
    pass
print(cat.__str__(print_all=True))
print(cat2.__str__(print_all=True))

cat.write('evtlocal30days.xml', format='QUAKEML')
cat2.write('evtmajor30days.xml', format='QUAKEML')

# read station metadata
try:
    r06ac = read_inventory('http://raspberryshake.net:8080/fdsnws/station/1/query?network=AM&station=R06AC&level=resp&format=sc3ml')
    r06ac.write('star06ac.xml', 'STATIONXML')
except:
    r06ac = read_inventory('star06ac.xml')
try:
    r35e7 = read_inventory('http://raspberryshake.net:8080/fdsnws/station/1/query?network=AM&station=R35E7&level=resp&format=sc3ml')
    r35e7.write('star35e7.xml', 'STATIONXML')
except:
    r35e7 = read_inventory('star35e7.xml')
try:
    rcb43 = read_inventory('http://raspberryshake.net:8080/fdsnws/station/1/query?network=AM&station=RCB43&level=resp&format=sc3ml')
    rcb43.write('starcb43.xml', 'STATIONXML')
except:
    try:
        rcb43 = read_inventory('starcb43.xml')
    except:
        pass

try:
    inv = r06ac + r35e7 + rcb43
except:
    inv = r06ac + r35e7
print(inv)

inv.write('stainv.xml', 'STATIONXML')

# Set up a custom basemap, example is taken from basemap users' manual
fig, ax = plt.subplots(figsize=(12, 12), dpi=100)

# setup albers equal area conic basemap
# lat_1 is first standard parallel.
# lat_2 is second standard parallel.
# lon_0, lat_0 is central point.
m = Basemap(width=2500000, height=2500000,
            resolution='i', projection='aea',
            lat_1=YOUR_LATITUDE-10., lat_2=YOUR_LONGITUDE-10, lon_0=YOUR_LONGITUDE, lat_0=YOUR_LATITUDE, ax=ax)
#m.etopo()
m.drawmapboundary(fill_color='skyblue')
m.drawcoastlines(linewidth=0.5)
m.drawcountries()
m.drawstates()
m.fillcontinents(color='wheat', lake_color='skyblue')
# draw parallels and meridians.
m.drawparallels(np.arange(-80., 81., 10.))
m.drawmeridians(np.arange(-180., 181., 10.))
ax.set_title("30-day local M 0.1+ seismicity, colored by date - %s" % t2)

# we need to attach the basemap object to the figure, so that obspy knows about
# it and reuses it
fig.bmap = m

# now let's plot some data on the custom basemap:
cat.plot(fig=fig, show=False, title="", colorbar=False, color='date', legend='lower right')
inv.plot(fig=fig, show=False, color_per_network={'AM': (0, 0, 1, 0.2)}, size=80, legend='lower right')

fig.tight_layout()
plt.savefig('evtlocal30days.png')

fig, ax = plt.subplots(figsize=(16,12), dpi=150)

m = Basemap(resolution='l', projection='hammer',
            lat_1=YOUR_LATITUDE-10., lat_2=YOUR_LONGITUDE-10, lon_0=YOUR_LONGITUDE, lat_0=YOUR_LATITUDE, ax=ax)
#m.etopo()
m.drawmapboundary(fill_color='skyblue')
m.drawcoastlines(linewidth=0.5)
m.drawcountries()
m.fillcontinents(color='wheat', lake_color='skyblue')
# draw parallels and meridians.
m.drawparallels(np.arange(-80., 81., 30.))
m.drawmeridians(np.arange(-180., 181., 30.))
fig.bmap = m

inv.plot(method='basemap', show=False, color_per_network={'AM': (0, 0, 1, 0.2)}, label=False, size=70, water_fill_color='skyblue', continent_fill_color='wheat', fig=fig)

cat2.plot(method='basemap', color='date', title='30-day world M 6.0+ seismicity, colored by date - %s' % t2, fig=fig)

fig.autofmt_xdate()

#plt.xticks(rotation=90)

#for tick in ax.get_xticklabels():
#    tick.set_rotation(45)
#fig.tight_layout()
plt.subplots_adjust(top=0.95)
plt.savefig('evtmajor30days.png', bbox_inches='tight')
