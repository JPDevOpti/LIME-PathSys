<template>
  <!-- Dashboard layout: KPIs + charts + urgent list -->
  <AdminLayout>
    <div class="grid grid-cols-12 gap-4 md:gap-6">
      <!-- Left column: KPIs and monthly cases -->
      <div class="col-span-12 space-y-4 xl:col-span-7">
        <MetricsBlocks />
        <CasesByMonth />
      </div>

      <!-- Right column: opportunity percentage -->
      <div class="col-span-12 xl:col-span-5">
        <OportunityPercentage />
      </div>

      <!-- Full width: urgent cases list -->
      <div class="col-span-12">
        <UrgentCases @show-details="handleShowDetails" />
      </div>
    </div>

    <!-- Details modal controlled by selectedUrgentCase -->
    <UrgentCaseDetailsModal :case-item="selectedUrgentCase" @close="closeUrgentCaseDetails" />
  </AdminLayout>
</template>

<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'
import AdminLayout from '@/shared/layouts/AdminLayout.vue'
import MetricsBlocks from '../components/MetricsBlocks.vue'
import CasesByMonth from '../components/CasesByMonth.vue'
import UrgentCases from '../components/UrgentCases.vue'
import OportunityPercentage from '../components/OportunityPercentage.vue'
import UrgentCaseDetailsModal from '../components/UrgentCaseDetailsModal.vue'
import type { CasoUrgente } from '../types/dashboard.types'
import { useAuthStore } from '@/stores/auth.store'
import { profileApiService } from '@/modules/profile/services/profileApiService'
import { API_CONFIG } from '@/core/config/api.config'
import { useSignatureNotifier } from '@/shared/composables/useSignatureNotifier'

// Currently selected urgent case for the details modal
const selectedUrgentCase = ref<CasoUrgente | null>(null)

const authStore = useAuthStore()
// const { warning } = useToasts()
const { checkAndShowOncePerSession, close: closeSignatureNotice } = useSignatureNotifier()

// Open modal with selected urgent case
function handleShowDetails(caso: CasoUrgente) {
  selectedUrgentCase.value = caso
}

// Close modal and clear selection
function closeUrgentCaseDetails() {
  selectedUrgentCase.value = null
}

let isCheckingSignature = false

async function ensureSignatureStatus() {
  if (isCheckingSignature) return
  const user = authStore.user as any
  const isPathologistRef = authStore.isPathologist as any
  const isPathologist = typeof isPathologistRef === 'object' && isPathologistRef !== null && 'value' in isPathologistRef
    ? Boolean(isPathologistRef.value)
    : Boolean(isPathologistRef)
  if (!isPathologist || !user?.pathologist_code) return

  isCheckingSignature = true
  try {
    console.log('[Dashboard] Verificando firma digital', {
      pathologistCode: user.pathologist_code,
      hasSignatureLocal: !!(user?.firma || user?.firma_url || user?.signatureUrl || user?.firmaDigital)
    })
    const profile = await profileApiService.getPathologistByCode(user.pathologist_code)
    console.log('[Dashboard] Respuesta profileApiService.getPathologistByCode', profile)
    const rawSignature = (profile?.firma || (profile as any)?.signature || '').toString().trim()

    if (rawSignature) {
      const baseUrl = API_CONFIG.BASE_URL
      const absoluteUrl = rawSignature.startsWith('http') ? rawSignature : `${baseUrl}${rawSignature}`
      user.firma = absoluteUrl
      user.firma_url = absoluteUrl
      user.signatureUrl = absoluteUrl
      user.firmaDigital = absoluteUrl
      try {
        sessionStorage.setItem('signature_url', absoluteUrl)
        localStorage.setItem('signature_url', absoluteUrl)
        sessionStorage.setItem('signature_missing_notified', '1')
      } catch {}
      console.log('[Dashboard] Firma encontrada y sincronizada', absoluteUrl)
      // Cerrar el modal si estaba abierto (por si acaso)
      closeSignatureNotice()
    } else {
      console.warn('[Dashboard] Firma no encontrada para el patólogo', user.pathologist_code)
      // Limpiar referencias a firma del usuario
      delete user.firma
      delete user.firma_url
      delete user.signatureUrl
      delete user.firmaDigital
      try {
        sessionStorage.removeItem('signature_url')
        localStorage.removeItem('signature_url')
      } catch {}
      // Solo mostrar el modal si realmente no tiene firma (después de verificar con el backend)
      // La función checkAndShowOncePerSession manejará si ya se mostró en esta sesión
      checkAndShowOncePerSession()
    }
  } catch (error) {
    console.error('Error verificando firma del patólogo:', error)
  } finally {
    isCheckingSignature = false
  }
}

onMounted(() => {
  ensureSignatureStatus()
})

watch(
  () => [
    (authStore.isAuthenticated as any)?.value ?? authStore.isAuthenticated,
    (authStore.user as any)?.pathologist_code,
    authStore.user?.role
  ],
  ([ready, code, role]) => {
    if (ready && code && role) ensureSignatureStatus()
  },
  { immediate: true }
)
</script>

<style scoped>
@media (max-width: 768px) {
  .grid {
    gap: 1rem;
  }
}

@media (max-width: 480px) {
  .grid {
    gap: 0.75rem;
  }
}
</style>