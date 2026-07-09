"""Rendu PDF via Chromium (Playwright) — conserve HTML/CSS/Tailwind tels quels."""

from __future__ import annotations

PDF_MARGIN_TOP_MM = 18
PDF_MARGIN_RIGHT_MM = 16
PDF_MARGIN_BOTTOM_MM = 22
PDF_MARGIN_LEFT_MM = 16

_LAYOUT_COMPLIANCE_PAGE_BREAK = """
() => {
  const tableSection = document.querySelector('.report-table-section');
  const compliance = document.querySelector('.document-compliance');
  if (!tableSection || !compliance) return;

  const mmToPx = (mm) => (mm * 96) / 25.4;
  const pageHeight = mmToPx(297);
  const marginTop = mmToPx(%(margin_top)s);
  const marginBottom = mmToPx(%(margin_bottom)s);
  const contentHeight = pageHeight - marginTop - marginBottom;

  compliance.style.breakBefore = '';
  compliance.style.pageBreakBefore = '';

  const complianceHeight = compliance.offsetHeight;
  const tableBottom = tableSection.getBoundingClientRect().bottom + window.scrollY;
  const tablePageIndex = Math.floor(tableBottom / contentHeight);
  const pageEndAfterTable = (tablePageIndex + 1) * contentHeight;
  const remainingAfterTable = pageEndAfterTable - tableBottom;

  if (complianceHeight > remainingAfterTable - 8) {
    compliance.style.breakBefore = 'page';
    compliance.style.pageBreakBefore = 'always';
  }
}
""" % {
    'margin_top': PDF_MARGIN_TOP_MM,
    'margin_bottom': PDF_MARGIN_BOTTOM_MM,
}


def render_html_to_pdf(html: str) -> bytes:
    from playwright.sync_api import sync_playwright

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        try:
            page = browser.new_page()
            page.set_content(html, wait_until='networkidle')
            page.evaluate(
                """async () => {
                    if (document.fonts && document.fonts.ready) {
                        await document.fonts.ready;
                    }
                }"""
            )
            try:
                page.wait_for_function(
                    """() => [...document.fonts].some(
                        (font) => font.family.toLowerCase().includes('material symbols')
                    )""",
                    timeout=20_000,
                )
            except Exception:
                pass
            page.wait_for_timeout(300)
            page.emulate_media(media='print')
            page.evaluate(_LAYOUT_COMPLIANCE_PAGE_BREAK)
            return page.pdf(
                format='A4',
                print_background=True,
                prefer_css_page_size=True,
                margin={
                    'top': f'{PDF_MARGIN_TOP_MM}mm',
                    'right': f'{PDF_MARGIN_RIGHT_MM}mm',
                    'bottom': f'{PDF_MARGIN_BOTTOM_MM}mm',
                    'left': f'{PDF_MARGIN_LEFT_MM}mm',
                },
            )
        finally:
            browser.close()
