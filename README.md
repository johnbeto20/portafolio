# JOHN B. — Creative Portfolio

Portafolio personal para diseñador web, ilustrador, piloto de drone y audiovisual aereo.

## Estilo & Referencias

El diseño combina elementos de tres sitios de referencia:

- **Decathlon Yestalgia** — Estética retro Y2K, colores vibrantes (violeta, verde, rosa), tipografía bold uppercase, grid de proyectos con hover effects, scroll suave, visual storytelling
- **Tamara Sredojevic** — Layout minimalista, uso de espacio blanco, tipografía limpia, showcase de trabajos tipo cards
- **Triadic Ballet AI** — Estética oscura/artística, hero grande, tipografía bold uppercase, split-screen, footer con logo, ubicación/hora, copyright, socials

## Estructura del Sitio

```
portafolio/
├── index.html          # Home con hero, work grid, featured, services
├── proyectos.html      # Grid de todos los proyectos (con filtros)
├── proyecto.html       # Detalle de proyecto (galeria, video, secciones)
├── certificados.html   # Certificados
├── mentoria.html       # Mentoría
├── about.html          # Quien Soy
├── 404.html            # Página de error
├── css/
│   └── style.css       # Estilos completos
├── js/
│   ├── main.js         # Interacciones y animaciones
│   ├── projects.js     # Filtros y grid de proyectos
│   ├── proyecto.js     # Pagina de detalle
│   ├── projects-data.js # Datos generados (no editar a mano)
│   ├── hero-shader.js  # Hero con shader
│   └── lottie-helper.js # Animaciones Lottie
├── img/                # Assets por categoria (una carpeta por proyecto)
├── Certificados/       # Imagenes de certificados
└── scripts/
    ├── generate_projects.py  # Genera js/projects-data.js desde img/
    ├── cleanup_duplicates.py # Elimina originales cuando existe .webp
    └── verify_sections.py    # Verifica secciones de proyectos generados
```

## Navegación

- **Home** — Página principal con hero animado, marquee, grid de trabajos, proyecto destacado y servicios
- **Proyectos** — Grid de todos los proyectos con filtros por categoria (web, ilustraciones, tomas aereas, microinteracciones, diseno grafico, sistemas de diseno...)
- **Proyecto (detalle)** — Galeria, video, descripcion y enlaces por proyecto
- **Certificados** — Credenciales y reconocimientos
- **Mentoría** — Servicios de mentoría
- **Quien Soy** — Página personal con habilidades y experiencia

## Scripts de mantenimiento

Los scripts viven en `scripts/` y se ejecutan desde la raiz del proyecto:

```bash
python scripts/generate_projects.py   # Regenera js/projects-data.js (convierte a webp y normaliza video)
python scripts/cleanup_duplicates.py  # Elimina .png/.jpg duplicados si ya hay .webp
python scripts/verify_sections.py     # Verifica secciones en los datos generados
```

## Características

- ✅ Custom cursor con efecto magnético
- ✅ Preloader animado
- ✅ Navbar con efecto scroll (blur + transparencia)
- ✅ Hero con parallax y gradientes animados
- ✅ Marquee infinito
- ✅ Grid de proyectos con filtros por categoría
- ✅ Scroll reveal animations
- ✅ Magnetic buttons
- ✅ Hover effects en cards
- ✅ Footer estilo Triadic Ballet AI
- ✅ Links a Instagram (@johnbeto20 y @alzarlavista)
- ✅ Totalmente responsive
- ✅ Tipografía Space Grotesk + Space Mono

## Tecnologías

- HTML5 semántico
- CSS3 con Custom Properties (Variables CSS)
- JavaScript vanilla (ES6+)
- Google Fonts (Space Grotesk, Space Mono)
- Intersection Observer API
- CSS Grid & Flexbox
- CSS Animations & Transitions

## Personalización

### Colores
Modificar las variables CSS en `css/style.css`:

```css
:root {
    --color-accent: #9b5de5;        /* Violeta principal */
    --color-accent-pink: #f15bb5;   /* Rosa */
    --color-accent-green: #00f5d4;  /* Verde */
    --color-accent-orange: #ff6b35; /* Naranja */
}
```

### Imágenes de proyectos
Cada proyecto es una carpeta dentro de `img/<categoria>/<proyecto>/` con sus imágenes y un `info.txt` (URL + descripción). Después ejecutar `python scripts/generate_projects.py` para regenerar `js/projects-data.js`. Reemplazar los `card-image-placeholder` con imágenes reales:

```html
<div class="card-image">
    <img src="ruta/de/la/imagen.jpg" alt="Descripción del proyecto">
    <!-- ... -->
</div>
```

### Contenido
Editar directamente los archivos HTML para agregar/modificar proyectos, textos y enlaces.

## Uso Local

Simplemente abrir `index.html` en un navegador web. No se requiere servidor.

Opcionalmente, usar un servidor local:
```bash
# Python
python -m http.server 8000

# Node.js (npx)
npx serve .

# PHP
php -S localhost:8000
```

## Licencia

Todos los derechos reservados © 2026 John B.
