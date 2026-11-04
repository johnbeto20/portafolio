"""
Configuracion central del pipeline de build del portafolio.

Fuente unica de verdad para rutas y categorias. Los scripts de
build/generate_projects.py, build/cleanup_duplicates.py y
build/qa/verify_sections.py importan de aqui para no repetir rutas.

Estructura de carpetas del sitio:
    img/
        proyectos/          # Categorias de portafolio (fuente del generador)
            <categoria>/<proyecto>/...
        mentoria/           # Imagenes estaticas de la pagina mentoria.html
        brand/              # Assets del sitio: favicon, og, foto personal
        src/                # Fuentes / originales no publicados
    Certificados/           # PDF/imagenes de certificados (raiz, por URL existente)

Para agregar una categoria: crear la carpeta en img/proyectos/<slug>/
y anadir su entrada a CATEGORIES (abajo).
"""

from pathlib import Path

# Raiz del proyecto (build/config/site_config.py -> 2 niveles arriba)
ROOT = Path(__file__).resolve().parents[2]

# ============================================================
# RUTAS DE FUENTE
# ============================================================

# Carpeta raiz de imagenes del sitio (para barridos completos de limpieza)
SITE_IMAGES_DIR = ROOT / "img"

# Categorias de portafolio: img/proyectos/<categoria>/<proyecto>/
PROJECTS_DIR = ROOT / "img" / "proyectos"

# Assets propios del sitio (favicon, apple-touch-icon, og-default, foto personal)
BRAND_DIR = ROOT / "img" / "brand"

# Imagenes de la pagina mentoria.html (no son proyectos generados)
MENTORIA_DIR = ROOT / "img" / "mentoria"

# Certificados (PDF/PNG/JPG sueltos en la raiz)
CERTIFICADOS_DIR = ROOT / "Certificados"

# ============================================================
# RUTAS DE SALIDA / ESTADO
# ============================================================

# Datos generados que consumen index.html, proyectos.html y proyecto.html
OUTPUT_FILE = ROOT / "js" / "projects-data.js"

# Cache de huella para detectar cambios en las fuentes entre ejecuciones
STATE_FILE = ROOT / "build" / ".generate_projects_state.json"

# ============================================================
# CATEGORIAS DEL PORTAFOLIO
# ============================================================

# El slug debe coincidir con el nombre de la carpeta en img/proyectos/.
# La unica excepcion es "certificados": sus archivos viven en Certificados/.
CATEGORIES = [
    {"slug": "ilustraciones", "label": "Ilustraciones"},
    {"slug": "tomas-aereas", "label": "Tomas Aereas"},
    {"slug": "aplicaciones-y-sitios-web", "label": "Aplicaciones y Sitios Web"},
    {"slug": "sistemas-de-diseno", "label": "Sistemas de Diseño"},
    {"slug": "animaciones", "label": "Animaciones"},
    {"slug": "disenio-grafico", "label": "Diseño Grafico"},
    {"slug": "certificados", "label": "Certificados"},
]

# Categoria que se maneja aparte (archivos sueltos, no carpetas de proyecto)
CERTIFICADOS_CATEGORY_SLUG = "certificados"
