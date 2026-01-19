<template>
  <div class="entity-multiselect">
    <!-- Label -->
    <label v-if="label" class="block text-sm font-medium text-gray-700 mb-1">
      {{ label }}
      <span v-if="required" class="text-red-500 ml-1">*</span>
    </label>

    <!-- Container -->
    <div class="relative">
      <!-- Input Area -->
      <div 
        class="relative w-full min-h-[42px] px-3 py-2 bg-white border rounded-lg focus-within:ring-2 focus-within:ring-blue-400 focus-within:border-blue-400 transition-colors flex flex-wrap gap-2 items-center"
        :class="[
          errorString ? 'border-red-300 focus-within:ring-red-500 focus-within:border-red-500' : 'border-gray-300',
          disabled ? 'bg-gray-50 cursor-not-allowed' : 'cursor-text'
        ]"
        @click="focusInput"
      >
        
        <!-- Selected Chips -->
        <span 
          v-for="entity in modelValue" 
          :key="(entity as any).id || (entity as any).codigo"
          class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800"
        >
          {{ (entity as any).nombre || (entity as any).name }}
          <button 
            type="button"
            class="ml-1.5 inline-flex flex-shrink-0 h-4 w-4 items-center justify-center rounded-full text-blue-600 hover:bg-blue-200 hover:text-blue-800 focus:outline-none focus:bg-blue-500 focus:text-white transition-colors"
            @click.stop="removeEntity(entity)"
            @mousedown.prevent
            :disabled="disabled"
            v-if="!disabled"
          >
            <span class="sr-only">Remover</span>
            <svg class="h-2 w-2" stroke="currentColor" fill="none" viewBox="0 0 8 8">
              <path stroke-linecap="round" stroke-width="1.5" d="M1 1l6 6m0-6L1 7" />
            </svg>
          </button>
        </span>

        <!-- Search Input -->
        <input
          ref="inputRef"
          v-model="searchQuery"
          type="text"
          class="flex-1 min-w-[120px] bg-transparent border-none p-0 focus:ring-0 text-sm text-gray-900 placeholder-gray-400"
          :placeholder="modelValue.length === 0 ? placeholder : ''"
          :disabled="disabled"
          @focus="handleFocus"
          @blur="handleBlur"
          @keydown="handleKeyDown"
        />

        <!-- Loading spinner -->
        <div v-if="isLoadingEntities" class="absolute right-3 top-1/2 transform -translate-y-1/2 flex items-center pointer-events-none">
          <svg class="animate-spin h-4 w-4 text-gray-400" fill="none" viewBox="0 0 24 24">
            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
          </svg>
        </div>

      </div>

      <!-- Dropdown options -->
      <div
        v-if="isOpen && !disabled"
        class="absolute z-[99999] w-full mt-1 bg-white border border-gray-300 rounded-lg shadow-lg max-h-60 overflow-y-auto"
      >
        <!-- Loading state -->
        <div v-if="isLoadingEntities" class="px-3 py-2 text-sm text-gray-500 text-center">
          Cargando entidades...
        </div>
        
        <!-- No results -->
        <div v-else-if="filteredOptions.length === 0" class="px-3 py-2 text-sm text-gray-500 text-center">
          {{ searchQuery.trim() ? 'No se encontraron entidades' : 'No hay entidades disponibles' }}
        </div>
        
        <!-- Options -->
        <div
          v-for="(option, index) in filteredOptions"
          :key="option.value"
          :class="[
            'px-3 py-2 text-sm cursor-pointer transition-colors',
            index === highlightedIndex ? 'bg-blue-50 text-blue-900' : 'text-gray-900 hover:bg-gray-100',
            isEntitySelected(option.entity) ? 'bg-blue-50' : ''
          ]"
          @click="toggleOption(option)"
          @mousedown.prevent
          @mouseenter="highlightedIndex = index"
        >
          <div class="flex items-center">
            <!-- Checkbox look -->
            <div class="flex-shrink-0 h-4 w-4 mr-3 border rounded border-gray-300" 
                 :class="{ 'bg-blue-600 border-blue-600': isEntitySelected(option.entity), 'bg-white': !isEntitySelected(option.entity) }">
              <svg v-if="isEntitySelected(option.entity)" class="h-4 w-4 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
              </svg>
            </div>

            <div class="flex flex-col">
              <span class="font-medium" :class="{ 'text-blue-900': isEntitySelected(option.entity) }">{{ option.label }}</span>
              <span v-if="(option.entity as any).codigo || (option.entity as any).id" class="text-xs text-gray-500">{{ (option.entity as any).codigo || (option.entity as any).id }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Help text -->
    <p v-if="helpText" class="mt-1 text-xs text-gray-500">
      {{ helpText }}
    </p>

    <!-- Error message -->
    <p v-if="errorString" class="mt-1 text-sm text-red-600">
      {{ errorString }}
    </p>

    <!-- Load error -->
    <div v-if="loadError" class="mt-3 p-3 bg-amber-50 border border-amber-200 rounded-lg">
      <div class="flex items-center">
        <svg class="w-5 h-5 text-amber-600 mr-2 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"/>
        </svg>
        <div>
          <p class="text-sm text-amber-800">No se pudieron cargar las entidades.</p>
          <button
            @click="reloadEntities"
            class="mt-1 text-sm text-amber-700 hover:text-amber-800 underline font-medium"
          >
            Intentar cargar nuevamente
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref, watch, onMounted } from 'vue'
import type { EntityInfo, SelectOption } from '@/modules/cases/types'
import { useEntityAPI } from '@/modules/cases/composables'

// Props
interface Props {
  modelValue?: EntityInfo[]
  label?: string
  placeholder?: string
  required?: boolean
  disabled?: boolean
  helpText?: string
  errors?: string[]
  autoLoad?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  modelValue: () => [],
  label: '',
  placeholder: 'Buscar y seleccionar entidades...',
  required: false,
  disabled: false,
  helpText: '',
  errors: () => [],
  autoLoad: true
})

// Emits
const emit = defineEmits<{
  'update:modelValue': [entities: EntityInfo[]]
  'load-error': [error: string]
  'load-success': [entities: EntityInfo[]]
}>()

// Composables
const { entities, loadEntities, isLoading: isLoadingEntities } = useEntityAPI()

// Refs
const inputRef = ref<HTMLInputElement>()
const searchQuery = ref('')
const isOpen = ref(false)
const highlightedIndex = ref(-1)
const loadError = ref('')
const isFocused = ref(false)

// Computed
const errorString = computed(() => {
  return Array.isArray(props.errors) ? props.errors.join(', ') : ''
})

// Convert entities to options
const entityOptions = computed((): (SelectOption & { entity: EntityInfo })[] => {
  if (!Array.isArray(entities.value)) {
    return []
  }
  
  return entities.value.map(entity => ({
    value: (entity as any).codigo || (entity as any).id,
    label: (entity as any).nombre || (entity as any).name,
    entity
  }))
})

// Filter options based on search
const filteredOptions = computed((): (SelectOption & { entity: EntityInfo })[] => {
  if (!searchQuery.value.trim()) {
    return entityOptions.value
  }
  
  const query = searchQuery.value.toLowerCase().trim()
  return entityOptions.value.filter(option => {
    const label = option.label.toLowerCase()
    const entity = option.entity as any
    const nombre = (entity.nombre || entity.name || '').toLowerCase()
    const codigo = (entity.codigo || entity.id || '').toLowerCase()
    return label.includes(query) || nombre.includes(query) || codigo.includes(query)
  })
})

// Helper methods
const isEntitySelected = (entity: EntityInfo) => {
  return props.modelValue.some(e => {
    const eId = (e as any).id || (e as any).codigo
    const targetId = (entity as any).id || (entity as any).codigo
    return eId === targetId
  })
}

const focusInput = () => {
  if (props.disabled) return
  inputRef.value?.focus()
}

const handleFocus = () => {
  isFocused.value = true
  isOpen.value = true
}

const handleBlur = () => {
  // Delay slightly to allow click on options to register
  setTimeout(() => {
    isFocused.value = false
    isOpen.value = false
    searchQuery.value = '' // Clear text on blur
  }, 150)
}

const toggleOption = (option: SelectOption & { entity: EntityInfo }) => {
  if (props.disabled) return

  const newSelection = [...props.modelValue]
  const entity = option.entity
  
  if (isEntitySelected(entity)) {
    const index = newSelection.findIndex(e => {
       const eId = (e as any).id || (e as any).codigo
       const targetId = (entity as any).id || (entity as any).codigo
       return eId === targetId
    })
    if (index !== -1) newSelection.splice(index, 1)
  } else {
    newSelection.push(entity)
  }

  emit('update:modelValue', newSelection)
  searchQuery.value = ''
  // Mantener el input enfocado y el menú abierto
  if (inputRef.value) {
    inputRef.value.focus()
  }
  // Force open just in case
  isOpen.value = true
}

const removeEntity = (entity: EntityInfo) => {
  if (props.disabled) return
  const newSelection = [...props.modelValue]
  const index = newSelection.findIndex(e => {
     const eId = (e as any).id || (e as any).codigo
     const targetId = (entity as any).id || (entity as any).codigo
     return eId === targetId
  })
  if (index !== -1) {
    newSelection.splice(index, 1)
    emit('update:modelValue', newSelection)
  }
}

const handleKeyDown = (event: KeyboardEvent) => {
  if (props.disabled) return
  
  switch (event.key) {
    case 'ArrowDown':
      event.preventDefault()
      if (!isOpen.value) isOpen.value = true
      highlightedIndex.value = Math.min(highlightedIndex.value + 1, filteredOptions.value.length - 1)
      break
    case 'ArrowUp':
      event.preventDefault()
      if (!isOpen.value) isOpen.value = true
      highlightedIndex.value = Math.max(highlightedIndex.value - 1, -1)
      break
    case 'Enter':
      event.preventDefault()
      if (isOpen.value && highlightedIndex.value >= 0 && filteredOptions.value[highlightedIndex.value]) {
        toggleOption(filteredOptions.value[highlightedIndex.value])
      }
      break
    case 'Escape':
      isOpen.value = false
      inputRef.value?.blur()
      break
    case 'Backspace':
      if (!searchQuery.value && props.modelValue.length > 0) {
        // Remove last item if backspace pressed with empty search
        const newSelection = [...props.modelValue]
        newSelection.pop()
        emit('update:modelValue', newSelection)
      }
      break
  }
}

const reloadEntities = async () => {
  try {
    loadError.value = ''
    const result = await loadEntities()
    
    if (result.success) {
      emit('load-success', entities.value)
    } else {
      loadError.value = result.message || 'Error al cargar entidades'
      emit('load-error', loadError.value)
    }
  } catch (error: any) {
    const errorMessage = 'Error al cargar la lista de entidades'
    loadError.value = errorMessage
    emit('load-error', errorMessage)
    console.error('Error al recargar entidades:', error)
  }
}



watch(searchQuery, () => {
  if (isFocused.value && searchQuery.value.trim()) {
    isOpen.value = true
    highlightedIndex.value = -1
  }
})

onMounted(async () => {
  if (props.autoLoad && entities.value.length === 0) {
    await reloadEntities()
  }
})
</script>

<style scoped>
/* Scrollbar styling for options list */
.overflow-y-auto::-webkit-scrollbar {
  width: 6px;
}
.overflow-y-auto::-webkit-scrollbar-track {
  background: #f1f1f1;
}
.overflow-y-auto::-webkit-scrollbar-thumb {
  background: #cbd5e1;
  border-radius: 3px;
}
.overflow-y-auto::-webkit-scrollbar-thumb:hover {
  background: #94a3b8;
}
</style>
