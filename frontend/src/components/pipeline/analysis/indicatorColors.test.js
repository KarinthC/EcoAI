// Tests de indicatorColors : couleur stable par indicateur.
import { describe, it, expect } from 'vitest'
import { CRITERIA_ORDER, indicatorColor } from '@/components/pipeline/analysis/indicatorColors.js'

describe('indicatorColors', () => {
  it('retourne une couleur hsl pour un indicateur connu', () => {
    expect(indicatorColor('PEF-GWP')).toMatch(/^hsl\(/)
  })

  it('retourne une couleur neutre pour un indicateur inconnu', () => {
    expect(indicatorColor('PEF-INCONNU')).toBe('#a0aec0')
  })

  it('associe une couleur distincte à chaque indicateur', () => {
    const colors = CRITERIA_ORDER.map((k) => indicatorColor(k))
    expect(new Set(colors).size).toBe(CRITERIA_ORDER.length)
  })

  it('est stable : même clé -> même couleur', () => {
    expect(indicatorColor('PEF-WU')).toBe(indicatorColor('PEF-WU'))
  })
})
