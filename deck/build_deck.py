"""Generate the You Know ____ Is a Lot Like ____ presentation as PPTX."""

from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE

# ── colours ──────────────────────────────────────────────────────────────────
BG_DARK   = RGBColor(0x0A, 0x0A, 0x1A)
BG_SECT1  = RGBColor(0x0A, 0x0A, 0x2E)
BG_SECT2  = RGBColor(0x0A, 0x1A, 0x0A)
BG_SECT3  = RGBColor(0x1A, 0x0A, 0x0A)
BG_SECT4  = RGBColor(0x0A, 0x0A, 0x1A)
ACCENT    = RGBColor(0x50, 0xE6, 0xFF)
ACCENT2   = RGBColor(0xFF, 0x8C, 0x00)
WHITE     = RGBColor(0xFF, 0xFF, 0xFF)
GREY      = RGBColor(0xAA, 0xAA, 0xAA)
LIGHT_GREY = RGBColor(0xCC, 0xCC, 0xCC)
CARD_BG   = RGBColor(0x1A, 0x1A, 0x30)
CARD_BG2  = RGBColor(0x2A, 0x1A, 0x10)

prs = Presentation()
prs.slide_width  = Inches(13.333)
prs.slide_height = Inches(7.5)
W = prs.slide_width
H = prs.slide_height

# ── helpers ──────────────────────────────────────────────────────────────────

def set_bg(slide, color):
    bg = slide.background
    fill = bg.fill
    fill.solid()
    fill.fore_color.rgb = color

def add_text_box(slide, left, top, width, height, text, font_size=18,
                 color=WHITE, bold=False, alignment=PP_ALIGN.LEFT,
                 font_name="Segoe UI"):
    txBox = slide.shapes.add_textbox(left, top, width, height)
    tf = txBox.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = text
    p.font.size = Pt(font_size)
    p.font.color.rgb = color
    p.font.bold = bold
    p.font.name = font_name
    p.alignment = alignment
    return txBox

def add_para(text_frame, text, font_size=18, color=WHITE, bold=False,
             alignment=PP_ALIGN.LEFT, space_before=Pt(6), font_name="Segoe UI"):
    p = text_frame.add_paragraph()
    p.text = text
    p.font.size = Pt(font_size)
    p.font.color.rgb = color
    p.font.bold = bold
    p.font.name = font_name
    p.alignment = alignment
    p.space_before = space_before
    return p

def add_rounded_rect(slide, left, top, width, height, fill_color, text="",
                     font_size=14, font_color=WHITE, bold=False,
                     alignment=PP_ALIGN.CENTER, border_color=None):
    shape = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, height)
    shape.fill.solid()
    shape.fill.fore_color.rgb = fill_color
    if border_color:
        shape.line.color.rgb = border_color
        shape.line.width = Pt(1.5)
    else:
        shape.line.fill.background()
    tf = shape.text_frame
    tf.word_wrap = True
    tf.paragraphs[0].alignment = alignment
    if text:
        tf.paragraphs[0].text = text
        tf.paragraphs[0].font.size = Pt(font_size)
        tf.paragraphs[0].font.color.rgb = font_color
        tf.paragraphs[0].font.bold = bold
        tf.paragraphs[0].font.name = "Segoe UI"
    return shape

def add_section_label(slide, text):
    add_text_box(slide, Inches(0.8), Inches(0.5), Inches(11), Inches(0.5),
                 text, font_size=14, color=ACCENT2, bold=False,
                 alignment=PP_ALIGN.CENTER)

def add_notes(slide, text):
    notes_slide = slide.notes_slide
    notes_slide.notes_text_frame.text = text

def add_research_card(slide, top, finding, cite):
    card = add_rounded_rect(slide, Inches(0.8), top, Inches(11.7), Inches(1.1),
                            CARD_BG2, border_color=ACCENT2)
    tf = card.text_frame
    tf.word_wrap = True
    tf.paragraphs[0].text = finding
    tf.paragraphs[0].font.size = Pt(15)
    tf.paragraphs[0].font.color.rgb = WHITE
    tf.paragraphs[0].font.bold = True
    tf.paragraphs[0].font.name = "Segoe UI"
    p2 = tf.add_paragraph()
    p2.text = cite
    p2.font.size = Pt(11)
    p2.font.color.rgb = GREY
    p2.font.name = "Segoe UI"
    p2.space_before = Pt(4)

def add_bullet_slide(slide, title, bullets, notes_text, bg=BG_DARK,
                     title_color=ACCENT, bullet_color=WHITE):
    set_bg(slide, bg)
    add_text_box(slide, Inches(0.8), Inches(0.4), Inches(11), Inches(0.8),
                 title, font_size=36, color=title_color, bold=True)
    txBox = add_text_box(slide, Inches(1.0), Inches(1.5), Inches(11), Inches(5.5),
                         "", font_size=22, color=bullet_color)
    tf = txBox.text_frame
    tf.word_wrap = True
    for i, b in enumerate(bullets):
        if i == 0:
            tf.paragraphs[0].text = f"\u25b8  {b}"
            tf.paragraphs[0].font.size = Pt(22)
            tf.paragraphs[0].font.color.rgb = bullet_color
            tf.paragraphs[0].font.name = "Segoe UI"
            tf.paragraphs[0].space_before = Pt(12)
        else:
            add_para(tf, f"\u25b8  {b}", font_size=22, color=bullet_color,
                     space_before=Pt(12))
    add_notes(slide, notes_text)

# ═══════════════════════════════════════════════════════════════════════════════
#  SLIDE 1 — TITLE
# ═══════════════════════════════════════════════════════════════════════════════
s = prs.slides.add_slide(prs.slide_layouts[6])  # blank
set_bg(s, BG_SECT1)
add_text_box(s, Inches(0.5), Inches(0.8), Inches(12.3), Inches(0.5),
             "INTRODUCING", font_size=14, color=ACCENT2, bold=False,
             alignment=PP_ALIGN.CENTER)
add_text_box(s, Inches(0.5), Inches(1.8), Inches(12.3), Inches(2.5),
             "You Know ____\nIs a Lot Like ____",
             font_size=54, color=ACCENT, bold=True, alignment=PP_ALIGN.CENTER)
add_text_box(s, Inches(0.5), Inches(4.8), Inches(12.3), Inches(1),
             "A game that makes technical depth visible,\nshareable, and fun.",
             font_size=22, color=GREY, alignment=PP_ALIGN.CENTER)
add_notes(s,
    "Keep this up for a beat. Let people read it.\n\n"
    "\"This is a game we built for CSA teams. It's fast, it's funny, and it's backed "
    "by real research on how technical teams learn and connect. I'm going to walk you "
    "through the problem it solves, how it works, why the science says it works, and "
    "then we're going to play a live round.\"")

# ═══════════════════════════════════════════════════════════════════════════════
#  SLIDE 2 — SECTION 1 HEADER: The Situation
# ═══════════════════════════════════════════════════════════════════════════════
s = prs.slides.add_slide(prs.slide_layouts[6])
set_bg(s, BG_SECT1)
add_section_label(s, "SECTION 1")
add_text_box(s, Inches(0.5), Inches(2.2), Inches(12.3), Inches(2),
             "The Situation", font_size=54, color=ACCENT, bold=True,
             alignment=PP_ALIGN.CENTER)
add_text_box(s, Inches(0.5), Inches(4.5), Inches(12.3), Inches(1),
             "A story in three acts.",
             font_size=22, color=GREY, alignment=PP_ALIGN.CENTER)
add_notes(s,
    "\"Before I show you the game, let me tell you three quick stories. "
    "These are composites, but I bet every one of you has lived at least one of them.\"")

# ═══════════════════════════════════════════════════════════════════════════════
#  SLIDE 3 — Act 1: The Brilliant CSA
# ═══════════════════════════════════════════════════════════════════════════════
s = prs.slides.add_slide(prs.slide_layouts[6])
set_bg(s, BG_DARK)
add_text_box(s, Inches(0.8), Inches(0.4), Inches(11), Inches(0.8),
             "Act 1: The Brilliant CSA", font_size=36, color=ACCENT, bold=True)
txBox = add_text_box(s, Inches(1.0), Inches(1.5), Inches(11), Inches(2),
             "Meet our CSA. They've spent three weeks designing a multi-region "
             "landing zone with private endpoints, managed identity, and a governance "
             "model that would make a compliance officer weep with joy.",
             font_size=22, color=WHITE)
add_text_box(s, Inches(1.0), Inches(3.3), Inches(11), Inches(0.8),
             "They present it to the customer's VP of Engineering.",
             font_size=22, color=WHITE)
add_text_box(s, Inches(1.0), Inches(4.3), Inches(11), Inches(0.8),
             "Twelve minutes in, the VP's eyes glaze over.",
             font_size=22, color=WHITE)
add_text_box(s, Inches(1.5), Inches(5.5), Inches(10), Inches(0.8),
             "\"So\u2026 is this like building a house?\"",
             font_size=30, color=ACCENT2, bold=True, alignment=PP_ALIGN.CENTER)
add_notes(s,
    "Tell this like a story, not a slide read. Pace it out.\n\n"
    "\"We've got a CSA — they are incredible. Three weeks deep into a multi-region "
    "landing zone. Private endpoints, managed identity, governance model, the whole "
    "thing. Technically flawless.\"\n\n"
    "Pause before revealing each line.\n\n"
    "\"They present it to the customer's VP of Engineering. Twelve minutes in, the "
    "VP's eyes glaze over.\"\n\n"
    "Let the punchline land: \"So\u2026 is this like building a house?\"\n\n"
    "The point: the depth was real, but the translation wasn't there. Not because "
    "they lack skill — because they've never had a reason to practice explaining it "
    "outside of a high-stakes customer meeting.")

# ═══════════════════════════════════════════════════════════════════════════════
#  SLIDE 4 — Act 2: The Team Call
# ═══════════════════════════════════════════════════════════════════════════════
s = prs.slides.add_slide(prs.slide_layouts[6])
set_bg(s, BG_DARK)
add_text_box(s, Inches(0.8), Inches(0.4), Inches(11), Inches(0.8),
             "Act 2: The Team Call", font_size=36, color=ACCENT, bold=True)
add_text_box(s, Inches(1.0), Inches(1.5), Inches(11), Inches(1.5),
             "Monday standup. Eight CSAs on camera. One shares a war story about "
             "debugging a Fabric lakehouse mirroring issue that took four days.",
             font_size=22, color=WHITE)
add_text_box(s, Inches(1.0), Inches(3.2), Inches(11), Inches(1.2),
             "Three teammates nod knowingly.\nThe other four check Outlook.",
             font_size=22, color=WHITE)
add_text_box(s, Inches(1.0), Inches(4.6), Inches(11), Inches(1.2),
             "Not because they don't care — because the story was told in a "
             "language only half the room speaks fluently.",
             font_size=22, color=WHITE)
add_text_box(s, Inches(1.5), Inches(6.0), Inches(10), Inches(0.7),
             "Deep expertise. Shallow connection.",
             font_size=30, color=ACCENT2, bold=True, alignment=PP_ALIGN.CENTER)
add_notes(s,
    "\"Monday standup. Eight people on camera. Someone shares a war story about a "
    "Fabric lakehouse mirroring issue that ate four days of their life.\"\n\n"
    "\"Three teammates nod — they've been there. The other four are checking Outlook. "
    "Not because they're disengaged. Because the story was told in a dialect only "
    "half the room speaks.\"\n\n"
    "Emphasize the tagline: \"Deep expertise. Shallow connection.\"\n\n"
    "The point: we have brilliant people who can't always share what they know in a "
    "way that connects across specialties.")

# ═══════════════════════════════════════════════════════════════════════════════
#  SLIDE 5 — Act 3: The Offsite Icebreaker
# ═══════════════════════════════════════════════════════════════════════════════
s = prs.slides.add_slide(prs.slide_layouts[6])
set_bg(s, BG_DARK)
add_text_box(s, Inches(0.8), Inches(0.4), Inches(11), Inches(0.8),
             "Act 3: The Offsite Icebreaker", font_size=36, color=ACCENT, bold=True)
add_text_box(s, Inches(1.0), Inches(1.8), Inches(11), Inches(1),
             "Someone suggests \"two truths and a lie.\" Again.",
             font_size=24, color=WHITE)
add_text_box(s, Inches(1.0), Inches(3.2), Inches(11), Inches(1.5),
             "It has nothing to do with the work. It doesn't make anyone "
             "better at their job. But hey — at least it's awkward for everyone equally.",
             font_size=22, color=WHITE)
add_text_box(s, Inches(1.0), Inches(5.2), Inches(11.3), Inches(1.2),
             "What if the team activity actually used\nthe thing CSAs are best at?",
             font_size=30, color=ACCENT, bold=True, alignment=PP_ALIGN.CENTER)
add_notes(s,
    "Play this for the laugh. Everyone in the room has done \"two truths and a lie\" "
    "too many times.\n\n"
    "\"Someone suggests two truths and a lie. Again. It has nothing to do with the "
    "actual work. Doesn't make anyone better at their job. But hey — at least it's "
    "equally awkward for everyone.\"\n\n"
    "Then land the reframe: \"What if the team activity actually used the thing "
    "CSAs are best at?\"")

# ═══════════════════════════════════════════════════════════════════════════════
#  SLIDE 6 — The Pattern
# ═══════════════════════════════════════════════════════════════════════════════
s = prs.slides.add_slide(prs.slide_layouts[6])
set_bg(s, BG_DARK)
add_text_box(s, Inches(0.8), Inches(0.4), Inches(11), Inches(0.8),
             "The Pattern", font_size=36, color=ACCENT, bold=True)
add_text_box(s, Inches(0.5), Inches(1.3), Inches(12.3), Inches(0.6),
             "Three scenes, one problem:", font_size=24, color=WHITE,
             alignment=PP_ALIGN.CENTER)

labels = [
    ("\U0001f9e0", "CSAs have\nmassive depth"),
    ("\U0001f507", "But rarely practice\ntranslating it"),
    ("\U0001f9ca", "And team activities\nignore the depth"),
]
box_w = Inches(3.5)
gap = Inches(0.5)
total = box_w * 3 + gap * 2
start_x = (W - total) // 2
for i, (icon, label) in enumerate(labels):
    x = start_x + i * (box_w + gap)
    shape = add_rounded_rect(s, x, Inches(2.5), box_w, Inches(3.5),
                              CARD_BG, border_color=ACCENT)
    tf = shape.text_frame
    tf.word_wrap = True
    tf.paragraphs[0].text = icon
    tf.paragraphs[0].font.size = Pt(48)
    tf.paragraphs[0].alignment = PP_ALIGN.CENTER
    p2 = tf.add_paragraph()
    p2.text = label
    p2.font.size = Pt(18)
    p2.font.color.rgb = LIGHT_GREY
    p2.alignment = PP_ALIGN.CENTER
    p2.space_before = Pt(16)

add_notes(s,
    "This is the summary of the three stories in a single visual.\n\n"
    "\"Three different scenes, one pattern. We have deep expertise that doesn't "
    "get exercised in translation, and our team activities don't tap into it at all.\"")

# ═══════════════════════════════════════════════════════════════════════════════
#  SLIDE 7 — Why This Happens — The Research
# ═══════════════════════════════════════════════════════════════════════════════
s = prs.slides.add_slide(prs.slide_layouts[6])
set_bg(s, BG_DARK)
add_text_box(s, Inches(0.8), Inches(0.4), Inches(11), Inches(0.8),
             "Why This Happens \u2014 The Research", font_size=36, color=ACCENT, bold=True)

add_research_card(s, Inches(1.5),
    "The Curse of Knowledge: once you understand something deeply, you lose the "
    "ability to imagine not understanding it \u2014 making it systematically harder to explain.",
    "Camerer, Loewenstein & Weber (1989). Journal of Political Economy.")
add_research_card(s, Inches(2.9),
    "The Illusion of Explanatory Depth: people consistently overestimate how well "
    "they can explain the systems they work with \u2014 until asked to do it out loud.",
    "Rozenblit & Keil (2002). Cognitive Science.")
add_research_card(s, Inches(4.3),
    "Expert Blind Spot: domain experts routinely skip steps and use jargon they "
    "no longer notice, creating communication failures with non-experts.",
    "Nathan & Petrosino (2003). Journal of the Learning Sciences.")

add_notes(s,
    "Shift tone here — go from storytelling to \"here's why this isn't just an anecdote.\"\n\n"
    "Curse of Knowledge: \"Once you understand something deeply, you literally lose "
    "the ability to imagine not understanding it. This isn't a character flaw — it's "
    "a documented cognitive bias. Camerer, Loewenstein, and Weber proved it in 1989.\"\n\n"
    "Illusion of Explanatory Depth: \"We all think we can explain the systems we work "
    "with. Rozenblit and Keil showed that people consistently overestimate their "
    "explanatory ability — until you actually ask them to do it.\"\n\n"
    "Expert Blind Spot: \"Nathan and Petrosino found that domain experts routinely "
    "skip steps and use jargon they don't even notice anymore. It's not laziness — "
    "it's what expertise does to your communication.\"\n\n"
    "The point: this is a structural problem, not a people problem.")

# ═══════════════════════════════════════════════════════════════════════════════
#  SLIDE 8 — What Doesn't Fix It
# ═══════════════════════════════════════════════════════════════════════════════
s = prs.slides.add_slide(prs.slide_layouts[6])
add_bullet_slide(s, "What Doesn\u2019t Fix It", [
    "More slide decks \u2014 passive review doesn't build communication skill",
    "Generic icebreakers \u2014 fun, but don't exercise technical thinking",
    "Trivia nights \u2014 reward memorization, punish newcomers",
    "Presentation practice \u2014 useful, but high-stakes and time-intensive",
],
    "Run through each bullet quickly — the audience will recognize all of these.\n\n"
    "Slide decks: \"Passive consumption. You don't build communication muscle by "
    "watching slides.\"\n\n"
    "Generic icebreakers: \"Fun in the moment, but they don't exercise the technical "
    "thinking that makes CSAs valuable.\"\n\n"
    "Trivia nights: \"Rewards memorization. Punishes newcomers. Doesn't help you "
    "explain anything.\"\n\n"
    "Presentation practice: \"Actually useful — but high-stakes, time-intensive, "
    "and hard to do frequently.\"\n\n"
    "Land the closer: \"What you need is something low-stakes, high-frequency, "
    "and that rewards real technical understanding.\"",
    bg=BG_DARK, bullet_color=ACCENT2)

# add the closer text
add_text_box(s, Inches(1.0), Inches(5.5), Inches(11), Inches(1),
             "You need something low-stakes, high-frequency,\n"
             "and that rewards real technical understanding.",
             font_size=24, color=ACCENT, bold=True, alignment=PP_ALIGN.CENTER)

# ═══════════════════════════════════════════════════════════════════════════════
#  SLIDE 9 — Bridge
# ═══════════════════════════════════════════════════════════════════════════════
s = prs.slides.add_slide(prs.slide_layouts[6])
set_bg(s, BG_SECT1)
add_rounded_rect(s, Inches(1), Inches(1.8), Inches(11.3), Inches(3.5),
                 CARD_BG2, border_color=ACCENT2)
add_text_box(s, Inches(1.5), Inches(2.2), Inches(10.3), Inches(3),
             "What if one game could exercise\ndeep knowledge, "
             "customer-ready communication,\nteam connection, "
             "and creative thinking \u2014\nall at once?",
             font_size=32, color=ACCENT, bold=False, alignment=PP_ALIGN.CENTER)
add_notes(s,
    "Let this slide breathe. Don't rush it.\n\n"
    "\"What if one game could exercise deep knowledge, customer-ready communication, "
    "team connection, and creative thinking — all in 90 seconds?\"\n\n"
    "Pause. Then advance to Section 2.")

# ═══════════════════════════════════════════════════════════════════════════════
#  SLIDE 10 — SECTION 2 HEADER: The Game
# ═══════════════════════════════════════════════════════════════════════════════
s = prs.slides.add_slide(prs.slide_layouts[6])
set_bg(s, RGBColor(0x0A, 0x1A, 0x1A))
add_section_label(s, "SECTION 2")
add_text_box(s, Inches(0.5), Inches(2.2), Inches(12.3), Inches(2),
             "The Game", font_size=54, color=ACCENT, bold=True,
             alignment=PP_ALIGN.CENTER)
add_text_box(s, Inches(0.5), Inches(4.5), Inches(12.3), Inches(1),
             "How it works, how it\u2019s played, how it\u2019s scored.",
             font_size=22, color=GREY, alignment=PP_ALIGN.CENTER)
add_notes(s, "\"Let me show you how it works.\"")

# ═══════════════════════════════════════════════════════════════════════════════
#  SLIDE 11 — The Format
# ═══════════════════════════════════════════════════════════════════════════════
s = prs.slides.add_slide(prs.slide_layouts[6])
set_bg(s, BG_DARK)
add_text_box(s, Inches(0.8), Inches(0.4), Inches(11), Inches(0.8),
             "The Format", font_size=36, color=ACCENT, bold=True)
prompt_box = add_rounded_rect(s, Inches(1.2), Inches(2), Inches(10.8), Inches(2.5),
                               CARD_BG, border_color=ACCENT)
tf = prompt_box.text_frame
tf.word_wrap = True
tf.paragraphs[0].text = "\"You know "
tf.paragraphs[0].font.size = Pt(32)
tf.paragraphs[0].font.color.rgb = WHITE
tf.paragraphs[0].font.name = "Segoe UI"
tf.paragraphs[0].alignment = PP_ALIGN.CENTER

from pptx.util import Pt as _Pt
run = tf.paragraphs[0].add_run()
run.text = "[technical thing]"
run.font.size = Pt(32)
run.font.color.rgb = ACCENT2
run.font.bold = True
run.font.name = "Segoe UI"

run2 = tf.paragraphs[0].add_run()
run2.text = "\nis a lot like "
run2.font.size = Pt(32)
run2.font.color.rgb = WHITE
run2.font.name = "Segoe UI"

run3 = tf.paragraphs[0].add_run()
run3.text = "[everyday thing]"
run3.font.size = Pt(32)
run3.font.color.rgb = ACCENT2
run3.font.bold = True
run3.font.name = "Segoe UI"

run4 = tf.paragraphs[0].add_run()
run4.text = ".\""
run4.font.size = Pt(32)
run4.font.color.rgb = WHITE
run4.font.name = "Segoe UI"

add_text_box(s, Inches(0.5), Inches(5.2), Inches(12.3), Inches(0.8),
             "Then you have to explain why.",
             font_size=24, color=WHITE, alignment=PP_ALIGN.CENTER)
add_notes(s,
    "Read the format out loud in a game-show voice: "
    "\"You know [technical thing] is a lot like [everyday thing].\"\n\n"
    "\"Two blanks. One from the world of what CSAs actually do. One from everyday "
    "life. Your job is to connect them — and make it make sense.\"")

# ═══════════════════════════════════════════════════════════════════════════════
#  SLIDE 12 — Example
# ═══════════════════════════════════════════════════════════════════════════════
s = prs.slides.add_slide(prs.slide_layouts[6])
set_bg(s, BG_DARK)
add_text_box(s, Inches(0.8), Inches(0.4), Inches(11), Inches(0.8),
             "Example", font_size=36, color=ACCENT, bold=True)

ex_box = add_rounded_rect(s, Inches(1.2), Inches(1.5), Inches(10.8), Inches(2),
                           CARD_BG, border_color=ACCENT)
tf = ex_box.text_frame
tf.word_wrap = True
tf.paragraphs[0].alignment = PP_ALIGN.CENTER

tf.paragraphs[0].text = "\"You know "
tf.paragraphs[0].font.size = Pt(26)
tf.paragraphs[0].font.color.rgb = WHITE
tf.paragraphs[0].font.name = "Segoe UI"
r = tf.paragraphs[0].add_run()
r.text = "designing a landing zone"
r.font.size = Pt(26); r.font.color.rgb = ACCENT2; r.font.bold = True; r.font.name = "Segoe UI"
r2 = tf.paragraphs[0].add_run()
r2.text = " is a lot like "
r2.font.size = Pt(26); r2.font.color.rgb = WHITE; r2.font.name = "Segoe UI"
r3 = tf.paragraphs[0].add_run()
r3.text = "hosting Thanksgiving dinner"
r3.font.size = Pt(26); r3.font.color.rgb = ACCENT2; r3.font.bold = True; r3.font.name = "Segoe UI"
r4 = tf.paragraphs[0].add_run()
r4.text = ".\""
r4.font.size = Pt(26); r4.font.color.rgb = WHITE; r4.font.name = "Segoe UI"

add_text_box(s, Inches(1.2), Inches(4.0), Inches(10.8), Inches(2.5),
             "\"Both start with a fight about the layout, involve way too many "
             "stakeholders who all think they're in charge, and if you skip the "
             "planning, someone ends up at the kids' table running production "
             "workloads.\"",
             font_size=20, color=LIGHT_GREY, alignment=PP_ALIGN.CENTER)
add_notes(s,
    "Read the full prompt: \"You know designing a landing zone is a lot like "
    "hosting Thanksgiving dinner.\"\n\n"
    "Then deliver the sample answer with energy. This is your chance to model "
    "what good looks like.\n\n"
    "\"Both start with a fight about the layout, involve way too many stakeholders "
    "who all think they're in charge, and if you skip the planning, someone ends up "
    "at the kids' table running production workloads.\"\n\n"
    "If people laugh, you've set the tone. If they groan, that works too.")

# ═══════════════════════════════════════════════════════════════════════════════
#  SLIDE 13 — How a Round Works
# ═══════════════════════════════════════════════════════════════════════════════
s = prs.slides.add_slide(prs.slide_layouts[6])
set_bg(s, BG_DARK)
add_text_box(s, Inches(0.8), Inches(0.4), Inches(11), Inches(0.8),
             "How a Round Works", font_size=36, color=ACCENT, bold=True)

steps = [
    ("\U0001f3b2  Draw two prompts", Inches(1.8)),
    ("\U0001f4d6  Read it aloud", Inches(2.7)),
    ("\U0001f914  30 seconds to think", Inches(3.6)),
    ("\U0001f3a4  60\u201390 seconds to explain", Inches(4.5)),
    ("\u2b50  Room scores", Inches(5.4)),
]
for text, top in steps:
    add_rounded_rect(s, Inches(3), top, Inches(7.3), Inches(0.7),
                     CARD_BG, text=text, font_size=20, font_color=WHITE,
                     border_color=RGBColor(0x30, 0x60, 0x80))

# arrows
for i in range(4):
    add_text_box(s, Inches(6.3), steps[i][1] + Inches(0.65), Inches(0.7), Inches(0.5),
                 "\u2193", font_size=20, color=ACCENT2, alignment=PP_ALIGN.CENTER)

add_notes(s,
    "Walk through the five steps quickly. This is mechanics, not storytelling.\n\n"
    "\"Draw two prompts. Read it out loud. Thirty seconds to think. Sixty to ninety "
    "seconds to explain. Room scores.\"\n\n"
    "Emphasize: \"It's fast. A full round takes under three minutes.\"")

# ═══════════════════════════════════════════════════════════════════════════════
#  SLIDE 14 — Scoring
# ═══════════════════════════════════════════════════════════════════════════════
s = prs.slides.add_slide(prs.slide_layouts[6])
set_bg(s, BG_DARK)
add_text_box(s, Inches(0.8), Inches(0.4), Inches(11), Inches(0.8),
             "Scoring", font_size=36, color=ACCENT, bold=True)

score_data = [
    ("Accuracy", "Does the analogy\nactually make sense?"),
    ("Creativity", "Was the connection\nunexpected and clever?"),
    ("Delivery", "Was it clear, funny,\nor memorable?"),
]
card_w = Inches(3.5)
gap = Inches(0.5)
total = card_w * 3 + gap * 2
start_x = (W - total) // 2
for i, (title, desc) in enumerate(score_data):
    x = start_x + i * (card_w + gap)
    shape = add_rounded_rect(s, x, Inches(1.8), card_w, Inches(3.8),
                              CARD_BG, border_color=RGBColor(0x30, 0x60, 0x80))
    tf = shape.text_frame
    tf.word_wrap = True
    tf.paragraphs[0].text = title
    tf.paragraphs[0].font.size = Pt(24)
    tf.paragraphs[0].font.color.rgb = ACCENT2
    tf.paragraphs[0].font.bold = True
    tf.paragraphs[0].font.name = "Segoe UI"
    tf.paragraphs[0].alignment = PP_ALIGN.CENTER
    p2 = tf.add_paragraph()
    p2.text = desc
    p2.font.size = Pt(16); p2.font.color.rgb = GREY; p2.font.name = "Segoe UI"
    p2.alignment = PP_ALIGN.CENTER; p2.space_before = Pt(12)
    p3 = tf.add_paragraph()
    p3.text = "1\u20135"
    p3.font.size = Pt(36); p3.font.color.rgb = ACCENT; p3.font.bold = True
    p3.font.name = "Segoe UI"; p3.alignment = PP_ALIGN.CENTER; p3.space_before = Pt(20)

add_text_box(s, Inches(0.5), Inches(6.2), Inches(12.3), Inches(0.7),
             "Max 15 points per round",
             font_size=24, color=ACCENT, bold=True, alignment=PP_ALIGN.CENTER)
add_notes(s,
    "\"Three categories, one to five each. Accuracy — does the analogy actually "
    "hold up technically? Creativity — was the connection surprising and clever? "
    "Delivery — was it clear, funny, or something people will repeat later?\"\n\n"
    "\"Max fifteen points per round. Simple enough to score in your head or drop "
    "in the chat.\"")

# ═══════════════════════════════════════════════════════════════════════════════
#  SLIDE 15 — Game Modes
# ═══════════════════════════════════════════════════════════════════════════════
s = prs.slides.add_slide(prs.slide_layouts[6])
set_bg(s, BG_DARK)
add_text_box(s, Inches(0.8), Inches(0.4), Inches(11), Inches(0.8),
             "Game Modes", font_size=36, color=ACCENT, bold=True)

modes = [
    ("Standard", "One player presents per round, 5 rounds", "Team meetings"),
    ("Battle", "Two players get same prompt, room votes", "Offsites"),
    ("Team", "Small teams prep together, one delivers", "Workshops"),
    ("Lightning", "15s think, 30s explain", "Energy bursts"),
    ("Customer-Friendly", "No acronyms allowed, bonus for exec clarity", "Comms training"),
]
# simple table-like layout with rounded rects
headers = ["Mode", "Format", "Best For"]
col_x = [Inches(0.8), Inches(3.5), Inches(10)]
col_w = [Inches(2.5), Inches(6.3), Inches(2.7)]
# header row
for j, h in enumerate(headers):
    add_rounded_rect(s, col_x[j], Inches(1.5), col_w[j], Inches(0.6),
                     RGBColor(0x15, 0x25, 0x45), text=h, font_size=16,
                     font_color=ACCENT, bold=True, alignment=PP_ALIGN.CENTER)
for i, (mode, fmt, best) in enumerate(modes):
    top = Inches(2.3) + Emu(int(i * Inches(0.75)))
    add_text_box(s, col_x[0] + Inches(0.2), top, col_w[0], Inches(0.6),
                 mode, font_size=16, color=WHITE, bold=True)
    add_text_box(s, col_x[1] + Inches(0.2), top, col_w[1], Inches(0.6),
                 fmt, font_size=15, color=LIGHT_GREY)
    add_text_box(s, col_x[2] + Inches(0.2), top, col_w[2], Inches(0.6),
                 best, font_size=15, color=LIGHT_GREY)

add_notes(s,
    "Don't read the whole table — pick two or three to highlight.\n\n"
    "Standard: \"One person per round, five rounds. Great for a team meeting.\"\n\n"
    "Battle: \"Two people get the same prompt and both explain. The room votes. "
    "This is the offsite crowd-pleaser.\"\n\n"
    "Customer-Friendly: \"No acronyms allowed. Bonus point if your explanation "
    "would land with a customer exec. This one is sneaky — it's basically comms "
    "training disguised as a game.\"\n\n"
    "Mention Lightning and Team modes briefly.")

# ═══════════════════════════════════════════════════════════════════════════════
#  SLIDE 16 — What Makes a Good Answer
# ═══════════════════════════════════════════════════════════════════════════════
s = prs.slides.add_slide(prs.slide_layouts[6])
add_bullet_slide(s, "What Makes a Good Answer", [
    "Explains the process in plain language",
    "Maps steps or roles from one side to the other",
    "Surfaces risks, tradeoffs, or coordination points",
    "Lands on a memorable image people can repeat later",
],
    "\"A strong answer does at least two of these: explains the process in plain "
    "English, maps steps or roles from one side to the other, shows risks or "
    "tradeoffs, and lands on a memorable image.\"\n\n"
    "\"The best answers are the ones people repeat at lunch the next day.\"")

# ═══════════════════════════════════════════════════════════════════════════════
#  SLIDE 17 — SECTION 3 HEADER: Why It Works
# ═══════════════════════════════════════════════════════════════════════════════
s = prs.slides.add_slide(prs.slide_layouts[6])
set_bg(s, RGBColor(0x1A, 0x0A, 0x1A))
add_section_label(s, "SECTION 3")
add_text_box(s, Inches(0.5), Inches(2.2), Inches(12.3), Inches(2),
             "Why It Works", font_size=54, color=ACCENT, bold=True,
             alignment=PP_ALIGN.CENTER)
add_text_box(s, Inches(0.5), Inches(4.5), Inches(12.3), Inches(1),
             "Six research-backed reasons this is more than a party trick.",
             font_size=22, color=GREY, alignment=PP_ALIGN.CENTER)
add_notes(s,
    "\"Now — you might be thinking, this is a fun game, but why am I looking at a "
    "deck about it? Because this isn't just fun. There are six well-researched "
    "mechanisms at work here.\"")

# ═══════════════════════════════════════════════════════════════════════════════
#  SLIDES 18-23 — Six research reasons
# ═══════════════════════════════════════════════════════════════════════════════
research_slides = [
    {
        "title": "1. Analogical Reasoning",
        "body": "The game forces structure-mapping \u2014 identifying the relational "
                "structure of a concept and mapping it onto a new domain. This is how "
                "experts actually solve novel problems.",
        "cards": [
            ("Analogy was the single most common reasoning mechanism in real scientific "
             "breakthroughs \u2014 more than deduction or hypothesis testing.",
             "Dunbar, K. (1997). How Scientists Think. Creative Thought."),
            ("People who practice analogical reasoning develop stronger mental models "
             "and transfer knowledge more effectively across problem types.",
             "Gentner, Holyoak & Kokinov (2001). The Analogical Mind. MIT Press."),
        ],
        "notes":
            "\"The game forces something called structure-mapping — you have to "
            "identify the relational structure of a technical concept and map it onto "
            "a completely different domain. This isn't a party trick. Dedre Gentner's "
            "work showed this is how experts actually solve novel problems.\"\n\n"
            "\"Kevin Dunbar studied how scientists work in real labs and found that "
            "analogy was the single most common reasoning mechanism behind real "
            "breakthroughs.\"\n\n"
            "The point for CSAs: \"Your job is to take deep platform knowledge and "
            "apply it to novel customer situations. This game is practicing exactly that.\"",
    },
    {
        "title": "2. Plain-Language Communication",
        "body": "The game structurally forces you to explain technical concepts "
                "through non-technical metaphors \u2014 directly countering the "
                "curse of knowledge.",
        "cards": [
            ("People consistently overestimate how well they understand complex "
             "systems \u2014 until forced to explain them.",
             "Rozenblit & Keil (2002). Cognitive Science."),
            ("The most memorable, persuasive explanations use concrete analogies "
             "and unexpected comparisons.",
             "Heath & Heath (2007). Made to Stick. Random House."),
        ],
        "notes":
            "\"The game structurally forces you to explain a technical concept through "
            "a non-technical metaphor. That directly trains the skill CSAs need most "
            "in customer conversations.\"\n\n"
            "\"Every round of this game is a rehearsal for a customer whiteboard session.\"",
    },
    {
        "title": "3. Psychological Safety",
        "body": "Everyone takes the same risk: making a weird comparison in front "
                "of peers. The humor defuses status differences. The structure makes "
                "everyone equally vulnerable.",
        "cards": [
            ("Psychological safety \u2014 the belief you won't be punished for taking "
             "interpersonal risks \u2014 was the #1 predictor of high-performing teams.",
             "Google Project Aristotle (2015); Edmondson (1999, 2019)."),
            ("Short improv exercises increased willingness to contribute ideas and "
             "reduced fear of judgment \u2014 effects that persisted after.",
             "Dunlop et al. (2017)."),
        ],
        "notes":
            "\"Google's Project Aristotle — the biggest study they've ever done on "
            "team performance — found psychological safety was the number one predictor. "
            "Not talent. Not process. Safety.\"\n\n"
            "\"This game builds it because everyone takes the same risk. The humor "
            "levels the playing field.\"",
    },
    {
        "title": "4. Retrieval Practice",
        "body": "When you draw \u201ctuning cost optimization\u201d and have to explain "
                "it well enough to compare it to \u201corganizing a garage sale,\u201d "
                "you\u2019re doing forced retrieval of real technical knowledge.",
        "cards": [
            ("Retrieval practice produced 50% more long-term retention than concept "
             "mapping or elaborative study.",
             "Karpicke & Blunt (2011). Science, 331(6018), 772\u2013775."),
        ],
        "notes":
            "\"This is the sneaky one. When you draw 'tuning cost optimization' and "
            "have to explain it well enough to compare it to 'organizing a garage sale,' "
            "you're pulling real technical knowledge from memory and restructuring it.\"\n\n"
            "\"Karpicke and Blunt published in Science that retrieval practice produces "
            "fifty percent more long-term retention than concept mapping or elaborative study.\"\n\n"
            "\"Players don't feel like they're studying — but they absolutely are.\"",
    },
    {
        "title": "5. Humor & Social Bonding",
        "body": "Content-relevant humor increases attention, reduces anxiety, and "
                "improves retention. Shared laughter creates team culture.",
        "cards": [
            ("Shared laughter triggers endorphin release and increases feelings of "
             "group affiliation.",
             "Dunbar et al. (2012). Proceedings of the Royal Society B."),
            ("Humor relevant to content enhances learning without distracting from it.",
             "Banas, Dunbar, Rodriguez & Liu (2011). Communication Education."),
        ],
        "notes":
            "\"Content-relevant humor — not random jokes, but the kind of "
            "surprising-yet-apt comparisons this game produces — increases attention, "
            "reduces anxiety, and improves retention.\"\n\n"
            "\"Dunbar's lab showed that shared laughter triggers endorphin release and "
            "increases group affiliation. For distributed teams, this matters.\"",
    },
    {
        "title": "6. Cross-Domain Creative Thinking",
        "body": "Breakthrough ideas come from connecting knowledge across domains. "
                "The game is a direct exercise in remote association.",
        "cards": [
            ("Cognitive diversity \u2014 drawing on varied mental models \u2014 is a "
             "stronger predictor of team innovation than demographic diversity alone.",
             "Kaplan & Vakili (2015). Academy of Management Review."),
            ("The ability to connect distant concepts is a trainable skill, and "
             "structured exercises are effective training.",
             "Wan & Chiu (2002). Journal of Creative Behavior."),
        ],
        "notes":
            "\"Mednick proposed that creative ability is basically the capacity to make "
            "useful connections between remote concepts. This game is a direct exercise "
            "in remote association.\"\n\n"
            "\"And the good news from Wan and Chiu: this skill is trainable. The more "
            "you practice connecting distant concepts, the better you get.\"",
    },
]

for rs in research_slides:
    s = prs.slides.add_slide(prs.slide_layouts[6])
    set_bg(s, BG_DARK)
    add_text_box(s, Inches(0.8), Inches(0.4), Inches(11), Inches(0.8),
                 rs["title"], font_size=36, color=ACCENT, bold=True)
    add_text_box(s, Inches(0.8), Inches(1.4), Inches(11.5), Inches(1.2),
                 rs["body"], font_size=20, color=WHITE)
    card_top = Inches(3.0)
    for finding, cite in rs["cards"]:
        add_research_card(s, card_top, finding, cite)
        card_top += Inches(1.5)
    add_notes(s, rs["notes"])

# ═══════════════════════════════════════════════════════════════════════════════
#  SLIDE 24 — Compared To Alternatives
# ═══════════════════════════════════════════════════════════════════════════════
s = prs.slides.add_slide(prs.slide_layouts[6])
set_bg(s, BG_DARK)
add_text_box(s, Inches(0.8), Inches(0.4), Inches(11), Inches(0.8),
             "Compared To Alternatives", font_size=36, color=ACCENT, bold=True)

compare_headers = ["Dimension", "Trivia Night", "Icebreakers", "You Know"]
compare_rows = [
    ["Tests real knowledge",    "\u2713", "\u2717", "\u2713"],
    ["Builds communication",    "\u2717", "~",      "\u2713"],
    ["Creates shared humor",    "~",      "\u2717", "\u2713"],
    ["Rewards creativity",      "\u2717", "\u2717", "\u2713"],
    ["Works for new + tenured", "\u2717", "\u2713", "\u2713"],
    ["Scales to remote",        "~",      "~",      "\u2713"],
]

col_x_c = [Inches(1.0), Inches(5.0), Inches(7.5), Inches(10.0)]
col_w_c = [Inches(3.8), Inches(2.3), Inches(2.3), Inches(2.3)]

for j, h in enumerate(compare_headers):
    add_rounded_rect(s, col_x_c[j], Inches(1.5), col_w_c[j], Inches(0.6),
                     RGBColor(0x15, 0x25, 0x45), text=h, font_size=15,
                     font_color=ACCENT, bold=True, alignment=PP_ALIGN.CENTER)

for i, row in enumerate(compare_rows):
    top = Inches(2.3 + i * 0.7)
    for j, cell in enumerate(row):
        clr = ACCENT if (j == 3 and cell == "\u2713") else WHITE
        bld = (j == 3 and cell == "\u2713")
        add_text_box(s, col_x_c[j] + Inches(0.2), top, col_w_c[j] - Inches(0.4),
                     Inches(0.55), cell, font_size=16, color=clr, bold=bld,
                     alignment=PP_ALIGN.CENTER if j > 0 else PP_ALIGN.LEFT)

add_notes(s,
    "Walk through the table quickly. The visual tells the story.\n\n"
    "\"Trivia tests knowledge but doesn't build communication. Icebreakers build "
    "connection but ignore the technical depth. This game checks every box.\"\n\n"
    "Don't dwell — the table is self-explanatory.")

# ═══════════════════════════════════════════════════════════════════════════════
#  SLIDE 25 — SECTION 4 HEADER: Live Demo
# ═══════════════════════════════════════════════════════════════════════════════
s = prs.slides.add_slide(prs.slide_layouts[6])
set_bg(s, RGBColor(0x0A, 0x0A, 0x1A))
add_section_label(s, "SECTION 4")
add_text_box(s, Inches(0.5), Inches(2.2), Inches(12.3), Inches(2),
             "Live Demo", font_size=54, color=ACCENT, bold=True,
             alignment=PP_ALIGN.CENTER)
add_text_box(s, Inches(0.5), Inches(4.5), Inches(12.3), Inches(1),
             "Let\u2019s play a round.",
             font_size=22, color=GREY, alignment=PP_ALIGN.CENTER)
add_notes(s, "Energy shift. \"Enough slides. Let's play.\"")

# ═══════════════════════════════════════════════════════════════════════════════
#  SLIDE 26 — How This App Works
# ═══════════════════════════════════════════════════════════════════════════════
s = prs.slides.add_slide(prs.slide_layouts[6])
add_bullet_slide(s, "How This App Works", [
    "Azure OpenAI generates unique prompt pairs \u2014 no repeats, always fresh",
    "Azure AI Speech reads the prompt aloud in an excited announcer voice",
    "Rationale hint stays hidden \u2014 gives the speaker an angle if stuck",
    "Two buttons: Spin Pair and Say It",
],
    "Quick overview — don't oversell the tech.\n\n"
    "\"The app uses Azure OpenAI to generate unique prompt pairs every time — no "
    "repeats. Azure AI Speech reads the prompt aloud in an excited announcer voice, "
    "which sets the game-show energy. There's a hidden rationale hint that gives the "
    "speaker an angle if they get stuck.\"\n\n"
    "\"Two buttons: Spin Pair and Say It. That's it.\"")

# ═══════════════════════════════════════════════════════════════════════════════
#  SLIDE 27 — DEMO TIME
# ═══════════════════════════════════════════════════════════════════════════════
s = prs.slides.add_slide(prs.slide_layouts[6])
set_bg(s, BG_DARK)
add_text_box(s, Inches(0.5), Inches(2), Inches(12.3), Inches(2),
             "\U0001f3b0  DEMO TIME  \U0001f3b0",
             font_size=60, color=ACCENT2, bold=True, alignment=PP_ALIGN.CENTER)
add_text_box(s, Inches(0.5), Inches(4.5), Inches(12.3), Inches(1),
             "Switch to the app \u2192",
             font_size=26, color=WHITE, alignment=PP_ALIGN.CENTER)
add_text_box(s, Inches(0.5), Inches(5.3), Inches(12.3), Inches(0.6),
             "http://localhost:5173",
             font_size=18, color=GREY, alignment=PP_ALIGN.CENTER)
add_notes(s,
    "Switch to the live app (or wherever it's hosted).\n\n"
    "Make sure you've tested the app before the presentation. Have Azure credentials "
    "ready. The app should be running in the background already.")

# ═══════════════════════════════════════════════════════════════════════════════
#  SLIDE 28 — Let's Play a Round
# ═══════════════════════════════════════════════════════════════════════════════
s = prs.slides.add_slide(prs.slide_layouts[6])
set_bg(s, BG_DARK)
add_text_box(s, Inches(0.8), Inches(0.4), Inches(11), Inches(0.8),
             "Let\u2019s Play a Round", font_size=36, color=ACCENT, bold=True)

play_steps = [
    "1.  Spin a prompt pair",
    "2.  Hit \u201cSay It\u201d \u2014 hear the announcer",
    "3.  A volunteer explains the analogy",
    "4.  Everyone scores 1\u20135 \u00d7 3 categories",
    "5.  Repeat \u2014 can you beat the first player?",
]
for i, step in enumerate(play_steps):
    add_rounded_rect(s, Inches(3), Inches(1.6 + i * 1.0), Inches(7.3), Inches(0.7),
                     CARD_BG, text=step, font_size=20, font_color=WHITE,
                     border_color=RGBColor(0x30, 0x60, 0x80),
                     alignment=PP_ALIGN.LEFT)

add_notes(s,
    "Walk through each step live:\n"
    "1. Click Spin Pair — read the prompt out loud or hit Say It to let the "
    "announcer do it.\n"
    "2. Ask for a volunteer. Give them 30 seconds to think.\n"
    "3. They explain for 60–90 seconds.\n"
    "4. Ask everyone to score in the chat: three numbers (accuracy, creativity, delivery).\n"
    "5. If time allows, spin again and get a second volunteer. Head-to-head is more fun.\n\n"
    "Tips:\n"
    "- If the volunteer freezes, remind them they can peek at the rationale hint.\n"
    "- Encourage the room to react — laughing and groaning both count.\n"
    "- If you're remote, have people unmute to react. Silence kills the energy.")

# ═══════════════════════════════════════════════════════════════════════════════
#  SLIDE 29 — Scoring Reminder
# ═══════════════════════════════════════════════════════════════════════════════
s = prs.slides.add_slide(prs.slide_layouts[6])
set_bg(s, BG_DARK)
add_text_box(s, Inches(0.8), Inches(0.4), Inches(11), Inches(0.8),
             "Scoring Reminder", font_size=36, color=ACCENT, bold=True)

for i, (title, _) in enumerate(score_data):
    x = start_x + i * (card_w + gap)
    shape = add_rounded_rect(s, x, Inches(2.0), card_w, Inches(2.5),
                              CARD_BG, border_color=RGBColor(0x30, 0x60, 0x80))
    tf = shape.text_frame
    tf.word_wrap = True
    tf.paragraphs[0].text = title
    tf.paragraphs[0].font.size = Pt(24)
    tf.paragraphs[0].font.color.rgb = ACCENT2
    tf.paragraphs[0].font.bold = True
    tf.paragraphs[0].font.name = "Segoe UI"
    tf.paragraphs[0].alignment = PP_ALIGN.CENTER
    p = tf.add_paragraph()
    p.text = "/ 5"
    p.font.size = Pt(40); p.font.color.rgb = ACCENT; p.font.bold = True
    p.font.name = "Segoe UI"; p.alignment = PP_ALIGN.CENTER; p.space_before = Pt(24)

add_text_box(s, Inches(0.5), Inches(5.5), Inches(12.3), Inches(0.7),
             "Drop your scores in the chat!",
             font_size=26, color=ACCENT2, bold=True, alignment=PP_ALIGN.CENTER)
add_notes(s,
    "Keep this slide up while people are scoring.\n\n"
    "\"Drop three numbers in the chat — accuracy, creativity, delivery. "
    "Each is one to five.\"")

# ═══════════════════════════════════════════════════════════════════════════════
#  SLIDE 30 — Round Results
# ═══════════════════════════════════════════════════════════════════════════════
s = prs.slides.add_slide(prs.slide_layouts[6])
set_bg(s, BG_DARK)
add_text_box(s, Inches(0.8), Inches(0.4), Inches(11), Inches(0.8),
             "\U0001f3c6  Round Results", font_size=36, color=ACCENT, bold=True)
add_text_box(s, Inches(0.5), Inches(2.5), Inches(12.3), Inches(1),
             "Tally up the scores\u2026",
             font_size=26, color=WHITE, alignment=PP_ALIGN.CENTER)
add_rounded_rect(s, Inches(2.5), Inches(4), Inches(8.3), Inches(1.5),
                 CARD_BG, text="Who had the best analogy?",
                 font_size=28, font_color=ACCENT, bold=True, border_color=ACCENT)
add_notes(s,
    "Tally scores out loud. Make it a moment.\n\n"
    "\"And the winner of round one is\u2026\"\n\n"
    "If you did two rounds, compare. If you did battle mode, have the room vote "
    "with reactions.")

# ═══════════════════════════════════════════════════════════════════════════════
#  SLIDE 31 — When To Use This
# ═══════════════════════════════════════════════════════════════════════════════
s = prs.slides.add_slide(prs.slide_layouts[6])
add_bullet_slide(s, "When To Use This", [
    "Offsites \u2014 warm-up or energy reset between sessions",
    "Community calls \u2014 10-min round keeps the call alive",
    "New hire onboarding \u2014 learn vocabulary by hearing peers explain it",
    "Workshop warm-ups \u2014 primes creative, non-judgmental thinking",
    "Friday team meetings \u2014 end the week with laughter, not status",
],
    "\"This isn't a one-time offsite activity. Here's where it fits:\"\n\n"
    "Offsites: \"Warm-up between sessions, or energy reset after lunch.\"\n\n"
    "Community calls: \"A ten-minute round gives people a reason to stay on the call.\"\n\n"
    "Onboarding: \"New hires learn the technical vocabulary by hearing how peers "
    "explain it — way more effective than reading docs.\"\n\n"
    "Workshop warm-ups: \"Primes the room for creative, non-judgmental thinking.\"\n\n"
    "Friday meetings: \"End the week with laughter instead of status updates.\"")

# ═══════════════════════════════════════════════════════════════════════════════
#  SLIDE 32 — The Short Version
# ═══════════════════════════════════════════════════════════════════════════════
s = prs.slides.add_slide(prs.slide_layouts[6])
set_bg(s, BG_SECT1)
add_text_box(s, Inches(0.8), Inches(0.4), Inches(11), Inches(0.8),
             "The Short Version", font_size=36, color=ACCENT, bold=True,
             alignment=PP_ALIGN.CENTER)
add_rounded_rect(s, Inches(1), Inches(1.5), Inches(11.3), Inches(4.5),
                 CARD_BG2, border_color=ACCENT2)
add_text_box(s, Inches(1.5), Inches(1.8), Inches(10.3), Inches(4),
             "This game sits at the intersection of analogical reasoning, "
             "retrieval practice, plain-language communication, psychological "
             "safety, social bonding, and creative thinking.\n\n"
             "Each mechanism is individually well-researched.\n\n"
             "Combined in a 90-second game round, they make this one of the "
             "highest-value, lowest-effort team activities a CSA team can run.",
             font_size=22, color=ACCENT, alignment=PP_ALIGN.CENTER)
add_notes(s,
    "This is your closing slide. Deliver it with conviction.\n\n"
    "\"This game sits at the intersection of analogical reasoning, retrieval practice, "
    "plain-language communication, psychological safety, humor and bonding, and "
    "creative thinking. Each of those is individually well-researched. Combined in a "
    "ninety-second game round, they make this one of the highest-value, lowest-effort "
    "team activities a CSA team can run.\"")

# ═══════════════════════════════════════════════════════════════════════════════
#  SLIDE 33 — Closing Title
# ═══════════════════════════════════════════════════════════════════════════════
s = prs.slides.add_slide(prs.slide_layouts[6])
set_bg(s, BG_SECT1)
add_text_box(s, Inches(0.5), Inches(1.5), Inches(12.3), Inches(2),
             "You Know ____\nIs a Lot Like ____",
             font_size=48, color=ACCENT, bold=True, alignment=PP_ALIGN.CENTER)
add_text_box(s, Inches(0.5), Inches(4.0), Inches(12.3), Inches(0.8),
             "Let\u2019s bring this to your team.",
             font_size=26, color=ACCENT2, bold=False, alignment=PP_ALIGN.CENTER)
add_text_box(s, Inches(0.5), Inches(5.8), Inches(12.3), Inches(0.6),
             "Built with Azure OpenAI \u00b7 Azure AI Speech \u00b7 FastAPI \u00b7 React",
             font_size=14, color=GREY, alignment=PP_ALIGN.CENTER)
add_notes(s,
    "\"Let's bring this to your team. I'll leave you with the app and the game doc. "
    "All you need is a group chat, a volunteer, and ninety seconds.\"\n\n"
    "If someone asks about the tech stack: \"FastAPI backend, React frontend, Azure "
    "OpenAI for prompt generation, Azure AI Speech for the announcer voice. The whole "
    "thing runs on two terminal windows.\"")

# ── save ─────────────────────────────────────────────────────────────────────
prs.save("deck/you-know-game.pptx")
print("Saved deck/you-know-game.pptx")
