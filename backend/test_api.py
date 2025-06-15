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

def test_multiple_scenarios():
    """
    Prueba múltiples escenarios de datos
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
    
    # Prueba principal
    challenge_id = test_store_endpoint()
    
    # Si se creó un reto, probar los otros endpoints
    if challenge_id:
        test_challenge_progress(challenge_id)
        test_get_challenge_status(challenge_id)
    
    # Probar múltiples escenarios
    test_multiple_scenarios()
    
    print("\n" + "=" * 50)
    print("✨ Pruebas completadas")