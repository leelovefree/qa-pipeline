import copy
from lxml import etree
from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE, MSO_CONNECTOR
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.dml import MSO_LINE
from pptx.opc.packuri import PackURI
from pptx.chart.data import CategoryChartData
from pptx.enum.chart import XL_CHART_TYPE, XL_LEGEND_POSITION

SRC = "/Users/macbook/Downloads/Astek Vietnam_AI powered QA Automation .pptx"
OUT = "/Users/macbook/Projects/Cursor/claudepj/qa-pipeline/docs/deck-qa-pipeline.en.pptx"
ICONS = "/private/tmp/claude-501/-Users-macbook-Projects-Cursor-claudepj-qa-pipeline/c3495220-2d08-41d6-a23c-9a920f22a7db/scratchpad/icons"

# ---- palette: dark green, light green, white, light gray (+ template charcoal for body text) ----
DARK = RGBColor(0x01, 0x2E, 0x2B)
GREEN = RGBColor(0x02, 0xBA, 0x71)
WHITE = RGBColor(0xFF, 0xFF, 0xFF)
GRAY = RGBColor(0xF2, 0xF2, 0xF2)
TEXT = RGBColor(0x33, 0x2C, 0x2C)
MUTED = RGBColor(0x58, 0x58, 0x58)
HEX = {"DARK": "012E2B", "GREEN": "02BA71", "WHITE": "FFFFFF"}

prs = Presentation(SRC)

# ---- keep cover (slide 1) and agenda (slide 3); drop the rest of the draft ----
ids = prs.slides._sldIdLst
for i, s in reversed(list(enumerate(list(ids)))):
    if i not in (0, 2):
        prs.part.drop_rel(s.rId)
        ids.remove(s)
cover, agenda = prs.slides[0], prs.slides[1]
agenda.part.partname = PackURI("/ppt/slides/slide2.xml")

LAYOUT_STD = prs.slide_layouts[17]   # 3_Page_Standard: title, category tag, lead phrase
LAYOUT_COVER = prs.slide_layouts[0]  # 1_Page_de_garde


# ---------------- helpers ----------------
def _runs(p, content, size, bold, color, italic=False):
    items = content if isinstance(content, list) else [(content, {})]
    for text, o in items:
        r = p.add_run()
        r.text = text
        f = r.font
        f.size = Pt(o.get("size", size))
        f.bold = o.get("bold", bold)
        f.italic = o.get("italic", italic)
        f.color.rgb = o.get("color", color)


def tb(slide, x, y, w, h, content, size=14, bold=False, color=TEXT, align=PP_ALIGN.LEFT,
       anchor=MSO_ANCHOR.TOP, name=None, space_after=0):
    box = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    if name:
        box.name = name
    tf = box.text_frame
    tf.word_wrap = True
    tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
    tf.vertical_anchor = anchor
    paras = content if (isinstance(content, list) and content and isinstance(content[0], (list, str)) and
                        not (isinstance(content[0], tuple))) else [content]
    # paras: list of paragraphs; each paragraph is str or list of (text, opts) runs
    if isinstance(content, str):
        paras = [content]
    elif isinstance(content, list) and content and isinstance(content[0], tuple):
        paras = [content]
    for i, para in enumerate(paras):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.alignment = align
        p.space_after = Pt(space_after)
        _runs(p, para, size, bold, color)
    return box


def shape(slide, kind, x, y, w, h, fill=None, line=None, line_w=1.0, dash=False, radius=None, name=None):
    sh = slide.shapes.add_shape(kind, Inches(x), Inches(y), Inches(w), Inches(h))
    if name:
        sh.name = name
    sh.shadow.inherit = False
    if fill is None:
        sh.fill.background()
    else:
        sh.fill.solid()
        sh.fill.fore_color.rgb = fill
    if line is None:
        sh.line.fill.background()
    else:
        sh.line.color.rgb = line
        sh.line.width = Pt(line_w)
        if dash:
            sh.line.dash_style = MSO_LINE.DASH
    if kind == MSO_SHAPE.ROUNDED_RECTANGLE and radius is not None:
        sh.adjustments[0] = min(0.5, radius / min(w, h))
    sh.text_frame.text = ""
    return sh


def card(slide, x, y, w, h, fill=GRAY, line=None, dash=False, name="Card"):
    return shape(slide, MSO_SHAPE.ROUNDED_RECTANGLE, x, y, w, h, fill=fill, line=line, dash=dash, radius=0.1, name=name)


def pic(slide, icon, color, x, y, size):
    return slide.shapes.add_picture(f"{ICONS}/{icon}_{HEX[color]}.png", Inches(x), Inches(y), Inches(size), Inches(size))


def icon_circle(slide, icon, x, y, d, bg="DARK"):
    fill = {"DARK": DARK, "GREEN": GREEN, "WHITE": WHITE}[bg]
    shape(slide, MSO_SHAPE.OVAL, x, y, d, d, fill=fill, name=f"Icon circle {icon}")
    k = d * 0.52
    ic = "DARK" if bg == "GREEN" else ("GREEN" if bg == "WHITE" else "WHITE")
    pic(slide, icon, ic, x + (d - k) / 2, y + (d - k) / 2, k)


def pill(slide, text, x, y, w, h, kind="dark", size=10):
    if kind == "dark":
        sh = shape(slide, MSO_SHAPE.ROUNDED_RECTANGLE, x, y, w, h, fill=DARK, radius=h / 2)
        col = WHITE
    elif kind == "green":
        sh = shape(slide, MSO_SHAPE.ROUNDED_RECTANGLE, x, y, w, h, fill=GREEN, radius=h / 2)
        col = DARK
    else:  # outline
        sh = shape(slide, MSO_SHAPE.ROUNDED_RECTANGLE, x, y, w, h, fill=WHITE, line=GREEN, line_w=1.5, radius=h / 2)
        col = DARK
    sh.name = "Pill " + text
    tb(slide, x, y, w, h, text, size=size, bold=True, color=col, align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)


def line(slide, x1, y1, x2, y2, color=MUTED, w=1.5, arrow=False):
    c = slide.shapes.add_connector(MSO_CONNECTOR.STRAIGHT, Inches(x1), Inches(y1), Inches(x2), Inches(y2))
    c.line.color.rgb = color
    c.line.width = Pt(w)
    if arrow:
        ln = c.line._get_or_add_ln()
        te = etree.SubElement(ln, "{http://schemas.openxmlformats.org/drawingml/2006/main}tailEnd")
        te.set("type", "triangle")
    return c


def new_slide(title, tag, lead, notes):
    s = prs.slides.add_slide(LAYOUT_STD)
    s.shapes.title.text = title
    for ph in s.placeholders:
        i = ph.placeholder_format.idx
        if i == 11:
            ph.text = tag
            for p in ph.text_frame.paragraphs:
                for r in p.runs:
                    r.font.color.rgb = WHITE
                    r.font.bold = True
                    r.font.size = Pt(12)
        elif i == 13:
            ph.text = lead
    s.notes_slide.notes_text_frame.text = notes
    return s


def set_runs_text(paragraph, text):
    runs = paragraph.runs
    runs[0].text = text
    for r in runs[1:]:
        r._r.getparent().remove(r._r)


# ================= COVER (reuse template slide 1) =================
sub = [sh for sh in cover.shapes if sh.name == "Subtitle 2"][0]
paras = sub.text_frame.paragraphs
set_runs_text(paras[0], "AI Proposes, the Runner Decides")
paras[0].runs[0].font.color.rgb = GREEN
newp = copy.deepcopy(paras[-1]._p)  # style of "@Astek TCoE"
paras[-1]._p.addprevious(newp)
from pptx.text.text import _Paragraph
np_ = _Paragraph(newp, paras[-1]._parent)
set_runs_text(np_, "AI-assisted mobile QA: from Jira ticket to reviewed PR to CI regression")
cover.notes_slide.notes_text_frame.text = (
    "Today I am not going to talk about how well AI writes tests. I want to talk about how you can trust the result: "
    "which controls exist, what it costs, and what we have actually measured.")

# ================= AGENDA (reuse template slide) =================
items = ["QA Process", "Architecture & Guardrails", "Cost & Context", "Demo", "Evaluation", "Governance & Scale-up"]
phs = [sh for sh in agenda.shapes if sh.has_text_frame and sh.name.startswith("Text Placeholder")]
body = sorted([p for p in phs if p.text_frame.text.strip().lower() != "agenda"], key=lambda p: p.top)
for ph, text in zip(body, items):
    set_runs_text(ph.text_frame.paragraphs[0], text)
agenda.notes_slide.notes_text_frame.text = (
    "Six blocks. First the process and the risks it answers, then the architecture and guardrails, then what it costs and how context is scoped. "
    "Then two short demos, how we evaluate, and finally governance, limits and a proposed pilot.")

# ================= S2 risks =================
s = new_slide("Risks & Controls", "QA PROCESS", "Letting AI write tests: 4 risks, and how each one is controlled",
              "Everyone knows AI can write tests. The real question is: can we trust it? I group it into four risks. "
              "One, fake green: the AI edits the test to make it pass. Two, the AI guesses when a requirement is vague. "
              "Three, the AI runs on without stopping. Four, nobody can trace who did what. Each has a control, and the rest of the talk walks through them. "
              "The first risk is not theoretical: our own system once reported green with no tests. We found it by running on a real ticket and fixed it.\n\n"
              "NOTES: These four risks frame the talk: S4 answers risks 1-2, S5 answers risk 3, S9 answers risk 4.")
risks = [
    ("FaTimesCircle", "“Fake green”", "AI edits the test so it passes instead of reporting the failure", "The test runner decides pass/fail, not the AI"),
    ("FaQuestionCircle", "AI guessing", "The ticket is vague but AI writes tests from assumptions", "On ambiguity the pipeline stops and asks a human"),
    ("FaClock", "Runs forever", "AI retries again and again, burning money and time", "Every step has a cost, time and attempt ceiling"),
    ("FaSearch", "No traceability", "Nobody knows which model did what, who approved, what it cost", "Model, cost and approver recorded for every step"),
]
cw, ch = 6.0, 1.85
for i, (ic, t, m, c) in enumerate(risks):
    x = 0.56 + (i % 2) * (cw + 0.2)
    y = 1.75 + (i // 2) * (ch + 0.15)
    card(s, x, y, cw, ch, name=f"Risk card {i+1}")
    icon_circle(s, ic, x + 0.25, y + 0.25, 0.7, "DARK")
    tb(s, x + 1.2, y + 0.2, cw - 1.4, 0.35, t, size=20, bold=True, color=DARK)
    tb(s, x + 1.2, y + 0.62, cw - 1.4, 0.5, m, size=14, color=MUTED)
    icon_circle(s, "FaCheck", x + 0.35, y + 1.22, 0.4, "GREEN")
    tb(s, x + 1.2, y + 1.15, cw - 1.4, 0.55, c, size=14, bold=True, color=TEXT, anchor=MSO_ANCHOR.MIDDLE)
card(s, 0.56, 5.8, 11.1, 0.7, fill=DARK, name="SCRUM-9 callout")
icon_circle(s, "FaExclamationTriangle", 0.8, 5.9, 0.5, "GREEN")
tb(s, 1.5, 5.8, 10.0, 0.7, [("Real example (SCRUM-9): ", {"bold": True, "color": GREEN}),
                            ("the pipeline once reported “green” although no test had been generated. Fixed: green only when every rule has a test and the tests pass.", {})],
   size=14, color=WHITE, anchor=MSO_ANCHOR.MIDDLE)

# ================= S3 process =================
s = new_slide("QA Process", "QA PROCESS", "8 steps: AI proposes, humans hold the gates",
              "This is the whole process in eight steps. Dark green is AI, light green is a human gate, white with a green outline means no AI at all. "
              "Three things to notice. One: three of the eight steps have a human gate. Two: the CI regression step has no AI; pass or fail is the test tool's result. "
              "Three: when a test goes red, a human classifies the cause, the AI never decides that. QA works in Jira and never has to open the repo. "
              "Steps 7 and 8 are still being built, so the slide marks them as designed.\n\n"
              "NOTES: Agent names if asked: spec-extractor (2), case-designer (3), automation-writer and flow-fixer (4), repair-agent (7), reporter (8).")
lx = 0.56
for kind, label, w in (("dark", "AI", 0.9), ("green", "Human gate", 1.8), ("outline", "No AI", 1.4)):
    shape(s, MSO_SHAPE.OVAL, lx, 1.75, 0.2, 0.2, fill={"dark": DARK, "green": GREEN, "outline": WHITE}[kind],
          line=GREEN if kind == "outline" else None, line_w=1.5)
    tb(s, lx + 0.3, 1.7, w, 0.3, label, size=13, anchor=MSO_ANCHOR.MIDDLE)
    lx += 0.3 + w
shape(s, MSO_SHAPE.ROUNDED_RECTANGLE, lx, 1.76, 0.4, 0.2, fill=WHITE, line=MUTED, dash=True, radius=0.04)
tb(s, lx + 0.5, 1.7, 3.5, 0.3, "Designed, not built yet", size=13, anchor=MSO_ANCHOR.MIDDLE)
nodes = [
    ("FaTicketAlt", "Receive ticket", "HUMAN", "green", "Requirement written in Jira", True),
    ("FaSearch", "Clarify the requirement", "AI", "dark", "Vague? Stop, a human answers", True),
    ("FaClipboardList", "Design test cases", "AI", "dark", "A human approves rules + cases", True),
    ("FaMobileAlt", "Write tests on the real app", "AI", "dark", "Cost and time ceilings", True),
    ("FaCodeBranch", "Review & merge", "HUMAN", "green", "A human approves the PR", True),
    ("FaCheckCircle", "CI regression", "NO AI", "outline", "Maestro decides pass/fail", True),
    ("FaWrench", "Diagnose failures", "AI", "dark", "A human merges any patch", False),
    ("FaFileAlt", "Report & audit", "AI", "dark", "Mostly code, short summary", False),
]
nw, ng, ny, nh = 1.4, 0.14, 2.15, 3.3
for i, (ic, name, who, kind, desc, built) in enumerate(nodes):
    x = 0.56 + i * (nw + ng)
    if built:
        card(s, x, ny, nw, nh, name=f"Step {i+1}")
    else:
        card(s, x, ny, nw, nh, fill=WHITE, line=MUTED, dash=True, name=f"Step {i+1} (designed)")
    bg = {"dark": "DARK", "green": "GREEN", "outline": "WHITE"}[kind]
    if kind == "outline":
        shape(s, MSO_SHAPE.OVAL, x + 0.15, ny + 0.2, 0.65, 0.65, fill=WHITE, line=GREEN, line_w=2.5)
        pic(s, ic, "GREEN", x + 0.15 + 0.165, ny + 0.2 + 0.165, 0.32)
    else:
        icon_circle(s, ic, x + 0.15, ny + 0.2, 0.65, bg)
    tb(s, x + 0.95, ny + 0.1, 0.35, 0.25, str(i + 1), size=12, bold=True, color=MUTED, align=PP_ALIGN.RIGHT)
    tb(s, x + 0.15, ny + 1.0, nw - 0.25, 0.8, name, size=14, bold=True, color=DARK)
    pill(s, who, x + 0.15, ny + 1.85, nw - 0.3, 0.26, kind=kind, size=10)
    tb(s, x + 0.15, ny + 2.2, nw - 0.25, 0.75, desc, size=12, color=MUTED)
    tb(s, x + 0.15, ny + 2.98, nw - 0.25, 0.22, "Built" if built else "Designed", size=11, bold=True, color=DARK if built else MUTED)
tb(s, 0.56, 5.6, 11.0, 0.3, "When a test goes red, a human classifies the cause (the AI never decides):", size=15, bold=True, color=DARK)
tri = [("A", "App bug"), ("B", "Ticket wrong"), ("C", "AI misread"), ("D", "Requirement changed")]
for i, (l, t) in enumerate(tri):
    x = 0.56 + i * 2.85
    card(s, x, 5.98, 2.7, 0.5, name=f"Triage {l}")
    shape(s, MSO_SHAPE.OVAL, x + 0.1, 6.03, 0.4, 0.4, fill=DARK)
    tb(s, x + 0.1, 6.03, 0.4, 0.4, l, size=15, bold=True, color=WHITE, align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
    tb(s, x + 0.65, 5.98, 2.0, 0.5, t, size=14, bold=True, color=DARK, anchor=MSO_ANCHOR.MIDDLE)

# ================= S4 architecture =================
s = new_slide("Architecture & Guardrails", "ARCHITECTURE & GUARDRAILS", "Three AIs in a chain; a test tool, not an AI, decides",
              "How it works is simple. Three AIs in a chain, each doing one job and handing over files in git, so a human can read and edit them. "
              "In between are two human gates: answering ambiguity, and approving rules and test cases. Most important is the green box: the test tool decides pass or fail, not an AI. "
              "The table is the six controls. I will be direct: five are enforced by code or CI. The last one, ‘must look at the real app before writing a selector’, "
              "is still an instruction to the AI, with no code check behind it.\n\n"
              "NOTES: Technical names only if asked: orchestrator bin/qa-auto, test runner bin/qa, coverage check bin/qa-check, assertion lock fix_is_legit, spec check spec-integrity, screen inspection inspect_screen (Maestro MCP). "
              "Handoff between steps = files in git on branch qa/<TICKET>, not chat memory.")
flow = [
    ("FaTicketAlt", "Jira ticket", "human"),
    ("FaSearch", "AI #1 · Split into rules (vague → stop)", "ai"),
    ("FaClipboardList", "AI #2 · Design test cases", "ai"),
    ("FaUserCheck", "Human approves rules + cases", "human"),
    ("FaMobileAlt", "AI #3 · Write tests on the real app", "ai"),
    ("FaCheckCircle", "Maestro runs tests = the verdict (no AI)", "noai"),
    ("FaCodeBranch", "Pull request → human merges", "human"),
]
bw, bh, st = 5.0, 0.5, 0.66
for i, (ic, label, kind) in enumerate(flow):
    y = 1.75 + i * st
    if kind == "ai":
        shape(s, MSO_SHAPE.ROUNDED_RECTANGLE, 0.56, y, bw, bh, fill=DARK, radius=0.1, name=f"Flow {i+1}"); col, icc = WHITE, "WHITE"
    elif kind == "human":
        shape(s, MSO_SHAPE.ROUNDED_RECTANGLE, 0.56, y, bw, bh, fill=GREEN, radius=0.1, name=f"Flow {i+1}"); col, icc = DARK, "DARK"
    else:
        shape(s, MSO_SHAPE.ROUNDED_RECTANGLE, 0.56, y, bw, bh, fill=WHITE, line=GREEN, line_w=2.5, radius=0.1, name=f"Flow {i+1}"); col, icc = DARK, "GREEN"
    pic(s, ic, icc, 0.74, y + 0.11, 0.28)
    tb(s, 1.2, y, bw - 0.8, bh, label, size=14, bold=True, color=col, anchor=MSO_ANCHOR.MIDDLE)
    if i < len(flow) - 1:
        line(s, 0.56 + bw / 2, y + bh, 0.56 + bw / 2, y + st, color=MUTED, w=1.5, arrow=True)
tb(s, 5.95, 1.7, 6.8, 0.35, "6 controls", size=18, bold=True, color=DARK)
tb(s, 5.95, 2.05, 6.8, 0.25, "CODE / CI = enforced by machine · PROMPT = only an instruction to the AI", size=12, color=MUTED)
rows = [
    ("FaCheckCircle", "Pass/fail", "Decided by Maestro's result; CI has no AI step", "CODE / CI"),
    ("FaClipboardList", "Every requirement covered", "Each rule in the spec needs a matching test case", "CODE"),
    ("FaShieldAlt", "Honest “green”", "Green only when every rule has a test and tests pass", "CODE"),
    ("FaLock", "No editing requirements to pass", "CI blocks spec + test changes in one PR without approval", "CI"),
    ("FaWrench", "Auto-fix cannot touch checks", "Only selectors and wait times; never assertions", "CODE"),
    ("FaEye", "Elements come from the real app", "AI must look at the real screen before writing a selector", "PROMPT"),
]
for i, (ic, n, d, lvl) in enumerate(rows):
    y = 2.45 + i * 0.64
    card(s, 5.95, y, 6.8, 0.58, name=f"Control {i+1}")
    icon_circle(s, ic, 6.05, y + 0.09, 0.4, "DARK")
    tb(s, 6.6, y + 0.04, 4.8, 0.25, n, size=14, bold=True, color=DARK)
    tb(s, 6.6, y + 0.31, 4.8, 0.24, d, size=12, color=MUTED)
    pill(s, lvl, 11.5, y + 0.15, 1.15, 0.28, kind="green" if lvl == "PROMPT" else "dark", size=10)

# ================= S5 cost =================
s = new_slide("Cost", "COST & CONTEXT", "Small, measured and capped: one data point, not a standard",
              "On cost I separate three layers. One: the hard ceiling. If an AI runs away it is stopped at this level; the ceiling is far above real spend because it is a guard rail, not a budget. "
              "Two: what we measured on five real tickets of a simple demo app, about 0.4 dollars per test. This is one data point, not a standard: a real app is more complex, so it may cost one to three times more, "
              "and the pilot will measure the real number. Three: to picture it, 0.4 dollars is about half a minute of an engineer's time at, say, 50 dollars an hour. So the real cost is review time, not AI spend. "
              "Finally, the daily regression run costs no AI money at all.\n\n"
              "NOTES: Ticket cost ≈ $0.5 fixed (split rules ~$0.3 + design cases ~$0.2) + ~$0.17 per test written (measured: SCRUM-8 $0.17, SCRUM-12 $0.19, SCRUM-13 $0.16). Check: SCRUM-13 $0.49 + $0.32 = $0.81. "
              "'1-3x' is an assumption. Pilot: 10 tickets x $0.84 ≈ $10 (lower bound); 15 tickets x ~$3.5 ≈ $53, plus step 7 → ~$70 (upper bound). $50/hour is illustrative. "
              "Do not say 'from $1.35 to $0.81': those tickets had different numbers of tests. Splitting out case-designer made the design-cases step ~$0.30 cheaper per ticket (3 earlier measurements, 1 later). "
              "No daily spend cap yet; excludes macOS CI runner minutes.")
cats = ["SCRUM-13 · $0.81", "SCRUM-12 · $1.32", "SCRUM-11 · $1.38", "SCRUM-9 · $1.35", "SCRUM-8 · $0.91"]
cd = CategoryChartData()
cd.categories = cats
cd.add_series("Split rules", (0.32, 0.29, 0.26, 0.24, 0.27))
cd.add_series("Design cases", (0.17, 0.47, 0.46, 0.47, 0.0))
cd.add_series("Write tests", (0.32, 0.57, 0.38, 0.47, 0.34))
cd.add_series("Auto-fix", (0.0, 0.0, 0.29, 0.17, 0.29))
gf = s.shapes.add_chart(XL_CHART_TYPE.BAR_STACKED, Inches(0.56), Inches(1.75), Inches(7.3), Inches(3.9), cd)
gf.name = "Cost per ticket chart"
ch_ = gf.chart
ch_.has_title = True
ch_.chart_title.text_frame.text = "AI cost per ticket by step (USD, ShopDemo)"
r = ch_.chart_title.text_frame.paragraphs[0].runs[0]
r.font.size = Pt(14); r.font.bold = True; r.font.color.rgb = DARK
ch_.has_legend = True
ch_.legend.position = XL_LEGEND_POSITION.BOTTOM
ch_.legend.include_in_layout = False
ch_.legend.font.size = Pt(12)
ch_.legend.font.color.rgb = TEXT
ch_.category_axis.tick_labels.font.size = Pt(12)
ch_.category_axis.tick_labels.font.color.rgb = TEXT
ch_.category_axis.format.line.color.rgb = RGBColor(0xC9, 0xD3, 0xCF)
va = ch_.value_axis
va.tick_labels.font.size = Pt(11)
va.tick_labels.font.color.rgb = TEXT
va.tick_labels.number_format = '$0.0'
va.tick_labels.number_format_is_linked = False
va.maximum_scale = 1.6
va.major_unit = 0.4
va.has_major_gridlines = True
va.major_gridlines.format.line.color.rgb = RGBColor(0xE2, 0xE6, 0xE4)
va.format.line.fill.background()
plot = ch_.plots[0]
plot.gap_width = 50
plot.overlap = 100
for ser, col in zip(plot.series, (DARK, GREEN, RGBColor(0x7F, 0xD9, 0xB4), RGBColor(0xB8, 0xC2, 0xBE))):
    ser.format.fill.solid()
    ser.format.fill.fore_color.rgb = col
stats = [("~$0.4", "per generated test (ShopDemo, 5 runs)"),
         ("$0", "AI cost when CI re-runs the tests"),
         ("~$10–70", "AI cost for the whole 10–15-ticket pilot (estimate)")]
for i, (big, cap) in enumerate(stats):
    y = 1.75 + i * 1.35
    card(s, 8.2, y, 4.55, 1.2, name=f"Stat {i+1}")
    tb(s, 8.45, y + 0.08, 4.1, 0.6, big, size=34, bold=True, color=DARK, anchor=MSO_ANCHOR.MIDDLE)
    tb(s, 8.45, y + 0.72, 4.1, 0.42, cap, size=13, color=MUTED)
card(s, 0.56, 5.85, 11.1, 0.7, fill=DARK, name="Caveat")
tb(s, 0.8, 5.85, 10.7, 0.7, [("One data point, not a standard. ", {"bold": True, "color": GREEN}),
                            ("ShopDemo is a simple app; a real app may cost 1–3× more (assumption). Hard ceilings per step: $1.5 · $2 · $12 · $4 — guard rails, not a budget.", {})],
   size=14, color=WHITE, anchor=MSO_ANCHOR.MIDDLE)

# ================= S6 scenario =================
s = new_slide("Demo Scenario", "DEMO", "Same app, three builds: watch what the AI does with each",
              "I will demo two parts. Part one: from a Jira ticket to a PR, live. Part two: re-running the tests on three versions of the app. "
              "Watch for one thing: not that the AI can fix a test, but that it knows when it may fix it and when it must refuse.\n\n"
              "NOTES: The 'changed ID' and 'real defect' builds still have to be built in the app repo (only build-0 and build-1 exist).")
builds = [
    ("GREEN", "FaCheckCircle", "Exists", "Original", "build-1 · nothing changed", "Tests pass"),
    ("DARK", "FaWrench", "To build", "Element ID renamed", "Behaviour stays the same", "AI patches the selector with evidence, re-run passes"),
    ("DARK", "FaBan", "To build", "Real logic defect", "The app misbehaves", "AI refuses to fix, test stays red, a human classifies it (A)"),
]
cw = 3.95
for i, (bg, ric, tag, t, sub, res) in enumerate(builds):
    x = 0.56 + i * (cw + 0.18)
    card(s, x, 1.75, cw, 3.2, name=f"Build {i+1}")
    icon_circle(s, "FaMobileAlt", x + 0.25, 1.95, 0.75, bg)
    pill(s, tag, x + cw - 1.45, 2.15, 1.2, 0.3, kind="green" if tag == "Exists" else "dark", size=11)
    tb(s, x + 0.25, 2.85, cw - 0.5, 0.4, t, size=20, bold=True, color=DARK)
    tb(s, x + 0.25, 3.3, cw - 0.5, 0.3, sub, size=14, color=MUTED)
    tb(s, x + 0.25, 3.8, cw - 0.5, 0.25, "EXPECTED RESULT", size=11, bold=True, color=MUTED)
    pic(s, ric, "DARK" if bg == "GREEN" else "DARK", x + 0.25, 4.15, 0.32)
    tb(s, x + 0.7, 4.1, cw - 0.95, 0.75, res, size=14, bold=True, color=TEXT)
card(s, 0.56, 5.2, 11.1, 0.85, fill=DARK, name="Watch for")
tb(s, 0.85, 5.2, 10.6, 0.85, [("Watch for one thing: ", {"bold": True, "color": GREEN}),
                             ("not that the AI can fix a test, but that it knows when it may fix it and when it must refuse.", {})],
   size=18, color=WHITE, anchor=MSO_ANCHOR.MIDDLE)

# ================= Demo 1 =================
s = new_slide("Demo 1", "DEMO", "From Jira ticket to pull request, live (≈ 6 min · steps 2–5 · built)",
              "This is a real ticket in Jira. I add the label qa-auto. The system reads the ticket and splits it into rules. Here is the single comment sent to QA, with both rules and test cases. "
              "I add the approval label. Now the AI opens the real app on the simulator to write the tests; that takes about two minutes. While we wait you can see the cost and time ceilings running. "
              "Done: here is the PR, with the model used and the total cost. And if the ticket is vague, the system stops and asks, like on this screen, instead of guessing.\n\n"
              "NOTES: Start the ticket before you speak so split-rules and design-cases are done (real timings: split rules ~33 s, design cases ~40 s, write tests ~139 s, create simulator ~86 s). "
              "Show the vague-ticket qa-needs-info comment as a screenshot. Backup: a recording of this exact run.")
steps = [("FaTicketAlt", "Jira ticket", "label qa-auto added", "green"),
         ("FaClipboardList", "Spec + test cases", "one single comment for QA", "dark"),
         ("FaUserCheck", "Human approves", "label qa-approved added", "green"),
         ("FaMobileAlt", "AI writes tests", "on a real simulator, ≈ 2 min", "dark"),
         ("FaCodeBranch", "Pull request", "model, sessions and cost recorded", "green")]
cw, gap = 2.3, 0.17
line(s, 0.56 + cw / 2, 2.85, 0.56 + 4 * (cw + gap) + cw / 2, 2.85, color=RGBColor(0xC9, 0xD3, 0xCF), w=2)
for i, (ic, t, sub, bg) in enumerate(steps):
    x = 0.56 + i * (cw + gap)
    icon_circle(s, ic, x + cw / 2 - 0.5, 2.35, 1.0, "DARK" if bg == "dark" else "GREEN")
    tb(s, x, 3.6, cw, 0.35, t, size=17, bold=True, color=DARK, align=PP_ALIGN.CENTER)
    tb(s, x + 0.1, 4.0, cw - 0.2, 0.6, sub, size=13, color=MUTED, align=PP_ALIGN.CENTER)
pill(s, "≈ 6 min · live", 0.56, 5.4, 2.2, 0.42, kind="green", size=13)
pill(s, "Steps 2–5 · Built", 2.95, 5.4, 2.4, 0.42, kind="dark", size=13)

# ================= Demo 2 =================
s = new_slide("Demo 2", "DEMO", "CI re-run: fix or refuse, then the report (≈ 5 min · pre-run results)",
              "Now the CI regression run, with no AI. The original version is green. In the second version a button's ID was renamed: the test goes red, the AI looks at the real screen, sees the button is still there with a new ID, "
              "and proposes a PR that fixes the selector. Re-run is green. In the third version the app calculates a value wrongly: the test is also red, but this time the AI refuses to fix it, because it is the app that is wrong. "
              "The test stays red and goes to a human. Finally, the report for the run.\n\n"
              "NOTES: A full 21-flow run takes ~12 min, so use the smoke group (6 flows) or a recording. Run step 7 live only if you have measured it at under ~2 min (not measured yet). "
              "Fallback that works today: SCRUM-7, a real app bug whose test stays red (tagged known-bug with a ticket key, excluded from CI).")
steps = [("FaCheckCircle", "CI re-run", "original build → green", "green"),
         ("FaWrench", "ID renamed → red", "AI patches the selector with evidence → green", "dark"),
         ("FaBan", "Real defect → red", "AI refuses; a human takes over", "dark"),
         ("FaFileAlt", "Report", "model, attempts, cost, approver", "green")]
cw, gap = 2.9, 0.2
line(s, 0.56 + cw / 2, 2.85, 0.56 + 3 * (cw + gap) + cw / 2, 2.85, color=RGBColor(0xC9, 0xD3, 0xCF), w=2)
for i, (ic, t, sub, bg) in enumerate(steps):
    x = 0.56 + i * (cw + gap)
    icon_circle(s, ic, x + cw / 2 - 0.5, 2.35, 1.0, "DARK" if bg == "dark" else "GREEN")
    tb(s, x, 3.6, cw, 0.35, t, size=17, bold=True, color=DARK, align=PP_ALIGN.CENTER)
    tb(s, x + 0.15, 4.0, cw - 0.3, 0.8, sub, size=13, color=MUTED, align=PP_ALIGN.CENTER)
pill(s, "≈ 5 min · pre-run results", 0.56, 5.4, 3.2, 0.42, kind="green", size=13)
pill(s, "Step 6 built · Steps 7–8 designed", 3.95, 5.4, 4.2, 0.42, kind="dark", size=13)

# ================= S7 heal vs refuse =================
s = new_slide("Fix or Refuse", "DEMO", "The key point: knowing when NOT to fix",
              "This is what I want you to remember. Making a test green is easy; an AI can do it right away. The hard part is knowing when not to. "
              "A self-healing tool that cannot tell ‘the UI moved’ from ‘the app is wrong’ turns every real bug into a green test. "
              "That is why we limit it tightly and leave every other case to a human.\n\n"
              "NOTES: This answers 'fake self-healing'. Swap the examples to match the two demo builds once built. Technical detail only if asked (designed): max 2 attempts · the case must be re-run · "
              "a patch that makes the test check less is rejected automatically · the output is always a PR. You can drop this slide if you need time; Demo 2 already makes the point.")
cols = [("GREEN", "FaCheckCircle", "AI may fix on its own", "The UI changed but the app is still correct. Example: a button's ID was renamed.",
         "Update the selector with evidence from the real screen, re-run, open a PR for review."),
        ("DARK", "FaBan", "AI must refuse and hand over", "The app behaves wrongly. Example: a displayed number is wrong.",
         "The test stays red; a human classifies it as A / B / C / D.")]
for i, (bg, ic, h, ex, act) in enumerate(cols):
    x = 0.56 + i * 6.2
    card(s, x, 1.75, 6.0, 3.0, name=h)
    icon_circle(s, ic, x + 0.3, 1.95, 0.75, bg)
    tb(s, x + 1.25, 1.95, 4.5, 0.75, h, size=22, bold=True, color=DARK, anchor=MSO_ANCHOR.MIDDLE)
    tb(s, x + 0.3, 2.95, 5.4, 0.25, "EXAMPLE", size=11, bold=True, color=MUTED)
    tb(s, x + 0.3, 3.22, 5.4, 0.6, ex, size=15, color=TEXT)
    tb(s, x + 0.3, 3.85, 5.4, 0.25, "ACTION", size=11, bold=True, color=MUTED)
    tb(s, x + 0.3, 4.12, 5.4, 0.6, act, size=15, bold=True, color=TEXT)
card(s, 0.56, 4.95, 11.1, 1.25, fill=DARK, name="Key line")
tb(s, 0.9, 4.95, 10.4, 1.25, "Making a test green is easy; the hard part is telling “the UI moved” from “the app is wrong”.",
   size=22, bold=True, color=WHITE, anchor=MSO_ANCHOR.MIDDLE)

# ================= S8 evaluation =================
s = new_slide("Effectiveness", "EVALUATION", "What exists, what we aim for, what the pilot will measure",
              "I split this plainly: what exists, starting targets, and what we have not measured. What exists: every rule has a test case, because code blocks the pipeline otherwise. "
              "The starting targets are a place to begin the conversation with you, not an industry standard. The only reference I have is Meta's study: 57 percent of AI-generated tests ran reliably. "
              "Those are unit tests, so a different domain; I use it only as a sanity check on our 60 percent target. For machine time and maintenance effort I set no number in advance, "
              "because I want the pilot to answer with your own data.\n\n"
              "NOTES: Basis for >=60%: 3/5 unattended runs (SCRUM-8, 12, 13 green; SCRUM-9 fake green and SCRUM-11 infrastructure fault, both fixed) and Meta 57%. Both are small samples or a different domain. "
              "Meta: Alshahwan et al., Automated Unit Test Improvement using LLMs at Meta (arXiv 2402.09171, FSE 2024 Industry): 75% built, 57% passed reliably, 25% increased coverage, 73% accepted. Re-read the paper before citing it. "
              "Do not use 'maintenance is 40-70% of effort' (vendor blogs only). '2/2 right' and '0 masking' are design targets on 2 known-answer builds, not statistics. Do not claim reduced QA effort or better defect detection.")
data = [
    ("Measure", "Exists (ShopDemo)", "Starting target for the pilot"),
    ("Every rule has a test case", "Code blocks if missing · 8 tickets, 32 flows", "100% (enforced by code)"),
    ("Tickets reaching a green PR with no human fixing a flow", "3 of 5 runs", "≥ 60% (reference: Meta 57%¹)"),
    ("“Fake green”", "1 case, fixed", "0"),
    ("Self-fix: right or wrong", "Not measured yet (2 known-answer builds)", "2 of 2 right · 0 masking a real bug"),
    ("Machine time, maintenance effort", "ShopDemo: 4–5 min per ticket; maintenance not measured", "No number in advance: the pilot measures"),
]
gt = s.shapes.add_table(6, 3, Inches(0.56), Inches(1.75), Inches(12.2), Inches(3.6))
gt.name = "Evaluation table"
tbl = gt.table
for j, wv in enumerate((4.2, 4.2, 3.8)):
    tbl.columns[j].width = Inches(wv)
for i in range(6):
    tbl.rows[i].height = Inches(0.45 if i == 0 else 0.63)
    for j in range(3):
        c = tbl.cell(i, j)
        c.margin_left = c.margin_right = Inches(0.12)
        c.margin_top = c.margin_bottom = Inches(0.04)
        c.vertical_anchor = MSO_ANCHOR.MIDDLE
        c.fill.solid()
        c.fill.fore_color.rgb = DARK if i == 0 else (GRAY if i % 2 == 0 else WHITE)
        tf = c.text_frame
        tf.word_wrap = True
        p = tf.paragraphs[0]
        p.alignment = PP_ALIGN.LEFT
        r = p.add_run()
        r.text = data[i][j]
        r.font.size = Pt(14)
        r.font.bold = (i == 0 or j in (0, 2))
        r.font.color.rgb = WHITE if i == 0 else (DARK if j in (0, 2) else TEXT)
tb(s, 0.56, 5.5, 11.0, 0.3, "How we measure in the pilot: the same 10–15 real tickets, the same app, the same reviewers", size=15, bold=True, color=DARK)
card(s, 0.56, 5.88, 5.0, 0.5, name="Arm A")
tb(s, 0.8, 5.88, 4.6, 0.5, "Arm A · Current way of working", size=14, bold=True, color=DARK, anchor=MSO_ANCHOR.MIDDLE)
shape(s, MSO_SHAPE.OVAL, 5.68, 5.88, 0.5, 0.5, fill=GREEN)
tb(s, 5.68, 5.88, 0.5, 0.5, "VS", size=12, bold=True, color=DARK, align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
card(s, 6.3, 5.88, 5.0, 0.5, fill=DARK, name="Arm B")
tb(s, 6.55, 5.88, 4.6, 0.5, "Arm B · With AI", size=14, bold=True, color=WHITE, anchor=MSO_ANCHOR.MIDDLE)
tb(s, 0.56, 6.55, 10.8, 0.3, "¹ Meta TestGen-LLM (FSE 2024): 57% of AI-generated tests ran reliably. Those are unit tests, a different domain: a reference only.", size=11, color=MUTED)

# ================= S9 governance =================
s = new_slide("Governance", "GOVERNANCE & SCALE-UP", "Audit trail, data handling and current limits",
              "On audit: every PR states which model did the work and what it cost, and who approved is in the Jira history. On data: we use no real customer data. "
              "One thing is not done and I want to say it now: we have not yet reviewed data residency and the EU AI Act, and that must be confirmed before a pilot. "
              "The limits are on the slide: one app, iOS only, five runs. I say this plainly because the pilot is designed to answer exactly the points we are unsure about.\n\n"
              "NOTES: Say the limits yourself; it is better coming from you than from the audience. Only if asked: GitHub branch protection is not verified; bin/qa-auto has no tests of its own; flows still hard-code demo credentials.")
left = [("FaHistory", "Audit", "The PR records model, sessions and total cost; approvals are in the Jira history."),
        ("FaLock", "Data", "No real customer or rider data; credentials only in machine config and CI secrets."),
        ("FaCodeBranch", "Traceability", "ticket → spec → case → flow → PR. A report per run (step 8) is designed.")]
for i, (ic, t, d) in enumerate(left):
    y = 1.75 + i * 1.17
    card(s, 0.56, y, 5.7, 1.05, name=t)
    icon_circle(s, ic, 0.78, y + 0.2, 0.65, "GREEN")
    tb(s, 1.65, y + 0.1, 4.45, 0.3, t, size=16, bold=True, color=DARK)
    tb(s, 1.65, y + 0.42, 4.45, 0.6, d, size=13, color=TEXT)
card(s, 0.56, 5.3, 5.7, 1.0, fill=DARK, name="Not done")
icon_circle(s, "FaGlobeEurope", 0.78, 5.5, 0.6, "GREEN")
tb(s, 1.6, 5.3, 4.5, 1.0, [("Not done yet: ", {"bold": True, "color": GREEN}), ("data residency and EU AI Act review. To be confirmed before the pilot.", {})],
   size=14, color=WHITE, anchor=MSO_ANCHOR.MIDDLE)
tb(s, 6.65, 1.7, 6.1, 0.35, "Current limits", size=18, bold=True, color=DARK)
lim = ["One app (ShopDemo), iOS only; no Android yet",
       "Steps 7 (diagnose) and 8 (report) are not built",
       "Only 5 runs, 1 app, 1 operator",
       "No daily spend cap yet",
       "Assertions are checked by PR review and rule coverage; no code check that each approved result became an assertion",
       "Personal Jira/GitHub accounts; the pilot needs a service account and a neutral CI runner"]
for i, t in enumerate(lim):
    y = 2.15 + i * 0.68
    card(s, 6.65, y, 6.1, 0.62, name=f"Limit {i+1}")
    icon_circle(s, "FaExclamationTriangle", 6.78, y + 0.12, 0.38, "GREEN")
    tb(s, 7.3, y, 5.35, 0.62, t, size=13, color=TEXT, anchor=MSO_ANCHOR.MIDDLE)

# ================= S10 roadmap + pilot =================
s = new_slide("Roadmap & Pilot", "GOVERNANCE & SCALE-UP", "Where we go next, and a pilot that answers the open questions",
              "The next step is a small pilot: one app, ten to fifteen real tickets, four to six weeks. I estimate the AI cost at roughly ten to seventy dollars for the whole trial, "
              "and that number will be replaced by measured data. What we bring is not just ‘we use AI’, but discipline around the AI: the test tool decides, humans own the gates, limits are in code, "
              "and we publish the numbers even when they are not yet good. Thank you.\n\n"
              "NOTES: Roadmap item 3 has not started; it comes only after 1 and 2. Do not claim reduced QA effort or better defect detection: those are hypotheses the pilot tests.")
road = [("App 2 + Android", "The multi-app layout already exists"),
        ("Parallel runs", "Neutral CI runner, CI sharding, daily spend cap, service account"),
        ("More model providers", "Enterprise authentication"),
        ("Closed loop", "CI failure → ticket → fix PR → report")]
cw = 2.95
for i, (t, d) in enumerate(road):
    x = 0.56 + i * (cw + 0.13)
    card(s, x, 1.75, cw, 1.7, name=f"Roadmap {i+1}")
    shape(s, MSO_SHAPE.OVAL, x + 0.2, 1.9, 0.42, 0.42, fill=DARK)
    tb(s, x + 0.2, 1.9, 0.42, 0.42, str(i + 1), size=15, bold=True, color=WHITE, align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
    tb(s, x + 0.2, 2.4, cw - 0.4, 0.3, t, size=15, bold=True, color=DARK)
    tb(s, x + 0.2, 2.75, cw - 0.4, 0.65, d, size=13, color=MUTED)
tb(s, 0.56, 3.65, 11.5, 0.35, "Proposed pilot: 1 app · 10–15 real tickets · 4–6 weeks", size=18, bold=True, color=DARK)
wk = 12.2 / 7
segs = [(0, 2, "green", "Weeks 0–1 · Setup", "build, Jira + service account, repo, test accounts"),
        (2, 4, "dark", "Weeks 1–5 · Run both arms", "weekly review of gates, reds and cost"),
        (6, 1, "outline", "Week 6", "Report")]
for a, n, kind, t, sub in segs:
    x = 0.56 + a * wk
    if kind == "green":
        shape(s, MSO_SHAPE.ROUNDED_RECTANGLE, x + 0.03, 4.1, n * wk - 0.06, 0.9, fill=GREEN, radius=0.1); col = DARK
    elif kind == "dark":
        shape(s, MSO_SHAPE.ROUNDED_RECTANGLE, x + 0.03, 4.1, n * wk - 0.06, 0.9, fill=DARK, radius=0.1); col = WHITE
    else:
        shape(s, MSO_SHAPE.ROUNDED_RECTANGLE, x + 0.03, 4.1, n * wk - 0.06, 0.9, fill=WHITE, line=GREEN, line_w=2.5, radius=0.1); col = DARK
    tb(s, x + 0.2, 4.1, n * wk - 0.4, 0.9, [[(t, {"bold": True, "size": 14})], [(sub, {"size": 12})]], color=col, anchor=MSO_ANCHOR.MIDDLE)
card(s, 0.56, 5.25, 5.5, 0.7, name="Cost chip")
icon_circle(s, "FaDollarSign", 0.72, 5.37, 0.46, "DARK")
tb(s, 1.35, 5.25, 4.6, 0.7, [("AI cost ~$10–70 ", {"bold": True}), ("for the whole trial (excluding CI and people time)", {})], size=13, color=TEXT, anchor=MSO_ANCHOR.MIDDLE)
card(s, 6.25, 5.25, 5.5, 0.7, name="Criteria chip")
icon_circle(s, "FaFlag", 6.41, 5.37, 0.46, "DARK")
tb(s, 7.04, 5.25, 4.6, 0.7, [("Continue / stop / widen criteria ", {"bold": True}), ("agreed in advance", {})], size=13, color=TEXT, anchor=MSO_ANCHOR.MIDDLE)

# ================= Closing (cover layout) =================
s = prs.slides.add_slide(LAYOUT_COVER)
tb(s, 1.5, 4.95, 10.33, 0.8, "Thank you · Q&A", size=34, bold=True, color=WHITE, align=PP_ALIGN.CENTER)
tb(s, 1.5, 5.75, 10.33, 0.5, "AI proposes  ·  Humans approve  ·  The test runner decides", size=18, color=GREEN, align=PP_ALIGN.CENTER)
s.notes_slide.notes_text_frame.text = ("Thank you. Three ideas to take away: the AI proposes, humans hold the gates, and the test runner, not the AI, decides pass or fail.")

# ---- final: unique, sequential slide part names ----
for i, sl in enumerate(prs.slides):
    sl.part.partname = PackURI(f"/ppt/slides/slide{i+1}.xml")
prs.core_properties.title = "AI Proposes, the Runner Decides"
prs.save(OUT)
print("saved", OUT, len(prs.slides), "slides")
