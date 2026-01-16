import os
import sys
from pathlib import Path
import asyncio
import pandas as pd
from typing import Optional, List, Dict

# Cargar variables de entorno desde .env (para MONGODB_URL Atlas)
try:
    from dotenv import load_dotenv
    load_dotenv(dotenv_path=Path(__file__).resolve().parent.parent / ".env")
except ImportError:
    print("[WARN] python-dotenv no está instalado. Si hay problemas de conexión, instálalo con 'pip install python-dotenv'.")

# Asegurar que el paquete 'app' sea importable al ejecutar el script directamente
CURRENT_DIR = Path(__file__).resolve().parent
BACKEND_ROOT = CURRENT_DIR.parent
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.config.database import connect_to_mongo, close_mongo_connection
from app.modules.diseases.repositories.disease_repository import DiseaseRepository
from app.modules.diseases.models.disease import DiseaseCreate

def normalize_text(text: str) -> str:
    if text is None or pd.isna(text):
        return None
    return " ".join(str(text).split()).strip()

def process_csv_data(file_path: str) -> List[Dict[str, str]]:
    try:
        df = pd.read_csv(file_path)
        print(f"Archivo CSV cargado. Filas: {len(df)}")
        diseases = []
        for index, row in df.iterrows():
            code = normalize_text(row.get('code'))
            name = normalize_text(row.get('description'))
            table = 'CIE10'
            description = name
            if not code or not name:
                print(f"Fila {index + 1}: Saltada - código o nombre vacío")
                continue
            diseases.append({
                'table': table,
                'code': code,
                'name': name,
                'description': description
            })
        return diseases
    except Exception as e:
        print(f"Error al procesar el archivo CSV: {e}")
        return []

async def import_cie10_from_csv(diseases: List[Dict[str, str]]):
    db = await connect_to_mongo()
    repo = DiseaseRepository(db)
    created = 0
    skipped = 0
    for disease in diseases:
        exists = await repo.get_by_code(disease['code'])
        if exists:
            print(f"[SKIP] {disease['code']} ya existe: {disease['name']}")
            skipped += 1
            continue
        payload = DiseaseCreate(
            table=disease['table'],
            code=disease['code'],
            name=disease['name'],
            description=disease['description'],
            is_active=True
        )
        await repo.create(payload)
        print(f"[OK] Enfermedad creada: {disease['code']} - {disease['name']}")
        created += 1
    await close_mongo_connection()
    print(f"Completado. Creadas: {created}, Saltadas: {skipped}")

def main():
    file_path = os.path.join(CURRENT_DIR, 'cie-10.csv')
    if not os.path.exists(file_path):
        print(f"No se encontró el archivo {file_path}")
        return
    diseases = process_csv_data(file_path)
    if not diseases:
        print("No se pudieron procesar datos del archivo CSV.")
        return
    asyncio.run(import_cie10_from_csv(diseases))

if __name__ == "__main__":
    main()
