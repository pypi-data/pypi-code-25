import folium
import csv
from folium.plugins import MarkerCluster

map_icmp = folium.Map(location=[45.523, -122.675],
                      zoom_start=2)

with open('python_scripts/base_data.txt') as tsv:
    for row in csv.reader(tsv, delimiter='\t'):
        name = row[0]
        try:
            x = float(row[1])
            y = float(row[2])
            print(" %s " % name)
            folium.Marker([x, y], popup=name).add_to(map_icmp)
        except ValueError:
            pass

map_icmp.save('map_icmp.html')
