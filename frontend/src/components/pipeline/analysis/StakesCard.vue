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
//
// Deux régimes de rendu, volontairement disjoints :
//   - état normal : fenêtre fixe 240×180, image positionnée par transform
//     (point focal `focal` + `zoom`) ;
//   - submersion : le bloc est forcé au ratio 19:10 et l'image le remplit en
//     CSS pur (object-fit: cover + object-position). Aucune mesure JS.
import { computed } from 'vue'
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

// Image d'illustration du critère ({ src, focal, focalWide, zoom } ou null).
const image = computed(() => stakesImage(props.criterionKey))

// Dimensions de la fenêtre image en état normal (cf. CSS .stakes-image-zone).
const NORMAL_ZONE = { width: 240, height: 180 }

// Transform de l'image en état normal : affichée à sa taille réelle, mise à
// l'échelle (zoom) puis translatée pour que le point focal tombe au centre de
// la fenêtre fixe. En submersion, le CSS reprend la main (object-fit: cover).
const imageTransform = computed(() => {
  const img = image.value
  if (!img?.focal) return 'none'
  const zoom = img.zoom ?? 1
  const dx = NORMAL_ZONE.width / 2 - img.focal.x * zoom
  const dy = NORMAL_ZONE.height / 2 - img.focal.y * zoom
  return `translate(${dx}px, ${dy}px) scale(${zoom})`
})

// Cadrage de l'image en submersion : point focal exprimé en fraction de
// l'image (0–1), `focalWide` prioritaire, repli sur `focal`.
const wideObjectPosition = computed(() => {
  const img = image.value
  const focal = img?.focalWide || img?.focal
  if (!focal) return '50% 50%'
  return `${focal.x * 100}% ${focal.y * 100}%`
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
      class="stakes-image-zone"
      :class="{ 'is-pulsing': isPulsing }"
      @mouseenter="onEnter"
      @mouseleave="onLeave"
    >
      <img
        class="stakes-image"
        :src="image.src"
        :style="{ transform: imageTransform, objectPosition: wideObjectPosition }"
        alt=""
        aria-hidden="true"
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
/* Submersion : le bloc est forcé au ratio 19:10 (hauteur indépendante du
   texte) et l'image le remplit en CSS pur. */
.stakes-card.is-revealed {
  aspect-ratio: 19 / 10;
  padding: 0;
}
.stakes-card.is-revealed .stakes-image-zone {
  inset: 0;
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
/* L'image remplit la zone (cover) : plus de transform, le cadrage vient de
   object-position (point focal en fraction de l'image). */
.stakes-card.is-revealed .stakes-image {
  inset: 0;
  width: 100%;
  height: 100%;
  object-fit: cover;
  transform: none !important;
}
/* Le contenu passe au-dessus de l'image, et s'efface quand l'image submerge.
   En submersion il sort du flux : c'est le ratio 19:10 qui fixe la hauteur. */
.stakes-content {
  position: relative;
  z-index: 1;
  transition: opacity 0.4s ease;
}
.stakes-content.is-hidden {
  position: absolute;
  inset: 0;
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
