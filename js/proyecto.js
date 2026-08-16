// ============================================
// JOHN B. — Creative Portfolio
// Pagina de detalle de proyecto (dinamica) — una sola pagina fisica
// que se alimenta de js/projects-data.js segun el ?slug= de la URL.
// ============================================

(function () {
    const detail = document.getElementById('projectDetail');
    if (!detail || typeof PROJECTS === 'undefined') return;

    const params = new URLSearchParams(window.location.search);
    const slug = params.get('slug');
    const project = PROJECTS.find(p => p.slug === slug);

    if (!project) {
        document.title = 'Proyecto no encontrado — JOHN B.';
        document.getElementById('robotsMeta')?.setAttribute('content', 'noindex, follow');
        document.getElementById('projectCategory').textContent = '';
        document.getElementById('projectTitleHeading').textContent = 'Proyecto no encontrado';
        detail.innerHTML = `
            <p class="card-description">No encontramos el proyecto solicitado. Puede que se haya movido o renombrado.</p>
            <a href="proyectos.html" class="btn btn-primary magnetic-btn" style="margin-top: var(--space-md);">
                <span class="btn-text">VER TODOS LOS PROYECTOS</span>
                <span class="btn-arrow">→</span>
            </a>
        `;
        return;
    }

    function stripTags(html) {
        return (html || '').replace(/<[^>]+>/g, ' ').replace(/\s+/g, ' ').trim();
    }

    function updateMetaTags(project, displayTitle) {
        const plainDescription = (project.description || '')
            .replace(/<[^>]+>/g, ' ')
            .replace(/\s+/g, ' ')
            .trim()
            .slice(0, 155) || `Proyecto de ${project.categoryLabel} — Diseñador Web Profesional`;

        const isVideo = typeof project.image === 'string' && /\.(mp4|webm|ogg)$/i.test(project.image);
        let imagePath = isVideo ? project.poster : project.image;
        if (!imagePath) {
            const firstImage = (project.images || []).find(m => (m.type || 'image') === 'image');
            imagePath = firstImage ? firstImage.src : null;
        }
        const imageUrl = imagePath
            ? new URL(imagePath, window.location.href).href
            : new URL('img/og-default.png', window.location.href).href;
        const canonicalUrl = `${window.location.origin}${window.location.pathname}?slug=${encodeURIComponent(project.slug)}`;
        const pageTitle = `${displayTitle} — JOHN B.`;

        const setContent = (id, value) => {
            const el = document.getElementById(id);
            if (el) el.setAttribute('content', value);
        };

        document.getElementById('metaDescription')?.setAttribute('content', plainDescription);
        document.getElementById('canonicalLink')?.setAttribute('href', canonicalUrl);
        setContent('ogTitle', pageTitle);
        setContent('ogDescription', plainDescription);
        setContent('ogUrl', canonicalUrl);
        setContent('ogImage', imageUrl);
        setContent('twitterTitle', pageTitle);
        setContent('twitterDescription', plainDescription);
        setContent('twitterImage', imageUrl);
    }

    document.title = `${project.title} — JOHN B.`;
    document.getElementById('projectCategory').textContent = project.categoryLabel.toUpperCase();
    // Usar título desde info.txt (H1) si existe, sino usar el título por defecto
    const displayTitle = project.titleFromInfo || project.title;
    document.getElementById('projectTitleHeading').textContent = displayTitle;
    updateMetaTags(project, displayTitle);

    let activeIndex = 0;

    // ============================================
    // RENDERIZAR PROYECTOS CON SECCIONES INTERNAS
    // Layout continuo en 2 columnas con -- para columnas
    // ============================================
    function renderSingleSection(section) {
        return `
            <div class="section-block" data-section-index="0">
                ${renderSectionColumns(section.columns)}
                ${section.associatedImage ? `
                    <div class="project-associated-image">
                        <img src="${section.associatedImage}" alt="${section.title}" loading="lazy">
                    </div>
                ` : ''}
            </div>
        `;
    }

    function renderProjectSections() {
        if (!project.sections || project.sections.length === 0) {
            return null; // No tiene secciones, usar renderBentoGrid()
        }

        // Extraer descripción general y título principal del proyecto
        const firstSection = project.sections[0];
        const projectHeader = (firstSection.description || firstSection.title)
            ? `<div class="project-description-header">
                ${firstSection.title ? `<h2 class="project-section-main-title">${firstSection.title}</h2>` : ''}
                ${firstSection.description ? `<p class="project-description-text">${firstSection.description}</p>` : ''}
               </div>` : '';

        // Crear todas las columnas directamente en el project-sections-grid
        // Sin grids intermedios para que ocupen el 100% del ancho
        const allColumns = project.sections.flatMap(section => section.columns);
        
        const sectionsGrid = allColumns.length > 0
            ? allColumns.map((col, index) => `
                <div class="section-column">
                    ${col.associatedImage ? `<div class="column-image"><img src="${col.associatedImage}" alt="${stripTags(col.content) || project.title}" loading="lazy"></div>` : ''}
                    ${col.content}
                    ${col.url || col.github ? `
                        <div class="project-detail-links">
                            ${col.url ? `<a class="btn btn-secondary magnetic-btn project-detail-link" href="${col.url}" target="_blank" rel="noopener noreferrer"><span class="btn-text">VISITAR SITIO</span><span class="btn-arrow">↗</span></a>` : ''}
                            ${col.github ? `<a class="btn btn-secondary magnetic-btn project-detail-link" href="${col.github}" target="_blank" rel="noopener noreferrer"><span class="btn-text">VER EN GITHUB</span><i class="hgi hgi-stroke hgi-github-circle" style="margin-left: 0.5rem;"></i></a>` : ''}
                        </div>
                    ` : ''}
                </div>
            `).join('')
            : '';

        return `
            ${projectHeader}
            <div class="project-sections-grid">
                ${sectionsGrid}
            </div>
        `;
    }

    function renderSectionColumns(columns) {
        if (!columns || columns.length === 0) return '';
        
        // Siempre mostrar en grid de 2 columnas
        const colsHtml = columns.map(col => `
            <div class="section-column">
                ${col.associatedImage ? `<div class="column-image"><img src="${col.associatedImage}" alt="${stripTags(col.content) || project.title}" loading="lazy"></div>` : ''}
                ${col.content}
                ${col.url || col.github ? `
                    <div class="project-detail-links">
                        ${col.url ? `<a class="btn btn-secondary magnetic-btn project-detail-link" href="${col.url}" target="_blank" rel="noopener noreferrer"><span class="btn-text">VISITAR SITIO</span><span class="btn-arrow">↗</span></a>` : ''}
                        ${col.github ? `<a class="btn btn-secondary magnetic-btn project-detail-link" href="${col.github}" target="_blank" rel="noopener noreferrer"><span class="btn-text">VER EN GITHUB</span><i class="hgi hgi-stroke hgi-github-circle" style="margin-left: 0.5rem;"></i></a>` : ''}
                    </div>
                ` : ''}
            </div>
        `).join('');
        return `<div class="columns-grid">${colsHtml}</div>`;
    }

    function renderSectionLinks(url, github) {
        if (!url && !github) return '';
        
        let linksHtml = '<div class="project-detail-links">';
        if (url) {
            linksHtml += `
                <a class="btn btn-secondary magnetic-btn project-detail-link" href="${url}" target="_blank" rel="noopener noreferrer">
                    <span class="btn-text">VISITAR SITIO</span>
                    <span class="btn-arrow">↗</span>
                </a>
            `;
        }
        if (github) {
            linksHtml += `
                <a class="btn btn-secondary magnetic-btn project-detail-link" href="${github}" target="_blank" rel="noopener noreferrer">
                    <span class="btn-text">VER EN GITHUB</span>
                    <i class="hgi hgi-stroke hgi-github-circle" style="margin-left: 0.5rem;"></i>
                </a>
            `;
        }
        linksHtml += '</div>';
        return linksHtml;
    }

    // Distribución bento: alternar celdas para variedad visual sin forzar spans
    function getBentoClass(index, total) {
        if (total <= 3) return '';
        // Patrón bento: grande, ancho, alto, normales
        const patterns = [
            'bento-large',       // primera: grande
            'bento-wide',        // segunda: ancha
            'bento-tall',        // tercera: alta
            '',                  // resto: normal
            'bento-wide',
            'bento-tall',
            '',
            '',
            'bento-wide',
        ];
        return patterns[index % patterns.length];
    }

    function renderBentoGrid() {
        if (project.images.length === 0) {
            // Proyecto solo-Lottie: sin galeria de imagenes/videos
            const lottieContainer = project.lottie
                ? `<div class="lottie-container" id="lottie-detail" style="display: block;"></div>`
                : '';
            const associatedImageHtml = project.associatedImage
                ? `<div class="project-associated-image"><img src="${project.associatedImage}" alt="Imagen asociada a ${project.title}" loading="lazy"></div>`
                : '';
            return `
                ${project.description ? `<div class="project-detail-description">${project.description}</div>` : ''}
                <div class="project-detail-links">
                    ${project.url ? `
                        <a class="btn btn-secondary magnetic-btn project-detail-link" href="${project.url}" target="_blank" rel="noopener noreferrer">
                            <span class="btn-text">VISITAR SITIO</span>
                            <span class="btn-arrow">↗</span>
                        </a>
                    ` : ''}
                    ${project.github ? `
                        <a class="btn btn-secondary magnetic-btn project-detail-link" href="${project.github}" target="_blank" rel="noopener noreferrer">
                            <span class="btn-text">VER EN GITHUB</span>
                            <i class="hgi hgi-stroke hgi-github-circle" style="margin-left: 0.5rem;"></i>
                        </a>
                    ` : ''}
                </div>
                ${associatedImageHtml}
                <div class="project-bento-single" id="projectMainImageWrap">
                    ${lottieContainer}
                </div>
            `;
        }
        if (project.images.length <= 1) {
            // Solo una imagen/video — mostrar como estaba
            const mediaItem = project.images[0];
            const src = typeof mediaItem === 'string' ? mediaItem : mediaItem.src;
            const isVideo = typeof mediaItem === 'string' 
                ? /\.(mp4|webm|ogg)$/i.test(src)
                : mediaItem.type === 'video';
            // Usar mimeType del data si disponible, sinon detectar por extension
            const mimeType = (typeof mediaItem === 'object' && mediaItem.mimeType)
                ? mediaItem.mimeType
                : {'.mp4': 'video/mp4', '.webm': 'video/webm', '.ogg': 'video/ogg'}[src.toLowerCase().split('.').pop()] || '';
            const typeAttr = mimeType ? ` type="${mimeType}"` : '';
            const posterAttr = project.poster ? ` poster="${project.poster}"` : '';
            const media = isVideo
                ? `<video class="project-detail-main-image" id="projectMainImage" src="${src}" controls muted playsinline preload="metadata"${typeAttr}${posterAttr}></video>`
                : `<img class="project-detail-main-image" id="projectMainImage" src="${src}" alt="${project.title}">`;
            
            // Contenedor Lottie para vista individual
            const lottieContainer = project.lottie 
                ? `<div class="lottie-container" id="lottie-detail" style="display: none;"></div>`
                : '';
            
            // Imagen asociada si existe
            const associatedImageHtml = project.associatedImage 
                ? `<div class="project-associated-image"><img src="${project.associatedImage}" alt="Imagen asociada a ${project.title}" loading="lazy"></div>`
                : '';
            
            return `
                ${project.description ? `<div class="project-detail-description">${project.description}</div>` : ''}
                <div class="project-detail-links">
                    ${project.url ? `
                        <a class="btn btn-secondary magnetic-btn project-detail-link" href="${project.url}" target="_blank" rel="noopener noreferrer">
                            <span class="btn-text">VISITAR SITIO</span>
                            <span class="btn-arrow">↗</span>
                        </a>
                    ` : ''}
                    ${project.github ? `
                        <a class="btn btn-secondary magnetic-btn project-detail-link" href="${project.github}" target="_blank" rel="noopener noreferrer">
                            <span class="btn-text">VER EN GITHUB</span>
                            <i class="hgi hgi-stroke hgi-github-circle" style="margin-left: 0.5rem;"></i>
                        </a>
                    ` : ''}
                </div>
                ${associatedImageHtml}
                <div class="project-bento-single is-loading" id="projectMainImageWrap">
                    ${media}
                    ${lottieContainer}
                </div>
            `;
        }

        // Bento grid con multiples celdas
        const total = project.images.length;
        const bentoCells = project.images.map((mediaItem, i) => {
            const src = typeof mediaItem === 'string' ? mediaItem : mediaItem.src;
            const isVideo = typeof mediaItem === 'string' 
                ? /\.(mp4|webm|ogg)$/i.test(src)
                : mediaItem.type === 'video';
            // Usar mimeType del data si disponible, sinon detectar por extension
            const mimeType = (typeof mediaItem === 'object' && mediaItem.mimeType)
                ? mediaItem.mimeType
                : {'.mp4': 'video/mp4', '.webm': 'video/webm', '.ogg': 'video/ogg'}[src.toLowerCase().split('.').pop()] || '';
            const typeAttr = mimeType ? ` type="${mimeType}"` : '';
            const posterAttr = (isVideo && project.poster) ? ` poster="${project.poster}"` : '';
            const bentoClass = getBentoClass(i, total);
            const icon = isVideo
                ? `<i class="hgi-stroke hgi-play bento-icon"></i>`
                : `<i class="hgi-stroke hgi-image-01 bento-icon"></i>`;
            const media = isVideo
                ? `<video src="${src}" muted playsinline controls preload="metadata"${typeAttr}${posterAttr} data-bento-index="${i}"></video>`
                : `<img src="${src}" alt="${project.title} ${i + 1}" loading="lazy" data-bento-index="${i}">`;
            return `
                <div class="bento-cell${bentoClass ? ' ' + bentoClass : ''}${i === 0 ? ' active' : ''}" 
                     data-index="${i}"
                     title="${isVideo ? 'Ver video' : 'Ver imagen'}">
                    ${media}
                    <div class="bento-overlay">
                        ${icon}
                    </div>
                </div>
            `;
        }).join('');

        // Contenedor Lottie para vista bento grid
        const lottieContainer = project.lottie 
            ? `<div class="lottie-container" id="lottie-detail" style="display: none;"></div>`
            : '';

        // Imagen asociada si existe
        const associatedImageHtml = project.associatedImage 
            ? `<div class="project-associated-image"><img src="${project.associatedImage}" alt="Imagen asociada a ${project.title}" loading="lazy"></div>`
            : '';

        return `
            ${project.description ? `<div class="project-detail-description">${project.description}</div>` : ''}
            <div class="project-detail-links">
                ${project.url ? `
                    <a class="btn btn-secondary magnetic-btn project-detail-link" href="${project.url}" target="_blank" rel="noopener noreferrer">
                        <span class="btn-text">VISITAR SITIO</span>
                        <span class="btn-arrow">↗</span>
                    </a>
                ` : ''}
                ${project.github ? `
                    <a class="btn btn-secondary magnetic-btn project-detail-link" href="${project.github}" target="_blank" rel="noopener noreferrer">
                        <span class="btn-text">VER EN GITHUB</span>
                        <i class="hgi hgi-stroke hgi-github-circle" style="margin-left: 0.5rem;"></i>
                    </a>
                ` : ''}
            </div>
            ${associatedImageHtml}
            <div class="project-bento-grid" id="projectBentoGrid">
                ${bentoCells}
            </div>
            ${lottieContainer}
        `;
    }

    // Intentar renderizar secciones primero, si no tiene, usar bento grid
    const sectionsHtml = renderProjectSections();
    if (sectionsHtml) {
        detail.innerHTML = sectionsHtml;
    } else {
        detail.innerHTML = renderBentoGrid();
    }

    const bentoGrid = document.getElementById('projectBentoGrid');
    const singleWrap = document.getElementById('projectMainImageWrap');
    const mainImage = document.getElementById('projectMainImage');

    // Wire load events for bento cells
    function wireMediaLoad(media, wrapper) {
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
    }

    if (bentoGrid) {
        bentoGrid.querySelectorAll('.bento-cell').forEach(cell => {
            const media = cell.querySelector('video, img');
            wireMediaLoad(media, cell);
            cell.addEventListener('click', () => {
                activeIndex = Number(cell.dataset.index);
                openLightbox(activeIndex);
            });
        });
    }

    // Single image/video mode
    if (singleWrap && mainImage) {
        wireMediaLoad(mainImage, singleWrap);
        mainImage.addEventListener('click', () => openLightbox(0));
    }
    
    // Initialize Lottie animation in detail view
    if (project.lottie) {
        const lottieDetail = document.getElementById('lottie-detail');
        // Solo se oculta la imagen principal en modo "single" (una sola imagen
        // sustituida por la animación). En bento grid (varias imágenes) todas
        // se mantienen visibles junto a la animación.
        const mainMedia = mainImage;

        if (lottieDetail) {
            // Hide main media and show Lottie animation (o el aviso correspondiente)
            if (mainMedia) {
                mainMedia.style.display = 'none';
            }
            lottieDetail.style.display = 'block';

            loadLottieSafe({
                container: lottieDetail,
                path: project.lottie
            });
        }
    }

    // Lightbox for full-size viewing with zoom support
    let lightboxZoom = {
        scale: 1,
        panX: 0,
        panY: 0,
        isPanning: false,
        startX: 0,
        startY: 0,
        lastTouchDistance: 0,
    };

    function buildLightbox() {
        const lightbox = document.createElement('div');
        lightbox.className = 'project-lightbox';
        lightbox.id = 'projectLightbox';
        lightbox.innerHTML = `
            <div class="lightbox-content">
                <button class="lightbox-close" aria-label="Cerrar">&times;</button>
                <button class="lightbox-nav lightbox-prev" aria-label="Anterior">&#8249;</button>
                <div class="lightbox-media-wrapper">
                    <div class="lightbox-media"></div>
                </div>
                <button class="lightbox-nav lightbox-next" aria-label="Siguiente">&#8250;</button>
                <span class="lightbox-caption"></span>
                
                <!-- Zoom controls: only + and - -->
                <div class="lightbox-zoom-controls">
                    <button class="lightbox-zoom-btn lightbox-zoom-in" aria-label="Acercar">+</button>
                    <button class="lightbox-zoom-btn lightbox-zoom-out" aria-label="Alejar">-</button>
                </div>
            </div>
        `;
        document.body.appendChild(lightbox);

        lightbox.querySelector('.lightbox-close').addEventListener('click', closeLightbox);
        lightbox.querySelector('.lightbox-prev').addEventListener('click', () => stepLightbox(-1));
        lightbox.querySelector('.lightbox-next').addEventListener('click', () => stepLightbox(1));
        lightbox.addEventListener('click', (e) => {
            if (e.target === lightbox) closeLightbox();
        });

        document.addEventListener('keydown', (e) => {
            if (!lightbox.classList.contains('active')) return;
            if (e.key === 'Escape') closeLightbox();
            if (e.key === 'ArrowLeft') stepLightbox(-1);
            if (e.key === 'ArrowRight') stepLightbox(1);
            if (e.key === '+' || e.key === '=') zoomLightbox(1.2);
            if (e.key === '-') zoomLightbox(0.8);
            if (e.key === '0') resetLightboxZoom();
        });

        // Zoom: doble clic para alternar zoom
        const mediaWrapper = lightbox.querySelector('.lightbox-media-wrapper');
        mediaWrapper.addEventListener('dblclick', (e) => {
            e.preventDefault();
            if (lightboxZoom.scale > 1) {
                resetLightboxZoom();
            } else {
                zoomLightbox(2);
            }
        });

        // Scroll wheel para zoom
        mediaWrapper.addEventListener('wheel', (e) => {
            if (!lightbox.classList.contains('active')) return;
            e.preventDefault();
            const delta = e.deltaY < 0 ? 1.1 : 0.9;
            zoomLightbox(delta, e);
        }, { passive: false });

        // Pan/drag cuando hay zoom (mouse)
        let isDragging = false;
        let dragStart = { x: 0, y: 0 };

        mediaWrapper.addEventListener('mousedown', (e) => {
            if (lightboxZoom.scale <= 1) return;
            isDragging = true;
            dragStart = { x: e.clientX - lightboxZoom.panX, y: e.clientY - lightboxZoom.panY };
            mediaWrapper.style.cursor = 'grabbing';
            e.preventDefault();
        });

        document.addEventListener('mousemove', (e) => {
            if (!isDragging) return;
            lightboxZoom.panX = e.clientX - dragStart.x;
            lightboxZoom.panY = e.clientY - dragStart.y;
            applyLightboxTransform();
        });

        document.addEventListener('mouseup', () => {
            if (isDragging) {
                isDragging = false;
                mediaWrapper.style.cursor = lightboxZoom.scale > 1 ? 'grab' : 'default';
            }
        });

        // Pinch-to-zoom para móviles
        mediaWrapper.addEventListener('touchstart', (e) => {
            if (e.touches.length === 2) {
                lightboxZoom.lastTouchDistance = getTouchDistance(e);
            } else if (e.touches.length === 1 && lightboxZoom.scale > 1) {
                // Pan con un dedo cuando hay zoom
                lightboxZoom.lastTouchPos = { x: e.touches[0].clientX, y: e.touches[0].clientY };
            }
        }, { passive: true });

        mediaWrapper.addEventListener('touchmove', (e) => {
            if (e.touches.length === 2) {
                e.preventDefault();
                const distance = getTouchDistance(e);
                if (lightboxZoom.lastTouchDistance > 0) {
                    const scale = distance / lightboxZoom.lastTouchDistance;
                    zoomLightbox(scale);
                }
                lightboxZoom.lastTouchDistance = distance;
            } else if (e.touches.length === 1 && lightboxZoom.scale > 1 && lightboxZoom.lastTouchPos) {
                // Pan con un dedo
                const dx = e.touches[0].clientX - lightboxZoom.lastTouchPos.x;
                const dy = e.touches[0].clientY - lightboxZoom.lastTouchPos.y;
                lightboxZoom.panX += dx;
                lightboxZoom.panY += dy;
                applyLightboxTransform();
                lightboxZoom.lastTouchPos = { x: e.touches[0].clientX, y: e.touches[0].clientY };
            }
        }, { passive: false });

        mediaWrapper.addEventListener('touchend', (e) => {
            if (e.touches.length < 2) {
                lightboxZoom.lastTouchDistance = 0;
            }
            if (e.touches.length === 0) {
                lightboxZoom.lastTouchPos = null;
            }
        });

        // Botones de zoom
        lightbox.querySelector('.lightbox-zoom-in').addEventListener('click', (e) => {
            e.stopPropagation();
            zoomLightbox(1.25);
        });
        lightbox.querySelector('.lightbox-zoom-out').addEventListener('click', (e) => {
            e.stopPropagation();
            zoomLightbox(0.8);
        });

        return lightbox;
    }

    function getTouchDistance(e) {
        const t1 = e.touches[0];
        const t2 = e.touches[1];
        const dx = t1.clientX - t2.clientX;
        const dy = t1.clientY - t2.clientY;
        return Math.sqrt(dx * dx + dy * dy);
    }

    function zoomLightbox(factor, event) {
        const newScale = Math.min(Math.max(lightboxZoom.scale * factor, 1), 5);
        
        if (newScale === 1) {
            resetLightboxZoom();
            return;
        }

        lightboxZoom.scale = newScale;
        applyLightboxTransform();
    }

    function resetLightboxZoom() {
        lightboxZoom.scale = 1;
        lightboxZoom.panX = 0;
        lightboxZoom.panY = 0;
        applyLightboxTransform();
    }

    function applyLightboxTransform() {
        const media = document.querySelector('.lightbox-media');
        if (!media) return;
        
        const image = media.querySelector('img, video');
        if (!image) return;

        // Solo aplicar transform si hay zoom o pan activo
        if (lightboxZoom.scale > 1 || lightboxZoom.panX !== 0 || lightboxZoom.panY !== 0) {
            image.style.transform = `scale(${lightboxZoom.scale}) translate(${lightboxZoom.panX}px, ${lightboxZoom.panY}px)`;
            image.style.transition = 'transform 0.2s ease';
            image.style.cursor = lightboxZoom.scale > 1 ? 'grab' : 'default';
            image.style.maxWidth = 'none';
            image.style.maxHeight = 'none';
        } else {
            // Reset completo: eliminar TODOS los estilos inline para volver al estado original
            image.style.transform = '';
            image.style.transition = '';
            image.style.cursor = '';
            image.style.maxWidth = '';
            image.style.maxHeight = '';
        }
    }

    function updateLightbox(lightbox) {
        resetLightboxZoom();
        const mediaContainer = lightbox.querySelector('.lightbox-media');
        
        // Si el proyecto tiene animación Lottie, mostrarla en el lightbox
        // (o el aviso dedicado si no se puede cargar, ej. abierto en local)
        if (project.lottie) {
            mediaContainer.innerHTML = `<div class="lightbox-lottie-container"></div>`;
            const lottieDiv = mediaContainer.querySelector('.lightbox-lottie-container');
            loadLottieSafe({
                container: lottieDiv,
                path: project.lottie
            });
            return;
        }
        
        // Mostrar imagen normal (fallback o si no hay lottie)
        const mediaItem = project.images[activeIndex];
        const src = typeof mediaItem === 'string' ? mediaItem : mediaItem.src;
        const isVideo = typeof mediaItem === 'string' 
            ? /\.(mp4|webm|ogg)$/i.test(src)
            : mediaItem.type === 'video';
        // Usar mimeType del data si disponible, sinon detectar por extension
        const mimeType = (typeof mediaItem === 'object' && mediaItem.mimeType)
            ? mediaItem.mimeType
            : {'.mp4': 'video/mp4', '.webm': 'video/webm', '.ogg': 'video/ogg'}[src.toLowerCase().split('.').pop()] || '';
        const typeAttr = mimeType ? ` type="${mimeType}"` : '';
        const posterAttr = project.poster ? ` poster="${project.poster}"` : '';
        if (isVideo) {
            mediaContainer.innerHTML = `<video src="${src}" controls autoplay muted playsinline style="max-width:100%;max-height:80vh;"${typeAttr}${posterAttr}></video>`;
        } else {
            mediaContainer.innerHTML = `<img class="lightbox-image" src="${src}" alt="${project.title}">`;
        }
        
        lightbox.querySelector('.lightbox-caption').textContent =
            `${project.title} — ${activeIndex + 1}/${project.images.length}`;

        const showNav = project.images.length > 1;
        lightbox.querySelector('.lightbox-prev').style.display = showNav ? 'flex' : 'none';
        lightbox.querySelector('.lightbox-next').style.display = showNav ? 'flex' : 'none';
    }

    function openLightbox(index) {
        activeIndex = index;
        const lightbox = document.getElementById('projectLightbox') || buildLightbox();
        updateLightbox(lightbox);
        lightbox.classList.add('active');
    }

    function closeLightbox() {
        const lightbox = document.getElementById('projectLightbox');
        if (lightbox) lightbox.classList.remove('active');
    }

    function stepLightbox(direction) {
        activeIndex = (activeIndex + direction + project.images.length) % project.images.length;
        updateLightbox(document.getElementById('projectLightbox'));
    }
})();
