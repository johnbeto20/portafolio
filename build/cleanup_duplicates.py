#!/usr/bin/env python3
"""
Elimina imágenes originales (.png, .jpg, .jpeg) cuando existe
una versión .webp con el mismo nombre en la misma carpeta.

Uso (desde la raiz del proyecto):
    python build/cleanup_duplicates.py

Esto deja solo las versiones .webp optimizadas.
"""

import sys
from pathlib import Path

# Importar la configuracion central (build/config/site_config.py)
sys.path.insert(0, str(Path(__file__).resolve().parent))
from config.site_config import (  # noqa: E402
    ROOT,
    SITE_IMAGES_DIR,
    CERTIFICADOS_DIR as CERTIFICADOS,
)

SOURCE_EXTENSIONS = {".png", ".jpg", ".jpeg"}

def cleanup_folder(folder):
    """Elimina originales cuando existe .webp con mismo nombre."""
    deleted = 0
    
    for webp_file in folder.rglob("*.webp"):
        stem = webp_file.stem
        parent = webp_file.parent
        
        for ext in SOURCE_EXTENSIONS:
            original = parent / f"{stem}{ext}"
            if original.exists():
                original.unlink()
                print(f"  ELIMINADA: {original.relative_to(ROOT)}")
                deleted += 1
    
    return deleted

def main():
    print("=" * 70)
    print("LIMPIEZA DE IMAGENES DUPLICADAS")
    print("Elimina .png/.jpg/.jpeg cuando existe .webp con mismo nombre")
    print("=" * 70)
    
    total_deleted = 0
    
    # Limpiar img/ (proyectos, mentoria, brand, src)
    print(f"\n[1/2] Procesando {SITE_IMAGES_DIR}/...")
    if SITE_IMAGES_DIR.exists():
        total_deleted += cleanup_folder(SITE_IMAGES_DIR)
    else:
        print("  [AVISO] Carpeta img/ no encontrada")
    
    # Limpiar Certificados/
    print(f"\n[2/2] Procesando {CERTIFICADOS}/...")
    if CERTIFICADOS.exists():
        total_deleted += cleanup_folder(CERTIFICADOS)
    else:
        print("  [AVISO] Carpeta Certificados/ no encontrada")
    
    print(f"\n{'=' * 70}")
    print(f"RESUMEN")
    print(f"{'=' * 70}")
    print(f"Total de imagenes eliminadas: {total_deleted}")
    print(f"\nAhora solo se conservan las versiones .webp optimizadas.")

if __name__ == "__main__":
    main()
