from pathlib import Path

from flask import Blueprint, send_file

docs_bp = Blueprint('docs', __name__)

# Documents statiques servis en téléchargement (explications des seuils et de
# la démarche ADEME/SRC). Résolu relativement à ce fichier : indépendant du cwd
# de lancement du serveur.
STATIC_DIR = Path(__file__).resolve().parent.parent / 'static'
SEUILS_PDF = STATIC_DIR / 'Explication_démarche_métriques__seuils.pdf'


@docs_bp.route('/api/docs/seuils-demarche.pdf', methods=['GET'])
def download_seuils_pdf():
    """Télécharge l'explication PDF des seuils (métriques) et de la démarche.

    Le nom de fichier côté client est normalisé en ASCII pour éviter les
    problèmes d'encodage lors du téléchargement.
    """
    if not SEUILS_PDF.is_file():
        return {'error': 'Document indisponible'}, 404
    return send_file(
        SEUILS_PDF,
        mimetype='application/pdf',
        as_attachment=True,
        download_name='explication-seuils-demarche.pdf',
    )
