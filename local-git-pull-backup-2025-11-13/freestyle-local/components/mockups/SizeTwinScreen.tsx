'use client'

import * as React from 'react'
import { motion, useReducedMotion } from 'framer-motion'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent } from '@/components/ui/card'
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from '@/components/ui/tooltip'
import {
  Avatar,
  AvatarFallback,
  AvatarImage,
} from '@/components/ui/avatar'
import { Skeleton } from '@/components/ui/skeleton'
import { Info, Lock } from 'lucide-react'
import { getMockSizeTwin, type SizeTwinMatch } from '@/lib/mock/sizeTwin'

type Props = {
  match?: SizeTwinMatch
  variant?: 'default' | 'skeleton' | 'private'
}

const confidenceSignals = [
  'Same size in Aritzia dresses',
  'Similar height and measurements',
  'Overlap in saved items',
]

const confidenceVariants = {
  initial: { opacity: 0, y: 8 },
  animate: { opacity: 1, y: 0 },
}

const gridVariants = {
  initial: { opacity: 0, y: 16 },
  animate: { opacity: 1, y: 0 },
}

function cn(...classes: Array<string | undefined | null | false>) {
  return classes.filter(Boolean).join(' ')
}

function getInitials(name?: string) {
  if (!name) return '??'
  return name
    .split(' ')
    .map((part) => part[0])
    .join('')
    .slice(0, 2)
    .toUpperCase()
}

function MatchSkeleton() {
  return (
    <Card className="border-none bg-white/80 shadow-[0_8px_24px_rgba(11,15,20,0.12)] backdrop-blur">
      <CardContent className="flex flex-col gap-6 p-6">
        <div className="flex items-center justify-between gap-3">
          <div className="flex flex-col items-center gap-2">
            <Skeleton className="h-14 w-14 rounded-full" />
            <Skeleton className="h-3 w-12 rounded-full" />
          </div>
          <div className="flex flex-1 flex-col items-center gap-3">
            <Skeleton className="h-8 w-16 rounded-full" />
            <Skeleton className="h-3 w-full rounded-full" />
          </div>
          <div className="flex flex-col items-center gap-2">
            <Skeleton className="h-14 w-14 rounded-full" />
            <Skeleton className="h-3 w-16 rounded-full" />
          </div>
        </div>
        <div className="flex items-center justify-center gap-3">
          <Skeleton className="h-6 w-32 rounded-full" />
          <Skeleton className="h-6 w-28 rounded-full" />
        </div>
        <div className="flex flex-col gap-3">
          <Skeleton className="h-10 w-full rounded-xl" />
          <Skeleton className="h-10 w-full rounded-xl" />
        </div>
      </CardContent>
    </Card>
  )
}

function ClosetSkeleton() {
  return (
    <div className="grid grid-cols-2 gap-4">
      {Array.from({ length: 6 }).map((_, index) => (
        <div
          key={index}
          className="relative overflow-hidden rounded-2xl border border-white/40 bg-white/50 p-4 backdrop-blur"
        >
          <Skeleton className="h-28 w-full rounded-xl" />
          <div className="mt-4 flex flex-col gap-2">
            <Skeleton className="h-3 w-24 rounded-full" />
            <Skeleton className="h-3 w-16 rounded-full" />
          </div>
        </div>
      ))}
    </div>
  )
}

function AvatarStack({
  name,
  avatarUrl,
  label,
}: {
  name: string
  avatarUrl?: string
  label: string
}) {
  return (
    <div className="flex flex-col items-center gap-2 text-center">
      <Avatar className="h-14 w-14 border border-white/60 ring-4 ring-white/50">
        {avatarUrl ? (
          <AvatarImage src={avatarUrl} alt={`${name} avatar`} />
        ) : null}
        <AvatarFallback className="bg-gradient-to-br from-slate-200 to-slate-300 font-medium text-slate-700">
          {getInitials(name)}
        </AvatarFallback>
      </Avatar>
      <span className="text-xs font-semibold uppercase tracking-wide text-slate-600">
        {label}
      </span>
      <span className="text-sm font-medium text-slate-900">{name}</span>
    </div>
  )
}

export default function SizeTwinScreen({
  match,
  variant = 'default',
}: Props) {
  const shouldReduceMotion = useReducedMotion()
  const isSkeleton = variant === 'skeleton'
  const isPrivate = variant === 'private'
  const data = React.useMemo(
    () => match ?? getMockSizeTwin(),
    [match]
  )

  return (
    <div
      data-testid="size-twin-screen"
      className="relative mx-auto flex w-full max-w-[360px] justify-center"
      role="region"
      aria-label="Size Twin screen mockup"
    >
      <div className="relative w-[344px] overflow-hidden rounded-[36px] border border-black/10 bg-gradient-to-br from-[#F7F9FB] via-[#EFF3F6] to-white shadow-[0_32px_80px_rgba(11,15,20,0.18)]">
        <div className="absolute inset-x-12 top-3 h-6 rounded-full bg-black/80" aria-hidden />
        <div className="relative flex min-h-[700px] flex-col gap-6 p-6">
          <header className="flex flex-col gap-2 text-center">
            <h1 className="text-lg font-semibold tracking-tight text-slate-900">
              Meet your Size Twin
            </h1>
            <p className="text-sm text-slate-600">
              People who wear the exact size you do—down to the brand &amp; item.
            </p>
          </header>

          {isSkeleton ? (
            <MatchSkeleton />
          ) : (
            <motion.div
              initial={shouldReduceMotion ? undefined : { opacity: 0, y: 16 }}
              animate={shouldReduceMotion ? undefined : { opacity: 1, y: 0 }}
              transition={
                shouldReduceMotion
                  ? undefined
                  : { duration: 0.45, ease: 'easeOut' }
              }
            >
              <Card className="border-none bg-white/90 shadow-[0_8px_24px_rgba(11,15,20,0.12)] backdrop-blur">
                <CardContent className="flex flex-col gap-6 p-6">
                  <div className="flex items-start justify-between gap-3">
                    <AvatarStack name="You" avatarUrl={data.you.avatarUrl} label="You" />
                    <div className="flex flex-1 flex-col items-center gap-3">
                      <Badge
                        className="rounded-full bg-[#00A3A3] px-4 py-1 text-sm font-semibold text-white shadow-[0_8px_16px_rgba(0,163,163,0.28)]"
                        aria-label={`Shared size ${data.sizeBadge}`}
                      >
                        {data.sizeBadge}
                      </Badge>
                      <div className="flex items-center gap-2 rounded-full bg-[#E0F7F7] px-4 py-2 text-xs font-medium text-[#0B0F14]">
                        <span className="truncate">
                          {data.brandItem.brand}
                          {data.brandItem.line
                            ? ` • ${data.brandItem.line}`
                            : ''}
                          {' • '}
                          {data.brandItem.item}
                        </span>
                        <span className="rounded-full bg-white/80 px-2 py-0.5 text-xs font-semibold">
                          {data.brandItem.sizeLabel}
                        </span>
                      </div>
                    </div>
                    <AvatarStack
                      name={data.twin.name}
                      avatarUrl={data.twin.avatarUrl}
                      label="Size Twin"
                    />
                  </div>

                  <div className="flex flex-wrap items-center justify-center gap-2">
                    <MetaChip>{`${data.stats.overlappingBrands} overlapping brands`}</MetaChip>
                    <MetaChip>{`${data.stats.fitMatchPct}% fit match`}</MetaChip>
                  </div>

                  <div className="flex flex-col gap-3 md:flex-row">
                    <Button
                      type="button"
                      className="h-11 flex-1 rounded-xl bg-[#00A3A3] text-base font-semibold text-white transition hover:bg-[#009090] focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[#00A3A3]"
                      disabled={isPrivate}
                    >
                      See her closet
                    </Button>
                    <Button
                      type="button"
                      variant="ghost"
                      className="h-11 flex-1 rounded-xl border border-[#CCD9E3]/70 bg-white text-base font-semibold text-[#0B0F14] transition hover:border-[#00A3A3]/50 hover:bg-[#E0F7F7]/50 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[#00A3A3]"
                    >
                      Follow
                    </Button>
                  </div>

                  <p className="text-center text-xs text-slate-500">
                    Only share what you choose. You control your visibility.
                  </p>
                </CardContent>
              </Card>
            </motion.div>
          )}

          <section
            className="relative"
            aria-label="Closet preview"
          >
            {isSkeleton ? (
              <ClosetSkeleton />
            ) : (
              <motion.div
                className="grid grid-cols-2 gap-4"
                variants={gridVariants}
                initial={shouldReduceMotion ? undefined : 'initial'}
                animate={shouldReduceMotion ? undefined : 'animate'}
                transition={
                  shouldReduceMotion
                    ? undefined
                    : { staggerChildren: 0.05, delayChildren: 0.1 }
                }
              >
                {data.closetPreview.map((item, index) => (
                  <motion.button
                    key={item.id}
                    type="button"
                    aria-label={`${item.brand} ${item.item} in size ${item.sizeLabel}`}
                    className={cn(
                      'group relative flex h-full flex-col overflow-hidden rounded-2xl border border-white/80 bg-white/90 p-3 text-left shadow-[0_8px_20px_rgba(11,15,20,0.08)] transition focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[#00A3A3]',
                      isPrivate ? 'opacity-60' : 'opacity-100'
                    )}
                    variants={shouldReduceMotion ? undefined : confidenceVariants}
                    transition={
                      shouldReduceMotion
                        ? undefined
                        : { duration: 0.35, delay: index * 0.05, ease: 'easeOut' }
                    }
                    whileHover={
                      shouldReduceMotion || isPrivate
                        ? undefined
                        : { y: -4, boxShadow: '0 24px 40px rgba(11,15,20,.12)' }
                    }
                    whileFocus={
                      shouldReduceMotion || isPrivate
                        ? undefined
                        : { y: -4, boxShadow: '0 24px 40px rgba(11,15,20,.12)' }
                    }
                  >
                    <div className="relative aspect-[4/5] overflow-hidden rounded-xl bg-slate-100">
                      <img
                        src={item.imageUrl}
                        alt={`${item.brand} ${item.item}`}
                        className="h-full w-full object-cover"
                        loading="lazy"
                      />
                      <Badge className="absolute left-3 top-3 rounded-full bg-white/90 px-3 py-1 text-xs font-semibold text-slate-800">
                        {item.sizeLabel}
                      </Badge>
                    </div>
                    <div className="mt-3 flex flex-col gap-1">
                      <span className="text-xs font-semibold uppercase tracking-wide text-slate-500">
                        {item.brand}
                      </span>
                      <span className="line-clamp-2 text-sm font-medium text-slate-900">
                        {item.item}
                      </span>
                    </div>
                  </motion.button>
                ))}
              </motion.div>
            )}

            {isPrivate ? (
              <div className="absolute inset-0 flex flex-col items-center justify-center gap-3 rounded-2xl bg-slate-900/70 text-center text-white backdrop-blur">
                <Lock className="h-8 w-8" aria-hidden="true" />
                <div className="space-y-1">
                  <p className="text-sm font-semibold">Private until you follow each other.</p>
                  <p className="text-xs text-white/80">
                    Follow to request access to their closet.
                  </p>
                </div>
              </div>
            ) : null}
          </section>

          <TooltipProvider>
            <motion.div
              className="flex items-center justify-center gap-3 rounded-2xl border border-[#CCD9E3]/70 bg-white/90 px-4 py-3 shadow-[0_8px_24px_rgba(11,15,20,0.08)]"
              initial={shouldReduceMotion ? undefined : { opacity: 0, y: 12 }}
              animate={shouldReduceMotion ? undefined : { opacity: 1, y: 0 }}
              transition={
                shouldReduceMotion
                  ? undefined
                  : { duration: 0.45, ease: 'easeOut', delay: 0.2 }
              }
            >
              <Tooltip>
                <TooltipTrigger asChild>
                  <button
                    type="button"
                    className="flex h-9 w-9 items-center justify-center rounded-full border border-[#00A3A3]/30 bg-[#E0F7F7]/80 text-[#006C6C] shadow-inner focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[#00A3A3]"
                    aria-label="Why this match?"
                  >
                    <Info className="h-4 w-4" aria-hidden="true" />
                  </button>
                </TooltipTrigger>
                <TooltipContent
                  side="top"
                  align="center"
                  className="w-64 rounded-2xl border border-[#CCD9E3]/70 bg-white/95 p-4 text-left text-sm text-slate-700 shadow-[0_16px_40px_rgba(11,15,20,0.16)]"
                >
                  <h3 className="mb-2 text-sm font-semibold text-slate-900">
                    Why this match?
                  </h3>
                  <ul className="space-y-1 text-sm">
                    {confidenceSignals.map((signal) => (
                      <li key={signal} className="flex items-start gap-2">
                        <span className="mt-1 h-1.5 w-1.5 rounded-full bg-[#00A3A3]" />
                        <span>{signal}</span>
                      </li>
                    ))}
                  </ul>
                </TooltipContent>
              </Tooltip>
              <div className="flex flex-col gap-1 text-center">
                <span className="text-sm font-semibold text-slate-900">
                  Confidence Meter
                </span>
                <span className="text-xs text-slate-500">
                  Powered by real size twins
                </span>
              </div>
            </motion.div>
          </TooltipProvider>
        </div>
      </div>
    </div>
  )
}

function MetaChip({ children }: { children: React.ReactNode }) {
  return (
    <span className="rounded-full border border-[#CCD9E3]/60 bg-white px-3 py-1 text-xs font-medium uppercase tracking-wide text-slate-600">
      {children}
    </span>
  )
}
