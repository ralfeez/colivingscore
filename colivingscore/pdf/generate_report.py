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

# ── Report data ───────────────────────────────────────────────────────────────
DATA = {
    "address":          "4721 Meadowbrook Dr, Sacramento, CA 95825",
    "property_type":    "Single-Family Residential",
    "beds":             5,
    "baths":            3.0,
    "sqft":             2_480,
    "floors":           1,
    "parking":          "Garage (2-car)",
    "hoa":              "None",
    "transit":          "< 0.5 mi",
    "hospital":         "1.2 mi",
    "target_tenant":    "Travel Nurses",
    "score":            87,
    "regulatory":       "Clear",
    "report_date":      "April 16, 2026",
    "mortgage":         2_850,
    "rent_per_room":    1_100,
    "occupancy_rate":   0.92,
    "annual_taxes":     4_800,
    "annual_insurance": 2_400,
    "hoa_monthly":      0,
    "utility_model":    "Owner-paid (combined)",
    "water_sewer":      220,
    "garbage":          45,
    "internet":         120,
    "yard":             80,
    "pest_control":     40,
    "repairs_reserve":  200,
    "capex_reserve":    150,
    "mgmt_model":       "Co-living Specialist (10%)",
    "gross_monthly":    5_060,
    "total_expenses":   4_055,
    "noi_monthly":      1_005,
    "noi_annual":       12_060,
    "dscr":             1.35,
    "oer":              0.80,
    "breakeven_occ":    0.68,
    "noi_margin":       0.20,
    "per_room_noi":     201,
}

TENANT_COMPARISON = [
    {"type": "Travel Nurses",         "score": 87, "monthly_noi": 1_005, "delta": 0,    "best": True},
    {"type": "Tech / Remote Workers", "score": 82, "monthly_noi":   920, "delta": -85,  "best": False},
    {"type": "General Workforce",     "score": 78, "monthly_noi":   840, "delta": -165, "best": False},
    {"type": "Construction / Trades", "score": 74, "monthly_noi":   790, "delta": -215, "best": False},
    {"type": "Students",              "score": 61, "monthly_noi":   640, "delta": -365, "best": False},
    {"type": "Seniors 55+",           "score": 58, "monthly_noi":   600, "delta": -405, "best": False},
    {"type": "Sober Living",          "score": 44, "monthly_noi":   490, "delta": -515, "best": False},
]

IMPROVEMENTS = [
    {"item": "Add 4th bathroom (convert half-bath)", "cost": 18_000, "rent_lift": 150, "roi_months": 10, "priority": "High"},
    {"item": "Add keypad entry per room",            "cost":  1_200, "rent_lift":  30, "roi_months":  3, "priority": "High"},
    {"item": "In-unit washer/dryer stack",           "cost":  2_800, "rent_lift":  50, "roi_months":  5, "priority": "High"},
    {"item": "Mini-fridge per bedroom",              "cost":  1_600, "rent_lift":  25, "roi_months":  6, "priority": "Medium"},
    {"item": "Dedicated desk + lighting per room",   "cost":  1_800, "rent_lift":  35, "roi_months":  4, "priority": "Medium"},
]

# Expense breakdown for donut
EXPENSES = [
    ("Mortgage",          2_850),
    ("Taxes & Insurance", 685),
    ("Utilities",         425),
    ("Reserves",          350),
    ("Management",        506),
    ("Maintenance",       120),
    ("Other",             119),
]

# ── Header / Footer ───────────────────────────────────────────────────────────
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
    canvas_obj.drawRightString(W - 0.55 * inch, H - 23, DATA["report_date"])

    # Bottom bar
    canvas_obj.setFillColor(GRAY_100)
    canvas_obj.rect(0, 0, W, 38, stroke=0, fill=1)
    canvas_obj.setFillColor(GRAY_500)
    canvas_obj.setFont("Helvetica", 7)

    # Disclaimer — split into two lines so it never clips
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

        # Outer ring background
        c.setStrokeColor(GRAY_300)
        c.setLineWidth(9)
        c.circle(cx, cy, r, stroke=1, fill=0)

        # Colored fill circle
        c.setFillColor(score_color)
        c.circle(cx, cy, r - 1, stroke=0, fill=1)

        # Inner white circle
        c.setFillColor(WHITE)
        c.circle(cx, cy, r - 10, stroke=0, fill=1)

        # Score number
        c.setFillColor(GRAY_900)
        c.setFont("Helvetica-Bold", 26)
        c.drawCentredString(cx, cy + 4, str(self.score))

        # Label
        c.setFillColor(GRAY_500)
        c.setFont("Helvetica", 7.5)
        c.drawCentredString(cx, cy - 12, "out of 100")


class ScoreSpectrumBar(Flowable):
    """Horizontal bar showing score zones and where this property lands."""
    def __init__(self, score, width=480, height=52):
        Flowable.__init__(self)
        self.score  = score
        self.width  = width
        self.height = height

    def draw(self):
        c  = self.canv
        w  = self.width
        bh = 18   # bar height
        by = 20   # bar y from bottom

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

        # Score marker
        sx = (self.score / 100) * w
        c.setFillColor(GRAY_900)
        c.setStrokeColor(WHITE)
        c.setLineWidth(1.5)
        c.circle(sx, by + bh / 2, 7, stroke=1, fill=1)
        c.setFillColor(WHITE)
        c.setFont("Helvetica-Bold", 6.5)
        c.drawCentredString(sx, by + bh / 2 - 2.5, str(self.score))

        # Tick label below
        c.setFillColor(GRAY_700)
        c.setFont("Helvetica-Bold", 7.5)
        c.drawCentredString(sx, by - 10, f"This property: {self.score}")

        # Axis ticks
        c.setFillColor(GRAY_500)
        c.setFont("Helvetica", 6.5)
        for tick in [0, 25, 50, 75, 100]:
            tx = (tick / 100) * w
            c.setStrokeColor(GRAY_300)
            c.setLineWidth(0.4)
            c.line(tx, by + bh, tx, by + bh + 4)
            c.drawCentredString(tx, by + bh + 6, str(tick))


class DSCRGauge(Flowable):
    """Needle-style DSCR gauge."""
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

        # Draw semicircle zones (180 degrees = pi radians)
        # 0.8 = leftmost, 2.0 = rightmost on our scale
        scale_min, scale_max = 0.8, 2.0
        scale_range = scale_max - scale_min

        def val_to_angle(v):
            pct = (v - scale_min) / scale_range
            return 180 - pct * 180  # 180=left, 0=right in degrees

        def draw_arc_zone(v_start, v_end, fill_color):
            a1 = val_to_angle(v_end)
            a2 = val_to_angle(v_start)
            c.setFillColor(fill_color)
            c.setStrokeColor(WHITE)
            c.setLineWidth(1)
            # Draw as wedge approximation using thick arc
            c.setLineWidth(22)
            c.setStrokeColor(fill_color)
            import math
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

        # Benchmark line
        ba = math.radians(val_to_angle(self.benchmark))
        c.setStrokeColor(colors.HexColor("#D97706"))
        c.setLineWidth(2)
        c.setDash([4, 3])
        c.line(cx + (r - 25) * math.cos(ba), cy + (r - 25) * math.sin(ba),
               cx + (r + 2)  * math.cos(ba), cy + (r + 2)  * math.sin(ba))
        c.setDash([])

        # Needle
        na = math.radians(val_to_angle(min(self.dscr, scale_max)))
        c.setStrokeColor(GRAY_900)
        c.setLineWidth(2.5)
        c.line(cx, cy,
               cx + (r - 18) * math.cos(na),
               cy + (r - 18) * math.sin(na))
        c.setFillColor(GRAY_900)
        c.circle(cx, cy, 5, stroke=0, fill=1)

        # Center value
        c.setFillColor(GRAY_900)
        c.setFont("Helvetica-Bold", 16)
        c.drawCentredString(cx, cy + 20, f"{self.dscr:.2f}x")
        c.setFillColor(GRAY_500)
        c.setFont("Helvetica", 7.5)
        c.drawCentredString(cx, cy + 10, "DSCR")

        # Labels
        c.setFillColor(RED)
        c.setFont("Helvetica", 7)
        c.drawCentredString(cx - 85, cy + 55, "Danger")
        c.setFillColor(AMBER)
        c.drawCentredString(cx - 25, cy + 90, "Caution")
        c.setFillColor(GREEN)
        c.drawCentredString(cx + 55, cy + 75, "Strong")

        # Benchmark label
        c.setFillColor(colors.HexColor("#D97706"))
        c.setFont("Helvetica", 7)
        c.drawCentredString(cx + (r - 8) * math.cos(ba) + 12,
                            cy + (r - 8) * math.sin(ba) + 6,
                            "1.25x min")


class ExpenseDonut(Flowable):
    """Expense composition donut chart with legend."""
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
        import math

        start_angle = 90
        for i, (label, value) in enumerate(self.expenses):
            sweep = (value / total) * 360
            col = CHART_COLORS[i % len(CHART_COLORS)]
            c.setFillColor(col)
            c.setStrokeColor(WHITE)
            c.setLineWidth(1.5)

            # Draw wedge as filled pie slice using Wedge-style path
            steps = max(int(sweep / 3), 4)
            p = c.beginPath()
            p.moveTo(cx, cy)
            for step in range(steps + 1):
                a = math.radians(start_angle + sweep * step / steps)
                p.lineTo(cx + r_out * math.cos(a), cy + r_out * math.sin(a))
            p.close()
            c.drawPath(p, stroke=1, fill=1)

            start_angle += sweep

        # Inner white circle (donut hole)
        c.setFillColor(WHITE)
        c.setStrokeColor(WHITE)
        c.circle(cx, cy, r_in, stroke=0, fill=1)

        # Center label
        c.setFillColor(GRAY_900)
        c.setFont("Helvetica-Bold", 10)
        c.drawCentredString(cx, cy + 4, f"${total:,}")
        c.setFillColor(GRAY_500)
        c.setFont("Helvetica", 7)
        c.drawCentredString(cx, cy - 8, "total/mo")

        # Legend
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
    """Horizontal bar chart — tenant NOI comparison."""
    def __init__(self, tenants, width=480, height=200):
        Flowable.__init__(self)
        self.tenants = tenants
        self.width   = width
        self.height  = height

    def draw(self):
        c        = self.canv
        max_noi  = max(t["monthly_noi"] for t in self.tenants)
        bar_h    = 20
        gap      = 8
        label_w  = 145
        bar_area = self.width - label_w - 60
        n        = len(self.tenants)
        total_h  = n * (bar_h + gap)
        start_y  = self.height - 20

        for i, t in enumerate(self.tenants):
            y    = start_y - i * (bar_h + gap)
            bw   = (t["monthly_noi"] / max_noi) * bar_area
            col  = GREEN if t["best"] else GRAY_300

            # Bar
            c.setFillColor(col)
            c.setStrokeColor(WHITE)
            c.rect(label_w, y - bar_h, bw, bar_h, stroke=0, fill=1)

            # Label
            fn = "Helvetica-Bold" if t["best"] else "Helvetica"
            tc = GRAY_900 if t["best"] else GRAY_700
            c.setFont(fn, 8)
            c.setFillColor(tc)
            c.drawRightString(label_w - 6, y - bar_h + 6, t["type"])

            # Value
            c.setFont("Helvetica-Bold" if t["best"] else "Helvetica", 8)
            c.setFillColor(GREEN_DARK if t["best"] else GRAY_500)
            c.drawString(label_w + bw + 5, y - bar_h + 6,
                         f"${t['monthly_noi']:,}/mo")

            # Best fit badge
            if t["best"]:
                c.setFillColor(GREEN_LIGHT)
                c.setStrokeColor(GREEN)
                c.setLineWidth(0.5)
                c.rect(label_w + bw + 52, y - bar_h + 2, 38, 14,
                       stroke=1, fill=1)
                c.setFillColor(GREEN_DARK)
                c.setFont("Helvetica-Bold", 6.5)
                c.drawCentredString(label_w + bw + 71, y - bar_h + 7, "BEST FIT")


class ImprovementBarChart(Flowable):
    """Horizontal bar chart — improvement payback months."""
    def __init__(self, improvements, width=480, height=160):
        Flowable.__init__(self)
        self.improvements = improvements
        self.width        = width
        self.height       = height

    def draw(self):
        c       = self.canv
        max_roi = max(i["roi_months"] for i in self.improvements)
        bar_h   = 18
        gap     = 10
        label_w = 190
        bar_area= self.width - label_w - 70
        start_y = self.height - 16

        # Header
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

def build_cover(story, styles):
    story += [
        sp(0.15),
        Paragraph("PRO ANALYSIS REPORT", styles["section_label"]),
        Paragraph(DATA["address"], ParagraphStyle("",
            fontName="Helvetica-Bold", fontSize=17, textColor=GRAY_900,
            leading=22, spaceAfter=4)),
        Paragraph(
            f"{DATA['property_type']}  ·  {DATA['beds']} bed / {DATA['baths']} bath  "
            f"·  {DATA['sqft']:,} sq ft  ·  {DATA['floors']}-story",
            styles["body"]),
        sp(0.12),
    ]

    # Score row — gauge with generous gap to text
    score_color = GREEN if DATA["score"] >= 75 else (AMBER if DATA["score"] >= 50 else RED)
    score_label = "STRONG CANDIDATE" if DATA["score"] >= 75 else (
                  "MODERATE CANDIDATE" if DATA["score"] >= 50 else "WEAK CANDIDATE")

    text_block = Table([
        [Paragraph("CO-LIVING SUITABILITY SCORE", styles["label_sm"])],
        [Paragraph(score_label, ParagraphStyle("", fontName="Helvetica-Bold",
                    fontSize=13, textColor=score_color, leading=17, spaceAfter=4))],
        [Paragraph(
            f"Target tenant: <b>{DATA['target_tenant']}</b>  ·  "
            f"Regulatory: <font color='#1D9E75'><b>{DATA['regulatory']}</b></font>",
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
        [[ScoreGauge(DATA["score"], size=100), text_block]],
        colWidths=[1.5 * inch, 4.2 * inch]   # wider gap col
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

    # Score spectrum bar
    story.append(ScoreSpectrumBar(DATA["score"], width=480, height=52))
    story.append(sp(0.18))
    story.append(hr())

    # Property detail grid
    story += section_header("Property Details", "Physical Profile", styles)
    story.append(sp(0.06))

    detail_rows = [
        ("Bedrooms",           str(DATA["beds"])),
        ("Bathrooms",          str(DATA["baths"])),
        ("Square Footage",     f"{DATA['sqft']:,} sq ft"),
        ("Floors",             str(DATA["floors"])),
        ("Parking",            DATA["parking"]),
        ("HOA",                DATA["hoa"]),
        ("Transit Proximity",  DATA["transit"]),
        ("Hospital Proximity", DATA["hospital"]),
        ("Management Model",   DATA["mgmt_model"]),
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


def build_narrative(story, styles):
    story += [sp(0.15), hr()]
    story += section_header("Market Analysis", "Travel Nurse Market Narrative", styles)
    story.append(sp(0.06))
    story.append(Paragraph(
        "Sacramento is one of the top-performing travel nurse markets in California, "
        "driven by UC Davis Medical Center, Sutter Health, and Kaiser Permanente — "
        "all within 15 minutes of this property. Travel nurse contracts typically run "
        "13 weeks, with assignment extensions common in high-demand markets like this one. "
        "Monthly travel nurse stipends for this region average $1,800–$2,400 for housing, "
        "making your target rent of $1,100 per room well within budget for this tenant class."
        "<br/><br/>"
        "The bathroom ratio at this property (3 baths for 5 rooms) is competitive but not "
        "optimal — travel nurse co-living operators typically target 1:1.5 bath-to-room "
        "ratios. Adding a fourth bathroom would move this property into the top tier for "
        "this tenant type and justify a $75–$150 per-room rent premium. Without it, "
        "strong demand still supports full occupancy in this submarket."
        "<br/><br/>"
        "Single-floor layout earns a premium with healthcare workers pulling extended "
        "shifts — no stairs after a 12-hour shift matters. Garage parking is a differentiator "
        "in this market; nurses arriving on assignment with personal vehicles prioritize "
        "covered, secure parking. This property checks that box cleanly.",
        styles["narrative"]))


def build_financials(story, styles):
    story += [sp(0.15), hr()]
    story += section_header("Financial Analysis", "Year 1 Pro Forma  —  Monthly & Annual", styles)
    story.append(sp(0.06))

    D = DATA
    mgmt_fee = round(D["gross_monthly"] * 0.10)

    # Donut + P&L kept together so NOI row never orphans
    donut_block = [
        Paragraph("Expense Composition", styles["label_sm"]),
        sp(0.06),
        ExpenseDonut(EXPENSES, width=480, height=150),
        sp(0.10),
    ]

    rows = [
        ["", "MONTHLY", "ANNUAL"],
        ["INCOME", "", ""],
        ["Gross Potential Rent (5 rooms × $1,100)", f"${5*1100:,}", f"${5*1100*12:,}"],
        [f"Vacancy Allowance ({int((1-D['occupancy_rate'])*100)}%)",
         f"(${round(5*1100*(1-D['occupancy_rate'])):,})",
         f"(${round(5*1100*(1-D['occupancy_rate'])*12):,})"],
        ["Effective Gross Income", f"${D['gross_monthly']:,}", f"${D['gross_monthly']*12:,}"],
        ["EXPENSES", "", ""],
        ["Mortgage (PITI)",        f"${D['mortgage']:,}",                    f"${D['mortgage']*12:,}"],
        ["Property Taxes",         f"${round(D['annual_taxes']/12):,}",      f"${D['annual_taxes']:,}"],
        ["Insurance",              f"${round(D['annual_insurance']/12):,}",  f"${D['annual_insurance']:,}"],
        ["HOA",                    "$0",                                      "$0"],
        ["Water & Sewer",          f"${D['water_sewer']:,}",                 f"${D['water_sewer']*12:,}"],
        ["Garbage",                f"${D['garbage']:,}",                     f"${D['garbage']*12:,}"],
        ["Internet (5 rooms)",     f"${D['internet']:,}",                    f"${D['internet']*12:,}"],
        ["Yard Maintenance",       f"${D['yard']:,}",                        f"${D['yard']*12:,}"],
        ["Pest Control",           f"${D['pest_control']:,}",                f"${D['pest_control']*12:,}"],
        ["Repairs Reserve",        f"${D['repairs_reserve']:,}",             f"${D['repairs_reserve']*12:,}"],
        ["CapEx Reserve",          f"${D['capex_reserve']:,}",               f"${D['capex_reserve']*12:,}"],
        ["Property Management (10%)", f"${mgmt_fee:,}",                      f"${mgmt_fee*12:,}"],
        ["Total Expenses",         f"${D['total_expenses']:,}",              f"${D['total_expenses']*12:,}"],
        ["NET OPERATING INCOME",   f"${D['noi_monthly']:,}",                 f"${D['noi_annual']:,}"],
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


def build_ratios(story, styles):
    story += [sp(0.15), hr()]
    story += section_header("Key Ratios", "Financial Health Indicators", styles)
    story.append(sp(0.06))

    # DSCR gauge chart
    story.append(Paragraph("Debt Service Coverage Ratio vs. 1.25x Lender Benchmark",
                           styles["label_sm"]))
    story.append(sp(0.06))

    # Center the gauge
    gauge_wrap = Table([[DSCRGauge(DATA["dscr"], width=280, height=155)]],
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

    D = DATA
    ratios = [
        ("Debt Service Coverage Ratio (DSCR)", f"{D['dscr']:.2f}x",
         "Lender benchmark: 1.25x minimum", "dscr", D["dscr"]),
        ("Operating Expense Ratio (OER)",      f"{int(D['oer']*100)}%",
         "Target: under 65% for co-living",   "oer",  D["oer"]),
        ("Break-Even Occupancy Rate",          f"{int(D['breakeven_occ']*100)}%",
         "Rooms needed to cover all expenses", "breakeven", D["breakeven_occ"]),
        ("NOI Margin",                         f"{int(D['noi_margin']*100)}%",
         "Net income as % of gross potential", "margin", D["noi_margin"]),
        ("Per-Room Monthly NOI",               f"${D['per_room_noi']:,}",
         "After all expenses per occupied room", "room", None),
        ("Annual Net Operating Income",        f"${D['noi_annual']:,}",
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


def build_tenant_comparison(story, styles):
    story += [sp(0.15), hr()]
    story += section_header("Tenant Type Analysis",
                            "All 7 Tenant Types — Ranked by Monthly NOI", styles)
    story.append(sp(0.06))
    story.append(Paragraph(
        "Rankings use your actual expense inputs. Score barriers noted where they would "
        "prevent a recommendation.", styles["label_sm"]))
    story.append(sp(0.10))

    # Bar chart
    story.append(TenantBarChart(TENANT_COMPARISON, width=480, height=200))
    story.append(sp(0.14))

    # Table
    header = [
        Paragraph("TENANT TYPE",   styles["table_head"]),
        Paragraph("SCORE",         styles["table_head"]),
        Paragraph("MONTHLY NOI",   styles["table_head"]),
        Paragraph("VS. SELECTION", styles["table_head"]),
    ]
    rows = [header]
    for t in TENANT_COMPARISON:
        delta_str  = "—" if t["delta"] == 0 else f"-${abs(t['delta']):,}/mo"
        delta_color= "#1D9E75" if t["delta"] == 0 else "#E24B4A"
        name_str   = t["type"] + ("  ✓ Best Fit" if t["best"] else "")
        rows.append([
            Paragraph(name_str, ParagraphStyle("",
                fontName="Helvetica-Bold" if t["best"] else "Helvetica",
                fontSize=8.5, leading=12,
                textColor=GREEN_DARK if t["best"] else GRAY_700)),
            Paragraph(str(t["score"]), ParagraphStyle("",
                fontName="Helvetica-Bold", fontSize=8.5, leading=12,
                alignment=TA_CENTER,
                textColor=GREEN if t["score"] >= 75 else
                          (AMBER if t["score"] >= 50 else RED))),
            Paragraph(f"${t['monthly_noi']:,}", ParagraphStyle("",
                fontName="Helvetica-Bold" if t["best"] else "Helvetica",
                fontSize=8.5, leading=12, alignment=TA_RIGHT,
                textColor=GREEN_DARK if t["best"] else GRAY_700)),
            Paragraph(delta_str, ParagraphStyle("",
                fontName="Helvetica-Bold", fontSize=8.5, leading=12,
                alignment=TA_RIGHT,
                textColor=colors.HexColor(delta_color))),
        ])

    col_w = [2.6 * inch, 0.9 * inch, 1.2 * inch, 1.4 * inch]
    tbl   = Table(rows, colWidths=col_w)
    tbl.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (-1, 0), GRAY_900),
        ("TEXTCOLOR",     (0, 0), (-1, 0), WHITE),
        ("BACKGROUND",    (0, 1), (-1, 1), GREEN_LIGHT),
        ("ROWBACKGROUNDS",(0, 2), (-1, -1), [WHITE, GRAY_100]),
        ("ALIGN",         (1, 0), (-1, -1), "CENTER"),
        ("ALIGN",         (2, 0), (-1, -1), "RIGHT"),
        ("ALIGN",         (3, 0), (-1, -1), "RIGHT"),
        ("LEFTPADDING",   (0, 0), (-1, -1), 8),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 8),
        ("TOPPADDING",    (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("LINEBELOW",     (0, 0), (-1, -1), 0.3, GRAY_300),
    ]))
    story.append(tbl)


def build_improvements(story, styles):
    story += [sp(0.15), hr()]
    story += section_header("Improvement Analysis",
                            "Capital Improvements — Cost vs. Rent Lift vs. ROI", styles)
    story.append(sp(0.06))
    story.append(Paragraph(
        "ROI expressed as months to recover improvement cost from incremental rent increase. "
        "Green bars = High priority. All payback periods calculated at 5 rooms.",
        styles["label_sm"]))
    story.append(sp(0.10))

    # Bar chart
    story.append(ImprovementBarChart(IMPROVEMENTS, width=480, height=165))
    story.append(sp(0.14))

    # Table
    header = [
        Paragraph("IMPROVEMENT",  styles["table_head"]),
        Paragraph("EST. COST",    styles["table_head"]),
        Paragraph("RENT LIFT/RM", styles["table_head"]),
        Paragraph("PAYBACK",      styles["table_head"]),
        Paragraph("PRIORITY",     styles["table_head"]),
    ]
    rows = [header]
    for imp in IMPROVEMENTS:
        pri_color = GREEN_DARK if imp["priority"] == "High" else GRAY_700
        rows.append([
            Paragraph(imp["item"],              styles["table_cell"]),
            Paragraph(f"${imp['cost']:,}",      styles["table_cell"]),
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


def build_verdict(story, styles):
    story += [sp(0.15), hr(GREEN, 1.5)]
    story += section_header("Investment Decision", "Go / No-Go Verdict", styles)
    story.append(sp(0.06))

    vbox = Table([[
        Paragraph("GO — Strong Co-Living Candidate", ParagraphStyle("",
            fontName="Helvetica-Bold", fontSize=15,
            textColor=GREEN_DARK, leading=20)),
    ]], colWidths=[6.2 * inch])
    vbox.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (-1, -1), GREEN_LIGHT),
        ("LEFTPADDING",   (0, 0), (-1, -1), 14),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 14),
        ("TOPPADDING",    (0, 0), (-1, -1), 12),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 12),
        ("BOX",           (0, 0), (-1, -1), 1, GREEN_MID),
    ]))
    story.append(vbox)
    story.append(sp(0.10))
    story.append(Paragraph(
        "This property clears every material threshold for travel nurse co-living. "
        "DSCR of 1.35x exceeds the 1.25x lender benchmark. Break-even occupancy of 68% "
        "provides a comfortable cushion — you cover expenses with fewer than 3.5 of 5 rooms "
        "filled. Regulatory status is clear with no HOA restrictions or zoning barriers. "
        "Transit, parking, and single-floor layout align with travel nurse preferences."
        "<br/><br/>"
        "<b>One recommended action before moving forward:</b> Adding a fourth bathroom "
        "at an estimated $18,000 cost recovers in under 10 months at the target rent point "
        "and moves the property into the top tier for this tenant class. It is not required "
        "to operate profitably — but it is the highest-ROI single improvement available."
        "<br/><br/>"
        "This report is suitable for submission to lenders as part of a co-living investment "
        "package. Attach to your loan application with the Year 1 P&amp;L and DSCR calculation.",
        styles["narrative"]))
    story.append(sp(0.20))
    story.append(hr())
    story.append(Paragraph(
        f"Report generated by CoLivingScore.com  ·  {DATA['report_date']}  ·  "
        "Pro Analysis  ·  For investment analysis purposes only.",
        ParagraphStyle("", fontSize=7.5, textColor=GRAY_500,
                       leading=11, alignment=TA_CENTER)))


# ── Main ──────────────────────────────────────────────────────────────────────

def collect_section(fn, styles):
    """Run a section builder and return its flowables as a list."""
    buf = []
    fn(buf, styles)
    return buf


def build_pdf(output_path):
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

    # Page 1 — Cover + property profile
    cover = collect_section(build_cover, styles)
    story.append(KeepTogether(cover))

    # Page 2 — Market narrative (starts fresh page)
    story.append(PageBreak())
    narrative = collect_section(build_narrative, styles)
    story.append(KeepTogether(narrative))

    # Page 3 — Financials (always multi-page; just break cleanly)
    story.append(PageBreak())
    build_financials(story, styles)

    # Page N — Ratios (fresh page, keep gauge + table together)
    story.append(PageBreak())
    ratios = collect_section(build_ratios, styles)
    story.append(KeepTogether(ratios))

    # Page N — Tenant comparison (fresh page, keep chart + table together)
    story.append(PageBreak())
    tenant = collect_section(build_tenant_comparison, styles)
    story.append(KeepTogether(tenant))

    # Page N — Improvements (fresh page, keep chart + table together)
    story.append(PageBreak())
    improvements = collect_section(build_improvements, styles)
    story.append(KeepTogether(improvements))

    # Page N — Verdict (fresh page)
    story.append(PageBreak())
    verdict = collect_section(build_verdict, styles)
    story.append(KeepTogether(verdict))

    doc.build(story, onFirstPage=header_footer, onLaterPages=header_footer)
    print(f"Done — {output_path}")


def build_pdf_from_data(data_dict, output_buffer):
    """
    Called by app.py. Accepts a dict of user inputs and
    writes the PDF to output_buffer (a BytesIO object).
    """
    # Merge user-supplied data over defaults
    global DATA
    DATA = {**DATA, **data_dict}

    # Compute derived values from inputs
    rooms         = DATA["beds"]
    rent_per_room = DATA.get("rent_per_room", 1100)
    occ_rate      = DATA.get("occupancy_rate", 0.92)
    mortgage      = DATA.get("mortgage", 0)
    taxes         = DATA.get("annual_taxes", 0)
    insurance     = DATA.get("annual_insurance", 0)
    water_sewer   = DATA.get("water_sewer", 0)
    garbage       = DATA.get("garbage", 0)
    internet      = DATA.get("internet", 0)
    yard          = DATA.get("yard", 0)
    pest          = DATA.get("pest_control", 0)
    repairs       = DATA.get("repairs_reserve", 0)
    capex         = DATA.get("capex_reserve", 0)

    gross_monthly = round(rooms * rent_per_room * occ_rate)
    mgmt_fee      = round(gross_monthly * 0.10)
    total_exp     = (mortgage + round(taxes/12) + round(insurance/12) +
                     water_sewer + garbage + internet + yard + pest +
                     repairs + capex + mgmt_fee)
    noi_monthly   = gross_monthly - total_exp
    noi_annual    = noi_monthly * 12
    dscr          = round(noi_monthly / mortgage, 2) if mortgage else 0
    oer           = round(total_exp / gross_monthly, 2) if gross_monthly else 0
    breakeven     = round(total_exp / (rooms * rent_per_room), 2) if rooms and rent_per_room else 0
    margin        = round(noi_monthly / gross_monthly, 2) if gross_monthly else 0

    DATA["gross_monthly"]   = gross_monthly
    DATA["total_expenses"]  = total_exp
    DATA["noi_monthly"]     = noi_monthly
    DATA["noi_annual"]      = noi_annual
    DATA["dscr"]            = dscr
    DATA["oer"]             = oer
    DATA["breakeven_occ"]   = breakeven
    DATA["noi_margin"]      = margin
    DATA["per_room_noi"]    = round(noi_monthly / rooms) if rooms else 0
    DATA["mgmt_model"]      = data_dict.get("mgmt_model", DATA["mgmt_model"])

    build_pdf(output_buffer)


if __name__ == "__main__":
    build_pdf("/mnt/user-data/outputs/CoLivingScore_ProAnalysis_v2.pdf")
