---
name: Institutional HR Core
colors:
  surface: '#f7f9fb'
  surface-dim: '#d8dadc'
  surface-bright: '#f7f9fb'
  surface-container-lowest: '#ffffff'
  surface-container-low: '#f2f4f6'
  surface-container: '#eceef0'
  surface-container-high: '#e6e8ea'
  surface-container-highest: '#e0e3e5'
  on-surface: '#191c1e'
  on-surface-variant: '#444651'
  inverse-surface: '#2d3133'
  inverse-on-surface: '#eff1f3'
  outline: '#757682'
  outline-variant: '#c5c5d2'
  surface-tint: '#465aa1'
  primary: '#072369'
  on-primary: '#ffffff'
  primary-container: '#253b80'
  on-primary-container: '#94a8f5'
  inverse-primary: '#b6c4ff'
  secondary: '#264dd9'
  on-secondary: '#ffffff'
  secondary-container: '#4568f3'
  on-secondary-container: '#fffbff'
  tertiary: '#461f00'
  on-tertiary: '#ffffff'
  tertiary-container: '#673100'
  on-tertiary-container: '#e89961'
  error: '#ba1a1a'
  on-error: '#ffffff'
  error-container: '#ffdad6'
  on-error-container: '#93000a'
  primary-fixed: '#dce1ff'
  primary-fixed-dim: '#b6c4ff'
  on-primary-fixed: '#00164f'
  on-primary-fixed-variant: '#2d4287'
  secondary-fixed: '#dde1ff'
  secondary-fixed-dim: '#b8c3ff'
  on-secondary-fixed: '#001355'
  on-secondary-fixed-variant: '#0035bd'
  tertiary-fixed: '#ffdcc6'
  tertiary-fixed-dim: '#ffb785'
  on-tertiary-fixed: '#301400'
  on-tertiary-fixed-variant: '#703806'
  background: '#f7f9fb'
  on-background: '#191c1e'
  surface-variant: '#e0e3e5'
typography:
  headline-lg:
    fontFamily: Hanken Grotesk
    fontSize: 28px
    fontWeight: '700'
    lineHeight: 34px
    letterSpacing: -0.02em
  headline-md:
    fontFamily: Hanken Grotesk
    fontSize: 20px
    fontWeight: '600'
    lineHeight: 28px
  body-lg:
    fontFamily: Hanken Grotesk
    fontSize: 16px
    fontWeight: '400'
    lineHeight: 24px
  body-md:
    fontFamily: Hanken Grotesk
    fontSize: 14px
    fontWeight: '400'
    lineHeight: 20px
  label-bold:
    fontFamily: Hanken Grotesk
    fontSize: 12px
    fontWeight: '600'
    lineHeight: 16px
  label-sm:
    fontFamily: Hanken Grotesk
    fontSize: 12px
    fontWeight: '500'
    lineHeight: 16px
rounded:
  sm: 0.25rem
  DEFAULT: 0.5rem
  md: 0.75rem
  lg: 1rem
  xl: 1.5rem
  full: 9999px
spacing:
  container-padding: 1rem
  stack-space: 1.25rem
  gutter: 1rem
  section-margin: 2rem
---

## Brand & Style

The design system is engineered for professional, high-trust environments within the HR and governmental sectors. It prioritizes clarity, authority, and efficiency, taking direct inspiration from the structured, clean interface of institutional portals.

The visual style is **Corporate / Modern**. It utilizes a light-flooded aesthetic with a "White & Air" philosophy, where ample negative space reduces cognitive load for administrative tasks. The emotional response is one of reliability and calm precision. Surfaces are layered to create a clear sense of information hierarchy, ensuring that critical workforce data is immediately digestible.

## Colors

The palette is anchored by "Institutional Blue" (#253B80), a deep, authoritative tone used for primary branding and navigation headers. A brighter secondary blue provides a modern interactive accent.

*   **Primary Palette:** A range of professional blues. Pure White (#FFFFFF) is the primary surface color, contrasted by a Soft Gray (#F8FAFC) background to define the mobile viewport.
*   **Presence States:** These are mission-critical for HR monitoring.
    *   **Present:** Emerald Green (#10B981) for active status.
    *   **Late:** Amber Orange (#F59E0B) for delays.
    *   **Absent:** Rose Red (#EF4444) for missed check-ins.
*   **Grays:** Used for borders and secondary text to maintain a soft, low-friction visual environment.

## Typography

The design system utilizes **Hanken Grotesk** for its technical precision and humanist approachability. It strikes a balance between a high-end startup aesthetic and institutional stability.

Headlines use a tighter letter-spacing and heavier weights to establish a strong visual anchor on the page. Body text is optimized for long-form reading of employee records, while labels use semi-bold weights and occasionally uppercase styling to denote metadata categories clearly.

## Layout & Spacing

This design system follows a **Fluid Grid** model optimized for mobile-first interactions. It relies on a consistent 8px (0.5rem) base unit to govern all spatial relationships.

*   **Mobile:** 1-column layout with 16px lateral margins.
*   **Vertical Rhythm:** Elements are grouped into "Cards" with a 20px bottom margin.
*   **Internal Padding:** Cards use a generous 20px internal padding to ensure touch targets for HR actions (Edit, Approve, Call) are easily accessible.

## Elevation & Depth

To maintain the institutional feel, depth is achieved through **Tonal Layers** rather than heavy shadows. 

The background is a soft gray (#F1F5F9). Cards and primary containers are pure white (#FFFFFF). To separate these containers from the background, a subtle, ultra-soft shadow (Y: 2, Blur: 4, Opacity: 0.05) or a 1px border in a very light gray (#E2E8F0) is used. This "Flat Plus" approach ensures the UI feels modern and lightweight. High-priority modal elements use a slightly deeper shadow to draw immediate focus.

## Shapes

The shape language is defined by a **Rounded** (Level 2) approach. This softens the formal nature of HR data, making the application feel welcoming and modern.

*   **Standard Cards:** 1rem (16px) corner radius.
*   **Buttons & Inputs:** 0.5rem (8px) corner radius to differentiate actionable elements from structural containers.
*   **Presence Indicators:** Small circles or rounded-pill badges for status displays.

## Components

*   **Buttons:** Primary buttons use the Institutional Blue with white text. Secondary buttons are ghost-styled with a light gray border.
*   **Status Badges:** Pill-shaped chips with a low-opacity background tint matching the presence state (e.g., Light Green background with Dark Green text for "Present").
*   **Cards:** The core unit of the design. White background, rounded corners, and a clear vertical hierarchy: Title -> Subtitle -> Action Bar.
*   **Input Fields:** Minimalist style with a subtle gray stroke. On focus, the stroke transitions to the secondary blue. Labels are always positioned above the input.
*   **Lists:** Divided by thin 1px lines (#F1F5F9). Each item should have a clear trailing icon (chevron) to indicate drill-down capability.
*   **Profile Avatars:** Circular with a subtle border to separate them from white card backgrounds.