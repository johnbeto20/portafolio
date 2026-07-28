// ============================================
// JOHN B. — Creative Portfolio
// Hero background — animated WebGL gradient shader (canvas), mirroring
// the flowing color-blob look of https://bold-answers-412382.framer.app/.
// Falls back to the blurred CSS gradient blobs (.hero-gradient-fallback)
// if WebGL isn't available or the shader fails to compile.
// ============================================

(function () {
    const canvas = document.getElementById('heroShaderCanvas');
    const heroBg = document.getElementById('heroBg');
    if (!canvas || !heroBg) return;

    const gl = canvas.getContext('webgl') || canvas.getContext('experimental-webgl');
    if (!gl) {
        heroBg.classList.add('no-webgl');
        return;
    }

    const VERTEX_SRC = `
        attribute vec2 a_position;
        void main() {
            gl_Position = vec4(a_position, 0.0, 1.0);
        }
    `;

    // Domain-warped fractal noise: a few octaves of simplex noise fed back
    // into itself so colors flow into each other like paint, instead of
    // looking like flat blurred circles.
    const FRAGMENT_SRC = `
        precision highp float;
        uniform vec2 u_resolution;
        uniform float u_time;
        uniform vec3 u_base;
        uniform vec3 u_blue;
        uniform vec3 u_orange;
        uniform vec3 u_glow;

        vec2 hash(vec2 p) {
            p = vec2(dot(p, vec2(127.1, 311.7)), dot(p, vec2(269.5, 183.3)));
            return -1.0 + 2.0 * fract(sin(p) * 43758.5453123);
        }

        float noise(vec2 p) {
            const float K1 = 0.366025404;
            const float K2 = 0.211324865;
            vec2 i = floor(p + (p.x + p.y) * K1);
            vec2 a = p - i + (i.x + i.y) * K2;
            vec2 o = (a.x > a.y) ? vec2(1.0, 0.0) : vec2(0.0, 1.0);
            vec2 b = a - o + K2;
            vec2 c = a - 1.0 + 2.0 * K2;
            vec3 h = max(0.5 - vec3(dot(a, a), dot(b, b), dot(c, c)), 0.0);
            vec3 n = h * h * h * h * vec3(dot(a, hash(i)), dot(b, hash(i + o)), dot(c, hash(i + 1.0)));
            return dot(n, vec3(70.0));
        }

        float fbm(vec2 p) {
            float f = 0.0;
            float amp = 0.5;
            for (int i = 0; i < 3; i++) {
                f += amp * noise(p);
                p *= 2.0;
                amp *= 0.5;
            }
            return f;
        }

        void main() {
            vec2 uv = gl_FragCoord.xy / u_resolution.xy;
            vec2 p = uv * 1.1;
            float t = u_time * 0.035;

            vec2 q = vec2(fbm(p + t), fbm(p + vec2(5.2, 1.3) + t));
            vec2 r = vec2(
                fbm(p + 2.2 * q + vec2(1.7, 9.2) - t),
                fbm(p + 2.2 * q + vec2(8.3, 2.8) + t)
            );
            float f = fbm(p + 2.2 * r);

            vec3 color = mix(u_base, u_blue, clamp(f * f * 3.0, 0.0, 1.0));
            color = mix(color, u_orange, clamp(length(q) * 0.9, 0.0, 1.0));
            color = mix(color, u_glow, clamp(pow(length(r), 2.0) * 0.6, 0.0, 1.0));

            gl_FragColor = vec4(color, 1.0);
        }
    `;

    function compileShader(type, source) {
        const shader = gl.createShader(type);
        gl.shaderSource(shader, source);
        gl.compileShader(shader);
        if (!gl.getShaderParameter(shader, gl.COMPILE_STATUS)) {
            console.warn('Hero shader compile error:', gl.getShaderInfoLog(shader));
            gl.deleteShader(shader);
            return null;
        }
        return shader;
    }

    const vertexShader = compileShader(gl.VERTEX_SHADER, VERTEX_SRC);
    const fragmentShader = compileShader(gl.FRAGMENT_SHADER, FRAGMENT_SRC);
    if (!vertexShader || !fragmentShader) {
        heroBg.classList.add('no-webgl');
        return;
    }

    const program = gl.createProgram();
    gl.attachShader(program, vertexShader);
    gl.attachShader(program, fragmentShader);
    gl.linkProgram(program);
    if (!gl.getProgramParameter(program, gl.LINK_STATUS)) {
        console.warn('Hero shader link error:', gl.getProgramInfoLog(program));
        heroBg.classList.add('no-webgl');
        return;
    }
    gl.useProgram(program);

    // Single oversized triangle covers the whole viewport without needing
    // a quad + index buffer.
    const positionBuffer = gl.createBuffer();
    gl.bindBuffer(gl.ARRAY_BUFFER, positionBuffer);
    gl.bufferData(gl.ARRAY_BUFFER, new Float32Array([-1, -1, 3, -1, -1, 3]), gl.STATIC_DRAW);

    const positionLoc = gl.getAttribLocation(program, 'a_position');
    gl.enableVertexAttribArray(positionLoc);
    gl.vertexAttribPointer(positionLoc, 2, gl.FLOAT, false, 0, 0);

    const resolutionLoc = gl.getUniformLocation(program, 'u_resolution');
    const timeLoc = gl.getUniformLocation(program, 'u_time');
    const baseLoc = gl.getUniformLocation(program, 'u_base');
    const blueLoc = gl.getUniformLocation(program, 'u_blue');
    const orangeLoc = gl.getUniformLocation(program, 'u_orange');
    const glowLoc = gl.getUniformLocation(program, 'u_glow');

    // Dark mode reads as a nebula on black; light mode swaps to soft pastel
    // clouds on the site's off-white so the shader always matches the
    // active theme instead of forcing the hero to stay dark.
    const PALETTES = {
        dark: {
            base: [0.02, 0.02, 0.03],
            blue: [0.231, 0.510, 0.965],
            orange: [0.976, 0.451, 0.086],
            glow: [0.85, 0.88, 0.95],
        },
        light: {
            base: [0.95, 0.95, 0.96],
            blue: [0.65, 0.78, 0.98],
            orange: [1.0, 0.80, 0.62],
            glow: [1.0, 0.97, 0.92],
        },
    };

    function isLightMode() {
        return document.body.classList.contains('light-mode');
    }

    // Deep-clone: `current` must own its arrays, otherwise lerping it would
    // mutate PALETTES.dark/light in place and corrupt the fixed targets.
    function clonePalette(palette) {
        return {
            base: palette.base.slice(),
            blue: palette.blue.slice(),
            orange: palette.orange.slice(),
            glow: palette.glow.slice(),
        };
    }

    const current = clonePalette(PALETTES[isLightMode() ? 'light' : 'dark']);

    function lerpPalette(target, amount) {
        ['base', 'blue', 'orange', 'glow'].forEach((key) => {
            for (let i = 0; i < 3; i++) {
                current[key][i] += (target[key][i] - current[key][i]) * amount;
            }
        });
    }

    const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

    // The canvas is heavily blurred via CSS, so rendering at full device
    // resolution buys nothing but GPU cost — half-res is indistinguishable
    // once blurred and cuts the fragment shader's per-frame work by ~4x.
    const RENDER_SCALE = 0.5;

    let width = 0;
    let height = 0;
    function resize() {
        const rect = heroBg.getBoundingClientRect();
        const dpr = Math.min(window.devicePixelRatio || 1, 2) * RENDER_SCALE;
        width = Math.max(1, Math.floor(rect.width * dpr));
        height = Math.max(1, Math.floor(rect.height * dpr));
        if (canvas.width !== width || canvas.height !== height) {
            canvas.width = width;
            canvas.height = height;
            gl.viewport(0, 0, width, height);
        }
    }

    // Skip drawing while the hero is scrolled out of view.
    let visible = true;
    const observer = new IntersectionObserver((entries) => {
        entries.forEach((entry) => { visible = entry.isIntersecting; });
    }, { threshold: 0 });
    observer.observe(heroBg);

    let startTime = null;
    function render(timestamp) {
        requestAnimationFrame(render);
        if (!visible) return;
        if (startTime === null) startTime = timestamp;
        resize();

        lerpPalette(PALETTES[isLightMode() ? 'light' : 'dark'], 0.04);
        gl.uniform3f(baseLoc, current.base[0], current.base[1], current.base[2]);
        gl.uniform3f(blueLoc, current.blue[0], current.blue[1], current.blue[2]);
        gl.uniform3f(orangeLoc, current.orange[0], current.orange[1], current.orange[2]);
        gl.uniform3f(glowLoc, current.glow[0], current.glow[1], current.glow[2]);

        gl.uniform2f(resolutionLoc, width, height);
        gl.uniform1f(timeLoc, prefersReducedMotion ? 0 : (timestamp - startTime) / 1000);
        gl.drawArrays(gl.TRIANGLES, 0, 3);
    }

    window.addEventListener('resize', resize, { passive: true });
    resize();
    requestAnimationFrame(render);
})();
