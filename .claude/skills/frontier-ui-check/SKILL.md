# /frontier-ui-check

**When to invoke:** After any frontend change — components, layouts, styles, or new pages. Mobile-first is non-negotiable; this skill enforces it.

---

## What This Skill Does

Audits the Frontier Brief UI against mobile-first requirements and general usability standards. Catches layout and interaction issues before they reach the user.

---

## Mobile-First Baseline

The primary user is reading Frontier Brief on their phone while traveling. The baseline viewport is **375px wide** (iPhone SE). Everything must work perfectly at this size before considering larger screens.

---

## Steps

### 1. Identify What Changed
List the components, pages, or layouts that were modified in this session.

### 2. Static Code Review — Mobile

Read the changed CSS / Tailwind classes. Check:

**Layout:**
- [ ] No fixed pixel widths on containers — use `w-full`, `max-w-*`, or `%`
- [ ] No element causes horizontal scroll at 375px (`overflow-x: hidden` on body is a band-aid — fix the root cause)
- [ ] Flexbox/grid with `gap` used for spacing — not hardcoded margins that collapse
- [ ] Text wraps correctly — no overflow-hidden that truncates readable content

**Filter Chips (Domain Filter Bar):**
- [ ] Filter chips are in a horizontal scroll container on mobile (`overflow-x: auto`, `flex-nowrap`)
- [ ] The active chip is visually distinct (color, weight, or border change)
- [ ] Tapping a chip filters the digest immediately (no page reload)
- [ ] All chips are visible and scrollable — not clipped

**Digest Cards:**
- [ ] Card width is full-width on mobile, constrained on desktop
- [ ] Source name and link are visible on the card without scrolling
- [ ] The "Source" link / button has a tap target of at least 44×44px
- [ ] Card text is readable without zooming (minimum 16px body text)
- [ ] Cards stack vertically on mobile — no side-by-side layout at 375px

**Typography:**
- [ ] Body text: minimum 16px (1rem)
- [ ] Heading text: appropriately sized — not so large it dominates the card
- [ ] Line height: at least 1.5 for body text
- [ ] No `white-space: nowrap` on long strings that would overflow

**Interactive Elements:**
- [ ] All buttons and links have visible focus states (`:focus-visible`)
- [ ] Tap targets are at least 44×44px (check padding, not just font size)
- [ ] No hover-only interactions — everything tappable must work without hover

### 3. Responsive Breakpoints
- [ ] Base (mobile) styles written first, then `md:` and `lg:` overrides
- [ ] Nothing in the mobile layout is hidden with `hidden md:block` that a phone user needs

### 4. Browser / DevTools Check (if available)
If Chrome DevTools (via MCP chrome-devtools tools) is available:
- Open the frontend at `localhost:3000`
- Use device emulation at 375×812 (iPhone SE)
- Take a screenshot and review it
- Check the console for errors
- Scroll the full page and confirm no layout breaks

If DevTools is not available, perform a thorough static review and note that live testing is needed.

### 5. Dark Mode Check
- [ ] The UI is readable in both light and dark mode
- [ ] Source link color has sufficient contrast in both modes
- [ ] Filter chip active state is distinct in both modes
- [ ] Card backgrounds and text have correct contrast in both modes

### 6. Accessibility Spot Check
- [ ] All images have `alt` text
- [ ] Interactive elements are reachable via keyboard Tab
- [ ] Filter chips have accessible labels (not just visual icons)
- [ ] Source links have meaningful link text (not "click here" or bare URLs)

### 7. Report
```
UI Check Report
===============
Viewport tested: 375px (mobile) + 1280px (desktop)
Date: [current date]

Layout: PASS/FAIL
Filter chips: PASS/FAIL
Digest cards: PASS/FAIL
Typography: PASS/FAIL
Tap targets: PASS/FAIL
Dark mode: PASS/FAIL
Accessibility: PASS/FAIL

Blockers (must fix before this is done):
- [list]

Suggestions (non-blocking):
- [list]
```

Present the report. Ask: "Any of these blockers need immediate fixing, or would you like me to address them now?"

---

## Related ECC Skills
- `ecc:react-reviewer` — Full React/Next.js code review (run this too, not just the UI check)
- `ecc:a11y-architect` — Deep WCAG accessibility audit if needed
- `ecc:performance-optimizer` — If page load or render performance is a concern
- `mcp__plugin_ecc_chrome-devtools__take_screenshot` — Capture live screenshot if DevTools available
