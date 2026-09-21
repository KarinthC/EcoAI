// Échelle LOGARITHMIQUE partagée pour colorer les valeurs d'impact en fonction
// du ratio valeur/seuil (valeur / seuil mensuel par habitant).
//
// Utilisée à l'identique par la Sidebar (impact global) et par le panneau de
// détail d'un nœud (impact par indicateur) afin que le dégradé soit cohérent.
//
// Du vert (120°) au rouge (0°) : ratio <= 0 -> vert, ratio >= 1 -> rouge.
export default function useImpactColor() {
  // Couleur d'une valeur via échelle LOGARITHMIQUE sur `ratio` (valeur/seuil).
  function ratioColor(ratio) {
    if (ratio === null || ratio === undefined) return '#4a5568'
    if (ratio <= 0) return 'hsl(120, 60%, 40%)'
    const lo = Math.log10(0.01)
    const hi = Math.log10(1)
    let t = (Math.log10(ratio) - lo) / (hi - lo)
    t = Math.min(1, Math.max(0, t))
    const hue = 120 * (1 - t) // 120° (vert) -> 0° (rouge)
    return `hsl(${hue}, 75%, 42%)`
  }

  return {
    ratioColor,
  }
}
