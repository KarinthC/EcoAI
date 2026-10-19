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

// Image d'illustration du critère ({ src, focal } ou null).
const image = computed(() => stakesImage(props.criterionKey))

// `object-position` en pixels : le point focal de l'image source est centré
// dans le cadre (petit carré comme bloc agrandi), sans conversion.
const objectPosition = computed(() => {
  const focal = image.value?.focal
  return focal ? `${focal.x}px ${focal.y}px` : 'center'
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
        :style="{ objectPosition }"
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
  padding-right: 180px;
}
/* Zone de survol de l'image : hauteur FIXE (cadrage stable quelle que soit la
   hauteur du bloc), ancrée en bas à droite. */
.stakes-image-zone {
  position: absolute;
  right: 0;
  bottom: 0;
  width: 170px;
  height: 130px;
  pointer-events: auto;
}
/* Image : remplit la zone sans déformation, cadrée par object-position. */
.stakes-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
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
    ellipse 130% 130% at 100% 100%,
    transparent 0%,
    transparent 30%,
    #f7fafc 78%
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
    transform: translate(-6%, -6%) scale(1.15);
    opacity: 0.85;
  }
}
/* Submersion : l'image remplit le bloc, le voile s'efface en fondu. */
.stakes-card.is-revealed .stakes-image-zone {
  width: 100%;
  height: 100%;
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
