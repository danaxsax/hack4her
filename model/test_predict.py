from predict_cluster import predecir_cluster

# Test con diferentes tipos de clientes
print("=== Probando función de predicción de clusters ===\n")

# Cliente 1: Cliente frecuente con alta compra
print("Cliente 1 - Alto valor:")
cluster1 = predecir_cluster(
    ticket_promedio=25.0,
    frecuencia_compra=15.0,
    variabilidad=5.0,
    recencia=0,
    meses_activo=24,
    dist_hospital_m=800,
    dist_escuela_m=300,
    dist_gimnasio_m=1500,
    dist_oficina_m=2000,
    categoria_mas_frecuente='COLAS'
)
print(f"Cluster asignado: {cluster1}\n")

# Cliente 2: Cliente ocasional
print("Cliente 2 - Ocasional:")
cluster2 = predecir_cluster(
    ticket_promedio=8.0,
    frecuencia_compra=3.0,
    variabilidad=1.5,
    recencia=3,
    meses_activo=8,
    dist_hospital_m=2000,
    dist_escuela_m=1200,
    dist_gimnasio_m=4000,
    dist_oficina_m=5000,
    categoria_mas_frecuente='AGUA'
)
print(f"Cluster asignado: {cluster2}\n")

# Cliente 3: Cliente inactivo
print("Cliente 3 - Inactivo:")
cluster3 = predecir_cluster(
    ticket_promedio=5.0,
    frecuencia_compra=1.0,
    variabilidad=0.8,
    recencia=6,
    meses_activo=3,
    dist_hospital_m=3000,
    dist_escuela_m=2500,
    dist_gimnasio_m=6000,
    dist_oficina_m=8000,
    categoria_mas_frecuente='JUGOS'
)
print(f"Cluster asignado: {cluster3}\n")

# Cliente 4: Cliente del ejemplo original
print("Cliente 4 - Ejemplo original:")
cluster4 = predecir_cluster(
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
print(f"Cluster asignado: {cluster4}\n")

# Cliente 5: Cliente urbano de alto valor
print("Cliente 5 - Urbano alto valor:")
cluster5 = predecir_cluster(
    ticket_promedio=35.0,
    frecuencia_compra=20.0,
    variabilidad=8.0,
    recencia=0,
    meses_activo=30,
    dist_hospital_m=500,
    dist_escuela_m=200,
    dist_gimnasio_m=800,
    dist_oficina_m=1000,
    categoria_mas_frecuente='ENERGETICAS'
)
print(f"Cluster asignado: {cluster5}\n")

print("=== Pruebas completadas ===")