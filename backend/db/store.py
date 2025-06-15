import os
from pymongo.mongo_client import MongoClient
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Check if URL and TOKEN is loaded
if not os.getenv('MONGODB_URL'):
    raise ValueError("MONGODB_URL not found. Please check your .env file.")

# Check if URL and TOKEN is loaded
if not os.getenv('MONGODB_DB'):
    raise ValueError("MONGODB_DB not found. Please check your .env file.")

# Conecta al cliente de MongoDB
client = MongoClient(os.getenv('MONGODB_URL'))

# Accede a la base de datos
db = client[os.getenv('MONGODB_DB')]


# Exportar la base de datos
def get_collection(collection_name: str):
    return db[collection_name]