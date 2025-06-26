"""
Module pour la conversion de PDFs en Markdown en utilisant Docling.
"""

import os
import logging
from pathlib import Path
from typing import Optional, Union
from urllib.parse import urlparse
import requests
from docling.document_converter import DocumentConverter

logger = logging.getLogger(__name__)


class PDFConverter:
    """Classe pour convertir des PDFs en Markdown en utilisant Docling."""

    def __init__(self, output_dir: str = "documents"):
        """
        Initialise le convertisseur PDF.

        Args:
            output_dir (str): Dossier de destination pour les fichiers Markdown
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        self.converter = DocumentConverter()

    def is_url(self, string: str) -> bool:
        """Vérifie si la chaîne est une URL valide."""
        try:
            result = urlparse(string)
            return all([result.scheme, result.netloc])
        except ValueError:
            return False

    def download_pdf(self, url: str, temp_dir: str = "temp") -> str:
        """
        Télécharge un PDF depuis une URL vers un dossier temporaire.

        Args:
            url (str): URL du PDF à télécharger
            temp_dir (str): Dossier temporaire pour le téléchargement

        Returns:
            str: Chemin vers le fichier téléchargé
        """
        temp_path = Path(temp_dir)
        temp_path.mkdir(exist_ok=True)

        logger.info(f"Téléchargement du PDF depuis: {url}")
        response = requests.get(url)
        response.raise_for_status()

        # Extraire le nom du fichier depuis l'URL
        filename = os.path.basename(urlparse(url).path)
        if not filename.endswith(".pdf"):
            filename += ".pdf"

        file_path = temp_path / filename
        with open(file_path, "wb") as f:
            f.write(response.content)

        return str(file_path)

    def convert_to_markdown(self, pdf_source: Union[str, Path]) -> str:
        """
        Convertit un PDF en Markdown.

        Args:
            pdf_source (Union[str, Path]): Chemin vers le fichier PDF ou URL

        Returns:
            str: Chemin vers le fichier Markdown généré

        Raises:
            FileNotFoundError: Si le fichier PDF n'existe pas
            Exception: En cas d'erreur lors de la conversion
        """
        temp_file = None

        try:
            # Gérer les URLs
            if isinstance(pdf_source, str) and self.is_url(pdf_source):
                pdf_path = self.download_pdf(pdf_source)
                temp_file = pdf_path
            else:
                pdf_path = str(pdf_source)

            # Vérifier que le fichier existe
            if not os.path.exists(pdf_path):
                raise FileNotFoundError(f"Le fichier PDF n'existe pas: {pdf_path}")

            logger.info(f"Conversion du PDF: {pdf_path}")

            # Convertir le PDF
            result = self.converter.convert(pdf_path)

            # Extraire le contenu Markdown
            markdown_content = result.document.export_to_markdown()

            # Générer le nom du fichier de sortie
            pdf_filename = os.path.basename(pdf_path)
            markdown_filename = os.path.splitext(pdf_filename)[0] + ".md"
            output_path = self.output_dir / markdown_filename

            # Sauvegarder le fichier Markdown
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(markdown_content)

            logger.info(f"Fichier Markdown généré: {output_path}")
            return str(output_path)

        finally:
            # Nettoyer le fichier temporaire si nécessaire
            if temp_file and os.path.exists(temp_file):
                os.remove(temp_file)
                # Supprimer le dossier temp s'il est vide
                temp_dir = os.path.dirname(temp_file)
                if os.path.exists(temp_dir) and not os.listdir(temp_dir):
                    os.rmdir(temp_dir)

    def convert_multiple(self, pdf_sources: list) -> list:
        """
        Convertit plusieurs PDFs en Markdown.

        Args:
            pdf_sources (list): Liste des chemins/URLs des PDFs à convertir

        Returns:
            list: Liste des chemins vers les fichiers Markdown générés
        """
        results = []
        for pdf_source in pdf_sources:
            try:
                result = self.convert_to_markdown(pdf_source)
                results.append(result)
            except Exception as e:
                logger.error(f"Erreur lors de la conversion de {pdf_source}: {str(e)}")
                continue

        return results
