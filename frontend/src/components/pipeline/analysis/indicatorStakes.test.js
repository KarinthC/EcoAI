// Tests de indicatorStakes : texte « Enjeux » par critère PEF.
import { describe, it, expect } from 'vitest'
import { indicatorStakes } from '@/components/pipeline/analysis/indicatorStakes.js'
import { CRITERIA_ORDER } from '@/components/pipeline/analysis/indicatorColors.js'

describe('indicatorStakes', () => {
  it('retourne une chaîne vide pour un critère inconnu', () => {
    expect(indicatorStakes('PEF-INCONNU')).toBe('')
  })

  it('retourne un paragraphe non vide pour chaque critère connu', () => {
    for (const key of CRITERIA_ORDER) {
      expect(indicatorStakes(key, 'fr').length).toBeGreaterThan(0)
      expect(indicatorStakes(key, 'en').length).toBeGreaterThan(0)
    }
  })

  it('fournit un texte français et anglais distincts', () => {
    const fr = indicatorStakes('PEF-GWP', 'fr')
    const en = indicatorStakes('PEF-GWP', 'en')
    expect(fr).not.toBe(en)
  })

  it('replie sur le français si la langue est inconnue', () => {
    expect(indicatorStakes('PEF-GWP', 'de')).toBe(indicatorStakes('PEF-GWP', 'fr'))
  })
})
