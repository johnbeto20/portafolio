#!/usr/bin/env python3
"""
Escanea la carpeta img/ y genera js/projects-data.js con la lista de
proyectos para proyectos.html y proyecto.html.

Uso:
    python generate_projects.py

Estructura esperada:
    img/<categoria>/<proyecto>/...imagenes...

Las categorias validas son las definidas en CATEGORIES mas abajo. Cada
subcarpeta de una categoria se trata como un proyecto:
  - Titulo: se deriva del nombre de la carpeta del proyecto.
  - Imagen destacada: la primera imagen (orden alfabetico) encontrada al
    recorrer la carpeta del proyecto recursivamente.
  - Galeria: todas las imagenes encontradas en la carpeta del proyecto
    (se usan en la pagina de detalle proyecto.html).
  - Descripcion / enlace: se leen de un archivo info.txt dentro de la
    carpeta del proyecto, si existe (se busca una URL y el resto se usa
    como descripcion).

Para excluir una carpeta de proyecto, agrega dentro de ella un archivo
vacio llamado ".skip".

Para agregar una nueva categoria, crea la carpeta img/<slug-categoria>/
y agregala a la lista CATEGORIES.
"""

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent
IMG_DIR = ROOT / "img"
OUTPUT_FILE = ROOT / "js" / "projects-data.js"

CATEGORIES = [
    {"slug": "ilustraciones", "label": "Ilustraciones"},
    {"slug": "tomas-aereas", "label": "Tomas Aereas"},
    {"slug": "aplicaciones-y-sitios-web", "label": "Aplicaciones y Sitios Web"},
    {"slug": "sistemas-de-diseno", "label": "Sistemas de Diseño"},
    {"slug": "animaciones", "label": "Animaciones"},
    {"slug": "disenio-grafico", "label": "Diseño Grafico"},
    {"slug": "certificados", "label": "Certificados"},
]

IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".webp", ".mp4"}
DOCUMENT_EXTENSIONS = {".pdf", ".png", ".jpg", ".jpeg"}
SKIP_MARKER = ".skip"


def prettify_title(folder_name):
    name = re.sub(r"(?<=[a-z0-9])(?=[A-Z])", " ", folder_name)
    name = re.sub(r"[_-]+", " ", name)
    name = re.sub(r"\s+", " ", name).strip()
    words = [w if (w.isupper() and len(w) > 1) else w.capitalize() for w in name.split(" ")]
    return " ".join(words)


def find_images(folder):
    images = []
    for path in folder.rglob("*"):
        if path.is_file() and path.suffix.lower() in IMAGE_EXTENSIONS:
            images.append(path)
    images.sort(key=lambda p: str(p.relative_to(folder)).lower())
    return images


def parse_info_txt(folder):
    info_path = folder / "info.txt"
    if not info_path.exists():
        return "", None

    text = info_path.read_text(encoding="utf-8", errors="ignore").strip()
    url_match = re.search(r"https?://\S+", text)
    url = url_match.group(0).rstrip(".,") if url_match else None

    remainder = text.replace(url, "") if url else text
    lines = [line.strip() for line in remainder.splitlines() if line.strip()]
    lines = [line for line in lines if not re.match(r"^(sitio web|website|link|url)\s*:?\s*$", line, re.I)]
    description = " ".join(lines).strip()
    return description, url


def to_web_path(path):
    return path.relative_to(ROOT).as_posix()


def build_project(folder, category):
    images = find_images(folder)
    if not images:
        return None

    description, url = parse_info_txt(folder)

    return {
        "slug": folder.name,
        "title": prettify_title(folder.name),
        "category": category["slug"],
        "categoryLabel": category["label"],
        "description": description,
        "url": url,
        "image": to_web_path(images[0]),
        "images": [to_web_path(img) for img in images],
        "mtime": folder.stat().st_mtime,
    }


def main():
    if not IMG_DIR.exists():
        raise SystemExit(f"No se encontro la carpeta {IMG_DIR}")

    projects = []
    for category in CATEGORIES:
        category_dir = IMG_DIR / category["slug"]
        
        # Manejo especial para Certificados: estan en Certificados/ en la raiz, no en img/
        if category["slug"] == "certificados":
            cert_dir = ROOT / "Certificados"
            if not cert_dir.exists():
                print(f"Aviso: no existe Certificados/ (se omite)")
                continue
            for file_path in sorted(cert_dir.iterdir()):
                if not file_path.is_file():
                    continue
                if file_path.suffix.lower() not in DOCUMENT_EXTENSIONS:
                    continue

                # Extraer titulo del nombre del archivo
                title = file_path.stem
                title = prettify_title(title)
                # Limpiar guiones bajos y guiones
                title = re.sub(r"[_-]+", " ", title)
                title = re.sub(r"\s+", " ", title).strip()

                projects.append({
                    "slug": file_path.stem,
                    "title": title,
                    "category": category["slug"],
                    "categoryLabel": category["label"],
                    "description": "",
                    "url": None,
                    "image": to_web_path(file_path),
                    "images": [to_web_path(file_path)],
                    "file_type": "pdf",
                    "mtime": file_path.stat().st_mtime,
                })
            continue

        if not category_dir.exists():
            print(f"Aviso: no existe img/{category['slug']}/ (se omite)")
            continue

        for folder in sorted(category_dir.iterdir()):
            if not folder.is_dir():
                continue
            if (folder / SKIP_MARKER).exists():
                print(f"Omitida (marcada con {SKIP_MARKER}): {category['slug']}/{folder.name}")
                continue

            project = build_project(folder, category)
            if project is None:
                print(f"Omitida (sin imagenes): {category['slug']}/{folder.name}")
                continue

            projects.append(project)

    projects.sort(key=lambda p: p["mtime"], reverse=True)
    for project in projects:
        del project["mtime"]

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    body = json.dumps(projects, ensure_ascii=False, indent=2)
    categories_body = json.dumps(CATEGORIES, ensure_ascii=False, indent=2)
    OUTPUT_FILE.write_text(
        "// Archivo generado automaticamente por generate_projects.py\n"
        "// No editar a mano: los cambios se pierden al volver a ejecutar el script.\n"
        f"const PROJECT_CATEGORIES = {categories_body};\n"
        f"const PROJECTS = {body};\n",
        encoding="utf-8",
    )

    print(f"\n{len(projects)} proyecto(s) escritos en {to_web_path(OUTPUT_FILE)}")
    for project in projects:
        print(f"  - [{project['categoryLabel']}] {project['title']} ({len(project['images'])} imagen(es))")


if __name__ == "__main__":
    main()
