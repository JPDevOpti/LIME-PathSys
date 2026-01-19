<template>
  <ComponentCard title="Información Personal">
    <!-- Personal Information Grid -->
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 mb-8">
      <!-- Nombre completo -->
      <InfoCard
        icon="user"
        label="Nombre Completo"
        :value="`${user.firstName} ${user.lastName}`"
      />

      <!-- Correo electrónico -->
      <InfoCard
        icon="email"
        label="Correo Electrónico"
        :value="user.email"
      />

      <!-- Rol -->
      <InfoCard
        icon="role"
        label="Rol"
        :value="getRoleLabel(user.role)"
      />

      <!-- Estado -->
      <InfoCard
        icon="status"
        label="Estado"
        :value="user.isActive ? 'Activo' : 'Inactivo'"
        :statusColor="user.isActive ? 'green' : 'red'"
      />
    </div>

    <!-- Role Specific Information -->
    <div v-if="user.roleSpecificData && hasRoleSpecificData" class="border-t border-gray-200 pt-6">
      <h4 class="text-md font-semibold text-gray-900 mb-4">
        Información Específica - {{ getRoleLabel(user.role) }}
      </h4>
      
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        <!-- Patólogo -->
        <template v-if="user.role === 'patologo'">
          <InfoCard
            v-if="user.roleSpecificData.iniciales"
            icon="initials"
            label="Iniciales"
            :value="user.roleSpecificData.iniciales"
          />
          <InfoCard
            v-if="user.roleSpecificData.registroMedico"
            icon="registro"
            label="Registro Médico"
            :value="user.roleSpecificData.registroMedico"
          />
          <InfoCard
            v-if="user.roleSpecificData.observaciones"
            icon="document"
            label="Observaciones"
            :value="user.roleSpecificData.observaciones"
          />
        </template>

        <!-- Residente -->
        <template v-if="user.role === 'residente'">
          <InfoCard
            v-if="user.roleSpecificData.iniciales"
            icon="initials"
            label="Iniciales"
            :value="user.roleSpecificData.iniciales"
          />
          <InfoCard
            v-if="user.roleSpecificData.registroMedico"
            icon="registro"
            label="Registro Médico"
            :value="user.roleSpecificData.registroMedico"
          />
          <InfoCard
            v-if="user.roleSpecificData.observaciones"
            icon="document"
            label="Observaciones"
            :value="user.roleSpecificData.observaciones"
          />
        </template>

        <!-- Auxiliar / Admin -->
        <template v-if="user.role === 'auxiliar' || user.role === 'admin'">
          <InfoCard
            v-if="user.roleSpecificData && user.roleSpecificData.observaciones"
            icon="document"
            label="Observaciones"
            :value="user.roleSpecificData.observaciones!"
          />
        </template>

        <!-- Facturación -->
        <template v-if="user.role === 'facturacion'">
          <InfoCard
            v-if="user.roleSpecificData && user.roleSpecificData.observaciones"
            icon="document"
            label="Observaciones"
            :value="user.roleSpecificData.observaciones!"
          />
          <div 
            v-if="user.roleSpecificData?.associatedEntities && user.roleSpecificData.associatedEntities.length > 0"
            class="col-span-full"
          >
            <label class="block text-sm font-medium text-gray-700 mb-2">Entidades Asociadas</label>
            <div class="flex flex-wrap gap-2">
              <span 
                v-for="entity in user.roleSpecificData.associatedEntities" 
                :key="entity.id || entity.codigo"
                class="inline-flex items-center px-3 py-1.5 rounded-full text-sm font-medium bg-blue-100 text-blue-800 border border-blue-200"
              >
                {{ entity.name || entity.nombre }} ({{ entity.id || entity.codigo }})
              </span>
            </div>
          </div>
        </template>
      </div>
    </div>
  </ComponentCard>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import type { UserProfile, UserRole } from '../../types/userProfile.types'
import ComponentCard from '@/shared/components/layout/ComponentCard.vue'
import InfoCard from './InfoCard.vue'

interface Props {
  user: UserProfile
}

const props = defineProps<Props>()


const getRoleLabel = (role: UserRole): string => {
  const roleLabels: Record<UserRole, string> = {
    admin: 'Administrador',
    patologo: 'Patólogo',
    residente: 'Residente',
    auxiliar: 'Auxiliar',
    facturacion: 'Usuario de Facturación'
  }
  return roleLabels[role]
}

const hasRoleSpecificData = computed(() => {
  if (!props.user.roleSpecificData) return false
  
  const data = props.user.roleSpecificData
  return !!(
    data.iniciales ||
    data.registroMedico ||
    data.observaciones ||
    (data.associatedEntities && data.associatedEntities.length > 0)
  )
})
</script>
