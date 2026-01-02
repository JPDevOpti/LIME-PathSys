// Entities API: small fetch wrapper + mappers to normalized EntityInfo
// Refactored to use apiClient (Axios) to ensure HTTPS and correct base URL
import type { EntityInfo } from '../types'
import { API_CONFIG } from '@/core/config/api.config'
import apiClient from '@/core/config/axios.config'

export class EntitiesApiService {
  // Map backend item to normalized EntityInfo
  private mapEntity = (e: any): any => ({
    id: e?.entity_code || e?.code || e?.id || '',
    name: e?.name || e?.nombre || '',
    codigo: e?.entity_code || e?.code || e?.id || '',
    nombre: e?.name || e?.nombre || ''
  })

  // Active entities only
  async getEntities(): Promise<EntityInfo[]> {
    // Add trailing slash to avoid 307 redirect which might cause Mixed Content issues on Render
    const response = await apiClient.get<any>(`${API_CONFIG.ENDPOINTS.ENTITIES}/?limit=100`)
    return Array.isArray(response) ? response.map(this.mapEntity) : []
  }

  // Active + inactive entities (includes activo flag)
  async getAllEntitiesIncludingInactive(): Promise<EntityInfo[]> {
    const response = await apiClient.get<any>(`${API_CONFIG.ENDPOINTS.ENTITIES}/inactive?limit=100`)
    return Array.isArray(response) ? response.map(this.mapEntity) : []
  }

  async getEntityByCode(code: string): Promise<EntityInfo | null> {
    if (!code || code.trim() === '') return null
    try {
      const response = await apiClient.get<any>(`${API_CONFIG.ENDPOINTS.ENTITIES}/${encodeURIComponent(code)}`)
      return response ? this.mapEntity(response) : null
    } catch {
      return null
    }
  }

  async searchEntities(query: string, includeInactive: boolean = false): Promise<EntityInfo[]> {
    const endpoint = includeInactive
      ? `${API_CONFIG.ENDPOINTS.ENTITIES}/inactive?query=${encodeURIComponent(query)}&limit=100`
      : `${API_CONFIG.ENDPOINTS.ENTITIES}?query=${encodeURIComponent(query)}&limit=100`
    const response = await apiClient.get<any>(endpoint)
    return Array.isArray(response) ? response.map(this.mapEntity) : []
  }
}

export const entitiesApiService = new EntitiesApiService()
