import { apiClient } from '@/core/config/axios.config'
import { API_CONFIG } from '@/core/config/api.config'
import type { OpportunityTest, PathologistPerformance } from '../types/opportunity.types'

const EXCLUDED_ENTITY_CODE = 'HAMA'

const isExcludedEntity = (item: any): boolean => {
  if (!item || typeof item !== 'object') return false
  const entity = item.entity || item.entityInfo || item.entidad || {}

  const idAsCode = String(
    entity.id ||
    entity.entity_id ||
    item.entity_id ||
    ''
  ).trim().toUpperCase()

  const code = String(
    item.entity_code ||
    item.entityCode ||
    entity.code ||
    entity.entity_code ||
    entity.codigo ||
    ''
  ).trim().toUpperCase()
  return code === EXCLUDED_ENTITY_CODE || idAsCode === EXCLUDED_ENTITY_CODE
}

export interface OpportunityReportData {
  tests: OpportunityTest[]
  pathologists: PathologistPerformance[]
  monthlyPct?: number[]
  summary?: { total: number; within: number; out: number }
}

export class OpportunityApiService {
  private readonly base = `${API_CONFIG.ENDPOINTS.CASES}/statistics/opportunity`

  async getMonthlyOpportunity(month?: number, year?: number): Promise<OpportunityReportData> {
    const params: Record<string, any> = {}
    if (typeof month === 'number') params.month = month
    if (typeof year === 'number') params.year = year
    const url = `${this.base}/monthly`
    const resp: any = await apiClient.get(url, { params })
    const data = resp?.data ?? resp
    return this.mapMonthlyV2ToFront(data)
  }

  async getYearlyOpportunity(year: number): Promise<number[]> {
    const url = `${this.base}/yearly/${year}`
    const resp: any = await apiClient.get(url)
    const data = resp?.data ?? resp
    const arr = Array.isArray(data?.percentageByMonth) ? data.percentageByMonth : []
    return arr.map((n: any) => Number(n))
  }

  private mapMonthlyV2ToFront(raw: any): OpportunityReportData {
    const tests: OpportunityTest[] = []
    const pathologists: PathologistPerformance[] = []

    const testBlocks: any[] = raw?.tests || []
    if (Array.isArray(testBlocks)) {
      for (const t of testBlocks) {
        if (isExcludedEntity(t)) continue
        tests.push({
          code: String(t.code || ''),
          name: String(t.name || ''),
          withinOpportunity: Number(t.withinOpportunity || 0),
          outOfOpportunity: Number(t.outOfOpportunity || 0),
          averageDays: Number(t.averageDays || 0)
        })
      }
    }

    const patoBlocks: any[] = raw?.pathologists || []
    if (Array.isArray(patoBlocks)) {
      for (const p of patoBlocks) {
        if (isExcludedEntity(p)) continue
        pathologists.push({
          code: String(p.code || ''),
          name: String(p.name || ''),
          withinOpportunity: Number(p.withinOpportunity || 0),
          outOfOpportunity: Number(p.outOfOpportunity || 0),
          avgTime: Number(p.averageDays || 0)
        })
      }
    }

    const res = raw?.summary || null
    const summary = res ? { total: Number(res.total || 0), within: Number(res.within || 0), out: Number(res.out || 0) } : undefined
    return { tests, pathologists, summary }
  }

  // Old fallbacks removed in v2
}

export const opportunityApiService = new OpportunityApiService()


