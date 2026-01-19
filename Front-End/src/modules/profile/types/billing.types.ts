// Types for the billing module

import type { EntityInfo } from "@/modules/cases/types"

// Creation form
export interface BillingFormModel {
  billingName: string
  billingCode: string
  billingEmail: string
  password: string
  observations: string
  isActive: boolean
  associatedEntities: EntityInfo[]
}

// Request to create billing
export interface BillingCreateRequest {
  billing_name: string
  billing_code: string
  billing_email: string
  password: string // Contraseña para crear el usuario asociado
  observations: string
  is_active: boolean
  associated_entities: EntityInfo[]
}

// Creation response
export interface BillingCreateResponse {
  id: string
  billing_name: string
  billing_code: string
  billing_email: string
  observations: string
  is_active: boolean
  associated_entities: EntityInfo[]
  created_at: string
  updated_at?: string
}

// Creation state
export interface BillingCreationState {
  isLoading: boolean
  isSuccess: boolean
  error: string
  successMessage: string
}

// Form validation
export interface BillingFormValidation {
  isValid: boolean
  errors: {
    billingName?: string
    billingCode?: string
    billingEmail?: string
    password?: string
    observations?: string
  }
}

// Edition
export interface BillingEditFormModel {
  id: string
  billingName: string
  billingCode: string
  billingEmail: string
  observations: string
  isActive: boolean
  associatedEntities: EntityInfo[]
  password?: string
  passwordConfirm?: string
}

export interface BillingUpdateRequest {
  billing_name: string
  billing_email: string
  observations: string
  is_active: boolean
  associated_entities: EntityInfo[]
  password?: string
}

export interface BillingUpdateResponse {
  id: string
  billing_name: string
  billing_code: string
  billing_email: string
  observations: string
  is_active: boolean
  associated_entities: EntityInfo[]
  created_at: string
  updated_at: string
}

export interface BillingEditionState {
  isLoading: boolean
  isSuccess: boolean
  error: string
  successMessage: string
}

export interface BillingEditFormValidation {
  isValid: boolean
  errors: {
    billingName?: string
    billingCode?: string
    billingEmail?: string
    observations?: string
    password?: string
    passwordConfirm?: string
  }
}
