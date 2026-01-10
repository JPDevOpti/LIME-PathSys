
import sys
import asyncio
from pathlib import Path

# Asegurar que el paquete 'app' sea importable
CURRENT_DIR = Path(__file__).resolve().parent
BACKEND_ROOT = CURRENT_DIR.parent
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.config.database import connect_to_mongo, close_mongo_connection
from app.modules.diseases.repositories.disease_repository import DiseaseRepository
from app.modules.diseases.models.disease import DiseaseCreate

async def insert_extras():
    db = await connect_to_mongo()
    repo = DiseaseRepository(db)
    extra_diseases = [
        {
            'table': 'CIE10',
            'code': 'M321',
            'name': 'Lupus eritematoso sistémico con compromiso de órganos o sistemas.',
            'description': 'Lupus eritematoso sistémico con compromiso de órganos o sistemas.'
        },
        {
            'table': 'CIE10',
            'code': 'Z941',
            'name': 'Estado de trasplante de corazón.',
            'description': 'Estado de trasplante de corazón.'
        },
        {
            'table': 'CIE10',
            'code': 'XXX',
            'name': 'ver en ghibs',
            'description': 'ver en ghibs'
        }
    ]
    created = 0
    skipped = 0
    for disease in extra_diseases:
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
    print(f"Completado solo extra. Creadas: {created}, Saltadas: {skipped}")

if __name__ == "__main__":
    asyncio.run(insert_extras())
