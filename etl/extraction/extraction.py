import logging
import csv
import os
import sys
import re
import requests
import os
from dotenv import load

TOKEN = load.os.getenv('TOKEN')  # Asegúrate de definir tu token en las variables de entorno

LOG_FILE = 'results.log'
CSV_FILE = 'data.csv'

# Lista blanca de clases de actividad permitidas
CLASES_PERMITIDAS = {
    "Cafeterías, fuentes de sodas, neverías, refresquerías y similares",
    "Campamentos y albergues recreativos",
    "Centros nocturnos, discotecas y similares",
    "Comercio al por mayor de abarrotes",
    "Comercio al por mayor de bebidas no alcohólicas y hielo",
    "Comercio al por mayor de botanas y frituras",
    "Comercio al por mayor de otros alimentos",
    "Comercio al por mayor de vinos y licores",
    "Comercio al por menor de bebidas no alcohólicas y hielo",
    "Comercio al por menor de otros alimentos",
    "Comercio al por menor de paletas de hielo y helados",
    "Comercio al por menor en tiendas de abarrotes, ultramarinos y misceláneas",
    "Comercio al por menor en tiendas departamentales",
    "Farmacias con minisúper",
    "Hoteles con otros servicios integrados",
    "Hoteles sin otros servicios integrados",
    "Restaurantes con servicio de preparación de alimentos a la carta o de comida corrida",
    "Restaurantes con servicio de preparación de antojitos",
    "Restaurantes con servicio de preparación de pescados y mariscos",
    "Restaurantes con servicio de preparación de pizzas, hamburguesas, hot dogs y pollos rostizados para llevar",
    "Restaurantes con servicio de preparación de tacos y tortas",
    "Restaurantes que preparan otro tipo de alimentos para llevar",
    "Servicios de comedor para empresas e instituciones",
    "Servicios de preparación de alimentos en unidades móviles",
    "Servicios de preparación de alimentos para ocasiones especiales",
    "Servicios de preparación de otros alimentos para consumo inmediato"
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
sector_ids = [43, 46, 72]
BASE_URL = "https://www.inegi.org.mx/app/api/denue/v1/consulta/BuscarAreaActEstr/19/0/0/0/0/{}/0/0/0/0/1/50000000/0/0/{}"


def fetch_and_log(sector_id):
    url = BASE_URL.format(sector_id, TOKEN)
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()

        with open(CSV_FILE, mode='a', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)

            for entry in data:
                clase_actividad = entry.get("Clase_actividad", "").strip()
                if clase_actividad not in CLASES_PERMITIDAS:
                    continue  # Filtrado

                estrato_original = entry.get("Estrato", "No disponible")
                tamaño_max = extraer_max_estrato(estrato_original)
                nombre = entry.get("Nombre", "No disponible")
                cp = entry.get("CP", "No disponible")
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
