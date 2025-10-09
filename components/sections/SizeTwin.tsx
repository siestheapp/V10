'use client'

import * as React from 'react'
import Image from 'next/image'
import { motion, useReducedMotion } from 'framer-motion'
import { Button } from '@/components/ui/button'
import SizeTwinScreen from '@/components/mockups/SizeTwinScreen'
import { getMockSizeTwin } from '@/lib/mock/sizeTwin'
import { Check } from 'lucide-react'

type SizeTwinSectionProps = {
  renderLive?: boolean
}

const bullets = [
  'Exact-size matches by brand & category',
  'Peek their closet, save looks you’ll actually fit',
  'Confidence meter powered by real-world fit data',
]

export function SizeTwin({ renderLive = false }: SizeTwinSectionProps) {
  const mockMatch = React.useMemo(() => getMockSizeTwin(), [])
  const prefersReducedMotion = useReducedMotion()
  const [isMounted, setIsMounted] = React.useState(false)

  React.useEffect(() => {
    setIsMounted(true)
  }, [])

  const shouldRenderLive = renderLive && isMounted && !prefersReducedMotion

  return (
    <section
      id="size-twin"
      aria-labelledby="size-twin-heading"
      className="relative isolate overflow-hidden bg-[#F7F9FB]"
    >
      <div className="mx-auto grid w-full max-w-6xl gap-16 px-6 py-24 lg:grid-cols-[1.1fr,0.9fr] lg:items-center lg:px-12 xl:px-16">
        <motion.div
          initial={{ opacity: 0, y: 12 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true, amount: 0.4 }}
          transition={{ duration: 0.5, ease: 'easeOut' }}
          className="space-y-10"
        >
          <div className="space-y-4">
            <p className="inline-flex items-center rounded-full border border-[#CCD9E3]/60 bg-white px-3 py-1 text-xs font-semibold uppercase tracking-[0.24em] text-[#2A3642]">
              Social Fit
            </p>
            <h2
              id="size-twin-heading"
              className="max-w-xl text-4xl font-semibold tracking-tight text-[#0B0F14] sm:text-5xl"
            >
              Shop with your Size Twin
            </h2>
            <p className="max-w-xl text-lg text-[#2A3642]">
              Freestyle matches you with real people who wear your size in your favorite brands—so you can see what fits before you buy.
            </p>
          </div>

          <ul className="space-y-4 text-base text-[#2A3642]">
            {bullets.map((bullet) => (
              <li key={bullet} className="flex items-start gap-3">
                <span className="mt-1 flex h-6 w-6 items-center justify-center rounded-full bg-[#E0F7F7]">
                  <Check className="h-4 w-4 text-[#00A3A3]" aria-hidden="true" />
                </span>
                <span>{bullet}</span>
              </li>
            ))}
          </ul>

          <Button
            type="button"
            className="h-12 rounded-xl bg-[#00A3A3] px-8 text-base font-semibold text-white shadow-[0_16px_40px_rgba(0,163,163,0.32)] transition hover:bg-[#009090] focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[#00A3A3]"
            asChild
          >
            <a href="#waitlist">Join the waitlist</a>
          </Button>
        </motion.div>

        <div className="relative flex justify-center">
          <div className="absolute -inset-10 rounded-[48px] bg-gradient-to-br from-[#A6FFCB]/40 via-transparent to-[#7FE1FF]/30 blur-3xl" aria-hidden />
          <div className="relative">
            {shouldRenderLive ? (
              <SizeTwinScreen match={mockMatch} />
            ) : (
              <Image
                src="/mockups/social-size-twin.png"
                alt="Freestyle size twin screen mockup"
                width={668}
                height={1284}
                className="w-full max-w-[360px] rounded-[36px] shadow-[0_32px_80px_rgba(11,15,20,0.18)]"
                priority
              />
            )}
          </div>
        </div>
      </div>
    </section>
  )
}

export default SizeTwin
