<script setup>
// Carte « Enjeux » : paragraphe narratif d'un indicateur, avec une image
// d'illustration fondue dans le coin inférieur droit.
//
// Le fondu de l'image vers le fond de la carte est porté par un pseudo-élément
// superposé (::after) : on anime sa position/opacité, ce qui est interpolable
// partout (contrairement à mask-size).
//
// Effet de révélation (survol de la zone image uniquement) :
//   - le bord du dégradé ondule doucement (animation du ::after) ;
//   - après 5 s de survol continu, l'image submerge le bloc (fondu) ;
//   - une citation apparaît alors sur un voile sombre, puis disparaît (10 s).
// La logique d'état et de timers vit dans useStakesReveal (composable).
import { computed, ref, watch, onBeforeUnmount } from 'vue'
import { useI18n } from 'vue-i18n'
import { stakesImage } from '@/components/pipeline/analysis/stakesImages.js'
import { indicatorQuote } from '@/components/pipeline/analysis/indicatorStakes.js'
import { useStakesReveal } from '@/components/pipeline/analysis/useStakesReveal.js'

const props = defineProps({
  // Clé technique stable du critère (ex. « PEF-GWP »), pour résoudre l'image.
  criterionKey: { type: String, required: true },
  // Paragraphe narratif à afficher.
  text: { type: String, required: true },
})

const { locale } = useI18n()

// Image d'illustration du critère ({ src, focal, zoom } ou null).
const image = computed(() => stakesImage(props.criterionKey))

// Dimensions naturelles de l'image source (remplies au chargement).
const naturalSize = ref({ width: 0, height: 0 })

// Dimensions courantes de la zone image (fenêtre ou bloc submergé), mesurées
// par ResizeObserver : elles varient avec l'état et la taille du bloc.
const zoneSize = ref({ width: 0, height: 0 })
const zoneEl = ref(null)
let resizeObserver = null

function onImageLoad(event) {
  const img = event.target
  naturalSize.value = { width: img.naturalWidth, height: img.naturalHeight }
}

// Observe la zone image pour suivre ses dimensions réelles (fenêtre fixe en
// état normal, bloc entier en submersion).
watch(zoneEl, (el) => {
  if (resizeObserver) {
    resizeObserver.disconnect()
    resizeObserver = null
  }
  if (!el || typeof ResizeObserver === 'undefined') return
  resizeObserver = new ResizeObserver((entries) => {
    const rect = entries[0].contentRect
    zoneSize.value = { width: rect.width, height: rect.height }
  })
  resizeObserver.observe(el)
})

onBeforeUnmount(() => {
  if (resizeObserver) resizeObserver.disconnect()
})

// Transform de l'image : elle est affichée à sa taille réelle, mise à l'échelle
// (scale) puis translatée pour que le point focal tombe au centre de la zone.
//
// - En état normal : scale = zoom, point focal = `focal`.
// - En submersion : scale = max(zoom, couverture) pour que l'image couvre tout
//   le bloc (comme object-fit: cover), point focal = `focalWide` s'il est
//   défini (cadrage propre au format large), sinon `focal`.
//
// Le point focal reste donc TOUJOURS au centre, quel que soit l'état.
const imageTransform = computed(() => {
  const img = image.value
  const { width: natW, height: natH } = naturalSize.value
  const { width: zoneW, height: zoneH } = zoneSize.value
  if (!img?.focal || !natW || !natH || !zoneW || !zoneH) return 'none'

  // Point focal : celui du mode large en submersion (repli sur le normal).
  const focal = isRevealed.value && img.focalWide ? img.focalWide : img.focal

  const zoom = img.zoom ?? 1
  let scale = zoom
  if (isRevealed.value) {
    // Couverture : l'image doit remplir la zone dans les deux dimensions.
    const coverScale = Math.max(zoneW / natW, zoneH / natH)
    scale = Math.max(zoom, coverScale)
  }

  const dx = zoneW / 2 - focal.x * scale
  const dy = zoneH / 2 - focal.y * scale
  return `translate(${dx}px, ${dy}px) scale(${scale})`
})

// Citation « révélation » (vide tant qu'elle n'est pas rédigée).
const quote = computed(() => indicatorQuote(props.criterionKey, locale.value))

// État de l'effet de révélation (ondulation -> submersion -> citation).
const { isPulsing, isRevealed, showQuote, onEnter, onLeave } = useStakesReveal()
</script>

<template>
  <div class="stakes-card" :class="{ 'is-revealed': isRevealed, 'has-image': image }">
    <!-- Zone image : déclenche l'effet au survol (coin inférieur droit). -->
    <div
      v-if="image"
      ref="zoneEl"
      class="stakes-image-zone"
      :class="{ 'is-pulsing': isPulsing }"
      @mouseenter="onEnter"
      @mouseleave="onLeave"
    >
      <img
        class="stakes-image"
        :src="image.src"
        :style="{ transform: imageTransform }"
        alt=""
        aria-hidden="true"
        @load="onImageLoad"
      />
    </div>

    <div class="stakes-content" :class="{ 'is-hidden': isRevealed }">
      <div class="stakes-header">
        <span class="stakes-icon" aria-hidden="true">
          <!-- Icône Lucide « globe » (licence ISC). -->
          <svg viewBox="0 0 24 24" width="18" height="18" fill="none"
               stroke="currentColor" stroke-width="2"
               stroke-linecap="round" stroke-linejoin="round">
            <circle cx="12" cy="12" r="10" />
            <path d="M12 2a14.5 14.5 0 0 0 0 20 14.5 14.5 0 0 0 0-20" />
            <path d="M2 12h20" />
          </svg>
        </span>
        <h4>{{ $t('analysis.stakes.title') }}</h4>
      </div>
      <p class="stakes-text">{{ text }}</p>
    </div>

    <!-- Citation révélée : voile sombre + texte en fondu. -->
    <div v-if="quote" class="stakes-quote" :class="{ 'is-visible': showQuote }">
      <p class="stakes-quote-text">{{ quote }}</p>
    </div>
  </div>
</template>

<style scoped>
.stakes-card {
  position: relative;
  overflow: hidden;
  background: #f7fafc;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  padding: 0.85rem 1rem;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.08);
}
/* Réserve la largeur de la zone image pour que le texte ne passe jamais
   dessous (l'image reste en absolu, fondue dans le coin). */
.stakes-card.has-image {
  padding-right: 250px;
}
/* Zone de survol de l'image : hauteur FIXE (cadrage stable quelle que soit la
   hauteur du bloc), ancrée en bas à droite. */
.stakes-image-zone {
  position: absolute;
  right: 0;
  bottom: 0;
  width: 240px;
  height: 180px;
  pointer-events: auto;
  /* Fenêtre : ne montre qu'une partie de l'image. */
  overflow: hidden;
  /* Fond les bords de la fenêtre (dégradé) pour éviter les lignes droites
     visibles quand le voile pulse. */
  -webkit-mask-image: radial-gradient(
    ellipse 100% 100% at 100% 100%,
    #000 55%,
    transparent 100%
  );
  mask-image: radial-gradient(
    ellipse 100% 100% at 100% 100%,
    #000 55%,
    transparent 100%
  );
}
/* Image affichée à sa taille réelle (mise à l'échelle par zoom), ancrée en haut
   à gauche de la fenêtre puis translatée (transform) pour centrer le point
   focal. Le cadre agit comme une fenêtre sur l'image native. */
.stakes-image {
  position: absolute;
  top: 0;
  left: 0;
  max-width: none;
  max-height: none;
  transform-origin: top left;
  pointer-events: none;
  user-select: none;
}
/* Voile de fondu superposé : dégradé radial opaque en bas à droite, transparent
   vers le haut/gauche. On anime sa position/opacité (interpolable partout). */
.stakes-image-zone::after {
  content: '';
  position: absolute;
  inset: 0;
  pointer-events: none;
  background: radial-gradient(
    ellipse 120% 120% at 100% 100%,
    transparent 0%,
    transparent 45%,
    #f7fafc 90%
  );
  transition: opacity 0.6s ease, transform 0.6s ease;
}
/* Ondulation : le bord du dégradé « respire » (le voile se déplace légèrement),
   sans que l'image ne change de taille. */
.stakes-image-zone.is-pulsing::after {
  animation: stakes-wave 2.4s ease-in-out infinite;
}
@keyframes stakes-wave {
  0%,
  100% {
    transform: translate(0, 0) scale(1);
    opacity: 1;
  }
  50% {
    transform: translate(-12%, -12%) scale(1.3);
    opacity: 0.8;
  }
}
/* Submersion : la zone prend tout le bloc, le voile s'efface en fondu. Le
   transform de l'image (calculé en JS) la fait couvrir la zone en gardant le
   point focal centré. */
.stakes-card.is-revealed .stakes-image-zone {
  width: 100%;
  height: 100%;
  -webkit-mask-image: none;
  mask-image: none;
}
.stakes-card.is-revealed .stakes-image-zone::after {
  animation: none;
  opacity: 0;
  transform: scale(1.4);
}
/* Le contenu passe au-dessus de l'image, et s'efface quand l'image submerge. */
.stakes-content {
  position: relative;
  z-index: 1;
  transition: opacity 0.4s ease;
}
.stakes-content.is-hidden {
  opacity: 0;
  pointer-events: none;
}
.stakes-header {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 0.4rem;
}
.stakes-icon {
  display: inline-flex;
  align-items: center;
  color: #4a5568;
}
.stakes-header h4 {
  margin: 0;
  color: #2d3748;
}
.stakes-text {
  margin: 0;
  font-size: 0.85rem;
  line-height: 1.55;
  color: #2d3748;
}
/* Citation révélée : voile sombre semi-transparent + texte en fondu. */
.stakes-quote {
  position: absolute;
  inset: 0;
  z-index: 2;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 1.5rem;
  background: rgba(20, 24, 33, 0.72);
  opacity: 0;
  pointer-events: none;
  transition: opacity 0.8s ease;
}
.stakes-quote.is-visible {
  opacity: 1;
}
.stakes-quote-text {
  margin: 0;
  max-width: 80%;
  text-align: center;
  font-size: 1rem;
  font-style: italic;
  line-height: 1.5;
  color: #f7fafc;
}
</style>
