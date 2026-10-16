// Tests de indicatorReferences : mapping critère PEF -> références fondatrices.
import { describe, it, expect } from 'vitest'
import { indicatorReferences } from '@/components/pipeline/analysis/indicatorReferences.js'
import { CRITERIA_ORDER } from '@/components/pipeline/analysis/indicatorColors.js'

describe('indicatorReferences', () => {
  it('retourne un tableau vide pour un critère inconnu', () => {
    expect(indicatorReferences('PEF-INCONNU')).toEqual([])
  })

  it('retourne au moins une référence pour chaque critère connu', () => {
    for (const key of CRITERIA_ORDER) {
      expect(indicatorReferences(key).length).toBeGreaterThan(0)
    }
  })

  it('chaque référence a une URL non vide et une clé i18n', () => {
    for (const key of CRITERIA_ORDER) {
      for (const ref of indicatorReferences(key)) {
        expect(typeof ref.url).toBe('string')
        expect(ref.url).toMatch(/^https?:\/\//)
        expect(typeof ref.sourceKey).toBe('string')
        expect(ref.sourceKey).toMatch(/^analysis\.reference\.source\./)
      }
    }
  })

  it('supporte plusieurs références pour un même critère', () => {
    // PEF-AP (acidification) porte deux références (Seppälä 2006 + Posch 2008).
    expect(indicatorReferences('PEF-AP').length).toBeGreaterThan(1)
  })
})
