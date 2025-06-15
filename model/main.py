import pandas as pd
import osmnx as ox
from osmnx.features import features_from_point
import geopandas as gpd
from sklearn.neighbors import BallTree
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np
from sklearn.cluster import KMeans

from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
import joblib
from joblib import load



df=pd.read_csv('df_con_coordenadas.csv')
df.head()
df_ubicaciones=pd.read_csv('df_ubicaciones.csv')
df_ubicaciones.head()
lat_test = 25.6866
lon_test = -100.3161
tags = {'amenity': 'hospital'}

pois = features_from_point((lat_test, lon_test), tags=tags, dist=3000)
print(pois.head())
tags_dict = {
    'hospital': {'amenity': 'hospital'},
    'escuela': {'amenity': 'school'},
    'gimnasio': {'leisure': 'fitness_centre'},
    'oficina': {'building': 'office'}
}

# Polígono de Nuevo León 
nuevo_leon = ox.geocode_to_gdf("Nuevo León, México")

# Diccionario de POIs
pois_dict = {}

for tipo, tags in tags_dict.items():
    print(f"Descargando {tipo}...")
    pois = ox.features_from_polygon(nuevo_leon.geometry[0], tags=tags)
    pois = pois.to_crs(epsg=4326)
    pois = pois[pois.geometry.type.isin(['Point', 'Polygon', 'MultiPolygon'])].copy()
    pois['centroid'] = pois.geometry.centroid
    pois['lat'] = pois['centroid'].y
    pois['lon'] = pois['centroid'].x
    pois_dict[tipo] = pois[['lat', 'lon', 'name']]

gdf_ubicaciones = gpd.GeoDataFrame(
    df_ubicaciones,
    geometry=gpd.points_from_xy(df_ubicaciones['Longitud'], df_ubicaciones['Latitud']),
    crs="EPSG:4326"
)


def calcular_distancia_mas_cercana(origenes, destinos, tipo):
    # Convertir a radianes
    origen_coords = np.radians(origenes[['Latitud', 'Longitud']].values)
    destino_coords = np.radians(destinos[['lat', 'lon']].values)

    # Construir árbol
    tree = BallTree(destino_coords, metric='haversine')

    # Calcular distancia mínima y el índice del punto más cercano
    dist, idx = tree.query(origen_coords, k=1)
    dist_m = dist[:, 0] * 6371000  # convertir de radianes a metros
    closest_names = destinos.iloc[idx[:, 0]]['name'].values

    # Agregar al DataFrame original
    df_ubicaciones[f'dist_{tipo}_m'] = dist_m
    df_ubicaciones[f'{tipo}_nombre'] = closest_names

for tipo in pois_dict:
    print(f"Calculando distancia a {tipo}...")
    calcular_distancia_mas_cercana(df_ubicaciones, pois_dict[tipo], tipo)

df_ubicaciones.head()
df_ubicaciones.to_csv('df_ubicaciones_con_puntos.csv', index=False)

pois_catalogo = []

for tipo, pois in pois_dict.items():
    df = pois.copy()
    df['tipo'] = tipo

    # Asegurar que 'geometry' es parte del dataframe (si aún no es GeoDataFrame)
    if not isinstance(df, gpd.GeoDataFrame):
        df = gpd.GeoDataFrame(df, geometry=gpd.points_from_xy(df['lon'], df['lat']), crs="EPSG:4326")

    # Seleccionar columnas incluyendo geometry
    df = df[['tipo', 'name', 'lat', 'lon', 'geometry']]
    pois_catalogo.append(df)

    catalogo_pois = pd.concat(pois_catalogo).reset_index(drop=True)

# Asegurar que esté correctamente definido como GeoDataFrame
gdf_catalogo = gpd.GeoDataFrame(catalogo_pois, geometry='geometry', crs="EPSG:4326")
gdf_catalogo.to_csv("catalogo_pois_nuevo_leon.csv", index=False)

gdf_catalogo.to_file("catalogo_pois_nuevo_leon.geojson", driver="GeoJSON")
gdf_catalogo.sample(5)

df_ubicaciones.columns

df_ubicaciones = df_ubicaciones.drop(columns=[
    'hospital_nombre',
    'escuela_nombre',
    'gimnasio_nombre',
    'oficina_nombre'
    
])

df_compras= pd.read_csv('df_con_coordenadas.csv')
df_compras.columns

meses = {
    'Enero': 1, 'Febrero': 2, 'Marzo': 3, 'Abril': 4,
    'Mayo': 5, 'Junio': 6, 'Julio': 7, 'Agosto': 8,
    'Septiembre': 9, 'Setiembre': 9, 'Octubre': 10,
    'Noviembre': 11, 'Diciembre': 12
}

df_compras['Mes_num'] = df_compras['Mes'].map(meses)
df_compras['fecha'] = pd.to_datetime(
    df_compras['Año'].astype(str) + '-' + df_compras['Mes_num'].astype(str) + '-01',
    format='%Y-%m-%d'
)

# 4. Agregación mensual por cliente
ventas_mensuales = df_compras.groupby(['ID Cliente', 'fecha']).agg({
    'Venta USD': 'sum',
    'Venta Cajas': 'sum'
}).reset_index()

# 5. Agregaciones generales por cliente
df_agg = df_compras.groupby('ID Cliente').agg(
    volumen_total_usd=('Venta USD', 'sum'),
    volumen_total_cajas=('Venta Cajas', 'sum'),
    ticket_promedio=('Venta USD', 'mean'),
    meses_activo=('fecha', lambda x: x.dt.to_period('M').nunique()),
    ultima_fecha=('fecha', 'max'),
    categoria_mas_frecuente=('Categoría', lambda x: x.value_counts().index[0])
).reset_index()

# 6. Recencia (en meses desde la última compra)
ultimo_mes = df_compras['fecha'].max().to_period('M')
df_agg['recencia'] = df_agg['ultima_fecha'].dt.to_period('M').apply(lambda x: (ultimo_mes - x).n)

# 7. Frecuencia de compra promedio por mes (USD)
df_agg['frecuencia_compra'] = df_agg['volumen_total_usd'] / df_agg['meses_activo']

# 8. Variabilidad mensual (desviación estándar en USD por mes)
variabilidad = ventas_mensuales.groupby('ID Cliente')['Venta USD'].std().reset_index(name='variabilidad')
df_agg = df_agg.merge(variabilidad, on='ID Cliente', how='left')

# 9. Top 3 categorías por cliente como texto
def top3_categorias(categorias):
    return ', '.join(categorias.value_counts().head(2).index)

top3 = df_compras.groupby('ID Cliente')['Categoría'].apply(top3_categorias).reset_index(name='categorias_top3')
df_agg = df_agg.merge(top3, on='ID Cliente', how='left')

# 10. Eliminar columna auxiliar
df_agg = df_agg.drop(columns='ultima_fecha')

df_agg.head()

df_agg['categoria_mas_frecuente'].value_counts()
df_agg = df_agg.drop(columns='categorias_top3')
df_agg.shape
df_agg['recencia'].value_counts()
df_clientes = df_agg.merge(df_ubicaciones, on='ID Cliente', how='left')
df_clientes.shape
df_clientes.head()
df_clientes.to_csv('df_primer_cluster.csv')

df_clientes = df_clientes.dropna(subset=['variabilidad'])



# Subset numérico sin normalizar
vars_numericas = [
    'volumen_total_usd', 'volumen_total_cajas', 'ticket_promedio',
    'meses_activo', 'recencia', 'frecuencia_compra', 'variabilidad',
    'dist_hospital_m', 'dist_escuela_m', 'dist_gimnasio_m', 'dist_oficina_m'
]

# Boxplots individuales
for col in vars_numericas:
    plt.figure(figsize=(6, 2.5))
    sns.boxplot(x=df_clientes[col])
    plt.title(f'Boxplot: {col}')
    plt.tight_layout()
    plt.show()

def contar_outliers(df, columnas):
    resumen = []
    for col in columnas:
        Q1 = df[col].quantile(0.25)
        Q3 = df[col].quantile(0.75)
        IQR = Q3 - Q1
        limite_inferior = Q1 - 1.5 * IQR
        limite_superior = Q3 + 1.5 * IQR
        n_outliers = ((df[col] < limite_inferior) | (df[col] > limite_superior)).sum()
        resumen.append({'Variable': col, 'Outliers': n_outliers})
    return pd.DataFrame(resumen)

# Lista de variables numéricas
vars_numericas = [
    'volumen_total_usd', 'volumen_total_cajas', 'ticket_promedio',
    'meses_activo', 'recencia', 'frecuencia_compra', 'variabilidad',
    'dist_hospital_m', 'dist_escuela_m', 'dist_gimnasio_m', 'dist_oficina_m'
]

# Aplicar
outliers_df = contar_outliers(df_clientes, vars_numericas)
outliers_df


df_clientes['volumen_total_usd_log'] = np.log1p(df_clientes['volumen_total_usd'])
df_clientes['volumen_total_cajas_log'] = np.log1p(df_clientes['volumen_total_cajas'])
df_clientes['ticket_promedio_log'] = np.log1p(df_clientes['ticket_promedio'])
df_clientes['frecuencia_compra_log'] = np.log1p(df_clientes['frecuencia_compra'])
df_clientes['variabilidad_log'] = np.log1p(df_clientes['variabilidad'])


vars_corr = [
    'volumen_total_usd_log', 'volumen_total_cajas_log', 'ticket_promedio_log',
    'frecuencia_compra_log', 'variabilidad_log',
    'meses_activo', 'recencia',
    'dist_hospital_m', 'dist_escuela_m', 'dist_gimnasio_m', 'dist_oficina_m'
]

# 3. Calcular y graficar la matriz de correlación
plt.figure(figsize=(10, 8))
sns.heatmap(df_clientes[vars_corr].corr(), annot=True, cmap='coolwarm', fmt='.2f')
plt.title("🔍 Matriz de correlación entre variables numéricas (con log transformado)")
plt.tight_layout()
plt.show()

df_clientes = df_clientes.drop(columns=[
    'volumen_total_usd_log', 'volumen_total_cajas_log'
])

vars_corr = [
    'ticket_promedio_log',
    'frecuencia_compra_log', 'variabilidad_log',
    'meses_activo', 'recencia',
    'dist_hospital_m', 'dist_escuela_m', 'dist_gimnasio_m', 'dist_oficina_m'
]
cols_categoricas = ['categoria_mas_frecuente']


# 3. Calcular y graficar la matriz de correlación
plt.figure(figsize=(10, 8))
sns.heatmap(df_clientes[vars_corr].corr(), annot=True, cmap='coolwarm', fmt='.2f')
plt.title("🔍 Matriz de correlación entre variables numéricas (con log transformado)")
plt.tight_layout()
plt.show()

cols_numericas = [
    'ticket_promedio_log',
    'frecuencia_compra_log', 'variabilidad_log',
    'meses_activo', 'recencia',
    'dist_hospital_m', 'dist_escuela_m', 'dist_gimnasio_m', 'dist_oficina_m'
]


# Evaluar varios valores de k
inertias = []
k_range = range(2, 15)


preprocessor = ColumnTransformer(transformers=[
    ('num', StandardScaler(), cols_numericas),
    ('cat', OneHotEncoder(handle_unknown='ignore'), cols_categoricas)
])

X_preprocesado = preprocessor.fit_transform(df_clientes)
df_clientes_activos = df_clientes[df_clientes['recencia'] <= 6].copy()


for k in k_range:
    kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
    kmeans.fit(X_preprocesado)
    inertias.append(kmeans.inertia_)

# Graficar
plt.figure(figsize=(8, 5))
plt.plot(k_range, inertias, marker='o')
plt.title('Elbow Method: Inertia vs Number of Clusters')
plt.xlabel('Número de Clusters (k)')
plt.ylabel('Inercia (Distancia total a centroides)')
plt.xticks(k_range)
plt.grid(True)
plt.show()

k = 5

# Ajustar KMeans
kmeans = KMeans(n_clusters=k, random_state=42)
clusters = kmeans.fit_predict(X_preprocesado)

# Añadir la asignación de cluster al DataFrame original
df_clientes_activos['cluster'] = clusters

pca = PCA(n_components=2)
X_pca = pca.fit_transform(X_preprocesado)

plt.figure(figsize=(8,6))
plt.scatter(X_pca[:, 0], X_pca[:, 1], c=df_clientes_activos['cluster'], cmap='tab10', alpha=0.7)
plt.title("Clusters visualizados con PCA")
plt.xlabel("Componente Principal 1")
plt.ylabel("Componente Principal 2")
plt.grid(True)
plt.show()

tsne = TSNE(n_components=2, perplexity=30, random_state=42)
X_tsne = tsne.fit_transform(X_preprocesado)

plt.figure(figsize=(8,6))
plt.scatter(X_tsne[:, 0], X_tsne[:, 1], c=df_clientes_activos['cluster'], cmap='tab10', alpha=0.7)
plt.title("Clusters visualizados con t-SNE")
plt.xlabel("t-SNE 1")
plt.ylabel("t-SNE 2")
plt.grid(True)
plt.show()

df_clientes_activos['cluster'].value_counts()

df_clientes_activos.groupby('cluster')[
    [ 'ticket_promedio_log', 'frecuencia_compra_log',
     'variabilidad_log', 'recencia', 'meses_activo',
     'dist_hospital_m', 'dist_escuela_m', 'dist_gimnasio_m', 'dist_oficina_m']
].median().round(2)

df_clientes_activos.groupby('cluster')[
    [ 'ticket_promedio_log', 'frecuencia_compra_log',
     'variabilidad_log', 'recencia', 'meses_activo',
     'dist_hospital_m', 'dist_escuela_m', 'dist_gimnasio_m', 'dist_oficina_m']
].mean().round(2)

joblib.dump(preprocessor, "preprocessor.pkl")
joblib.dump(kmeans, "kmeans_model.pkl")

nuevo_cliente = pd.DataFrame([{
    'ticket_promedio_log': np.log1p(12.50),
    'frecuencia_compra_log': np.log1p(8),
    'variabilidad_log': np.log1p(3.2),
    'recencia': 1,
    'meses_activo': 20,
    'dist_hospital_m': 1200,
    'dist_escuela_m': 500,
    'dist_gimnasio_m': 3000,
    'dist_oficina_m': 6000,
    'categoria_mas_frecuente': 'COLAS'
}])

preprocessor = load("preprocessor.pkl")
kmeans = load("kmeans_model.pkl")

# Transformar y predecir
X_nuevo = preprocessor.transform(nuevo_cliente)
cluster_asignado = kmeans.predict(X_nuevo)

print(f"Cluster asignado: {cluster_asignado[0]}")
df_clientes_activos.columns

df_cluster = df_clientes_activos[['ID Cliente', 'cluster']]

#Hacemos el merge con df_ubicaciones, usando 'id_cliente' como clave
df_con_cluster1 = df_ubicaciones.merge(df_cluster, on='ID Cliente', how='left')

df_con_cluster1.info()