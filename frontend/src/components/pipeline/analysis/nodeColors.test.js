// Tests de nodeColors : couleur stable par index de nœud, teintes distinctes
// pour des index consécutifs.
import { describe, it, expect } from 'vitest'
import { nodeColor } from '@/components/pipeline/analysis/nodeColors.js'

describe('nodeColor', () => {
  it('retourne une couleur hexadécimale', () => {
    expect(nodeColor(0)).toMatch(/^#[0-9A-Fa-f]{6}$/)
  })

  it('donne des teintes distinctes pour des index consécutifs', () => {
    expect(nodeColor(0)).not.toBe(nodeColor(1))
    expect(nodeColor(1)).not.toBe(nodeColor(2))
  })

  it('est stable pour un même index', () => {
    expect(nodeColor(3)).toBe(nodeColor(3))
  })

  it('boucle sur la palette au-delà du nombre de teintes', () => {
    expect(nodeColor(12)).toBe(nodeColor(0))
  })
})

