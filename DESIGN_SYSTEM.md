# SteadyVox — Design System Specification

Inspired by the refined visual language of **nixtio.com** (dark-first, typography-driven, hairline borders, micro-interactions).

---

## 1. Design Philosophy & Principles

1. **Dark-First Foundation:** Deep obsidian surface (`#000000`) paired with subtle elevated cards (`#0B0B0C`, `#141416`) and crisp typography.
2. **Hairline Precision:** Zero heavy drop-shadows. Depth is achieved entirely through `1px solid var(--border)` hairline edges (`rgba(255,255,255,0.10)` on dark, `rgba(0,0,0,0.09)` on light).
3. **Medical Credibility:** Vivid yet measured indigo accent (`#6366F1`) combined with unambiguous risk tiering (emerald, amber, rose).
4. **Motor Accessibility (WCAG AA):**
   * Minimum `48px` touch target bounding boxes.
   * Visible focus rings (`2px solid var(--accent)`).
   * Full keyboard navigation on all interactive recording controls.
   * `prefers-reduced-motion` compliance across all procedural canvases.

---

## 2. CSS Design Tokens

Defined in `frontend/src/index.css`:

```css
:root {
  /* Light Theme */
  --bg: #FFFFFF;
  --surface: #F5F5F6;
  --surface-2: #EAEAEC;
  --border: rgba(0, 0, 0, 0.09);
  --border-hover: rgba(0, 0, 0, 0.20);
  --text: #0A0A0A;
  --text-muted: #6B7280;
  --accent: #6366F1;
  --accent-hover: #4F46E5;
  --accent-subtle: rgba(99, 102, 241, 0.08);
}

.dark {
  /* Dark-First Theme */
  --bg: #000000;
  --surface: #0B0B0C;
  --surface-2: #141416;
  --border: rgba(255, 255, 255, 0.10);
  --border-hover: rgba(255, 255, 255, 0.22);
  --text: #FFFFFF;
  --text-muted: #A1A1AA;
  --accent: #6366F1;
  --accent-hover: #4F46E5;
  --accent-subtle: rgba(99, 102, 241, 0.14);
}
```

---

## 3. Typography Scale

* **Font Family:** `Inter, -apple-system, system-ui, sans-serif`
* **Monospace:** `JetBrains Mono, Menlo, monospace` (for latencies, hashes, audio metrics)
* **Hero Headline:** `clamp(40px, 8vw, 88px)` with tight letter-spacing (`-0.03em`)
* **Eyebrow Tag:** `11px` uppercase, `0.12em` letter-spacing, bold
* **Body Text:** `14px` / `16px` with generous `1.6` line-height

---

## 4. Key Component Blueprints

1. **Sticky Translucent Header:**
   * Height: `72px` (`h-18`)
   * Blur: `backdrop-blur-xl` with `bg-bg/80`
   * Controls: Logo, pill navigation links, API health indicator, theme switch, high-contrast CTA.

2. **Waveform Canvas Hero:**
   * Dynamic sine wave superposition with 4–7 Hz tremor frequency modulation.
   * `IntersectionObserver` automatically halts the render loop when scrolled out of view.
   * Disables motion when `prefers-reduced-motion: reduce` is detected.

3. **Numbered Process Cards (`001` - `004`):**
   * Monospace sequence number with accent pill tag.
   * Hover effect: `translateY(-2px)` with subtle border highlight.

4. **Screening Result 3-Tier Badges:**
   * **Low Risk:** Emerald badge + emerald meter.
   * **Uncertain / Borderline:** Amber badge + amber meter.
   * **Elevated Risk:** Rose badge + rose meter.
