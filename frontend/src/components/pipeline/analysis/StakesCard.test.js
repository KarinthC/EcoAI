// Tests de StakesCard : carte « Enjeux » avec image fondue et effet de
// révélation (pulsation -> submersion -> citation).
import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { mount } from '@vue/test-utils'
import StakesCard from '@/components/pipeline/analysis/StakesCard.vue'
import {
  PULSE_DURATION_MS,
  LEAVE_GRACE_MS,
} from '@/components/pipeline/analysis/useStakesReveal.js'

// i18n mocké : on renvoie la clé brute (suffisant pour vérifier le rendu).
vi.mock('vue-i18n', () => ({
  useI18n: () => ({ t: (k) => k, locale: { value: 'fr' } }),
}))

// `$t` est utilisé dans le template : on le fournit via les globals de montage.
const global = { mocks: { $t: (k) => k } }

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

describe('StakesCard', () => {
  beforeEach(() => {
    vi.useFakeTimers()
    mockMedia()
  })
  afterEach(() => {
    vi.useRealTimers()
  })

  it('affiche le texte passé en prop', () => {
    const wrapper = mount(StakesCard, {
      props: { criterionKey: 'PEF-GWP', text: 'Un paragraphe sur le climat.' },
      global,
    })
    expect(wrapper.text()).toContain('Un paragraphe sur le climat.')
  })

  it('affiche une image pour un critère qui en a une', () => {
    const wrapper = mount(StakesCard, {
      props: { criterionKey: 'PEF-GWP', text: 'texte' },
      global,
    })
    expect(wrapper.find('img.stakes-image').exists()).toBe(true)
  })

  it("n'affiche pas d'image pour un critère sans illustration", () => {
    const wrapper = mount(StakesCard, {
      props: { criterionKey: 'PEF-ODP', text: 'texte' },
      global,
    })
    expect(wrapper.find('img.stakes-image').exists()).toBe(false)
  })

  it('pulse au survol de la zone image', async () => {
    const wrapper = mount(StakesCard, {
      props: { criterionKey: 'PEF-GWP', text: 'texte' },
      global,
    })
    await wrapper.find('.stakes-image-zone').trigger('mouseenter')
    expect(wrapper.find('.stakes-image-zone').classes()).toContain('is-pulsing')
  })

  it('submerge le bloc après la durée de pulsation', async () => {
    const wrapper = mount(StakesCard, {
      props: { criterionKey: 'PEF-GWP', text: 'texte' },
      global,
    })
    await wrapper.find('.stakes-image-zone').trigger('mouseenter')
    vi.advanceTimersByTime(PULSE_DURATION_MS)
    await wrapper.vm.$nextTick()
    expect(wrapper.find('.stakes-card').classes()).toContain('is-revealed')
  })

  it('annule la pulsation si la souris sort avant la submersion', async () => {
    const wrapper = mount(StakesCard, {
      props: { criterionKey: 'PEF-GWP', text: 'texte' },
      global,
    })
    const zone = wrapper.find('.stakes-image-zone')
    await zone.trigger('mouseenter')
    await zone.trigger('mouseleave')
    // L'effet persiste pendant le délai de grâce.
    expect(wrapper.find('.stakes-image-zone').classes()).toContain('is-pulsing')
    vi.advanceTimersByTime(LEAVE_GRACE_MS)
    await wrapper.vm.$nextTick()
    expect(wrapper.find('.stakes-image-zone').classes()).not.toContain('is-pulsing')
    expect(wrapper.find('.stakes-card').classes()).not.toContain('is-revealed')
  })

  it('masque le contenu quand l\'image submerge', async () => {
    const wrapper = mount(StakesCard, {
      props: { criterionKey: 'PEF-GWP', text: 'texte' },
      global,
    })
    await wrapper.find('.stakes-image-zone').trigger('mouseenter')
    vi.advanceTimersByTime(PULSE_DURATION_MS)
    await wrapper.vm.$nextTick()
    expect(wrapper.find('.stakes-content').classes()).toContain('is-hidden')
  })
})
