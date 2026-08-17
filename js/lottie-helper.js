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

    if (typeof lottie === 'undefined') {
        // El <script> del CDN de lottie-web no llegó a cargar (bloqueado por
        // CSP/adblock/red, o el CDN no respondió). Se deja constancia en consola
        // porque de otro modo el mensaje al usuario es indistinguible de un 404 del JSON.
        console.error('Lottie: la librería lottie-web no está disponible (revisa que el <script> del CDN haya cargado).');
        renderLottieFallback(container, 'No se pudo cargar esta animación.');
        if (onFail) onFail();
        return null;
    }

    // Las rutas de proyectos-data.js pueden contener espacios u otros
    // caracteres sin codificar (p. ej. "img/animaciones/Loader propiapp/loader.json").
    // encodeURI evita depender de que el navegador/CDN los normalice por su cuenta.
    const encodedPath = encodeURI(path);

    try {
        const anim = lottie.loadAnimation({
            container,
            renderer: 'svg',
            loop: true,
            autoplay: true,
            path: encodedPath
        });
        anim.addEventListener('data_failed', () => {
            console.error('Lottie: no se pudo obtener/parsear el JSON en', encodedPath);
            renderLottieFallback(container, 'No se pudo cargar esta animación.');
            if (onFail) onFail();
        });
        return anim;
    } catch (e) {
        console.error('Error loading Lottie animation:', encodedPath, e);
        renderLottieFallback(container, 'No se pudo cargar esta animación.');
        if (onFail) onFail();
        return null;
    }
}
