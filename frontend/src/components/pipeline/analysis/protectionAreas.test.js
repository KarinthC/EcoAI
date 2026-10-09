// Tests de protectionAreas : rattachement des critères PEF aux aires de
// protection EF 3.1 (santé humaine / écosystèmes / ressources).
import { describe, it, expect } from 'vitest'
import { protectionAreaKey } from '@/components/pipeline/analysis/protectionAreas.js'

describe('protectionAreaKey', () => {
  it('rattache les critères sanitaires à la santé humaine', () => {
    expect(protectionAreaKey('PEF-GWP')).toBe('analysis.protectionArea.humanHealth')
    expect(protectionAreaKey('PEF-PM')).toBe('analysis.protectionArea.humanHealth')
    expect(protectionAreaKey('PEF-CTUh-c')).toBe('analysis.protectionArea.humanHealth')
  })

  it('rattache les critères écosystémiques aux écosystèmes', () => {
    expect(protectionAreaKey('PEF-AP')).toBe('analysis.protectionArea.ecosystems')
    expect(protectionAreaKey('PEF-CTUe')).toBe('analysis.protectionArea.ecosystems')
    expect(protectionAreaKey('PEF-WU')).toBe('analysis.protectionArea.ecosystems')
  })

  it('rattache les critères de ressources aux ressources', () => {
    expect(protectionAreaKey('PEF-ADPf')).toBe('analysis.protectionArea.resources')
    expect(protectionAreaKey('PEF-ADPe')).toBe('analysis.protectionArea.resources')
  })

  it('retourne null pour une clé inconnue', () => {
    expect(protectionAreaKey('PEF-UNKNOWN')).toBeNull()
    expect(protectionAreaKey(undefined)).toBeNull()
  })
})
