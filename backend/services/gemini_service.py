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
        
        # Productos sugeridos por cluster con URLs de imagen
        self.cluster_products = {
            0: {
                "productos": ["Coca-Cola 2L", "Fanta Harmony 500ml", "Sprite Harmony 500ml"],
                "imagenes": [
                    "https://i5.walmartimages.com.mx/gr/images/product-images/img_large/00750105530292L.jpg",
                    "https://mercadomi.com.ec/wp-content/uploads/2024/12/19706P-1.jpg", 
                    "https://micocacola.vtexassets.com/arquivos/ids/198982-800-auto?v=638470725999470000&width=800&height=auto&aspect=true"
                ]
            },
            1: {
                "productos": ["Dasani 500ml", "Powerade Frutas 500ml", "Fuze Tea 500ml"],
                "imagenes": [
                    "https://example.com/dasani-500ml.jpg",
                    "https://example.com/powerade-frutas.jpg",
                    "https://example.com/fuze-tea.jpg"
                ]
            },
            2: {
                "productos": ["Inca Kola 500ml", "Del Valle 1L", "Powerade Manzana 500ml"],
                "imagenes": [
                    "https://metroio.vtexassets.com/arquivos/ids/503952/59539001-01-37679.jpg?v=638381183547530000",
                    "https://images.rappi.com.mx/products/f2ea99f0-f5a8-40e7-9f70-b1be5ded9a74.png",
                    "https://http2.mlstatic.com/D_NQ_NP_653106-MLA47061825203_082021-O.webp"
                ]
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
        products = self.cluster_products.get(cluster_id, self.cluster_products[0])
        
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
        1. Genera un reto comercial ESPECÍFICO y ALCANZABLE para esta tienda
        2. El reto debe estar basado en el cluster y las métricas del cliente
        3. Debe incluir una meta numérica concreta (ejemplo: "vender 50 unidades de...")
        4. Debe ser motivador pero realista
        5. La fecha límite es: {deadline_str}
        
        FORMATO DE RESPUESTA (JSON):
        {{
            "titulo": "Título atractivo del reto",
            "descripcion": "Descripción detallada del reto",
            "meta_numerica": número_objetivo,
            "unidad_medida": "unidades/litros/cajas/etc",
            "producto_objetivo": "nombre del producto",
            "incentivo": "qué gana al completar el reto",
            "fecha_limite": "{deadline_str}",
            "tips": ["tip 1", "tip 2", "tip 3"]
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
        
        fallback_challenges = {
            0: {
                "titulo": "¡Expande tu Portafolio Premium!",
                "descripcion": "Aumenta la variedad de productos premium en tu tienda",
                "meta_numerica": 30,
                "unidad_medida": "unidades",
                "producto_objetivo": products["productos"][0],
                "incentivo": "Descuento especial del 15% en próxima compra",
                "tips": ["Exhibe los productos en lugares visibles", "Ofrece combos atractivos", "Promociona en redes sociales"]
            },
            1: {
                "titulo": "¡Reactivación Total!",
                "descripcion": "Vende productos básicos para reactivar tu tienda",
                "meta_numerica": 20,
                "unidad_medida": "unidades", 
                "producto_objetivo": products["productos"][0],
                "incentivo": "Capacitación gratuita en ventas",
                "tips": ["Mantén stock constante", "Mejora la atención al cliente", "Crea promociones diarias"]
            },
            2: {
                "titulo": "¡Diversifica tu Negocio!",
                "descripcion": "Introduce nuevas marcas para ampliar tu catálogo",
                "meta_numerica": 15,
                "unidad_medida": "unidades",
                "producto_objetivo": products["productos"][0], 
                "incentivo": "Material promocional gratuito",
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