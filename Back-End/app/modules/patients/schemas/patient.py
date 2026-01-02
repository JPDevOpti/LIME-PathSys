from datetime import datetime, date
from typing import Optional
from pydantic import BaseModel, Field, field_validator, model_validator
from pydantic.config import ConfigDict
from enum import Enum

class EntityInfo(BaseModel):
    id: str = Field(..., min_length=1, max_length=50, description="ID de la entidad")
    name: str = Field(..., min_length=2, max_length=100, description="Nombre de la entidad")


class Gender(str, Enum):
    MASCULINO = "Masculino"
    FEMENINO = "Femenino"

class CareType(str, Enum):
    AMBULATORIO = "Ambulatorio"
    HOSPITALIZADO = "Hospitalizado"

class IdentificationType(int, Enum):
    CEDULA_CIUDADANIA = 1
    CEDULA_EXTRANJERIA = 2
    TARJETA_IDENTIDAD = 3
    PASAPORTE = 4
    REGISTRO_CIVIL = 5
    DOCUMENTO_EXTRANJERO = 6
    NIT = 7
    CARNET_DIPLOMATICO = 8
    SALVOCONDUCTO = 9

class Location(BaseModel):
    municipality_code: str = Field(..., min_length=1, max_length=10, description="Código del municipio")
    municipality_name: str = Field(..., min_length=2, max_length=100, description="Nombre del municipio")
    subregion: str = Field(..., min_length=2, max_length=100, description="Subregión")
    address: Optional[str] = Field(None, min_length=5, max_length=200, description="Dirección de residencia")
    
    # Permitir que una cadena vacía se interprete como "sin dirección"
    @field_validator('address', mode='before')
    def normalize_empty_address(cls, v):
        if isinstance(v, str) and v.strip() == "":
            return None
        return v
    
    model_config = ConfigDict(populate_by_name=True)

class LocationUpdate(BaseModel):
    """Esquema para actualizaciones parciales de Location"""
    municipality_code: Optional[str] = Field(None, description="Código del municipio")
    municipality_name: Optional[str] = Field(None, description="Nombre del municipio")
    subregion: Optional[str] = Field(None, description="Subregión")
    address: Optional[str] = Field(None, description="Dirección de residencia")
    
    # Normalizar campos de ubicación: convertir cadenas vacías a None
    @field_validator('municipality_code', mode='before')
    def normalize_municipality_code(cls, v):
        if v is None:
            return None
        if isinstance(v, str):
            v_stripped = v.strip()
            if v_stripped == "":
                return None
            if len(v_stripped) < 1 or len(v_stripped) > 10:
                raise ValueError('El código del municipio debe tener entre 1 y 10 caracteres')
            return v_stripped
        return v
    
    @field_validator('municipality_name', mode='before')
    def normalize_municipality_name(cls, v):
        if v is None:
            return None
        if isinstance(v, str):
            v_stripped = v.strip()
            if v_stripped == "":
                return None
            if len(v_stripped) < 2 or len(v_stripped) > 100:
                raise ValueError('El nombre del municipio debe tener entre 2 y 100 caracteres')
            return v_stripped
        return v
    
    @field_validator('subregion', mode='before')
    def normalize_subregion(cls, v):
        if v is None:
            return None
        if isinstance(v, str):
            v_stripped = v.strip()
            if v_stripped == "":
                return None
            if len(v_stripped) < 2 or len(v_stripped) > 100:
                raise ValueError('La subregión debe tener entre 2 y 100 caracteres')
            return v_stripped
        return v
    
    @field_validator('address', mode='before')
    def normalize_address(cls, v):
        if v is None:
            return None
        if isinstance(v, str):
            v_stripped = v.strip()
            # Si está vacía o tiene menos de 5 caracteres, convertir a None
            if v_stripped == "" or len(v_stripped) < 5:
                return None
            # Validar longitud máxima
            if len(v_stripped) > 200:
                raise ValueError('La dirección no puede tener más de 200 caracteres')
            return v_stripped
        return v
    
    model_config = ConfigDict(populate_by_name=True)

class PatientBase(BaseModel):
    patient_code: str = Field(..., description="Código único del paciente")
    identification_type: IdentificationType = Field(...)
    identification_number: str = Field(..., min_length=5, max_length=12)
    first_name: str = Field(..., min_length=2, max_length=50)
    second_name: Optional[str] = Field(None, min_length=2, max_length=50)
    first_lastname: str = Field(..., min_length=2, max_length=50)
    second_lastname: Optional[str] = Field(None, min_length=2, max_length=50)
    birth_date: Optional[date] = Field(None)
    gender: Gender = Field(...)
    location: Optional[Location] = None
    entity_info: EntityInfo = Field(...)
    care_type: CareType = Field(...)
    observations: Optional[str] = Field(None, max_length=500)

    @field_validator('identification_number', mode='before')
    def validate_identification_number(cls, v):
        if not v or not v.strip():
            raise ValueError('El número de identificación no puede estar vacío')
        # Remove any non-digit characters
        clean_number = ''.join(c for c in str(v) if c.isdigit())
        if not clean_number:
            raise ValueError('El número de identificación debe contener al menos un dígito')
        if len(clean_number) < 5 or len(clean_number) > 12:
            raise ValueError('El número de identificación debe tener entre 5 y 12 dígitos')
        return clean_number

    @field_validator('first_name', 'second_name', 'first_lastname', 'second_lastname', mode='before')
    def validate_name_fields(cls, v):
        if v is not None:
            if not v.strip():
                raise ValueError('El campo de nombre no puede estar vacío')
            # Validate that name contains only letters, spaces, and common name characters
            clean_name = v.strip()
            if not all(c.isalpha() or c.isspace() or c in "'-." for c in clean_name):
                raise ValueError('El campo de nombre solo puede contener letras, espacios, apóstrofes, guiones y puntos')
            return clean_name.title()
        return v
    
    model_config = ConfigDict(populate_by_name=True, use_enum_values=True)

class PatientCreate(PatientBase):
    patient_code: Optional[str] = Field(None, description="Código único del paciente (se genera automáticamente si no se proporciona)")

class PatientUpdate(BaseModel):
    patient_code: Optional[str] = Field(None, description="Código único del paciente")
    identification_type: Optional[IdentificationType] = None
    identification_number: Optional[str] = Field(None, min_length=5, max_length=12)
    first_name: Optional[str] = Field(None, min_length=2, max_length=50)
    second_name: Optional[str] = Field(None, min_length=2, max_length=50)
    first_lastname: Optional[str] = Field(None, min_length=2, max_length=50)
    second_lastname: Optional[str] = Field(None, min_length=2, max_length=50)
    birth_date: Optional[date] = None
    gender: Optional[Gender] = None
    location: Optional[LocationUpdate] = None
    entity_info: Optional[EntityInfo] = None
    care_type: Optional[CareType] = None
    observations: Optional[str] = Field(None, max_length=500)

    @field_validator('identification_number', mode='before')
    def validate_identification_number(cls, v):
        if v is not None:
            if not v.strip():
                raise ValueError('El número de identificación no puede estar vacío')
            clean_number = ''.join(c for c in str(v) if c.isdigit())
            if not clean_number:
                raise ValueError('El número de identificación debe contener al menos un dígito')
            if len(clean_number) < 5 or len(clean_number) > 12:
                raise ValueError('El número de identificación debe tener entre 5 y 12 dígitos')
            return clean_number
        return v

    @field_validator('first_name', 'second_name', 'first_lastname', 'second_lastname', mode='before')
    def validate_name_fields(cls, v):
        if v is not None:
            if not v.strip():
                raise ValueError('El campo de nombre no puede estar vacío')
            clean_name = v.strip()
            if not all(c.isalpha() or c.isspace() or c in "'-." for c in clean_name):
                raise ValueError('El campo de nombre solo puede contener letras, espacios, apóstrofes, guiones y puntos')
            return clean_name.title()
        return v
    
    model_config = ConfigDict(use_enum_values=True)

class PatientResponse(PatientBase):
    id: str = Field(...)
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    model_config = ConfigDict(from_attributes=True, use_enum_values=True)

class PatientSearch(BaseModel):
    search: Optional[str] = Field(None, max_length=100, description="Búsqueda general por nombre o identificación")
    identification_type: Optional[IdentificationType] = None
    identification_number: Optional[str] = Field(None, min_length=1, max_length=12)
    first_name: Optional[str] = Field(None, min_length=1, max_length=50)
    first_lastname: Optional[str] = Field(None, min_length=1, max_length=50)
    birth_date_from: Optional[date] = None
    birth_date_to: Optional[date] = None
    age_min: Optional[int] = Field(None, ge=0, le=150)
    age_max: Optional[int] = Field(None, ge=0, le=150)
    gender: Optional[Gender] = None
    municipality_code: Optional[str] = Field(None, min_length=1, max_length=10)
    municipality_name: Optional[str] = Field(None, min_length=1, max_length=100)
    subregion: Optional[str] = Field(None, min_length=1, max_length=100)
    entity: Optional[str] = Field(None, min_length=1, max_length=100)
    care_type: Optional[CareType] = None
    # Nuevos parámetros para búsqueda por created_at (prioritarios)
    created_at_from: Optional[str] = Field(None, description="Fecha de creación desde en formato YYYY-MM-DD (busca en campo created_at)")
    created_at_to: Optional[str] = Field(None, description="Fecha de creación hasta en formato YYYY-MM-DD (busca en campo created_at)")
    # Parámetros legacy para compatibilidad hacia atrás (deprecated, usar created_at_from/created_at_to)
    date_from: Optional[str] = Field(None, description="[Deprecated] Fecha desde en formato YYYY-MM-DD. Use created_at_from en su lugar.")
    date_to: Optional[str] = Field(None, description="[Deprecated] Fecha hasta en formato YYYY-MM-DD. Use created_at_to en su lugar.")
    skip: int = Field(0, ge=0)
    limit: int = Field(100, ge=1, le=1000)

    @field_validator('search', 'identification_number', 'first_name', 'first_lastname', 'municipality_code', 'municipality_name', 'subregion', 'entity', mode='before')
    def empty_to_none(cls, v):
        if isinstance(v, str) and v.strip() == '':
            return None
        return v

    @model_validator(mode='after')
    def validate_age_range(self):
        if self.age_min is not None and self.age_max is not None and self.age_min > self.age_max:
            raise ValueError('La edad mínima no puede ser mayor que la edad máxima')
        return self

    @field_validator('birth_date_from', 'birth_date_to', mode='before')
    def validate_search_dates(cls, v):
        if v is not None:
            if isinstance(v, str):
                try:
                    return datetime.strptime(v, '%Y-%m-%d').date()
                except ValueError:
                    raise ValueError('La fecha debe estar en formato YYYY-MM-DD')
        return v

    @field_validator('created_at_from', 'created_at_to', 'date_from', 'date_to', mode='before')
    def validate_date_strings(cls, v):
        if v is None:
            return None
        # Convertir a string y limpiar espacios
        v_str = v.strip() if isinstance(v, str) else str(v).strip()
        # Si está vacío después de limpiar, retornar None
        if not v_str:
            return None
        # Validar formato de fecha
        try:
            datetime.strptime(v_str, '%Y-%m-%d')
            return v_str
        except ValueError:
            raise ValueError('La fecha debe estar en formato YYYY-MM-DD')
    
    @model_validator(mode='after')
    def normalize_created_at_dates(self):
        """Prioriza created_at_from/created_at_to sobre date_from/date_to para compatibilidad"""
        if self.created_at_from is None and self.date_from is not None:
            self.created_at_from = self.date_from
        if self.created_at_to is None and self.date_to is not None:
            self.created_at_to = self.date_to
        return self
    
    model_config = ConfigDict(use_enum_values=True)
