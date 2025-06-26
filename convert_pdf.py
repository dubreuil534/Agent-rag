#!/usr/bin/env python3
"""
Script CLI pour convertir des PDFs en Markdown en utilisant Docling.
Par défaut, traite tous les PDFs du dossier pdf/
"""

import argparse
import sys
import os
import glob
from pathlib import Path
from ingestion.pdf_converter import PDFConverter


def find_pdf_files(pdf_folder="pdf"):
    """
    Trouve tous les fichiers PDF dans un dossier.

    Args:
        pdf_folder (str): Chemin vers le dossier contenant les PDFs

    Returns:
        list: Liste des chemins vers les fichiers PDF trouvés
    """
    pdf_folder = Path(pdf_folder)
    if not pdf_folder.exists():
        print(f"⚠️ Le dossier {pdf_folder} n'existe pas")
        return []

    if not pdf_folder.is_dir():
        print(f"⚠️ {pdf_folder} n'est pas un dossier")
        return []

    # Rechercher tous les fichiers PDF (extensions .pdf et .PDF)
    pdf_files = []
    for pattern in ["*.pdf", "*.PDF"]:
        pdf_files.extend(pdf_folder.glob(pattern))

    return [str(pdf_file) for pdf_file in sorted(pdf_files)]


def main():
    """Fonction principale du script CLI."""
    parser = argparse.ArgumentParser(
        description="Convertit des PDFs en Markdown en utilisant Docling",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemples d'utilisation:
  python convert_pdf.py                           # Convertit tous les PDFs du dossier pdf/
  python convert_pdf.py document.pdf             # Convertit un fichier spécifique
  python convert_pdf.py https://arxiv.org/pdf/2408.09869.pdf
  python convert_pdf.py document.pdf file2.pdf   # Convertit plusieurs fichiers
  python convert_pdf.py --folder mon_dossier/    # Convertit tous les PDFs d'un autre dossier
        """,
    )

    # Groupe mutuellement exclusif pour les sources
    source_group = parser.add_mutually_exclusive_group()

    source_group.add_argument(
        "pdf_sources",
        nargs="*",
        help="Chemin(s) vers le(s) fichier(s) PDF ou URL(s) à convertir (si vide, traite le dossier pdf/)",
    )

    source_group.add_argument(
        "--folder", help="Dossier contenant les PDFs à convertir (par défaut: pdf/)"
    )

    parser.add_argument(
        "-o",
        "--output",
        default="documents",
        help="Dossier de destination pour les fichiers Markdown (défaut: documents)",
    )

    parser.add_argument(
        "-v", "--verbose", action="store_true", help="Affichage détaillé des opérations"
    )

    args = parser.parse_args()

    # Configuration du logging si verbose
    if args.verbose:
        import logging

        logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

    # Déterminer les sources PDF à traiter
    pdf_sources = []

    if args.folder:
        # Utiliser le dossier spécifié
        pdf_sources = find_pdf_files(args.folder)
        if not pdf_sources:
            print(f"❌ Aucun fichier PDF trouvé dans le dossier: {args.folder}")
            sys.exit(1)
        print(f"📁 Traitement du dossier: {args.folder}")
    elif args.pdf_sources:
        # Utiliser les fichiers spécifiés
        pdf_sources = args.pdf_sources
        print(f"📄 Traitement de fichiers spécifiques")
    else:
        # Par défaut, traiter le dossier pdf/
        pdf_sources = find_pdf_files("pdf")
        if not pdf_sources:
            print("❌ Aucun fichier PDF trouvé dans le dossier pdf/")
            print(
                "💡 Créez un dossier 'pdf/' et placez-y vos fichiers PDF, ou spécifiez des fichiers individuels"
            )
            sys.exit(1)
        print(f"📁 Traitement du dossier par défaut: pdf/")

    # Initialiser le convertisseur
    converter = PDFConverter(output_dir=args.output)

    print(f"🔄 Conversion de {len(pdf_sources)} fichier(s) PDF vers Markdown...")
    print(f"📁 Dossier de sortie: {args.output}")
    print()

    success_count = 0
    total_count = len(pdf_sources)

    for i, pdf_source in enumerate(pdf_sources, 1):
        print(f"[{i}/{total_count}] Traitement: {pdf_source}")

        try:
            output_path = converter.convert_to_markdown(pdf_source)
            print(f"  ✅ Converti vers: {output_path}")
            success_count += 1

        except FileNotFoundError as e:
            print(f"  ❌ Fichier non trouvé: {e}")

        except Exception as e:
            print(f"  ❌ Erreur: {str(e)}")

        print()

    # Résumé final
    print("=" * 50)
    print(f"📊 Résumé de la conversion:")
    print(f"  • Succès: {success_count}/{total_count}")
    print(f"  • Échecs: {total_count - success_count}/{total_count}")

    if success_count > 0:
        print(f"  • Fichiers sauvegardés dans: {args.output}/")

    # Code de sortie
    if success_count == total_count:
        print("🎉 Toutes les conversions ont réussi!")
        sys.exit(0)
    elif success_count > 0:
        print("⚠️ Certaines conversions ont échoué.")
        sys.exit(1)
    else:
        print("💥 Aucune conversion n'a réussi.")
        sys.exit(1)


if __name__ == "__main__":
    main()
