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

    document.title = `${project.title} — JOHN B.`;
    document.getElementById('projectCategory').textContent = project.categoryLabel.toUpperCase();
    document.getElementById('projectTitleHeading').textContent = project.title;

    let activeIndex = 0;

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
        if (project.images.length <= 1) {
            // Solo una imagen/video — mostrar como estaba
            const src = project.images[0];
            const isVideo = /\.(mp4|webm|ogg)$/i.test(src);
            const media = isVideo
                ? `<video class="project-detail-main-image" id="projectMainImage" src="${src}" controls preload="metadata"></video>`
                : `<img class="project-detail-main-image" id="projectMainImage" src="${src}" alt="${project.title}">`;
            return `
                ${project.description ? `<p class="project-detail-description">${project.description}</p>` : ''}
                ${project.url ? `
                    <a class="btn btn-secondary magnetic-btn project-detail-link" href="${project.url}" target="_blank" rel="noopener noreferrer">
                        <span class="btn-text">VISITAR SITIO</span>
                        <span class="btn-arrow">↗</span>
                    </a>
                ` : ''}
                <div class="project-bento-single is-loading" id="projectMainImageWrap">
                    ${media}
                </div>
            `;
        }

        // Bento grid con multiples celdas
        const total = project.images.length;
        const bentoCells = project.images.map((src, i) => {
            const isVideo = /\.(mp4|webm|ogg)$/i.test(src);
            const bentoClass = getBentoClass(i, total);
            const icon = isVideo
                ? `<i class="hgi-stroke hgi-play bento-icon"></i>`
                : `<i class="hgi-stroke hgi-image-01 bento-icon"></i>`;
            const media = isVideo
                ? `<video src="${src}" muted playsinline preload="metadata" loading="lazy" data-bento-index="${i}"></video>`
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

        return `
            ${project.description ? `<p class="project-detail-description">${project.description}</p>` : ''}
            ${project.url ? `
                <a class="btn btn-secondary magnetic-btn project-detail-link" href="${project.url}" target="_blank" rel="noopener noreferrer">
                    <span class="btn-text">VISITAR SITIO</span>
                    <span class="btn-arrow">↗</span>
                </a>
            ` : ''}
            <div class="project-bento-grid" id="projectBentoGrid">
                ${bentoCells}
            </div>
        `;
    }

    detail.innerHTML = renderBentoGrid();

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

    // Lightbox for full-size viewing
    function buildLightbox() {
        const lightbox = document.createElement('div');
        lightbox.className = 'project-lightbox';
        lightbox.id = 'projectLightbox';
        lightbox.innerHTML = `
            <div class="lightbox-content">
                <button class="lightbox-close" aria-label="Cerrar">&times;</button>
                <button class="lightbox-nav lightbox-prev" aria-label="Anterior">&#8249;</button>
                <div class="lightbox-media"></div>
                <button class="lightbox-nav lightbox-next" aria-label="Siguiente">&#8250;</button>
                <span class="lightbox-caption"></span>
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
        });

        return lightbox;
    }

    function updateLightbox(lightbox) {
        const mediaContainer = lightbox.querySelector('.lightbox-media');
        const isVideo = project.images[activeIndex] && /\.(mp4|webm|ogg)$/i.test(project.images[activeIndex]);
        if (isVideo) {
            mediaContainer.innerHTML = `<video src="${project.images[activeIndex]}" controls autoplay muted style="max-width:100%;max-height:80vh;"></video>`;
        } else {
            mediaContainer.innerHTML = `<img class="lightbox-image" src="${project.images[activeIndex]}" alt="${project.title}">`;
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
