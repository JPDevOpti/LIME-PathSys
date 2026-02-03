from typing import List, Dict, Any, Optional
from motor.motor_asyncio import AsyncIOMotorDatabase
from app.modules.cases.repositories.urgent_cases_repository import UrgentCasesRepository


class UrgentCasesService:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.repo = UrgentCasesRepository(db)

    def _extract_test_code(self, test_value: Any) -> Optional[str]:
        if not test_value:
            return None
        raw = str(test_value).strip()
        if not raw:
            return None
        if " - " in raw:
            raw = raw.split(" - ", 1)[0].strip()
        else:
            raw = raw.split(" ", 1)[0].strip()
        return raw.upper() if raw else None

    async def _get_test_times_map(self, items: List[Dict[str, Any]]) -> Dict[str, int]:
        codes: set[str] = set()
        for item in items:
            tests = item.get("tests") or []
            for t in tests:
                code = self._extract_test_code(t)
                if code:
                    codes.add(code)
        if not codes:
            return {}
        cursor = self.db.tests.find(
            {"test_code": {"$in": list(codes)}},
            projection={"test_code": 1, "time": 1, "_id": 0},
        )
        docs = await cursor.to_list(length=None)
        out: Dict[str, int] = {}
        for d in docs:
            code = str(d.get("test_code") or "").upper()
            if not code:
                continue
            try:
                time_val = int(d.get("time"))
            except (TypeError, ValueError):
                continue
            if time_val > 0:
                out[code] = time_val
        return out

    def _resolve_max_time(self, tests: List[Any], time_map: Dict[str, int], default_time: int) -> int:
        max_time = 0
        for t in tests or []:
            code = self._extract_test_code(t)
            if not code:
                continue
            time_val = time_map.get(code, default_time)
            if time_val > max_time:
                max_time = time_val
        return max_time if max_time > 0 else default_time

    async def list_urgent(self, limit: int = 50, min_days: int = 6) -> List[Dict[str, Any]]:
        # Transform repository output (English keys) into Spanish keys for UI/Frontend
        items = await self.repo.find_urgent_cases(limit=limit, min_days=min_days)
        time_map = await self._get_test_times_map(items)
        return [
            {
                "caso_code": i.get("case_code"),
                "paciente_nombre": i.get("patient_name"),
                "paciente_documento": i.get("patient_code"),
                "entidad_nombre": i.get("entity_name"),
                "entidad_codigo": i.get("entity_code"),
                "pruebas": i.get("tests") or [],
                "patologo_nombre": i.get("pathologist_name"),
                "fecha_creacion": i.get("created_at"),
                "estado": i.get("state"),
                "prioridad": i.get("priority"),
                "dias_habiles_transcurridos": i.get("days_in_system") or 0,
                "tiempo_oportunidad_max": self._resolve_max_time(
                    i.get("tests") or [],
                    time_map,
                    min_days,
                ),
            }
            for i in items
        ]

    async def list_urgent_by_pathologist(self, code: str, limit: int = 50, min_days: int = 6) -> List[Dict[str, Any]]:
        # Transform repository output (English keys) into Spanish keys for UI/Frontend
        items = await self.repo.find_urgent_cases(limit=limit, min_days=min_days, pathologist_code=code)
        time_map = await self._get_test_times_map(items)
        return [
            {
                "caso_code": i.get("case_code"),
                "paciente_nombre": i.get("patient_name"),
                "paciente_documento": i.get("patient_code"),
                "entidad_nombre": i.get("entity_name"),
                "entidad_codigo": i.get("entity_code"),
                "pruebas": i.get("tests") or [],
                "patologo_nombre": i.get("pathologist_name"),
                "fecha_creacion": i.get("created_at"),
                "estado": i.get("state"),
                "prioridad": i.get("priority"),
                "dias_habiles_transcurridos": i.get("days_in_system") or 0,
                "tiempo_oportunidad_max": self._resolve_max_time(
                    i.get("tests") or [],
                    time_map,
                    min_days,
                ),
            }
            for i in items
        ]


