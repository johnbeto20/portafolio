#!/usr/bin/env python3
"""
Elimina imágenes originales (.png, .jpg, .jpeg) cuando existe
una versión .webp con el mismo nombre en la misma carpeta.

Uso (desde la raiz del proyecto):
    python scripts/cleanup_duplicates.py

Esto deja solo las versiones .webp optimizadas.
"""

from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
IMG_DIR = ROOT / "img"
CERTIFICADOS = ROOT / "Certificados"

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
                print(f"  ELIMINADA: {original.relative_to(IMG_DIR)}")
                deleted += 1
    
    return deleted

def main():
    print("=" * 70)
    print("LIMPIEZA DE IMAGENES DUPLICADAS")
    print("Elimina .png/.jpg/.jpeg cuando existe .webp con mismo nombre")
    print("=" * 70)
    
    total_deleted = 0
    
    # Limpiar img/
    print(f"\n[1/2] Procesando {IMG_DIR}/...")
    if IMG_DIR.exists():
        total_deleted += cleanup_folder(IMG_DIR)
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
