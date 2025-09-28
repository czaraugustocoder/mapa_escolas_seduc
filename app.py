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

data_semed = os.path.join(current_working_directory, "semed_escolas_loc_adaptado_novo.xlsx")

m = folium.Map(location=[-3.057334413281103, -59.98600479911497], zoom_start=12.45)

st.title("MAPA DAS ESCOLAS - MANAUS")

st.write("Mapa interativo das escolas estaduais (cor azul) e municipais (cor laranja) da cidade de Manaus")

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
      icon=folium.DivIcon(html="""
            <div style="background-color: blue; border-radius: 45%; width: 10px; height: 10px; transform: translate(-50%, -50%);"></div>
        """),
        popup=folium.Popup(
            f"<div style='font-size:14px; width:220px;'><b>Escola:</b> {data.iloc[i]['SIGEAM_ESCOLA']}<br><b>Ensinos Ofertados:</b> {data.iloc[i]['ENSINO-OFERTADO']}</div>",  
            max_width=300, min_width=200
        )
   ).add_to(m)

# add marker one by one of state schools on the map
for i in range(0,len(dados_semed)):
   folium.Marker(
      location=[dados_semed.iloc[i]['LATITUDE'], dados_semed.iloc[i]['LONGITUDE']],
      icon=folium.DivIcon(html="""
            <div style="background-color: orange; border-radius: 45%; width: 10px; height: 10px; transform: translate(-50%, -50%);"></div>
        """),
        popup=folium.Popup(
            f"<div style='font-size:14px; width:220px;'><b>Escola:</b> {dados_semed.iloc[i]['SIGEAM_ESCOLA']}<br><b>Ensinos Ofertados:</b> {dados_semed.iloc[i]['ENSINO-OFERTADO']}</div>",  
            max_width=300, min_width=200
        )
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

num_raio = st.sidebar.number_input("Digite o valor do raio (em metros)", min_value=0, max_value=3000, value=1000)

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
    radius=num_raio,
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
    radius=num_raio,
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

st.sidebar.header("Selecione o distrito que deseja:")

escola_encaminha = st.sidebar.selectbox('Escolha o distrito para verificar o encaminhamento', [0, "D6", "D7", "D5", "D4", "D3", "D2", "D1"])

D6 = [
    (1382, 1374),
    (1382, 77),
    (1382, 1474),
    (1505, 78),
    (1505, 1474),
    (6228, 70),
    (7440, 1474),
    (675, 77),
    (1108, 79),
    (1125, 79),
    (1125, 83),
    (1321, 81),
    (1612, 79),
    (6226, 81),
    (6227, 81),
    (7792, 7240),
    (669, 69),
    (674, 84),
    (1046, 80),
    (1109, 78),
    (1110, 73),
    (1123, 84),
    (1124, 1283),
    (1201, 1617),
    (1333, 75),
    (1351, 70),
    (1386, 7216),
    (1420, 1560),
    (1470, 75),
    (1470, 81),
    (1484, 1283),
    (1510, 70),
    (1511, 6294),
    (1511, 1617),
    (1511, 69),
    (1652, 69),
    (1656, 77),
    (1687, 1375),
    (1692, 6520),
    (6299, 69),
    (6299, 1617),
    (6511, 72),
    (6519, 7216),
    (6519, 1617),
    (6652, 7216),
    (7737, 72),
    (7796, 84),
    (9817, 78),
    (1508, 1560)
]

D7 = [
    (8494, 7466),
    (8494, 9111),
    (8494, 76),
    (651, 1481),
    (676, 1481),
    (1125, 1514),
    (1385, 6525),
    (1388, 82),
    (1405, 76),
    (1418, 7239),
    (6226, 1514),
    (6227, 1514),
    (6534, 7421),
    (6888, 7221),
    (6888, 1356),
    (6967, 1507),
    (6967, 76),
    (7052, 9731),
    (7436, 6525),
    (7437, 1516),
    (7439, 9302),
    (7447, 7241),
    (7791, 7221),
    (7792, 7241),
    (7792, 1389),
    (7792, 7238),
    (7794, 82),
    (8667, 1516),
    (8667, 9302),
    (8667, 82),
    (8667, 7516),
    (9735, 1507),
    (9735, 8671),
    (1381, 74),
    (759, 76),
    (760, 76),
    (791, 76),
    (827, 1507),
    (835, 82),
    (837, 1507),
    (1226, 9111),
    (6502, 1507),
    (7736, 1507)
]

D5 = [
    (1320, 1378),
    (1320, 1378),
    (1320, 1378),
    (612, 9610),
    (612, 9610),
    (615, 1377),
    (615, 1377),
    (616, 6486),
    (616, 162),
    (617, 164),
    (617, 164),
    (617, 164),
    (618, 1383),
    (618, 1383),
    (618, 1383),
    (619, 1376),
    (619, 1376),
    (620, 101),
    (620, 101),
    (621, 100),
    (621, 95),
    (623, 164),
    (623, 164),
    (623, 164),
    (624, 101),
    (624, 101),
    (626, 1506),
    (626, 166),
    (626, 6486),
    (626, 1506),
    (627, 100),
    (627, 101),
    (747, 121),
    (747, 121),
    (747, 121),
    (1147, 164),
    (1147, 164),
    (1147, 1376),
    (1149, 7807),
    (1149, 1284),
    (1149, 1284),
    (1151, 1284),
    (1151, 1284),
    (1151, 9610),
    (1156, 1515),
    (1156, 1515),
    (1159, 1515),
    (1206, 161),
    (1206, 161),
    (1280, 166),
    (1280, 166),
    (1352, 1377),
    (1352, 1377),
    (1439, 167),
    (1439, 167),
    (1482, 1282),
    (1482, 1282),
    (1508, 1282),
    (1508, 1282),
    (1671, 164),
    (1671, 164),
    (1671, 164),
    (1671, 164),
    (6232, 1282),
    (6232, 1282),
    (6898, 161),
    (6898, 161),
    (6898, 161),
    (7220, 1515),
    (7220, 1515),
    (7304, 1377),
    (7304, 166),
    (9411, 121),
    (606, 7740),
    (606, 168),
    (606, 168),
    (631, 163),
    (631, 163),
    (631, 163),
    (638, 168),
    (638, 168),
    (638, 1378),
    (639, 163),
    (639, 163),
    (639, 163),
    (1142, 1378),
    (1142, 1378),
    (1143, 1284),
    (1152, 1378),
    (1152, 168),
    (1153, 9610),
    (1153, 9610),
    (1153, 164),
    (1153, 164),
    (1153, 164),
    (1153, 9610),
    (1153, 9610),
    (1153, 1376),
    (1203, 7740),
    (1203, 7740),
    (1203, 168),
    (1204, 1378),
    (1204, 1378),
    (1204, 1378),
    (1204, 1378),
    (1205, 6522),
    (1205, 7740),
    (1208, 7442),
    (1208, 7442),
    (1209, 1284),
    (1209, 1284),
    (1210, 168),
    (1210, 1378),
    (1210, 1378),
    (1210, 1378),
    (1329, 168),
    (1332, 1284),
    (1332, 1284),
    (1387, 6486),
    (1387, 6486),
    (1552, 163),
    (1552, 163),
    (1557, 1376),
    (1557, 6486),
    (1557, 1376),
    (1557, 6486),
    (1644, 6522),
    (1644, 6522),
    (6234, 7809),
    (6234, 9610),
    (6234, 9610),
    (6250, 6522),
    (6270, 168),
    (6279, 9924),
    (6279, 9924),
    (6279, 9924),
    (6291, 1506),
    (6298, 6486),
    (6298, 6486),
    (6344, 7442),
    (6503, 7807),
    (6503, 7807),
    (7215, 1506),
    (7215, 1506),
    (7215, 6486),
    (8087, 7809),
    (8680, 1378),
    (8680, 1378),
    (9678, 168),
    (9678, 168),
    (9678, 168),
    (9726, 1378),
    (9726, 1284),
    (9726, 168),
    (9727, 1376),
    (9727, 9610),
    (9727, 1377),
    (9727, 6486),
    (804, 7442),
    (829, 7442),
    (1179, 7442),
    (1179, 1506),
    (1182, 168),
    (1182, 168),
    (1196, 1506)
]

D4 = [
    (8086, 159),
    (704, 21),
    (704, 21),
    (710, 22),
    (714, 91),
    (720, 170),
    (720, 170),
    (724, 92),
    (724, 92),
    (724, 93),
    (724, 93),
    (726, 93),
    (726, 93),
    (726, 93),
    (726, 93),
    (727, 92),
    (727, 92),
    (729, 158),
    (732, 159),
    (733, 93),
    (733, 158),
    (735, 94),
    (736, 158),
    (1161, 176),
    (1161, 176),
    (1170, 157),
    (1328, 86),
    (1328, 157),
    (1478, 87),
    (1478, 87),
    (1479, 24),
    (1606, 169),
    (1673, 154),
    (1673, 169),
    (1673, 155),
    (6236, 170),
    (6236, 179),
    (785, 158),
    (835, 158),
    (836, 8117),
    (6221, 8117)
]

D3 = [
    (570, 127),
    (576, 147),
    (576, 147),
    (579, 98),
    (579, 98),
    (585, 138),
    (588, 150),
    (588, 150),
    (588, 148),
    (655, 130),
    (655, 130),
    (671, 151),
    (671, 151),
    (673, 123),
    (673, 123),
    (677, 130),
    (725, 147),
    (1171, 130),
    (1171, 130),
    (1504, 98),
    (1504, 98),
    (1504, 98),
    (6231, 125),
    (6231, 127),
    (6231, 127),
    (6286, 7),
    (6286, 7),
    (6530, 130),
    (6530, 130),
    (683, 23),
    (683, 23),
    (687, 8),
    (687, 8),
    (699, 11),
    (699, 11),
    (701, 6238),
    (701, 6238),
    (701, 151),
    (701, 151),
    (703, 9),
    (704, 23),
    (707, 9),
    (708, 5),
    (708, 6),
    (708, 6238),
    (708, 5),
    (710, 25),
    (710, 25),
    (710, 25),
    (729, 16),
    (1169, 6238),
    (1169, 6238),
    (1169, 8),
    (1312, 9823),
    (1312, 25),
    (1368, 10),
    (1368, 10),
    (1467, 151),
    (1467, 151),
    (6343, 151),
    (7045, 9),
    (7045, 17),
    (7790, 5),
    (7790, 6238),
    (8494, 151),
    (8494, 151),
    (659, 151),
    (760, 152),
    (763, 151),
    (1181, 152),
    (1181, 151),
    (1185, 152),
    (1185, 152),
    (1193, 152),
    (1576, 152),
    (1576, 151),
    (7109, 151)
]

D2 = [
    (112, 109),
    (112, 1308),
    (112, 107),
    (112, 109),
    (112, 1308),
    (112, 107),
    (580, 118),
    (580, 118),
    (584, 144),
    (584, 144),
    (748, 41),
    (749, 48),
    (749, 48),
    (749, 48),
    (749, 40),
    (749, 40),
    (749, 48),
    (749, 34),
    (751, 39),
    (752, 34),
    (752, 41),
    (752, 34),
    (757, 40),
    (757, 40),
    (963, 45),
    (963, 45),
    (1129, 41),
    (1130, 39),
    (1130, 39),
    (1130, 39),
    (1131, 108),
    (1131, 6247),
    (1131, 108),
    (1131, 6247),
    (1132, 33),
    (1132, 33),
    (1133, 102),
    (1133, 102),
    (1133, 144),
    (1133, 144),
    (1134, 144),
    (1134, 144),
    (1136, 117),
    (1136, 117),
    (1137, 111),
    (1137, 111),
    (1137, 104),
    (1137, 34),
    (1138, 144),
    (1138, 10076),
    (1372, 38),
    (1372, 38),
    (1476, 120),
    (1476, 116),
    (1476, 120),
    (1476, 116),
    (6229, 144),
    (6229, 144),
    (6510, 119),
    (8086, 122),
    (7303, 122),
    (7303, 122),
    (1160, 102)
]

D1 = [
    (68, 49),
    (68, 49),
    (564, 135),
    (564, 135),
    (570, 140),
    (570, 140),
    (573, 143),
    (573, 141),
    (573, 143),
    (573, 141),
    (576, 50),
    (576, 63),
    (576, 50),
    (576, 63),
    (582, 28),
    (582, 52),
    (725, 63),
    (725, 63),
    (1127, 44),
    (1127, 44),
    (1127, 42),
    (1127, 44),
    (1672, 43),
    (1672, 139),
    (1672, 139),
    (8086, 50),
    (1467, 54),
    (7082, 1322),
    (7082, 55),
    (747, 1322)
]

if (escola_encaminha == 0):
  print("nada")

elif (escola_encaminha == "D1"):
  print("distrito selecionado")
  for semed, seduc in D1:
    print(semed, seduc)
    try:
      # Obtenha as coordenadas das escolas selecionadas
      coords_estadual = data.loc[data['SIGEAM'] == seduc, ['LATITUDE', 'LONGITUDE']].values[0]
      coords_municipal = dados_semed.loc[dados_semed['SIGEAM'] == semed, ['LATITUDE', 'LONGITUDE']].values[0]
      
      # Calcular a distância entre as duas escolas usando Haversine
      distancia = haversine(coords_estadual, coords_municipal)
      
      # Adiciona uma linha entre as duas escolas
      folium.PolyLine([coords_estadual, coords_municipal], color="red", weight=2.5, opacity=0.8).add_to(m)
      print("sucesso")
    except Exception as e:
      print(f"Ocorreu o erro: {e}")

elif (escola_encaminha == "D2"):
  print("distrito selecionado")
  for semed, seduc in D2:
    print(semed, seduc)
    try:
      # Obtenha as coordenadas das escolas selecionadas
      coords_estadual = data.loc[data['SIGEAM'] == seduc, ['LATITUDE', 'LONGITUDE']].values[0]
      coords_municipal = dados_semed.loc[dados_semed['SIGEAM'] == semed, ['LATITUDE', 'LONGITUDE']].values[0]
      
      # Calcular a distância entre as duas escolas usando Haversine
      distancia = haversine(coords_estadual, coords_municipal)
      
      # Adiciona uma linha entre as duas escolas
      folium.PolyLine([coords_estadual, coords_municipal], color="red", weight=2.5, opacity=0.8).add_to(m)
      print("sucesso")
    except Exception as e:
      print(f"Ocorreu o erro: {e}")

elif (escola_encaminha == "D3"):
  print("distrito selecionado")
  for semed, seduc in D3:
    print(semed, seduc)
    try:
      # Obtenha as coordenadas das escolas selecionadas
      coords_estadual = data.loc[data['SIGEAM'] == seduc, ['LATITUDE', 'LONGITUDE']].values[0]
      coords_municipal = dados_semed.loc[dados_semed['SIGEAM'] == semed, ['LATITUDE', 'LONGITUDE']].values[0]
      
      # Calcular a distância entre as duas escolas usando Haversine
      distancia = haversine(coords_estadual, coords_municipal)
      
      # Adiciona uma linha entre as duas escolas
      folium.PolyLine([coords_estadual, coords_municipal], color="red", weight=2.5, opacity=0.8).add_to(m)
      print("sucesso")
    except Exception as e:
      print(f"Ocorreu o erro: {e}")

elif (escola_encaminha == "D4"):
  print("distrito selecionado")
  for semed, seduc in D4:
    print(semed, seduc)
    try:
      # Obtenha as coordenadas das escolas selecionadas
      coords_estadual = data.loc[data['SIGEAM'] == seduc, ['LATITUDE', 'LONGITUDE']].values[0]
      coords_municipal = dados_semed.loc[dados_semed['SIGEAM'] == semed, ['LATITUDE', 'LONGITUDE']].values[0]
      
      # Calcular a distância entre as duas escolas usando Haversine
      distancia = haversine(coords_estadual, coords_municipal)
      
      # Adiciona uma linha entre as duas escolas
      folium.PolyLine([coords_estadual, coords_municipal], color="red", weight=2.5, opacity=0.8).add_to(m)
      print("sucesso")
    except Exception as e:
      print(f"Ocorreu o erro: {e}")
  
elif (escola_encaminha == "D5"):
  print("distrito selecionado")
  for semed, seduc in D5:
    print(semed, seduc)
    try:
      # Obtenha as coordenadas das escolas selecionadas
      coords_estadual = data.loc[data['SIGEAM'] == seduc, ['LATITUDE', 'LONGITUDE']].values[0]
      coords_municipal = dados_semed.loc[dados_semed['SIGEAM'] == semed, ['LATITUDE', 'LONGITUDE']].values[0]
      
      # Calcular a distância entre as duas escolas usando Haversine
      distancia = haversine(coords_estadual, coords_municipal)
      
      # Adiciona uma linha entre as duas escolas
      folium.PolyLine([coords_estadual, coords_municipal], color="red", weight=2.5, opacity=0.8).add_to(m)
      print("sucesso")
    except Exception as e:
      print(f"Ocorreu o erro: {e}")
      
elif (escola_encaminha == "D6"):
  print("distrito selecionado")
  for semed, seduc in D6:
    print(semed, seduc)
    try:
      # Obtenha as coordenadas das escolas selecionadas
      coords_estadual = data.loc[data['SIGEAM'] == seduc, ['LATITUDE', 'LONGITUDE']].values[0]
      coords_municipal = dados_semed.loc[dados_semed['SIGEAM'] == semed, ['LATITUDE', 'LONGITUDE']].values[0]
      
      # Calcular a distância entre as duas escolas usando Haversine
      distancia = haversine(coords_estadual, coords_municipal)
      
      # Adiciona uma linha entre as duas escolas
      folium.PolyLine([coords_estadual, coords_municipal], color="red", weight=2.5, opacity=0.8).add_to(m)
      print("sucesso")
    except Exception as e:
      print(f"Ocorreu o erro: {e}")

elif (escola_encaminha == "D7"):
  print("distrito selecionado")
  for semed, seduc in D7:
    print(semed, seduc)
    try:
      # Obtenha as coordenadas das escolas selecionadas
      coords_estadual = data.loc[data['SIGEAM'] == seduc, ['LATITUDE', 'LONGITUDE']].values[0]
      coords_municipal = dados_semed.loc[dados_semed['SIGEAM'] == semed, ['LATITUDE', 'LONGITUDE']].values[0]
      
      # Calcular a distância entre as duas escolas usando Haversine
      distancia = haversine(coords_estadual, coords_municipal)
      
      # Adiciona uma linha entre as duas escolas
      folium.PolyLine([coords_estadual, coords_municipal], color="red", weight=2.5, opacity=0.8).add_to(m)
      print("sucesso")
    except Exception as e:
      print(f"Ocorreu o erro: {e}")
   
st_folium(m, width=925, returned_objects=[])




