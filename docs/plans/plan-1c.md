# Plan: Phase 1c — Web UI

## Goal
Build a premium, editorial-quality digest UI that feels like something worth opening every day — not another AI dashboard. Mobile-first, content-first, calm and refined.

---

## Design Direction: Editorial Minimalism

**Reference feel:** Apple + The Browser Company + Stripe Docs — confident whitespace, beautiful typography, UI that recedes so content leads.

**What we are NOT building:**
- Generic blue gradient hero
- Dense card grids with colored borders on everything
- Neon accent colors
- SaaS dashboard aesthetic

---

## Design System

### Color Palette
| Token | Value | Usage |
|-------|-------|-------|
| Background | `#F8F9FA` | Page background (warm near-white) |
| Surface | `#FFFFFF` | Cards, header |
| Border | `#E8EAED` | Card borders, dividers |
| Border hover | `#D1D5DB` | Card hover state |
| Text primary | `#0F172A` | Headlines, card titles |
| Text secondary | `#475569` | Narrative body text |
| Text muted | `#94A3B8` | Timestamps, meta info |
| Accent | `#0F172A` | Active chips, refresh button |

### Typography (Inter)
| Element | Size | Weight | Color |
|---------|------|--------|-------|
| Wordmark "Frontier Brief" | `text-xl` | `700` | `#0F172A` |
| Section domain heading | `text-sm` | `600` | `#94A3B8` (uppercase, tracked) |
| Narrative body | `text-[15px]` leading-relaxed | `400` | `#475569` |
| Source link | `text-sm` | `500` | `#0F172A` |
| Chip label | `text-[13px]` | `500` | varies |
| Meta (timestamp) | `text-xs` | `400` | `#94A3B8` |

### Domain Color Pills (muted, tasteful — background + text pairs)
| Domain | Bg | Text |
|--------|----|------|
| Agentic AI | `#EEF2FF` | `#4338CA` |
| New Model Capabilities | `#EFF6FF` | `#1D4ED8` |
| Context Management | `#F0FDFA` | `#0F766E` |
| Token Economics | `#F0FDF4` | `#15803D` |
| Tool Use & Function Calling | `#FFF7ED` | `#C2410C` |
| AI Coding Agents | `#F5F3FF` | `#6D28D9` |
| Reasoning & Planning | `#FFFBEB` | `#B45309` |
| Agent Memory & Persistence | `#FFF1F2` | `#BE123C` |
| Applied AI Engineering | `#F1F5F9` | `#475569` |
| AI Research | `#F8FAFC` | `#334155` |

### Card Design
```
┌─────────────────────────────────────────────┐  ← rounded-2xl, border border-[#E8EAED]
│                                             │     bg-white, p-5, hover: border-[#D1D5DB]
│  [Agentic AI ●]           [Video]           │  ← pill + content-type badge, space-between
│                                             │
│  Narrative body text here. Two to four      │  ← text-[15px] leading-[1.7] text-[#475569]
│  sentences of readable prose that explains  │
│  what happened and why it matters.          │
│                                             │
│  ↗ Source Name                              │  ← text-sm font-medium with arrow icon SVG
└─────────────────────────────────────────────┘
```

### Header
- Sticky, `bg-white/90 backdrop-blur-md`, `border-b border-[#E8EAED]`
- Left: "Frontier Brief" wordmark
- Right: last-fetched time + refresh icon button (not a labeled button)
- Height: 52px

### Filter Chip Row
- Sits below header, `bg-[#F8F9FA]`, `sticky top-[52px]`, `border-b border-[#E8EAED]`
- `overflow-x: auto`, hidden scrollbar
- Chips: `rounded-full px-4 py-1.5 text-[13px] font-medium`
- Inactive: `bg-white border border-[#E8EAED] text-[#475569]`
- Active: `bg-[#0F172A] text-white border-transparent`
- Smooth `transition-colors` on state change

### Page Layout
```
[sticky header]
[sticky chip row]
──────────────────
max-w-[680px] mx-auto px-4 py-6

  AI RESEARCH                 ← section heading: text-xs font-semibold tracking-widest uppercase text-[#94A3B8]
  [DigestCard]
  [DigestCard]

  AGENTIC AI
  [DigestCard]
  [DigestCard]
  [DigestCard]
```
Single column. No grid. Each section separated by `mb-8`. Cards have `gap-3` between them.

---

## Files to Create

| File | Purpose |
|------|---------|
| `frontend/src/components/digest/SourceLink.tsx` | `<a target="_blank" rel="noopener noreferrer">` with external link SVG icon |
| `frontend/src/components/digest/DigestCard.tsx` | Premium card: domain pill + content-type badge + narrative + source link |
| `frontend/src/components/digest/DigestSection.tsx` | Uppercase section heading + card list |
| `frontend/src/components/filters/DomainFilterChips.tsx` | Horizontal scroll chip bar |
| `frontend/src/components/ui/Spinner.tsx` | Minimal SVG spinner, accessible |
| `frontend/src/components/ui/EmptyState.tsx` | Tasteful empty state — not a big sad illustration |

---

## Files to Modify

| File | Change |
|------|--------|
| `frontend/src/app/layout.tsx` | Add Inter font, set `antialiased`, `bg-[#F8F9FA]` on body |
| `frontend/src/app/page.tsx` | Full Client Component: data fetch, filter state, refresh, layout |
| `frontend/src/lib/types.ts` | Remove placeholder comment |
| `frontend/src/lib/api.ts` | Remove placeholder comment |
| `frontend/tailwind.config.ts` | Add `scrollbar-hide` utility if needed |

---

## Implementation Order

1. `layout.tsx` — Inter font, body base styles
2. `Spinner.tsx` — SVG ring spinner, `animate-spin`
3. `EmptyState.tsx` — single line of calm text + subtext
4. `SourceLink.tsx` — anchor with external SVG arrow, `hover:underline`
5. `DigestCard.tsx` — full card with pill, badge, narrative, link
6. `DigestSection.tsx` — section heading + cards
7. `DomainFilterChips.tsx` — chip bar with "All" first
8. `page.tsx` — full page with all state logic

---

## Acceptance Criteria

- [ ] Renders correctly at 375px with no horizontal scroll
- [ ] Header is sticky, frosted glass effect works
- [ ] Chip row is sticky below header, scrolls horizontally on mobile
- [ ] Cards show correct domain pill color per domain
- [ ] Narrative text is legible at 15px on mobile
- [ ] Source links open in new tab, have visible arrow icon
- [ ] Tap targets all ≥ 44×44px (chips, refresh icon, source link)
- [ ] Empty state shown when no items (expected until Phase 1d)
- [ ] Refresh button shows spinner while polling
- [ ] Transition on chip selection is smooth
- [ ] `ecc:react-reviewer` passes
- [ ] `/frontier-ui-check` passes

---

## ECC Skills to Run

| When | Skill |
|------|-------|
| After implementation | `ecc:react-reviewer` |
| After implementation | `/frontier-ui-check` |
