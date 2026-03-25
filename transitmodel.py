import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as colors
import pandas as pd
import geopandas as gpd
import osmnx as ox
from shapely.geometry import Point
from collections import Counter

root = '/Users/Emmanuel Olusheki/Downloads/Spring_2025_Stop_Summary_(Bus).csv'
df_stops = pd.read_csv(root)
coords = np.array([df_stops['Lat'],
                   df_stops['Lon']])

def haversine(lat1, lon1, lat2, lon2):
    """
    Uses haversine formula to calculate the distance 
    between 2 points given lon and lat (miles)
    """
    dlon = (np.pi/180)*(lon2 - lon1)
    dlat = (np.pi/180)*(lat2 - lat1)
    lat1 = lat1 * (np.pi/180)
    lat2 = lat2 * (np.pi/180)
    a = np.sin(dlat/2)**2 + (np.cos(lat1)*np.cos(lat2)*(np.sin(dlon/2)**2))
    r = 3959 #radius of the Earth in miles
    d = 2*r*np.arcsin(np.sqrt(a))

    return d # miles

def find_nearest_stop(lat, lon):
    nearest_stop = None
    near_stops = np.zeros([2,len(coords[0])])
    epsilon = 0.0005 # Degrees
    c = 0
    while nearest_stop == None:
        lat_max = lat + epsilon
        lat_min = lat - epsilon
        lon_max = lon + epsilon
        lon_min = lon - epsilon
        for i in range(len(coords[0])):
            if lat_min <= coords[0,i] <= lat_max and lon_min <= coords[1,i] <= lon_max:
                # print(coords[0,i])
                stop_match = coords[:, i]
                near_stops[:,c] = stop_match
                c += 1
                nearest_stop = 1
            else:
                epsilon += 0.005 # Degrees
    near_stops = np.trim_zeros(near_stops)
    # print(near_stops)

    # Calculates all distances within range
    dist = []
    for k in range(len(near_stops[0])):
        dist.append(haversine(lat, lon, near_stops[0,k], near_stops[1,k]))
    dist = np.array(dist)
    
    # Finds lowest distance
    # distance, nearest_stop = enumerate(dist)
    mindist_index = np.argmin(dist)
    mindist = dist[mindist_index]
    return mindist_index, mindist

def walking_time(lat, lon):
    mindist = find_nearest_stop(lat, lon)[1]
    walkingtime = mindist*20 # assumes a 20-minute mile when walking
    return walkingtime

# Plotting
city = 'Philadelphia'
geometry = [Point(xy) for xy in zip(df_stops['Lon'], df_stops['Lat'])]
gdf_stops = gpd.GeoDataFrame(df_stops, geometry=geometry)
df_stops.crs = 'EPSG:4326'

philadelphia = ox.geocode_to_gdf(city)
philadelphia.crs = 4326

y = np.linspace(-76, -74, 90)
x = np.linspace(39, 41, 90)
X,Y = np.meshgrid(x,y)

walkingtime_array = np.zeros((len(x),len(y)))

for i in range(len(x)):
    for j in range(len(y)):
         walkingtime_array[i,j] = walking_time(x[i],y[j])

# get the water bodies
left, bottom, right, top = philadelphia.total_bounds
bbox = (-75.858, 39.804, -74.7, 40.3474)
poly = ox.utils_geo.bbox_to_poly(bbox)
water = ox.features_from_polygon(poly, tags={'natural': 'water'})

water_color = 'blue'
land_color = '#aaaaaa'
marker_color = '#F14728'
chalk = '#f0f7e0'

# figure 1 - bus stop plot
fig, ax = ox.plot_footprints(water, bbox=bbox,
                             color=water_color, bgcolor= chalk,
                             show=False, close=False, alpha = .5,
                             figsize=[6, 6])
philadelphia.plot(ax=ax, zorder=0, fc=land_color)
ax.set_title('Bus stops in Philly', fontsize = 18, color = 'white')
gdf_stops.plot(ax=ax, alpha = 0.2, markersize = 0.5, color = 'magenta')
philadelphia.plot(ax=ax, color = 'none', edgecolor = 'k')
fig.set_facecolor('white')
fig.tight_layout()

# figure 2 - contour plot
f, ax2 = ox.plot_footprints(water, bbox=bbox,
                             color=water_color, bgcolor= 'w',
                             show=False, close=False, alpha = .5,
                             figsize=[6, 6])
bounds = np.linspace(0, 45, 9)
norm = colors.BoundaryNorm(boundaries = bounds, ncolors = 256)
cs = ax2.pcolormesh(y, x, walkingtime_array, alpha = .5, norm=norm, cmap = 'viridis_r')
# ax2 = philadelphia.plot(ax=ax2, zorder=3, fc=land_color)
# f, ax2 = plt.subplots(1,1,figsize=(10,10))
f.suptitle('Walking time to nearest bus stop, minutes', color = 'white')
f.tight_layout()
f.set_facecolor('white')
cb = f.colorbar(cs, label = "Minutes")
cb.set_label('Minutes', color = 'w')
cb.ax.yaxis.set_tick_params(color='w')
plt.setp(plt.getp(cb.ax.axes, 'yticklabels'), color='w')
ax2 = philadelphia.plot(ax=ax2, color = 'none', edgecolor = 'k')
# gdf_stops.plot(ax=ax2, alpha = 0.2, markersize = 0.5, color = marker_color)
# ax.axis('off')

plt.show()