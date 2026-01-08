# Configurar Corrector Ortográfico en Español para Firefox

## Problema
El corrector ortográfico de Firefox está mostrando sugerencias en inglés en lugar de español.

## Solución

### Opción 1: Instalar Diccionario Español en Firefox (Recomendado)

1. Abre Firefox y ve a: `about:addons`
2. En el menú lateral, selecciona **"Diccionarios"**
3. Busca **"Spanish"** o **"Español"**
4. Instala el diccionario **"Español (España)"** o **"Español (México)"** según tu preferencia
5. **Reinicia Firefox**

### Opción 2: Desde la Configuración de Firefox

1. Abre Firefox y escribe en la barra de direcciones: `about:preferences#general`
2. Desplázate hasta la sección **"Idioma"**
3. Haz clic en **"Configurar alternativas..."**
4. Agrega **"Español"** como idioma preferido (debe estar primero en la lista)
5. Haz clic en **"Aceptar"** y **reinicia Firefox**

### Opción 3: Instalación Manual del Diccionario

1. Ve a: https://addons.mozilla.org/es/firefox/language-tools/
2. Busca el diccionario **"Spanish (Spain) Dictionary"** o **"Spanish (Mexico) Dictionary"**
3. Haz clic en **"Añadir a Firefox"**
4. **Reinicia Firefox**

### Verificar que Funciona

1. Abre la aplicación PathSys
2. Ve a la sección de resultados (Corte Macro, Micro o Diagnóstico)
3. Escribe una palabra mal escrita en español (ejemplo: "probando")
4. Deberías ver el subrayado rojo y sugerencias en español al hacer clic derecho

## Notas Técnicas

- Firefox **NO** usa el atributo `lang="es"` del HTML para decidir el idioma del corrector
- Firefox usa su **propio sistema de diccionarios** instalado en el navegador
- Los atributos `autocorrect`, `autocapitalize` e `inputmode` solo funcionan en Safari/iOS
- Para Firefox, es **obligatorio** tener instalado el diccionario del idioma deseado

## Alternativa: Usar Chrome/Chromium

Si prefieres no instalar el diccionario en Firefox, puedes usar Chrome o Chromium que detectan mejor el idioma del sistema:

```bash
# Instalar Chromium en Fedora
sudo dnf install chromium

# Verificar instalación
chromium --version
```

Chrome/Chromium detectan automáticamente el idioma del sistema (`es_ES.UTF-8`) y usan el diccionario correspondiente.
