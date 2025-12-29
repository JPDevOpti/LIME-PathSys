<template>
  <AdminLayout>
    <div class="min-h-[80vh] flex flex-col items-center justify-center px-4 sm:px-6 lg:px-8">
      <div class="text-center">
        <p class="text-base font-semibold text-red-600">500</p>
        <h1 class="mt-2 text-4xl font-bold tracking-tight text-gray-900 sm:text-5xl">Error del Servidor</h1>
        <p class="mt-4 text-base text-gray-500">Algo salió mal en nuestros servidores. Por favor, inténtalo de nuevo más tarde.</p>
        <div class="mt-6 flex items-center justify-center gap-4">
          <button 
            @click="reloadPage"
            class="rounded-md bg-blue-600 px-3.5 py-2.5 text-sm font-semibold text-white shadow-sm hover:bg-blue-500 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-blue-600"
          >
            Recargar página
          </button>
          <router-link 
            to="/dashboard" 
            class="text-base font-medium text-blue-600 hover:text-blue-500"
          >
            Volver al inicio <span aria-hidden="true">&rarr;</span>
          </router-link>
        </div>
      </div>
    </div>
  </AdminLayout>
</template>

<script setup lang="ts">
import AdminLayout from '@/shared/layouts/AdminLayout.vue'

const reloadPage = () => {
  window.location.reload()
}
</script>
