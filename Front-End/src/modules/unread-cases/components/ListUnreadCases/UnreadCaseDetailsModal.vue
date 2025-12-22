<template>
  <transition name="fade-scale">
    <div 
      v-if="isOpen" 
      class="fixed right-0 bottom-0 z-[10000] flex items-center justify-center p-4 bg-black/40 top-16 left-0 lg:left-[290px]"
      @click.self="$emit('close')"
    >
      <div class="relative w-full max-w-3xl bg-white rounded-2xl shadow-2xl overflow-hidden max-h-[90vh] flex flex-col">
        <!-- Header -->
        <div class="flex-shrink-0 px-6 py-5 border-b border-gray-200 bg-white rounded-t-2xl">
          <div class="flex items-center justify-between">
            <div class="flex items-center space-x-3">
              <div class="flex-shrink-0">
                <div class="w-10 h-10 bg-blue-50 rounded-full flex items-center justify-center">
                  <SpecialCaseIcon class="w-5 h-5 text-blue-600" />
                </div>
              </div>
              <div>
                <h3 class="text-lg font-bold text-gray-900">Detalles del caso sin lectura</h3>
                <p class="text-gray-600 text-xs mt-1">Información completa del caso sin lectura</p>
              </div>
            </div>
            
            <!-- Close button -->
            <button
              @click="$emit('close')"
              class="flex-shrink-0 p-2 rounded-lg bg-gray-100 hover:bg-gray-200 transition-all duration-200 text-gray-600 hover:text-gray-800"
              title="Cerrar"
            >
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
        </div>

        <!-- Content -->
        <div class="flex-1 overflow-y-auto p-6 space-y-6">
          
          <!-- Información del Paciente -->
          <div class="bg-white rounded-2xl border border-gray-200 overflow-hidden shadow-sm">
            <div class="px-6 py-4 border-b border-gray-200 bg-white">
              <div class="flex items-start gap-2">
                <div class="w-8 h-8 bg-blue-50 rounded-lg flex items-center justify-center flex-shrink-0 mt-0.5">
                  <UserCircleIcon class="w-4 h-4 text-blue-600" />
                </div>
                <div>
                  <h4 class="text-sm font-semibold text-gray-900 uppercase tracking-wide">Información del Paciente</h4>
                  <p class="text-xs text-gray-500 mt-0.5">Datos personales del paciente</p>
                </div>
              </div>
            </div>
            <div class="p-6">
                <div v-if="unreadCase?.isSpecialCase" class="p-4 bg-blue-50 text-blue-700 rounded-lg border border-blue-100 flex items-center gap-3">
                    <SpecialCaseIcon class="w-5 h-5" />
                    <span class="font-medium">Caso Especial (Laboratorio Externo)</span>
                </div>
                <div v-else class="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div>
                        <span class="text-xs font-medium text-gray-500 uppercase tracking-wider">Paciente</span>
                        <p class="mt-1 text-base font-semibold text-gray-900">{{ patientName }}</p>
                    </div>
                    <div>
                        <span class="text-xs font-medium text-gray-500 uppercase tracking-wider">Documento</span>
                        <p class="mt-1 text-base font-medium text-gray-900">{{ patientDocument }}</p>
                    </div>
                </div>
            </div>
          </div>

          <!-- Detalles del Caso -->
          <div class="bg-white rounded-2xl border border-gray-200 overflow-hidden shadow-sm">
            <div class="px-6 py-4 border-b border-gray-200 bg-white">
              <div class="flex items-start gap-2">
                <div class="w-8 h-8 bg-indigo-50 rounded-lg flex items-center justify-center flex-shrink-0 mt-0.5">
                  <SpecialCaseIcon class="w-4 h-4 text-indigo-600" />
                </div>
                <div>
                  <h4 class="text-sm font-semibold text-gray-900 uppercase tracking-wide">Detalles del Caso</h4>
                  <p class="text-xs text-gray-500 mt-0.5">Entidad, placas y observaciones</p>
                </div>
              </div>
            </div>
            <div class="p-6">
                <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div class="md:col-span-2">
                        <span class="text-xs font-medium text-gray-500 uppercase tracking-wider">Entidad / Institución</span>
                        <p class="mt-1 text-base font-medium text-gray-900">{{ institution }}</p>
                    </div>
                    <div>
                        <span class="text-xs font-medium text-gray-500 uppercase tracking-wider">Código del Caso</span>
                        <p class="mt-1 text-base font-mono font-medium text-gray-900">{{ caseCode }}</p>
                    </div>
                    <div>
                        <span class="text-xs font-medium text-gray-500 uppercase tracking-wider">Número de Placas</span>
                        <p class="mt-1 text-base font-medium text-gray-900">{{ numberOfPlates }}</p>
                    </div>
                    <div v-if="unreadCase?.notes" class="md:col-span-2">
                        <span class="text-xs font-medium text-gray-500 uppercase tracking-wider">Observaciones</span>
                        <div class="mt-2 p-3 bg-yellow-50 border border-yellow-200 rounded-lg text-sm text-gray-800">
                            {{ unreadCase.notes }}
                        </div>
                    </div>
                </div>
            </div>
          </div>

          <!-- Pruebas Realizadas -->
          <div class="bg-white rounded-2xl border border-gray-200 overflow-hidden shadow-sm">
            <div class="px-6 py-4 border-b border-gray-200 bg-white">
              <div class="flex items-start gap-2">
                <div class="w-8 h-8 bg-purple-50 rounded-lg flex items-center justify-center flex-shrink-0 mt-0.5">
                  <TestIcon class="w-4 h-4 text-purple-600" />
                </div>
                <div>
                  <h4 class="text-sm font-semibold text-gray-900 uppercase tracking-wide">Pruebas Realizadas</h4>
                  <p class="text-xs text-gray-500 mt-0.5">Listado de pruebas solicitadas</p>
                </div>
              </div>
            </div>
            <div class="p-6 space-y-4">
              <!-- Nuevo formato con testGroups -->
              <template v-if="unreadCase?.testGroups && unreadCase.testGroups.length > 0">
                <div v-for="(group, idx) in unreadCase.testGroups" :key="idx" :class="['rounded-lg p-4 border', getTestGroupColorClass(group.type)]">
                  <div class="flex flex-col gap-3">
                    <!-- Tipo de prueba -->
                    <div class="flex items-center justify-between">
                      <p class="text-sm font-semibold" :class="getTestGroupTextClass(group.type)">
                        {{ getTestTypeLabel(group.type) }}
                      </p>
                      <span :class="['px-2 py-1 text-xs font-bold rounded', getTestGroupBadgeClass(group.type)]">
                        {{ getTotalQuantity(group.tests) }} {{ getTotalQuantity(group.tests) === 1 ? 'placa' : 'placas' }}
                      </span>
                    </div>
                    
                    <!-- Lista de pruebas -->
                    <div class="flex flex-wrap gap-2">
                      <span 
                        v-for="(test, testIdx) in group.tests" 
                        :key="testIdx"
                        class="test-badge inline-flex items-center justify-center bg-white/50 font-mono text-xs px-3 py-1.5 rounded-lg border-2 relative min-w-0 transition-all hover:scale-105"
                        :class="getTestBadgeBorderClass(group.type)"
                        :title="getTestTooltip(test)"
                      >
                        <span class="truncate test-code font-semibold">{{ test.code }}</span>
                        <sub v-if="test.quantity > 1" class="absolute -top-1 -right-1 w-5 h-5 rounded-full flex items-center justify-center text-[10px] font-bold" :class="getTestCountBadgeClass(group.type)">
                          {{ test.quantity }}
                        </sub>
                      </span>
                    </div>
                    
                    <!-- Observaciones generales del grupo -->
                    <p v-if="group.observations" class="text-xs italic mt-3 pt-3 border-t" :class="[getTestGroupTextClass(group.type), 'border-current/20']">
                      <svg class="w-3.5 h-3.5 inline mr-1.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                      </svg>
                      <span class="font-semibold">Observaciones:</span> {{ group.observations }}
                    </p>
                  </div>
                </div>
              </template>

              <!-- Formato antiguo (retrocompatibilidad) -->
              <template v-else>
                <div v-if="lowComplexityIHQ" class="bg-blue-50 rounded-lg p-4 border border-blue-200">
                  <div class="flex items-start justify-between">
                    <div class="flex-1">
                      <p class="text-sm font-semibold text-blue-900 mb-1">Inmunohistoquímicas de Baja Complejidad</p>
                      <p class="text-sm text-blue-800">{{ lowComplexityIHQ }}</p>
                    </div>
                    <span class="ml-3 px-2 py-1 bg-blue-100 text-blue-800 text-xs font-bold rounded">{{ lowComplexityPlates }} placas</span>
                  </div>
                </div>

                <div v-if="highComplexityIHQ" class="bg-purple-50 rounded-lg p-4 border border-purple-200">
                  <div class="flex items-start justify-between">
                    <div class="flex-1">
                      <p class="text-sm font-semibold text-purple-900 mb-1">Inmunohistoquímicas de Alta Complejidad</p>
                      <p class="text-sm text-purple-800">{{ highComplexityIHQ }}</p>
                    </div>
                    <span class="ml-3 px-2 py-1 bg-purple-100 text-purple-800 text-xs font-bold rounded">{{ highComplexityPlates }} placas</span>
                  </div>
                </div>

                <div v-if="specialIHQ" class="bg-orange-50 rounded-lg p-4 border border-orange-200">
                  <div class="flex items-start justify-between">
                    <div class="flex-1">
                      <p class="text-sm font-semibold text-orange-900 mb-1">Inmunohistoquímicas Especiales</p>
                      <p class="text-sm text-orange-800">{{ specialIHQ }}</p>
                    </div>
                    <span class="ml-3 px-2 py-1 bg-orange-100 text-orange-800 text-xs font-bold rounded">{{ specialPlates }} placas</span>
                  </div>
                </div>

                <div v-if="histochemistry" class="bg-green-50 rounded-lg p-4 border border-green-200">
                  <div class="flex items-start justify-between">
                    <div class="flex-1">
                      <p class="text-sm font-semibold text-green-900 mb-1">Histoquímicas</p>
                      <p class="text-sm text-green-800">{{ histochemistry }}</p>
                    </div>
                    <span class="ml-3 px-2 py-1 bg-green-100 text-green-800 text-xs font-bold rounded">{{ histochemistryPlates }} placas</span>
                  </div>
                </div>

                <div v-if="!lowComplexityIHQ && !highComplexityIHQ && !specialIHQ && !histochemistry" class="text-center py-6">
                  <p class="text-gray-500 text-sm">No se han registrado pruebas para este caso sin lectura</p>
                </div>
              </template>

              <!-- Sin pruebas -->
              <div v-if="!unreadCase?.testGroups?.length && !lowComplexityIHQ && !highComplexityIHQ && !specialIHQ && !histochemistry" class="text-center py-8">
                <svg class="w-12 h-12 text-gray-300 mx-auto mb-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
                <p class="text-gray-500 text-sm">No se han registrado pruebas para este caso sin lectura</p>
              </div>
            </div>
          </div>

          <!-- Información de Entrega -->
          <div class="bg-white rounded-2xl border border-gray-200 overflow-hidden shadow-sm">
            <div class="px-6 py-4 border-b border-gray-200 bg-white">
              <div class="flex items-start gap-2">
                <div class="w-8 h-8 bg-green-50 rounded-lg flex items-center justify-center flex-shrink-0 mt-0.5">
                  <CalendarIcon class="w-4 h-4 text-green-600" />
                </div>
                <div>
                  <h4 class="text-sm font-semibold text-gray-900 uppercase tracking-wide">Información de Entrega</h4>
                  <p class="text-xs text-gray-500 mt-0.5">Detalles de recepción y entrega del caso</p>
                </div>
              </div>
            </div>
            <div class="p-6">
                <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div>
                        <span class="text-xs font-medium text-gray-500 uppercase tracking-wider">Fecha de Ingreso</span>
                        <p class="mt-1 text-base font-medium text-gray-900">{{ formatDate(entryDate) }}</p>
                    </div>
                    <div>
                        <span class="text-xs font-medium text-gray-500 uppercase tracking-wider">Recibido Por</span>
                        <p class="mt-1 text-base font-medium text-gray-900">{{ receivedBy }}</p>
                    </div>
                    <div>
                        <span class="text-xs font-medium text-gray-500 uppercase tracking-wider">Fecha de Entrega</span>
                        <p class="mt-1 text-base font-medium text-gray-900">{{ deliveryDate ? formatDate(deliveryDate) : '—' }}</p>
                    </div>
                    <div>
                        <span class="text-xs font-medium text-gray-500 uppercase tracking-wider">Entregado A</span>
                        <p class="mt-1 text-base font-medium text-gray-900">{{ deliveredTo }}</p>
                    </div>
                </div>
            </div>
          </div>

        </div>

        <!-- Footer -->
        <div class="flex-shrink-0 px-6 py-4 border-t border-gray-200 bg-gray-50">
          <div class="flex justify-end gap-3">
            <button
              @click="$emit('close')"
              class="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
            >
              Cerrar
            </button>
            <button
              @click="unreadCase && $emit('edit', unreadCase)"
              :disabled="!unreadCase"
              class="px-4 py-2 text-sm font-medium text-white bg-blue-600 rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Editar
            </button>
          </div>
        </div>
      </div>
    </div>
  </transition>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import type { UnreadCase } from '../../types'
import { SpecialCaseIcon, UserCircleIcon, CalendarIcon, TestIcon } from '@/assets/icons'

interface Props {
  unreadCase: UnreadCase | null
}

const props = defineProps<Props>()
const emit = defineEmits<{
  (e: 'close'): void
  (e: 'edit', unreadCase: UnreadCase): void
}>()

const isOpen = computed(() => props.unreadCase !== null)
const unreadCaseId = computed(() => props.unreadCase?.id || '—')
const caseCode = computed(() => props.unreadCase?.caseCode || '—')
const patientDocument = computed(() => props.unreadCase?.patientDocument || (props.unreadCase?.isSpecialCase ? 'Lab. Externo' : 'Sin documento'))
const patientName = computed(() => props.unreadCase?.patientName || (props.unreadCase?.isSpecialCase ? 'Caso Especial' : 'Sin nombre de paciente'))
const institution = computed(() => props.unreadCase?.institution || '—')
const numberOfPlates = computed(() => props.unreadCase?.numberOfPlates || 0)
const deliveredTo = computed(() => props.unreadCase?.deliveredTo || '—')
const deliveryDate = computed(() => props.unreadCase?.deliveryDate || '')
const entryDate = computed(() => props.unreadCase?.entryDate || '')
const receivedBy = computed(() => props.unreadCase?.receivedBy || '—')
const unreadCaseStatus = computed(() => props.unreadCase?.status || '—')
const lowComplexityIHQ = computed(() => props.unreadCase?.lowComplexityIHQ || null)
const lowComplexityPlates = computed(() => props.unreadCase?.lowComplexityPlates || 0)
const highComplexityIHQ = computed(() => props.unreadCase?.highComplexityIHQ || null)
const highComplexityPlates = computed(() => props.unreadCase?.highComplexityPlates || 0)
const specialIHQ = computed(() => props.unreadCase?.specialIHQ || null)
const specialPlates = computed(() => props.unreadCase?.specialPlates || 0)
const histochemistry = computed(() => props.unreadCase?.histochemistry || null)
const histochemistryPlates = computed(() => props.unreadCase?.histochemistryPlates || 0)

const getStatusClass = (status: string) => {
  const classes: Record<string, string> = {
    'En proceso': 'bg-blue-100 text-blue-800',
    'Completado': 'bg-green-100 text-green-800'
  }
  return classes[status] || 'bg-gray-100 text-gray-800'
}

const formatDate = (date: string) => {
  if (!date) return '—'
  try {
    return new Date(date).toLocaleDateString('es-ES', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    })
  } catch {
    return date
  }
}

const getTestTypeLabel = (type: string) => {
  const labels: Record<string, string> = {
    'LOW_COMPLEXITY_IHQ': 'Inmunohistoquímicas de Baja Complejidad',
    'HIGH_COMPLEXITY_IHQ': 'Inmunohistoquímicas de Alta Complejidad',
    'SPECIAL_IHQ': 'Inmunohistoquímicas Especiales',
    'HISTOCHEMISTRY': 'Histoquímicas'
  }
  return labels[type] || type
}

const getTestGroupColorClass = (type: string) => {
  const classes: Record<string, string> = {
    'LOW_COMPLEXITY_IHQ': 'bg-blue-50 border-blue-200',
    'HIGH_COMPLEXITY_IHQ': 'bg-purple-50 border-purple-200',
    'SPECIAL_IHQ': 'bg-orange-50 border-orange-200',
    'HISTOCHEMISTRY': 'bg-green-50 border-green-200'
  }
  return classes[type] || 'bg-gray-50 border-gray-200'
}

const getTestGroupTextClass = (type: string) => {
  const classes: Record<string, string> = {
    'LOW_COMPLEXITY_IHQ': 'text-blue-900',
    'HIGH_COMPLEXITY_IHQ': 'text-purple-900',
    'SPECIAL_IHQ': 'text-orange-900',
    'HISTOCHEMISTRY': 'text-green-900'
  }
  return classes[type] || 'text-gray-900'
}

const getTestGroupBadgeClass = (type: string) => {
  const classes: Record<string, string> = {
    'LOW_COMPLEXITY_IHQ': 'bg-blue-100 text-blue-800',
    'HIGH_COMPLEXITY_IHQ': 'bg-purple-100 text-purple-800',
    'SPECIAL_IHQ': 'bg-orange-100 text-orange-800',
    'HISTOCHEMISTRY': 'bg-green-100 text-green-800'
  }
  return classes[type] || 'bg-gray-100 text-gray-800'
}

const getTestBadgeBorderClass = (type: string) => {
  const classes: Record<string, string> = {
    'LOW_COMPLEXITY_IHQ': 'border-blue-300',
    'HIGH_COMPLEXITY_IHQ': 'border-purple-300',
    'SPECIAL_IHQ': 'border-orange-300',
    'HISTOCHEMISTRY': 'border-green-300'
  }
  return classes[type] || 'border-gray-300'
}

const getTestCountBadgeClass = (type: string) => {
  const classes: Record<string, string> = {
    'LOW_COMPLEXITY_IHQ': 'bg-blue-200 text-blue-800',
    'HIGH_COMPLEXITY_IHQ': 'bg-purple-200 text-purple-800',
    'SPECIAL_IHQ': 'bg-orange-200 text-orange-800',
    'HISTOCHEMISTRY': 'bg-green-200 text-green-800'
  }
  return classes[type] || 'bg-gray-200 text-gray-800'
}

const getTotalQuantity = (tests: Array<{ quantity: number }>) => {
  return tests.reduce((sum, test) => sum + (test.quantity || 0), 0)
}

const getTestTooltip = (test: any): string => {
  const name = test.name || test.code
  const quantity = test.quantity || 1
  return `${name} • ${quantity} vez${quantity > 1 ? 'es' : ''}`
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

/* Estilos para los códigos de pruebas */
.test-code {
  font-family: 'Courier New', monospace;
  font-size: 0.75rem;
  line-height: 1;
}

.test-badge {
  transition: all 0.2s ease-in-out;
}

.test-badge:hover {
  transform: scale(1.05);
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

/* Mejoras para tooltips */
[title] {
  position: relative;
}

[title]:hover::after {
  content: attr(title);
  position: absolute;
  bottom: 100%;
  left: 50%;
  transform: translateX(-50%);
  background: rgba(0, 0, 0, 0.8);
  color: white;
  padding: 0.5rem;
  border-radius: 0.25rem;
  font-size: 0.75rem;
  white-space: nowrap;
  z-index: 1000;
  pointer-events: none;
  margin-bottom: 0.25rem;
}
</style>
