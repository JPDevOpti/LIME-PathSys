"""
Pool de navegadores persistentes para generación de PDFs
Optimiza el rendimiento reutilizando instancias de Playwright en lugar de crear/cerrar en cada request
"""
from __future__ import annotations
from typing import Optional
import asyncio
import logging
from playwright.async_api import async_playwright, Playwright, Browser, BrowserContext, Page  # type: ignore

logger = logging.getLogger(__name__)


class BrowserPool:
    """
    Pool singleton para reutilizar navegadores de Playwright.
    Mantiene una instancia persistente del navegador para reducir el overhead
    de crear/cerrar navegadores en cada generación de PDF.
    """
    _instance: Optional[BrowserPool] = None
    _lock = asyncio.Lock()
    
    def __init__(self):
        self.playwright: Optional[Playwright] = None
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self._initialized = False
        self._shutting_down = False
        # Pool de páginas reutilizables para reducir overhead
        self._page_pool: Optional[asyncio.Queue[Page]] = None
        self._max_pool_size = 5  # Máximo 5 páginas en el pool
        
    @classmethod
    async def get_instance(cls) -> BrowserPool:
        """Obtener la instancia singleton del pool"""
        if cls._instance is None:
            async with cls._lock:
                if cls._instance is None:
                    cls._instance = cls()
        return cls._instance
    
    async def initialize(self) -> None:
        """Inicializar el pool (crear navegador y contexto)"""
        if self._initialized or self._shutting_down:
            return
            
        try:
            # Verificar que playwright está disponible
            from playwright.async_api import async_playwright  # type: ignore
        except ImportError:
            raise RuntimeError(
                "Playwright no está instalado o no se han instalado los navegadores. "
                "Ejecuta: pip install playwright && playwright install chromium"
            )
        
        async with self._lock:
            if self._initialized or self._shutting_down:
                return
                
            try:
                logger.info("Inicializando pool de navegadores para PDFs...")
                # async_playwright() retorna un objeto que necesita ser iniciado con .start()
                p = async_playwright()
                self.playwright = await p.start()
                
                # Configuración optimizada del navegador
                self.browser = await self.playwright.chromium.launch(
                    headless=True,
                    args=[
                        '--no-sandbox',
                        '--disable-setuid-sandbox',
                        '--disable-dev-shm-usage',
                        '--disable-gpu',
                        '--disable-software-rasterizer',
                        '--disable-extensions',
                        '--disable-background-timer-throttling',
                        '--disable-backgrounding-occluded-windows',
                        '--disable-renderer-backgrounding',
                        '--disable-features=TranslateUI',
                        '--disable-ipc-flooding-protection',
                        '--disable-background-networking',
                        '--disable-default-apps',
                        '--disable-sync',
                        '--metrics-recording-only',
                        '--no-first-run',
                        '--mute-audio',
                        '--no-default-browser-check',
                        '--no-pings',
                        '--password-store=basic',
                        '--use-mock-keychain',
                        '--disable-blink-features=AutomationControlled',
                    ]
                )
                
                # Crear contexto optimizado para PDFs
                self.context = await self.browser.new_context(
                    viewport={'width': 1240, 'height': 1754},  # Letter size en puntos
                    java_script_enabled=True,
                    accept_downloads=False,
                    has_touch=False,
                    is_mobile=False,
                    locale='es-CO',
                    timezone_id='America/Bogota',
                    # Deshabilitar recursos innecesarios para mejor rendimiento
                    ignore_https_errors=True,
                    # Deshabilitar imágenes y otros recursos para acelerar renderizado
                    bypass_csp=True,
                )
                
                # Interceptar requests para bloquear recursos innecesarios (opcional, más agresivo)
                # Esto puede acelerar mucho pero comentado por si afecta el renderizado
                # await self.context.route("**/*.{png,jpg,jpeg,gif,svg,woff,woff2,ttf}", lambda route: route.abort())
                
                # Inicializar pool de páginas
                self._page_pool = asyncio.Queue(maxsize=self._max_pool_size)
                
                self._initialized = True
                logger.info("Pool de navegadores inicializado correctamente")
                
            except Exception as e:
                logger.error(f"Error inicializando pool de navegadores: {e}")
                await self._cleanup()
                raise
    
    async def get_page(self) -> Page:
        """
        Obtener una página del pool o crear una nueva si no hay disponibles.
        La página debe ser devuelta con return_page() después de usarse.
        """
        if not self._initialized or self._shutting_down:
            await self.initialize()
        
        if not self.context:
            raise RuntimeError("Browser context no está inicializado")
        
        # Intentar obtener una página del pool
        if self._page_pool and not self._page_pool.empty():
            try:
                page = self._page_pool.get_nowait()
                # Verificar que la página sigue siendo válida
                if not page.is_closed():
                    # Limpiar la página antes de reutilizarla
                    try:
                        await page.goto("about:blank", wait_until="domcontentloaded", timeout=1000)
                    except Exception:
                        # Si falla, crear una nueva
                        page = await self.context.new_page()
                    else:
                        return page
            except asyncio.QueueEmpty:
                pass
            except Exception as e:
                logger.warning(f"Error obteniendo página del pool: {e}")
        
        # Crear una nueva página si no hay disponibles en el pool
        page = await self.context.new_page()
        
        # Optimizaciones adicionales para la página
        await page.set_extra_http_headers({
            'Accept-Language': 'es-CO,es;q=0.9'
        })
        
        return page
    
    async def return_page(self, page: Page) -> None:
        """
        Devolver una página al pool para reutilización.
        Si el pool está lleno o la página está cerrada, simplemente la cerramos.
        """
        if self._shutting_down or not self._page_pool:
            try:
                if not page.is_closed():
                    await page.close()
            except Exception:
                pass
            return
        
        try:
            # Verificar que la página sigue siendo válida
            if page.is_closed():
                return
            
            # Limpiar la página
            try:
                await page.goto("about:blank", wait_until="domcontentloaded", timeout=1000)
            except Exception:
                # Si falla al limpiar, cerrar la página en lugar de devolverla al pool
                try:
                    await page.close()
                except Exception:
                    pass
                return
            
            # Intentar devolver al pool
            try:
                self._page_pool.put_nowait(page)
            except asyncio.QueueFull:
                # Si el pool está lleno, cerrar la página
                try:
                    await page.close()
                except Exception:
                    pass
        except Exception as e:
            logger.warning(f"Error devolviendo página al pool: {e}")
            # En caso de error, cerrar la página
            try:
                if not page.is_closed():
                    await page.close()
            except Exception:
                pass
    
    async def _cleanup(self) -> None:
        """Limpiar recursos del pool"""
        try:
            # Cerrar todas las páginas del pool
            if self._page_pool:
                while not self._page_pool.empty():
                    try:
                        page = self._page_pool.get_nowait()
                        if not page.is_closed():
                            await page.close()
                    except Exception:
                        pass
                self._page_pool = None
            
            if self.context:
                await self.context.close()
                self.context = None
            if self.browser:
                await self.browser.close()
                self.browser = None
            if self.playwright:
                await self.playwright.stop()
                self.playwright = None
            self._initialized = False
            logger.info("Pool de navegadores limpiado")
        except Exception as e:
            logger.error(f"Error limpiando pool de navegadores: {e}")
    
    async def shutdown(self) -> None:
        """Cerrar el pool (llamar en shutdown de la aplicación)"""
        if self._shutting_down:
            return
        
        self._shutting_down = True
        async with self._lock:
            await self._cleanup()
    
    async def is_healthy(self) -> bool:
        """Verificar si el pool está saludable"""
        if not self._initialized or self._shutting_down:
            return False
        try:
            # Intentar crear y cerrar una página de prueba
            if self.context:
                test_page = await self.context.new_page()
                await test_page.close()
                return True
            return False
        except Exception:
            # Si falla, reinicializar en el próximo uso
            self._initialized = False
            return False

