import csv
import io

from fpdf import FPDF


def export_breakdown_to_csv(breakdown_data: dict) -> str:
    """
    Produce a scene-by-scene CSV of the breakdown. Returns a CSV string
    (not bytes) so the caller can decide on encoding/response headers.
    """
    output = io.StringIO()
    writer = csv.writer(output)

    writer.writerow([
        "Scene #", "Heading", "INT/EXT", "Time of Day", "Location",
        "Synopsis", "Characters", "Props", "Costumes", "Departments",
    ])

    for scene in breakdown_data.get("scenes", []):
        writer.writerow([
            scene.get("scene_number", ""),
            scene.get("heading", ""),
            scene.get("int_ext", ""),
            scene.get("time_of_day", ""),
            scene.get("location", ""),
            scene.get("synopsis", ""),
            "; ".join(scene.get("characters", [])),
            "; ".join(scene.get("props", [])),
            "; ".join(scene.get("costumes", [])),
            "; ".join(scene.get("departments", [])),
        ])

    return output.getvalue()


class _BreakdownPDF(FPDF):
    def header(self):
        self.set_font("Helvetica", "B", 14)
        self.cell(0, 10, self.title_text, new_x="LMARGIN", new_y="NEXT")
        self.set_font("Helvetica", "", 9)
        self.set_text_color(120, 120, 120)
        self.cell(0, 6, self.subtitle_text, new_x="LMARGIN", new_y="NEXT")
        self.set_text_color(0, 0, 0)
        self.ln(2)

    def footer(self):
        self.set_y(-15)
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(150, 150, 150)
        self.cell(0, 10, f"Page {self.page_no()}", align="C")


_PUNCTUATION_FALLBACKS = {
    "\u2014": "-",   # em dash
    "\u2013": "-",   # en dash
    "\u2018": "'",   # left single quote
    "\u2019": "'",   # right single quote
    "\u201c": '"',   # left double quote
    "\u201d": '"',   # right double quote
    "\u2026": "...", # ellipsis
}


def _sanitize(text) -> str:
    """fpdf2's core fonts (Helvetica) are Latin-1 only. Map common smart
    punctuation to plain ASCII first (so output stays readable), then fall
    back to '?' for anything else outside that range rather than letting
    the whole export crash on a stray character from the AI's output."""
    if text is None:
        return ""
    text = str(text)
    for char, replacement in _PUNCTUATION_FALLBACKS.items():
        text = text.replace(char, replacement)
    return text.encode("latin-1", "replace").decode("latin-1")


def export_breakdown_to_pdf(breakdown_data: dict, script_filename: str) -> bytes:
    """
    Produce a formatted PDF production breakdown: a summary page followed
    by one entry per scene. Returns raw PDF bytes.
    """
    pdf = _BreakdownPDF()
    pdf.title_text = _sanitize("Script Breakdown")
    pdf.subtitle_text = _sanitize(script_filename or "")
    pdf.set_auto_page_break(auto=True, margin=20)
    pdf.add_page()

    summary = breakdown_data.get("summary", {})
    pdf.set_font("Helvetica", "B", 11)
    pdf.cell(0, 8, "Summary", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "", 10)
    pdf.multi_cell(
        0, 6,
        _sanitize(
            f"{summary.get('total_scenes', 0)} scenes | "
            f"{len(summary.get('characters', []))} characters | "
            f"{len(summary.get('locations', []))} locations | "
            f"{len(summary.get('props', []))} props | "
            f"{len(summary.get('costumes', []))} costumes"
        ),
    )
    pdf.ln(4)

    for scene in breakdown_data.get("scenes", []):
        pdf.set_font("Helvetica", "B", 11)
        pdf.cell(
            0, 8,
            _sanitize(f"Scene {scene.get('scene_number', '')}: {scene.get('heading', '')}"),
            new_x="LMARGIN", new_y="NEXT",
        )

        pdf.set_font("Helvetica", "", 10)
        pdf.multi_cell(0, 6, _sanitize(scene.get("synopsis", "")))
        pdf.ln(1)

        for label, key in [
            ("Characters", "characters"),
            ("Props", "props"),
            ("Costumes", "costumes"),
            ("Departments", "departments"),
        ]:
            items = scene.get(key, [])
            value = ", ".join(items) if items else "—"
            pdf.set_font("Helvetica", "B", 9)
            pdf.cell(0, 5, _sanitize(f"{label}:"), new_x="LMARGIN", new_y="NEXT")
            pdf.set_font("Helvetica", "", 9)
            pdf.multi_cell(0, 5, _sanitize(value))

        pdf.ln(4)
        # A light rule between scenes
        pdf.set_draw_color(220, 220, 220)
        pdf.line(pdf.l_margin, pdf.get_y(), pdf.w - pdf.r_margin, pdf.get_y())
        pdf.ln(4)

    return bytes(pdf.output())
