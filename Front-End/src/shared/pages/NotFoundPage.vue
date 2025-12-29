<template>
  <AdminLayout>
    <div class="min-h-[80vh] flex flex-col items-center justify-center px-4 sm:px-6 lg:px-8">
      <div class="text-center">
        <p class="text-base font-semibold text-blue-600">404</p>
        <h1 class="mt-2 text-4xl font-bold tracking-tight text-gray-900 sm:text-5xl">Página no encontrada</h1>
        <p class="mt-4 text-base text-gray-500">Lo sentimos, no pudimos encontrar la página que estás buscando.</p>
        <div class="mt-6">
          <router-link 
            to="/dashboard" 
            class="text-base font-medium text-blue-600 hover:text-blue-500 flex items-center justify-center gap-2"
          >
            <span aria-hidden="true">&larr;</span>
            Volver al inicio
          </router-link>
        </div>
      </div>
    </div>
  </AdminLayout>
</template>

<script setup lang="ts">
import AdminLayout from '@/shared/layouts/AdminLayout.vue'
</script>
