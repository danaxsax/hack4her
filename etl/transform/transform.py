import pandas as pd

archivos = ['1.csv', '2.csv', '3.csv', '4.csv', '5.csv', '6.csv', '7.csv', '8.csv', '9.csv']
df1=pd.read_csv('1.csv', encoding='latin1')
df2=pd.read_csv('2.csv', encoding='latin1')
df3=pd.read_csv('3.csv', encoding='latin1') 
df4=pd.read_csv('4.csv', encoding='latin1')
df5=pd.read_csv('5.csv', encoding='latin1')
df6=pd.read_csv('6.csv', encoding='latin1')
df7=pd.read_csv('7.csv', encoding='latin1')
df8=pd.read_csv('8.csv', encoding='latin1')
df9=pd.read_csv('9.csv', encoding='latin1')

df3.head()
df9.columns
df4.columns = df4.columns.str.replace('^Sum of ', '', regex=True)
df4.columns

df = pd.concat([df1, df2, df3,df4,df5,df6,df7,df8,df9], ignore_index=True)
df.shape

df.isna().sum()

df['ID Cliente'].nunique()

inegi=pd.read_csv('data.csv')
inegi.columns

inegi['Max_estrato_personas'].value_counts()

df_unicos = df.drop_duplicates(subset='ID Cliente')
df_unicos['Tamaño de Cliente'].value_counts()
df_unicos.columns
df_resultado = df_unicos.copy()

# Filtrar clientes por tamaño
micro = df_resultado[df_resultado['Tamaño de Cliente'] == 'MICRO'].copy().reset_index(drop=True)
chico = df_resultado[df_resultado['Tamaño de Cliente'] == 'CHICO'].copy().reset_index(drop=True)
mediano = df_resultado[df_resultado['Tamaño de Cliente'] == 'MEDIANO'].copy().reset_index(drop=True)
grande = df_resultado[df_resultado['Tamaño de Cliente'] == 'GRANDE'].copy().reset_index(drop=True)
extgde = df_resultado[df_resultado['Tamaño de Cliente'] == 'EXT-GDE'].copy().reset_index(drop=True)

# Muestras INEGI

# 1. EXT-GDE: 26 de 251 + 45 de 250
inegi_251 = inegi[inegi['Max_estrato_personas'] == 251].sample(n=26, random_state=1)
inegi_250 = inegi[inegi['Max_estrato_personas'] == 250]
inegi_250_ext = inegi_250.sample(n=45, random_state=2)
coordenadas_extgde = pd.concat([inegi_251, inegi_250_ext]).reset_index(drop=True)

# 2. Quitar los 45 usados para EXT-GDE del 250 para GRANDE
inegi_250_grande = inegi_250.drop(index=inegi_250_ext.index)

# 3. GRANDE: 46 de 250 restantes + 117 de 100 + 231 de 50
inegi_100 = inegi[inegi['Max_estrato_personas'] == 100]
inegi_50 = inegi[inegi['Max_estrato_personas'] == 50]
inegi_50_grande = inegi_50.sample(n=231, random_state=3)
coordenadas_grande = pd.concat([inegi_250_grande, inegi_100, inegi_50_grande]).reset_index(drop=True)

# 4. MEDIANO: 150 restantes de 50 + 988 de 30
inegi_50_mediano = inegi_50.drop(index=inegi_50_grande.index)
inegi_30 = inegi[inegi['Max_estrato_personas'] == 30]
inegi_30_mediano = inegi_30.sample(n=988, random_state=4)
coordenadas_mediano = pd.concat([inegi_50_mediano, inegi_30_mediano]).reset_index(drop=True)

# 5. CHICO: 1685 de 10
inegi_10 = inegi[inegi['Max_estrato_personas'] == 10].sample(n=1685, random_state=5).reset_index(drop=True)

# 6. MICRO: 5040 de 5
inegi_5 = inegi[inegi['Max_estrato_personas'] == 5].sample(n=5040, random_state=6).reset_index(drop=True)


# Asignar coordenadas
extgde['Latitud'] = coordenadas_extgde['Latitud']
extgde['Longitud'] = coordenadas_extgde['Longitud']

grande['Latitud'] = coordenadas_grande['Latitud']
grande['Longitud'] = coordenadas_grande['Longitud']

mediano['Latitud'] = coordenadas_mediano['Latitud']
mediano['Longitud'] = coordenadas_mediano['Longitud']

chico['Latitud'] = inegi_10['Latitud']
chico['Longitud'] = inegi_10['Longitud']

micro['Latitud'] = inegi_5['Latitud']
micro['Longitud'] = inegi_5['Longitud']

# Concatenar todo
df_final = pd.concat([micro, chico, mediano, grande, extgde], ignore_index=True)