# Optimización Mobile - Imágenes y Videos

## Problema
Imágenes y videos no se veían correctamente en dispositivos móviles.

## Cambios Realizados

### 1. CSS (css/style.css)
- Agregadas reglas `max-width: 100%` y `background: #000` para videos
- Agregadas propiedades `-webkit-backface-visibility: hidden` para renderizado mobile
- Media query `@media (max-width: 768px)` con reglas prioritarias para videos
- Media query `@media (max-width: 640px)` con ajustes para bento cells
- Fix para aspect-ratio en mobile

### 2. JavaScript - proyecto.js (js/proyecto.js)
- Agregado atributo `muted` a todos los videos (requerido por iOS)
- Agregado atributo `controls` a videos del bento grid
- Agregado atributo `type` con MIME correcto para cada video
- Soporte para campo `mimeType` desde projects-data.js
- Fallback a detección por extensión si no hay mimeType

### 3. JavaScript - projects.js (js/projects.js)
- Agregado atributo `type` con MIME para videos en cards
- Soporte para campo `mimeType` desde projects-data.js

### 4. Script Generador (generate_projects.py)
- Nuevas funciones de optimización mobile:
  - `find_optimal_image()`: Prioriza .webp y .jpg sobre .png
  - `find_video_with_poster()`: Ordena videos (mp4 primero)
  - `get_video_mime_type()`: Mapea extensión a MIME
  - `get_optimal_poster_for_video()`: Encuentra mejor poster para video
- `find_images()` actualizado con ordenamiento optimizado:
  - Videos: .mp4 primero (mejor compatibilidad iOS/Android)
  - Imágenes: .webp/.jpg primero, luego .png
- Campos `mimeType` agregados automáticamente en el output

## Formatos Optimizados para Mobile
- **Videos**: .mp4 (H.264) - Universal en iOS/Android
- **Imágenes**: .webp, .jpg, .jpeg - Mejor compresión y soporte
- **Fallback**: .png, .gif

## Videos Detectados y Optimizados
1. `img/animaciones/EPM/video_splash.mp4` → mimeType: video/mp4
2. `img/sistemas-de-diseno/Logisfashion/logisfasion-video.mp4` → mimeType: video/mp4

## Cómo Regenerar
```bash
python generate_projects.py
```

Esto regenera `js/projects-data.js` con:
- Videos ordenados (mp4 primero)
- Imágenes optimizadas (.webp/.jpg primero)
- Campos mimeType automáticos
- Búsqueda inteligente de posters
