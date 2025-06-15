import pandas as pd
import numpy as np
from joblib import load

def predecir_cluster(ticket_promedio, frecuencia_compra, variabilidad, recencia, meses_activo, 
                    dist_hospital_m, dist_escuela_m, dist_gimnasio_m, dist_oficina_m, 
                    categoria_mas_frecuente):
    """
    Predice el cluster de un cliente basado en sus características.
    
    Parámetros requeridos:
    - ticket_promedio: Valor promedio de compra en USD
    - frecuencia_compra: Frecuencia de compra mensual en USD
    - variabilidad: Desviación estándar de compras mensuales
    - recencia: Meses desde la última compra
    - meses_activo: Número de meses que ha estado activo
    - dist_hospital_m: Distancia al hospital más cercano en metros
    - dist_escuela_m: Distancia a la escuela más cercana en metros  
    - dist_gimnasio_m: Distancia al gimnasio más cercano en metros
    - dist_oficina_m: Distancia a la oficina más cercana en metros
    - categoria_mas_frecuente: Categoría de producto más comprada (ej: 'COLAS', 'AGUA', etc.)
    
    Retorna:
    - cluster: Número del cluster asignado (0-4)
    """
    
    # Cargar modelos entrenados
    preprocessor = load("preprocessor.pkl")
    kmeans = load("kmeans_model.pkl")
    
    # Crear DataFrame con los datos del nuevo cliente
    nuevo_cliente = pd.DataFrame([{
        'ticket_promedio_log': np.log1p(ticket_promedio),
        'frecuencia_compra_log': np.log1p(frecuencia_compra),
        'variabilidad_log': np.log1p(variabilidad),
        'recencia': recencia,
        'meses_activo': meses_activo,
        'dist_hospital_m': dist_hospital_m,
        'dist_escuela_m': dist_escuela_m,
        'dist_gimnasio_m': dist_gimnasio_m,
        'dist_oficina_m': dist_oficina_m,
        'categoria_mas_frecuente': categoria_mas_frecuente
    }])
    
    # Transformar y predecir
    X_nuevo = preprocessor.transform(nuevo_cliente)
    cluster_asignado = kmeans.predict(X_nuevo)
    
    return cluster_asignado[0]

# Ejemplo de uso:
if __name__ == "__main__":
    cluster = predecir_cluster(
        ticket_promedio=12.50,
        frecuencia_compra=8.0,
        variabilidad=3.2,
        recencia=1,
        meses_activo=20,
        dist_hospital_m=1200,
        dist_escuela_m=500,
        dist_gimnasio_m=3000,
        dist_oficina_m=6000,
        categoria_mas_frecuente='COLAS'
    )
    print(f"Cliente asignado al cluster: {cluster}")