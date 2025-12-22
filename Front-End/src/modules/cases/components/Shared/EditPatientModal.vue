<template>
  <Modal v-model="isOpen" title="Editar datos del paciente" size="lg">
    <div v-if="isLoading" class="p-6 text-center text-sm text-gray-600">Cargando datos del paciente...</div>
    <div v-else class="space-y-6">
      <!-- Encabezado visual del paciente -->
      <div class="bg-white rounded-2xl border border-gray-200 overflow-hidden shadow-sm">
        <div class="px-6 py-5 border-b border-gray-200">
          <div class="flex items-start gap-4">
            <div class="flex-shrink-0">
              <div class="w-12 h-12 bg-blue-50 rounded-xl flex items-center justify-center">
                <EditPatientIcon class="w-6 h-6 text-blue-600" />
              </div>
            </div>
            <div class="flex-1 min-w-0">
              <div class="flex flex-col md:flex-row md:items-start md:justify-between gap-3">
                <div class="min-w-0">
                  <h3 class="text-xl font-bold text-gray-900 mb-1">
                    {{ patientDisplayName || 'Paciente' }}
                  </h3>
                  <div class="flex items-center flex-wrap gap-3">
                    <div class="flex items-center gap-1.5">
                      <span class="text-xs text-gray-500 font-medium uppercase tracking-wide">Código</span>
                      <span class="text-lg font-bold text-gray-900 font-mono">
                        {{ patientCode || '' }}
                      </span>
                    </div>
                    <div v-if="patientEntity" class="flex items-center gap-1.5">
                      <span class="text-xs text-gray-500 font-medium uppercase tracking-wide">Entidad</span>
                      <span class="text-sm font-semibold text-gray-900">{{ patientEntity }}</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Contenido del formulario -->
        <div class="px-6 py-5 space-y-6">
          <!-- Sección: Identificación -->
          <div class="space-y-4">
            <div class="flex items-center gap-2">
              <span class="text-xs text-gray-500 font-medium uppercase tracking-wide">Identificación</span>
              <div class="flex-1 h-px bg-gray-200"></div>
            </div>
            <div class="grid grid-cols-1 sm:grid-cols-2 gap-4 sm:gap-6">
              <FormSelect 
                v-model="form.identification_type" 
                label="Tipo de identificación" 
                :options="identificationTypeOptions" 
                placeholder="Seleccione tipo"
                :required="true"
              />
              <FormInputField 
                v-model="form.identification_number" 
                label="Número de identificación" 
                placeholder="Ingrese número de identificación"
                :required="true"
                :max-length="12"
                :only-numbers="true"
              />
            </div>
          </div>
          <!-- Sección: Datos Personales -->
          <div class="space-y-4">
            <div class="flex items-center gap-2">
              <span class="text-xs text-gray-500 font-medium uppercase tracking-wide">Datos Personales</span>
              <div class="flex-1 h-px bg-gray-200"></div>
            </div>
            <div class="grid grid-cols-1 sm:grid-cols-2 gap-4 sm:gap-6">
              <FormInputField 
                v-model="form.first_name" 
                label="Primer nombre" 
                placeholder="Ingrese primer nombre"
                :required="true"
                :max-length="50"
                :only-letters="true"
              />
              <FormInputField 
                v-model="form.second_name" 
                label="Segundo nombre" 
                placeholder="Ingrese segundo nombre"
                :max-length="50"
                :only-letters="true"
              />
              <FormInputField 
                v-model="form.first_lastname" 
                label="Primer apellido" 
                placeholder="Ingrese primer apellido"
                :required="true"
                :max-length="50"
                :only-letters="true"
              />
              <FormInputField 
                v-model="form.second_lastname" 
                label="Segundo apellido" 
                placeholder="Ingrese segundo apellido"
                :max-length="50"
                :only-letters="true"
              />
              <DateInputField 
                v-model="form.birth_date" 
                label="Fecha de nacimiento" 
                :required="true"
                :max="maxBirthDate"
              />
              <FormSelect 
                v-model="form.gender" 
                label="Sexo" 
                :options="genderOptions" 
                placeholder="Seleccione sexo"
                :required="true"
              />
            </div>
          </div>

          <!-- Sección: Ubicación y Contacto -->
          <div class="space-y-4">
            <div class="flex items-center gap-2">
              <span class="text-xs text-gray-500 font-medium uppercase tracking-wide">Ubicación y Contacto</span>
              <div class="flex-1 h-px bg-gray-200"></div>
            </div>
            <div class="grid grid-cols-1 sm:grid-cols-2 gap-4 sm:gap-6">
              <MunicipalityList 
                v-model="form.municipality_code"
                :selectedName="form.municipality_name"
                label="Municipio"
                placeholder="Buscar y seleccionar municipio"
                @municipality-code-change="handleMunicipalityCodeChange"
                @municipality-name-change="handleMunicipalityNameChange"
                @subregion-change="handleSubregionChange"
              />
              <FormInputField 
                v-model="form.address" 
                label="Dirección" 
                placeholder="Dirección del paciente"
                :max-length="200"
              />
            </div>
          </div>

          <!-- Sección: Cobertura y Atención -->
          <div class="space-y-4">
            <div class="flex items-center gap-2">
              <span class="text-xs text-gray-500 font-medium uppercase tracking-wide">Cobertura y Atención</span>
              <div class="flex-1 h-px bg-gray-200"></div>
            </div>
            <div class="grid grid-cols-1 sm:grid-cols-2 gap-4 sm:gap-6">
              <EntityList 
                v-model="form.entity_id"
                label="Entidad"
                placeholder="Buscar y seleccionar entidad"
                :required="true"
                @entity-selected="handleEntitySelected"
              />
              <FormSelect 
                v-model="form.care_type" 
                label="Tipo de atención" 
                :options="careTypeOptions" 
                placeholder="Seleccione tipo"
                :required="true"
              />
            </div>
          </div>

          <!-- Sección: Observaciones -->
          <div class="space-y-4">
            <div class="flex items-center gap-2">
              <span class="text-xs text-gray-500 font-medium uppercase tracking-wide">Observaciones</span>
              <div class="flex-1 h-px bg-gray-200"></div>
            </div>
            <FormTextarea 
              v-model="form.observations" 
              label="Observaciones" 
              placeholder="Observaciones del paciente" 
              :rows="4" 
              :max-length="500" 
            />
          </div>
        </div>
      </div>
    </div>

    <template #footer>
      <div class="px-4 py-3 border-t border-gray-200 bg-gray-50 flex justify-end gap-2 sticky bottom-0 z-10">
        <SaveButton text="Guardar" :loading="isLoading" @click="handleSave" />
      </div>
    </template>
  </Modal>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted } from 'vue'
import { Modal } from '@/shared/components/layout'
import { FormInputField, FormSelect, FormTextarea, DateInputField } from '@/shared/components/ui/forms'
import { MunicipalityList, EntityList } from '@/shared/components/ui/lists'
import { SaveButton } from '@/shared/components/ui/buttons'
import { EditPatientIcon } from '@/assets/icons'
import patientsApiService from '@/modules/patients/services/patientsApi.service'
import { IdentificationType } from '@/modules/patients/types'
import type { PatientData, Gender, CareType, UpdatePatientRequest } from '@/modules/patients/types'
import { useNotifications } from '../../composables/useNotifications'
import casesApiService from '../../services/casesApi.service'

interface Props {
  modelValue: boolean
  patientCode?: string
  patientDisplayName?: string
  patientEntity?: string
  caseCode?: string // Si se proporciona, actualizará el patient_info del caso en lugar del paciente directamente
  casePatientInfo?: any // Información del paciente desde el caso (patient_info)
}

interface Emits {
  (e: 'update:modelValue', value: boolean): void
  (e: 'patient-updated', patient: PatientData): void
  (e: 'case-patient-updated', caseData: any): void // Emitir cuando se actualiza el patient_info del caso
}

const props = defineProps<Props>()
const emit = defineEmits<Emits>()
const { showError, showSuccess } = useNotifications()

const isOpen = computed({
  get: () => props.modelValue,
  set: (value) => emit('update:modelValue', value)
})

const isLoading = ref(false)
const originalPatientData = ref<PatientData | null>(null)
const form = ref({
  patient_code: '',
  identification_type: '' as IdentificationType | '',
  identification_number: '',
  first_name: '',
  second_name: '',
  first_lastname: '',
  second_lastname: '',
  birth_date: '',
  gender: '' as Gender | '',
  municipality_code: '',
  municipality_name: '',
  subregion: '',
  address: '',
  entity_id: '',
  entity_name: '',
  care_type: '' as CareType | '',
  observations: ''
})

const genderOptions = [
  { value: 'Masculino', label: 'Masculino' },
  { value: 'Femenino', label: 'Femenino' }
]

const careTypeOptions = [
  { value: 'Ambulatorio', label: 'Ambulatorio' },
  { value: 'Hospitalizado', label: 'Hospitalizado' }
]

const identificationTypeOptions = [
  { value: IdentificationType.CEDULA_CIUDADANIA, label: 'Cédula de Ciudadanía' },
  { value: IdentificationType.TARJETA_IDENTIDAD, label: 'Tarjeta de Identidad' },
  { value: IdentificationType.CEDULA_EXTRANJERIA, label: 'Cédula de Extranjería' },
  { value: IdentificationType.PASAPORTE, label: 'Pasaporte' },
  { value: IdentificationType.REGISTRO_CIVIL, label: 'Registro Civil' },
  { value: IdentificationType.DOCUMENTO_EXTRANJERO, label: 'Documento Extranjero' },
  { value: IdentificationType.NIT, label: 'NIT' }
]

// Fecha máxima para el campo de nacimiento (hoy)
const maxBirthDate = computed(() => {
  const today = new Date()
  return today.toISOString().split('T')[0]
})

// Utilidad: convertir fechas a ISO (soporta DD/MM/AAAA y MM/DD/AAAA)
const toISODateString = (value: string): string => {
  if (!value) return ''
  // Si ya es ISO
  if (/^\d{4}-\d{2}-\d{2}$/.test(value)) return value
  // Si es DD/MM/AAAA o MM/DD/AAAA
  if (/^\d{2}\/\d{2}\/\d{4}$/.test(value)) {
    const [p1, p2, yyyy] = value.split('/')
    const n1 = Number(p1)
    const n2 = Number(p2)
    // Si el segundo segmento es >12 asumimos que el usuario escribió MM/DD
    if (n2 > 12 && n1 >= 1 && n1 <= 12) {
      return `${yyyy}-${p1.padStart(2, '0')}-${p2.padStart(2, '0')}`
    }
    // Caso normal DD/MM
    return `${yyyy}-${p2.padStart(2, '0')}-${p1.padStart(2, '0')}`
  }
  return ''
}

// Handlers
const handleMunicipalityCodeChange = (code: string) => { form.value.municipality_code = code }
const handleMunicipalityNameChange = (name: string) => { form.value.municipality_name = name }
const handleSubregionChange = (subregion: string) => { form.value.subregion = subregion }
const handleEntitySelected = (entity: any) => {
  if (entity) {
    form.value.entity_id = entity.codigo || entity.id || ''
    form.value.entity_name = entity.nombre || entity.name || ''
  } else {
    form.value.entity_id = ''
    form.value.entity_name = ''
  }
}

// Cargar datos del paciente cuando se abre el modal o cambia el código
watch([() => props.modelValue, () => props.patientCode, () => props.casePatientInfo], async ([isOpen, patientCode, casePatientInfo]) => {
  if (isOpen) {
    // Si tenemos información del paciente desde el caso, usarla (prioridad)
    if (casePatientInfo) {
      // Verificar si los datos han cambiado para evitar recargas innecesarias
      const currentPatientCode = form.value.patient_code || ''
      const newPatientCode = casePatientInfo.patient_code || ''
      
      if (currentPatientCode !== newPatientCode || !originalPatientData.value) {
        loadPatientDataFromCase()
      }
    } else if (patientCode) {
      // Solo cargar si no tenemos datos o si el código cambió
      const needsLoad = !originalPatientData.value || 
                       originalPatientData.value.patient_code !== patientCode ||
                       form.value.patient_code !== patientCode
      
      if (needsLoad && !isLoading.value) {
        await loadPatientData()
      }
    }
  } else if (!isOpen) {
    // Limpiar formulario cuando se cierra el modal
    form.value = {
      patient_code: '',
      identification_type: '' as IdentificationType | '',
      identification_number: '',
      first_name: '',
      second_name: '',
      first_lastname: '',
      second_lastname: '',
      birth_date: '',
      gender: '' as Gender | '',
      municipality_code: '',
      municipality_name: '',
      subregion: '',
      address: '',
      entity_id: '',
      entity_name: '',
      care_type: '' as CareType | '',
      observations: ''
    }
    originalPatientData.value = null
  }
}, { immediate: true, deep: true })

// Cargar datos al montar si el modal ya está abierto
onMounted(() => {
  if (props.modelValue) {
    // Dar un pequeño delay para asegurar que los props estén completamente cargados
    setTimeout(() => {
      if (props.casePatientInfo) {
        loadPatientDataFromCase()
      } else if (props.patientCode && !originalPatientData.value) {
        loadPatientData()
      }
    }, 100)
  }
})

// Calcular edad desde fecha de nacimiento
const calculateAge = (birthDate: string | Date | null | undefined): number => {
  if (!birthDate) return 0
  const date = typeof birthDate === 'string' ? new Date(birthDate) : birthDate
  if (isNaN(date.getTime())) return 0
  const today = new Date()
  let age = today.getFullYear() - date.getFullYear()
  const monthDiff = today.getMonth() - date.getMonth()
  if (monthDiff < 0 || (monthDiff === 0 && today.getDate() < date.getDate())) {
    age--
  }
  return age >= 0 ? age : 0
}

// Función auxiliar para parsear fechas de MongoDB
const parseMongoDate = (dateValue: any): string => {
  if (!dateValue) return ''
  
  try {
    // Si es un objeto Date
    if (dateValue instanceof Date) {
      return dateValue.toISOString().split('T')[0]
    }
    
    // Si es un string ISO
    if (typeof dateValue === 'string') {
      return dateValue.split('T')[0]
    }
    
    // Si es formato MongoDB con $date
    if (dateValue.$date) {
      // Puede ser string ISO o numberLong (timestamp en milisegundos)
      if (typeof dateValue.$date === 'string') {
        return dateValue.$date.split('T')[0]
      }
      // Si es numberLong (timestamp en milisegundos)
      if (dateValue.$date.$numberLong) {
        const timestamp = parseInt(dateValue.$date.$numberLong, 10)
        return new Date(timestamp).toISOString().split('T')[0]
      }
      // Si $date es directamente un número (timestamp)
      if (typeof dateValue.$date === 'number') {
        return new Date(dateValue.$date).toISOString().split('T')[0]
      }
    }
    
    // Si es un número directamente (timestamp en milisegundos)
    if (typeof dateValue === 'number') {
      return new Date(dateValue).toISOString().split('T')[0]
    }
    
    return ''
  } catch (e) {
    console.error('[EditPatientModal] Error al parsear fecha:', dateValue, e)
    return ''
  }
}

// Función auxiliar para parsear nombre completo
const parseFullName = (fullName: string): { first_name: string; second_name: string; first_lastname: string; second_lastname: string } => {
  if (!fullName || !fullName.trim()) {
    return { first_name: '', second_name: '', first_lastname: '', second_lastname: '' }
  }
  
  const nameParts = fullName.trim().split(/\s+/).filter(part => part.length > 0)
  
  if (nameParts.length === 0) {
    return { first_name: '', second_name: '', first_lastname: '', second_lastname: '' }
  }
  
  if (nameParts.length === 1) {
    return { first_name: nameParts[0], second_name: '', first_lastname: '', second_lastname: '' }
  }
  
  if (nameParts.length === 2) {
    return { first_name: nameParts[0], second_name: '', first_lastname: nameParts[1], second_lastname: '' }
  }
  
  if (nameParts.length === 3) {
    return { first_name: nameParts[0], second_name: '', first_lastname: nameParts[1], second_lastname: nameParts[2] }
  }
  
  // Si tiene 4 o más partes, asumimos: primer nombre, segundo nombre (puede ser múltiple), primer apellido, segundo apellido
  // Ejemplo: "Alejandra Palacios Prieto" -> first_name: "Alejandra", first_lastname: "Palacios", second_lastname: "Prieto"
  // Ejemplo: "Juan Carlos Pérez González" -> first_name: "Juan", second_name: "Carlos", first_lastname: "Pérez", second_lastname: "González"
  
  // Si tiene exactamente 4 partes
  if (nameParts.length === 4) {
    return {
      first_name: nameParts[0],
      second_name: nameParts[1],
      first_lastname: nameParts[2],
      second_lastname: nameParts[3]
    }
  }
  
  // Si tiene más de 4 partes, los nombres intermedios van al segundo nombre
  // Ejemplo: "Juan Carlos Alberto Pérez González" -> first_name: "Juan", second_name: "Carlos Alberto", first_lastname: "Pérez", second_lastname: "González"
  return {
    first_name: nameParts[0],
    second_name: nameParts.slice(1, -2).join(' '),
    first_lastname: nameParts[nameParts.length - 2],
    second_lastname: nameParts[nameParts.length - 1]
  }
}

// Cargar datos desde patient_info del caso
const loadPatientDataFromCase = () => {
  const patientInfo = props.casePatientInfo
  if (!patientInfo) {
    console.warn('[EditPatientModal] No hay casePatientInfo para cargar')
    return
  }
  
  // Validar que tenga al menos el patient_code
  if (!patientInfo.patient_code && !patientInfo.identification_number) {
    console.warn('[EditPatientModal] casePatientInfo no tiene información válida:', patientInfo)
    return
  }
  
  isLoading.value = true
  try {
    console.log('[EditPatientModal] Cargando datos del paciente desde caso:', patientInfo)
    console.log('[EditPatientModal] patient_info completo:', JSON.stringify(patientInfo, null, 2))
    
    // Parsear nombre completo
    const fullName = patientInfo.name || ''
    const parsedName = parseFullName(fullName)
    console.log('[EditPatientModal] Nombre parseado:', parsedName)
    
    // Parsear fecha de nacimiento
    let birthDateStr = ''
    if (patientInfo.birth_date) {
      birthDateStr = parseMongoDate(patientInfo.birth_date)
      console.log('[EditPatientModal] Fecha de nacimiento parseada:', birthDateStr, 'desde:', patientInfo.birth_date)
    }
    
    // Si no hay birth_date pero hay age, calcular una fecha aproximada
    // Esto permite que el usuario vea una fecha estimada y pueda corregirla
    if (!birthDateStr && patientInfo.age !== undefined && patientInfo.age !== null && patientInfo.age > 0) {
      const today = new Date()
      const estimatedBirthYear = today.getFullYear() - patientInfo.age
      // Usar el 1 de enero del año estimado como fecha aproximada
      // El usuario puede corregirla si es necesario
      birthDateStr = `${estimatedBirthYear}-01-01`
      console.log('[EditPatientModal] Fecha de nacimiento calculada desde age:', birthDateStr, 'age:', patientInfo.age)
    }
    
    if (!birthDateStr) {
      console.warn('[EditPatientModal] No se pudo obtener fecha de nacimiento ni calcular desde age')
    }
    
    // Extraer tipo y número de identificación
    let identificationType: IdentificationType | '' = ''
    let identificationNumber = ''
    
    // Primero intentar obtenerlos directamente de patient_info
    if (patientInfo.identification_type !== undefined && patientInfo.identification_type !== null) {
      identificationType = patientInfo.identification_type as IdentificationType
      console.log('[EditPatientModal] identification_type encontrado directamente:', identificationType)
    }
    if (patientInfo.identification_number) {
      identificationNumber = String(patientInfo.identification_number)
      console.log('[EditPatientModal] identification_number encontrado directamente:', identificationNumber)
    }
    
    // Si no están presentes directamente, intentar extraerlos del patient_code (formato: "1-123456")
    const patientCode = patientInfo.patient_code || ''
    console.log('[EditPatientModal] patient_code:', patientCode, 'identificationType:', identificationType, 'identificationNumber:', identificationNumber)
    
    if (!identificationType || !identificationNumber) {
      const codeMatch = patientCode.match(/^(\d+)-(.+)$/)
      console.log('[EditPatientModal] Regex match del patient_code:', codeMatch)
      if (codeMatch) {
        const [, typeStr, numberStr] = codeMatch
        if (!identificationType && typeStr) {
          const typeNum = parseInt(typeStr, 10)
          if (!isNaN(typeNum) && typeNum >= 1 && typeNum <= 9) {
            identificationType = typeNum as IdentificationType
            console.log('[EditPatientModal] identification_type extraído del patient_code:', identificationType)
          }
        }
        if (!identificationNumber && numberStr) {
          identificationNumber = numberStr
          console.log('[EditPatientModal] identification_number extraído del patient_code:', identificationNumber)
        }
      }
    }
    
    console.log('[EditPatientModal] Identificación final:', { identificationType, identificationNumber, patient_code: patientCode })
    
    // Información de ubicación
    const location = patientInfo.location || null
    console.log('[EditPatientModal] Location:', location)
    
    // Cargar todos los campos del formulario
    form.value = {
      patient_code: patientInfo.patient_code || '',
      identification_type: identificationType,
      identification_number: identificationNumber,
      first_name: parsedName.first_name,
      second_name: parsedName.second_name,
      first_lastname: parsedName.first_lastname,
      second_lastname: parsedName.second_lastname,
      birth_date: birthDateStr,
      gender: patientInfo.gender || '',
      municipality_code: patientInfo.location?.municipality_code || '',
      municipality_name: patientInfo.location?.municipality_name || '',
      subregion: patientInfo.location?.subregion || '',
      address: patientInfo.location?.address || '',
      entity_id: patientInfo.entity_info?.id || '',
      entity_name: patientInfo.entity_info?.name || '',
      care_type: patientInfo.care_type || '',
      observations: patientInfo.observations || ''
    }
    
    // Guardar referencia para comparaciones
    originalPatientData.value = {
      patient_code: patientInfo.patient_code || '',
      identification_type: identificationType || 0,
      identification_number: identificationNumber,
      first_name: parsedName.first_name,
      second_name: parsedName.second_name || null,
      first_lastname: parsedName.first_lastname,
      second_lastname: parsedName.second_lastname || null,
      birth_date: birthDateStr,
      gender: patientInfo.gender as Gender,
      location: patientInfo.location ? {
        municipality_code: patientInfo.location.municipality_code || '',
        municipality_name: patientInfo.location.municipality_name || '',
        subregion: patientInfo.location.subregion || '',
        address: patientInfo.location.address || null
      } : null,
      entity_info: {
        id: patientInfo.entity_info?.id || '',
        name: patientInfo.entity_info?.name || ''
      },
      care_type: patientInfo.care_type as CareType,
      observations: patientInfo.observations || null
    } as PatientData
    
    console.log('[EditPatientModal] Formulario actualizado desde caso:', form.value)
    console.log('[EditPatientModal] Nombre parseado:', parsedName)
  } catch (e: any) {
    console.error('[EditPatientModal] Error al cargar paciente desde caso:', e)
    showError('Error', `No se pudo cargar los datos del paciente: ${e.message || 'Error desconocido'}`)
  } finally {
    isLoading.value = false
  }
}

const loadPatientData = async () => {
  const codeToLoad = props.patientCode || form.value.patient_code
  if (!codeToLoad) {
    console.warn('[EditPatientModal] No hay código de paciente para cargar')
    return
  }
  
  isLoading.value = true
  try {
    console.log('[EditPatientModal] Cargando datos del paciente:', codeToLoad)
    const patient: PatientData = await patientsApiService.getPatientByCode(codeToLoad)
    console.log('[EditPatientModal] Datos del paciente cargados:', patient)
    
    form.value = {
      patient_code: patient.patient_code || '',
      identification_type: (patient.identification_type as IdentificationType) || '',
      identification_number: patient.identification_number || '',
      first_name: patient.first_name || '',
      second_name: patient.second_name || '',
      first_lastname: patient.first_lastname || '',
      second_lastname: patient.second_lastname || '',
      birth_date: patient.birth_date || '',
      gender: patient.gender || '',
      municipality_code: patient.location?.municipality_code || '',
      municipality_name: patient.location?.municipality_name || '',
      subregion: patient.location?.subregion || '',
      address: patient.location?.address || '',
      entity_id: patient.entity_info?.id || '',
      entity_name: patient.entity_info?.name || '',
      care_type: patient.care_type || '',
      observations: patient.observations || ''
    }
    originalPatientData.value = patient
    console.log('[EditPatientModal] Formulario actualizado:', form.value)
  } catch (e: any) {
    console.error('[EditPatientModal] Error al cargar paciente:', e)
    showError('Error', `No se pudo cargar los datos del paciente: ${e.message || 'Error desconocido'}`)
  } finally {
    isLoading.value = false
  }
}

const handleSave = async () => {
  console.log('[EditPatientModal] handleSave llamado')
  console.log('[EditPatientModal] Estado del formulario:', form.value)
  console.log('[EditPatientModal] caseCode:', props.caseCode)
  console.log('[EditPatientModal] patientCode prop:', props.patientCode)
  
  try {
    if (!form.value.patient_code && !props.patientCode && !props.caseCode) {
      console.error('[EditPatientModal] No se encontró código del paciente ni caseCode')
      showError('Error', 'No se encontró el código del paciente')
      return
    }
    
    const patientCode = form.value.patient_code || props.patientCode || ''
    console.log('[EditPatientModal] patientCode a usar:', patientCode)
    
    // Validar campos requeridos
    console.log('[EditPatientModal] Validando campos...')
    console.log('[EditPatientModal] identification_type:', form.value.identification_type)
    console.log('[EditPatientModal] identification_number:', form.value.identification_number)
    console.log('[EditPatientModal] first_name:', form.value.first_name)
    console.log('[EditPatientModal] first_lastname:', form.value.first_lastname)
    console.log('[EditPatientModal] birth_date:', form.value.birth_date)
    console.log('[EditPatientModal] gender:', form.value.gender)
    console.log('[EditPatientModal] entity_id:', form.value.entity_id)
    console.log('[EditPatientModal] entity_name:', form.value.entity_name)
    console.log('[EditPatientModal] care_type:', form.value.care_type)
  
    if (!form.value.identification_type) {
      console.error('[EditPatientModal] Falta identification_type')
      showError('Error de validación', 'El tipo de identificación es obligatorio')
      return
    }
  
    if (!form.value.identification_number || (typeof form.value.identification_number === 'string' && !form.value.identification_number.trim())) {
      console.error('[EditPatientModal] Falta identification_number')
      showError('Error de validación', 'El número de identificación es obligatorio')
      return
    }
  
    if (!form.value.first_name || (typeof form.value.first_name === 'string' && !form.value.first_name.trim())) {
      console.error('[EditPatientModal] Falta first_name')
      showError('Error de validación', 'El primer nombre es obligatorio')
      return
    }
  
    if (!form.value.first_lastname || (typeof form.value.first_lastname === 'string' && !form.value.first_lastname.trim())) {
      console.error('[EditPatientModal] Falta first_lastname')
      showError('Error de validación', 'El primer apellido es obligatorio')
      return
    }
  
    if (!form.value.birth_date || (typeof form.value.birth_date === 'string' && !form.value.birth_date.trim())) {
      console.error('[EditPatientModal] Falta birth_date')
      showError('Error de validación', 'La fecha de nacimiento es obligatoria. Por favor, ingrésela.')
      return
    }
  
    if (!form.value.gender) {
      console.error('[EditPatientModal] Falta gender')
      showError('Error de validación', 'El género es obligatorio')
      return
    }
  
    if (!form.value.entity_id || (typeof form.value.entity_id === 'string' && !form.value.entity_id.trim())) {
      console.error('[EditPatientModal] Falta entity_id')
      showError('Error de validación', 'La entidad de salud es obligatoria')
      return
    }
  
    if (!form.value.entity_name || (typeof form.value.entity_name === 'string' && !form.value.entity_name.trim())) {
      console.error('[EditPatientModal] Falta entity_name')
      showError('Error de validación', 'El nombre de entidad es obligatorio')
      return
    }
  
    if (!form.value.care_type) {
      console.error('[EditPatientModal] Falta care_type')
      showError('Error de validación', 'El tipo de atención es obligatorio')
      return
    }
  
    // Validar fecha de nacimiento
    const birthDateIso = toISODateString(form.value.birth_date)
    if (!birthDateIso) {
      console.error('[EditPatientModal] birth_date no es válida:', form.value.birth_date)
      showError('Error de validación', 'La fecha de nacimiento no es válida. Por favor, ingrese una fecha válida.')
      return
    }
    
    console.log('[EditPatientModal] birthDateIso:', birthDateIso)
  
    const birthDate = new Date(birthDateIso)
    const today = new Date()
    const age = today.getFullYear() - birthDate.getFullYear()
  
    if (birthDate > today) {
      console.error('[EditPatientModal] birth_date es futura')
      showError('Error de validación', 'La fecha de nacimiento no puede ser futura')
      return
    }
  
    if (age > 120) {
      console.error('[EditPatientModal] age > 120:', age)
      showError('Error de validación', 'La edad no puede ser mayor a 120 años')
      return
    }
  
    // Validar dirección si se proporciona
    if (form.value.address && form.value.address.trim() && form.value.address.trim().length < 5) {
      console.error('[EditPatientModal] address muy corta')
      showError('Error de validación', 'La dirección debe tener al menos 5 caracteres')
      return
    }
  
    console.log('[EditPatientModal] Todas las validaciones pasaron, procesando...')
    isLoading.value = true
  
    // Normalizar valores opcionales: enviar null cuando se limpian para que el backend los elimine
    const secondNameRaw = form.value.second_name.trim()
    const secondLastnameRaw = form.value.second_lastname.trim()
    const observationsRaw = form.value.observations.trim()

    const secondName = secondNameRaw === '' ? null : secondNameRaw
    const secondLastname = secondLastnameRaw === '' ? null : secondLastnameRaw
    const observations = observationsRaw === '' ? null : observationsRaw

    // Validación coherente con backend: si se llena algún campo de ubicación, exigir los obligatorios
    const locCode = form.value.municipality_code.trim()
    const locName = form.value.municipality_name.trim()
    const locSubregion = form.value.subregion.trim()
    const locAddressRaw = form.value.address.trim()

    const hasLocationFields = Boolean(locCode || locName || locSubregion || locAddressRaw)
    const hasRequiredLocation = Boolean(locCode && locName && locSubregion)
    if (hasLocationFields && !hasRequiredLocation) {
      showError('Error de validación', 'Complete código, municipio y subregión para guardar la ubicación')
      isLoading.value = false
      return
    }

    const hadLocation = Boolean(
      originalPatientData.value?.location &&
      (
        originalPatientData.value.location.municipality_code ||
        originalPatientData.value.location.municipality_name ||
        originalPatientData.value.location.subregion ||
        originalPatientData.value.location.address
      )
    )

    // Construir el payload de ubicación: solo incluir address si tiene valor
    const locationPayload: UpdatePatientRequest['location'] = hasRequiredLocation
      ? {
          municipality_code: locCode,
          municipality_name: locName,
          subregion: locSubregion,
          ...(locAddressRaw ? { address: locAddressRaw } : {})
        }
      : (hadLocation ? null : undefined)

    // Paso 1: si cambió la identificación y NO estamos editando desde un caso, validar duplicados
    // Cuando editamos desde un caso, solo actualizamos el patient_info del caso, no el paciente
    if (!props.caseCode && originalPatientData.value && (
      form.value.identification_type !== originalPatientData.value.identification_type ||
      form.value.identification_number !== originalPatientData.value.identification_number
    )) {
      // Validar que no exista otro paciente con la misma identificación
      const exists = await patientsApiService.checkPatientExists(
        form.value.identification_type as IdentificationType,
        form.value.identification_number.trim()
      )
      if (exists) {
        showError('Error de validación', 'Ya existe un paciente con el tipo y número de identificación proporcionados')
        isLoading.value = false
        return
      }

      // Ejecutar cambio de identificación y sincronizar el nuevo código del paciente
      const changedPatient = await patientsApiService.changeIdentification(
        form.value.patient_code || patientCode,
        form.value.identification_type as IdentificationType,
        form.value.identification_number.trim()
      )
      // El backend puede cambiar el patient_code cuando cambia la identificación
      form.value.patient_code = changedPatient.patient_code
      originalPatientData.value = { ...changedPatient }
    }

    const updateData: UpdatePatientRequest = {
      first_name: form.value.first_name.trim(),
      second_name: secondName,
      first_lastname: form.value.first_lastname.trim(),
      second_lastname: secondLastname,
      birth_date: birthDateIso,
      gender: form.value.gender as Gender,
      location: locationPayload,
      entity_info: {
        id: form.value.entity_id.trim(),
        name: form.value.entity_name.trim()
      },
      care_type: form.value.care_type as CareType,
      observations
    }

    // Limpiar claves undefined para evitar validaciones innecesarias
    Object.keys(updateData).forEach((k) => {
      if ((updateData as any)[k] === undefined) delete (updateData as any)[k]
    })

    // Paso 2: actualizar el resto de datos
    if (props.caseCode) {
      // Si tenemos caseCode, actualizar el patient_info del caso
      // Construir el nombre completo
      const nameParts: string[] = []
      if (form.value.first_name.trim()) nameParts.push(form.value.first_name.trim())
      if (form.value.second_name.trim()) nameParts.push(form.value.second_name.trim())
      if (form.value.first_lastname.trim()) nameParts.push(form.value.first_lastname.trim())
      if (form.value.second_lastname.trim()) nameParts.push(form.value.second_lastname.trim())
      const fullName = nameParts.join(' ').trim()
      
      // Calcular edad desde fecha de nacimiento
      const age = calculateAge(birthDateIso)
      
      // Actualizar patient_code si cambió la identificación
      // El patient_code debe seguir el formato: "identification_type-identification_number"
      let finalPatientCode = form.value.patient_code || patientCode
      if (form.value.identification_type && form.value.identification_number.trim()) {
        finalPatientCode = `${form.value.identification_type}-${form.value.identification_number.trim()}`
      }
      
      // Construir patient_info para el caso según el esquema del backend
      // Campos requeridos: patient_code, name, age, gender, entity_info, care_type
      const patientInfoForCase: any = {
        patient_code: finalPatientCode,
        name: fullName,
        age: age,
        gender: form.value.gender as string,
        entity_info: {
          id: form.value.entity_id.trim(),
          name: form.value.entity_name.trim()
        },
        care_type: form.value.care_type as string
      }
      
      // Agregar identification_type y identification_number (opcionales pero recomendados)
      if (form.value.identification_type) {
        patientInfoForCase.identification_type = form.value.identification_type as number
      }
      if (form.value.identification_number.trim()) {
        patientInfoForCase.identification_number = form.value.identification_number.trim()
      }
      
      // Agregar birth_date si está disponible (formato ISO completo para Pydantic)
      if (birthDateIso) {
        // Convertir a formato ISO completo con hora para que Pydantic lo reconozca como datetime
        const birthDateObj = new Date(birthDateIso + 'T00:00:00Z')
        patientInfoForCase.birth_date = birthDateObj.toISOString()
      }
      
      // Agregar observations si tiene valor
      if (observations !== null && observations !== undefined) {
        patientInfoForCase.observations = observations
      }
      
      // Agregar location si tiene los campos requeridos
      if (hasRequiredLocation) {
        patientInfoForCase.location = {
          municipality_code: locCode,
          municipality_name: locName,
          subregion: locSubregion
        }
        // Agregar address solo si tiene valor
        if (locAddressRaw) {
          patientInfoForCase.location.address = locAddressRaw
        }
      } else if (hadLocation) {
        // Si tenía ubicación pero ahora no, eliminar location
        patientInfoForCase.location = null
      }
      
      console.log('[EditPatientModal] Actualizando patient_info del caso:', props.caseCode)
      console.log('[EditPatientModal] patient_info a enviar:', JSON.stringify(patientInfoForCase, null, 2))
      
      // Actualizar el caso con el nuevo patient_info
      const updatedCase = await casesApiService.updateCase(props.caseCode, {
        patient_info: patientInfoForCase
      })
      
      console.log('[EditPatientModal] Caso actualizado exitosamente:', updatedCase)
      
      showSuccess('Paciente actualizado', 'Los datos del paciente en el caso se han actualizado correctamente')
      emit('case-patient-updated', updatedCase)
    } else {
      // Actualizar el paciente directamente
      const updated: PatientData = await patientsApiService.updatePatient(
        form.value.patient_code || patientCode, 
        updateData
      )
      
      // Actualizar originalData para reflejar nuevos datos (incluye identificación ya cambiada)
      originalPatientData.value = { ...updated }

      showSuccess('Paciente actualizado', 'Los datos del paciente se han actualizado correctamente')
      emit('patient-updated', updated)
    }
    
    isOpen.value = false
  } catch (e: any) {
    console.error('[EditPatientModal] Error en handleSave:', e)
    console.error('[EditPatientModal] Stack trace:', e.stack)
    
    let errorMessage = 'No se pudo actualizar el paciente. Por favor, inténtelo nuevamente.'

    // Mensajes específicos para identificación duplicada o cambio fallido
    if (e.message?.includes('Ya existe un paciente')) {
      errorMessage = e.message
    } else if (e.message?.includes('Error al cambiar la identificación')) {
      errorMessage = e.message
    } else if (e.message?.includes('ERR_CONNECTION_REFUSED') || e.code === 'ERR_NETWORK') {
      errorMessage = 'Error de conexión: El servidor no está disponible. Verifique que el backend esté ejecutándose.'
    } else if (e.response?.data?.detail) {
      errorMessage = Array.isArray(e.response.data.detail) 
        ? e.response.data.detail.map((err: any) => err.msg || err.message || String(err)).join(', ')
        : String(e.response.data.detail)
    } else if (e.message) {
      errorMessage = e.message
    }
    
    showError('Error al actualizar', errorMessage)
  } finally {
    isLoading.value = false
    console.log('[EditPatientModal] handleSave finalizado, isLoading:', isLoading.value)
  }
}
</script>

