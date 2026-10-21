<script setup>
// Encart « Enjeux » d'un indicateur : résout le paragraphe narratif dans la
// langue active, puis délègue le rendu à StakesCard (présentation pure).
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { indicatorStakes } from '@/components/pipeline/analysis/indicatorStakes.js'
import StakesCard from '@/components/pipeline/analysis/StakesCard.vue'

const props = defineProps({
  // Clé technique stable du critère (ex. « PEF-GWP »).
  criterionKey: { type: String, required: true },
})

const { locale } = useI18n()

// Paragraphe dans la langue active (repli sur le français si absente).
const stakes = computed(() => indicatorStakes(props.criterionKey, locale.value))
</script>

<template>
  <StakesCard v-if="stakes" :criterion-key="criterionKey" :text="stakes" />
</template>

