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

    const items = fullGrid ? PROJECTS : PROJECTS.slice(0, HOME_LIMIT);

    function renderFilters() {
        if (!filters) return;

        const presentSlugs = new Set(PROJECTS.map(p => p.category));
        const categories = (typeof PROJECT_CATEGORIES !== 'undefined' ? PROJECT_CATEGORIES : [])
            .filter(cat => presentSlugs.has(cat.slug));

        const buttons = [`<button class="filter-btn active" data-filter="all">TODOS</button>`]
            .concat(categories.map(cat =>
                `<button class="filter-btn" data-filter="${cat.slug}">${cat.label.toUpperCase()}</button>`
            ));

        filters.innerHTML = buttons.join('\n');
    }

    function renderCards() {
        grid.innerHTML = items.map((project, index) => {
            const isVideo = project.image && /\.(mp4|webm|ogg)$/i.test(project.image);
            const media = isVideo
                ? `<video src="${project.image}" muted playsinline preload="metadata" class="card-media"></video>`
                : `<img src="${project.image}" alt="${project.title}" loading="lazy">`;
            return `
            <article class="work-card" data-category="${project.category}" data-scroll-reveal data-index="${index}">
                <div class="card-image is-loading" data-open-project="${project.slug}">
                    ${media}
                    <div class="card-overlay">
                        <span class="card-category">${project.categoryLabel.toUpperCase()}</span>
                        <span class="card-arrow">↗</span>
                    </div>
                </div>
                <div class="card-info">
                    <h3 class="card-title">${project.title}</h3>
                    ${project.description ? `<p class="card-description">${project.description}</p>` : ''}
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
    }

    renderFilters();
    renderCards();
})();
