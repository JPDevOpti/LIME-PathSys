<template>
  <transition name="fade-scale">
    <div
      v-if="isOpen"
      :class="['fixed right-0 bottom-0 z-[100000] flex items-center justify-center p-4 bg-black/40 top-16', overlayLeftClass]"
      @click.self="handleClose"
    >
      <div class="relative w-full max-w-md bg-white rounded-2xl shadow-2xl overflow-hidden max-h-[90vh] flex flex-col">
        <button
          @click="handleClose"
          class="absolute top-4 right-4 z-10 p-2 rounded-lg bg-white/90 hover:bg-white transition-all duration-200 text-gray-600 hover:text-gray-800 ring-1 ring-transparent hover:ring-gray-200 hover:scale-105"
          title="Cerrar"
        >
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
        
        <!-- Header -->
        <div class="flex-shrink-0 px-6 py-4 border-b border-gray-200 bg-white rounded-t-2xl">
          <div class="flex items-center space-x-3">
            <div class="flex-shrink-0">
              <div class="w-10 h-10 bg-green-50 rounded-full flex items-center justify-center">
                <CalendarIcon class="w-5 h-5 text-green-600" />
              </div>
            </div>
            <div>
              <h3 class="text-lg font-bold text-gray-900">Gestión de Entrega</h3>
              <p class="text-gray-600 text-xs mt-1">Actualizar información de recepción y entrega</p>
            </div>
          </div>
        </div>

        <!-- Content -->
        <div class="flex-1 overflow-y-auto p-6 space-y-6">
          <div class="bg-gray-50 rounded-2xl border border-gray-200 shadow-sm">
            <div class="p-6 space-y-4">
              <!-- Fecha de Ingreso -->
              <DateInputField
                v-model="formData.entryDate"
                label="Fecha de Ingreso"
                :errors="errors.entryDate ? [errors.entryDate] : []"
                required
              />

              <!-- Recibido Por -->
              <FormInput
                v-model="formData.receivedBy"
                label="Recibido Por"
                placeholder="Nombre de quien recibe"
                :errors="errors.receivedBy ? [errors.receivedBy] : []"
                required
              />

              <!-- Fecha de Entrega -->
              <DateInputField
                v-model="formData.deliveryDate"
                label="Fecha de Entrega"
                :errors="errors.deliveryDate ? [errors.deliveryDate] : []"
                required
              />

              <!-- Entregado A -->
              <FormInputField
                v-model="formData.deliveredTo"
                label="Entregado A"
                placeholder="Ej: IMQ, AMPR"
                :errors="errors.deliveredTo ? [errors.deliveredTo] : []"
                required
              />
            </div>
          </div>
        </div>

        <!-- Footer -->
        <div class="flex-shrink-0 px-6 py-4 border-t border-gray-200 bg-gray-50">
          <div class="flex justify-end gap-3">
            <button
              @click="handleClose"
              class="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
            >
              Cancelar
            </button>
            <SaveButton 
              text="Guardar Cambios"
              size="sm"
              :loading="isSaving"
              :fit-content="true"
              @click="handleSave"
            />
          </div>
        </div>
      </div>
    </div>
  </transition>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { CalendarIcon } from '@/assets/icons'
import { useSidebar } from '@/shared/composables/SidebarControl'
import FormInput from '@/shared/components/ui/forms/FormInput.vue'
import FormInputField from '@/shared/components/ui/forms/FormInputField.vue'
import DateInputField from '@/shared/components/ui/forms/DateInputField.vue'
import SaveButton from '@/shared/components/ui/buttons/SaveButton.vue'
import type { UnreadCase } from '../../types'

interface Props {
  isOpen: boolean
  unreadCase: UnreadCase | null
}

interface FormData {
  entryDate: string
  receivedBy: string
  deliveryDate: string
  deliveredTo: string
}

const props = defineProps<Props>()
const emit = defineEmits<{
  (e: 'close'): void
  (e: 'save', data: Partial<UnreadCase>): void
}>()

const isSaving = ref(false)
const { isExpanded, isMobileOpen, isHovered } = useSidebar()

// Computed class for overlay positioning based on sidebar state
const overlayLeftClass = computed(() => {
  const hasWideSidebar = (isExpanded.value && !isMobileOpen.value) || (!isExpanded.value && isHovered.value)
  return hasWideSidebar ? 'left-0 lg:left-72' : 'left-0 lg:left-20'
})

const formData = ref<FormData>({
  entryDate: '',
  receivedBy: '',
  deliveryDate: '',
  deliveredTo: ''
})

const errors = ref<Record<string, string>>({})

watch(() => props.unreadCase, (newVal) => {
  if (newVal) {
    formData.value = {
      entryDate: newVal.entryDate || '',
      receivedBy: newVal.receivedBy || '',
      deliveryDate: newVal.deliveryDate || new Date().toISOString().split('T')[0],
      deliveredTo: newVal.deliveredTo || ''
    }
  }
}, { immediate: true })

const validateForm = (): boolean => {
  errors.value = {}
  let isValid = true

  if (!formData.value.entryDate) {
    errors.value.entryDate = 'La fecha de ingreso es requerida'
    isValid = false
  }
  if (!formData.value.receivedBy) {
    errors.value.receivedBy = 'Recibido por es requerido'
    isValid = false
  }
  if (!formData.value.deliveryDate) {
    errors.value.deliveryDate = 'La fecha de entrega es requerida'
    isValid = false
  }
  if (!formData.value.deliveredTo) {
    errors.value.deliveredTo = 'Entregado a es requerido'
    isValid = false
  }

  return isValid
}

const handleSave = async () => {
  if (!validateForm()) return

  isSaving.value = true
  emit('save', { ...formData.value })
  // No cerramos aquí, esperamos a que el padre maneje el éxito o error
  // El padre debe cerrar el drawer si todo sale bien
  isSaving.value = false
}

const handleClose = () => {
  if (isSaving.value) return
  emit('close')
}
</script>

<style scoped>
.fade-scale-enter-active,
.fade-scale-leave-active {
  transition: all 0.3s ease;
}

.fade-scale-enter-from,
.fade-scale-leave-to {
  opacity: 0;
  transform: scale(0.95);
}
</style>
