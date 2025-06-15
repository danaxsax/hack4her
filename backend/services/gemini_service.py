import google.generativeai as genai
import os
from datetime import datetime, timedelta
from typing import Dict, Any
import json
from dotenv import load_dotenv

load_dotenv()
KEY = os.getenv('GEMINI')

class GeminiService:
    """
    Servicio para generar retos usando la API de Gemini
    """
    
    def __init__(self):
        self.api_key = KEY
        self.model = genai.GenerativeModel('gemini-pro')
        
        # Mapeo de categorías a tipos de productos
        self.category_to_product_type = {
            'COLAS': 'bebidas_gaseosas',
            'AGUA': 'bebidas_hidratantes', 
            'JUGOS': 'bebidas_naturales',
            'ENERGIZANTES': 'bebidas_energeticas',
            'LACTEOS': 'productos_lacteos',
            'SNACKS': 'productos_snacks'
        }
        
        # Productos sugeridos por cluster y categoría con URLs de imagen
        self.cluster_products = {
            0: {
                "bebidas_gaseosas": {
                    "productos": ["Coca Cola Kaizen Lata", "Coca Cola Original Lata 350ml", "Coca Cola Light", "Coca Cola 300ml", "Fanta Harmony NRJ", "Fanta Misterio", "Fanta Mora Azul", "Fanta MZ Verde", "Fanta Piña", "Schweppes"],
                    "imagenes": [
                        "https://i5.walmartimages.com.mx/gr/images/product-images/img_large/00750105530292L.jpg",
                        "https://mercadomi.com.ec/wp-content/uploads/2024/12/19706P-1.jpg", 
                        "https://micocacola.vtexassets.com/arquivos/ids/198982-800-auto?v=638470725999470000&width=800&height=auto&aspect=true",
                        "https://example.com/coca-cola-300ml.jpg",
                        "https://example.com/fanta-harmony-nrj.jpg",
                        "https://example.com/fanta-misterio.jpg",
                        "https://example.com/fanta-mora-azul.jpg",
                        "https://example.com/fanta-mz-verde.jpg",
                        "https://example.com/fanta-pina.jpg",
                        "https://example.com/schweppes.jpg"
                    ]
                },
                "bebidas_hidratantes": {
                    "productos": ["Dasani Maracuyá", "Dasani 300ml", "Powerade Fruta", "Powerade Lima Limón", "Powerade Manzana", "Powerade Uva"],
                    "imagenes": [
                        "https://example.com/dasani-maracuya.jpg",
                        "https://example.com/dasani-300ml.jpg",
                        "https://example.com/powerade-fruta.jpg",
                        "https://example.com/powerade-lima-limon.jpg",
                        "https://example.com/powerade-manzana.jpg",
                        "https://example.com/powerade-uva.jpg"
                    ]
                },
                "bebidas_naturales": {
                    "productos": ["Del Valle Tpack", "Fuze Tea Coldfill", "JDV NRJA Choice", "Fuze Tea Negro"],
                    "imagenes": [
                        "https://images.rappi.com.mx/products/f2ea99f0-f5a8-40e7-9f70-b1be5ded9a74.png",
                        "https://example.com/fuze-tea-coldfill.jpg",
                        "https://example.com/jdv-nrja-choice.jpg",
                        "https://example.com/fuze-tea-negro.jpg"
                    ]
                },
                "bebidas_energeticas": {
                    "productos": ["Monster Lata", "Sprince Fenix"],
                    "imagenes": [
                        "https://example.com/monster-lata.jpg",
                        "https://example.com/sprince-fenix.jpg"
                    ]
                }
            },
            1: {
                "bebidas_hidratantes": {
                    "productos": ["Dasani 300ml", "Powerade Fruta", "Powerade Lima Limón", "Powerade Manzana", "Powerade Uva"],
                    "imagenes": [
                        "https://example.com/dasani-300ml.jpg",
                        "https://example.com/powerade-fruta.jpg",
                        "https://example.com/powerade-lima-limon.jpg",
                        "https://example.com/powerade-manzana.jpg",
                        "https://example.com/powerade-uva.jpg"
                    ]
                },
                "bebidas_gaseosas": {
                    "productos": ["Coca Cola Original Lata 350ml", "Coca Cola Light", "Fanta Harmony NRJ", "Fanta Misterio", "Fanta Mora Azul"],
                    "imagenes": [
                        "https://example.com/coca-cola-355ml.jpg",
                        "https://example.com/coca-cola-light.jpg",
                        "https://example.com/fanta-harmony-nrj.jpg",
                        "https://example.com/fanta-misterio.jpg",
                        "https://example.com/fanta-mora-azul.jpg"
                    ]
                },
                "bebidas_naturales": {
                    "productos": ["Fuze Tea Coldfill", "Del Valle Tpack", "Fuze Tea Negro"],
                    "imagenes": [
                        "https://example.com/fuze-tea-coldfill.jpg",
                        "https://example.com/del-valle-tpack.jpg",
                        "https://example.com/fuze-tea-negro.jpg"
                    ]
                },
                "bebidas_energeticas": {
                    "productos": ["Monster Lata"],
                    "imagenes": [
                        "https://example.com/monster-lata.jpg"
                    ]
                }
            },
            2: {
                "bebidas_naturales": {
                    "productos": ["Del Valle Tpack", "Fuze Tea Negro", "JDV NRJA Choice", "Fiora Harmony Fresa"],
                    "imagenes": [
                        "https://images.rappi.com.mx/products/f2ea99f0-f5a8-40e7-9f70-b1be5ded9a74.png",
                        "https://example.com/fuze-tea-negro.jpg",
                        "https://example.com/jdv-nrja-choice.jpg",
                        "https://example.com/fiora-harmony-fresa.jpg"
                    ]
                },
                "bebidas_gaseosas": {
                    "productos": ["Coca Cola 300ml", "Fanta Piña", "Fanta MZ Verde", "Schweppes"],
                    "imagenes": [
                        "https://example.com/coca-cola-300ml.jpg",
                        "https://example.com/fanta-pina.jpg",
                        "https://example.com/fanta-mz-verde.jpg",
                        "https://example.com/schweppes.jpg"
                    ]
                },
                "bebidas_hidratantes": {
                    "productos": ["Powerade Manzana", "Powerade Uva", "Dasani Maracuyá"],
                    "imagenes": [
                        "https://http2.mlstatic.com/D_NQ_NP_653106-MLA47061825203_082021-O.webp",
                        "https://example.com/powerade-uva.jpg",
                        "https://example.com/dasani-maracuya.jpg"
                    ]
                },
                "bebidas_energeticas": {
                    "productos": ["Sprince Fenix"],
                    "imagenes": [
                        "https://example.com/sprince-fenix.jpg"
                    ]
                }
            }
        }
    
    def generate_challenge(self, cluster_info: Dict, user_data: Dict) -> Dict[str, Any]:
        """
        Genera un reto personalizado usando Gemini
        """
        # Calcular fecha límite (1 mes desde hoy)
        deadline = datetime.now() + timedelta(days=30)
        deadline_str = deadline.strftime("%Y-%m-%d")
        
        # Obtener productos sugeridos para el cluster
        cluster_id = self._get_cluster_id_from_info(cluster_info)
        cluster_products = self.cluster_products.get(cluster_id, self.cluster_products[0])
        
        # Obtener la categoría más frecuente del usuario
        categoria_frecuente = user_data.get('categoria_mas_frecuente', 'COLAS')
        product_type = self.category_to_product_type.get(categoria_frecuente, 'bebidas_gaseosas')
        
        # Obtener productos específicos para esa categoría
        products = cluster_products.get(product_type, list(cluster_products.values())[0])
        
        # Crear prompt para Gemini
        prompt = f"""
            Eres un experto en estrategias comerciales para tiendas de abarrotes.

            INFORMACIÓN DEL CLIENTE:
            - Cluster: {cluster_info['name']}
            - Descripción: {cluster_info['description']}
            - Recomendación: {cluster_info['recommendation']}
            - Productos distintos promedio: {user_data.get('promedio_productos_distintos', 0)}
            - Meses activos: {user_data.get('meses_activos', 0)}
            - Porcentaje top 1: {user_data.get('promedio_porcentaje_top1', 0)}

            PRODUCTOS SUGERIDOS: {', '.join(products['productos'])}

            INSTRUCCIONES:
            1. Genera un reto de lealtad claro, específico y motivador para esta tienda.
            2. El reto debe estar alineado con el cluster y las métricas del cliente.
            3. La meta debe incluir una cantidad numérica concreta y alcanzable (ejemplo: "Compra 3 cajas de Powerade Mora de 1L").
            4. El sistema de recompensa es siempre a través de puntos canjeables por productos.
            5. Incluye el incentivo detallado (ejemplo: "gana 100 puntos").
            6. El reto debe tener un periodo válido, desde el día 1 hasta el {deadline_str}.
            7. El tono debe ser motivador pero realista, incentivando la participación y compras.

            FORMATO DE RESPUESTA (JSON):
            {{
                "titulo": "Título atractivo del reto",
                "descripcion": "Descripción clara y motivadora del reto, especificando la meta, producto y recompensa en puntos",
                "meta_numerica": número_objetivo,
                "unidad_medida": "unidades/litros/cajas/etc",
                "producto_objetivo": "nombre del producto",
                "incentivo": "qué gana al completar el reto (puntos canjeables por productos)",
                "fecha_limite": "{deadline_str}",
                "tips": ["tip 1 para lograr el reto", "tip 2 para incentivar la compra", "tip 3 para aprovechar el reto"]
            }}

            Responde SOLO con el JSON, sin texto adicional. 

        """
        
        try:
            response = self.model.generate_content(prompt)
            challenge_json = json.loads(response.text.strip())
            
            # Agregar imagen del producto
            challenge_json["imagen_producto"] = products["imagenes"][0]
            challenge_json["productos_sugeridos"] = products["productos"]
            challenge_json["imagenes_productos"] = products["imagenes"]
            
            return challenge_json
            
        except Exception as e:
            # Fallback challenge si falla Gemini
            return self._generate_fallback_challenge(cluster_info, user_data, products, deadline_str)
    
    def _get_cluster_id_from_info(self, cluster_info: Dict) -> int:
        """
        Extrae el ID del cluster basado en el nombre
        """
        name = cluster_info.get('name', '')
        if 'formadas' in name.lower():
            return 0
        elif 'riesgo' in name.lower():
            return 1
        else:
            return 2
    
    def _generate_fallback_challenge(self, cluster_info: Dict, user_data: Dict, products: Dict, deadline: str) -> Dict[str, Any]:
        """
        Genera un reto por defecto si falla la API de Gemini
        """
        cluster_id = self._get_cluster_id_from_info(cluster_info)
        categoria_mas_frecuente = user_data.get('categoria_mas_frecuente', 'COLAS')
        
        # Títulos personalizados por categoría
        category_titles = {
            'COLAS': '¡Domina las Bebidas Gaseosas!',
            'AGUA': '¡Líder en Hidratación!', 
            'JUGOS': '¡Experto en Bebidas Naturales!',
            'ENERGIZANTES': '¡Potencia la Energía!',
            'LACTEOS': '¡Maestro de los Lácteos!',
            'SNACKS': '¡Rey de los Snacks!'
        }
        
        fallback_challenges = {
            0: {
                "titulo": category_titles.get(categoria_mas_frecuente, "¡Expande tu Portafolio Premium!"),
                "descripcion": f"Aumenta las ventas de {categoria_mas_frecuente.lower()} aprovechando tu experiencia en esta categoría",
                "meta_numerica": 30,
                "unidad_medida": "unidades",
                "producto_objetivo": products["productos"][0],
                "incentivo": "Gana 150 puntos canjeables por productos",
                "tips": ["Exhibe los productos en lugares visibles", "Ofrece combos atractivos", "Promociona en redes sociales"]
            },
            1: {
                "titulo": category_titles.get(categoria_mas_frecuente, "¡Reactivación Total!"),
                "descripcion": f"Reactiva tu tienda vendiendo más {categoria_mas_frecuente.lower()}, tu categoría fuerte",
                "meta_numerica": 20,
                "unidad_medida": "unidades", 
                "producto_objetivo": products["productos"][0],
                "incentivo": "Gana 100 puntos canjeables por productos",
                "tips": ["Mantén stock constante", "Mejora la atención al cliente", "Crea promociones diarias"]
            },
            2: {
                "titulo": category_titles.get(categoria_mas_frecuente, "¡Diversifica tu Negocio!"),
                "descripcion": f"Diversifica dentro de {categoria_mas_frecuente.lower()}, donde ya tienes experiencia",
                "meta_numerica": 15,
                "unidad_medida": "unidades",
                "producto_objetivo": products["productos"][0], 
                "incentivo": "Gana 75 puntos canjeables por productos",
                "tips": ["Prueba con pequeñas cantidades", "Pide feedback a tus clientes", "Combina con productos conocidos"]
            }
        }
        
        challenge = fallback_challenges[cluster_id].copy()
        challenge["fecha_limite"] = deadline
        challenge["imagen_producto"] = products["imagenes"][0]
        challenge["productos_sugeridos"] = products["productos"]
        challenge["imagenes_productos"] = products["imagenes"]
        
        return challenge

# Instancia global del servicio
gemini_service = GeminiService()