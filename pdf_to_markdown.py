#!/usr/bin/env python3
"""
Script pour convertir des PDFs en Markdown en utilisant Docling.
Les fichiers Markdown générés sont sauvegardés dans le dossier documents/.
"""

import os
import sys
import argparse
from pathlib import Path
from docling.document_converter import DocumentConverter
from urllib.parse import urlparse
import requests


def is_url(string):
    """Vérifie si la chaîne est une URL valide."""
    try:
        result = urlparse(string)
        return all([result.scheme, result.netloc])
    except ValueError:
        return False


def download_pdf(url, temp_dir="temp"):
    """Télécharge un PDF depuis une URL vers un dossier temporaire."""
    if not os.path.exists(temp_dir):
        os.makedirs(temp_dir)

    response = requests.get(url)
    response.raise_for_status()

    # Extraire le nom du fichier depuis l'URL
    filename = os.path.basename(urlparse(url).path)
    if not filename.endswith(".pdf"):
        filename += ".pdf"

    temp_path = os.path.join(temp_dir, filename)
    with open(temp_path, "wb") as f:
        f.write(response.content)

    return temp_path


def convert_pdf_to_markdown(pdf_source, output_dir="documents"):
    """
    Convertit un PDF en Markdown en utilisant Docling.

    Args:
        pdf_source (str): Chemin vers le fichier PDF ou URL
        output_dir (str): Dossier de destination pour le fichier Markdown

    Returns:
        str: Chemin vers le fichier Markdown généré
    """
    # Créer le dossier de sortie s'il n'existe pas
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Initialiser le convertisseur Docling
    converter = DocumentConverter()

    temp_file = None
    try:
        # Si c'est une URL, télécharger le fichier
        if is_url(pdf_source):
            print(f"Téléchargement du PDF depuis: {pdf_source}")
            pdf_path = download_pdf(pdf_source)
            temp_file = pdf_path
        else:
            pdf_path = pdf_source

        # Vérifier que le fichier existe
        if not os.path.exists(pdf_path):
            raise FileNotFoundError(f"Le fichier PDF n'existe pas: {pdf_path}")

        print(f"Conversion du PDF: {pdf_path}")

        # Convertir le PDF
        result = converter.convert(pdf_path)

        # Extraire le contenu Markdown
        markdown_content = result.document.export_to_markdown()

        # Générer le nom du fichier de sortie
        pdf_filename = os.path.basename(pdf_path)
        markdown_filename = os.path.splitext(pdf_filename)[0] + ".md"
        output_path = os.path.join(output_dir, markdown_filename)

        # Sauvegarder le fichier Markdown
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(markdown_content)

        print(f"Fichier Markdown généré: {output_path}")
        return output_path

    finally:
        # Nettoyer le fichier temporaire si nécessaire
        if temp_file and os.path.exists(temp_file):
            os.remove(temp_file)
            # Supprimer le dossier temp s'il est vide
            temp_dir = os.path.dirname(temp_file)
            if os.path.exists(temp_dir) and not os.listdir(temp_dir):
                os.rmdir(temp_dir)


def main():
    """Fonction principale du script."""
    parser = argparse.ArgumentParser(
        description="Convertit des PDFs en Markdown en utilisant Docling"
    )
    parser.add_argument(
        "pdf_source", help="Chemin vers le fichier PDF ou URL du PDF à convertir"
    )
    parser.add_argument(
        "-o",
        "--output",
        default="documents",
        help="Dossier de destination pour le fichier Markdown (défaut: documents)",
    )

    args = parser.parse_args()

    try:
        output_path = convert_pdf_to_markdown(args.pdf_source, args.output)
        print(f"✅ Conversion réussie! Fichier sauvegardé: {output_path}")

    except Exception as e:
        print(f"❌ Erreur lors de la conversion: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
