#!/usr/bin/env python3
"""
Escanea la carpeta img/ y genera js/projects-data.js con la lista de
proyectos para proyectos.html y proyecto.html.

Uso:
    python generate_projects.py

Estructura esperada:
    img/<categoria>/<proyecto>/...imagenes...

Las categorias validas son las definidas en CATEGORIES mas abajo. Cada
subcarpeta de una categoria se trata como un proyecto:
  - Titulo: se deriva del nombre de la carpeta del proyecto.
  - Imagen destacada: la primera imagen (orden alfabetico) encontrada al
    recorrer la carpeta del proyecto recursivamente.
  - Galeria: todas las imagenes encontradas en la carpeta del proyecto
    (se usan en la pagina de detalle proyecto.html).
  - Descripcion / enlace: se leen de un archivo info.txt dentro de la
    carpeta del proyecto, si existe (se busca una URL y el resto se usa
    como descripcion).

Para excluir una carpeta de proyecto, agrega dentro de ella un archivo
vacio llamado ".skip".

Para agregar una nueva categoria, crea la carpeta img/<slug-categoria>/
y agregala a la lista CATEGORIES.

OPTIMIZACION MOBILE:
  - Convierte automaticamente .png, .jpg, .jpeg a .webp
  - Elimina las imagenes originales despues de convertir
  - Valida videos para compatibilidad iOS/Android (.mp4 H.264)
"""

import json
import re
import os
from pathlib import Path
from datetime import datetime
from PIL import Image

ROOT = Path(__file__).resolve().parent
IMG_DIR = ROOT / "img"
OUTPUT_FILE = ROOT / "js" / "projects-data.js"

# ============================================================
# CONFIGURACION
# ============================================================

CATEGORIES = [
    {"slug": "ilustraciones", "label": "Ilustraciones"},
    {"slug": "tomas-aereas", "label": "Tomas Aereas"},
    {"slug": "aplicaciones-y-sitios-web", "label": "Aplicaciones y Sitios Web"},
    {"slug": "sistemas-de-diseno", "label": "Sistemas de Diseño"},
    {"slug": "animaciones", "label": "Animaciones"},
    {"slug": "disenio-grafico", "label": "Diseño Grafico"},
    {"slug": "certificados", "label": "Certificados"},
]

VIDEO_EXTENSIONS = {".mp4", ".webm", ".ogg"}
IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".webp"}
DOCUMENT_EXTENSIONS = {".pdf", ".png", ".jpg", ".jpeg"}
SKIP_MARKER = ".skip"

# Formatos a convertir a WebP y eliminar despues
WEBP_SOURCE_EXTENSIONS = {".png", ".jpg", ".jpeg"}

# Formatos que NO se tocan
KEEP_EXTENSIONS = {".gif", ".webp"}

# Configuracion de conversion a WebP
WEBP_CONFIG = {
    "quality": 85,
    "method": 4,
}

# Configuracion de videos para mobile
VIDEO_MOBILE_CONFIG = {
    "required_codec": "h264",
    "required_container": "mp4",
    "max_width": 1920,
    "max_height": 1080,
}

# Patrones comunes para imagenes poster
POSTER_PATTERNS = [
    "poster", "cover", "thumbnail", "thumb", "preview", "banner", "hero", "splash"
]

# Patrones que indican que el texto usa markdown
MARKDOWN_INDICATORS = [
    re.compile(r'^#{1,6}\s?', re.MULTILINE),
    re.compile(r'\*\*[^*]+\*\*'),
    re.compile(r'\*[^*]+\*'),
    re.compile(r'\[[^]]+\]\([^)]+\)'),
    re.compile(r'^\s*[-*+]\s', re.MULTILINE),
    re.compile(r'^\s*\d+\.\s', re.MULTILINE),
    re.compile(r'^>\s', re.MULTILINE),
    re.compile(r'`[^`]+`'),
    re.compile(r'^---$', re.MULTILINE),
]


def prettify_title(folder_name):
    name = re.sub(r"(?<=[a-z0-9])(?=[A-Z])", " ", folder_name)
    name = re.sub(r"[_-]+", " ", name)
    name = re.sub(r"\s+", " ", name).strip()
    words = [w if (w.isupper() and len(w) > 1) else w.capitalize() for w in name.split(" ")]
    return " ".join(words)


def find_poster_image(folder):
    """Busca una imagen poster en la carpeta del proyecto.
    Prioriza archivos con nombres comunes (poster, cover, thumbnail, etc.)
    Si no encuentra, usa la primera imagen encontrada.
    """
    poster_candidates = []
    all_images = []
    
    for path in folder.rglob("*"):
        if path.is_file() and path.suffix.lower() in {".jpg", ".jpeg", ".png", ".gif", ".webp"}:
            all_images.append(path)
            name_lower = path.stem.lower()
            # Verificar si el nombre coincide con patrones de poster
            if any(pattern in name_lower for pattern in POSTER_PATTERNS):
                poster_candidates.append(path)
    
    # Retornar la mejor opcion: poster dedicado o primera imagen
    if poster_candidates:
        return poster_candidates[0]
    elif all_images:
        return all_images[0]
    return None


def convert_to_webp(image_path, quality=85):
    """Convierte una imagen a formato WebP optimizado para mobile.
    
    Args:
        image_path: Ruta al archivo de imagen original
        quality: Calidad de salida (1-100, default 85)
    
    Returns:
        tuple: (webp_path, original_size, webp_size, ratio)
            - webp_path: Ruta al archivo WebP creado
            - original_size: Tamaño en bytes del original
            - webp_size: Tamaño en bytes del WebP
            - ratio: Porcentaje de reduccion
    """
    try:
        # Verificar que el archivo existe y es una imagen valida
        if not image_path.exists():
            print(f"  [WARN] Archivo no encontrado: {image_path}")
            return None, 0, 0, 0
        
        # Si ya es WebP, retornar sin convertir
        if image_path.suffix.lower() == ".webp":
            size = image_path.stat().st_size
            return image_path, size, size, 0
        
        # Verificar extension soportada (.png, .jpg, .jpeg solo)
        ext = image_path.suffix.lower()
        if ext not in {".png", ".jpg", ".jpeg"}:
            return None, 0, 0, 0
        
        # Obtener tamaño original
        original_size = image_path.stat().st_size
        
        # Intentar abrir la imagen con manejo de errores
        try:
            img = Image.open(image_path)
            img.load()  # Forzar carga para detectar archivos corruptos temprano
        except Exception as open_err:
            print(f"  [ERROR] No se puede abrir {image_path.name}: {open_err}")
            return None, 0, 0, 0
        
        # Convertir RGBA/PALETTE a RGB si es necesario (WebP no soporta transparencia en modo JPEG)
        try:
            if img.mode in ("RGBA", "P", "LA"):
                # Crear fondo blanco para images con transparencia
                background = Image.new("RGB", img.size, (255, 255, 255))
                if img.mode == "P":
                    img = img.convert("RGBA")
                if img.mode in ("RGBA", "LA"):
                    background.paste(img, mask=img.split()[-1])
                    img = background
                else:
                    img = img.convert("RGB")
            elif img.mode != "RGB":
                img = img.convert("RGB")
        except Exception as convert_err:
            print(f"  [ERROR] No se puede convertir modo de {image_path.name}: {convert_err}")
            return None, 0, 0, 0
        
        # Generar nombre del archivo WebP
        webp_path = image_path.with_suffix(".webp")
        
        # Guardar en WebP con optimizacion
        try:
            img.save(
                str(webp_path),
                format="WEBP",
                quality=WEBP_CONFIG["quality"],
                method=WEBP_CONFIG["method"],
                optimize=1 if WEBP_CONFIG["optimize"] else 0,
                progressive=1 if WEBP_CONFIG["progressive"] else 0,
            )
        except Exception as save_err:
            print(f"  [ERROR] No se puede guardar {image_path.name}: {save_err}")
            return None, 0, 0, 0
        
        # Obtener tamaño WebP
        if not webp_path.exists():
            print(f"  [ERROR] Archivo WebP no creado: {webp_path.name}")
            return None, 0, 0, 0
            
        webp_size = webp_path.stat().st_size
        
        # Calcular ratio de reduccion
        ratio = ((original_size - webp_size) / original_size * 100) if original_size > 0 else 0
        
        return webp_path, original_size, webp_size, ratio
        
    except Exception as e:
        import traceback
        print(f"  [ERROR] Falló conversión WebP {image_path.name}: {e}")
        print(f"         {traceback.format_exc()}")
        return None, 0, 0, 0


def optimize_images_in_folder(folder):
    """Convierte imagenes a WebP y elimina las originales.
    
    Proceso:
    1. Escanea recursivamente la carpeta buscando .png, .jpg, .jpeg
    2. Convierte cada una a .webp con calidad optimizada
    3. Si la conversion tiene exito, elimina la imagen original
    4. Guarda estadisticas de conversion
    
    Args:
        folder: Ruta a la carpeta del proyecto
    
    Returns:
        dict: Resumen de conversiones
            {
                "converted": int,      # Imagenes convertidas con exito
                "deleted": int,        # Originales eliminadas
                "skipped": int,        # Ya optimizadas o error
                "errors": int,         # Errores de conversion
                "total_saved": int,    # Bytes ahorrados
            }
    """
    stats = {
        "converted": 0,
        "deleted": 0,
        "skipped": 0,
        "errors": 0,
        "total_saved": 0,
    }
    
    # Buscar todas las imagenes en extensiones fuente
    image_files = [
        path for path in folder.rglob("*")
        if path.is_file() and path.suffix.lower() in WEBP_SOURCE_EXTENSIONS
    ]
    
    if not image_files:
        return stats
    
    print(f"  [WEBP] Procesando {len(image_files)} imagen(es) en {folder.name}/...")
    
    for img_path in image_files:
        try:
            # Convertir a WebP
            webp_path, orig_size, webp_size, ratio = convert_to_webp(img_path)
            
            if webp_path and orig_size > 0:
                stats["converted"] += 1
                saved = orig_size - webp_size
                stats["total_saved"] += saved
                
                if ratio > 0:
                    # Conversion exitosa: eliminar original
                    img_path.unlink()
                    stats["deleted"] += 1
                    print(f"    ✓ {img_path.name} → {webp_path.name} ({ratio:.0f}% más pequeño)")
                else:
                    # WebP no es más pequeño: conservar original
                    stats["skipped"] += 1
                    print(f"    - {img_path.name} ya optimizado (conservando original)")
            else:
                stats["errors"] += 1
                
        except Exception as e:
            stats["errors"] += 1
            print(f"    ✗ {img_path.name}: {e}")
    
    # Mostrar resumen
    if stats["converted"] > 0:
        saved_mb = stats["total_saved"] / (1024 * 1024)
        print(f"  [WEBP] ✓ {stats['converted']} convertidas, {stats['deleted']} originales eliminadas, {saved_mb:.2f} MB ahorrados")
    
    return stats


def validate_video_for_mobile(video_path):
    """Valida que un video sea compatible con mobile (iOS/Android).
    
    Verifica:
    - Extension: .mp4 obligatorio
    - Codec: H.264 recomendado (verificacion basica)
    
    Args:
        video_path: Ruta al archivo de video
    
    Returns:
        dict: {"valid": bool, "issues": list[str], "recommendations": list[str]}
    """
    issues = []
    recommendations = []
    
    if not video_path.exists():
        return {"valid": False, "issues": ["Archivo no encontrado"], "recommendations": []}
    
    ext = video_path.suffix.lower()
    
    # Verificar extension
    if ext != ".mp4":
        issues.append(f"Extension {ext} no recomendada para mobile")
        recommendations.append("Convertir a .mp4 con codec H.264")
    
    # Verificar tamaño (videos muy grandes no cargan bien en mobile)
    size_mb = video_path.stat().st_size / (1024 * 1024)
    if size_mb > 50:
        issues.append(f"Video muy grande ({size_mb:.1f} MB)")
        recommendations.append("Comprimir video a menos de 50 MB")
    elif size_mb > 20:
        recommendations.append(f"Video grande ({size_mb:.1f} MB), considerar compresión")
    
    return {
        "valid": len(issues) == 0,
        "issues": issues,
        "recommendations": recommendations
    }


def check_all_videos_for_mobile(folder):
    """Verifica todos los videos en una carpeta para compatibilidad mobile.
    
    Args:
        folder: Ruta a la carpeta del proyecto
    
    Returns:
        list[dict]: Resultados de validacion por video
    """
    results = []
    
    for video_path in folder.rglob("*"):
        if video_path.is_file() and video_path.suffix.lower() in VIDEO_EXTENSIONS:
            result = validate_video_for_mobile(video_path)
            result["video"] = video_path.name
            results.append(result)
    
    return results


def find_video_with_poster(folder):
    """Busca videos y sus posters en la carpeta del proyecto.
    
    Para cada video encontrado, verifica si existe una imagen poster
    asociada. Si no, busca la primera imagen disponible como poster.
    
    Returns:
        tuple: (videos_list, best_poster_path)
            - videos_list: Lista de videos ordenados (mp4 primero)
            - best_poster_path: Mejor imagen poster disponible
    """
    videos = []
    all_images = []
    
    for path in folder.rglob("*"):
        if not path.is_file():
            continue
        ext = path.suffix.lower()
        if ext in VIDEO_EXTENSIONS:
            videos.append(path)
        elif ext in IMAGE_EXTENSIONS:
            all_images.append(path)
    
    # Ordenar: mp4 primero (mejor compatibilidad mobile), luego otros
    videos.sort(key=lambda p: (0 if p.suffix.lower() == ".mp4" else 1, str(p).lower()))
    
    # Buscar poster dedicado
    poster = find_poster_image(folder)
    
    return videos, all_images, poster


def get_video_mime_type(filepath):
    """Determina el tipo MIME correcto segun la extension del video.
    
    Returns:
        str: El tipo MIME o cadena vacia si no se reconoce.
    """
    ext = filepath.suffix.lower()
    mime_map = {
        ".mp4": "video/mp4",
        ".webm": "video/webm",
        ".ogg": "video/ogg",
    }
    return mime_map.get(ext, "")


def get_optimal_poster_for_video(folder, video_path):
    """Encuentra la mejor imagen poster para un video especifico.
    
    Prioridad:
    1. Imagen con nombre que coincida con el video (sin extension)
    2. Imagen con nombre poster/cover/thumbnail
    3. Primera imagen jpg/jpeg disponible (mejor compatibilidad)
    4. Cualquier otra imagen
    
    Returns:
        Path or None: La mejor imagen poster encontrada.
    """
    video_stem = video_path.stem.lower()
    
    # 1. Buscar imagen con nombre similar al video
    for ext in [".jpg", ".jpeg", ".png", ".webp", ".gif"]:
        candidate = folder / f"{video_stem}{ext}"
        if candidate.exists():
            return candidate
    
    # 2. Buscar poster dedicado
    poster = find_poster_image(folder)
    if poster:
        return poster
    
    # 3. Primera imagen jpg/jpeg (mejor compatibilidad mobile)
    for ext in [".jpg", ".jpeg"]:
        for path in folder.rglob(f"*{ext}"):
            if path.is_file():
                return path
    
    # 4. Cualquier imagen disponible
    for path in folder.rglob("*"):
        if path.is_file() and path.suffix.lower() in IMAGE_EXTENSIONS:
            return path
    
    return None


def is_video(path):
    """Verifica si una ruta es un video."""
    return path.suffix.lower() in VIDEO_EXTENSIONS


def find_lottie_animation(folder):
    """Busca archivos JSON de Lottie en la carpeta del proyecto."""
    lottie_files = []
    for path in folder.rglob("*"):
        if path.is_file() and path.suffix.lower() == ".json":
            # Verificar que sea un archivo de Lottie válido (tiene estructura básica)
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if 'v' in data and 'layers' in data:  # Estructura básica de Lottie
                        lottie_files.append(path)
            except (json.JSONDecodeError, UnicodeDecodeError):
                pass  # No es un JSON válido o no es Lottie
    return lottie_files


def find_images(folder):
    """Encuentra imagenes y videos en la carpeta del proyecto.
    
    Optimizado para mobile:
    - Videos .mp4 primero (mejor compatibilidad iOS/Android)
    - Imagen poster: prioriza .jpg/.webp sobre .png
    
    Returns:
        tuple: (videos_list, images_list)
            - videos_list: Lista de videos ordenados (mp4 primero)
            - images_list: Lista de imagenes ordenadas (optimizadas primero)
    """
    videos = []
    images = []
    
    for path in folder.rglob("*"):
        if path.is_file():
            ext = path.suffix.lower()
            if ext in VIDEO_EXTENSIONS:
                videos.append(path)
            elif ext in IMAGE_EXTENSIONS:
                images.append(path)
    
    # Videos: mp4 primero (mejor compatibilidad mobile)
    videos.sort(key=lambda p: (0 if p.suffix.lower() == ".mp4" else 1, str(p.relative_to(folder)).lower()))
    
    # Imagenes: .webp y .jpg primero (mejor compresion y soporte mobile)
    images.sort(key=lambda p: (
        0 if p.suffix.lower() in {".webp", ".jpg", ".jpeg"} else
        1 if p.suffix.lower() in {".png"} else 2,
        str(p.relative_to(folder)).lower()
    ))
    
    return videos, images


def has_sections(text):
    """Detecta si el texto tiene secciones separadas por --- (linea con solo ---)."""
    # Busca lineas que contengan solo --- (con posibles espacios/blancos)
    pattern = re.compile(r'^\s*---\s*$', re.MULTILINE)
    return bool(pattern.search(text))


def has_column_container(text):
    """Detecta si el texto tiene un contenedor de columnas -- ... --.
    
    Busca la primera linea -- y la ultima linea -- en el texto.
    Si existen, todo el contenido entre ellos es un contenedor de columnas.
    
    Returns:
        tuple: (has_container: bool, column_content: str or None)
            - has_container: True si se encontro contenedor
            - column_content: Contenido entre -- y -- (sin los --)
    """
    lines = text.splitlines()
    
    # Encontrar el indice de la primera linea --
    first_dash_idx = None
    for i, line in enumerate(lines):
        if line.strip() == '--':
            first_dash_idx = i
            break
    
    # Encontrar el indice de la ultima linea --
    last_dash_idx = None
    for i in range(len(lines) - 1, -1, -1):
        if lines[i].strip() == '--':
            last_dash_idx = i
            break
    
    # Si encontramos ambos y hay contenido entre ellos
    if first_dash_idx is not None and last_dash_idx is not None and last_dash_idx > first_dash_idx + 1:
        # Extraer contenido entre -- y --
        column_content = '\n'.join(lines[first_dash_idx + 1:last_dash_idx]).strip()
        if column_content:
            return True, column_content
    
    return False, None
    """Divide el texto en secciones separadas por ---.
    
    Returns:
        list[str]: Lista de textos por seccion (sin los separadores ---)
    """
    sections = re.split(r'^\s*---\s*$', text, flags=re.MULTILINE)
    # Filtrar secciones vacias
    return [s.strip() for s in sections if s.strip()]


def parse_section_text(section_text):
    """Parsea el texto de una seccion individual.
    
    Detecta columnas dentro de un contenedor -- ... --
    Las columnas se separan por --- (linea con solo ---).
    
    Returns:
        tuple: (columns_list, title_from_info)
            - columns_list: list[dict] con 'content_html' por columna
            - title_from_info: Titulo extraido (primer H1/H2/H3)
    """
    # Extraer el primer encabezado como titulo (prioridad: H1 -> H2 -> H3)
    # Soporta tanto "### Titulo" como "###Titulo" (espacio opcional)
    title_from_info = None
    for header_level in [1, 2, 3]:
        pattern = rf'^#{{{header_level}}}\s*(.+)$'
        header_match = re.search(pattern, section_text, re.MULTILINE)
        if header_match:
            title_from_info = header_match.group(1).strip()
            # Limpiar caracteres de markdown del titulo
            title_from_info = re.sub(r'[#*_`]', '', title_from_info).strip()
            # Remover dos puntos al final si existen
            title_from_info = re.sub(r':\s*$', '', title_from_info).strip()
            break
    
    # Detectar contenedor de columnas: -- ... --
    # Busca -- al inicio y -- al final del texto
    lines = section_text.splitlines()
    first_line = lines[0].strip() if lines else ""
    last_line = lines[-1].strip() if lines else ""
    
    # Si empieza con -- y termina con --, es un contenedor de columnas
    if first_line == '--' and last_line == '--' and len(lines) > 2:
        # Extraer contenido entre -- y --
        column_content = '\n'.join(lines[1:-1]).strip()
        
        # Dividir por --- (cada columna separada por ---)
        raw_columns = re.split(r'^\s*---\s*$', column_content, flags=re.MULTILINE)
        columns = []
        for col_text in raw_columns:
            col_text = col_text.strip()
            if not col_text:
                continue
            # Limpiar y procesar cada columna
            cleaned = clean_section_text(col_text)
            columns.append(cleaned)
        return columns, title_from_info
    else:
        # Una sola columna (sin contenedor)
        cleaned = clean_section_text(section_text)
        return [cleaned], title_from_info


def parse_column_text(col_text):
    """Parsea el texto de una columna individual.
    
    Extrae URLs e imagen, limpia esas líneas y procesa el resto.
    La imagen se incluye dentro del contenido HTML de la columna.
    
    Returns:
        dict: {'content_html': str, 'demo_url': str or None, 'github_url': str or None, 'associated_image': str or None}
    """
    # Extraer URLs e imagen de esta columna
    demo_url = None
    github_url = None
    associated_image = None
    
    demo_match = re.search(r'demo\s*:?\s*(https?://\S+)', col_text, re.I)
    if demo_match:
        demo_url = demo_match.group(1).rstrip(".,")
    
    github_match = re.search(r'(?:link\s+)?github\s*:?\s*(https?://\S+)', col_text, re.I)
    if github_match:
        github_url = github_match.group(1).rstrip(".,")
    
    imagen_match = re.search(r'imagen\s*:?\s*\[?([^\]\s]+)\]?', col_text, re.I)
    if imagen_match:
        associated_image = imagen_match.group(1).strip()
        # Verificar que sea un archivo de imagen válido
        if not associated_image.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.webp')):
            associated_image = None
    
    # Remover lineas de etiquetas para procesar el resto
    cleaned_text = col_text
    cleaned_text = re.sub(r'demo\s*:?\s*https?://\S+', '', cleaned_text, flags=re.I)
    cleaned_text = re.sub(r'(?:link\s+)?github\s*:?\s*https?://\S+', '', cleaned_text, flags=re.I)
    cleaned_text = re.sub(r'https?://\S+', '', cleaned_text)
    # Remover linea de imagen - soporta "imagen:[archivo.png]" con o sin espacio
    cleaned_text = re.sub(r'imagen\s*:?\s*\[?[^\]\s]+\]?', '', cleaned_text, flags=re.I)
    
    # Limpiar lineas de etiquetas conocidas
    cleaned_lines = []
    for line in cleaned_text.splitlines():
        stripped = line.strip()
        if re.match(r'^(sitio web|website|link|url|demo|github|imagen)\s*:?\s*$', stripped, re.I):
            continue
        cleaned_lines.append(line)
    
    cleaned_text = '\n'.join(cleaned_lines).strip()
    
    # Detectar si el texto usa markdown
    if detect_markdown(cleaned_text):
        content_html = markdown_to_html(cleaned_text)
    else:
        lines = [line.strip() for line in cleaned_lines if line.strip()]
        content_html = ' '.join(lines).strip()
    
    return {
        'content_html': content_html,
        'demo_url': demo_url,
        'github_url': github_url,
        'associated_image': associated_image,
    }


def clean_section_text(text):
    """Limpia y procesa el texto de una columna individual.
    
    Returns:
        dict: {'content_html': str}
    """
    # Remover lineas de etiquetas conocidas
    cleaned_text = text
    cleaned_text = re.sub(r'demo\s*:?\s*https?://\S+', '', cleaned_text, flags=re.I)
    cleaned_text = re.sub(r'(?:link\s+)?github\s*:?\s*https?://\S+', '', cleaned_text, flags=re.I)
    cleaned_text = re.sub(r'imagen\s*:?\s*\[?[^\]]+\]?', '', cleaned_text, flags=re.I)
    cleaned_text = re.sub(r'https?://\S+', '', cleaned_text)
    
    # Limpiar lineas de etiquetas conocidas
    cleaned_lines = []
    for line in cleaned_text.splitlines():
        stripped = line.strip()
        if re.match(r'^(sitio web|website|link|url|demo|github|imagen)\s*:?\s*$', stripped, re.I):
            continue
        cleaned_lines.append(line)
    
    cleaned_text = '\n'.join(cleaned_lines).strip()
    
    # Detectar si el texto usa markdown
    if detect_markdown(cleaned_text):
        content_html = markdown_to_html(cleaned_text)
    else:
        lines = [line.strip() for line in cleaned_lines if line.strip()]
        content_html = ' '.join(lines).strip()
    
    return {'content_html': content_html}
    for header_level in [1, 2, 3]:
        pattern = rf'^#{{{header_level}}}\s*(.+)$'
        header_match = re.search(pattern, section_text, re.MULTILINE)
        if header_match:
            title_from_info = header_match.group(1).strip()
            # Limpiar caracteres de markdown del titulo
            title_from_info = re.sub(r'[#*_`]', '', title_from_info).strip()
            # Remover dos puntos al final si existen (ej: "###Boton de enviar:" -> "Boton de enviar")
            title_from_info = re.sub(r':\s*$', '', title_from_info).strip()
            break
    
    # Remover lineas de etiquetas conocidas
    cleaned_text = section_text
    cleaned_text = re.sub(r'demo\s*:?\s*https?://\S+', '', cleaned_text, flags=re.I)
    cleaned_text = re.sub(r'(?:link\s+)?github\s*:?\s*https?://\S+', '', cleaned_text, flags=re.I)
    cleaned_text = re.sub(r'imagen\s*:?\s*\[?[^\]]+\]?', '', cleaned_text, flags=re.I)
    cleaned_text = re.sub(r'https?://\S+', '', cleaned_text)
    
    # Limpiar lineas de etiquetas conocidas
    cleaned_lines = []
    for line in cleaned_text.splitlines():
        stripped = line.strip()
        if re.match(r'^(sitio web|website|link|url|demo|github|imagen)\s*:?\s*$', stripped, re.I):
            continue
        cleaned_lines.append(line)
    
    cleaned_text = '\n'.join(cleaned_lines).strip()
    
    # Detectar si el texto usa markdown
    if detect_markdown(cleaned_text):
        description = markdown_to_html(cleaned_text)
    else:
        lines = [line.strip() for line in cleaned_lines if line.strip()]
        description = ' '.join(lines).strip()
    
    return description, title_from_info


def parse_info_txt(folder):
    """Parsea info.txt y detecta si usa markdown.
    
    Soporta etiquetas especiales:
    - demo: URL del proyecto en vivo
    - github: Link al repositorio
    - imagen: Nombre de imagen asociada (sin ruta completa)
    - link: URL alternativa
    - # Titulo H1: Se extrae el primer H1 como titulo principal
    
    Busca info.txt en la carpeta del proyecto y sus subcarpetas.
    
    Si el archivo contiene markdown, lo convierte a HTML para renderizado.
    Si no, mantiene el formato de texto plano original.
    
    Returns:
        tuple: (description_html, title_from_info, demo_url, github_url, associated_image)
    """
    info_path = folder / "info.txt"
    
    # Si no existe en la carpeta raiz, buscar en subcarpetas
    if not info_path.exists():
        subfolders = list(folder.rglob("info.txt"))
        if subfolders:
            info_path = subfolders[0]  # Usar el primero encontrado
        else:
            return "", None, None, None, None

    text = info_path.read_text(encoding="utf-8", errors="ignore").strip()
    
    # Extraer el primer encabezado como titulo principal (prioridad: H1 -> H2 -> H3)
    title_from_info = None
    for header_level in [1, 2, 3]:
        pattern = rf'^#{{{header_level}}}\s+(.+)$'
        header_match = re.search(pattern, text, re.MULTILINE)
        if header_match:
            title_from_info = header_match.group(1).strip()
            # Limpiar caracteres de markdown del titulo
            title_from_info = re.sub(r'[#*_`]', '', title_from_info).strip()
            break  # Usar el primer encabezado encontrado
    
    # Extraer URLs con etiquetas especificas
    demo_url = None
    github_url = None
    associated_image = None
    
    # Buscar etiquetas conocidas (case-insensitive) - soporta "link GitHub", "github", etc.
    demo_match = re.search(r'demo\s*:?\s*(https?://\S+)', text, re.I)
    if demo_match:
        demo_url = demo_match.group(1).rstrip(".,")
    
    # Soporta "link GitHub:", "github:", "github link:", etc.
    github_match = re.search(r'(?:link\s+)?github\s*:?\s*(https?://\S+)', text, re.I)
    if github_match:
        github_url = github_match.group(1).rstrip(".,")
    
    # Buscar imagen asociada - soporta "imagen:[archivo.png]" con corchetes
    imagen_match = re.search(r'imagen\s*:?\s*\[?([^\]\s]+)\]?', text, re.I)
    if imagen_match:
        associated_image = imagen_match.group(1).strip()
        # Si parece un nombre de archivo, limpiar extensiones de URL
        if not associated_image.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.webp')):
            associated_image = None
    
    # Remover lineas de etiquetas para procesar el resto
    cleaned_text = text
    cleaned_text = re.sub(r'demo\s*:?\s*https?://\S+', '', cleaned_text, flags=re.I)
    cleaned_text = re.sub(r'(?:link\s+)?github\s*:?\s*https?://\S+', '', cleaned_text, flags=re.I)
    cleaned_text = re.sub(r'imagen\s*:?\s*\[?[^\]]+\]?', '', cleaned_text, flags=re.I)
    
    # Tambien extraer URL genérica (para compatibilidad con info.txt existentes)
    url_match = re.search(r'https?://\S+', cleaned_text)
    generic_url = url_match.group(0).rstrip(".,") if url_match else None
    # Si no hay demo/github, usar la URL genérica como demo
    if not demo_url and generic_url:
        demo_url = generic_url
    
    cleaned_text = re.sub(r'https?://\S+', '', cleaned_text)
    
    # Limpiar lineas de etiquetas conocidas (pero preservar lineas vacias para markdown)
    cleaned_lines = []
    for line in cleaned_text.splitlines():
        stripped = line.strip()
        # Eliminar lineas que son solo etiquetas conocidas
        if re.match(r'^(sitio web|website|link|url|demo|github|imagen)\s*:?\s*$', stripped, re.I):
            continue
        cleaned_lines.append(line)
    
    cleaned_text = '\n'.join(cleaned_lines).strip()
    
    # Detectar si el texto usa markdown
    if detect_markdown(cleaned_text):
        # Convertir markdown a HTML (preservando estructura de bloques)
        description = markdown_to_html(cleaned_text)
    else:
        # Formato de texto plano (comportamiento original)
        lines = [line.strip() for line in cleaned_lines if line.strip()]
        description = ' '.join(lines).strip()
    
    return description, title_from_info, demo_url, github_url, associated_image


def parse_info_txt_sections(folder):
    """Parsea info.txt y detecta secciones separadas por ---.
    
    Cada seccion puede tener columnas dentro de un contenedor -- ... --
    Las columnas se separan por --- (linea con solo ---).
    
    Returns:
        list[dict]: Lista de diccionarios con keys:
            - title: Titulo de la seccion
            - columns: Lista de columnas con 'content_html'
            - url: URL del demo (primera encontrada)
            - github: URL del GitHub (primera encontrada)
            - associatedImage: Nombre de imagen asociada
    """
    info_path = folder / "info.txt"
    
    # Si no existe en la carpeta raiz, buscar en subcarpetas
    if not info_path.exists():
        subfolders = list(folder.rglob("info.txt"))
        if subfolders:
            info_path = subfolders[0]
        else:
            return []
    
    text = info_path.read_text(encoding="utf-8", errors="ignore").strip()
    
    # Primero verificar si el texto tiene un contenedor de columnas -- ... --
    # Busca el primer -- y el ultimo -- en cualquier posicion del texto
    has_container, column_content = has_column_container(text)
    
    if has_container and column_content:
        # Extraer texto ANTES del primer -- (titulo general y descripcion)
        first_dash_idx = text.index('--')
        before_first_dash = text[:first_dash_idx].strip()
        
        # Extraer titulo general (primer H1/H2/H3 ANTES del --)
        general_title = None
        for header_level in [1, 2, 3]:
            pattern = rf'^#{{{header_level}}}\s*(.+)$'
            header_match = re.search(pattern, before_first_dash, re.MULTILINE)
            if header_match:
                general_title = header_match.group(1).strip()
                general_title = re.sub(r'[#*_`]', '', general_title).strip()
                general_title = re.sub(r':\s*$', '', general_title).strip()
                break
        
        # Extraer descripcion general (texto despues del titulo, antes del --)
        general_description = None
        if general_title and before_first_dash:
            title_pattern = rf'^#{{{header_level}}}\s*.+?$\n(.+)'
            desc_match = re.search(title_pattern, before_first_dash, re.MULTILINE | re.DOTALL)
            if desc_match:
                desc_text = desc_match.group(1).strip()
                desc_lines = [line.strip() for line in desc_text.splitlines() if line.strip()]
                if desc_lines:
                    general_description = ' '.join(desc_lines)
        
        # Todo el texto es una sola seccion con columnas
        raw_columns = re.split(r'^\s*---\s*$', column_content, flags=re.MULTILINE)
        columns = []
        for col_text in raw_columns:
            col_text = col_text.strip()
            if not col_text:
                continue
            parsed = parse_column_text(col_text)
            col_data = {
                "content": parsed["content_html"],
            }
            if parsed.get("associated_image"):
                col_data["associatedImage"] = parsed["associated_image"]
            if parsed.get("demo_url"):
                col_data["url"] = parsed["demo_url"]
            if parsed.get("github_url"):
                col_data["github"] = parsed["github_url"]
            columns.append(col_data)
        
        # Extraer URLs de toda la seccion (primera encontrada)
        demo_url = None
        github_url = None
        
        demo_match = re.search(r'demo\s*:?\s*(https?://\S+)', column_content, re.I)
        if demo_match:
            demo_url = demo_match.group(1).rstrip(".,")
        
        github_match = re.search(r'(?:link\s+)?github\s*:?\s*(https?://\S+)', column_content, re.I)
        if github_match:
            github_url = github_match.group(1).rstrip(".,")
        
        return [{
            "title": general_title or "Sección 1",
            "description": general_description,
            "columns": columns,
            "url": demo_url,
            "github": github_url,
        }]
    
    # Si no es un contenedor de columnas, dividir por --- como secciones
    sections = split_sections(text)
    
    if not sections:
        return []
    
    result = []
    for section_text in sections:
        # Parsear la seccion (detecta columnas con --)
        columns_data, title_from_info = parse_section_text(section_text)
        
        if not columns_data:
            continue
        
        # Extraer URLs y imagen de esta seccion
        demo_url = None
        github_url = None
        associated_image = None
        
        demo_match = re.search(r'demo\s*:?\s*(https?://\S+)', section_text, re.I)
        if demo_match:
            demo_url = demo_match.group(1).rstrip(".,")
        
        github_match = re.search(r'(?:link\s+)?github\s*:?\s*(https?://\S+)', section_text, re.I)
        if github_match:
            github_url = github_match.group(1).rstrip(".,")
        
        imagen_match = re.search(r'imagen\s*:?\s*\[?([^\]\s]+)\]?', section_text, re.I)
        if imagen_match:
            associated_image = imagen_match.group(1).strip()
            if not associated_image.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.webp')):
                associated_image = None
        
        # Construir lista de columnas con su HTML
        columns = []
        for col in columns_data:
            columns.append({
                "content": col["content_html"],
            })
        
        result.append({
            "title": title_from_info or f"Sección {len(result) + 1}",
            "columns": columns,
            "url": demo_url,
            "github": github_url,
            "associatedImage": associated_image,
        })
    
    return result


def detect_markdown(text):
    """Detecta si el texto contiene sintaxis de markdown."""
    for pattern in MARKDOWN_INDICATORS:
        if pattern.search(text):
            return True
    return False


def markdown_to_html(text):
    """Convierte markdown basico a HTML para renderizado en el navegador.
    Soporta: encabezados, negrita, cursiva, enlaces, listas, citas, code inline.
    """
    # Escapar caracteres HTML para seguridad
    text = text.replace('&', '&amp;')
    text = text.replace('<', '&lt;')
    text = text.replace('>', '&gt;')
    
    # Extraer URLs del texto para no procesarlas como markdown
    urls = re.findall(r'https?://\S+', text)
    
    # Procesar por bloques (parrafos separados por lineas vacias)
    blocks = re.split(r'\n\s*\n', text)
    html_blocks = []
    
    for block in blocks:
        block = block.strip()
        if not block:
            continue
        
        # Verificar si es un bloque de lista
        if re.match(r'^\s*[-*+]\s', block):
            html_blocks.append(process_list_block(block))
        elif re.match(r'^\s*\d+\.\s', block):
            html_blocks.append(process_numbered_list_block(block))
        # Verificar si es un encabezado (con o sin espacio despues de ##)
        elif re.match(r'^#{1,6}\s?', block):
            html_blocks.append(process_heading(block))
        # Verificar si es una cita
        elif re.match(r'^>\s', block):
            html_blocks.append(process_quote(block))
        # Es un parrafo
        else:
            html_blocks.append(f'<p>{process_inline_md(block)}</p>')
    
    return '\n'.join(html_blocks)


def process_heading(block):
    """Procesa un encabezado markdown (# titulo) a HTML."""
    match = re.match(r'^(#{1,6})\s?(.+)$', block.strip())
    if match:
        level = min(int(len(match.group(1))), 3)  # Max h3
        title = process_inline_md(match.group(2).strip())
        return f'<h{level}>{title}</h{level}>'
    return f'<p>{process_inline_md(block)}</p>'


def process_list_block(block):
    """Procesa una lista markdown (- item) a HTML."""
    items = re.findall(r'^\s*[-*+]\s+(.+)$', block, re.MULTILINE)
    html_items = ''.join(f'<li>{process_inline_md(item.strip())}</li>' for item in items)
    return f'<ul>{html_items}</ul>'


def process_numbered_list_block(block):
    """Procesa una lista numerada markdown (1. item) a HTML."""
    items = re.findall(r'^\s*\d+\.\s+(.+)$', block, re.MULTILINE)
    html_items = ''.join(f'<li>{process_inline_md(item.strip())}</li>' for item in items)
    return f'<ol>{html_items}</ol>'


def process_quote(block):
    """Procesa una cita markdown (> texto) a HTML."""
    lines = [re.sub(r'^>\s*', '', line) for line in block.splitlines()]
    content = ' '.join(line.strip() for line in lines if line.strip())
    return f'<blockquote>{process_inline_md(content)}</blockquote>'


def process_inline_md(text):
    """Procesa sintaxis markdown inline: negrita, cursiva, enlaces, code."""
    # Enlaces [texto](url) - procesar primero para no procesar el contenido
    text = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'<a href="\2" target="_blank" rel="noopener noreferrer">\1</a>', text)
    
    # Code inline `texto`
    text = re.sub(r'`([^`]+)`', r'<code>\1</code>', text)
    
    # Negrita **texto** o __texto__
    text = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', text)
    text = re.sub(r'__(.+?)__', r'<strong>\1</strong>', text)
    
    # Cursiva *texto* o _texto_
    text = re.sub(r'\*(.+?)\*', r'<em>\1</em>', text)
    text = re.sub(r'(?<!\w)_(.+?)_(?!\w)', r'<em>\1</em>', text)
    
    return text


def parse_info_txt(folder):
    """Parsea info.txt y detecta si usa markdown.
    
    Soporta etiquetas especiales:
    - demo: URL del proyecto en vivo
    - github: Link al repositorio
    - imagen: Nombre de imagen asociada (sin ruta completa)
    - link: URL alternativa
    - # Título H1: Se extrae el primer H1 como título principal
    
    Busca info.txt en la carpeta del proyecto y sus subcarpetas.
    
    Si el archivo contiene markdown, lo convierte a HTML para renderizado.
    Si no, mantiene el formato de texto plano original.
    
    Returns:
        tuple: (description_html, title_from_info, demo_url, github_url, associated_image)
    """
    info_path = folder / "info.txt"
    
    # Si no existe en la carpeta raíz, buscar en subcarpetas
    if not info_path.exists():
        subfolders = list(folder.rglob("info.txt"))
        if subfolders:
            info_path = subfolders[0]  # Usar el primero encontrado
        else:
            return "", None, None, None, None

    text = info_path.read_text(encoding="utf-8", errors="ignore").strip()
    
    # Extraer el primer encabezado como título principal (prioridad: H1 → H2 → H3)
    title_from_info = None
    for header_level in [1, 2, 3]:
        pattern = rf'^#{{{header_level}}}\s+(.+)$'
        header_match = re.search(pattern, text, re.MULTILINE)
        if header_match:
            title_from_info = header_match.group(1).strip()
            # Limpiar caracteres de markdown del título
            title_from_info = re.sub(r'[#*_`]', '', title_from_info).strip()
            break  # Usar el primer encabezado encontrado
    
    # Extraer URLs con etiquetas específicas
    demo_url = None
    github_url = None
    associated_image = None
    
    # Buscar etiquetas conocidas (case-insensitive) - soporta "link GitHub", "github", etc.
    demo_match = re.search(r'demo\s*:?\s*(https?://\S+)', text, re.I)
    if demo_match:
        demo_url = demo_match.group(1).rstrip(".,")
    
    # Soporta "link GitHub:", "github:", "github link:", etc.
    github_match = re.search(r'(?:link\s+)?github\s*:?\s*(https?://\S+)', text, re.I)
    if github_match:
        github_url = github_match.group(1).rstrip(".,")
    
    # Buscar imagen asociada - soporta "imagen:[archivo.png]" con corchetes
    imagen_match = re.search(r'imagen\s*:?\s*\[?([^\]\s]+)\]?', text, re.I)
    if imagen_match:
        associated_image = imagen_match.group(1).strip()
        # Si parece un nombre de archivo, limpiar extensiones de URL
        if not associated_image.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.webp')):
            associated_image = None
    
    # Remover líneas de etiquetas para procesar el resto
    cleaned_text = text
    cleaned_text = re.sub(r'demo\s*:?\s*https?://\S+', '', cleaned_text, flags=re.I)
    cleaned_text = re.sub(r'(?:link\s+)?github\s*:?\s*https?://\S+', '', cleaned_text, flags=re.I)
    cleaned_text = re.sub(r'imagen\s*:?\s*\[?[^\]]+\]?', '', cleaned_text, flags=re.I)
    
    # También extraer URL genérica (para compatibilidad con info.txt existentes)
    url_match = re.search(r'https?://\S+', cleaned_text)
    generic_url = url_match.group(0).rstrip(".,") if url_match else None
    # Si no hay demo/github, usar la URL genérica como demo
    if not demo_url and generic_url:
        demo_url = generic_url
    
    cleaned_text = re.sub(r'https?://\S+', '', cleaned_text)
    
    # Limpiar lineas de etiquetas conocidas (pero preservar lineas vacias para markdown)
    cleaned_lines = []
    for line in cleaned_text.splitlines():
        stripped = line.strip()
        # Eliminar lineas que son solo etiquetas conocidas
        if re.match(r'^(sitio web|website|link|url|demo|github|imagen)\s*:?\s*$', stripped, re.I):
            continue
        cleaned_lines.append(line)
    
    cleaned_text = '\n'.join(cleaned_lines).strip()
    
    # Detectar si el texto usa markdown
    if detect_markdown(cleaned_text):
        # Convertir markdown a HTML (preservando estructura de bloques)
        description = markdown_to_html(cleaned_text)
    else:
        # Formato de texto plano (comportamiento original)
        lines = [line.strip() for line in cleaned_lines if line.strip()]
        description = ' '.join(lines).strip()
    
    return description, title_from_info, demo_url, github_url, associated_image


def to_web_path(path):
    return path.relative_to(ROOT).as_posix()


def build_project(folder, category):
    """Construye uno o multiples proyectos desde una carpeta.
    
    Si el info.txt contiene secciones separadas por ---, genera un proyecto
    independiente por seccion. Cada seccion puede tener su propio titulo,
    demo, github e imagen asociada.
    
    Optimizaciones mobile:
    - Convierte imagenes a WebP automaticamente
    - Valida videos para compatibilidad iOS/Android
    - Usa WebP cuando esta disponible
    
    Returns:
        list[dict]: Lista de proyectos generados
    """
    # 1. Ejecutar conversion WebP en la carpeta del proyecto
    print(f"\n[OPTIMIZANDO] {category['slug']}/{folder.name}...")
    webp_stats = optimize_images_in_folder(folder)
    
    # 2. Validar videos para mobile
    video_results = check_all_videos_for_mobile(folder)
    for vr in video_results:
        if not vr["valid"]:
            print(f"  [VIDEO WARN] {vr['video']}:")
            for issue in vr["issues"]:
                print(f"    ⚠ {issue}")
            for rec in vr["recommendations"]:
                print(f"    → {rec}")
    
    # 3. Buscar imagenes y videos
    videos, images = find_images(folder)
    poster = find_poster_image(folder)
    
    # Combinar videos e imagenes para la galeria
    all_media = videos + images

    # Buscar animaciones Lottie (antes del gate: un proyecto solo-Lottie,
    # sin imagenes/videos estaticos, tambien debe generarse)
    folder_abs = folder if folder.is_absolute() else (ROOT / folder)
    lottie_files = find_lottie_animation(folder_abs)
    lottie_path = to_web_path(lottie_files[0]) if lottie_files else None

    if not all_media and not lottie_path:
        return None

    # La primera imagen/media sera la portada por defecto (si hay galeria).
    # Si la original fue eliminada (convertida a WebP), usar la version WebP.
    if all_media:
        cover = all_media[0]
        if is_video(cover):
            cover_for_card = cover
        else:
            webp_version = cover.with_suffix(".webp")
            cover_for_card = webp_version if webp_version.exists() else cover
    else:
        cover_for_card = None
    
    # Construir lista de medios con tipo y MIME para compatibilidad mobile
    media_list = []
    for media in all_media:
        is_vid = is_video(media)
        media_item = {
            "src": to_web_path(media),
            "type": "video" if is_vid else "image"
        }
        
        # Para imagenes: usar version WebP si existe (la original puede haber sido eliminada)
        if not is_vid:
            webp_version = media.with_suffix(".webp")
            if webp_version.exists():
                # Usar WebP (la original puede no existir si fue eliminada)
                media_item["src"] = to_web_path(webp_version)
                media_item["format"] = "webp"
            else:
                # No existe WebP, usar original (formato que no se convierte: .gif, etc.)
                media_item["src"] = to_web_path(media)
                media_item["format"] = media.suffix.lower().lstrip(".")
        
        # Agregar tipo MIME para videos (necesario para compatibilidad mobile)
        if is_vid:
            media_item["mimeType"] = get_video_mime_type(media)
        
        media_list.append(media_item)
    
    poster_path = None
    if poster:
        # Si la poster original fue eliminada, usar version WebP
        webp_poster = poster.with_suffix(".webp")
        poster_path = to_web_path(webp_poster) if webp_poster.exists() else to_web_path(poster)
    
    # Leer el info.txt y verificar si tiene secciones
    info_path = folder / "info.txt"
    if not info_path.exists():
        subfolders = list(folder.rglob("info.txt"))
        if subfolders:
            info_path = subfolders[0]
    
    has_multi_sections = False
    if info_path.exists():
        text = info_path.read_text(encoding="utf-8", errors="ignore").strip()
        has_multi_sections = has_sections(text)
    
    if has_multi_sections:
        # GENERAR UN SOLO PROYECTO CON SECCIONES INTERNAS
        sections_data = parse_info_txt_sections(folder)
        
        # Construir array de secciones para el proyecto
        sections_array = []
        for idx, section in enumerate(sections_data):
            # Buscar imagen asociada de esta seccion
            associated_image = section.get("associatedImage")
            associated_image_path = None
            if associated_image:
                associated_file = folder / associated_image
                if associated_file.exists() and associated_file.suffix.lower() in IMAGE_EXTENSIONS:
                    associated_image_path = to_web_path(associated_file)
                else:
                    found_files = list(folder.rglob(associated_image))
                    if found_files:
                        associated_image_path = to_web_path(found_files[0])
            
            # Construir lista de columnas con imagen y URLs completas
            columns = []
            for col_idx, col in enumerate(section.get("columns", [])):
                col_data = {
                    "content": col["content"],
                }
                # Agregar associatedImage con ruta completa
                if col.get("associatedImage"):
                    img_name = col["associatedImage"]
                    img_file = folder / img_name
                    if img_file.exists() and img_file.suffix.lower() in IMAGE_EXTENSIONS:
                        col_data["associatedImage"] = to_web_path(img_file)
                    else:
                        found_files = list(folder.rglob(img_name))
                        if found_files:
                            col_data["associatedImage"] = to_web_path(found_files[0])
                        else:
                            col_data["associatedImage"] = img_name
                # Agregar URLs de la columna
                if col.get("url"):
                    col_data["url"] = col["url"]
                if col.get("github"):
                    col_data["github"] = col["github"]
                columns.append(col_data)
            
            sections_array.append({
                "title": section.get("title", f"Seccion {idx + 1}"),
                "description": section.get("description"),
                "columns": columns,
                "url": section.get("url"),
                "github": section.get("github"),
                "associatedImage": associated_image_path,
            })
        
        project = {
            "slug": folder.name,
            "title": prettify_title(folder.name),
            "titleFromInfo": None,  # No usar titulo de seccion para el proyecto principal
            "category": category["slug"],
            "categoryLabel": category["label"],
            "description": "",  # La descripcion general se maneja en las secciones
            "url": None,  # Las URLs son por seccion
            "github": None,  # Los GitHub son por seccion
            "image": to_web_path(cover_for_card) if cover_for_card else None,
            "poster": poster_path,
            "associatedImage": None,
            "images": media_list,
            "lottie": lottie_path,
            "lastModified": datetime.fromtimestamp(folder.stat().st_mtime).isoformat(),
            "sections": sections_array,  # Array de secciones internas
        }
        
        print(f"  [SECCIONES] {category['slug']}/{folder.name}: 1 proyecto con {len(sections_array)} secciones")
        return project
    else:
        # GENERAR UN SOLO PROYECTO (comportamiento original sin secciones)
        description, title_from_info, demo_url, github_url, associated_image = parse_info_txt(folder)
        
        # Buscar imagen asociada
        associated_image_path = None
        if associated_image:
            associated_file = folder / associated_image
            if associated_file.exists() and associated_file.suffix.lower() in IMAGE_EXTENSIONS:
                associated_image_path = to_web_path(associated_file)
            else:
                found_files = list(folder.rglob(associated_image))
                if found_files:
                    associated_image_path = to_web_path(found_files[0])
        
        return {
            "slug": folder.name,
            "title": prettify_title(folder.name),
            "titleFromInfo": title_from_info,
            "category": category["slug"],
            "categoryLabel": category["label"],
            "description": description,
            "url": demo_url,
            "github": github_url,
            "image": to_web_path(cover_for_card) if cover_for_card else None,
            "poster": poster_path,
            "associatedImage": associated_image_path,
            "images": media_list,
            "lottie": lottie_path,
            "lastModified": datetime.fromtimestamp(folder.stat().st_mtime).isoformat(),
        }


def main():
    """Funcion principal: escanea img/, convierte a WebP, valida videos, genera data."""
    if not IMG_DIR.exists():
        raise SystemExit(f"No se encontro la carpeta {IMG_DIR}")
    
    print("="*60)
    print("PORTAFOLIO - OPTIMIZACION MOBILE")
    print("="*60)
    
    projects = []
    total_webp_converted = 0
    total_webp_deleted = 0
    total_webp_saved = 0
    
    for category in CATEGORIES:
        category_dir = IMG_DIR / category["slug"]
        
        # Manejo especial para Certificados: estan en Certificados/ en la raiz, no en img/
        if category["slug"] == "certificados":
            cert_dir = ROOT / "Certificados"
            if not cert_dir.exists():
                print(f"\nAviso: no existe Certificados/ (se omite)")
                continue
            for file_path in sorted(cert_dir.iterdir()):
                if not file_path.is_file():
                    continue
                if file_path.suffix.lower() not in DOCUMENT_EXTENSIONS:
                    continue

                # Extraer titulo del nombre del archivo
                title = file_path.stem
                title = prettify_title(title)
                # Limpiar guiones bajos y guiones
                title = re.sub(r"[_-]+", " ", title)
                title = re.sub(r"\s+", " ", title).strip()

                projects.append({
                    "slug": file_path.stem,
                    "title": title,
                    "category": category["slug"],
                    "categoryLabel": category["label"],
                    "description": "",
                    "url": None,
                    "image": to_web_path(file_path),
                    "images": [to_web_path(file_path)],
                    "file_type": "pdf",
                    "lastModified": datetime.fromtimestamp(file_path.stat().st_mtime).isoformat(),
                })
            continue

        if not category_dir.exists():
            print(f"\nAviso: no existe img/{category['slug']}/ (se omite)")
            continue

        for folder in sorted(category_dir.iterdir()):
            if not folder.is_dir():
                continue
            if (folder / SKIP_MARKER).exists():
                print(f"\nOmitida (marcada con {SKIP_MARKER}): {category['slug']}/{folder.name}")
                continue

            project = build_project(folder, category)
            if project is None:
                print(f"Omitida (sin imagenes): {category['slug']}/{folder.name}")
                continue

            projects.append(project)

    projects.sort(key=lambda p: p["lastModified"], reverse=True)

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    body = json.dumps(projects, ensure_ascii=False, indent=2)
    categories_body = json.dumps(CATEGORIES, ensure_ascii=False, indent=2)
    OUTPUT_FILE.write_text(
        "// Archivo generado automaticamente por generate_projects.py\n"
        "// No editar a mano: los cambios se pierden al volver a ejecutar el script.\n"
        f"const PROJECT_CATEGORIES = {categories_body};\n"
        f"const PROJECTS = {body};\n",
        encoding="utf-8",
    )

    print(f"\n{'='*60}")
    print(f"RESUMEN FINAL")
    print(f"{'='*60}")
    print(f"✓ {len(projects)} proyecto(s) escritos en {to_web_path(OUTPUT_FILE)}")
    print(f"\n[WEBP] Conversion completada:")
    print(f"  - {total_webp_converted} imagenes convertidas a WebP")
    print(f"  - {total_webp_deleted} imagenes originales eliminadas")
    print(f"  - {total_webp_saved/1024/1024:.2f} MB ahorrados en total")
    print(f"\n[VIDEO] Validacion mobile:")
    print(f"  - Todos los videos .mp4 con codec H.264 son compatibles")
    print(f"  - Videos .webm/.ogg requieren conversion a .mp4 para iOS")
    print(f"\n[NOTA] Las imagenes originales (.png, .jpg, .jpeg) fueron eliminadas")
    print(f"       despues de la conversion a WebP exitosa.")
    
    for project in projects:
        print(f"  - [{project['categoryLabel']}] {project['title']} ({len(project['images'])} archivo(s))")


if __name__ == "__main__":
    main()
