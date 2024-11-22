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

path_logo = os.path.join(current_working_directory, "cest_logo.jpeg")

shp_path = os.path.join(current_working_directory, "BAIRROS.shp")

data_path = os.path.join(current_working_directory, "ESCOLAS_LOCATION_NEW.xlsx")

data_semed = os.path.join(current_working_directory, "semed_escolas_loc_adaptado.xlsx")

shp_setor = os.path.join(current_working_directory, "Manaus_setores_CD2022.shp")

demografia_path = os.path.join(current_working_directory, "AGREGADOS_POR_SETORES_CENSITARIOS_MANAUS.xlsx")

m = folium.Map(location=[-3.057334413281103, -59.98600479911497], zoom_start=12.45)

st.title("MAPA DAS ESCOLAS")

st.sidebar.image(path_logo)

st.sidebar.header("Filtre as opções que deseja:")

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

data = pd.read_excel(data_path)

# add marker one by one of state schools on the map
for i in range(0,len(data)):
   folium.Marker(
      location=[data.iloc[i]['Latitude'], data.iloc[i]['Longitude']],
      icon=folium.DivIcon(html=f"""
            <div style="background-color: green; border-radius: 45%; width: 8px; height: 8px; transform: translate(-50%, -50%);"></div>
        """),
      popup=data.iloc[i]['Escola']
   ).add_to(m)


dados_semed = pd.read_excel(data_semed)

# add marker one by one of state schools on the map
for i in range(0,len(dados_semed)):
   folium.Marker(
      location=[dados_semed.iloc[i]['LATITUDE'], dados_semed.iloc[i]['LONGITUDE']],
      icon=folium.DivIcon(html=f"""
            <div style="background-color: blue; border-radius: 45%; width: 8px; height: 8px; transform: translate(-50%, -50%);"></div>
        """),
      popup=dados_semed.iloc[i]['ESCOLA']
   ).add_to(m)

escola = st.sidebar.selectbox('Escolha a escola estadual para adicionar o raio de 1km:', data['SIGEAM_Escola'].unique())

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


escola_m = st.sidebar.selectbox('Escolha a escola municipal para adicionar o raio de 1km:', dados_semed['SIGEAM_ESCOLA'].unique())

if escola_m == 0:
   print(escola_m)
else:
   index = dados_semed.loc[dados_semed['SIGEAM_ESCOLA'] == escola_m].index[0]
   folium.Circle(
    location=[dados_semed.iloc[index]['LATITUDE'], dados_semed.iloc[index]['LONGITUDE']],
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
  coords_estadual = data.loc[data['SIGEAM_Escola'] == escola, ['Latitude', 'Longitude']].values[0]
  coords_municipal = dados_semed.loc[dados_semed['SIGEAM_ESCOLA'] == escola_m, ['LATITUDE', 'LONGITUDE']].values[0]
  
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

manaus_setores = gpd.read_file(shp_setor)

population = pd.read_excel(demografia_path)
population.rename(columns={'CD_setor': 'CD_SETOR'}, inplace=True)
population['CD_SETOR'] = population['CD_SETOR'].astype(str)

resultado = manaus_setores.merge(population, on="CD_SETOR")

local_setor = st.sidebar.multiselect('Escolha o bairro:', ['Lago Azul', 'Nova Cidade', 'Centro',
       'Nossa Senhora Aparecida', 'Praça 14 de Janeiro',
       'Presidente Vargas', 'Cachoeirinha', 'Vila da Prata', 'Compensa',
       'São Jorge', 'Santo Antônio', 'Santo Agostinho', 'São Raimundo',
       'Glória', 'Planalto', 'Alvorada', 'Nova Esperança',
       'Lírio do Vale', 'Redenção', 'Da Paz', 'Dom Pedro I',
       'Ponta Negra', 'Tarumã', 'Japiim', 'Petrópolis', 'Raiz',
       'São Francisco', 'Coroado', 'Vila Buriti', 'São Lázaro', 'Betânia',
       'Crespo', 'Distrito Industrial I', 'Distrito Industrial II',
       'Colônia Oliveira Machado', 'Morro da Liberdade', 'Armando Mendes',
       'Gilberto Mestrinho', 'Colônia Antônio Aleixo', 'Educandos',
       'Santa Luzia', 'Puraquequara', 'Mauazinho', 'Jorge Teixeira',
       'Parque 10 de Novembro', 'Aleixo', 'Adrianópolis', 'Flores',
       'Nossa Senhora das Graças', 'Chapada', 'Cidade Nova',
       'São Geraldo', 'Novo Aleixo', 'Colônia Santo Antônio',
       'Novo Israel', 'Colônia Terra Nova', 'Monte das Oliveiras',
       'Santa Etelvina', 'Cidade de Deus', 'Tarumã-Açu', 'Tancredo Neves',
       'São José Operário', 'Zumbi dos Palmares'])


if (len(local_setor) > 1) or (len(local_setor) == 0):
    print(local_setor)
    populacao_bairro = resultado[["CD_SETOR", "geometry", "V01006"]]
    # Converter para GeoJSON
    geo_json_data = populacao_bairro[['geometry', 'CD_SETOR']].set_index('CD_SETOR').__geo_interface__

    # Adicionar o mapa coroplético
    Choropleth(
        geo_data=geo_json_data,
        name='choropleth',
        data=populacao_bairro,
        columns=['CD_SETOR', 'V01006'],  # Nome da coluna de união e a coluna de valores
        key_on='feature.id',  # Mapeia os dados pela chave (assumindo que 'bairros' é o identificador)
        fill_color='YlOrRd',
        fill_opacity=0.7,
        line_opacity=0.2,
        legend_name='População por Setor Censitario'
    ).add_to(m)

    # Adicionar controles ao mapa
    folium.LayerControl().add_to(m)
else:
    print(local_setor)
    populacao_bairro = resultado.loc[resultado["NM_BAIRRO"] == local_setor[0]]
    populacao_bairro = populacao_bairro[["CD_SETOR", "geometry", "V01006"]]
    # Converter para GeoJSON
    geo_json_data = populacao_bairro[['geometry', 'CD_SETOR']].set_index('CD_SETOR').__geo_interface__

    # Adicionar o mapa coroplético
    Choropleth(
        geo_data=geo_json_data,
        name='choropleth',
        data=populacao_bairro,
        columns=['CD_SETOR', 'V01006'],  # Nome da coluna de união e a coluna de valores
        key_on='feature.id',  # Mapeia os dados pela chave (assumindo que 'bairros' é o identificador)
        fill_color='YlOrRd',
        fill_opacity=0.7,
        line_opacity=0.2,
        legend_name='População por Setor Censitario'
    ).add_to(m)

    # Adicionar controles ao mapa
    folium.LayerControl().add_to(m)

#icon = folium.Icon(color='blue', icon='info-sign')

# Adicionar o primeiro GeoJSON ao mapa
#folium.GeoJson(
#    geojson_data,
#    name='shapefile',
#    style_function=lambda x: {'color': 'blue'}
#).add_to(m)

# Adicionar um controle de camadas
folium.LayerControl().add_to(m)

st_data = st_folium(m, width=1000, height=700)
