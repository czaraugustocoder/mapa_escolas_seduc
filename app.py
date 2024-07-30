import folium
import geopandas as gpd
import streamlit as st
from streamlit_folium import st_folium
import pandas as pd
import os

current_working_directory = os.getcwd()

path_logo = os.path.join(current_working_directory, "cest_logo.jpeg")

shp_path = os.path.join(current_working_directory, "Bairro_de_Manaus__SEMEF_.shp")

data_path = os.path.join(current_working_directory, "CDE7.xlsx")

m = folium.Map(location=[-3.057334413281103, -59.98600479911497], zoom_start=11.45)

st.title("MAPA DAS ESCOLAS")

st.sidebar.image(path_logo)

st.sidebar.header("Filtre as opções que deseja:")

# Ler o shapefile usando geopandas
gdf = gpd.read_file(shp_path)

local = st.sidebar.multiselect('Escolha o bairro:', gdf['nome'].unique())

if (len(local) > 1) or (len(local) == 0):
   print(local)
else:
    print(local)
    bairro_shp = gdf.loc[gdf['nome']  ==  local[0]]
    geojson_bairro = bairro_shp.to_json()
    # Adicionar o segundo GeoJSON ao mapa com uma cor diferente
    folium.GeoJson(
        geojson_bairro,
        name='shapefile',
        style_function=lambda x: {'color': 'purple'}
    ).add_to(m)

data = pd.read_excel(data_path)

# add marker one by one on the map
for i in range(0,len(data)):
   folium.Marker(
      location=[data.iloc[i]['Latitude'], data.iloc[i]['Longitude']],
      icon=folium.DivIcon(html=f"""
            <div style="background-color: green; border-radius: 45%; width: 8px; height: 8px; transform: translate(-50%, -50%);"></div>
        """),
      popup=data.iloc[i]['Escola']
   ).add_to(m)

escola = st.sidebar.selectbox('Escolha a escola para adicionar o raio de 1km:', data['SIGEAM_Escola'].unique())

if escola == 0:
   print(escola)
else:
   index = data.loc[data['SIGEAM_Escola'] == escola].index[0]
   folium.Circle(
    location=[data.iloc[index]['Latitude'], data.iloc[index]['Longitude']],
    radius=1000,
    color='red',
    fill=True,
    fill_color='lightblue'
    ).add_to(m)

#icon = folium.Icon(color='blue', icon='info-sign')

# Adicionar o primeiro GeoJSON ao mapa
#folium.GeoJson(
#    geojson_data,
#    name='shapefile',
#    style_function=lambda x: {'color': 'blue'}
#).add_to(m)

# Adicionar um controle de camadas
folium.LayerControl().add_to(m)

st_data = st_folium(m, width=600, height=400)
