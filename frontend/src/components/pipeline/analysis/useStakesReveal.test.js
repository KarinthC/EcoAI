// Tests de useStakesReveal : phases de l'effet de révélation (fake timers).
import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { defineComponent, h, ref } from 'vue'
import { mount } from '@vue/test-utils'
import {
  useStakesReveal,
  PULSE_DURATION_MS,
  QUOTE_DURATION_MS,
  LEAVE_GRACE_MS,
} from '@/components/pipeline/analysis/useStakesReveal.js'

// Monte un composant minimal qui expose le composable.
function mountReveal(options) {
  let api
  const Comp = defineComponent({
    setup() {
      api = useStakesReveal(options)
      return () => h('div')
    },
  })
  const wrapper = mount(Comp)
  return { wrapper, api }
}

// Force les media queries : survol disponible, animations autorisées.
function mockMedia({ hover = true, reduced = false } = {}) {
  window.matchMedia = vi.fn().mockImplementation((query) => ({
    matches: query.includes('hover: hover')
      ? hover
      : query.includes('prefers-reduced-motion')
        ? reduced
        : false,
    media: query,
    addEventListener: vi.fn(),
    removeEventListener: vi.fn(),
  }))
}

describe('useStakesReveal', () => {
  beforeEach(() => {
    vi.useFakeTimers()
    mockMedia()
  })
  afterEach(() => {
    vi.useRealTimers()
  })

  it('démarre en phase idle', () => {
    const { api } = mountReveal()
    expect(api.phase.value).toBe('idle')
  })

  it('passe en pulsing au survol', () => {
    const { api } = mountReveal()
    api.onEnter()
    expect(api.phase.value).toBe('pulsing')
    expect(api.isPulsing.value).toBe(true)
  })

  it('révèle après la durée de pulsation', () => {
    const { api } = mountReveal()
    api.onEnter()
    vi.advanceTimersByTime(PULSE_DURATION_MS)
    expect(api.phase.value).toBe('revealed')
    expect(api.isRevealed.value).toBe(true)
    expect(api.showQuote.value).toBe(true)
  })

  it('revient en idle après la durée de citation', () => {
    const { api } = mountReveal()
    api.onEnter()
    vi.advanceTimersByTime(PULSE_DURATION_MS + QUOTE_DURATION_MS)
    expect(api.phase.value).toBe('idle')
  })

  it('annule si la souris sort avant la submersion (après le délai de grâce)', () => {
    const { api } = mountReveal()
    api.onEnter()
    vi.advanceTimersByTime(PULSE_DURATION_MS - 1000)
    api.onLeave()
    // L'effet continue pendant le délai de grâce.
    expect(api.phase.value).toBe('pulsing')
    vi.advanceTimersByTime(LEAVE_GRACE_MS)
    expect(api.phase.value).toBe('idle')
    // Le timer de submersion ne doit plus se déclencher.
    vi.advanceTimersByTime(PULSE_DURATION_MS)
    expect(api.phase.value).toBe('idle')
  })

  it('annule l\'annulation si la souris revient pendant le délai de grâce', () => {
    const { api } = mountReveal()
    api.onEnter()
    api.onLeave()
    vi.advanceTimersByTime(LEAVE_GRACE_MS - 100)
    api.onEnter()
    vi.advanceTimersByTime(LEAVE_GRACE_MS)
    expect(api.phase.value).toBe('pulsing')
  })

  it('ne déclenche rien si prefers-reduced-motion', () => {
    mockMedia({ reduced: true })
    const { api } = mountReveal()
    api.onEnter()
    expect(api.phase.value).toBe('idle')
  })

  it('ne déclenche rien sans survol (tactile)', () => {
    mockMedia({ hover: false })
    const { api } = mountReveal()
    api.onEnter()
    expect(api.phase.value).toBe('idle')
  })

  it('respecte une durée de pulsation propre au critère', () => {
    const { api } = mountReveal({ pulseDurationMs: 1000 })
    api.onEnter()
    vi.advanceTimersByTime(999)
    expect(api.phase.value).toBe('pulsing')
    vi.advanceTimersByTime(1)
    expect(api.phase.value).toBe('revealed')
  })

  it('respecte une durée de citation propre au critère', () => {
    const { api } = mountReveal({ pulseDurationMs: 1000, quoteDurationMs: 2000 })
    api.onEnter()
    vi.advanceTimersByTime(1000 + 1999)
    expect(api.phase.value).toBe('revealed')
    vi.advanceTimersByTime(1)
    expect(api.phase.value).toBe('idle')
  })

  it('retombe sur les durées par défaut si elles sont invalides', () => {
    const { api } = mountReveal({ pulseDurationMs: NaN, quoteDurationMs: undefined })
    api.onEnter()
    vi.advanceTimersByTime(PULSE_DURATION_MS - 1)
    expect(api.phase.value).toBe('pulsing')
    vi.advanceTimersByTime(1)
    expect(api.phase.value).toBe('revealed')
    vi.advanceTimersByTime(QUOTE_DURATION_MS)
    expect(api.phase.value).toBe('idle')
  })

  it('applique les durées par défaut (10 s / 30 s) sans option', () => {
    expect(PULSE_DURATION_MS).toBe(10000)
    expect(QUOTE_DURATION_MS).toBe(30000)
  })

  it('accepte des durées réactives (ref) relues à chaque survol', () => {
    const pulse = ref(1000)
    const quote = ref(2000)
    const { api } = mountReveal({ pulseDurationMs: pulse, quoteDurationMs: quote })

    api.onEnter()
    vi.advanceTimersByTime(1000)
    expect(api.phase.value).toBe('revealed')
    vi.advanceTimersByTime(2000)
    expect(api.phase.value).toBe('idle')

    // Le critère change sans remontage : les nouvelles durées s'appliquent.
    pulse.value = 3000
    quote.value = 4000
    api.onEnter()
    vi.advanceTimersByTime(2999)
    expect(api.phase.value).toBe('pulsing')
    vi.advanceTimersByTime(1)
    expect(api.phase.value).toBe('revealed')
    vi.advanceTimersByTime(3999)
    expect(api.phase.value).toBe('revealed')
    vi.advanceTimersByTime(1)
    expect(api.phase.value).toBe('idle')
  })

  it('retombe sur le défaut si la ref devient invalide', () => {
    const pulse = ref(1000)
    const { api } = mountReveal({ pulseDurationMs: pulse })
    pulse.value = undefined
    api.onEnter()
    vi.advanceTimersByTime(PULSE_DURATION_MS - 1)
    expect(api.phase.value).toBe('pulsing')
    vi.advanceTimersByTime(1)
    expect(api.phase.value).toBe('revealed')
  })
})
