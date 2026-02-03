from __future__ import annotations

from typing import Any, Optional, Dict
import asyncio
from jinja2 import Environment, FileSystemLoader, select_autoescape
from markupsafe import Markup
import re
from pathlib import Path
from datetime import datetime, date

# Mapeo valor interno -> etiqueta para informe (tildes, espacios; igual que frontend)
METHOD_VALUE_TO_LABEL = {
    "hematoxilina-eosina": "Hematoxilina-Eosina",
    "inmunohistoquimica-polimero-peroxidasa": "Inmunohistoquímica: Polímero-Peroxidasa",
    "coloraciones-especiales": "Coloraciones histoquímicas",
    "inmunofluorescencia-metodo-directo": "Inmunofluorescencia: método directo",
    "microscopia-electronica-transmision": "Microscopía electrónica de transmisión",
}


def _method_values_to_labels(values: list) -> list:
    """Convierte lista de valores (keys) a etiquetas para mostrar en el informe."""
    if not values:
        return []
    out = []
    for v in values:
        if isinstance(v, str):
            label = METHOD_VALUE_TO_LABEL.get(v.strip().lower(), v.strip())
            if label:
                out.append(label)
        else:
            out.append(str(v))
    return out


class CasePdfService:
    def __init__(self, database: Any):
        from app.modules.cases.services.case_service import CaseService
        from app.modules.pathologists.services.pathologist_service import PathologistService
        from app.modules.approvals.services.approval_service import ApprovalService
        from app.modules.residents.services.resident_service import ResidentService
        
        self.case_service = CaseService(database)
        self.pathologist_service = PathologistService(database)
        self.approval_service = ApprovalService(database)
        self.resident_service = ResidentService(database)
        self.database = database
        
        templates_dir = Path(__file__).parent.parent / "templates"
        self.templates_path = templates_dir.resolve()
        self.jinja_env = Environment(
            loader=FileSystemLoader(str(self.templates_path)),
            autoescape=select_autoescape(["html", "xml"]),
            enable_async=True,
        )
        assets_dir = self.templates_path.parent / "assets"
        self.logos = self._load_logos(assets_dir)
        
        # Caché de firmas de patólogos (las firmas raramente cambian)
        self._signature_cache: Dict[str, Optional[str]] = {}

    # Sanitizador básico de HTML para PDF
    def _sanitize_html(self, html: Optional[str]) -> Markup:
        """Sanitiza HTML permitiendo un subconjunto seguro de etiquetas y estilos.
        Comentario: Mantiene alineaciones simples de texto y elimina scripts/eventos."""
        if not html:
            return Markup("")

        # Remover bloques peligrosos (script/style)
        clean = re.sub(r"(?is)<(script|style).*?>.*?</\\1>", "", html)

        # Eliminar atributos de eventos (onload, onclick, etc.)
        clean = re.sub(r"\son[a-zA-Z]+\s*=\s*(\".*?\"|\'.*?\'|[^\s>]+)", "", clean)

        # Permitir solo ciertos estilos en style="..."
        allowed_props = {"text-align", "font-weight", "font-style", "text-decoration"}

        def _clean_style(match: re.Match) -> str:
            style_val = match.group(1)
            parts = [p.strip() for p in style_val.split(";") if p.strip()]
            kept = []
            for decl in parts:
                if ":" not in decl:
                    continue
                prop, val = decl.split(":", 1)
                prop = prop.strip().lower()
                val = val.strip()
                if prop in allowed_props:
                    kept.append(f"{prop}: {val}")
            return f' style="{"; ".join(kept)}"' if kept else ""

        clean = re.sub(r"\sstyle\s*=\s*\"(.*?)\"", _clean_style, clean)
        clean = re.sub(r"\sstyle\s*=\s*\'(.*?)\'", _clean_style, clean)

        # Remover etiquetas no permitidas, conservar: div, span, br, p, b, strong, i, em, u, ul, ol, li
        allowed_tags = {"div", "span", "br", "p", "b", "strong", "i", "em", "u", "ul", "ol", "li"}

        def _filter_tag(match: re.Match) -> str:
            tag_name = match.group(1).lower()
            return match.group(0) if tag_name in allowed_tags else ""

        clean = re.sub(r"</?([a-zA-Z0-9]+)(\b[^>]*)?>", _filter_tag, clean)
        return Markup(clean)

    def _load_logos(self, assets_dir: Path) -> Dict[str, str]:
        logos: Dict[str, str] = {}
        files = {
            "lime": ("logo_lime.b64", "image/png"),
            "udea": ("logo_udea.b64", "image/png"),
            "hama": ("logo_hama.b64", "image/png"),
        }
        for key, (filename, mime) in files.items():
            path = assets_dir / filename
            if path.exists():
                data = path.read_text(encoding="utf-8").replace("\n", "").strip()
                logos[key] = f"data:{mime};base64,{data}" if data else ""
            else:
                logos[key] = ""
        return logos

    async def _render_and_generate_pdf(self, case_data: dict, case_code: str) -> bytes:
        """
        Método interno para renderizar HTML y generar PDF.
        Permite reutilización con datos pre-cargados para optimización en batch.
        """
        # Obtener pruebas complementarias pendientes de aprobación
        complementary_tests = await self._get_complementary_tests(case_code)
        
        # Obtener firma del patólogo
        pathologist_signature = await self._get_pathologist_signature(case_data)
        print(f"DEBUG: Firma obtenida: {'SÍ' if pathologist_signature else 'NO'}")

        # Renderizar template
        template = self.jinja_env.get_template("case_report.html")
        html: str = await template.render_async(
            case=case_data, 
            pathologist_signature=pathologist_signature,
            pruebas_complementarias=complementary_tests,
            logos=self.logos,
            is_pdf=True
        )

        # Generar PDF usando el pool de navegadores (mucho más eficiente)
        from app.modules.cases.services.browser_pool import BrowserPool
        
        browser_pool = await BrowserPool.get_instance()
        page = await browser_pool.get_page()  # get_page maneja la inicialización si es necesario
        
        try:
            # Usar "domcontentloaded" que es más rápido - solo espera el DOM, no los recursos
            # Para PDFs estáticos con HTML embebido esto es suficiente y mucho más rápido
            await page.set_content(html, wait_until="domcontentloaded", timeout=10000)
            pdf_bytes = await page.pdf(
                format="Letter",
                margin={"top": "15mm", "right": "12mm", "bottom": "22mm", "left": "12mm"},
                print_background=True,
                display_header_footer=True,
                header_template="<span></span>",
                footer_template=(
                    "<div style='font-family: Arial, sans-serif; font-size:10px; color:#000; width:100%; padding:0 15mm;'>"
                    "<div style='text-align:center; font-style:italic; white-space:nowrap;'>"
                    "Los informes de resultados, las placas y bloques de estudios anatomopatológicos se archivan por 15 años"
                    "</div>"
                    "<div style='border-top:1px solid #000; margin:2mm 0 0 0;'></div>"
                    "<div style='position:relative; margin-top:1mm;'>"
                    "<div style='text-align:center; font-weight:bold; white-space:nowrap;'>"
                    f"Informe No {case_data.get('caso_code') or case_data.get('id') or case_code}"
                    "</div>"
                    "<div style='position:absolute; right:0; top:0; font-weight:bold; white-space:nowrap;'>Página <span class='pageNumber'></span> de <span class='totalPages'></span></div>"
                    "</div>"
                    "</div>"
                ),
            )
        finally:
            # Devolver la página al pool para reutilización
            await browser_pool.return_page(page)

        return pdf_bytes

    async def generate_case_pdf(self, case_code: str) -> bytes:
        # Obtener datos del caso
        case_data = await self._get_case_data(case_code)
        # Usar método interno para renderizar y generar PDF
        return await self._render_and_generate_pdf(case_data, case_code)

    async def generate_batch_pdf(self, case_codes: list[str]) -> bytes:
        """
        Generar un PDF combinado con múltiples casos, cada uno con su propia numeración de páginas
        Optimizado con paralelización y pre-carga de datos para mejorar rendimiento en servidor
        
        Args:
            case_codes: Lista de códigos de caso a incluir en el PDF
            
        Returns:
            bytes: PDF combinado con todos los casos, cada uno con paginación independiente
        """
        if not case_codes:
            raise ValueError("Se requiere al menos un código de caso")
        
        from io import BytesIO
        
        try:
            from pypdf import PdfWriter, PdfReader
        except ImportError:
            raise RuntimeError("La biblioteca pypdf no está instalada. Instálela con: pip install pypdf")
        
        # Pre-cargar todos los datos de casos en paralelo para optimizar consultas a BD
        # Esto reduce el número de consultas individuales
        async def preload_case_data(case_code: str) -> tuple[str, dict | Exception]:
            """Pre-cargar datos del caso"""
            try:
                case_data = await self._get_case_data(case_code)
                return (case_code, case_data)
            except Exception as e:
                return (case_code, e)
        
        # Pre-cargar datos de todos los casos en paralelo
        preload_tasks = [preload_case_data(code) for code in case_codes]
        preloaded_data = await asyncio.gather(*preload_tasks, return_exceptions=False)
        
        # Crear un diccionario de datos pre-cargados
        case_data_cache: Dict[str, dict] = {}
        for case_code, data in preloaded_data:
            if isinstance(data, Exception):
                print(f"Error pre-cargando datos del caso {case_code}: {str(data)}")
            else:
                case_data_cache[case_code] = data
        
        # Limitar paralelismo para evitar sobrecarga del servidor
        # 5-8 PDFs simultáneos es un buen balance entre velocidad y recursos
        max_concurrent = min(8, len(case_codes))
        semaphore = asyncio.Semaphore(max_concurrent)
        
        async def generate_one_pdf(case_code: str) -> tuple[str, bytes | Exception]:
            """Generar un PDF individual con manejo de errores"""
            async with semaphore:
                try:
                    # Usar datos pre-cargados si están disponibles para optimización
                    if case_code in case_data_cache:
                        case_data = case_data_cache[case_code]
                        # Usar método interno con datos pre-cargados
                        pdf_bytes = await self._render_and_generate_pdf(case_data, case_code)
                    else:
                        # Fallback al método normal si no hay datos pre-cargados
                        pdf_bytes = await self.generate_case_pdf(case_code)
                    return (case_code, pdf_bytes)
                except Exception as e:
                    print(f"Error generando PDF para caso {case_code}: {str(e)}")
                    return (case_code, e)
        
        # Generar todos los PDFs en paralelo
        tasks = [generate_one_pdf(code) for code in case_codes]
        results = await asyncio.gather(*tasks, return_exceptions=False)
        
        # Combinar PDFs exitosos de forma optimizada
        # Para grandes volúmenes, procesar en chunks para evitar cargar todo en memoria
        successful_count = 0
        chunk_size = 50  # Procesar en chunks de 50 PDFs
        
        if len(case_codes) <= chunk_size:
            # Para volúmenes pequeños, procesar todo de una vez
            pdf_writer = PdfWriter()
            for case_code, result in results:
                if isinstance(result, Exception):
                    continue
                
                try:
                    pdf_reader = PdfReader(BytesIO(result))
                    for page in pdf_reader.pages:
                        pdf_writer.add_page(page)
                    successful_count += 1
                except Exception as e:
                    print(f"Error procesando PDF del caso {case_code}: {str(e)}")
                    continue
            
            # Generar PDF final
            output_buffer = BytesIO()
            pdf_writer.write(output_buffer)
            output_buffer.seek(0)
            return output_buffer.read()
        else:
            # Para grandes volúmenes, procesar en chunks y combinar incrementalmente
            pdf_writer = PdfWriter()
            pdf_chunks = []
            
            for i in range(0, len(results), chunk_size):
                chunk = results[i:i + chunk_size]
                chunk_writer = PdfWriter()
                
                for case_code, result in chunk:
                    if isinstance(result, Exception):
                        continue
                    
                    try:
                        pdf_reader = PdfReader(BytesIO(result))
                        for page in pdf_reader.pages:
                            chunk_writer.add_page(page)
                        successful_count += 1
                    except Exception as e:
                        print(f"Error procesando PDF del caso {case_code}: {str(e)}")
                        continue
                
                # Guardar chunk en memoria temporal
                chunk_buffer = BytesIO()
                chunk_writer.write(chunk_buffer)
                chunk_buffer.seek(0)
                pdf_chunks.append(chunk_buffer)
            
            # Combinar todos los chunks
            for chunk_buffer in pdf_chunks:
                chunk_reader = PdfReader(chunk_buffer)
                for page in chunk_reader.pages:
                    pdf_writer.add_page(page)
                chunk_buffer.close()
            
            # Generar PDF final
            output_buffer = BytesIO()
            pdf_writer.write(output_buffer)
            output_buffer.seek(0)
            result_bytes = output_buffer.read()
            output_buffer.close()
            
            if successful_count == 0:
                raise ValueError("No se pudo generar ningún caso para el PDF")
            
            return result_bytes

    async def _get_case_data(self, case_code: str) -> dict:
        """Obtener datos del caso y convertirlos al formato esperado por la plantilla"""
        case = await self.case_service.get_case(case_code)
        if not case:
            raise ValueError(f"Caso con código {case_code} no encontrado")
        
        # Convertir CaseResponse a diccionario compatible con la plantilla
        case_dict = case.model_dump()
        
        # Mapear campos del nuevo formato al formato esperado por la plantilla
        mapped_case = {
            # Información básica
            'id': case_dict.get('id'),
            'caso_code': case_dict.get('case_code'),
            'fecha_creacion': case_dict.get('created_at'),
            'fecha_firma': case_dict.get('signed_at'),
            'fecha_entrega': case_dict.get('delivered_at'),
            'updated_at': case_dict.get('updated_at'),
            'estado': case_dict.get('state'),
            
            # Información del paciente (mapear de patient_info)
            'paciente': {
                'nombre': case_dict.get('patient_info', {}).get('name', ''),
                'paciente_code': case_dict.get('patient_info', {}).get('patient_code', ''),
                'identification_type': case_dict.get('patient_info', {}).get('identification_type', None),
                'identification_number': case_dict.get('patient_info', {}).get('identification_number', ''),
                'edad': case_dict.get('patient_info', {}).get('age', ''),
                'sexo': case_dict.get('patient_info', {}).get('gender', ''),
                'telefono': case_dict.get('patient_info', {}).get('phone', ''),
                'entidad_info': {
                    'nombre': case_dict.get('patient_info', {}).get('entity_info', {}).get('name', '')
                }
            },
            
            # Médico solicitante
            'medico_solicitante': case_dict.get('requesting_physician', ''),
            
            # Servicio
            'servicio': case_dict.get('service', ''),
            
            # Patólogo asignado (mapear de assigned_pathologist)
            'patologo_asignado': {
                'nombre': case_dict.get('assigned_pathologist', {}).get('name', ''),
                'codigo': case_dict.get('assigned_pathologist', {}).get('id', ''),
                'registro_medico': case_dict.get('assigned_pathologist', {}).get('medical_license', '')
            } if case_dict.get('assigned_pathologist') else None,
            
            # Residente asignado (mapear de assigned_resident)
            'residente_asignado': None,
            
            # Muestras (mapear de samples)
            'muestras': self._map_samples(case_dict.get('samples', [])),
            
            # Resultado (mapear de result)
            'resultado': self._map_result(case_dict.get('result')),
            
            # Notas adicionales
            'notas_adicionales': case_dict.get('additional_notes', []),
            
            # Pruebas complementarias
            'complementary_tests': case_dict.get('complementary_tests', []),
            
            # Observaciones generales
            'observaciones_generales': case_dict.get('observations', '')
        }
        
        # Obtener información completa del residente si está asignado
        if case_dict.get('assigned_resident'):
            resident_id = case_dict.get('assigned_resident', {}).get('id', '')
            if resident_id:
                try:
                    resident = await self.resident_service.get_resident(resident_id)
                    if resident:
                        mapped_case['residente_asignado'] = {
                            'nombre': case_dict.get('assigned_resident', {}).get('name', ''),
                            'codigo': resident_id,
                            'registro_medico': resident.medical_license or ''
                        }
                except Exception:
                    # Si no se puede obtener el residente, usar solo los datos del caso
                    mapped_case['residente_asignado'] = {
                        'nombre': case_dict.get('assigned_resident', {}).get('name', ''),
                        'codigo': resident_id,
                        'registro_medico': ''
        }
        
        return mapped_case

    def _map_samples(self, samples: list) -> list:
        """Mapear muestras del nuevo formato al formato esperado por la plantilla"""
        mapped_samples = []
        for sample in samples:
            mapped_sample = {
                'region_cuerpo': sample.get('body_region', ''),
                'pruebas': []
            }
            
            # Mapear pruebas
            for test in sample.get('tests', []):
                mapped_test = {
                    'id': test.get('id', ''),
                    'codigo': test.get('id', ''),
                    'nombre': test.get('name', ''),
                    'cantidad': test.get('quantity', 1)
                }
                mapped_sample['pruebas'].append(mapped_test)
            
            mapped_samples.append(mapped_sample)
        
        return mapped_samples

    def _map_result(self, result: Optional[dict]) -> Optional[dict]:
        """Mapear resultado del nuevo formato al formato esperado por la plantilla"""
        if not result:
            return None

        metodo_raw = result.get('method', [])
        if not isinstance(metodo_raw, list):
            metodo_raw = [metodo_raw] if metodo_raw else []

        mapped_result = {
            'metodo': metodo_raw,
            'metodo_display': _method_values_to_labels(metodo_raw),
            # Sanitizar campos con posible HTML
            'resultado_macro': self._sanitize_html(result.get('macro_result', '')),
            'resultado_micro': self._sanitize_html(result.get('micro_result', '')),
            'diagnostico': self._sanitize_html(result.get('diagnosis', '')),
            'observaciones': self._sanitize_html(result.get('observations', '')),
            'updated_at': result.get('updated_at'),
            
            # Diagnósticos CIE-10 y CIE-O
            'diagnostico_cie10': None,
            'diagnostico_cieo': None
        }
        
        # Mapear diagnóstico CIE-10
        cie10 = result.get('cie10_diagnosis')
        if cie10:
            mapped_result['diagnostico_cie10'] = {
                'codigo': cie10.get('code', ''),
                'nombre': cie10.get('name', '')
            }
        
        # Mapear diagnóstico CIE-O
        cieo = result.get('cieo_diagnosis')
        if cieo:
            mapped_result['diagnostico_cieo'] = {
                'codigo': cieo.get('code', ''),
                'nombre': cieo.get('name', '')
            }
        
        return mapped_result

    async def _get_complementary_tests(self, case_code: str) -> Optional[dict]:
        """Obtener pruebas complementarias pendientes de aprobación"""
        try:
            # Buscar solicitudes de aprobación para este caso
            from app.modules.approvals.schemas.approval import ApprovalRequestSearch
            from app.modules.approvals.models.approval_request import ApprovalStateEnum
            
            search_params = ApprovalRequestSearch(
                original_case_code=case_code,
                approval_state=ApprovalStateEnum.REQUEST_MADE
            )
            approval_requests = await self.approval_service.search_approvals(search_params)
            
            if not approval_requests or len(approval_requests) == 0:
                # Intentar buscar en pending_approval también
                search_params.approval_state = ApprovalStateEnum.PENDING_APPROVAL
                approval_requests = await self.approval_service.search_approvals(search_params)
                
                if not approval_requests or len(approval_requests) == 0:
                    return None
            
            # Tomar la primera solicitud pendiente
            approval = approval_requests[0]
            
            # Extraer motivo del approval_info
            motivo = ''
            if approval.approval_info:
                motivo = approval.approval_info.reason or ''
            
            # Mapear al formato esperado por la plantilla
            complementary_tests = {
                'pruebas': [],
                'motivo': motivo,
                'fecha_solicitud': approval.created_at,
                'estado': approval.approval_state.value if hasattr(approval.approval_state, 'value') else str(approval.approval_state)
            }
            
            # Mapear pruebas complementarias
            for test in approval.complementary_tests or []:
                # test es un objeto ComplementaryTestInfo
                mapped_test = {
                    'codigo': test.code if hasattr(test, 'code') else test.get('code', ''),
                    'nombre': test.name if hasattr(test, 'name') else test.get('name', ''),
                    'cantidad': test.quantity if hasattr(test, 'quantity') else test.get('quantity', 1)
                }
                complementary_tests['pruebas'].append(mapped_test)
            
            return complementary_tests
            
        except Exception as e:
            print(f"Error obteniendo pruebas complementarias: {e}")
            import traceback
            traceback.print_exc()
            return None

    async def _get_pathologist_signature(self, case_data: dict) -> Optional[str]:
        """Obtener la firma del patólogo asignado. Soporta firmas base64 en BD y rutas antiguas."""
        try:
            patologo_asignado = case_data.get('patologo_asignado')
            pathologist_id = None

            if patologo_asignado:
                pathologist_id = patologo_asignado.get('codigo') or patologo_asignado.get('id')
                if pathologist_id:
                    print(f"DEBUG: Patólogo asignado encontrado: {pathologist_id}")

            if not pathologist_id:
                print("DEBUG: No hay patólogo asignado para obtener firma")
                return None

            # Verificar caché
            if pathologist_id in self._signature_cache:
                cached_signature = self._signature_cache[pathologist_id]
                if cached_signature is not None:
                    print(f"DEBUG: Firma obtenida desde caché para ID: {pathologist_id}")
                return cached_signature

            # Obtener patólogo desde la BD
            try:
                pathologist = await self.pathologist_service.get_pathologist(pathologist_id)
            except Exception as e:
                print(f"DEBUG: No se pudo obtener el patólogo {pathologist_id}: {e}")
                self._signature_cache[pathologist_id] = None
                return None

            signature_value = getattr(pathologist, "signature", None)

            # Sin firma registrada
            if not signature_value:
                self._signature_cache[pathologist_id] = None
                print(f"DEBUG: Patólogo {pathologist_id} no tiene firma registrada")
                return None

            # Si ya es data URL, usar tal cual
            if signature_value.startswith("data:"):
                self._signature_cache[pathologist_id] = signature_value
                print(f"DEBUG: Firma base64 obtenida desde BD para ID: {pathologist_id}")
                return signature_value

            # Si es URL absoluta, devolver directamente
            if signature_value.startswith("http"):
                self._signature_cache[pathologist_id] = signature_value
                print(f"DEBUG: Firma URL absoluta para ID: {pathologist_id}")
                return signature_value

            # Si es una ruta relativa (legacy /uploads/signatures/xxx), leer y convertir a base64
            import base64
            from pathlib import Path

            rel_path = signature_value[1:] if signature_value.startswith('/') else signature_value
            project_root = Path(__file__).parent.parent.parent.parent.parent
            file_path = project_root / rel_path

            if not file_path.exists():
                print(f"DEBUG: Ruta de firma no encontrada en disco: {file_path}")
                self._signature_cache[pathologist_id] = None
                return None

            mime_map = {
                '.jpg': 'image/jpeg',
                '.jpeg': 'image/jpeg',
                '.png': 'image/png',
                '.gif': 'image/gif',
                '.webp': 'image/webp'
            }
            file_ext = file_path.suffix.lower()
            mime = mime_map.get(file_ext, 'image/png')

            with open(file_path, "rb") as img_file:
                img_data = img_file.read()
                img_base64 = base64.b64encode(img_data).decode('utf-8')
                data_url = f"data:{mime};base64,{img_base64}"
                self._signature_cache[pathologist_id] = data_url
                print(f"DEBUG: Firma convertida desde archivo legacy para ID: {pathologist_id}")
                return data_url

        except Exception as e:
            print(f"Error obteniendo firma del patólogo: {e}")
            if 'pathologist_id' in locals() and pathologist_id:
                self._signature_cache[pathologist_id] = None
            return None
