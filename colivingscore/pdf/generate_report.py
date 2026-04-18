from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable, KeepTogether, Flowable, PageBreak, CondPageBreak
)
from reportlab.graphics.shapes import (
    Drawing, Rect, String, Line, Circle, Wedge,
    Group, Polygon, PolyLine, ArcPath
)
from reportlab.graphics import renderPDF
from reportlab.graphics.charts.barcharts import HorizontalBarChart
from reportlab.graphics.charts.piecharts import Pie
from reportlab.graphics.widgets.markers import makeMarker
import math

# ── Brand colors ──────────────────────────────────────────────────────────────
GREEN        = colors.HexColor("#1D9E75")
GREEN_LIGHT  = colors.HexColor("#EAF3DE")
GREEN_MID    = colors.HexColor("#97C459")
GREEN_DARK   = colors.HexColor("#27500A")
GREEN_TOP    = colors.HexColor("#4DBF8F")
TEAL_DARK    = colors.HexColor("#0D6B52")
RED          = colors.HexColor("#E24B4A")
RED_LIGHT    = colors.HexColor("#FCEBEB")
AMBER        = colors.HexColor("#D97706")
AMBER_LIGHT  = colors.HexColor("#FAEEDA")
BLUE         = colors.HexColor("#185FA5")
BLUE_LIGHT   = colors.HexColor("#E6F1FB")
GRAY_900     = colors.HexColor("#1A1A1A")
GRAY_700     = colors.HexColor("#374151")
GRAY_500     = colors.HexColor("#6B7280")
GRAY_300     = colors.HexColor("#D1D5DB")
GRAY_100     = colors.HexColor("#F3F4F6")
GRAY_50      = colors.HexColor("#F9FAFB")
WHITE        = colors.white

# Chart accent colors for donut
CHART_COLORS = [
    colors.HexColor("#1D9E75"),
    colors.HexColor("#185FA5"),
    colors.HexColor("#D97706"),
    colors.HexColor("#6B7280"),
    colors.HexColor("#4DBF8F"),
    colors.HexColor("#E24B4A"),
    colors.HexColor("#97C459"),
]

# ── Tenant lookup tables (mirrors JS TENANT_PROFILES) ────────────────────────
TENANT_RENTS = {
    'nurses': 1100, 'tech': 1000, 'trades': 950, 'students': 800,
    'seniors': 900, 'sober': 850, 'workforce': 875,
}
TENANT_LABELS = {
    'nurses':    'Travel Nurses',
    'tech':      'Tech / Remote Workers',
    'trades':    'Construction / Trades',
    'students':  'Students',
    'seniors':   'Seniors 55+',
    'sober':     'Sober Living',
    'workforce': 'General Workforce',
}
TENANT_ORDER = ['nurses', 'tech', 'trades', 'students', 'seniors', 'sober', 'workforce']

MGMT_RATES   = {'self': 0.0, 'specialist': 0.10, 'padsplit': 0.20, 'other': 0.10}
MGMT_LABELS  = {
    'self':       'Self-managed (0%)',
    'specialist': 'Co-living Specialist (10%)',
    'padsplit':   'PadSplit (20%)',
    'other':      'Other / TBD (10%)',
}


# ── Header / Footer factory ───────────────────────────────────────────────────
def make_header_footer(d):
    def header_footer(canvas_obj, doc):
        canvas_obj.saveState()
        W, H = letter

        # Top bar
        canvas_obj.setFillColor(GRAY_900)
        canvas_obj.rect(0, H - 36, W, 36, stroke=0, fill=1)
        canvas_obj.setFillColor(WHITE)
        canvas_obj.setFont("Helvetica-Bold", 11)
        canvas_obj.drawString(0.55 * inch, H - 23, "CoLiving")
        canvas_obj.setFillColor(GREEN)
        canvas_obj.drawString(0.55 * inch + 57, H - 23, "Score")
        canvas_obj.setFillColor(WHITE)
        canvas_obj.setFont("Helvetica", 9)
        canvas_obj.drawString(0.55 * inch + 107, H - 23, ".com  |  Pro Analysis Report")
        canvas_obj.setFillColor(GRAY_300)
        canvas_obj.setFont("Helvetica", 8)
        canvas_obj.drawRightString(W - 0.55 * inch, H - 23, d.get("report_date", ""))

        # Bottom bar
        canvas_obj.setFillColor(GRAY_100)
        canvas_obj.rect(0, 0, W, 38, stroke=0, fill=1)
        canvas_obj.setFillColor(GRAY_500)
        canvas_obj.setFont("Helvetica", 7)
        line1 = ("This report is for investment analysis purposes only and does not constitute "
                 "legal, tax, or financial advice.")
        line2 = ("Verify all regulatory items with a licensed attorney and local municipality "
                 "before making any investment decision.")
        canvas_obj.drawString(0.55 * inch, 25, line1)
        canvas_obj.drawString(0.55 * inch, 13, line2)
        canvas_obj.setFillColor(GRAY_500)
        canvas_obj.setFont("Helvetica", 8)
        canvas_obj.drawRightString(W - 0.55 * inch, 14, f"Page {doc.page}")

        canvas_obj.restoreState()
    return header_footer


# ── Styles ────────────────────────────────────────────────────────────────────
def make_styles():
    def S(**kw):
        defaults = dict(fontName="Helvetica", fontSize=10, leading=14,
                        textColor=GRAY_700, spaceAfter=4)
        defaults.update(kw)
        return ParagraphStyle("", **defaults)

    return {
        "section_label": S(fontName="Helvetica-Bold", fontSize=7, textColor=GREEN,
                           leading=10, spaceAfter=2, spaceBefore=16),
        "section_title": S(fontName="Helvetica-Bold", fontSize=14, textColor=GRAY_900,
                           leading=18, spaceAfter=8),
        "body":          S(fontSize=9.5, leading=14),
        "body_bold":     S(fontName="Helvetica-Bold", fontSize=9.5, leading=14),
        "label_sm":      S(fontSize=8, textColor=GRAY_500, leading=11),
        "narrative":     S(fontSize=9.5, leading=15, textColor=GRAY_700),
        "table_head":    S(fontName="Helvetica-Bold", fontSize=8.5, textColor=WHITE, leading=12),
        "table_cell":    S(fontSize=8.5, leading=12, textColor=GRAY_700),
        "table_cell_b":  S(fontName="Helvetica-Bold", fontSize=8.5, leading=12, textColor=GRAY_900),
        "chart_label":   S(fontSize=8, textColor=GRAY_500, leading=11, alignment=TA_CENTER),
    }


# ── Helpers ───────────────────────────────────────────────────────────────────
def section_header(label, title, styles):
    return [
        Paragraph(label.upper(), styles["section_label"]),
        Paragraph(title, styles["section_title"]),
    ]

def hr(color=GRAY_300, thickness=0.5):
    return HRFlowable(width="100%", thickness=thickness, color=color,
                      spaceAfter=8, spaceBefore=8)

def sp(h=0.12):
    return Spacer(1, h * inch)


# ── Custom Flowables ──────────────────────────────────────────────────────────

class ScoreGauge(Flowable):
    def __init__(self, score, size=100):
        Flowable.__init__(self)
        self.score = score
        self.size  = size
        self.width = size
        self.height= size

    def draw(self):
        c   = self.canv
        cx  = self.size / 2
        cy  = self.size / 2
        r   = self.size / 2 - 6

        score_color = GREEN if self.score >= 75 else (AMBER if self.score >= 50 else RED)

        c.setStrokeColor(GRAY_300)
        c.setLineWidth(9)
        c.circle(cx, cy, r, stroke=1, fill=0)

        c.setFillColor(score_color)
        c.circle(cx, cy, r - 1, stroke=0, fill=1)

        c.setFillColor(WHITE)
        c.circle(cx, cy, r - 10, stroke=0, fill=1)

        c.setFillColor(GRAY_900)
        c.setFont("Helvetica-Bold", 26)
        c.drawCentredString(cx, cy + 4, str(self.score))

        c.setFillColor(GRAY_500)
        c.setFont("Helvetica", 7.5)
        c.drawCentredString(cx, cy - 12, "out of 100")


class ScoreSpectrumBar(Flowable):
    def __init__(self, score, width=480, height=52):
        Flowable.__init__(self)
        self.score  = score
        self.width  = width
        self.height = height

    def draw(self):
        c  = self.canv
        w  = self.width
        bh = 18
        by = 20

        zones = [
            (0,  50,  colors.HexColor("#FCEBEB"), colors.HexColor("#E24B4A"), "Weak  0–49"),
            (50, 74,  colors.HexColor("#FAEEDA"), colors.HexColor("#D97706"), "Moderate  50–74"),
            (75, 100, colors.HexColor("#EAF3DE"), colors.HexColor("#1D9E75"), "Strong  75–100"),
        ]

        for lo, hi, fill, stroke_c, label in zones:
            x1 = (lo / 100) * w
            x2 = (hi / 100) * w
            bw = x2 - x1
            c.setFillColor(fill)
            c.setStrokeColor(stroke_c)
            c.setLineWidth(0.5)
            c.rect(x1, by, bw, bh, stroke=1, fill=1)
            c.setFillColor(stroke_c)
            c.setFont("Helvetica", 7)
            c.drawCentredString(x1 + bw / 2, by + 5, label)

        sx = (self.score / 100) * w
        c.setFillColor(GRAY_900)
        c.setStrokeColor(WHITE)
        c.setLineWidth(1.5)
        c.circle(sx, by + bh / 2, 7, stroke=1, fill=1)
        c.setFillColor(WHITE)
        c.setFont("Helvetica-Bold", 6.5)
        c.drawCentredString(sx, by + bh / 2 - 2.5, str(self.score))

        c.setFillColor(GRAY_700)
        c.setFont("Helvetica-Bold", 7.5)
        c.drawCentredString(sx, by - 10, f"This property: {self.score}")

        c.setFillColor(GRAY_500)
        c.setFont("Helvetica", 6.5)
        for tick in [0, 25, 50, 75, 100]:
            tx = (tick / 100) * w
            c.setStrokeColor(GRAY_300)
            c.setLineWidth(0.4)
            c.line(tx, by + bh, tx, by + bh + 4)
            c.drawCentredString(tx, by + bh + 6, str(tick))


class DSCRGauge(Flowable):
    def __init__(self, dscr, benchmark=1.25, width=280, height=160):
        Flowable.__init__(self)
        self.dscr      = dscr
        self.benchmark = benchmark
        self.width     = width
        self.height    = height

    def draw(self):
        c  = self.canv
        cx = self.width / 2
        cy = 30
        r  = 110

        scale_min, scale_max = 0.8, 2.0
        scale_range = scale_max - scale_min

        def val_to_angle(v):
            pct = (v - scale_min) / scale_range
            return 180 - pct * 180

        def draw_arc_zone(v_start, v_end, fill_color):
            a1 = val_to_angle(v_end)
            a2 = val_to_angle(v_start)
            steps = 30
            for i in range(steps):
                t1 = math.radians(a1 + (a2 - a1) * i / steps)
                t2 = math.radians(a1 + (a2 - a1) * (i + 1) / steps)
                x1 = cx + (r - 11) * math.cos(t1)
                y1 = cy + (r - 11) * math.sin(t1)
                x2 = cx + (r - 11) * math.cos(t2)
                y2 = cy + (r - 11) * math.sin(t2)
                c.setStrokeColor(fill_color)
                c.setLineWidth(22)
                c.line(x1, y1, x2, y2)

        draw_arc_zone(0.8, 1.0,  colors.HexColor("#FCEBEB"))
        draw_arc_zone(1.0, 1.25, colors.HexColor("#FAEEDA"))
        draw_arc_zone(1.25, 2.0, colors.HexColor("#EAF3DE"))

        ba = math.radians(val_to_angle(self.benchmark))
        c.setStrokeColor(colors.HexColor("#D97706"))
        c.setLineWidth(2)
        c.setDash([4, 3])
        c.line(cx + (r - 25) * math.cos(ba), cy + (r - 25) * math.sin(ba),
               cx + (r + 2)  * math.cos(ba), cy + (r + 2)  * math.sin(ba))
        c.setDash([])

        na = math.radians(val_to_angle(min(self.dscr, scale_max)))
        c.setStrokeColor(GRAY_900)
        c.setLineWidth(2.5)
        c.line(cx, cy,
               cx + (r - 18) * math.cos(na),
               cy + (r - 18) * math.sin(na))
        c.setFillColor(GRAY_900)
        c.circle(cx, cy, 5, stroke=0, fill=1)

        c.setFillColor(GRAY_900)
        c.setFont("Helvetica-Bold", 16)
        c.drawCentredString(cx, cy + 20, f"{self.dscr:.2f}x")
        c.setFillColor(GRAY_500)
        c.setFont("Helvetica", 7.5)
        c.drawCentredString(cx, cy + 10, "DSCR")

        c.setFillColor(RED)
        c.setFont("Helvetica", 7)
        c.drawCentredString(cx - 85, cy + 55, "Danger")
        c.setFillColor(AMBER)
        c.drawCentredString(cx - 25, cy + 90, "Caution")
        c.setFillColor(GREEN)
        c.drawCentredString(cx + 55, cy + 75, "Strong")

        c.setFillColor(colors.HexColor("#D97706"))
        c.setFont("Helvetica", 7)
        c.drawCentredString(cx + (r - 8) * math.cos(ba) + 12,
                            cy + (r - 8) * math.sin(ba) + 6,
                            "1.25x min")


class ExpenseDonut(Flowable):
    def __init__(self, expenses, width=480, height=200):
        Flowable.__init__(self)
        self.expenses = expenses
        self.width    = width
        self.height   = height

    def draw(self):
        c      = self.canv
        total  = sum(v for _, v in self.expenses)
        cx     = 110
        cy     = self.height / 2
        r_out  = 75
        r_in   = 42

        start_angle = 90
        for i, (label, value) in enumerate(self.expenses):
            sweep = (value / total) * 360
            col = CHART_COLORS[i % len(CHART_COLORS)]
            c.setFillColor(col)
            c.setStrokeColor(WHITE)
            c.setLineWidth(1.5)

            steps = max(int(sweep / 3), 4)
            p = c.beginPath()
            p.moveTo(cx, cy)
            for step in range(steps + 1):
                a = math.radians(start_angle + sweep * step / steps)
                p.lineTo(cx + r_out * math.cos(a), cy + r_out * math.sin(a))
            p.close()
            c.drawPath(p, stroke=1, fill=1)
            start_angle += sweep

        c.setFillColor(WHITE)
        c.setStrokeColor(WHITE)
        c.circle(cx, cy, r_in, stroke=0, fill=1)

        c.setFillColor(GRAY_900)
        c.setFont("Helvetica-Bold", 10)
        c.drawCentredString(cx, cy + 4, f"${total:,}")
        c.setFillColor(GRAY_500)
        c.setFont("Helvetica", 7)
        c.drawCentredString(cx, cy - 8, "total/mo")

        lx = 210
        ly = self.height - 18
        for i, (label, value) in enumerate(self.expenses):
            col = CHART_COLORS[i % len(CHART_COLORS)]
            row = i
            rx = lx + (row // 4) * 145
            ry = ly - (row % 4) * 22

            c.setFillColor(col)
            c.rect(rx, ry - 1, 10, 10, stroke=0, fill=1)
            c.setFillColor(GRAY_700)
            c.setFont("Helvetica", 8)
            pct = round(value / total * 100)
            c.drawString(rx + 14, ry, f"{label}  ${value:,}  ({pct}%)")


class TenantBarChart(Flowable):
    def __init__(self, tenants, width=480, height=200):
        Flowable.__init__(self)
        self.tenants = tenants
        self.width   = width
        self.height  = height

    def draw(self):
        c        = self.canv
        max_noi  = max(t["monthly_noi"] for t in self.tenants) or 1
        bar_h    = 20
        gap      = 8
        label_w  = 145
        bar_area = self.width - label_w - 60
        start_y  = self.height - 20

        for i, t in enumerate(self.tenants):
            y    = start_y - i * (bar_h + gap)
            bw   = max(0, (t["monthly_noi"] / max_noi) * bar_area)
            col  = GREEN if t["best"] else GRAY_300

            c.setFillColor(col)
            c.setStrokeColor(WHITE)
            c.rect(label_w, y - bar_h, bw, bar_h, stroke=0, fill=1)

            fn = "Helvetica-Bold" if t["best"] else "Helvetica"
            tc = GRAY_900 if t["best"] else GRAY_700
            c.setFont(fn, 8)
            c.setFillColor(tc)
            c.drawRightString(label_w - 6, y - bar_h + 6, t["type"])

            c.setFont("Helvetica-Bold" if t["best"] else "Helvetica", 8)
            c.setFillColor(GREEN_DARK if t["best"] else GRAY_500)
            c.drawString(label_w + bw + 5, y - bar_h + 6,
                         f"${t['monthly_noi']:,}/mo")

            if t["best"]:
                c.setFillColor(GREEN_LIGHT)
                c.setStrokeColor(GREEN)
                c.setLineWidth(0.5)
                c.rect(label_w + bw + 52, y - bar_h + 2, 38, 14, stroke=1, fill=1)
                c.setFillColor(GREEN_DARK)
                c.setFont("Helvetica-Bold", 6.5)
                c.drawCentredString(label_w + bw + 71, y - bar_h + 7, "BEST FIT")


class ImprovementBarChart(Flowable):
    def __init__(self, improvements, width=480, height=160):
        Flowable.__init__(self)
        self.improvements = improvements
        self.width        = width
        self.height       = height

    def draw(self):
        c       = self.canv
        max_roi = max(i["roi_months"] for i in self.improvements) or 1
        bar_h   = 18
        gap     = 10
        label_w = 190
        bar_area= self.width - label_w - 70
        start_y = self.height - 16

        c.setFillColor(GRAY_500)
        c.setFont("Helvetica", 7)
        c.drawString(label_w, start_y + 8, "Payback period (months) — shorter = better ROI")

        for i, imp in enumerate(self.improvements):
            y   = start_y - i * (bar_h + gap)
            bw  = (imp["roi_months"] / max_roi) * bar_area
            col = GREEN if imp["priority"] == "High" else colors.HexColor("#97C459")

            c.setFillColor(col)
            c.rect(label_w, y - bar_h, bw, bar_h, stroke=0, fill=1)

            fn = "Helvetica-Bold" if imp["priority"] == "High" else "Helvetica"
            c.setFont(fn, 7.5)
            c.setFillColor(GRAY_900)
            c.drawRightString(label_w - 6, y - bar_h + 5, imp["item"][:38])

            c.setFont("Helvetica-Bold", 8)
            c.setFillColor(TEAL_DARK)
            c.drawString(label_w + bw + 5, y - bar_h + 5,
                         f"{imp['roi_months']} mo  (+${imp['rent_lift']}/rm)")


# ── Report sections ───────────────────────────────────────────────────────────

def build_cover(d, story, styles):
    story += [
        sp(0.15),
        Paragraph("PRO ANALYSIS REPORT", styles["section_label"]),
        Paragraph(d["address"], ParagraphStyle("",
            fontName="Helvetica-Bold", fontSize=17, textColor=GRAY_900,
            leading=22, spaceAfter=4)),
        Paragraph(
            f"{d['property_type']}  ·  {d['beds']} bed / {d['baths']} bath  "
            f"·  {d['sqft']:,} sq ft  ·  {d['floors']}-story",
            styles["body"]),
        sp(0.12),
    ]

    score_color = GREEN if d["score"] >= 75 else (AMBER if d["score"] >= 50 else RED)
    score_label = ("STRONG CANDIDATE" if d["score"] >= 75 else
                   "MODERATE CANDIDATE" if d["score"] >= 50 else "WEAK CANDIDATE")

    text_block = Table([
        [Paragraph("CO-LIVING SUITABILITY SCORE", styles["label_sm"])],
        [Paragraph(score_label, ParagraphStyle("", fontName="Helvetica-Bold",
                    fontSize=13, textColor=score_color, leading=17, spaceAfter=4))],
        [Paragraph(
            f"Target tenant: <b>{d['target_tenant']}</b>  ·  "
            f"Regulatory: <font color='#1D9E75'><b>{d['regulatory']}</b></font>",
            styles["body"])],
    ], colWidths=[4.2 * inch])
    text_block.setStyle(TableStyle([
        ("LEFTPADDING",   (0, 0), (-1, -1), 0),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 0),
        ("TOPPADDING",    (0, 0), (-1, -1), 2),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
        ("VALIGN",        (0, 0), (-1, -1), "MIDDLE"),
    ]))

    score_row = Table(
        [[ScoreGauge(d["score"], size=100), text_block]],
        colWidths=[1.5 * inch, 4.2 * inch]
    )
    score_row.setStyle(TableStyle([
        ("VALIGN",        (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING",   (0, 0), (-1, -1), 0),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 0),
        ("TOPPADDING",    (0, 0), (-1, -1), 0),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
    ]))
    story.append(score_row)
    story.append(sp(0.15))
    story.append(ScoreSpectrumBar(d["score"], width=480, height=52))
    story.append(sp(0.18))
    story.append(hr())

    story += section_header("Property Details", "Physical Profile", styles)
    story.append(sp(0.06))

    detail_rows = [
        ("Bedrooms",           str(d["beds"])),
        ("Bathrooms",          str(d["baths"])),
        ("Square Footage",     f"{d['sqft']:,} sq ft"),
        ("Floors",             str(d["floors"])),
        ("Parking",            d["parking"]),
        ("HOA",                d["hoa"]),
        ("Transit Proximity",  d["transit"]),
        ("Hospital Proximity", d["hospital"]),
        ("Management Model",   d["mgmt_model"]),
    ]

    def mini_kv(rows):
        data = [[Paragraph(k, styles["label_sm"]),
                 Paragraph(v, styles["body_bold"])] for k, v in rows]
        t = Table(data, colWidths=[1.35 * inch, 1.65 * inch])
        t.setStyle(TableStyle([
            ("VALIGN",           (0, 0), (-1, -1), "TOP"),
            ("ROWBACKGROUNDS",   (0, 0), (-1, -1), [WHITE, GRAY_100]),
            ("LEFTPADDING",      (0, 0), (-1, -1), 6),
            ("RIGHTPADDING",     (0, 0), (-1, -1), 6),
            ("TOPPADDING",       (0, 0), (-1, -1), 4),
            ("BOTTOMPADDING",    (0, 0), (-1, -1), 4),
        ]))
        return t

    left  = detail_rows[:5]
    right = detail_rows[5:]
    grid  = Table([[mini_kv(left), mini_kv(right)]], colWidths=[3.2 * inch, 3.2 * inch])
    grid.setStyle(TableStyle([
        ("VALIGN",        (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING",   (0, 0), (-1, -1), 0),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 0),
        ("TOPPADDING",    (0, 0), (-1, -1), 0),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
    ]))
    story.append(grid)


def build_narrative(d, story, styles):
    story += [sp(0.15), hr()]
    story += section_header("Market Analysis",
                            f"{d['target_tenant']} Market Narrative", styles)
    story.append(sp(0.06))
    story.append(Paragraph(d.get("market_narrative",
        "Market narrative is generated based on your property location and target tenant type. "
        "Full AI-generated narrative available in Phase 2 via the Claude API."),
        styles["narrative"]))


def build_financials(d, story, styles):
    story += [sp(0.15), hr()]
    story += section_header("Financial Analysis", "Year 1 Pro Forma  —  Monthly & Annual", styles)
    story.append(sp(0.06))

    gross    = d["gross_monthly"]
    occ_rate = d["occupancy_rate"]
    beds     = d["beds"]
    rent     = d["rent_per_room"]
    vac_mo   = round(beds * rent * (1 - occ_rate))
    mgmt_fee = round(gross * d["mgmt_rate"])
    tax_mo   = round(d["annual_taxes"] / 12)
    ins_mo   = round(d["annual_insurance"] / 12)

    donut_block = [
        Paragraph("Expense Composition", styles["label_sm"]),
        sp(0.06),
        ExpenseDonut(d["_expenses"], width=480, height=150),
        sp(0.10),
    ]

    occ_pct = int((1 - occ_rate) * 100)
    rows = [
        ["", "MONTHLY", "ANNUAL"],
        ["INCOME", "", ""],
        [f"Gross Potential Rent ({beds} rooms × ${rent:,})",
         f"${beds * rent:,}", f"${beds * rent * 12:,}"],
        [f"Vacancy Allowance ({occ_pct}%)",
         f"(${vac_mo:,})", f"(${vac_mo * 12:,})"],
        ["Effective Gross Income",
         f"${gross:,}", f"${gross * 12:,}"],
        ["EXPENSES", "", ""],
        ["Mortgage (PITI)",          f"${d['mortgage']:,}",        f"${d['mortgage'] * 12:,}"],
        ["Property Taxes",           f"${tax_mo:,}",               f"${d['annual_taxes']:,}"],
        ["Insurance",                f"${ins_mo:,}",               f"${d['annual_insurance']:,}"],
        ["HOA",                      f"${d['hoa_monthly']:,}",     f"${d['hoa_monthly'] * 12:,}"],
        ["Water & Sewer",            f"${d['water_sewer']:,}",     f"${d['water_sewer'] * 12:,}"],
        ["Garbage",                  f"${d['garbage']:,}",         f"${d['garbage'] * 12:,}"],
        [f"Internet ({beds} rooms)", f"${d['internet']:,}",        f"${d['internet'] * 12:,}"],
        ["Yard Maintenance",         f"${d['yard']:,}",            f"${d['yard'] * 12:,}"],
        ["Pest Control",             f"${d['pest_control']:,}",    f"${d['pest_control'] * 12:,}"],
        ["Repairs Reserve",          f"${d['repairs_reserve']:,}", f"${d['repairs_reserve'] * 12:,}"],
        ["CapEx Reserve",            f"${d['capex_reserve']:,}",   f"${d['capex_reserve'] * 12:,}"],
        [f"Property Management ({int(d['mgmt_rate']*100)}%)",
         f"${mgmt_fee:,}", f"${mgmt_fee * 12:,}"],
        ["Total Expenses",           f"${d['total_expenses']:,}",  f"${d['total_expenses'] * 12:,}"],
        ["NET OPERATING INCOME",     f"${d['noi_monthly']:,}",     f"${d['noi_annual']:,}"],
    ]

    col_w = [3.7 * inch, 1.35 * inch, 1.35 * inch]
    tbl   = Table(rows, colWidths=col_w)
    tbl.setStyle(TableStyle([
        ("FONTNAME",      (0, 0), (-1, -1), "Helvetica"),
        ("FONTSIZE",      (0, 0), (-1, -1), 8.5),
        ("TEXTCOLOR",     (0, 0), (-1, -1), GRAY_700),
        ("ALIGN",         (1, 0), (-1, -1), "RIGHT"),
        ("LEFTPADDING",   (0, 0), (-1, -1), 8),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 8),
        ("TOPPADDING",    (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
        ("BACKGROUND",    (0, 0), (-1, 0), GRAY_900),
        ("TEXTCOLOR",     (0, 0), (-1, 0), WHITE),
        ("FONTNAME",      (0, 0), (-1, 0), "Helvetica-Bold"),
        ("BACKGROUND",    (0, 1), (-1, 1), GRAY_100),
        ("FONTNAME",      (0, 1), (-1, 1), "Helvetica-Bold"),
        ("TEXTCOLOR",     (0, 1), (-1, 1), GRAY_900),
        ("BACKGROUND",    (0, 5), (-1, 5), GRAY_100),
        ("FONTNAME",      (0, 5), (-1, 5), "Helvetica-Bold"),
        ("TEXTCOLOR",     (0, 5), (-1, 5), GRAY_900),
        ("BACKGROUND",    (0, 18), (-1, 18), GRAY_100),
        ("FONTNAME",      (0, 18), (-1, 18), "Helvetica-Bold"),
        ("TEXTCOLOR",     (0, 18), (-1, 18), GRAY_900),
        ("BACKGROUND",    (0, 19), (-1, 19), GREEN),
        ("FONTNAME",      (0, 19), (-1, 19), "Helvetica-Bold"),
        ("TEXTCOLOR",     (0, 19), (-1, 19), WHITE),
        ("FONTSIZE",      (0, 19), (-1, 19), 9.5),
        ("ROWBACKGROUNDS",(0, 6), (-1, 17), [WHITE, GRAY_100]),
        ("LINEBELOW",     (0, 0), (-1, -1), 0.3, GRAY_300),
    ]))
    donut_block.append(tbl)
    story.append(KeepTogether(donut_block))


def build_ratios(d, story, styles):
    story += [sp(0.15), hr()]
    story += section_header("Key Ratios", "Financial Health Indicators", styles)
    story.append(sp(0.06))

    story.append(Paragraph("Debt Service Coverage Ratio vs. 1.25x Lender Benchmark",
                           styles["label_sm"]))
    story.append(sp(0.06))

    gauge_wrap = Table([[DSCRGauge(d["dscr"], width=280, height=155)]],
                       colWidths=[6.4 * inch])
    gauge_wrap.setStyle(TableStyle([
        ("ALIGN",         (0, 0), (-1, -1), "CENTER"),
        ("LEFTPADDING",   (0, 0), (-1, -1), 0),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 0),
        ("TOPPADDING",    (0, 0), (-1, -1), 0),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
    ]))
    story.append(gauge_wrap)
    story.append(sp(0.12))

    def ratio_hex(metric, value):
        if metric == "dscr":      return "#1D9E75" if value >= 1.25 else "#E24B4A"
        if metric == "oer":       return "#1D9E75" if value <= 0.65 else ("#D97706" if value <= 0.80 else "#E24B4A")
        if metric == "breakeven": return "#1D9E75" if value <= 0.75 else ("#D97706" if value <= 0.85 else "#E24B4A")
        if metric == "margin":    return "#1D9E75" if value >= 0.20 else ("#D97706" if value >= 0.10 else "#E24B4A")
        return "#1D9E75"

    ratios = [
        ("Debt Service Coverage Ratio (DSCR)", f"{d['dscr']:.2f}x",
         "Lender benchmark: 1.25x minimum", "dscr", d["dscr"]),
        ("Operating Expense Ratio (OER)",      f"{int(d['oer']*100)}%",
         "Target: under 65% for co-living",   "oer",  d["oer"]),
        ("Break-Even Occupancy Rate",          f"{int(d['breakeven_occ']*100)}%",
         "Rooms needed to cover all expenses", "breakeven", d["breakeven_occ"]),
        ("NOI Margin",                         f"{int(d['noi_margin']*100)}%",
         "Net income as % of gross potential", "margin", d["noi_margin"]),
        ("Per-Room Monthly NOI",               f"${d['per_room_noi']:,}",
         "After all expenses per occupied room", "room", None),
        ("Annual Net Operating Income",        f"${d['noi_annual']:,}",
         "Total NOI if sustained 12 months",   "annual", None),
    ]

    ratio_rows = []
    for label, value, benchmark, metric, raw in ratios:
        hex_color = ratio_hex(metric, raw) if raw is not None else "#1D9E75"
        ratio_rows.append([
            Paragraph(label, styles["body"]),
            Paragraph(benchmark, styles["label_sm"]),
            Paragraph(f'<font color="{hex_color}"><b>{value}</b></font>',
                      styles["body_bold"]),
        ])

    rt = Table(ratio_rows, colWidths=[2.8 * inch, 2.6 * inch, 1.0 * inch])
    rt.setStyle(TableStyle([
        ("VALIGN",        (0, 0), (-1, -1), "MIDDLE"),
        ("ROWBACKGROUNDS",(0, 0), (-1, -1), [WHITE, GRAY_100]),
        ("LEFTPADDING",   (0, 0), (-1, -1), 8),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 8),
        ("TOPPADDING",    (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("ALIGN",         (2, 0), (2, -1), "RIGHT"),
        ("LINEBELOW",     (0, 0), (-1, -1), 0.3, GRAY_300),
    ]))
    story.append(rt)


def build_sensitivity(d, story, styles):
    story += [sp(0.15), hr()]
    story += section_header("Sensitivity Analysis", "Break-Even Occupancy Scenarios", styles)
    story.append(sp(0.06))
    story.append(Paragraph(
        "Shows financial performance at reduced occupancy levels. "
        "Management fee scales with revenue at each occupancy level.",
        styles["label_sm"]))
    story.append(sp(0.10))

    beds      = d["beds"]
    rent      = d["rent_per_room"]
    mgmt_rate = d["mgmt_rate"]
    fixed_exp = d["_fixed_exp"]
    mortgage  = d["mortgage"]
    gross_100 = beds * rent

    be_rev  = (fixed_exp + mortgage) / (1 - mgmt_rate) if mgmt_rate < 1 else fixed_exp + mortgage
    be_occ  = min(be_rev / gross_100, 1.0) if gross_100 else 1.0
    be_noi  = be_rev - round(be_rev * mgmt_rate) - fixed_exp

    def sens_row(occ, is_be=False):
        rev     = round(gross_100 * occ)
        mgmt_f  = round(rev * mgmt_rate)
        noi_s   = rev - mgmt_f - fixed_exp
        cf_s    = noi_s - mortgage
        dscr_s  = round(noi_s / mortgage, 2) if mortgage else 0
        if is_be:
            occ_str   = f"{round(be_occ * 100)}%  (Break-Even)"
            cf_str    = "$0"
            assess    = "Break-Even"
            assess_c  = AMBER
            bg        = AMBER_LIGHT
        else:
            occ_str   = f"{int(occ * 100)}%"
            cf_str    = f"${cf_s:,}" if cf_s >= 0 else f"(${abs(cf_s):,})"
            if dscr_s >= 1.25:
                assess, assess_c = "Strong", GREEN
            elif dscr_s >= 1.0:
                assess, assess_c = "Acceptable", GREEN_DARK
            else:
                assess, assess_c = "Below Threshold", RED
            bg = WHITE
        return [occ_str, f"${rev:,}", f"${mgmt_f:,}", f"${noi_s:,}", f"{dscr_s:.2f}x", assess], assess_c, bg

    header = [
        Paragraph("OCCUPANCY",   styles["table_head"]),
        Paragraph("REVENUE",     styles["table_head"]),
        Paragraph("MGMT FEE",    styles["table_head"]),
        Paragraph("NOI",         styles["table_head"]),
        Paragraph("DSCR",        styles["table_head"]),
        Paragraph("ASSESSMENT",  styles["table_head"]),
    ]

    tbl_rows  = [header]
    row_bgs   = []
    assess_colors = []

    for occ in [1.00, 0.90, 0.80]:
        vals, a_color, bg = sens_row(occ)
        tbl_rows.append([Paragraph(v, styles["table_cell"]) for v in vals])
        row_bgs.append(bg)
        assess_colors.append(a_color)

    be_vals, be_a_color, be_bg = sens_row(be_occ, is_be=True)
    tbl_rows.append([Paragraph(v, styles["table_cell"]) for v in be_vals])
    row_bgs.append(be_bg)
    assess_colors.append(be_a_color)

    col_w = [1.1 * inch, 0.9 * inch, 0.85 * inch, 0.85 * inch, 0.7 * inch, 1.8 * inch]
    tbl = Table(tbl_rows, colWidths=col_w)

    ts = [
        ("BACKGROUND",    (0, 0), (-1, 0), GRAY_900),
        ("TEXTCOLOR",     (0, 0), (-1, 0), WHITE),
        ("FONTNAME",      (0, 0), (-1, 0), "Helvetica-Bold"),
        ("ALIGN",         (1, 0), (-1, -1), "RIGHT"),
        ("LEFTPADDING",   (0, 0), (-1, -1), 8),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 8),
        ("TOPPADDING",    (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("LINEBELOW",     (0, 0), (-1, -1), 0.3, GRAY_300),
    ]
    for i, (bg, ac) in enumerate(zip(row_bgs, assess_colors)):
        r = i + 1
        ts.append(("BACKGROUND",  (0, r), (-1, r), bg))
        ts.append(("TEXTCOLOR",   (5, r), (5, r),  ac))
        ts.append(("FONTNAME",    (5, r), (5, r),  "Helvetica-Bold"))

    tbl.setStyle(TableStyle(ts))
    story.append(tbl)


def build_projection(d, story, styles):
    story += [sp(0.15), hr()]
    story += section_header("5-Year Projection", "Cash Flow Forecast", styles)
    story.append(sp(0.06))

    rent_growth = 0.030
    exp_growth  = 0.025
    occ_rate    = d["occupancy_rate"]
    mortgage    = d["mortgage"]
    mgmt_rate   = d["mgmt_rate"]
    fixed_exp   = d["_fixed_exp"]

    # Assumptions note
    assumptions = Table([[
        Paragraph(
            f"Assumptions: {int(rent_growth*100)}% annual rent growth · "
            f"{int(exp_growth*100)}% annual expense growth · "
            f"{int(occ_rate*100)}% occupancy · fixed mortgage · "
            f"management at {int(mgmt_rate*100)}% of gross",
            styles["label_sm"])
    ]], colWidths=[6.4 * inch])
    assumptions.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (-1, -1), GRAY_100),
        ("LEFTPADDING",   (0, 0), (-1, -1), 10),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 10),
        ("TOPPADDING",    (0, 0), (-1, -1), 7),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
    ]))
    story.append(assumptions)
    story.append(sp(0.10))

    header = [
        Paragraph("YEAR",         styles["table_head"]),
        Paragraph("RENT/MO",      styles["table_head"]),
        Paragraph("GROSS/MO",     styles["table_head"]),
        Paragraph("NOI/MO",       styles["table_head"]),
        Paragraph("CASH FLOW/MO", styles["table_head"]),
        Paragraph("CUMULATIVE CF",styles["table_head"]),
    ]
    tbl_rows = [header]

    # Current year
    tbl_rows.append([
        Paragraph("Current", styles["table_cell_b"]),
        Paragraph(f"${d['rent_per_room']:,}", styles["table_cell"]),
        Paragraph(f"${d['gross_monthly']:,}", styles["table_cell"]),
        Paragraph(f"${d['noi_monthly']:,}",  styles["table_cell"]),
        Paragraph(f"${d['noi_monthly'] - mortgage:,}", styles["table_cell"]),
        Paragraph("—", styles["table_cell"]),
    ])

    rent_mo = d["rent_per_room"]
    exp_mo  = fixed_exp
    cumulative = 0
    row_styles = []

    for yr in range(1, 6):
        rent_mo = rent_mo * (1 + rent_growth)
        exp_mo  = exp_mo  * (1 + exp_growth)
        gross_y = round(d["beds"] * rent_mo * occ_rate)
        mgmt_y  = round(gross_y * mgmt_rate)
        noi_y   = round(gross_y - mgmt_y - exp_mo)
        cf_y    = noi_y - mortgage
        cumulative += cf_y * 12
        cf_color = "#1D9E75" if cf_y >= 0 else "#E24B4A"
        is_last = (yr == 5)

        tbl_rows.append([
            Paragraph(f"Year {yr}", styles["table_cell_b" if is_last else "table_cell"]),
            Paragraph(f"${round(rent_mo):,}", styles["table_cell"]),
            Paragraph(f"${gross_y:,}",        styles["table_cell"]),
            Paragraph(f"${noi_y:,}",          styles["table_cell"]),
            Paragraph(f'<font color="{cf_color}">${cf_y:,}</font>', styles["table_cell"]),
            Paragraph(f"${cumulative:,}",     styles["table_cell_b" if is_last else "table_cell"]),
        ])
        if is_last:
            row_styles.append(yr)

    col_w = [0.7*inch, 0.9*inch, 0.9*inch, 0.9*inch, 1.0*inch, 1.05*inch]
    # Pad to full width
    col_w = [1.0*inch, 0.95*inch, 0.95*inch, 0.95*inch, 1.05*inch, 1.5*inch]
    tbl = Table(tbl_rows, colWidths=col_w)

    ts = [
        ("BACKGROUND",    (0, 0), (-1, 0), GRAY_900),
        ("TEXTCOLOR",     (0, 0), (-1, 0), WHITE),
        ("FONTNAME",      (0, 0), (-1, 0), "Helvetica-Bold"),
        ("BACKGROUND",    (0, 1), (-1, 1), GREEN_LIGHT),
        ("ROWBACKGROUNDS",(0, 2), (-1, -2), [WHITE, GRAY_100]),
        ("BACKGROUND",    (0, -1), (-1, -1), GREEN_LIGHT),
        ("ALIGN",         (1, 0), (-1, -1), "RIGHT"),
        ("LEFTPADDING",   (0, 0), (-1, -1), 8),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 8),
        ("TOPPADDING",    (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("LINEBELOW",     (0, 0), (-1, -1), 0.3, GRAY_300),
    ]
    tbl.setStyle(TableStyle(ts))
    story.append(tbl)

    story.append(sp(0.12))
    story.append(Paragraph(
        f"At {int(rent_growth*100)}% annual rent growth, cumulative 5-year cash flow reaches "
        f"<b>${cumulative:,}</b>. Year 5 monthly cash flow of <b>${cf_y:,}</b> represents a "
        f"{round((cf_y - (d['noi_monthly'] - mortgage)) / max(abs(d['noi_monthly'] - mortgage), 1) * 100)}% "
        f"increase over the current run rate.",
        styles["narrative"]))


def build_tenant_comparison(d, story, styles):
    story += [sp(0.15), hr()]
    story += section_header("Tenant Type Analysis",
                            "All 7 Tenant Types — Ranked by Monthly NOI", styles)
    story.append(sp(0.06))
    story.append(Paragraph(
        "Rankings use your actual expense inputs. Score barriers noted where they would "
        "prevent a recommendation.", styles["label_sm"]))
    story.append(sp(0.10))

    story.append(TenantBarChart(d["_tenant_comparison"], width=480, height=200))
    story.append(sp(0.14))

    header = [
        Paragraph("TENANT TYPE",   styles["table_head"]),
        Paragraph("MONTHLY NOI",   styles["table_head"]),
        Paragraph("VS. SELECTION", styles["table_head"]),
    ]
    rows = [header]
    best_noi = next((t["monthly_noi"] for t in d["_tenant_comparison"] if t["best"]), 1)

    for t in d["_tenant_comparison"]:
        delta     = t["monthly_noi"] - best_noi
        delta_str = "—" if delta == 0 else f"-${abs(delta):,}/mo"
        delta_col = "#1D9E75" if delta == 0 else "#E24B4A"
        name_str  = t["type"] + ("  ✓ Best Fit" if t["best"] else "")
        rows.append([
            Paragraph(name_str, ParagraphStyle("",
                fontName="Helvetica-Bold" if t["best"] else "Helvetica",
                fontSize=8.5, leading=12,
                textColor=GREEN_DARK if t["best"] else GRAY_700)),
            Paragraph(f"${t['monthly_noi']:,}", ParagraphStyle("",
                fontName="Helvetica-Bold" if t["best"] else "Helvetica",
                fontSize=8.5, leading=12, alignment=TA_RIGHT,
                textColor=GREEN_DARK if t["best"] else GRAY_700)),
            Paragraph(delta_str, ParagraphStyle("",
                fontName="Helvetica-Bold", fontSize=8.5, leading=12,
                alignment=TA_RIGHT,
                textColor=colors.HexColor(delta_col))),
        ])

    col_w = [3.5 * inch, 1.5 * inch, 1.4 * inch]
    tbl   = Table(rows, colWidths=col_w)
    tbl.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (-1, 0), GRAY_900),
        ("TEXTCOLOR",     (0, 0), (-1, 0), WHITE),
        ("BACKGROUND",    (0, 1), (-1, 1), GREEN_LIGHT),
        ("ROWBACKGROUNDS",(0, 2), (-1, -1), [WHITE, GRAY_100]),
        ("ALIGN",         (1, 0), (-1, -1), "RIGHT"),
        ("LEFTPADDING",   (0, 0), (-1, -1), 8),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 8),
        ("TOPPADDING",    (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("LINEBELOW",     (0, 0), (-1, -1), 0.3, GRAY_300),
    ]))
    story.append(tbl)


def build_improvements(d, story, styles):
    story += [sp(0.15), hr()]
    story += section_header("Improvement Analysis",
                            "Capital Improvements — Cost vs. Rent Lift vs. ROI", styles)
    story.append(sp(0.06))
    story.append(Paragraph(
        "ROI expressed as months to recover improvement cost from incremental rent increase. "
        f"Green bars = High priority. All payback periods calculated at {d['beds']} rooms.",
        styles["label_sm"]))
    story.append(sp(0.10))

    story.append(ImprovementBarChart(d["_improvements"], width=480, height=165))
    story.append(sp(0.14))

    header = [
        Paragraph("IMPROVEMENT",  styles["table_head"]),
        Paragraph("EST. COST",    styles["table_head"]),
        Paragraph("RENT LIFT/RM", styles["table_head"]),
        Paragraph("PAYBACK",      styles["table_head"]),
        Paragraph("PRIORITY",     styles["table_head"]),
    ]
    rows = [header]
    for imp in d["_improvements"]:
        pri_color = GREEN_DARK if imp["priority"] == "High" else GRAY_700
        rows.append([
            Paragraph(imp["item"],               styles["table_cell"]),
            Paragraph(f"${imp['cost']:,}",       styles["table_cell"]),
            Paragraph(f"+${imp['rent_lift']}/mo", styles["table_cell"]),
            Paragraph(f"{imp['roi_months']} mos", styles["table_cell"]),
            Paragraph(imp["priority"], ParagraphStyle("",
                fontName="Helvetica-Bold", fontSize=8.5, leading=12,
                textColor=pri_color)),
        ])

    col_w = [2.65 * inch, 0.85 * inch, 0.95 * inch, 0.75 * inch, 0.80 * inch]
    tbl   = Table(rows, colWidths=col_w)
    tbl.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (-1, 0), GRAY_900),
        ("TEXTCOLOR",     (0, 0), (-1, 0), WHITE),
        ("ROWBACKGROUNDS",(0, 1), (-1, -1), [WHITE, GRAY_100]),
        ("ALIGN",         (1, 0), (-1, -1), "RIGHT"),
        ("LEFTPADDING",   (0, 0), (-1, -1), 8),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 8),
        ("TOPPADDING",    (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("LINEBELOW",     (0, 0), (-1, -1), 0.3, GRAY_300),
    ]))
    story.append(tbl)


def build_verdict(d, story, styles):
    story += [sp(0.15), hr(GREEN, 1.5)]
    story += section_header("Investment Decision", "Go / No-Go Verdict", styles)
    story.append(sp(0.06))

    noi    = d["noi_monthly"]
    dscr   = d["dscr"]
    be     = d["breakeven_occ"]
    score  = d["score"]
    is_go  = score >= 65 and noi > 0 and dscr >= 1.0

    verdict_text = ("GO — Strong Co-Living Candidate" if is_go
                    else "NO-GO — Does Not Meet Thresholds")
    verdict_color = GREEN_DARK if is_go else RED
    verdict_bg    = GREEN_LIGHT if is_go else RED_LIGHT
    verdict_border= GREEN_MID  if is_go else colors.HexColor("#F09595")

    vbox = Table([[
        Paragraph(verdict_text, ParagraphStyle("",
            fontName="Helvetica-Bold", fontSize=15,
            textColor=verdict_color, leading=20)),
    ]], colWidths=[6.2 * inch])
    vbox.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (-1, -1), verdict_bg),
        ("LEFTPADDING",   (0, 0), (-1, -1), 14),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 14),
        ("TOPPADDING",    (0, 0), (-1, -1), 12),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 12),
        ("BOX",           (0, 0), (-1, -1), 1, verdict_border),
    ]))
    story.append(vbox)
    story.append(sp(0.10))

    if is_go:
        body = (
            f"This property clears every material threshold for {d['target_tenant']} co-living. "
            f"DSCR of {dscr:.2f}x {'exceeds' if dscr >= 1.25 else 'approaches'} the 1.25x lender benchmark. "
            f"Break-even occupancy of {int(be*100)}% provides a "
            f"{'comfortable' if be <= 0.75 else 'tight'} cushion — you cover expenses with "
            f"fewer than {math.ceil(be * d['beds']):.0f} of {d['beds']} rooms filled. "
            f"Monthly NOI of ${noi:,} supports a viable co-living operation at this rent level."
        )
    else:
        body = (
            "This property does not meet minimum thresholds for co-living investment at current inputs. "
            "Review the improvement recommendations and re-run the analysis with adjusted rent or expense assumptions."
        )

    story.append(Paragraph(body, styles["narrative"]))
    story.append(sp(0.20))
    story.append(hr())
    story.append(Paragraph(
        f"Report generated by CoLivingScore.com  ·  {d['report_date']}  ·  "
        "Pro Analysis  ·  For investment analysis purposes only.",
        ParagraphStyle("", fontSize=7.5, textColor=GRAY_500,
                       leading=11, alignment=TA_CENTER)))


# ── Main builders ─────────────────────────────────────────────────────────────

def collect_section(fn, d, styles):
    buf = []
    fn(d, buf, styles)
    return buf


def build_pdf(d, output_path):
    doc = SimpleDocTemplate(
        output_path,
        pagesize=letter,
        leftMargin=0.65 * inch,
        rightMargin=0.65 * inch,
        topMargin=0.60 * inch,
        bottomMargin=0.65 * inch,
    )

    styles = make_styles()
    story  = []
    hf     = make_header_footer(d)

    story.append(KeepTogether(collect_section(build_cover, d, styles)))

    story.append(PageBreak())
    story.append(KeepTogether(collect_section(build_narrative, d, styles)))

    story.append(PageBreak())
    build_financials(d, story, styles)

    story.append(PageBreak())
    story.append(KeepTogether(collect_section(build_ratios, d, styles)))

    story.append(PageBreak())
    story.append(KeepTogether(collect_section(build_sensitivity, d, styles)))

    story.append(PageBreak())
    story.append(KeepTogether(collect_section(build_tenant_comparison, d, styles)))

    story.append(PageBreak())
    story.append(KeepTogether(collect_section(build_improvements, d, styles)))

    story.append(PageBreak())
    story.append(KeepTogether(collect_section(build_projection, d, styles)))

    story.append(PageBreak())
    story.append(KeepTogether(collect_section(build_verdict, d, styles)))

    doc.build(story, onFirstPage=hf, onLaterPages=hf)
    print(f"Done — {output_path}")


def _compute_tenant_comparison(d):
    beds      = d["beds"]
    occ_rate  = d["occupancy_rate"]
    mgmt_rate = d["mgmt_rate"]
    fixed_exp = d["_fixed_exp"]
    mortgage  = d["mortgage"]
    target    = d.get("_tenant_key", "nurses")

    results = []
    for key in TENANT_ORDER:
        rent_k  = TENANT_RENTS[key]
        gross_k = round(beds * rent_k * occ_rate)
        mgmt_k  = round(gross_k * mgmt_rate)
        noi_k   = gross_k - mgmt_k - fixed_exp - mortgage
        results.append({
            "type":       TENANT_LABELS[key],
            "monthly_noi": noi_k,
            "best":       key == target,
        })

    results.sort(key=lambda x: x["monthly_noi"], reverse=True)
    return results


def _compute_improvements(d):
    baths = d.get("baths", 3)
    beds  = d.get("beds", 5)

    imps = []
    if baths % 1 != 0:
        imps.append({"item": "Convert half-bath to full bath", "cost": 10_000,
                     "rent_lift": 100, "roi_months": 8, "priority": "High"})
    else:
        imps.append({"item": "Add full bathroom (addition)", "cost": 18_000,
                     "rent_lift": 150, "roi_months": 10, "priority": "High"})

    imps += [
        {"item": "Keypad entry per room",       "cost": 1_200, "rent_lift": 30,  "roi_months": 3,  "priority": "High"},
        {"item": "In-unit washer/dryer stack",  "cost": 2_800, "rent_lift": 50,  "roi_months": 5,  "priority": "High"},
        {"item": "Mini-fridge per bedroom",     "cost": 1_600, "rent_lift": 25,  "roi_months": 6,  "priority": "Medium"},
        {"item": "Dedicated desk + lighting",   "cost": 1_800, "rent_lift": 35,  "roi_months": 4,  "priority": "Medium"},
    ]
    return imps


def _compute_expenses(d):
    mgmt_fee = round(d["gross_monthly"] * d["mgmt_rate"])
    tax_ins  = round(d["annual_taxes"] / 12) + round(d["annual_insurance"] / 12)
    utils    = d["water_sewer"] + d["garbage"] + d["internet"] + d["yard"] + d["pest_control"]
    reserves = d["repairs_reserve"] + d["capex_reserve"]
    hoa      = d["hoa_monthly"]

    expenses = [
        ("Mortgage",           d["mortgage"]),
        ("Taxes & Insurance",  tax_ins),
        ("Utilities",          utils),
        ("Reserves",           reserves),
        ("Management",         mgmt_fee),
    ]
    if hoa > 0:
        expenses.append(("HOA", hoa))
    return expenses


def build_pdf_from_data(data_dict, output_buffer):
    """
    Called by app.py. Accepts a dict of user inputs and
    writes the PDF to output_buffer (a BytesIO object).
    Thread-safe: uses a local data dict, no global mutation.
    """
    mgmt_key  = data_dict.get("mgmt_model_key", "specialist")
    mgmt_rate = MGMT_RATES.get(mgmt_key, 0.10)
    mgmt_label = MGMT_LABELS.get(mgmt_key, data_dict.get("mgmt_model", "Co-living Specialist (10%)"))

    beds      = int(data_dict.get("beds", 5))
    baths     = float(data_dict.get("baths", 3))
    rent      = int(data_dict.get("rent_per_room", 1100))
    occ_rate  = float(data_dict.get("occupancy_rate", 0.92))
    mortgage  = int(data_dict.get("mortgage", 0))
    taxes     = int(data_dict.get("annual_taxes", 0))
    insurance = int(data_dict.get("annual_insurance", 0))
    hoa_mo    = int(data_dict.get("hoa_monthly", 0))
    water     = int(data_dict.get("water_sewer", 0))
    garbage   = int(data_dict.get("garbage", 0))
    internet  = int(data_dict.get("internet", 0))
    yard      = int(data_dict.get("yard", 0))
    pest      = int(data_dict.get("pest_control", 0))
    repairs   = int(data_dict.get("repairs_reserve", 0))
    capex     = int(data_dict.get("capex_reserve", 0))

    gross_monthly = round(beds * rent * occ_rate)
    mgmt_fee      = round(gross_monthly * mgmt_rate)
    tax_mo        = round(taxes / 12)
    ins_mo        = round(insurance / 12)

    # Fixed expenses (do not scale with revenue)
    fixed_exp = tax_mo + ins_mo + hoa_mo + water + garbage + internet + yard + pest + repairs + capex

    total_exp   = mortgage + fixed_exp + mgmt_fee
    noi_monthly = gross_monthly - total_exp
    noi_annual  = noi_monthly * 12
    dscr        = round(noi_monthly / mortgage, 2) if mortgage else 0
    oer         = round(total_exp / gross_monthly, 2) if gross_monthly else 0
    breakeven   = round((fixed_exp + mortgage) / (beds * rent), 2) if beds and rent else 0
    margin      = round(noi_monthly / gross_monthly, 2) if gross_monthly else 0

    # Infer tenant key from label if needed
    label_to_key = {v: k for k, v in TENANT_LABELS.items()}
    tenant_label = data_dict.get("target_tenant", "Travel Nurses")
    tenant_key   = label_to_key.get(tenant_label, "nurses")

    d = {
        # Property
        "address":       data_dict.get("address", "Property Address"),
        "property_type": data_dict.get("property_type", "Single-Family Residential"),
        "beds":          beds,
        "baths":         baths,
        "sqft":          int(data_dict.get("sqft", 0)),
        "floors":        int(data_dict.get("floors", 1)),
        "parking":       data_dict.get("parking", "—"),
        "hoa":           data_dict.get("hoa", "None"),
        "transit":       data_dict.get("transit", "—"),
        "hospital":      data_dict.get("hospital", "—"),
        "target_tenant": tenant_label,
        "score":         int(data_dict.get("score", 0)),
        "regulatory":    data_dict.get("regulatory", "Verify"),
        "report_date":   data_dict.get("report_date", ""),
        # Financial inputs
        "mortgage":        mortgage,
        "rent_per_room":   rent,
        "occupancy_rate":  occ_rate,
        "annual_taxes":    taxes,
        "annual_insurance":insurance,
        "hoa_monthly":     hoa_mo,
        "water_sewer":     water,
        "garbage":         garbage,
        "internet":        internet,
        "yard":            yard,
        "pest_control":    pest,
        "repairs_reserve": repairs,
        "capex_reserve":   capex,
        "mgmt_model":      mgmt_label,
        "mgmt_rate":       mgmt_rate,
        # Derived financials
        "gross_monthly":   gross_monthly,
        "total_expenses":  total_exp,
        "noi_monthly":     noi_monthly,
        "noi_annual":      noi_annual,
        "dscr":            dscr,
        "oer":             oer,
        "breakeven_occ":   breakeven,
        "noi_margin":      margin,
        "per_room_noi":    round(noi_monthly / beds) if beds else 0,
        # Internal computed lists
        "_fixed_exp":   fixed_exp,
        "_tenant_key":  tenant_key,
    }

    d["_tenant_comparison"] = _compute_tenant_comparison(d)
    d["_improvements"]      = _compute_improvements(d)
    d["_expenses"]          = _compute_expenses(d)

    build_pdf(d, output_buffer)


if __name__ == "__main__":
    # Standalone test with sample data
    sample = {
        "address":          "2847 Maple Grove Drive, Austin TX 78704",
        "property_type":    "Single-Family · Co-Living Conversion",
        "beds": 5, "baths": 3.0, "sqft": 2640, "floors": 1,
        "parking": "Garage (2-car)", "hoa": "None",
        "transit": "< 0.5 mi", "hospital": "1.4 mi",
        "target_tenant": "Travel Nurses", "score": 87, "regulatory": "Clear",
        "report_date": "April 18, 2026",
        "mortgage": 2180, "rent_per_room": 950, "occupancy_rate": 0.93,
        "annual_taxes": 3480, "annual_insurance": 1740, "hoa_monthly": 0,
        "water_sewer": 220, "garbage": 50, "internet": 120,
        "yard": 150, "pest_control": 75, "repairs_reserve": 500,
        "capex_reserve": 238, "mgmt_model_key": "specialist",
    }
    import io
    buf = io.BytesIO()
    build_pdf_from_data(sample, buf)
    buf.seek(0)
    with open("/tmp/CoLivingScore_test.pdf", "wb") as f:
        f.write(buf.read())
    print("Test PDF written to /tmp/CoLivingScore_test.pdf")
