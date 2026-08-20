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

### 5. Normalización real de video (2026-08-18)
Los videos existentes tenían el codec correcto (H.264) pero fallaban en
iOS/Android por dos causas reales, no solo de extensión:
- `logisfasion-video.mp4` (59.8 MB) no tenía el átomo `moov` al inicio
  (sin "faststart"), por lo que Safari/iOS no podía leer los metadatos
  sin descargar el archivo completo.
- Videos grandes sin compresión adecuada para redes móviles.

Se agregó normalización real vía `ffmpeg` en `generate_projects.py`
(funciones `optimize_videos_in_folder` / `optimize_video_for_mobile`):
- Re-codifica cualquier video (.mp4, .mov, .webm, .ogg, .avi, .mkv) a
  H.264 perfil baseline + AAC + `yuv420p` + `-movflags +faststart`.
- Escala el lado más largo a máx. 1920px preservando orientación
  (portrait/landscape), evitando aplastar videos verticales.
- Marca cada archivo con metadato `comment=mobile_optimized_v1` para
  no re-codificar en corridas futuras si ya está optimizado.
- Requiere `ffmpeg`/`ffprobe` en PATH (si faltan, solo advierte y omite).

Resultado: `logisfasion-video.mp4` bajó de 59.8 MB a 9.7 MB;
`video_splash.mp4` bajó de 818 KB a 462 KB conservando su aspecto
1124:2436 (quedó en 886x1920).

## Formatos Optimizados para Mobile
- **Videos**: .mp4 (H.264 baseline + AAC + faststart) - Universal en iOS/Android
- **Imágenes**: .webp, .jpg, .jpeg - Mejor compresión y soporte
- **Fallback**: .png, .gif

## Videos Detectados y Optimizados
1. `img/animaciones/Splash EPM/video_splash.mp4` → mimeType: video/mp4
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
