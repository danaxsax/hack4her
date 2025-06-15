from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime
from db.store import get_collection
from ml.cyrce_model import predecir_cluster
from services.gemini_service import gemini_service
from bson import ObjectId
import os
from dotenv import load_dotenv

load_dotenv()

COLLECTION = os.getenv('MONGODB_DB')

chat_router = APIRouter()

class UserMetricsData(BaseModel):
    ticket_promedio: float
    frecuencia_compra: float
    variabilidad: float
    recencia: int
    meses_activo: int
    dist_hospital_m: float
    dist_escuela_m: float
    dist_gimnasio_m: float
    dist_oficina_m: float
    categoria_mas_frecuente: str

class ChallengeProgress(BaseModel):
    challenge_id: str
    progress_data: Dict[str, Any]  # Ej: {"leches_vendidas": 12}
    timestamp: Optional[datetime] = None
    
@chat_router.post("/store")
async def store_user_metrics_and_generate_challenge(data: UserMetricsData):
    try:
        # 1. Preparar datos para el modelo
        data_dict = data.model_dump()
        
        # 2. Predecir cluster usando Cyrce
        cluster_id = predecir_cluster(
            ticket_promedio=data_dict['ticket_promedio'],
            frecuencia_compra=data_dict['frecuencia_compra'],
            variabilidad=data_dict['variabilidad'],
            recencia=data_dict['recencia'],
            meses_activo=data_dict['meses_activo'],
            dist_hospital_m=data_dict['dist_hospital_m'],
            dist_escuela_m=data_dict['dist_escuela_m'],
            dist_gimnasio_m=data_dict['dist_gimnasio_m'],
            dist_oficina_m=data_dict['dist_oficina_m'],
            categoria_mas_frecuente=data_dict['categoria_mas_frecuente']
        )
        
        # Convert numpy int to Python int for MongoDB compatibility
        cluster_id = int(cluster_id)
        
        # Definir información del cluster basada en el ID
        cluster_descriptions = {
            0: {
                "name": "Cluster 0",
                "description": "Cliente tipo 0",
                "recommendation": "Recomendación para cluster 0"
            },
            1: {
                "name": "Cluster 1", 
                "description": "Cliente tipo 1",
                "recommendation": "Recomendación para cluster 1"
            },
            2: {
                "name": "Cluster 2",
                "description": "Cliente tipo 2", 
                "recommendation": "Recomendación para cluster 2"
            },
            3: {
                "name": "Cluster 3",
                "description": "Cliente tipo 3",
                "recommendation": "Recomendación para cluster 3"
            },
            4: {
                "name": "Cluster 4",
                "description": "Cliente tipo 4",
                "recommendation": "Recomendación para cluster 4"
            }
        }
        
        cluster_info = cluster_descriptions.get(cluster_id, {
            "name": f"Cluster {cluster_id}",
            "description": f"Cliente tipo {cluster_id}",
            "recommendation": f"Recomendación para cluster {cluster_id}"
        })
        
        # 3. Generar reto usando Gemini
        challenge = gemini_service.generate_challenge(cluster_info, data_dict)
        
        # 4. Preparar documento para MongoDB
        document = {
            "user_data": data_dict,
            "cluster_id": cluster_id,
            "cluster_info": cluster_info,
            "challenge": challenge,
            "timestamp": datetime.utcnow(),
            "challenge_completed": False,
            "progress_updates": []
        }
        
        # 5. Insertar en MongoDB
        collection = get_collection("user_challenges")
        result = collection.insert_one(document)
        
        return {
            "success": True,
            "message": "Datos procesados y reto generado correctamente",
            "challenge_id": str(result.inserted_id),
            "cluster": {
                "id": cluster_id,
                "name": cluster_info["name"],
                "description": cluster_info["description"],
                "recommendation": cluster_info["recommendation"]
            },
            "challenge": challenge
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al procesar datos: {str(e)}")

@chat_router.post("/challenge/progress")
async def update_challenge_progress(progress: ChallengeProgress):
    try:
        collection = get_collection(COLLECTION)
        
        # Buscar el documento del reto
        challenge_doc = collection.find_one({"_id": ObjectId(progress.challenge_id)})
        if not challenge_doc:
            raise HTTPException(status_code=404, detail="Reto no encontrado")
        
        # Preparar actualización de progreso
        progress_update = {
            "data": progress.progress_data,
            "timestamp": progress.timestamp or datetime.utcnow()
        }
        
        # Verificar si el reto se completó
        challenge_completed = False
        if challenge_doc.get("challenge", {}).get("meta_numerica"):
            meta_numerica = challenge_doc["challenge"]["meta_numerica"]
            # producto_objetivo = challenge_doc["challenge"]["producto_objetivo"]
            
            # Buscar en progress_data una clave que coincida con el producto
            for key, value in progress.progress_data.items():
                if isinstance(value, (int, float)) and value >= meta_numerica:
                    challenge_completed = True
                    break
        
        # Actualizar documento en MongoDB
        update_result = collection.update_one(
            {"_id": ObjectId(progress.challenge_id)},
            {
                "$push": {"progress_updates": progress_update},
                "$set": {"challenge_completed": challenge_completed}
            }
        )
        
        if update_result.modified_count == 0:
            raise HTTPException(status_code=500, detail="No se pudo actualizar el progreso")
        
        return {
            "success": True,
            "message": "Progreso actualizado correctamente",
            "challenge_completed": challenge_completed,
            "progress_data": progress.progress_data
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al actualizar progreso: {str(e)}")

@chat_router.get("/challenge/{challenge_id}")
async def get_challenge_status(challenge_id: str):
    try:
        collection = get_collection("user_challenges")
        
        challenge_doc = collection.find_one({"_id": ObjectId(challenge_id)})
        if not challenge_doc:
            raise HTTPException(status_code=404, detail="Reto no encontrado")
        
        return {
            "challenge_id": challenge_id,
            "cluster": {
                "id": challenge_doc["cluster_id"],
                "info": challenge_doc["cluster_info"]
            },
            "challenge": challenge_doc["challenge"],
            "challenge_completed": challenge_doc.get("challenge_completed", False),
            "progress_updates": challenge_doc.get("progress_updates", []),
            "created_at": challenge_doc["timestamp"]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener estado del reto: {str(e)}")
