# build/config

Configuración central del pipeline de renderizado automático del portafolio.
Es la fuente única de verdad para **rutas de carpetas** y **categorías de proyectos**.

| Archivo | Contenido |
| --- | --- |
| `site_config.py` | Rutas (`img/proyectos/`, `Certificados/`, salida `js/projects-data.js`) y lista de `CATEGORIES` |

## Reglas

- **No hardcodear rutas** de `img/...` en los scripts de `build/`: importar de `site_config`.
- **Nueva categoría de portafolio**: crear `img/proyectos/<slug>/` y añadir la entrada a `CATEGORIES`.
- **Categoría especial**: `certificados` no es una carpeta dentro de `img/proyectos/`, usa `Certificados/` en la raíz (las URLs de `certificados.html` dependen de esa ruta).

## Scripts que consumen esta config

| Script | Ruta | Función |
| --- | --- | --- |
| Generador | `build/generate_projects.py` | Escanea `img/proyectos/`, optimiza WebP/video y genera `js/projects-data.js` |
| Limpieza | `build/cleanup_duplicates.py` | Elimina `.png/.jpg` que ya tienen versión `.webp` |
| QA | `build/qa/verify_sections.py` | Verifica secciones en `js/projects-data.js` |
