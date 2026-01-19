from typing import Optional, Dict, Any
from motor.motor_asyncio import AsyncIOMotorDatabase
from pydantic import EmailStr
from bson import ObjectId


class AuthRepository:
    def __init__(self, db: AsyncIOMotorDatabase) -> None:
        self.db = db
        self.collection = db.get_collection("users")

    async def get_user_by_email(self, email: EmailStr) -> Optional[Dict[str, Any]]:
        # Búsqueda case-insensitive por email para evitar fallos por mayúsculas/minúsculas
        doc = await self.collection.find_one({
            "email": {"$regex": f"^{email}$", "$options": "i"},
            "is_active": True
        })
        if not doc:
            return None
        doc["_id"] = str(doc.get("_id", ""))

        # SI ES BILLING Y NO TIENE ENTIDADES EN USERS, BUSCAR EN COLECCION BILLING
        if doc.get("role") == "billing" and not doc.get("associated_entities"):
            try:
                billing_code = doc.get("billing_code")
                if billing_code:
                    billing_doc = await self.db.get_collection("billing").find_one({"billing_code": billing_code})
                    if billing_doc and billing_doc.get("associated_entities"):
                         doc["associated_entities"] = billing_doc["associated_entities"]
            except Exception:
                pass
                
        return doc

    async def get_user_by_id(self, user_id: str) -> Optional[Dict[str, Any]]:
        try:
            oid = ObjectId(user_id)
        except Exception:
            return None
        doc = await self.collection.find_one({"_id": oid, "is_active": True})
        if not doc:
            return None
        doc["_id"] = str(doc.get("_id", ""))
        
        # SI ES BILLING Y NO TIENE ENTIDADES EN USERS, BUSCAR EN COLECCION BILLING
        if doc.get("role") == "billing" and not doc.get("associated_entities"):
            try:
                billing_code = doc.get("billing_code")
                if billing_code:
                    billing_doc = await self.db.get_collection("billing").find_one({"billing_code": billing_code})
                    if billing_doc and billing_doc.get("associated_entities"):
                         doc["associated_entities"] = billing_doc["associated_entities"]
            except Exception:
                pass

        return doc


