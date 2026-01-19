<template>
  <ComponentCard title="Edición de usuarios" description="Selecciona una pestaña, busca y edita el perfil." :dense="true">
    <template #icon>
      <EditPatientIcon class="w-5 h-5 mr-2" />
    </template>
    <div class="border-b border-gray-200 mb-1">
      <nav class="-mb-px flex flex-wrap gap-1 md:gap-4" aria-label="Tabs">
        <button v-for="t in tabs" :key="t.value" type="button"
          class="whitespace-nowrap py-1 px-1 md:px-1 border-b-2 font-medium text-xs md:text-sm" :class="selectedType === t.value
            ? 'border-blue-500 text-blue-600'
            : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'"
          @click="selectType(t.value)">
          {{ t.label }}
        </button>
      </nav>
    </div>

    <div class="space-y-3 md:space-y-4">
      <div>
        <UserSearch :busqueda="searchQuery" :tipo-busqueda="selectedType" :esta-buscando="isSearching"
          :error="searchError" @buscar="onSearch" @limpiar="onClearSearch" />
      </div>

      <div>
        <SearchResults 
          :resultados="filteredResults" 
          :busqueda-realizada="searchPerformed || allResults.length > 0" 
          :esta-buscando="isSearching"
          :selected-id="selectedUser?.id || ''" 
          @usuario-seleccionado="onSelectUserToEdit" 
        />
      </div>

      <div>
        <div v-if="selectedUser">
          <h5 class="text-base font-semibold text-gray-800 dark:text-white/90 mb-4">
            Editando: {{ selectedUser.nombre }}
          </h5>

          <FormEditAuxiliary v-if="selectedUser.tipo === 'auxiliar'" :usuario="selectedUser"
            :usuario-actualizado="userUpdated" :mensaje-exito="updateSuccessMessage" @usuario-actualizado="onUpdateUser" />

          <FormEditBilling v-else-if="selectedUser.tipo === 'facturacion'" v-model="selectedUser"
            @usuario-actualizado="onUpdateUser" />

          <FormEditPathologist v-else-if="selectedUser.tipo === 'patologo'" :usuario="selectedUser"
            :usuario-actualizado="userUpdated" :mensaje-exito="updateSuccessMessage" @usuario-actualizado="onUpdateUser" />

          <FormEditResident v-else-if="selectedUser.tipo === 'residente'" :usuario="selectedUser"
            :usuario-actualizado="userUpdated" :mensaje-exito="updateSuccessMessage" @usuario-actualizado="onUpdateUser" />

          <FormEditEntity v-else-if="selectedUser.tipo === 'entidad'" :usuario="selectedUser"
            :usuario-actualizado="userUpdated" :mensaje-exito="updateSuccessMessage" @usuario-actualizado="onUpdateUser" />

          <FormEditTests v-else-if="selectedUser.tipo === 'pruebas'" :usuario="selectedUser"
            :usuario-actualizado="userUpdated" :mensaje-exito="updateSuccessMessage" @usuario-actualizado="onUpdateUser" />
        </div>

        <div v-if="userUpdated && !selectedUser"
          class="mt-6 p-4 bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800 rounded-lg">
          <p class="text-sm font-medium text-green-800 dark:text-green-200">
            {{ updateSuccessMessage }}
          </p>
        </div>
      </div>
    </div>
  </ComponentCard>
</template>

<script setup lang="ts">
import { computed, ref, watch, onMounted } from 'vue'
import ComponentCard from '@/shared/components/layout/ComponentCard.vue'
import EditPatientIcon from '@/assets/icons/EditPatientIcon.vue'
import UserSearch from './UserSearch.vue'
import SearchResults from './SearchResults.vue'
import FormEditAuxiliary from './FormEditAuxiliary.vue'
import FormEditBilling from './FormEditBilling.vue'
import FormEditPathologist from './FormEditPathologist.vue'
import FormEditResident from './FormEditResident.vue'
import FormEditEntity from './FormEditEntity.vue'
import FormEditTests from './FormEditTests.vue'
import { testSearchService } from '../../services/testSearchService'
import { entitySearchService } from '../../services/entitySearchService'

type UserType = 'auxiliar' | 'facturacion' | 'patologo' | 'residente' | 'entidad' | 'pruebas'

const tabs = [
  { value: 'auxiliar', label: 'Auxiliar administrativo' },
  { value: 'facturacion', label: 'Facturación' },
  { value: 'patologo', label: 'Patólogo' },
  { value: 'residente', label: 'Residente' },
  { value: 'entidad', label: 'Entidad' },
  { value: 'pruebas', label: 'Pruebas' }
] as const

const selectedType = ref<UserType>('auxiliar')
const searchQuery = ref('')
const searchPerformed = ref(false)
const isSearching = ref(false)
const searchError = ref('')
const results = ref<any[]>([])
const allResults = ref<any[]>([])

const selectedUser = ref<any | null>(null)
const userUpdated = ref(false)
const updateSuccessMessage = ref('')

const filteredResults = computed(() => {
  let baseResults = allResults.value.filter(r => r.tipo === selectedType.value)
  
  if (searchQuery.value.trim()) {
    const query = searchQuery.value.toLowerCase().trim()
    baseResults = baseResults.filter(r => {
      const nombre = (r.nombre || '').toLowerCase()
      const codigo = (r.codigo || r.documento || r.nit || '').toLowerCase()
      const email = (r.email || '').toLowerCase()
      return nombre.includes(query) || codigo.includes(query) || email.includes(query)
    })
  }
  
  return baseResults
})

const loadAllProfiles = async (type: UserType, includeInactive: boolean = true) => {
  isSearching.value = true
  searchError.value = ''
  
  try {
    const loadServices = {
      pruebas: () => testSearchService.getAllTests(includeInactive),
      entidad: () => entitySearchService.getAllEntities(includeInactive),
      residente: () => entitySearchService.getAllResidents(includeInactive),
      patologo: () => entitySearchService.getAllPathologists(includeInactive),
      auxiliar: () => entitySearchService.getAllAuxiliaries(includeInactive),
      facturacion: () => entitySearchService.getAllFacturacion(includeInactive)
    }
    
    const loadedResults = await (loadServices[type]?.() || Promise.resolve([]))
    allResults.value = loadedResults
    searchPerformed.value = true
  } catch (error: any) {
    searchError.value = error.message || 'Error al cargar los perfiles. Por favor, inténtelo nuevamente.'
    allResults.value = []
  } finally {
    isSearching.value = false
  }
}

const selectType = async (type: UserType) => {
  selectedType.value = type
  selectedUser.value = null
  searchQuery.value = ''
  await loadAllProfiles(type)
}

const onSearch = (params: { query: string; tipo: string; includeInactive: boolean }) => {
  searchQuery.value = params.query
  searchError.value = ''
}

const onClearSearch = () => {
  searchQuery.value = ''
  selectedUser.value = null
  searchError.value = ''
}

watch(() => selectedType.value, async (newType) => {
  await loadAllProfiles(newType)
})

onMounted(async () => {
  await loadAllProfiles(selectedType.value)
})

const onSelectUserToEdit = (item: any) => {
  const baseFields = {
    id: item.id,
    nombre: item.nombre,
    tipo: item.tipo,
    codigo: item.codigo,
    activo: item.activo,
    email: item.email,
    isActive: item.is_active ?? item.isActive ?? item.activo,
    fecha_creacion: item.created_at ?? item.fecha_creacion,
    fecha_actualizacion: item.updated_at ?? item.fecha_actualizacion
  }

  const typeMappings = {
    pruebas: {
      pruebaCode: item.test_code ?? item.codigo,
      pruebasName: item.name ?? item.nombre,
      pruebasDescription: item.description ?? item.descripcion ?? '',
      tiempo: item.time ?? item.tiempo ?? 1
    },
    entidad: {
      EntidadName: item.name ?? item.nombre,
      EntidadCode: item.entity_code ?? item.codigo,
      observaciones: item.notes ?? item.observaciones ?? ''
    },
    facturacion: {
      facturacionName: item.billing_name ?? item.facturacionName ?? item.nombre,
      facturacionCode: item.billing_code ?? item.facturacionCode ?? item.codigo,
      FacturacionEmail: item.billing_email ?? item.FacturacionEmail ?? item.email,
      observaciones: item.observations ?? item.observaciones ?? '',
      associated_entities: item.associated_entities ?? item.associatedEntities ?? []
    },
    residente: {
      residenteName: item.resident_name ?? item.residenteName ?? item.nombre,
      residenteCode: item.resident_code ?? item.residenteCode ?? item.codigo,
      InicialesResidente: item.initials ?? item.InicialesResidente ?? '',
      ResidenteEmail: item.resident_email ?? item.ResidenteEmail ?? item.email,
      registro_medico: item.medical_license ?? item.registro_medico ?? '',
      observaciones: item.observations ?? item.observaciones ?? ''
    },
    patologo: {
      patologoName: item.pathologist_name ?? item.patologoName ?? item.nombre,
      InicialesPatologo: item.initials ?? item.InicialesPatologo ?? '',
      patologoCode: item.pathologist_code ?? item.patologoCode ?? item.codigo,
      PatologoEmail: item.pathologist_email ?? item.PatologoEmail ?? item.email,
      registro_medico: item.medical_license ?? item.registro_medico ?? '',
      observaciones: item.observations ?? item.observaciones ?? ''
    },
    auxiliar: {
      auxiliarName: item.auxiliar_name ?? item.auxiliarName ?? item.nombre,
      auxiliarCode: item.auxiliar_code ?? item.auxiliarCode ?? item.codigo,
      AuxiliarEmail: item.auxiliar_email ?? item.AuxiliarEmail ?? item.email,
      observaciones: item.observations ?? item.observaciones ?? ''
    }
  }

  selectedUser.value = {
    ...baseFields,
    ...(typeMappings[item.tipo as keyof typeof typeMappings] || {})
  }
  console.log('Selected User for Edit (mapped):', selectedUser.value)
}



const onUpdateUser = async (_data: any) => {
  const tipo = selectedUser.value?.tipo
  const formsWithInternalNotification = ['pruebas', 'entidad', 'residente', 'auxiliar', 'facturacion']
  
  if (formsWithInternalNotification.includes(tipo)) {
    await loadAllProfiles(selectedType.value)
    return
  }
  
  updateSuccessMessage.value = 'Registro actualizado exitosamente'
  userUpdated.value = true
  await loadAllProfiles(selectedType.value)
  setTimeout(() => { selectedUser.value = null }, 700)
  setTimeout(() => { userUpdated.value = false; updateSuccessMessage.value = '' }, 3000)
}
</script>
