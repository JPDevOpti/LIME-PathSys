/**
 * Utilidades de formateo para el proyecto
 */

export const formatearNumero = (num: number): string => {
  return new Intl.NumberFormat('es-CO').format(num)
}

export const obtenerClasePorcentaje = (porcentaje: number): string => {
  return porcentaje >= 0
    ? 'bg-green-50 text-green-600 hover:bg-green-100'
    : 'bg-red-50 text-red-600 hover:bg-red-100'
}

export const formatPatientAge = (age: number | string, birthDate?: string | Date): string => {
  if (birthDate) {
    const birth = new Date(birthDate)
    const now = new Date()

    if (!isNaN(birth.getTime())) {
      let years = now.getFullYear() - birth.getFullYear()
      let months = now.getMonth() - birth.getMonth()

      if (now.getDate() < birth.getDate()) {
        months--
      }

      if (months < 0) {
        years--
        months += 12
      }

      // Safety check for future dates
      if (years < 0) return 'Recién nacido'

      if (years < 1) {
        return `${months} meses`
      } else if (years < 2) {
        return `${years} año y ${months} meses`
      }

      // For older patients, stick to the simple age if calculated matches provided
      // or just return calculated years
      return `${years} años`
    }
  }

  // Fallback
  if (!age) return ''
  return `${age} años`
}
