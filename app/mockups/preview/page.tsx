import { Metadata } from 'next'
import SizeTwinScreen from '@/components/mockups/SizeTwinScreen'
import { getMockSizeTwin } from '@/lib/mock/sizeTwin'

export const metadata: Metadata = {
  title: 'Freestyle Mockup Preview',
  description: 'Preview Freestyle marketing mockups for export.',
}

type PreviewPageProps = {
  searchParams?: { screen?: string; variant?: 'default' | 'skeleton' | 'private' }
}

export default function MockupsPreview({ searchParams }: PreviewPageProps) {
  const screenKey = searchParams?.screen ?? 'size-twin'
  const variant = searchParams?.variant ?? 'default'

  return (
    <main className="flex min-h-screen items-center justify-center bg-[#0B0F14] p-12">
      <div className="flex h-[1398px] w-[645px] items-center justify-center rounded-[48px] bg-[#121A22] shadow-[0_40px_120px_rgba(0,0,0,0.35)]">
        {screenKey === 'size-twin' ? (
          <SizeTwinScreen match={getMockSizeTwin()} variant={variant} />
        ) : (
          <div className="text-white">Unknown mockup: {screenKey}</div>
        )}
      </div>
    </main>
  )
}
