# backend/app/services/carbon/acv/__init__.py
"""Famille de nœuds dont les impacts sont calculés via un modèle ACV documenté.

Ces nœuds s'appuient sur les données d'Analyse de Cycle de Vie (ACV) des GPUs
utilisés dans nos serveurs (rapport ADEME/AltImpact) et produisent l'ensemble
des indicateurs PEF, pas seulement le GWP.

Méthode : 'acv' — confiance : 'high' (données ACV documentées).
"""
