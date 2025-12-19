<template>
  <div class="relative">
    <FormInputField
      :label="label"
      :placeholder="placeholder || 'Seleccione fecha'"
      :type="'text'"
      :required="required"
      :errors="combinedErrors"
      :warnings="warnings"
      :help-text="helpText"
      inputmode="numeric"
      rightAdornmentWidth="1.5rem"
      v-model="displayValue"
      ref="container"
      class="date-input-field"
    />

    <!-- Input nativo oculto para abrir el selector de fecha sin mostrar el icono del navegador -->
    <input
      ref="nativeDateInput"
      type="date"
      class="native-date-input"
      :min="minIso"
      :max="maxIso"
      :value="isoValue"
      @change="onNativeDateChange"
      tabindex="-1"
      aria-hidden="true"
    />

    <button 
      type="button" 
      class="absolute right-2 top-0 h-full flex items-center p-1 text-blue-600 hover:text-blue-700 z-10" 
      @click="openCalendar" 
      aria-label="Abrir calendario"
      :style="buttonStyle"
    >
      <CalendarSearchIcon class="w-5 h-5" aria-hidden="true" />
    </button>
  </div>
  
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'
import FormInputField from './FormInputField.vue'
import CalendarSearchIcon from '@/assets/icons/CalendarSearchIcon.vue'

interface Props {
  modelValue?: string
  label?: string
  placeholder?: string
  required?: boolean
  errors?: string[]
  warnings?: string[]
  helpText?: string
  min?: string
  max?: string
  minYear?: number
  notBefore?: string
  notAfter?: string
}

const props = withDefaults(defineProps<Props>(), {
  modelValue: '',
  label: '',
  placeholder: 'Seleccione fecha',
  required: false,
  errors: () => [],
  warnings: () => [],
  helpText: '',
  min: '',
  max: '',
  minYear: undefined,
  notBefore: '',
  notAfter: ''
})

const emit = defineEmits<{ (e: 'update:modelValue', value: string): void }>()

function isISODateFormat(value: string): boolean {
  return /^\d{4}-\d{2}-\d{2}$/.test(value)
}

function isDisplayDateFormat(value: string): boolean {
  return /^\d{2}\/\d{2}\/\d{4}$/.test(value)
}

function convertDisplayToISO(displayDate: string): string {
  if (!isDisplayDateFormat(displayDate)) return ''
  const [dd, mm, yyyy] = displayDate.split('/')
  return `${yyyy}-${mm}-${dd}`
}

function convertISOToDisplay(isoDate: string): string {
  if (!isISODateFormat(isoDate)) return ''
  const [yyyy, mm, dd] = isoDate.split('-')
  return `${dd}/${mm}/${yyyy}`
}

function normalizeDisplayDate(displayDate: string): string {
  // Si luce como DD/MM/AAAA o MM/DD/AAAA, ajustar a un formato válido DD/MM/AAAA
  if (!isDisplayDateFormat(displayDate)) return displayDate
  const [p1, p2, yyyy] = displayDate.split('/')
  const n1 = Number(p1)
  const n2 = Number(p2)

  // Caso: el usuario escribe MM/DD/AAAA y el “mes” (p2) quedó > 12 -> intercambiar
  if (n2 > 12 && n1 >= 1 && n1 <= 12) {
    return `${p2.padStart(2, '0')}/${p1.padStart(2, '0')}/${yyyy}`
  }

  // Caso: el usuario escribe DD/MM/AAAA (normal), mantener
  return displayDate
}

const displayValue = computed({
  get: () => {
    const value = props.modelValue || ''
    if (!value) return ''
    if (isISODateFormat(value)) return convertISOToDisplay(value)
    if (isDisplayDateFormat(value)) return normalizeDisplayDate(value)
    return value
  },
  set: (val: string) => {
    if (!val) {
      emit('update:modelValue', '')
      return
    }
    // Formatear a DD/MM/AAAA mientras el usuario escribe (ergonomía)
    const digits = val.replace(/\D/g, '').slice(0, 8) // máximo 8 dígitos
    let formatted = ''
    if (digits.length <= 2) {
      formatted = digits
    } else if (digits.length <= 4) {
      formatted = `${digits.slice(0, 2)}/${digits.slice(2)}`
    } else {
      formatted = `${digits.slice(0, 2)}/${digits.slice(2, 4)}/${digits.slice(4)}`
    }
    formatted = normalizeDisplayDate(formatted)
    emit('update:modelValue', formatted)
  }
})

const isoValue = computed(() => {
  const value = props.modelValue || ''
  if (!value) return ''
  if (isISODateFormat(value)) return value
  if (isDisplayDateFormat(value)) return convertDisplayToISO(normalizeDisplayDate(value))
  return ''
})

// Errores combinados: añade validación opcional por año mínimo
const combinedErrors = computed(() => {
  const list = Array.isArray(props.errors) ? [...props.errors] : []
  if (props.minYear && isoValue.value) {
    const iso = isoValue.value
    const year = /^\d{4}-\d{2}-\d{2}$/.test(iso) ? Number(iso.slice(0, 4)) : NaN
    if (!Number.isNaN(year) && year < (props.minYear as number)) {
      list.push(`La fecha no puede ser anterior al año ${props.minYear}`)
    }
  }
  // Comparaciones relativas (aceptan DD/MM/AAAA o ISO)
  const norm = (v: string): string => {
    if (!v) return ''
    if (/^\d{4}-\d{2}-\d{2}$/.test(v)) return v
    if (/^\d{2}\/\d{2}\/\d{4}$/.test(v)) {
      const [dd, mm, yyyy] = v.split('/')
      return `${yyyy}-${mm}-${dd}`
    }
    return ''
  }
  if (isoValue.value) {
    const current = isoValue.value
    const nb = norm(props.notBefore || '')
    const na = norm(props.notAfter || '')
    if (nb && current < nb) {
      const disp = convertISOToDisplay(nb)
      list.push(`La fecha debe ser mayor o igual a ${disp}`)
    }
    if (na && current > na) {
      const disp = convertISOToDisplay(na)
      list.push(`La fecha debe ser menor o igual a ${disp}`)
    }
  }
  return list
})

// min/max: aceptar DD/MM/AAAA y convertir a ISO
const minIso = computed(() => {
  if (!props.min) return ''
  if (isISODateFormat(props.min)) return props.min
  if (isDisplayDateFormat(props.min)) return convertDisplayToISO(props.min)
  return ''
})
const maxIso = computed(() => {
  if (!props.max) return ''
  if (isISODateFormat(props.max)) return props.max
  if (isDisplayDateFormat(props.max)) return convertDisplayToISO(props.max)
  return ''
})

const container = ref<any>(null)
const nativeDateInput = ref<HTMLInputElement | null>(null)

// Calculate button position to align with input field
const buttonStyle = computed(() => {
  // Ajustar alineación vertical del botón del calendario
  const labelHeight = props.label ? '1.5rem' : '0rem'
  const labelSpacing = props.label ? '0.25rem' : '0rem'
  const inputHeight = '2.5rem'
  const nudgePx = -2 // levantar 2px para alinear con adornos derechos

  const topOffset = `calc(${labelHeight} + ${labelSpacing} + ${nudgePx}px)`

  return { top: topOffset, height: inputHeight }
})

function openCalendar() {
  const input = nativeDateInput.value
  if (!input) return

  // Asegurar que el input nativo esté sincronizado antes de abrir
  try { input.value = isoValue.value || '' } catch {}

  if (typeof (input as any).showPicker === 'function') {
    try { (input as any).showPicker() } catch { input.click() }
  } else {
    input.click()
  }
}

function onNativeDateChange(event: Event) {
  const target = event.target as HTMLInputElement
  const iso = target.value || ''
  if (!iso) {
    emit('update:modelValue', '')
    return
  }
  emit('update:modelValue', convertISOToDisplay(iso))
}
</script>

<style scoped>
/* Mantener el input nativo fuera de vista pero disponible para showPicker/click */
.native-date-input {
  position: absolute;
  opacity: 0;
  pointer-events: none;
  width: 1px;
  height: 1px;
  right: 0;
  top: 0;
}
</style>
<style scoped>
/* Ocultar el ícono nativo del navegador para input type="date" (evita doble icono) */
:deep(.date-input-field input[type='date']::-webkit-calendar-picker-indicator) {
  opacity: 0 !important;
  display: none !important;
  width: 0 !important;
  height: 0 !important;
  pointer-events: none !important;
}

/* Chrome/Safari: ocultar botones auxiliares que pueden aparecer */
:deep(.date-input-field input[type='date']::-webkit-clear-button),
:deep(.date-input-field input[type='date']::-webkit-inner-spin-button) {
  display: none !important;
}

/* Quitar apariencia nativa para evitar el icono del input date */
:deep(.date-input-field input[type='date']) {
  -webkit-appearance: none !important;
  appearance: none !important;
  background-image: none !important;
  padding-right: 2.75rem; /* espacio para el botón azul */
}
</style>


