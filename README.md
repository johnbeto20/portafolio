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
├── web.html            # Sitios Web
├── illustrations.html  # Ilustraciones
├── aerial.html         # Tomas Aereas
├── chargers.html       # Microinteracciones & Loaders
├── about.html          # Quien Soy
├── css/
│   └── style.css       # Estilos completos
├── js/
│   └── main.js         # Interacciones y animaciones
```

## Navegación

- **Home** — Página principal con hero animado, marquee, grid de trabajos, proyecto destacado y servicios
- **Sitios Web** — Portafolio de proyectos web
- **Ilustraciones** — Galería de ilustraciones digitales
- **Tomas Aereas** — Producción audiovisual con drone
- **Microinteracciones** — Loaders, animaciones y motion design
- **Quien Soy** — Página personal con habilidades y experiencia

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
Reemplazar los `card-image-placeholder` con imágenes reales:

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
