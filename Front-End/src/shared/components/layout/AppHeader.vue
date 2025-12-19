<!--
  Componente AppHeader (PanelSuperior)
  Encabezado principal de la aplicación.
  Incluye toggle del sidebar, logo, barra de búsqueda y menú de usuario.
  Incluye soporte para tema oscuro y responsive.
-->
<template>
  <header
    class="sticky top-0 flex w-full bg-white border-gray-200 z-99999 lg:border-b transition-colors duration-200"
  >
    <div class="flex items-center justify-between w-full px-4 py-3 lg:px-6 lg:py-4">
      <!-- Left side - Toggle button and logo -->
      <div class="flex items-center gap-4">
        <button
          @click="toggleSidebar"
          class="flex items-center justify-center w-10 h-10 text-gray-500 rounded-lg hover:bg-gray-100 transition-colors duration-200"
          :aria-label="sidebarOpen ? 'Colapsar menú lateral' : 'Expandir menú lateral'"
          :aria-expanded="sidebarOpen"
          :title="sidebarOpen ? 'Colapsar menú lateral' : 'Expandir menú lateral'"
        >
          <ChevronRightIcon :class="['w-5 h-5 transition-transform duration-300', sidebarOpen ? 'rotate-180' : '']" />
        </button>
        <HeaderLogo />
      </div>

      <!-- Center - Search bar -->
      <div class="flex-1 max-w-md mx-4 hidden sm:block">
        <SearchBar />
      </div>

      <!-- Right side - User menu -->
      <div class="flex items-center gap-4">
        <!-- Mobile menu toggle -->
        <button
          @click="toggleApplicationMenu"
          class="flex items-center justify-center w-10 h-10 text-gray-700 rounded-lg hover:bg-gray-100 sm:hidden transition-colors duration-200"
          aria-label="Toggle application menu"
          :aria-expanded="isApplicationMenuOpen"
        >
          <svg
            class="transform transition-transform duration-200"
            width="24"
            height="24"
            viewBox="0 0 24 24"
            fill="none"
            xmlns="http://www.w3.org/2000/svg"
          >
            <path
              fillRule="evenodd"
              clipRule="evenodd"
              d="M5.99902 10.4951C6.82745 10.4951 7.49902 11.1667 7.49902 11.9951V12.0051C7.49902 12.8335 6.82745 13.5051 5.99902 13.5051C5.1706 13.5051 4.49902 12.8335 4.49902 12.0051V11.9951C4.49902 11.1667 5.1706 10.4951 5.99902 10.4951ZM17.999 10.4951C18.8275 10.4951 19.499 11.1667 19.499 11.9951V12.0051C19.499 12.8335 18.8275 13.5051 17.999 13.5051C17.1706 13.5051 16.499 12.8335 16.499 12.0051V11.9951C16.499 11.1667 17.1706 10.4951 17.999 10.4951ZM13.499 11.9951C13.499 11.1667 12.8275 10.4951 11.999 10.4951C11.1706 10.4951 10.499 11.1667 10.499 11.9951V12.0051C10.499 12.8335 11.1706 13.5051 11.999 13.5051C12.8275 13.5051 13.499 12.8335 13.499 12.0051V11.9951Z"
              fill="currentColor"
            />
          </svg>
        </button>
        
        <!-- Desktop user menu -->
        <div class="hidden sm:flex items-center gap-4">
          <UserMenu />
        </div>
      </div>
    </div>

    <!-- Mobile dropdown menu -->
    <div
      v-if="isApplicationMenuOpen"
      class="sm:hidden border-t border-gray-200 bg-white animate-slideDown"
    >
      <div class="px-4 py-3">
        <SearchBar />
      </div>
      <div class="flex items-center justify-between px-4 py-3 border-t border-gray-200">
        <UserMenu />
      </div>
    </div>
  </header>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import { useSidebar } from '@/shared/composables/SidebarControl'
import SearchBar from './SearchBar.vue'
import HeaderLogo from './HeaderLogo.vue'
import UserMenu from './UserMenu.vue'
import { ChevronRightIcon } from '@/assets/icons'

const { toggleSidebar, sidebarOpen } = useSidebar()
const isApplicationMenuOpen = ref(false)

const toggleApplicationMenu = () => {
  isApplicationMenuOpen.value = !isApplicationMenuOpen.value
}

// Handle window resize to close mobile menu
const handleResize = () => {
  if (window.innerWidth >= 1024) {
    isApplicationMenuOpen.value = false
  }
}

onMounted(() => {
  window.addEventListener('resize', handleResize)
})

onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
})
</script>

<style scoped>
.animate-slideDown {
  animation: slideDown 0.3s ease-out;
}

@keyframes slideDown {
  from {
    opacity: 0;
    transform: translateY(-10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.shadow-theme-md {
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
}
</style>