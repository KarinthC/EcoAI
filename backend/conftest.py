"""Configuration pytest commune au dossier backend.

Ajoute la racine `backend/` au sys.path pour que les imports
`app.services...` fonctionnent quel que soit le répertoire d'appel.
"""

import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
