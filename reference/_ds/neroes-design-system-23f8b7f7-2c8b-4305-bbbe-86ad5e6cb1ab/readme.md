# Neroes Design System

**neroes** (always lowercase) is a Lisbon neurotechnology company. It builds an adaptive, closed-loop platform — the **Mental Training Platform** — that reads the brain in real time and trains the circuits behind anxiety, focus, and performance. The promise: *train the mind the way you train the body*, with objective feedback instead of guesswork.

The design system is **dark, calm, instrument-grade** — a precision measurement tool, not a consumer wellness app. Data visualization is a first-class design element. Detailing borrows from circuit boards; the EEG trace is the recurring motif.

## Sources

- `uploads/Screenshot 2026-07-09 at 16.09.06.png` — primary logo lockup on white (mark + wordmark).
- `uploads/Screenshot 2026-07-09 at 14.50.48.png` — brand sheet: logo at 64/32/16px, one-colour mono, reversed-on-dark, app icons. Notes: "lines thinned to instrument weight · mitred PCB routing, square pads, round vias · palette deepened, amber → brass · EEG trace replaces the soft wave."
- Written brand brief supplied in-conversation (colors, type, voices, UI rules). No codebase or Figma was provided — components and UI kits are authored from the brief, not recreated from an existing product.

## Products represented

1. **Mental Training Platform** (`ui_kits/platform/`) — the app. Dark instrument dashboard: Today, Live session, Progress, Protocols.
2. **Marketing website** (`ui_kits/website/`) — dark landing page: hero, evidence, method, vision, CTA.

---

## CONTENT FUNDAMENTALS

**Tone:** precise, quietly confident, evidence-first. Short declarative sentences. No hype, no exclamation marks, no emoji.

**Compliance (hard rule):** never use *cure*, *treat*, *guaranteed*, or *proven*. Neroes is a training and research platform, not a medical treatment. Footers carry: "Not a medical device; does not diagnose, cure, or treat any condition."

**The two voices — never blur them:**
- **MEASURED** — teal dot · IBM Plex Mono · factual. For evidence, data, claims with sources. Always attributed in mono caps: `N=41 PILOT · 2025`.
  - *"Mean anxiety score fell 31% over eight sessions. Effect held at 12-week follow-up."*
- **Vision** — brass dot · Newsreader italic. For belief and aspiration only; never numbers, never claims.
  - *"Mental fitness should be as trainable as physical fitness."*
- Sequencing rule: **the evidence earns the right to the vision.** Measured content precedes or outweighs vision content on every surface.

**Casing & person:**
- Wordmark: lowercase `neroes`, always.
- Headings: sentence case, often ending in a period ("Train the mind the way you train the body.").
- Labels/nav/data: IBM Plex Mono, ALL CAPS, wide tracking.
- Product speaks to "you"; Neroes refers to itself by name, not "we", in UI. Marketing may use "we" sparingly.
- Numbers are readouts: pair value with mono unit ("94 SEC", "12.4 HZ"), tabular numerals.

**Copy examples in system:** greetings ("Good afternoon, Rui"), states ("Ready for session 15."), quiet confirmations ("Session saved · 16:02"), factual cautions ("Electrode drift · CH-03 · check contact").

---

## VISUAL FOUNDATIONS

**Color.** Dark base is **Petrol Ink #152E38** — black is not a brand color. Surface ladder `--ink-900…500` steps from chart beds to raised hovers. Cool accent triad from the logo: **teal #2E9296** (primary), **green #479B7E**, **blue #3A67AE**; one warm accent, **brass #B8873C**, used sparingly for energy/vision moments (≈1 brass element per view). Text on dark: `#E9F2F3 / #A9BFC5 / #6E8B93`. Light "paper" context (#F3F5F5, wordmark petrol #2B5A66) for print/marketing moments. Semantic: good=green, caution=brass, poor=`#C4685A` ember (intentional addition — no red in the brand; documented below).

**Type.** **Sora** for headings (semibold, ≤600 weight, −2.5% tracking at display sizes) and body (400, 15/1.6). **IBM Plex Mono** (500, uppercase, 0.14em tracking; 0.22em for eyebrows) for labels, nav, table heads, and every data readout. **Newsreader italic** exclusively for vision quotes. Body copy sits on `--text-2`; only headings and values get `--text-1`.

**Space & density.** 4px base scale. Instrument density: compact controls (38px inputs/buttons), 20px card padding, generous 64–96px section rhythm on marketing pages.

**Shape.** Fully rounded **pills** for buttons, badges, switches. Small radii elsewhere: 6px inputs, 10px cards, 14px modals — PCB corners, not bubbles. Checkbox = **square pad**, radio = **round via** (PCB motif carried into controls).

**Lines.** Everything is **1px, instrument weight** — borders `--border-1`, hover `--border-2`, dividers `--divider` (lowest contrast). Icon strokes 1.5px. Chart lines 1.5px.

**Backgrounds.** Flat petrol surfaces; no gradients on chrome, no textures, no photography in-product. Depth comes from surface-ladder steps + 1px hairlines, not shadow stacks. The only gradient allowed: the area fade under a chart line.

**Data visualization.** Luminous lines on dark grids — the signature element. Chart bed is `--ink-900` inset; grid: dotted horizontals (`--border-1`), faint verticals (`--divider`); lines in bright accent variants with soft glow (`--glow-*`) and gradient underfill. Glow is for **data only, never chrome**. Comparisons: you=teal, cohort/reference=blue, positive=green, vision-related=brass, degraded=ember.

**Elevation & shadows.** Quiet: `--shadow-1` cards, `--shadow-2` popovers, `--shadow-overlay` modals. Modal overlay: petrol scrim at 62% + 3px blur. Blur otherwise only on the sticky marketing nav.

**Motion.** Calm, no bounce: one easing `cubic-bezier(0.2,0.7,0.3,1)`; 120ms hover/color, 200ms reveals/toggles, 360ms panels. Live-status dots may pulse (2.4s); everything respects `prefers-reduced-motion`. No infinite decorative loops on content.

**Interaction states.** Hover: borders and text brighten one step (never darken); ghost/nav items gain a faint raised background. Press: fill darkens one step (primary → petrol). Focus: 1px page-color gap + 3px teal ring (`--focus-ring`). Disabled: 42% opacity.

**Imagery.** None in-product. If marketing needs imagery, keep it cool-toned and desaturated to sit on petrol. No stock photography of brains/headsets was provided — use placeholders and ask.

---

## ICONOGRAPHY

- **No proprietary icon set was provided.** The system uses **Lucide** from CDN (`unpkg.com/lucide@0.469.0`) at **1.5px stroke** ("instrument weight", 1.25 at ≥24px), wrapped by the `Icon` component. This is a flagged substitution — closest CDN match to the brand's thin PCB-line language. Replace with a bespoke set when one exists.
- The **PCB language** (mitred 45° routing, square pads, round vias) is a *decoration/control* motif — carried by Checkbox (square pad), Radio (round via), nav markers, and the `guidelines/brand-motif.card.html` pattern — not by the glyph set.
- Logo files are **provided assets** in `assets/logo/` (cropped from the uploads — lockup light/dark, mark, mono mark, app icons ×2). PNG only; no vector logo exists yet — ask the user for an SVG. Never redraw the mark.
- No emoji, ever. Unicode is acceptable only as data notation in mono readouts (✓, ×, →, ·, α/β/θ/δ band letters).
- Status is communicated by **dots + mono labels** (StatusDot), not icon swaps.

---

## Index

**Root**
- `styles.css` — global entry; imports every token file below.
- `tokens/` — `fonts.css` (Google-hosted Sora / IBM Plex Mono / Newsreader), `colors.css`, `typography.css`, `spacing.css`, `effects.css`, `base.css`.
- `assets/logo/` — neroes-lockup-light/dark, neroes-mark, neroes-mark-mono, neroes-appicon-light/dark (all PNG crops from provided uploads).
- `guidelines/` — foundation specimen cards (Colors ×5, Type ×5, Structure ×4, Brand ×3).
- `SKILL.md` — agent skill entry point.

**Components** (`components/<group>/<Name>.jsx` + `.d.ts` + `.prompt.md`; bundle namespace `NeroesDesignSystem_23f8b7`)
- `actions/` — **Button**, **IconButton**
- `forms/` — **Input**, **Select**, **Checkbox**, **Radio**, **Switch**
- `display/` — **Card**, **Badge**, **Tabs**, **Divider**
- `data/` — **TraceChart**, **Metric**, **StatusDot**
- `overlay/` — **Dialog**, **Tooltip**, **Toast**
- `voice/` — **VoiceQuote**
- `icons/` — **Icon**

**Intentional additions** (no source component library existed; the standard set above was authored from the brief):
- `--signal-poor` ember `#C4685A` — the brand has no red; charts and error states need a "degraded" color.
- `Icon` wrapper — Lucide substitution, flagged above.

**UI kits**
- `ui_kits/platform/` — `index.html` (interactive: click-through nav, live session simulation) + PlatformShell, DashboardScreen, SessionScreen, ProgressScreen, ProtocolsScreen.
- `ui_kits/website/` — `index.html` + SiteChrome (nav/footer), LandingSections (hero, evidence, method, vision, CTA).

No slide templates were provided, so none were authored.
