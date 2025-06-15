import requests
import json

# URL base de tu API
BASE_URL = "http://localhost:8000"

def test_store_endpoint():
    """
    Prueba el endpoint /store con datos de ejemplo
    """
    print("🧪 Probando endpoint /store...")
    
    # Datos de prueba basados en el ejemplo de tu función
    test_data = {
        "ticket_promedio": 12.50,
        "frecuencia_compra": 8.0,
        "variabilidad": 3.2,
        "recencia": 1,
        "meses_activo": 20,
        "dist_hospital_m": 1200.0,
        "dist_escuela_m": 500.0,
        "dist_gimnasio_m": 3000.0,
        "dist_oficina_m": 6000.0,
        "categoria_mas_frecuente": "COLAS"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/store", json=test_data)
        
        print(f"Status Code: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Respuesta exitosa:")
            print(json.dumps(result, indent=2, ensure_ascii=False))
            
            # Extraer challenge_id para pruebas adicionales
            challenge_id = result.get("challenge_id")
            if challenge_id:
                print(f"\n📝 Challenge ID generado: {challenge_id}")
                return challenge_id
        else:
            print("❌ Error en la respuesta:")
            print(f"Response: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Error de conexión. ¿Está corriendo el servidor?")
        print("💡 Ejecuta: uvicorn main:app --reload")
    except Exception as e:
        print(f"❌ Error inesperado: {str(e)}")
    
    return None

def test_challenge_progress(challenge_id):
    """
    Prueba el endpoint de progreso del reto
    """
    if not challenge_id:
        print("⚠️  No hay challenge_id para probar progreso")
        return
        
    print(f"\n🔄 Probando progreso para challenge: {challenge_id}")
    
    progress_data = {
        "challenge_id": challenge_id,
        "progress_data": {
            "colas_vendidas": 15,
            "ventas_totales": 180.50
        }
    }
    
    try:
        response = requests.post(f"{BASE_URL}/challenge/progress", json=progress_data)
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Progreso actualizado:")
            print(json.dumps(result, indent=2, ensure_ascii=False))
        else:
            print("❌ Error actualizando progreso:")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")

def test_get_challenge_status(challenge_id):
    """
    Prueba obtener el estado del reto
    """
    if not challenge_id:
        print("⚠️  No hay challenge_id para consultar estado")
        return
        
    print(f"\n📊 Consultando estado del challenge: {challenge_id}")
    
    try:
        response = requests.get(f"{BASE_URL}/challenge/{challenge_id}")
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Estado del reto:")
            print(json.dumps(result, indent=2, ensure_ascii=False))
        else:
            print("❌ Error consultando estado:")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")

def test_complete_flow():
    """
    Prueba el flujo completo de la API
    """
    print("\n🔄 Probando flujo completo...")
    
    scenarios = [
        {
            "name": "Cliente frecuente premium",
            "data": {
                "ticket_promedio": 25.0,
                "frecuencia_compra": 15.0,
                "variabilidad": 5.2,
                "recencia": 0,
                "meses_activo": 36,
                "dist_hospital_m": 800.0,
                "dist_escuela_m": 300.0,
                "dist_gimnasio_m": 1500.0,
                "dist_oficina_m": 2000.0,
                "categoria_mas_frecuente": "AGUA"
            }
        },
        {
            "name": "Cliente ocasional",
            "data": {
                "ticket_promedio": 8.0,
                "frecuencia_compra": 2.0,
                "variabilidad": 1.5,
                "recencia": 6,
                "meses_activo": 8,
                "dist_hospital_m": 2500.0,
                "dist_escuela_m": 1200.0,
                "dist_gimnasio_m": 4000.0,
                "dist_oficina_m": 8000.0,
                "categoria_mas_frecuente": "JUGOS"
            }
        },
        {
            "name": "Cliente VIP alto valor",
            "data": {
                "ticket_promedio": 45.0,
                "frecuencia_compra": 20.0,
                "variabilidad": 8.5,
                "recencia": 0,
                "meses_activo": 48,
                "dist_hospital_m": 400.0,
                "dist_escuela_m": 200.0,
                "dist_gimnasio_m": 800.0,
                "dist_oficina_m": 1000.0,
                "categoria_mas_frecuente": "ENERGY"
            }
        }
    ]
    
    challenge_ids = []
    
    for i, scenario in enumerate(scenarios, 1):
        print(f"\n{'='*60}")
        print(f"🎯 ESCENARIO {i}: {scenario['name']}")
        print(f"{'='*60}")
        
        try:
            # 1. Crear challenge
            print(f"📝 1. Creando challenge para: {scenario['name']}")
            response = requests.post(f"{BASE_URL}/store", json=scenario['data'])
            
            if response.status_code == 200:
                result = response.json()
                challenge_id = result.get("challenge_id")
                cluster_info = result.get('cluster', {})
                
                print(f"   ✅ Challenge creado: {challenge_id}")
                print(f"   📊 Cluster asignado: {cluster_info.get('id')} - {cluster_info.get('name')}")
                print(f"   🎯 Challenge sugerido: {result.get('challenge', {}).get('name', 'N/A')}")
                
                if challenge_id:
                    challenge_ids.append(challenge_id)
                    
                    # 2. Actualizar progreso
                    print(f"\n📈 2. Actualizando progreso del challenge...")
                    progress_data = {
                        "challenge_id": challenge_id,
                        "progress_data": {
                            "colas_vendidas": 10 + (i * 5),
                            "ventas_totales": 150.0 + (i * 50.0),
                            "dias_activo": i * 2
                        }
                    }
                    
                    progress_response = requests.post(f"{BASE_URL}/challenge/progress", json=progress_data)
                    if progress_response.status_code == 200:
                        progress_result = progress_response.json()
                        print(f"   ✅ Progreso actualizado")
                        print(f"   📊 Completado: {progress_result.get('completion_percentage', 0)}%")
                    else:
                        print(f"   ❌ Error actualizando progreso: {progress_response.status_code}")
                    
                    # 3. Consultar estado
                    print(f"\n📋 3. Consultando estado final...")
                    status_response = requests.get(f"{BASE_URL}/challenge/{challenge_id}")
                    if status_response.status_code == 200:
                        status_result = status_response.json()
                        print(f"   ✅ Estado consultado exitosamente")
                        print(f"   🏆 Estado: {status_result.get('status', 'N/A')}")
                        if status_result.get('completed_at'):
                            print(f"   🎉 Completado: {status_result.get('completed_at')}")
                    else:
                        print(f"   ❌ Error consultando estado: {status_response.status_code}")
                        
            else:
                print(f"   ❌ Error creando challenge: {response.status_code}")
                print(f"   📄 Response: {response.text}")
                
        except Exception as e:
            print(f"   ❌ Error en escenario: {str(e)}")
    
    # Resumen final
    print(f"\n{'='*60}")
    print(f"📊 RESUMEN FINAL")
    print(f"{'='*60}")
    print(f"Challenges creados: {len(challenge_ids)}")
    if challenge_ids:
        print("IDs generados:")
        for i, cid in enumerate(challenge_ids, 1):
            print(f"  {i}. {cid}")
    print(f"{'='*60}")

def test_multiple_scenarios():
    """
    Prueba múltiples escenarios de datos (método simple)
    """
    print("\n🎯 Probando múltiples escenarios...")
    
    scenarios = [
        {
            "name": "Cliente frecuente premium",
            "data": {
                "ticket_promedio": 25.0,
                "frecuencia_compra": 15.0,
                "variabilidad": 5.2,
                "recencia": 0,
                "meses_activo": 36,
                "dist_hospital_m": 800.0,
                "dist_escuela_m": 300.0,
                "dist_gimnasio_m": 1500.0,
                "dist_oficina_m": 2000.0,
                "categoria_mas_frecuente": "AGUA"
            }
        },
        {
            "name": "Cliente ocasional",
            "data": {
                "ticket_promedio": 8.0,
                "frecuencia_compra": 2.0,
                "variabilidad": 1.5,
                "recencia": 6,
                "meses_activo": 8,
                "dist_hospital_m": 2500.0,
                "dist_escuela_m": 1200.0,
                "dist_gimnasio_m": 4000.0,
                "dist_oficina_m": 8000.0,
                "categoria_mas_frecuente": "JUGOS"
            }
        }
    ]
    
    for scenario in scenarios:
        print(f"\n📝 Escenario: {scenario['name']}")
        try:
            response = requests.post(f"{BASE_URL}/store", json=scenario['data'])
            if response.status_code == 200:
                result = response.json()
                cluster_info = result.get('cluster', {})
                print(f"   Cluster asignado: {cluster_info.get('id')} - {cluster_info.get('name')}")
            else:
                print(f"   ❌ Error: {response.status_code}")
        except Exception as e:
            print(f"   ❌ Error: {str(e)}")

if __name__ == "__main__":
    print("🚀 Iniciando pruebas de la API...")
    print("=" * 50)
    
    # Opción 1: Flujo completo (recomendado)
    print("\n🔄 Ejecutando FLUJO COMPLETO...")
    test_complete_flow()
    
    print("\n" + "=" * 50)
    print("🧪 Ejecutando pruebas individuales...")
    
    # Opción 2: Pruebas individuales (original)
    challenge_id = test_store_endpoint()
    
    # Si se creó un reto, probar los otros endpoints
    if challenge_id:
        test_challenge_progress(challenge_id)
        test_get_challenge_status(challenge_id)
    
    # Probar múltiples escenarios simples
    test_multiple_scenarios()
    
    print("\n" + "=" * 50)
    print("✨ Todas las pruebas completadas")