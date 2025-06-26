from pathlib import Path
import re


def repl(match):
    code_point = int(match.group(1), 16)  # ex : "006F" → 111
    return chr(code_point)


def fix_unicode_in_markdown(file_path):
    """Corrige les codes Unicode dans un fichier Markdown"""
    try:
        text = file_path.read_text(encoding="utf-8")

        # remplace /uniXXXX ou v/uniXXXX, peu importe la lettre devant
        new_text = re.sub(r"/uni([0-9A-Fa-f]{4})", repl, text)

        # Vérifier s'il y a eu des changements
        if new_text != text:
            file_path.write_text(new_text, encoding="utf-8")
            print(f"✓ Fichier corrigé : {file_path.name}")
            return True
        else:
            print(f"- Aucune correction nécessaire : {file_path.name}")
            return False
    except Exception as e:
        print(f"✗ Erreur lors du traitement de {file_path.name}: {e}")
        return False


def main():
    documents_dir = Path("documents")

    if not documents_dir.exists():
        print(f"Le dossier '{documents_dir}' n'existe pas.")
        return

    # Trouver tous les fichiers .md dans le dossier documents
    md_files = list(documents_dir.glob("*.md"))

    if not md_files:
        print(f"Aucun fichier Markdown trouvé dans le dossier '{documents_dir}'.")
        return

    print(f"Traitement de {len(md_files)} fichier(s) Markdown...")
    print("-" * 50)

    corrected_count = 0
    for md_file in md_files:
        if fix_unicode_in_markdown(md_file):
            corrected_count += 1

    print("-" * 50)
    print(
        f"Traitement terminé ! {corrected_count} fichier(s) corrigé(s) sur {len(md_files)}."
    )


if __name__ == "__main__":
    main()
