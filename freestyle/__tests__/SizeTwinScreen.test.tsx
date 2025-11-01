import '@testing-library/jest-dom'
import { render, screen } from '@testing-library/react'
import SizeTwinScreen from '@/components/mockups/SizeTwinScreen'
import { getMockSizeTwin } from '@/lib/mock/sizeTwin'

beforeAll(() => {
  Object.defineProperty(window, 'matchMedia', {
    writable: true,
    value: (query: string) => ({
      matches: false,
      media: query,
      onchange: null,
      addListener: () => {},
      removeListener: () => {},
      addEventListener: () => {},
      removeEventListener: () => {},
      dispatchEvent: () => false,
    }),
  })
})

describe('SizeTwinScreen', () => {
  it('renders default size twin content', () => {
    const match = getMockSizeTwin()
    render(<SizeTwinScreen match={match} />)

    expect(
      screen.getByRole('heading', { name: /meet your size twin/i })
    ).toBeInTheDocument()

    expect(screen.getByText(/8 overlapping brands/i)).toBeInTheDocument()
    expect(screen.getByText(/92% fit match/i)).toBeInTheDocument()
    expect(screen.getAllByRole('button', { name: /closet/i })).toHaveLength(1)
    expect(
      screen.getByRole('button', { name: /follow/i })
    ).toBeInTheDocument()
    expect(screen.getAllByLabelText(/in size/i)).toHaveLength(6)
  })

  it('renders private variant with lock overlay', () => {
    const match = getMockSizeTwin()
    render(<SizeTwinScreen match={match} variant="private" />)

    const primaryCta = screen.getByRole('button', { name: /see her closet/i })
    expect(primaryCta).toBeDisabled()
    expect(screen.getByText(/private until you follow each other/i)).toBeInTheDocument()
  })
})
