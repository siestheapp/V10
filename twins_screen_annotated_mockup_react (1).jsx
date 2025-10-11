import React from "react";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { ChevronRight, ChevronLeft, Heart } from "lucide-react";

// ===== Test IDs (exported for easy UI tests) =====
export const TEST_IDS = {
  header: "size-twins-header",
  tryOnCopy: "tryon-subcopy",
  exactTag: "tag-exact-match",
  alsoTag: "tag-also-wears",
  shopItemBtn: "btn-shop-item",
  seeMoreFromUserBtn: "btn-see-more",
  stickyCta: "sticky-cta",
  commentTeaser: "comment-teaser",
};

// Simple pill tag
const Tag = ({ children }: { children: React.ReactNode }) => (
  <span className="inline-flex items-center rounded-full px-3 py-1 text-xs font-semibold bg-teal-100 text-teal-700">
    {children}
  </span>
);

// Placeholder image block
const Img = ({ label }: { label: string }) => (
  <div className="relative w-full aspect-[4/5] rounded-2xl bg-gray-200 flex items-center justify-center text-gray-500">
    <span className="text-sm">{label}</span>
  </div>
);

// Carousel dot indicator (static for mockup)
const Dots = () => (
  <div className="flex items-center gap-2 mt-3 justify-center">
    <span className="w-2 h-2 rounded-full bg-gray-300" />
    <span className="w-4 h-2 rounded-full bg-teal-500" />
    <span className="w-2 h-2 rounded-full bg-gray-300" />
  </div>
);

// Comment teaser row (tappable to open the full thread)
const CommentTeaser = ({
  count,
  qa,
}: {
  count: number;
  qa: { q: string; a?: string };
}) => (
  <button
    className="w-full text-left mt-3 rounded-2xl border bg-white px-3 py-2 hover:bg-gray-50 transition"
    data-testid={TEST_IDS.commentTeaser}
    aria-label={`View ${count} comments`}
  >
    <div className="text-xs text-gray-500 mb-1">Comments · {count}</div>
    <div className="text-sm">
      <span className="font-semibold">Q:</span> {qa.q}
      {qa.a ? (
        <>
          <span className="mx-2 text-gray-400">·</span>
          <span className="font-semibold">A:</span> {qa.a}
        </>
      ) : null}
    </div>
    {/* Use &gt; to avoid JSX parsing the ">" as markup */}
    <div className="text-xs text-teal-700 mt-1">See full thread &gt;</div>
  </button>
);

export default function TwinsMock() {
  return (
    <div className="w-full min-h-screen bg-white text-gray-900 flex items-center justify-center py-6">
      {/* Phone frame */}
      <div className="w-[390px] rounded-[44px] border border-gray-200 shadow-xl overflow-hidden">
        {/* Top bar */}
        <div className="px-5 pt-6 pb-4 bg-white border-b">
          <div className="text-center mb-2">
            <span className="text-emerald-500 font-extrabold text-2xl">freestyle</span>
          </div>
          <h1 className="text-2xl font-bold" data-testid={TEST_IDS.header}>Size Twins</h1>
          <p className="text-sm text-gray-500 mt-1" data-testid={TEST_IDS.tryOnCopy}>
            A <span className="font-semibold">Try-On</span> is a garment owned by one of your size twins. Think of your <span className="font-semibold">Try-Ons</span> as clothes you've tried on by proxy.
          </p>

          {/* Selected piece + size */}
          <div className="mt-4 grid grid-cols-[1fr_auto] items-center gap-2">
            <button className="w-full text-left truncate rounded-xl border px-3 py-2">
              Anthropologie - Somerset Maxi Dress
            </button>
            <button className="rounded-xl border px-3 py-2">Size XS</button>
          </div>

          {/* Selected item thumbnail row */}
          <div className="mt-3 flex items-center gap-3 text-sm">
            <div className="w-10 h-10 rounded-lg bg-gray-200" />
            <span className="text-gray-600">Selected piece</span>
          </div>
        </div>

        {/* Gallery area */}
        <div className="p-4 bg-gray-50">
          {/* Card 1: Exact Match Anchor */}
          <Card className="rounded-3xl overflow-hidden">
            <CardContent className="p-0">
              {/* Header row */}
              <div className="flex items-center justify-between px-4 pt-4">
                <div className="flex items-center gap-2">
                  <div className="w-8 h-8 rounded-full bg-gray-300" />
                  <div className="text-sm font-semibold">ellaa76</div>
                </div>
                <Tag><span data-testid={TEST_IDS.exactTag}>Exact match in Selected Piece</span></Tag>
              </div>

              {/* Image */}
              <div className="relative mt-3 px-4">
                <Img label="Photo: wearing the Somerset Maxi (XS)" />
                {/* Carousel controls (non-functional for mock) */}
                <button className="absolute left-6 top-1/2 -translate-y-1/2 grid place-items-center w-10 h-10 rounded-full bg-white/80 shadow">
                  <ChevronLeft size={18} />
                </button>
                <button className="absolute right-6 top-1/2 -translate-y-1/2 grid place-items-center w-10 h-10 rounded-full bg-white/80 shadow">
                  <ChevronRight size={18} />
                </button>
                {/* Quick actions */}
                <button className="absolute right-8 bottom-8 grid place-items-center w-10 h-10 rounded-full bg-white/90 shadow">
                  <Heart size={18} />
                </button>
              </div>

              {/* Caption + CTA */}
              <div className="px-4 pb-4 pt-3">
                <p className="text-sm"><span className="font-semibold">ellaa76</span> - wears <span className="font-semibold">Size XS</span> in this dress.</p>
                <p className="text-sm text-gray-500 mt-1">Swipe to see what else she wears.</p>
                <div className="flex gap-2 mt-3">
                  <Button className="rounded-xl" data-testid={TEST_IDS.shopItemBtn}>Shop this item</Button>
                  <Button variant="outline" className="rounded-xl" data-testid={TEST_IDS.seeMoreFromUserBtn}>See more from ellaa76</Button>
                </div>
                <Dots />
                {/* Comment teaser */}
                <CommentTeaser count={12} qa={{ q: "Is this petite or regular?", a: "Regular!" }} />
              </div>
            </CardContent>
          </Card>

          {/* Spacer */}
          <div className="h-4" />

          {/* Card 2: Discovery Slide (Other product) */}
          <Card className="rounded-3xl overflow-hidden">
            <CardContent className="p-0">
              <div className="flex items-center justify-between px-4 pt-4">
                <div className="flex items-center gap-2">
                  <div className="w-8 h-8 rounded-full bg-gray-300" />
                  <div className="text-sm font-semibold">ellaa76</div>
                </div>
                <Tag><span data-testid={TEST_IDS.alsoTag}>Also wears Size XS in...</span></Tag>
              </div>

              <div className="relative mt-3 px-4">
                <Img label="Photo: Marigold Blazer (XS)" />
                <div className="absolute left-6 bottom-8 rounded-full bg-white/90 px-3 py-1 text-xs font-semibold shadow">
                  Anthropologie - Marigold Blazer
                </div>
                <button className="absolute right-6 top-1/2 -translate-y-1/2 grid place-items-center w-10 h-10 rounded-full bg-white/80 shadow">
                  <ChevronRight size={18} />
                </button>
              </div>

              <div className="px-4 pb-4 pt-3">
                <div className="flex gap-2">
                  <Button className="rounded-xl">Shop this look</Button>
                  <Button variant="outline" className="rounded-xl">View details</Button>
                </div>
                <p className="text-xs text-gray-500 mt-2">These are items this twin wears in your size - great fit candidates for you.</p>
              </div>
            </CardContent>
          </Card>

          {/* Sticky CTA mock */}
          <div className="sticky bottom-4 mt-4 bg-white rounded-2xl border p-3 shadow-sm flex items-center justify-between" data-testid={TEST_IDS.stickyCta}>
            <span className="text-sm font-semibold">Explore ellaa76's XS wardrobe</span>
            <Button className="rounded-xl">View all -&gt;</Button>
          </div>
        </div>

        {/* Bottom nav */}
        <div className="grid grid-cols-4 text-center text-sm py-3 border-t bg-white">
          <div className="opacity-60">Find</div>
          <div className="opacity-60">Feed</div>
          <div className="font-semibold text-emerald-600">Twins</div>
          <div className="opacity-60">Profile</div>
        </div>
      </div>
    </div>
  );
}

/* -------------------------------------------------
   Minimal test plan (add these to your Jest/RTL suite)
   -------------------------------------------------
   - Renders header "Size Twins" (getByTestId(TEST_IDS.header)).
   - Shows Try-On definition copy (getByTestId(TEST_IDS.tryOnCopy)).
   - Contains Exact Match tag (getByTestId(TEST_IDS.exactTag)).
   - Contains Also Wears tag (getByTestId(TEST_IDS.alsoTag)).
   - "Shop this item" and "See more from" buttons are present (by test ids).
   - Sticky CTA is present (getByTestId(TEST_IDS.stickyCta)).
   - Comment teaser renders (getByTestId(TEST_IDS.commentTeaser)).
*/
