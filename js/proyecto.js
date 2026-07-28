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

    detail.innerHTML = `
        ${project.description ? `<p class="project-detail-description">${project.description}</p>` : ''}
        ${project.url ? `
            <a class="btn btn-secondary magnetic-btn project-detail-link" href="${project.url}" target="_blank" rel="noopener noreferrer">
                <span class="btn-text">VISITAR SITIO</span>
                <span class="btn-arrow">↗</span>
            </a>
        ` : ''}
        <div class="project-main-image-wrap is-loading" id="projectMainImageWrap">
            <img class="project-detail-main-image" id="projectMainImage" src="${project.images[0]}" alt="${project.title}">
        </div>
        ${project.images.length > 1 ? `
            <div class="project-thumbs" id="projectThumbs">
                ${project.images.map((img, i) => `
                    <div class="project-thumb${i === 0 ? ' active' : ''} is-loading" data-index="${i}">
                        <img src="${img}" alt="${project.title} ${i + 1}" loading="lazy">
                    </div>
                `).join('')}
            </div>
        ` : ''}
    `;

    const mainImageWrap = document.getElementById('projectMainImageWrap');
    const mainImage = document.getElementById('projectMainImage');
    const thumbs = document.getElementById('projectThumbs');

    // Skeleton shimmer stays on each wrapper until its image reports load/error.
    // A helper keeps this uniform whether the wrapper is a static thumb tile or
    // the main image (whose src keeps changing as the user browses the gallery).
    function wireImageLoad(img, wrapper) {
        function markLoaded() {
            wrapper.classList.remove('is-loading');
            img.classList.add('is-loaded');
        }
        if (img.complete && img.naturalWidth > 0) {
            markLoaded();
        } else {
            img.onload = markLoaded;
            img.onerror = markLoaded;
        }
    }

    wireImageLoad(mainImage, mainImageWrap);
    if (thumbs) {
        thumbs.querySelectorAll('.project-thumb').forEach(thumb => {
            wireImageLoad(thumb.querySelector('img'), thumb);
        });
    }

    function selectImage(index) {
        activeIndex = index;
        mainImage.classList.remove('is-loaded');
        mainImageWrap.classList.add('is-loading');
        mainImage.src = project.images[index];
        wireImageLoad(mainImage, mainImageWrap);
        if (thumbs) {
            thumbs.querySelectorAll('.project-thumb').forEach(t => {
                t.classList.toggle('active', Number(t.dataset.index) === index);
            });
        }
    }

    if (thumbs) {
        thumbs.querySelectorAll('.project-thumb').forEach(thumb => {
            thumb.addEventListener('click', () => selectImage(Number(thumb.dataset.index)));
        });
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
                <img class="lightbox-image" src="" alt="">
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
        lightbox.querySelector('.lightbox-image').src = project.images[activeIndex];
        lightbox.querySelector('.lightbox-image').alt = project.title;
        lightbox.querySelector('.lightbox-caption').textContent =
            `${project.title} — ${activeIndex + 1}/${project.images.length}`;

        const showNav = project.images.length > 1;
        lightbox.querySelector('.lightbox-prev').style.display = showNav ? 'flex' : 'none';
        lightbox.querySelector('.lightbox-next').style.display = showNav ? 'flex' : 'none';
    }

    function openLightbox(index) {
        selectImage(index);
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
        selectImage(activeIndex);
        updateLightbox(document.getElementById('projectLightbox'));
    }

    mainImage.addEventListener('click', () => openLightbox(activeIndex));
    if (thumbs) {
        thumbs.querySelectorAll('.project-thumb').forEach(thumb => {
            thumb.addEventListener('dblclick', () => openLightbox(Number(thumb.dataset.index)));
        });
    }
})();
