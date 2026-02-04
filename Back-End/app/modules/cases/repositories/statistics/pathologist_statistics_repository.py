from typing import Dict, Any, List
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorDatabase


class PathologistStatisticsRepository:
    def __init__(self, database: AsyncIOMotorDatabase):
        self.collection = database["cases"]
        self.excluded_entity_code = "HAMA"

    def _exclude_entity_match(self) -> Dict[str, Any]:
        """Excluir entidad por código en entity_info."""
        return {
            "patient_info.entity_info.id": {"$ne": self.excluded_entity_code},
            "patient_info.entity_info.entity_code": {"$ne": self.excluded_entity_code},
            "patient_info.entity_info.code": {"$ne": self.excluded_entity_code},
        }

    def _add_max_time_fields(self, base_pipeline: List[Dict[str, Any]], default_time: int) -> List[Dict[str, Any]]:
        # Agrega tiempo máximo de pruebas por caso usando lookup a tests
        return [
            *base_pipeline,
            {"$unwind": {"path": "$samples", "preserveNullAndEmptyArrays": True}},
            {"$unwind": {"path": "$samples.tests", "preserveNullAndEmptyArrays": True}},
            {
                "$lookup": {
                    "from": "tests",
                    "localField": "samples.tests.id",
                    "foreignField": "test_code",
                    "as": "test_info",
                }
            },
            {"$unwind": {"path": "$test_info", "preserveNullAndEmptyArrays": True}},
            {
                "$group": {
                    "_id": "$_id",
                    "assigned_pathologist": {"$first": "$assigned_pathologist"},
                    "pathologist": {"$first": "$pathologist"},
                    "state": {"$first": "$state"},
                    "created_at": {"$first": "$created_at"},
                    "signed_at": {"$first": "$signed_at"},
                    "business_days": {"$first": "$business_days"},
                    "max_time_raw": {"$max": "$test_info.time"},
                }
            },
            {
                "$addFields": {
                    "max_time": {
                        "$cond": [
                            {"$and": [{"$ne": ["$max_time_raw", None]}, {"$gt": ["$max_time_raw", 0]}]},
                            "$max_time_raw",
                            default_time,
                        ]
                    }
                }
            },
        ]

    # Rendimiento mensual por patólogo (casos completados).
    async def get_pathologist_monthly_performance(
        self,
        month: int,
        year: int,
        threshold_days: int = 7,
        pathologist_name: str = None
    ) -> Dict[str, Any]:
        start_date = datetime(year, month, 1)
        end_date = datetime(year + 1, 1, 1) if month == 12 else datetime(year, month + 1, 1)
        match_conditions = {
            "state": {"$in": ["Completado", "Por entregar"]},
            "created_at": {"$gte": start_date, "$lt": end_date},
            **self._exclude_entity_match()
        }
        if pathologist_name:
            name_regex = {"$regex": pathologist_name.strip(), "$options": "i"}
            match_conditions["$or"] = [
                {"assigned_pathologist.name": name_regex},
                {"pathologist.name": name_regex},
                {"pathologist": name_regex},
            ]
        
        base_pipeline = [
            {"$match": match_conditions},
            {
                "$project": {
                    "assigned_pathologist": 1,
                    "pathologist": 1,
                    "state": 1,
                    "created_at": 1,
                    "business_days": 1,
                    "samples.tests.id": 1,
                }
            },
        ]
        pipeline = [
            *self._add_max_time_fields(base_pipeline, threshold_days),
            {
                "$addFields": {
                    "pathologist_name": {
                        "$ifNull": [
                            "$assigned_pathologist.name",
                            {"$ifNull": ["$pathologist.name", "$pathologist"]},
                        ]
                    },
                    "pathologist_code": {
                        "$ifNull": ["$assigned_pathologist.id", "$pathologist.id"]
                    },
                    "business_days_safe": {"$ifNull": ["$business_days", 0]},
                }
            },
            {"$match": {"pathologist_name": {"$ne": None, "$ne": ""}}},
            {
                "$group": {
                    "_id": {
                        "pathologist_code": "$pathologist_code",
                        "pathologist_name": "$pathologist_name"
                    },
                    "total_cases": {"$sum": 1},
                    "within_opportunity": {
                        "$sum": {
                            "$cond": [
                                {"$lte": ["$business_days_safe", "$max_time"]},
                                1,
                                0
                            ]
                        }
                    },
                    "out_of_opportunity": {
                        "$sum": {
                            "$cond": [
                                {"$gt": ["$business_days_safe", "$max_time"]},
                                1,
                                0
                            ]
                        }
                    },
                    "total_business_days": {"$sum": "$business_days_safe"},
                    "avg_business_days": {"$avg": "$business_days_safe"}
                }
            },
            {
                "$project": {
                    "_id": 0,
                    "code": "$_id.pathologist_code",
                    "name": "$_id.pathologist_name",
                    "withinOpportunity": "$within_opportunity",
                    "outOfOpportunity": "$out_of_opportunity",
                    "averageDays": {"$round": ["$avg_business_days", 2]}
                }
            },
            {"$sort": {"total_cases": -1}}
        ]
        
        results = await self.collection.aggregate(pipeline).to_list(length=None)
        return {"pathologists": results}
    
    # Entidades en las que trabaja un patólogo.
    async def get_pathologist_entities(
        self,
        pathologist_name: str,
        month: int,
        year: int
    ) -> Dict[str, Any]:
        start_date = datetime(year, month, 1)
        end_date = datetime(year + 1, 1, 1) if month == 12 else datetime(year, month + 1, 1)
        
        pipeline = [
            {
                "$match": {
                    "$or": [
                        {"assigned_pathologist.name": {"$regex": pathologist_name.strip(), "$options": "i"}},
                        {"pathologist.name": {"$regex": pathologist_name.strip(), "$options": "i"}},
                        {"pathologist": {"$regex": pathologist_name.strip(), "$options": "i"}},
                    ],
                    "state": {"$in": ["Completado", "Por entregar"]},
                    "created_at": {"$gte": start_date, "$lt": end_date},
                    **self._exclude_entity_match()
                }
            },
            {
                "$group": {
                    "_id": {
                        "entity_name": "$patient_info.entity_info.name",
                        "entity_code": "$patient_info.entity_info.code"
                    },
                    "casesCount": {"$sum": 1}
                }
            },
            {
                "$project": {
                    "_id": 0,
                    "name": "$_id.entity_name",
                    "codigo": "$_id.entity_code",
                    "type": "Institución",
                    "casesCount": 1
                }
            },
            {"$sort": {"casesCount": -1}}
        ]
        
        results = await self.collection.aggregate(pipeline).to_list(length=None)
        return {"entidades": results}
    
    # Pruebas asociadas a un patólogo.
    async def get_pathologist_tests(
        self,
        pathologist_name: str,
        month: int,
        year: int
    ) -> Dict[str, Any]:
        start_date = datetime(year, month, 1)
        end_date = datetime(year + 1, 1, 1) if month == 12 else datetime(year, month + 1, 1)
        
        pipeline = [
            {
                "$match": {
                    "$or": [
                        {"assigned_pathologist.name": {"$regex": pathologist_name.strip(), "$options": "i"}},
                        {"pathologist.name": {"$regex": pathologist_name.strip(), "$options": "i"}},
                        {"pathologist": {"$regex": pathologist_name.strip(), "$options": "i"}},
                    ],
                    "state": {"$in": ["Completado", "Por entregar"]},
                    "created_at": {"$gte": start_date, "$lt": end_date},
                    **self._exclude_entity_match()
                }
            },
            {"$unwind": "$samples"},
            {"$unwind": "$samples.tests"},
            {
                "$group": {
                    "_id": {
                        "test_code": "$samples.tests.id",
                        "test_name": "$samples.tests.name"
                    },
                    "count": {"$sum": 1}
                }
            },
            {
                "$project": {
                    "_id": 0,
                    "name": "$_id.test_name",
                    "codigo": "$_id.test_code",
                    "category": "Laboratorio",
                    "count": 1
                }
            },
            {"$sort": {"count": -1}}
        ]
        
        results = await self.collection.aggregate(pipeline).to_list(length=None)
        return {"pruebas": results}
    
    # Resumen de oportunidad (dentro/fuera) para un patólogo.
    async def get_pathologist_opportunity_summary(
        self,
        pathologist_name: str,
        threshold_days: int = 7
    ) -> Dict[str, Any]:
        base_pipeline = [
            {
                "$match": {
                    "$or": [
                        {"assigned_pathologist.name": pathologist_name.strip()},
                        {"pathologist.name": pathologist_name.strip()},
                        {"pathologist": pathologist_name.strip()},
                    ],
                    "state": {"$in": ["Completado", "Por entregar"]},
                    "created_at": {"$exists": True},
                    **self._exclude_entity_match()
                }
            },
            {
                "$project": {
                    "assigned_pathologist": 1,
                    "pathologist": 1,
                    "state": 1,
                    "created_at": 1,
                    "business_days": 1,
                    "samples.tests.id": 1,
                }
            },
        ]
        pipeline = [
            *self._add_max_time_fields(base_pipeline, threshold_days),
            {
                "$addFields": {
                    "business_days_safe": {"$ifNull": ["$business_days", 0]},
                }
            },
            {
                "$group": {
                    "_id": None,
                    "total_cases": {"$sum": 1},
                    "within_opportunity": {
                        "$sum": {
                            "$cond": [
                                {"$lte": ["$business_days_safe", "$max_time"]},
                                1,
                                0
                            ]
                        }
                    },
                    "out_of_opportunity": {
                        "$sum": {
                            "$cond": [
                                {"$gt": ["$business_days_safe", "$max_time"]},
                                1,
                                0
                            ]
                        }
                    },
                    "avg_business_days": {"$avg": "$business_days_safe"}
                }
            },
            {
                "$project": {
                    "_id": 0,
                    "total": "$total_cases",
                    "within": "$within_opportunity",
                    "out": "$out_of_opportunity",
                    "averageDays": {"$round": ["$avg_business_days", 2]}
                }
            }
        ]
        
        results = await self.collection.aggregate(pipeline).to_list(length=None)
        return results[0] if results else {"total": 0, "within": 0, "out": 0, "averageDays": 0}
    
    # Tendencias mensuales en el año para un patólogo.
    async def get_pathologist_monthly_trends(
        self,
        pathologist_name: str,
        year: int,
        threshold_days: int = 7
    ) -> Dict[str, Any]:
        start_date = datetime(year, 1, 1)
        end_date = datetime(year + 1, 1, 1)
        
        base_pipeline = [
            {
                "$match": {
                    "$or": [
                        {"assigned_pathologist.name": pathologist_name.strip()},
                        {"pathologist.name": pathologist_name.strip()},
                        {"pathologist": pathologist_name.strip()},
                    ],
                    "state": {"$in": ["Completado", "Por entregar"]},
                    "created_at": {"$gte": start_date, "$lt": end_date},
                    **self._exclude_entity_match()
                }
            },
            {
                "$project": {
                    "assigned_pathologist": 1,
                    "pathologist": 1,
                    "state": 1,
                    "created_at": 1,
                    "signed_at": 1,
                    "business_days": 1,
                    "samples.tests.id": 1,
                }
            },
        ]
        pipeline = [
            *self._add_max_time_fields(base_pipeline, threshold_days),
            {
                "$addFields": {
                    "business_days_safe": {"$ifNull": ["$business_days", 0]},
                }
            },
            {
                "$group": {
                    "_id": {
                        "month": {"$month": "$signed_at"},
                        "year": {"$year": "$signed_at"}
                    },
                    "total_cases": {"$sum": 1},
                    "within_opportunity": {
                        "$sum": {
                            "$cond": [
                                {"$lte": ["$business_days_safe", "$max_time"]},
                                1,
                                0
                            ]
                        }
                    },
                    "out_of_opportunity": {
                        "$sum": {
                            "$cond": [
                                {"$gt": ["$business_days_safe", "$max_time"]},
                                1,
                                0
                            ]
                        }
                    },
                    "avg_business_days": {"$avg": "$business_days_safe"}
                }
            },
            {
                "$project": {
                    "_id": 0,
                    "month": "$_id.month",
                    "year": "$_id.year",
                    "total": "$total_cases",
                    "within": "$within_opportunity",
                    "out": "$out_of_opportunity",
                    "averageDays": {"$round": ["$avg_business_days", 2]}
                }
            },
            {"$sort": {"month": 1}}
        ]
        
        results = await self.collection.aggregate(pipeline).to_list(length=None)
        
        # Fill in missing months with zeros
        monthly_data = []
        for month in range(1, 13):
            month_data = next((item for item in results if item["month"] == month), {
                "month": month,
                "year": year,
                "total": 0,
                "within": 0,
                "out": 0,
                "averageDays": 0
            })
            monthly_data.append(month_data)
        
        return {"monthlyTrends": monthly_data}
