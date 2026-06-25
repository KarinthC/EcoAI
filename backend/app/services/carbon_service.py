def compute_impact(pipeline: dict) -> dict:
    # Coefficients par type (kgCO2 par unité).
    COEFFS = {
        'Données': {'base': 0.0, 'par_go': 0.01},            # 0.01 kg par Go
        'Entrainement': {'base': 0.5, 'par_param': 0.0001, 'par_epoch': 0.05, 'par_batch': 0.001},
        'Inférence': {'base': 0.1, 'par_lot': 0.0002}
    }
    
    total_impact = 0.0
    nodes_analysis = []
    
    for node in pipeline.get('nodes', []):
        label = node.get('data', {}).get('label', '')
        params = node.get('data', {}).get('params', {})
        impact = 0.0
        suggestions = []
        
        coeff = COEFFS.get(label, {})
        impact += coeff.get('base', 0)
        
        if label == 'Données':
            taille = float(params.get('taille', 0))
            impact += taille * coeff.get('par_go', 0)
        elif label == 'Entrainement':
            nb_param = float(params.get('parametres', 0))
            nb_epochs = float(params.get('epochs', 0))
            batch_size = float(params.get('batch_size', 1))
            impact += nb_param * coeff.get('par_param', 0)
            impact += nb_epochs * coeff.get('par_epoch', 0)
            impact += batch_size * coeff.get('par_batch', 0)
        elif label == 'Inférence':
            taille_lot = float(params.get('taille_lot', 0))
            impact += taille_lot * coeff.get('par_lot', 0)
        
        # Niveau de criticité
        if impact < 5:
            level = 'low'
        elif impact < 20:
            level = 'medium'
        else:
            level = 'high'
            suggestions.append(f"L'impact du nœud '{label}' est élevé ({impact:.1f} kgCO₂). Essayez de réduire les paramètres.")
        
        nodes_analysis.append({
            'id': node['id'],
            'impact_kg': round(impact, 2),
            'level': level,
            'message': suggestions[0] if suggestions else ''
        })
        total_impact += impact
    
    # Suggestions globales
    global_suggestions = []
    if total_impact > 30:
        global_suggestions.append("L'empreinte totale est très élevée. Pensez à utiliser des modèles pré-entraînés.")
    if total_impact > 10:
        global_suggestions.append("Réduire le nombre d'epochs ou la taille du batch peut significativement baisser l'impact.")
    
    equivalences = {
        'km_voiture': round(total_impact * 4.5, 1),
        'heures_streaming': round(total_impact * 2.3, 1),
        'repas_equivalent': round(total_impact * 0.1, 1)
    }

    return {
        'total_impact_kg': round(total_impact, 2),
        'nodes': nodes_analysis,
        'suggestions': global_suggestions,
        'equivalences': equivalences
    }