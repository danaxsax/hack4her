import logging
import csv
import os
import sys
import re
import requests

LOG_FILE = 'results.log'
CSV_FILE = 'data.csv'

# Lista blanca de clases de actividad permitidas
CLASES_PERMITIDAS = {
    "BARES, CANTINAS Y SIMILARES",
    "CABAÑAS, VILLAS Y SIMILARES",
    "CAFETERÍAS, FUENTES DE SODAS, NEVERÍAS, REFRESQUERÍAS Y SIMILARES",
    "CAMPAMENTOS Y ALBERGUES RECREATIVOS",
    "CENTROS NOCTURNOS, DISCOTECAS Y SIMILARES",
    "COMERCIO AL POR MAYOR DE ABARROTES",
    "COMERCIO AL POR MAYOR DE BEBIDAS NO ALCOHÓLICAS Y HIELO",
    "COMERCIO AL POR MAYOR DE BOTANAS Y FRITURAS",
    "COMERCIO AL POR MAYOR DE OTROS ALIMENTOS",
    "COMERCIO AL POR MAYOR DE VINOS Y LICORES",
    "COMERCIO AL POR MENOR DE BEBIDAS NO ALCOHÓLICAS Y HIELO",
    "COMERCIO AL POR MENOR DE OTROS ALIMENTOS",
    "COMERCIO AL POR MENOR DE PALETAS DE HIELO Y HELADOS",
    "COMERCIO AL POR MENOR EN TIENDAS DE ABARROTES, ULTRAMARINOS Y MISCELÁNEAS",
    "COMERCIO AL POR MENOR EN TIENDAS DEPARTAMENTALES",
    "FARMACIAS CON MINISÚPER",
    "HOTELES CON OTROS SERVICIOS INTEGRADOS",
    "HOTELES SIN OTROS SERVICIOS INTEGRADOS",
    "RESTAURANTES CON SERVICIO DE PREPARACIÓN DE ALIMENTOS A LA CARTA O DE COMIDA CORRIDA",
    "RESTAURANTES CON SERVICIO DE PREPARACIÓN DE ANTOJITOS",
    "RESTAURANTES CON SERVICIO DE PREPARACIÓN DE PESCADOS Y MARISCOS",
    "RESTAURANTES CON SERVICIO DE PREPARACIÓN DE PIZZAS, HAMBURGUESAS, HOT DOGS Y POLLOS ROSTIZADOS PARA LLEVAR",
    "RESTAURANTES CON SERVICIO DE PREPARACIÓN DE TACOS Y TORTAS",
    "RESTAURANTES QUE PREPARAN OTRO TIPO DE ALIMENTOS PARA LLEVAR",
    "SERVICIOS DE COMEDOR PARA EMPRESAS E INSTITUCIONES",
    "SERVICIOS DE PREPARACIÓN DE ALIMENTOS EN UNIDADES MÓVILES",
    "SERVICIOS DE PREPARACIÓN DE ALIMENTOS PARA OCASIONES ESPECIALES",
    "SERVICIOS DE PREPARACIÓN DE OTROS ALIMENTOS PARA CONSUMO INMEDIATO"
}

# Función para pedir confirmación y borrar archivos si existen
def check_and_clear_files():
    archivos = []
    if os.path.exists(LOG_FILE):
        archivos.append(LOG_FILE)
    if os.path.exists(CSV_FILE):
        archivos.append(CSV_FILE)

    if archivos:
        print(f"⚠️ Los siguientes archivos ya existen: {', '.join(archivos)}")
        respuesta = input("¿Deseas borrar estos archivos y continuar? (s/n): ").strip().lower()
        if respuesta == 's':
            for archivo in archivos:
                try:
                    os.remove(archivo)
                    print(f"✅ Archivo {archivo} borrado.")
                except Exception as e:
                    print(f"❌ No se pudo borrar {archivo}: {e}")
                    sys.exit(1)
        else:
            print("❌ Operación cancelada por el usuario.")
            sys.exit(0)

# Configurar logging
def setup_logging():
    logging.basicConfig(
        filename=LOG_FILE,
        level=logging.INFO,
        format='%(message)s',
        encoding='utf-8'
    )

# Extraer número máximo del estrato (ej. "0 a 5 personas" → 5)
def extraer_max_estrato(estrato: str) -> str:
    numeros = re.findall(r'\d+', estrato)
    if numeros:
        return max(map(int, numeros))
    return "No disponible"

# Petición al API y procesamiento
TOKEN = "5cded4fb-4e60-4cc0-b129-bb225c4040d9"
sector_ids = [43, 46, 72]
BASE_URL = "https://www.inegi.org.mx/app/api/denue/v1/consulta/BuscarAreaActEstr/00/0/0/0/0/{}/0/0/0/0/1/50/0/0/{}"

def fetch_and_log(sector_id):
    url = BASE_URL.format(sector_id, TOKEN)
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()

        with open(CSV_FILE, mode='a', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)

            for entry in data:
                clase_actividad = entry.get("Clase_actividad", "").strip().upper()
                if clase_actividad not in CLASES_PERMITIDAS:
                    continue  # Filtrado

                estrato_original = entry.get("Estrato", "No disponible")
                tamaño_max = extraer_max_estrato(estrato_original)
                nombre = entry.get("Nombre", "No disponible")
                cp = entry.get("CP")
                if not cp or str(cp).strip() == "":
                    cp = "03560"
                longitud = entry.get("Longitud", "No disponible")
                latitud = entry.get("Latitud", "No disponible")

                logging.info("=====================================")
                logging.info(f"📌 Clase de actividad : {clase_actividad}")
                logging.info(f"👥 Máximo en estrato : {tamaño_max} personas ({estrato_original})")
                logging.info(f"🏪 Nombre del establecimiento : {nombre}")
                logging.info(f"📫 Código postal : {cp}")
                logging.info(f"🗺️ Coordenadas : Longitud = {longitud}, Latitud = {latitud}")
                logging.info("")

                writer.writerow([
                    clase_actividad,
                    tamaño_max,
                    nombre,
                    cp,
                    longitud,
                    latitud
                ])

    except requests.RequestException as e:
        print(f"❌ Error al hacer la solicitud para sector {sector_id}: {e}")

def main():
    check_and_clear_files()
    setup_logging()

    with open(CSV_FILE, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow([
            "Clase_actividad",
            "Max_estrato_personas",
            "Nombre",
            "CP",
            "Longitud",
            "Latitud"
        ])

    for sector_id in sector_ids:
        fetch_and_log(sector_id)

if __name__ == "__main__":
    main()
