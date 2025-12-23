// Resident API composable: load list of residents
import { ref } from 'vue'
import { entitySearchService } from '@/modules/profile/services/entitySearchService'

export interface FormResidentInfo {
  id: string
  resident_code?: string
  resident_name?: string
  nombre: string
  iniciales?: string
  documento: string
  email: string
  medicalLicense?: string
  isActive: boolean
}

export function useResidentAPI() {
  const isLoading = ref(false)
  const error = ref('')
  const residents = ref<FormResidentInfo[]>([])
  let loadPromise: Promise<{ success: boolean; residents?: FormResidentInfo[]; message?: string }> | null = null

  // Transform normalized resident to FormResidentInfo
  const transformResident = (resident: any): FormResidentInfo => {
    return {
      id: resident.id || resident.residenteCode || '',
      resident_code: resident.residenteCode || resident.codigo || resident.id || '',
      resident_name: resident.residenteName || resident.nombre || '',
      nombre: resident.nombre || resident.residenteName || '',
      iniciales: resident.InicialesResidente || resident.iniciales || '',
      documento: resident.documento || resident.codigo || resident.residenteCode || '',
      email: resident.ResidenteEmail || resident.email || '',
      medicalLicense: resident.registro_medico || resident.medical_license || '',
      isActive: resident.isActive !== undefined ? resident.isActive : (resident.activo !== undefined ? resident.activo : true)
    } as FormResidentInfo
  }

  // Load list with simple in-flight dedupe
  const loadResidents = async () => {
    if (loadPromise) return loadPromise
    isLoading.value = true
    error.value = ''
    loadPromise = (async () => {
      try {
        const response = await entitySearchService.getAllResidents(false)
        residents.value = response.map(transformResident)
        return { success: true, residents: residents.value }
      } catch (err: any) {
        error.value = err.message || 'Error al cargar la lista de residentes'
        return { success: false, message: error.value, residents: [] }
      } finally {
        isLoading.value = false
        loadPromise = null
      }
    })()
    return loadPromise
  }

  // Find in loaded list by code/id
  const findSelectedResident = (residentId: string): FormResidentInfo | undefined => {
    return residents.value.find(r => (r as any).resident_code === residentId || (r as any).id === residentId)
  }

  // Clear UI state flags
  const clearState = () => { error.value = ''; isLoading.value = false }

  return {
    isLoading, error, residents, loadResidents,
    findSelectedResident, clearState
  }
}

