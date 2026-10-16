// frontend/src/components/pipeline/analysis/useStakesReveal.js
//
// Composable de l'effet « révélation » de l'encart Enjeux : au survol de la
// zone image, le bord du dégradé ondule doucement (sans gagner de place) ;
// après un délai continu, l'image submerge le bloc puis une citation apparaît,
// avant de disparaître.
//
// La logique (état + timers) est isolée ici pour rester testable et garder
// StakesCard.vue en présentation pure.
//
// Phases :
//   idle      : état initial (aucun effet)
//   pulsing   : survol en cours, ondulation du bord dégradé
//   revealed  : image submergée (déclenche l'apparition de la citation)
//   quote     : citation affichée
//
// Contraintes :
//   - tactile / pas de survol : aucun déclenchement ;
//   - prefers-reduced-motion : aucun déclenchement ;
//   - sortie de souris avant la submersion : annulation (après un court délai
//     de grâce pour absorber les micro-mouvements du curseur).

import { ref, computed, onUnmounted } from 'vue'

// Durée d'ondulation avant submersion (ms).
export const PULSE_DURATION_MS = 5000
// Durée d'affichage de la citation (ms), après la submersion.
export const QUOTE_DURATION_MS = 10000
// Délai de grâce avant annulation à la sortie de souris (ms) : absorbe les
// micro-mouvements du curseur sans interrompre l'effet.
export const LEAVE_GRACE_MS = 300

/**
 * Détecte si l'effet peut se déclencher : appareil avec survol réel (pas
 * tactile) et animations autorisées par l'utilisateur.
 * @returns {boolean}
 */
function canReveal() {
  if (typeof window === 'undefined' || !window.matchMedia) return false
  const hoverCapable = window.matchMedia('(hover: hover)').matches
  const reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches
  return hoverCapable && !reducedMotion
}

/**
 * Pilote l'effet de révélation de l'encart Enjeux.
 * @returns {{
 *   phase: import('vue').Ref<string>,
 *   isPulsing: import('vue').ComputedRef<boolean>,
 *   isRevealed: import('vue').ComputedRef<boolean>,
 *   showQuote: import('vue').ComputedRef<boolean>,
 *   onEnter: () => void,
 *   onLeave: () => void,
 * }}
 */
export function useStakesReveal() {
  const phase = ref('idle')
  let pulseTimer = null
  let quoteTimer = null
  let leaveTimer = null

  function clearTimers() {
    if (pulseTimer) {
      clearTimeout(pulseTimer)
      pulseTimer = null
    }
    if (quoteTimer) {
      clearTimeout(quoteTimer)
      quoteTimer = null
    }
    if (leaveTimer) {
      clearTimeout(leaveTimer)
      leaveTimer = null
    }
  }

  // Démarre l'ondulation au survol de la zone image.
  function onEnter() {
    if (!canReveal()) return
    // Un retour dans la zone annule une annulation en cours.
    if (leaveTimer) {
      clearTimeout(leaveTimer)
      leaveTimer = null
    }
    if (phase.value !== 'idle') return
    phase.value = 'pulsing'
    pulseTimer = setTimeout(() => {
      pulseTimer = null
      phase.value = 'revealed'
      // La citation apparaît après la submersion, puis disparaît.
      quoteTimer = setTimeout(() => {
        quoteTimer = null
        phase.value = 'idle'
      }, QUOTE_DURATION_MS)
    }, PULSE_DURATION_MS)
  }

  // Sortie de souris : annule tant que la submersion n'a pas eu lieu, après un
  // court délai de grâce (un retour rapide dans la zone annule l'annulation).
  function onLeave() {
    if (phase.value !== 'pulsing') return
    if (leaveTimer) return
    leaveTimer = setTimeout(() => {
      leaveTimer = null
      if (phase.value === 'pulsing') {
        clearTimers()
        phase.value = 'idle'
      }
    }, LEAVE_GRACE_MS)
  }

  onUnmounted(clearTimers)

  return {
    phase,
    isPulsing: computed(() => phase.value === 'pulsing'),
    isRevealed: computed(() => phase.value === 'revealed' || phase.value === 'quote'),
    showQuote: computed(() => phase.value === 'revealed' || phase.value === 'quote'),
    onEnter,
    onLeave,
  }
}
