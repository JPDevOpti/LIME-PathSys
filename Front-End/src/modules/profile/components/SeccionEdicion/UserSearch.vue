<template>
  <div class="space-y-2">
    <h4 class="text-base font-semibold text-gray-800 mb-1" :id="titleId">{{ searchTitle }}</h4>
    <div class="flex gap-2 items-end">
      <div class="flex-1">
        <FormInput
          v-model="localBusqueda"
          :id="inputId"
          :aria-labelledby="titleId"
          :aria-describedby="error ? errorId : undefined"
          :placeholder="searchPlaceholder"
          :disabled="estaBuscando"
          @input="handleSearch"
        />
      </div>
      <div class="h-12 flex items-center">
        <ClearButton @click="handleClear" :disabled="estaBuscando" />
      </div>
    </div>
    <div v-if="error" :id="errorId" role="alert" class="text-sm text-red-600">{{ error }}</div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch, computed } from 'vue'
import { FormInput } from '@/shared/components/ui/forms'
import { ClearButton } from '@/shared/components/ui/buttons'

type TipoBusqueda = 'auxiliar' | 'facturacion' | 'patologo' | 'residente' | 'entidad' | 'pruebas'

interface BuscarEventPayload {
  query: string
  tipo: TipoBusqueda
  includeInactive: boolean
}

const props = defineProps<{ busqueda: string; tipoBusqueda: TipoBusqueda; estaBuscando: boolean; error: string }>()
const emit = defineEmits<{
  (e: 'buscar', payload: BuscarEventPayload): void
  (e: 'limpiar'): void
}>()

const localBusqueda = ref(props.busqueda)
const uid = Math.random().toString(36).slice(2, 9)
const inputId = `buscador-${uid}`
const titleId = `buscador-title-${uid}`
const errorId = `buscador-error-${uid}`

const SEARCH_META: Record<TipoBusqueda, { title: string; placeholder: string }> = {
  auxiliar: {
    title: 'Filtrar Auxiliares Administrativos',
    placeholder: 'Filtrar por nombre, código o email...'
  },
  facturacion: {
    title: 'Filtrar Usuarios de Facturación',
    placeholder: 'Filtrar por nombre, código o email...'
  },
  patologo: {
    title: 'Filtrar Patólogos',
    placeholder: 'Filtrar por nombre, código, registro médico o email...'
  },
  residente: {
    title: 'Filtrar Residentes',
    placeholder: 'Filtrar por nombre, código, registro médico o email...'
  },
  entidad: {
    title: 'Filtrar Entidades',
    placeholder: 'Filtrar por nombre, código o NIT...'
  },
  pruebas: {
    title: 'Filtrar Pruebas Médicas',
    placeholder: 'Filtrar por nombre o código...'
  }
}

const tipoActual = computed(() => props.tipoBusqueda)
const searchTitle = computed(() => SEARCH_META[tipoActual.value]?.title || 'Filtrar registros')
const searchPlaceholder = computed(() => SEARCH_META[tipoActual.value]?.placeholder || 'Filtrar...')

const handleSearch = () => {
  const query = localBusqueda.value.trim()
  const payload: BuscarEventPayload = {
    query,
    tipo: tipoActual.value,
    includeInactive: true
  }
  emit('buscar', payload)
}

const handleClear = () => {
  localBusqueda.value = ''
  emit('limpiar')
}

watch(() => props.busqueda, v => { if (v !== localBusqueda.value) localBusqueda.value = v })
</script>


