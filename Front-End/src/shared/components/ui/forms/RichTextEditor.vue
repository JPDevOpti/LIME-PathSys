<template>
  <div class="rich-text-editor border border-gray-300 rounded-lg overflow-hidden">
    <!-- Barra de herramientas minimalista -->
    <div v-if="editor" class="toolbar bg-gray-50 border-b border-gray-300 px-2 py-1.5 flex flex-wrap gap-1 items-center">
      <!-- Deshacer/Rehacer -->
      <div class="toolbar-group">
        <button
          @click="editor.chain().focus().undo().run()"
          :disabled="!editor.can().undo()"
          type="button"
          class="toolbar-btn"
          title="Deshacer"
        >
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 10h10a8 8 0 018 8v2M3 10l6 6m-6-6l6-6"/>
          </svg>
        </button>
        <button
          @click="editor.chain().focus().redo().run()"
          :disabled="!editor.can().redo()"
          type="button"
          class="toolbar-btn"
          title="Rehacer"
        >
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 10H11a8 8 0 00-8 8v2m18-10l-6 6m6-6l-6-6"/>
          </svg>
        </button>
      </div>

      <div class="toolbar-separator"></div>

      <!-- Formato de texto -->
      <div class="toolbar-group">
        <button
          @click="editor.chain().focus().toggleBold().run()"
          :class="{ 'bg-blue-100': editor.isActive('bold') }"
          type="button"
          class="toolbar-btn font-bold"
          title="Negrita"
        >
          B
        </button>
        <button
          @click="editor.chain().focus().toggleItalic().run()"
          :class="{ 'bg-blue-100': editor.isActive('italic') }"
          type="button"
          class="toolbar-btn italic"
          title="Cursiva"
        >
          I
        </button>
        <button
          @click="editor.chain().focus().toggleUnderline().run()"
          :class="{ 'bg-blue-100': editor.isActive('underline') }"
          type="button"
          class="toolbar-btn underline"
          title="Subrayado"
        >
          U
        </button>
      </div>

      <div class="toolbar-separator"></div>

      <!-- Alineación -->
      <div class="toolbar-group">
        <button
          @click="editor.chain().focus().setTextAlign('left').run()"
          :class="{ 'bg-blue-100': editor.isActive({ textAlign: 'left' }) }"
          type="button"
          class="toolbar-btn"
          title="Alinear izquierda"
        >
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h10M4 18h16"/>
          </svg>
        </button>
        <button
          @click="editor.chain().focus().setTextAlign('center').run()"
          :class="{ 'bg-blue-100': editor.isActive({ textAlign: 'center' }) }"
          type="button"
          class="toolbar-btn"
          title="Centrar"
        >
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M7 12h10M4 18h16"/>
          </svg>
        </button>
        <button
          @click="editor.chain().focus().setTextAlign('right').run()"
          :class="{ 'bg-blue-100': editor.isActive({ textAlign: 'right' }) }"
          type="button"
          class="toolbar-btn"
          title="Alinear derecha"
        >
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M10 12h10M4 18h16"/>
          </svg>
        </button>
        <button
          @click="editor.chain().focus().setTextAlign('justify').run()"
          :class="{ 'bg-blue-100': editor.isActive({ textAlign: 'justify' }) }"
          type="button"
          class="toolbar-btn"
          title="Justificar"
        >
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16"/>
          </svg>
        </button>
      </div>

      <div class="toolbar-separator"></div>

      <!-- Listas -->
      <div class="toolbar-group">
        <button
          @click="editor.chain().focus().toggleBulletList().run()"
          :class="{ 'bg-blue-100': editor.isActive('bulletList') }"
          type="button"
          class="toolbar-btn"
          title="Lista con viñetas"
        >
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 6h13M8 12h13M8 18h13M3 6h.01M3 12h.01M3 18h.01"/>
          </svg>
        </button>
        <button
          @click="editor.chain().focus().toggleOrderedList().run()"
          :class="{ 'bg-blue-100': editor.isActive('orderedList') }"
          type="button"
          class="toolbar-btn"
          title="Lista numerada"
        >
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 4h.01M3 8h.01M3 12h.01M8 4h13M8 8h13M8 12h13"/>
          </svg>
        </button>
      </div>

      <div class="toolbar-separator"></div>

      <!-- Limpiar formato -->
      <button
        @click="editor.chain().focus().clearNodes().unsetAllMarks().run()"
        type="button"
        class="toolbar-btn"
        title="Limpiar formato"
      >
        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/>
        </svg>
      </button>
    </div>

    <!-- Editor content -->
    <EditorContent
      :editor="editor"
      class="editor-wrapper"
      :style="{ minHeight: computedMinHeight, maxHeight: computedMaxHeight }"
    />
  </div>
</template>

<script setup lang="ts">
import { watch, onBeforeUnmount, computed, onMounted } from 'vue'
import { useEditor, EditorContent } from '@tiptap/vue-3'
import StarterKit from '@tiptap/starter-kit'
import Underline from '@tiptap/extension-underline'
import TextAlign from '@tiptap/extension-text-align'

interface Props {
  modelValue: string
  placeholder?: string
  minHeight?: number
  maxHeight?: number
  language?: string
  spellcheck?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  language: 'es',
  spellcheck: true,
  minHeight: 360,
  maxHeight: 560
})

const emit = defineEmits<{
  (e: 'update:modelValue', value: string): void
}>()

const computedMinHeight = computed(() => `${props.minHeight}px`)
const computedMaxHeight = computed(() => `${props.maxHeight}px`)

// Función para limpiar HTML de Word
const cleanWordHTML = (html: string): string => {
  let cleaned = html

  // Remover comentarios condicionales de Word
  cleaned = cleaned.replace(/<!--\[if[\s\S]*?<!\[endif\]-->/gi, '')
  
  // Remover comentarios HTML
  cleaned = cleaned.replace(/<!--[\s\S]*?-->/g, '')
  
  // Remover tags XML de Office
  cleaned = cleaned.replace(/<(\/)?(xml|o:|w:|m:|v:)[^>]*>/gi, '')
  
  // Remover clases de Word/Office
  cleaned = cleaned.replace(/class="?Mso[^"]*"?/gi, '')
  
  // Remover todos los atributos style
  cleaned = cleaned.replace(/style="[^"]*"/gi, '')
  
  // Remover atributos lang
  cleaned = cleaned.replace(/lang="[^"]*"/gi, '')
  
  // Remover spans vacíos o innecesarios
  cleaned = cleaned.replace(/<span[^>]*>(.*?)<\/span>/gi, '$1')
  
  // Normalizar espacios múltiples
  cleaned = cleaned.replace(/\s+/g, ' ')
  
  // Remover &nbsp; excesivos
  cleaned = cleaned.replace(/(&nbsp;|\u00A0)+/g, ' ')
  
  // Limpiar tags vacíos
  cleaned = cleaned.replace(/<(\w+)[^>]*>\s*<\/\1>/gi, '')
  
  return cleaned.trim()
}

// Configurar editor con TipTap
const editor = useEditor({
  content: props.modelValue,
  editorProps: {
    attributes: {
      class: 'prose prose-sm max-w-none focus:outline-none p-4',
      spellcheck: props.spellcheck ? 'true' : 'false',
      lang: props.language,
      'data-placeholder': props.placeholder || ''
    },
    handlePaste: (view, event) => {
      const html = event.clipboardData?.getData('text/html')
      
      if (html) {
        // Limpiar HTML de Word
        const cleanedHTML = cleanWordHTML(html)
        
        // Si el HTML limpio es muy corto comparado con el original,
        // probablemente era basura de Word, insertar como texto plano
        if (cleanedHTML.length < html.length * 0.3) {
          const text = event.clipboardData?.getData('text/plain') || ''
          if (text) {
            view.dispatch(view.state.tr.insertText(text))
            return true
          }
        }
        
        // Dejar que TipTap maneje el HTML limpio
        // preservando solo los formatos permitidos
      }
      
      return false
    }
  },
  extensions: [
    StarterKit.configure({
      heading: false,        // Sin encabezados
      code: false,           // Sin código inline
      codeBlock: false,      // Sin bloques de código
      strike: false,         // Sin tachado
      blockquote: false,     // Sin citas
      horizontalRule: false, // Sin líneas horizontales
      // Habilitar solo extensiones necesarias
      // history se habilita por defecto, no necesita ser true
    }),
    Underline,               // Extensión de subrayado
    TextAlign.configure({    // Alineación de texto
      types: ['paragraph'],
      alignments: ['left', 'center', 'right', 'justify']
    })
  ],
  onUpdate: ({ editor }) => {
    emit('update:modelValue', editor.getHTML())
  }
})

// Sincronizar contenido cuando cambia desde fuera
watch(() => props.modelValue, (newValue) => {
  if (editor.value && editor.value.getHTML() !== newValue) {
    editor.value.commands.setContent(newValue || '')
  }
})

// Aplicar idioma al montar
onMounted(() => {
  if (editor.value) {
    const editorElement = document.querySelector('.ProseMirror') as HTMLElement
    if (editorElement) {
      editorElement.setAttribute('lang', props.language)
      editorElement.setAttribute('spellcheck', props.spellcheck ? 'true' : 'false')
    }
  }
})

// Limpiar al desmontar
onBeforeUnmount(() => {
  editor.value?.destroy()
})
</script>

<style scoped>
.toolbar-btn {
  @apply px-2 py-1 rounded hover:bg-gray-200 transition-colors flex items-center justify-center min-w-[28px] h-7 text-sm disabled:opacity-50 disabled:cursor-not-allowed;
}

.toolbar-btn:active:not(:disabled) {
  @apply bg-gray-300;
}

.toolbar-separator {
  @apply w-px h-5 bg-gray-300 mx-1;
}

.toolbar-group {
  @apply flex gap-1 items-center;
}

.editor-wrapper {
  @apply overflow-y-auto bg-white;
}

/* Estilos globales para el contenido del editor TipTap */
:deep(.ProseMirror) {
  /* Tipografía estándar fija */
  font-family: Arial, sans-serif;
  font-size: 14px;
  color: #000000;
  line-height: 1.6;
  outline: none;
}

:deep(.ProseMirror:focus) {
  @apply ring-2 ring-blue-500 ring-inset;
}

/* Placeholder */
:deep(.ProseMirror p.is-editor-empty:first-child::before) {
  content: attr(data-placeholder);
  @apply text-gray-400 pointer-events-none float-left h-0;
}

/* Párrafos */
:deep(.ProseMirror p) {
  @apply mb-2;
}

/* Listas */
:deep(.ProseMirror ul),
:deep(.ProseMirror ol) {
  @apply ml-6 mb-2;
}

:deep(.ProseMirror ul) {
  @apply list-disc;
}

:deep(.ProseMirror ol) {
  @apply list-decimal;
}

:deep(.ProseMirror li) {
  @apply mb-1;
}

/* Formatos de texto */
:deep(.ProseMirror strong) {
  @apply font-bold;
}

:deep(.ProseMirror em) {
  @apply italic;
}

:deep(.ProseMirror u) {
  @apply underline;
}

/* Alineación */
:deep(.ProseMirror [style*="text-align: left"]) {
  text-align: left !important;
}

:deep(.ProseMirror [style*="text-align: center"]) {
  text-align: center !important;
}

:deep(.ProseMirror [style*="text-align: right"]) {
  text-align: right !important;
}

:deep(.ProseMirror [style*="text-align: justify"]) {
  text-align: justify !important;
}
</style>
