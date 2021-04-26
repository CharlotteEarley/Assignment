%matplotlib notebook

import geopandas as gpd
import matplotlib.pyplot as plt
from cartopy.feature import ShapelyFeature
import cartopy.crs as ccrs
import matplotlib.patches as mpatches
import matplotlib.lines as mlines

plt.ion()

def generate_handles(labels, colors, edge='k', alpha=1):
    lc = len(colors)  # get the length of the color list
    handles = []
    for i in range(len(labels)):
        handles.append(mpatches.Rectangle((0, 0), 1, 1, facecolor=colors[i % lc], edgecolor=edge, alpha=alpha))
    return handles

def scale_bar(ax, location=(0.92, 0.95)):
    llx0, llx1, lly0, lly1 = ax.get_extent(ccrs.PlateCarree())
    sbllx = (llx1 + llx0) / 2
    sblly = lly0 + (lly1 - lly0) * location[1]

    tmc = ccrs.TransverseMercator(sbllx, sblly)
    x0, x1, y0, y1 = ax.get_extent(tmc)
    sbx = x0 + (x1 - x0) * location[0]
    sby = y0 + (y1 - y0) * location[1]

    plt.plot([sbx, sbx - 20000], [sby, sby], color='k', linewidth=9, transform=tmc)
    plt.plot([sbx, sbx - 10000], [sby, sby], color='k', linewidth=6, transform=tmc)
    plt.plot([sbx-10000, sbx - 20000], [sby, sby], color='w', linewidth=6, transform=tmc)

    plt.text(sbx, sby-4500, '20 km', transform=tmc, fontsize=8)
    plt.text(sbx-12500, sby-4500, '10 km', transform=tmc, fontsize=8)
    plt.text(sbx-24500, sby-4500, '0 km', transform=tmc, fontsize=8)

outline = gpd.read_file('BangladeshData/bgd_adm_bbs_20201113_shp/BGDoutline.shp')

#=============================================================================================================
ward = gpd.read_file('BangladeshData/bgd_adm_bbs_20201113_shp/BGDward.shp')
water = gpd.read_file('BangladeshData/bgd_watcrsa_1m_iscgm/bgd_watcrsa_1m_iscgm.shp')
towns = gpd.read_file('BangladeshData/bgd_majtowns/bgd_majtowns.shp')
#=============================================================================================================
myFig = plt.figure(figsize=(10, 10))  

myCRS = ccrs.UTM(29)  

ax = plt.axes(projection=ccrs.Mercator())  
#=============================================================================================================
outline_feature = ShapelyFeature(outline['geometry'], myCRS, edgecolor='k', facecolor='w')
xmin, ymin, xmax, ymax = outline.total_bounds
ax.add_feature(outline_feature) 

ax.set_extent([xmin, xmax, ymin, ymax], crs=myCRS) # because total_bounds gives output as xmin, ymin, xmax, ymax,
#=============================================================================================================
num_ward = len(ward.ADM1_EN.unique())
print('Number of unique features: {}'.format(num_ward)) 
#=============================================================================================================
county_colors = ['palegreen', 'chartreuse', 'springgreen', 'cyan', 'lime', 'turquoise', 'aqua', 'deepskyblue']

county_names = list(ward.ADM1_EN.unique())
county_names.sort() # sort the counties alphabetically by name

for i, name in enumerate(county_names):
    feat = ShapelyFeature(ward['geometry'][ward['ADM1_EN'] == name], myCRS, 
                          edgecolor='k',
                          facecolor=county_colors[i],
                          linewidth=1,
                          alpha=0.25)
    ax.add_feature(feat)
#=============================================================================================================
water_feat = ShapelyFeature(water['geometry'], myCRS, 
                            edgecolor='mediumblue', 
                            facecolor='mediumblue',
                            linewidth=1)
ax.add_feature(water_feat)

town_handle = ax.plot(towns.geometry.x, towns.geometry.y, 's', color='0.5', ms=6, transform=myCRS)
#=============================================================================================================
county_handles = generate_handles(ward.ADM1_EN.unique(), county_colors, alpha=0.25)

water_handle = generate_handles(['Lakes'], ['mediumblue'])

nice_names = [name.title() for name in county_names]

handles = county_handles + water_handle  + town_handle
labels = nice_names + ['Lakes', 'Towns']

leg = ax.legend(handles, labels, title='Legend', title_fontsize=14, 
                 fontsize=12, loc='upper left', frameon=True, framealpha=1)

#=============================================================================================================
gridlines = ax.gridlines(draw_labels=True,
                         xlocs=[-8, -7.5, -7, -6.5, -6, -5.5], 
                         ylocs=[54, 54.5, 55, 55.5])
gridlines.left_labels = False # turn off the left-side labels
gridlines.bottom_labels = False # turn off the bottom labels
ax.set_extent([xmin, xmax, ymin, ymax], crs=myCRS) # set the extent to the boundaries of the NI outline
#=============================================================================================================
for i, row in towns.iterrows():
    x, y = row.geometry.x, row.geometry.y # get the x,y location for each town
    plt.text(x, y, row['nam'].title(), fontsize=8, transform=myCRS) # use plt.text to place a label at x,y
#=============================================================================================================
scale_bar(ax)
#=============================================================================================================
myFig.savefig('mapChar1.png', bbox_inches='tight', dpi=300)
