import { ref } from 'vue'
import { useAuthStore } from '@/stores/auth.store'

// Manejador simple para notificación centrada de firma faltante
// Comentario: Verifica sesión y rol, muestra alerta una vez por sesión.
const visible = ref(false)

function hasSignature(u: any): boolean {
  try {
    // Comentario: Detectar firma solo con datos actuales del usuario y sesión;
    // evitar usar localStorage para no arrastrar valores de sesiones previas.
    let sig: string | null = u?.firma || u?.firma_url || u?.signatureUrl || u?.firmaDigital || null
    // Conservar compatibilidad: revisar sessionStorage y localStorage por si la firma se cargó desde otros flujos.
    if (!sig) {
      sig = sessionStorage.getItem('signature_url') || localStorage.getItem('signature_url')
    }
    return !!(sig && sig.toString().trim())
  } catch {
    return false
  }
}

function checkAndShowOncePerSession(): void {
  const authStore = useAuthStore()
  try {
    const shownKey = 'signature_missing_notified'
    const alreadyShown = sessionStorage.getItem(shownKey)
    const rawIsPathologist = authStore.isPathologist as any
    const rawIsAuth = authStore.isAuthenticated as any
    const isPatologist = typeof rawIsPathologist === 'object' && rawIsPathologist !== null && 'value' in rawIsPathologist
      ? Boolean(rawIsPathologist.value)
      : Boolean(rawIsPathologist)
    const isAuth = typeof rawIsAuth === 'object' && rawIsAuth !== null && 'value' in rawIsAuth
      ? Boolean(rawIsAuth.value)
      : Boolean(rawIsAuth)
    const user = authStore.user as any
    if (!alreadyShown && isAuth && isPatologist && !hasSignature(user)) {
      visible.value = true
      sessionStorage.setItem(shownKey, '1')
    } else {
      visible.value = false
    }
  } catch {}
}

function close(): void {
  visible.value = false
}

export function useSignatureNotifier() {
  return { visible, checkAndShowOncePerSession, close }
}