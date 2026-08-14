// ============================================
// JOHN B. — Creative Portfolio
// Proyectos — renderiza filtros y tarjetas desde PROJECTS
// (generado por generate_projects.py). El filtrado en si lo maneja
// initWorkFilters() en main.js (mismos .filter-btn / .work-card[data-category]
// que usa la seccion de trabajos del home).
// ============================================

(function () {
    const fullGrid = document.getElementById('projectsGrid');
    const homeGrid = document.getElementById('workGrid');
    const grid = fullGrid || homeGrid;
    const filters = document.getElementById('projectFilters');
    const HOME_LIMIT = 6;

    if (!grid || typeof PROJECTS === 'undefined') return;

    // Filtrar certificados de proyectos.html (solo aparecen en certificados.html)
    // En el home: ordenar por última modificación (más reciente primero)
    const allProjects = PROJECTS.filter(p => p.category !== 'certificados');
    const sortedProjects = [...allProjects].sort((a, b) => {
        if (a.lastModified && b.lastModified) {
            return new Date(b.lastModified) - new Date(a.lastModified);
        }
        return 0;
    });
    const items = fullGrid 
        ? sortedProjects
        : sortedProjects.slice(0, HOME_LIMIT);

    function renderFilters() {
        if (!filters) return;

        const presentSlugs = new Set(PROJECTS.filter(p => p.category !== 'certificados').map(p => p.category));
        const categories = (typeof PROJECT_CATEGORIES !== 'undefined' ? PROJECT_CATEGORIES : [])
            .filter(cat => presentSlugs.has(cat.slug));

        const buttons = [`<button class="filter-btn active" data-filter="all">TODOS</button>`]
            .concat(categories.map(cat =>
                `<button class="filter-btn" data-filter="${cat.slug}">${cat.label.toUpperCase()}</button>`
            ));

        filters.innerHTML = buttons.join('\n');
    }

    const CARD_DESCRIPTION_LIMIT = 64;

    function truncate(text, limit) {
        if (!text || text.length <= limit) return text;
        return text.slice(0, limit).trim() + '…';
    }

    // Truncar HTML manteniendo etiquetas abiertas
    function truncateHtml(html, limit) {
        if (!html || html.length <= limit) return html;
        
        // Crear un elemento temporal para parsear el HTML
        const temp = document.createElement('div');
        temp.innerHTML = html;
        
        // Obtener el texto plano para truncar
        const text = temp.textContent || temp.innerText;
        if (text.length <= limit) return html;
        
        // Truncar el HTML manteniendo estructura
        let result = '';
        let charCount = 0;
        const regex = /<[^>]+>|[^<]+/g;
        let match;
        
        while ((match = regex.exec(html)) && charCount < limit) {
            const segment = match[0];
            if (segment.startsWith('<')) {
                result += segment;
            } else {
                const remaining = limit - charCount;
                result += segment.substring(0, remaining);
                charCount += remaining;
            }
        }
        
        // Cerrar etiquetas abiertas
        const openTags = result.match(/<([a-z][a-z0-9]*)[^>]*>/gi) || [];
        const closedTags = result.match(/<\/([a-z][a-z0-9]*)>/gi) || [];
        const toClose = openTags.filter(tag => {
            const name = tag.match(/<([a-z][a-z0-9]*)/i)[1];
            return !closedTags.some(ct => ct.includes(name));
        });
        
        // Cerrar en orden inverso
        toClose.reverse().forEach(tag => {
            const name = tag.match(/<([a-z][a-z0-9]*)/i)[1];
            result += `</${name}>`;
        });
        
        return result + '…';
    }

    // Extraer texto plano desde HTML (para previews en tarjetas)
    function stripHtml(html) {
        const temp = document.createElement('div');
        temp.innerHTML = html;
        return temp.textContent || temp.innerText;
    }

    function renderCards() {
        grid.innerHTML = items.map((project, index) => {
            // Soporte para nuevo formato (array con type) y formato antiguo (string)
            const isVideo = project.image && typeof project.image === 'string' && /\.(mp4|webm|ogg)$/i.test(project.image);
            const posterAttr = project.poster ? ` poster="${project.poster}"` : '';
            const media = isVideo
                ? `<video src="${project.image}" muted playsinline preload="metadata"${posterAttr} class="card-media"></video>`
                : `<img src="${project.image}" alt="${project.title}" loading="lazy">`;
            
            // Contenedor para animación Lottie (oculto por defecto)
            const lottieContainer = project.lottie 
                ? `<div class="lottie-container" id="lottie-${project.slug}" style="display: none;"></div>`
                : '';
            
            return `
            <article class="work-card" data-category="${project.category}" data-scroll-reveal data-index="${index}">
                <div class="card-image is-loading" data-open-project="${project.slug}">
                    ${media}
                    ${lottieContainer}
                    <div class="card-overlay">
                        <span class="card-category">${project.categoryLabel.toUpperCase()}</span>
                        <i class="hgi hgi-stroke hgi-rounded hgi-plus-sign-circle bento-icon"></i>
                    </div>
                </div>
                <div class="card-info">
                    <h3 class="card-title">${project.title}</h3>
                    ${project.description ? `<p class="card-description">${truncate(stripHtml(project.description), CARD_DESCRIPTION_LIMIT)}</p>` : ''}
                </div>
            </article>
        `;
        }).join('');

        grid.querySelectorAll('[data-open-project]').forEach(el => {
            el.addEventListener('click', () => {
                window.location.href = `proyecto.html?slug=${encodeURIComponent(el.dataset.openProject)}`;
            });
        });

        // Skeleton shimmer on each card until its media reports load/error —
        // handles the cached-media case too (onload never fires if it's
        // already complete by the time we attach the listener).
        grid.querySelectorAll('.card-image').forEach(wrapper => {
            const media = wrapper.querySelector('video, img');
            function markLoaded() {
                wrapper.classList.remove('is-loading');
                media.classList.add('is-loaded');
            }
            if (media.tagName === 'VIDEO') {
                if (media.readyState >= 1) {
                    markLoaded();
                } else {
                    media.addEventListener('loadeddata', markLoaded, { once: true });
                    media.addEventListener('error', markLoaded, { once: true });
                }
            } else {
                if (media.complete && media.naturalWidth > 0) {
                    markLoaded();
                } else {
                    media.addEventListener('load', markLoaded, { once: true });
                    media.addEventListener('error', markLoaded, { once: true });
                }
            }
        });
        
        // Inicializar animaciones Lottie en las tarjetas
        items.forEach(project => {
            if (project.lottie) {
                const container = document.getElementById(`lottie-${project.slug}`);
                if (container) {
                    const cardImage = container.closest('.card-image');
                    const media = cardImage.querySelector('video, img');
                    
                    // Ocultar imagen/video y mostrar contenedor Lottie
                    if (media) {
                        media.style.display = 'none';
                    }
                    container.style.display = 'block';
                    
                    // Cargar y reproducir animación Lottie
                    try {
                        lottie.loadAnimation({
                            container: container,
                            renderer: 'svg',
                            loop: true,
                            autoplay: true,
                            path: project.lottie
                        });
                    } catch (e) {
                        console.error(`Error loading Lottie animation for ${project.slug}:`, e);
                        // Fallback: mostrar imagen si Lottie falla
                        if (media) {
                            media.style.display = '';
                        }
                        container.style.display = 'none';
                    }
                }
            }
        });
    }

    renderFilters();
    renderCards();
})();
