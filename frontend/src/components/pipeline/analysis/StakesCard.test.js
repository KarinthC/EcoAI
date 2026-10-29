// Tests de StakesCard : carte « Enjeux » avec image fondue et effet de
// révélation (pulsation -> submersion -> citation).
import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { mount } from '@vue/test-utils'
import StakesCard from '@/components/pipeline/analysis/StakesCard.vue'
import {
  LEAVE_GRACE_MS,
  PULSE_DURATION_MS,
  QUOTE_DURATION_MS,
} from '@/components/pipeline/analysis/useStakesReveal.js'

// Durées de révélation du critère mocké (cf. mock de stakesImages ci-dessous).
const MOCK_PULSE_MS = 1000
const MOCK_QUOTE_MS = 2000
// Second critère illustré, avec des durées différentes et sans `reveal`.
const OTHER_PULSE_MS = 3000
const OTHER_QUOTE_MS = 4000

// i18n mocké : on renvoie la clé brute (suffisant pour vérifier le rendu).
vi.mock('vue-i18n', () => ({
  useI18n: () => ({ t: (k) => k, locale: { value: 'fr' } }),
}))

// Images mockées :
//   - PEF-GWP   : image avec durées explicites ;
//   - PEF-ODP   : image avec d'autres durées explicites ;
//   - PEF-AP    : image SANS `reveal` (repli sur les défauts du composable) ;
//   - autres    : aucune image.
vi.mock('@/components/pipeline/analysis/stakesImages.js', () => ({
  stakesImage: (key) => {
    if (key === 'PEF-GWP') {
      return {
        src: 'test.webp',
        focal: { x: 1000, y: 400 },
        focalWide: { x: 0.5, y: 0.25 },
        zoom: 0.5,
        reveal: { pulseMs: 1000, quoteMs: 2000 },
      }
    }
    if (key === 'PEF-ODP') {
      return {
        src: 'other.webp',
        focal: { x: 800, y: 400 },
        focalWide: { x: 1, y: 1 },
        zoom: 0.17,
        reveal: { pulseMs: 3000, quoteMs: 4000 },
      }
    }
    if (key === 'PEF-AP') {
      return { src: 'no-reveal.webp', focal: { x: 100, y: 100 }, zoom: 1 }
    }
    return null
  },
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

  it('conserve les sauts de ligne du texte (rendus par white-space: pre-line)', () => {
    const wrapper = mount(StakesCard, {
      props: { criterionKey: 'PEF-GWP', text: 'Ligne 1\nLigne 2' },
      global,
    })
    // jsdom ne calcule pas white-space : on vérifie que le « \n » est bien
    // présent dans le nœud texte, le rendu visuel étant assuré par le CSS.
    expect(wrapper.find('.stakes-text').element.textContent).toContain('\n')
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
      props: { criterionKey: 'PEF-Epf', text: 'texte' },
      global,
    })
    expect(wrapper.find('img.stakes-image').exists()).toBe(false)
  })

  it('centre le point focal dans la fenêtre via transform (avec zoom)', () => {
    const wrapper = mount(StakesCard, {
      props: { criterionKey: 'PEF-GWP', text: 'texte' },
      global,
    })
    // Fenêtre 240×180, focal (1000, 400), zoom 0.5 :
    // dx = 120 - 1000*0.5 = -380, dy = 90 - 400*0.5 = -110.
    const style = wrapper.find('img.stakes-image').attributes('style')
    expect(style).toContain('translate(-380px, -110px)')
    expect(style).toContain('scale(0.5)')
  })

  it('applique le cadrage large via object-position (focalWide en fraction)', () => {
    const wrapper = mount(StakesCard, {
      props: { criterionKey: 'PEF-GWP', text: 'texte' },
      global,
    })
    const style = wrapper.find('img.stakes-image').attributes('style')
    expect(style).toContain('object-position: 50% 25%')
  })

  it('force le bloc au ratio 19:10 en submersion', async () => {
    const wrapper = mount(StakesCard, {
      props: { criterionKey: 'PEF-GWP', text: 'texte' },
      global,
    })
    await wrapper.find('.stakes-image-zone').trigger('mouseenter')
    vi.advanceTimersByTime(MOCK_PULSE_MS)
    await wrapper.vm.$nextTick()
    expect(wrapper.find('.stakes-card').classes()).toContain('is-revealed')
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
    vi.advanceTimersByTime(MOCK_PULSE_MS)
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
    vi.advanceTimersByTime(MOCK_PULSE_MS)
    await wrapper.vm.$nextTick()
    expect(wrapper.find('.stakes-content').classes()).toContain('is-hidden')
  })

  it('applique la durée de citation propre au critère', async () => {
    const wrapper = mount(StakesCard, {
      props: { criterionKey: 'PEF-GWP', text: 'texte' },
      global,
    })
    await wrapper.find('.stakes-image-zone').trigger('mouseenter')
    vi.advanceTimersByTime(MOCK_PULSE_MS + MOCK_QUOTE_MS - 1)
    await wrapper.vm.$nextTick()
    expect(wrapper.find('.stakes-card').classes()).toContain('is-revealed')
    vi.advanceTimersByTime(1)
    await wrapper.vm.$nextTick()
    expect(wrapper.find('.stakes-card').classes()).not.toContain('is-revealed')
  })

  it('utilise des durées différentes selon le critère', async () => {
    const wrapper = mount(StakesCard, {
      props: { criterionKey: 'PEF-ODP', text: 'texte' },
      global,
    })
    await wrapper.find('.stakes-image-zone').trigger('mouseenter')
    // La durée de PEF-GWP (1000 ms) ne suffit pas pour PEF-ODP (3000 ms).
    vi.advanceTimersByTime(MOCK_PULSE_MS)
    await wrapper.vm.$nextTick()
    expect(wrapper.find('.stakes-card').classes()).not.toContain('is-revealed')
    vi.advanceTimersByTime(OTHER_PULSE_MS - MOCK_PULSE_MS)
    await wrapper.vm.$nextTick()
    expect(wrapper.find('.stakes-card').classes()).toContain('is-revealed')
    // La citation de PEF-ODP dure 4000 ms, pas 2000 ms.
    vi.advanceTimersByTime(OTHER_QUOTE_MS - 1)
    await wrapper.vm.$nextTick()
    expect(wrapper.find('.stakes-card').classes()).toContain('is-revealed')
    vi.advanceTimersByTime(1)
    await wrapper.vm.$nextTick()
    expect(wrapper.find('.stakes-card').classes()).not.toContain('is-revealed')
  })

  it('retombe sur les durées par défaut (10 s / 30 s) sans `reveal`', async () => {
    const wrapper = mount(StakesCard, {
      props: { criterionKey: 'PEF-AP', text: 'texte' },
      global,
    })
    await wrapper.find('.stakes-image-zone').trigger('mouseenter')
    vi.advanceTimersByTime(PULSE_DURATION_MS - 1)
    await wrapper.vm.$nextTick()
    expect(wrapper.find('.stakes-card').classes()).not.toContain('is-revealed')
    vi.advanceTimersByTime(1)
    await wrapper.vm.$nextTick()
    expect(wrapper.find('.stakes-card').classes()).toContain('is-revealed')
    vi.advanceTimersByTime(QUOTE_DURATION_MS - 1)
    await wrapper.vm.$nextTick()
    expect(wrapper.find('.stakes-card').classes()).toContain('is-revealed')
    vi.advanceTimersByTime(1)
    await wrapper.vm.$nextTick()
    expect(wrapper.find('.stakes-card').classes()).not.toContain('is-revealed')
  })

  it('relit les durées quand le critère change sans remontage', async () => {
    const wrapper = mount(StakesCard, {
      props: { criterionKey: 'PEF-GWP', text: 'texte' },
      global,
    })
    await wrapper.find('.stakes-image-zone').trigger('mouseenter')
    vi.advanceTimersByTime(MOCK_PULSE_MS + MOCK_QUOTE_MS)
    await wrapper.vm.$nextTick()
    expect(wrapper.find('.stakes-card').classes()).not.toContain('is-revealed')

    // Même instance, nouveau critère : les durées doivent suivre.
    await wrapper.setProps({ criterionKey: 'PEF-ODP' })
    await wrapper.find('.stakes-image-zone').trigger('mouseenter')
    vi.advanceTimersByTime(OTHER_PULSE_MS - 1)
    await wrapper.vm.$nextTick()
    expect(wrapper.find('.stakes-card').classes()).not.toContain('is-revealed')
    vi.advanceTimersByTime(1)
    await wrapper.vm.$nextTick()
    expect(wrapper.find('.stakes-card').classes()).toContain('is-revealed')
  })
})
