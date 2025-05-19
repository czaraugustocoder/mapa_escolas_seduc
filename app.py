import folium
from folium import Choropleth
from folium import Choropleth, GeoJson, LayerControl
import geopandas as gpd
import streamlit as st
from streamlit_folium import st_folium
import pandas as pd
import math
import os

st.set_page_config(page_title="MAPA",
                   layout="wide"
)

current_working_directory = os.getcwd()

shp_path = os.path.join(current_working_directory, "BAIRROS.shp")

path_logo = os.path.join(current_working_directory, "cest_logo.jpeg")

data_path = os.path.join(current_working_directory, "ESCOLAS_LOCATION_NEW.xlsx")

data_semed = os.path.join(current_working_directory, "semed_escolas_loc_adaptado.xlsx")

m = folium.Map(location=[-3.057334413281103, -59.98600479911497], zoom_start=12.45)

st.title("MAPA DAS ESCOLAS - MANAUS")

st.write("Mapa interativo das escolas estaduais (cor verde) e municipais (cor azul) da cidade de Manaus")

st.sidebar.image(path_logo, use_column_width=True)

st.sidebar.header("Selecione as opções de bairros que deseja:")

data = pd.read_excel(data_path)

data.rename(columns={
    'Latitude': 'LATITUDE',
    'Longitude': 'LONGITUDE',
    'Escola': 'ESCOLA',
    'SIGEAM_Escola': 'SIGEAM_ESCOLA',
}, inplace=True)

dados_semed = pd.read_excel(data_semed)

# add marker one by one of state schools on the map
for i in range(0,len(data)):
   folium.Marker(
      location=[data.iloc[i]['LATITUDE'], data.iloc[i]['LONGITUDE']],
      icon=folium.DivIcon(html=f"""
            <div style="background-color: green; border-radius: 45%; width: 8px; height: 8px; transform: translate(-50%, -50%);"></div>
        """),
      popup=data.iloc[i]['SIGEAM_ESCOLA']
   ).add_to(m)

# add marker one by one of state schools on the map
for i in range(0,len(dados_semed)):
   folium.Marker(
      location=[dados_semed.iloc[i]['LATITUDE'], dados_semed.iloc[i]['LONGITUDE']],
      icon=folium.DivIcon(html=f"""
            <div style="background-color: blue; border-radius: 45%; width: 8px; height: 8px; transform: translate(-50%, -50%);"></div>
        """),
      popup=dados_semed.iloc[i]['SIGEAM_ESCOLA']
   ).add_to(m)


# Ler o shapefile usando geopandas
gdf = gpd.read_file(shp_path)

gdf = gdf.to_crs("EPSG:4326")

zona = st.sidebar.multiselect('Escolha a zona:', gdf['ZONAS'].unique())

if (len(zona) > 1) or (len(zona) == 0):
   print(zona)
else:
    print(zona)
    zona_shp = gdf.loc[gdf['ZONAS']  ==  zona[0]]
    geojson_zona = zona_shp.to_json()
    # Adicionar o segundo GeoJSON ao mapa com uma cor diferente
    folium.GeoJson(
        geojson_zona,
        name='shapefile',
        style_function=lambda x: {'color': 'yellow'}
    ).add_to(m)

local = st.sidebar.multiselect('Escolha o bairro:', gdf['NOME_BAIRR'].unique())

if (len(local) > 1) or (len(local) == 0):
   print(local)
else:
    print(local)
    bairro_shp = gdf.loc[gdf['NOME_BAIRR']  ==  local[0]]
    geojson_bairro = bairro_shp.to_json()
    # Adicionar o segundo GeoJSON ao mapa com uma cor diferente
    folium.GeoJson(
        geojson_bairro,
        name='shapefile',
        style_function=lambda x: {'color': 'purple'}
    ).add_to(m)


st.sidebar.header("Selecione as opções de escolas que deseja:")

selecao1 = st.sidebar.radio("Escolha a rede:",["estadual", "municipal"])

if selecao1 == "estadual":
   data1 = data
elif selecao1 == "municipal":
   data1 = dados_semed

escola = st.sidebar.selectbox('Escolha a escola para adicionar o raio de 1km: ', data1['SIGEAM_ESCOLA'].unique())

selecao2 = st.sidebar.radio("Escolha a rede:",["municipal", "estadual"])

if selecao2 == "municipal":
   data2 = dados_semed
elif selecao2 == "estadual":
   data2 = data

escola_m = st.sidebar.selectbox('Escolha a escola para adicionar o raio de 1km:', data2['SIGEAM_ESCOLA'].unique())

if escola == 0:
   print(escola)
elif (escola != 0) and (escola_m == 0):
   index = data1.loc[data1['SIGEAM_ESCOLA'] == escola].index[0]
   folium.Circle(
    location=[data1.iloc[index]['LATITUDE'], data1.iloc[index]['LONGITUDE']],
    radius=1000,
    color='red',
    fill=True,
    fill_color='lightblue'
    ).add_to(m)

if escola_m == 0:
   print(escola_m)
elif (escola_m != 0) and (escola == 0):
   index = data2.loc[data2['SIGEAM_ESCOLA'] == escola_m].index[0]
   folium.Circle(
    location=[data2.iloc[index]['LATITUDE'], data2.iloc[index]['LONGITUDE']],
    radius=1000,
    color='red',
    fill=True,
    fill_color='lightblue'
    ).add_to(m)
   

# Função para calcular a distância usando a fórmula de Haversine
def haversine(coord1, coord2):
    # Raio da Terra em quilômetros
    R = 6371.0
    
    # Converter latitude e longitude de graus para radianos
    lat1, lon1 = math.radians(coord1[0]), math.radians(coord1[1])
    lat2, lon2 = math.radians(coord2[0]), math.radians(coord2[1])
    
    # Diferenças entre as coordenadas
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    
    # Aplicar a fórmula de Haversine
    a = math.sin(dlat / 2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    
    # Distância em quilômetros
    distancia = R * c
    return distancia


if ((escola != 0) and (escola_m != 0)):
  # Obtenha as coordenadas das escolas selecionadas
  coords_estadual = data1.loc[data1['SIGEAM_ESCOLA'] == escola, ['LATITUDE', 'LONGITUDE']].values[0]
  coords_municipal = data2.loc[data2['SIGEAM_ESCOLA'] == escola_m, ['LATITUDE', 'LONGITUDE']].values[0]
  
  # Calcular a distância entre as duas escolas usando Haversine
  distancia = haversine(coords_estadual, coords_municipal)
  
  # Adiciona uma linha entre as duas escolas
  folium.PolyLine([coords_estadual, coords_municipal], color="red", weight=2.5, opacity=0.8).add_to(m)

  # Calcula o ponto médio para exibir a distância
  ponto_medio = [(coords_estadual[0] + coords_municipal[0]) / 2, (coords_estadual[1] + coords_municipal[1]) / 2]
  
  # Adiciona um marcador no ponto médio com a distância
  folium.Marker(
      location=ponto_medio,
      icon=folium.DivIcon(html=f'<div style="font-size: 12pt; color: black;">{distancia:.2f} km</div>')
  ).add_to(m)
   
st_folium(m, width=925, returned_objects=[])
