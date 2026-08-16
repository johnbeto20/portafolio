// ============================================
// JOHN B. — Creative Portfolio
// Carga segura de animaciones Lottie: en file:// el
// fetch del .json falla por CORS, así que mostramos un
// aviso dedicado en vez de un recuadro vacío/roto.
// ============================================

function isLocalFile() {
    return window.location.protocol === 'file:';
}

function renderLottieFallback(container, message) {
    container.innerHTML = `
        <div class="lottie-unavailable">
            <i class="hgi hgi-stroke hgi-rounded hgi-video-off"></i>
            <p>${message}</p>
        </div>
    `;
}

// Carga una animación Lottie con manejo de errores.
// Si se abre el sitio como archivo local, muestra el aviso directamente
// (evita el intento de fetch, que siempre falla bajo file://).
// options: { container, path, onFail }
function loadLottieSafe(options) {
    const { container, path, onFail } = options;

    if (isLocalFile()) {
        renderLottieFallback(container, 'No se puede ver este contenido en local. Ábrelo desde un servidor (http/https) para visualizarlo.');
        if (onFail) onFail();
        return null;
    }

    try {
        const anim = lottie.loadAnimation({
            container,
            renderer: 'svg',
            loop: true,
            autoplay: true,
            path
        });
        anim.addEventListener('data_failed', () => {
            renderLottieFallback(container, 'No se pudo cargar esta animación.');
            if (onFail) onFail();
        });
        return anim;
    } catch (e) {
        console.error('Error loading Lottie animation:', e);
        renderLottieFallback(container, 'No se pudo cargar esta animación.');
        if (onFail) onFail();
        return null;
    }
}
