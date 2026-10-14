// frontend/src/components/pipeline/analysis/nodeColors.js
//
// Palette STABLE par nœud, utilisée par les camemberts de contribution
// (un secteur par nœud contributeur).
//
// Contrairement aux indicateurs (couleur fixe par clé technique), les nœuds
// n'ont pas d'ordre stable connu à l'avance : la couleur est donc dérivée de
// l'INDEX du nœud dans la liste affichée.
//
// La palette est ORDONNÉE pour que les PREMIÈRES couleurs soient bien
// distinctes entre elles (un pipeline courant a 3 à 6 nœuds) : bleu, violet,
// rose, jaune canard, turquoise, orange… On évite le vert et le rouge purs,
// pour ne pas être confondus avec le code couleur d'impact (vert = faible,
// rouge = élevé).

// Palette ordonnée : les premières teintes sont volontairement très
// contrastées entre voisines.
const NODE_PALETTE = [
  '#2196F3', // bleu
  '#7E57C2', // violet
  '#EC407A', // rose
  '#FBC02D', // jaune canard
  '#26A69A', // turquoise
  '#FB8C00', // orange
  '#5C6BC0', // bleu indigo
  '#AB47BC', // pourpre
  '#00897B', // sarcelle
  '#8D6E63', // brun
  '#D81B60', // framboise
  '#546E7A', // bleu-gris
]

// Couleur d'un nœud : teinte dérivée de sa position dans la liste. Au-delà de
// la palette, on boucle (les pipelines dépassent rarement 12 nœuds).
export function nodeColor(index) {
  return NODE_PALETTE[index % NODE_PALETTE.length]
}

