"""
Hagleitner Bohrtechnik GmbH
Bohrprotokoll PDF Generator

Eingabe: Dictionary mit Formulardaten (aus Google Sheets)
Ausgabe: PDF das dem Original-Papierformular entspricht
"""

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import Paragraph
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
import os

W, H = A4  # 595 x 842 pt

def pt(x_mm, y_mm):
    """Konvertiert mm-Koordinaten (von oben links) zu ReportLab-Koordinaten (von unten links)"""
    return x_mm * mm, H - y_mm * mm

def draw_bohrprotokoll(c: canvas.Canvas, data: dict):
    """Zeichnet ein vollständiges Bohrprotokoll auf den Canvas."""

    # ── Farben & Linien ──────────────────────────────────────────────────────
    BLACK = colors.black
    LIGHT_GRAY = colors.HexColor("#CCCCCC")

    def box(x_mm, y_mm, w_mm, h_mm, fill=None, stroke=True):
        x, y = pt(x_mm, y_mm + h_mm)
        if fill:
            c.setFillColor(fill)
            c.rect(x, y, w_mm * mm, h_mm * mm, fill=1, stroke=1 if stroke else 0)
            c.setFillColor(BLACK)
        else:
            c.rect(x, y, w_mm * mm, h_mm * mm, fill=0, stroke=1 if stroke else 0)

    def line(x1, y1, x2, y2):
        c.line(x1 * mm, H - y1 * mm, x2 * mm, H - y2 * mm)

    def text(txt, x_mm, y_mm, size=8, bold=False, align="left"):
        c.setFont("Helvetica-Bold" if bold else "Helvetica", size)
        x, y = pt(x_mm, y_mm)
        if align == "center":
            c.drawCentredString(x, y, str(txt))
        elif align == "right":
            c.drawRightString(x, y, str(txt))
        else:
            c.drawString(x, y, str(txt))

    def field_value(txt, x_mm, y_mm, size=9):
        """Handschrift-ähnliche Feldwerte"""
        c.setFont("Helvetica", size)
        x, y = pt(x_mm, y_mm)
        c.drawString(x, y, str(txt))

    # ════════════════════════════════════════════════════════════════════════
    # KOPFBEREICH
    # ════════════════════════════════════════════════════════════════════════
    margin_l = 10
    margin_r = 200
    page_w = 190  # nutzbare Breite in mm

    # Äußerer Rahmen
    box(margin_l, 8, page_w, 280)

    # Logo-Bereich (links oben)
    box(margin_l, 8, 55, 28)

    # Logo-Text (Hagleitner)
    c.setFont("Helvetica-Bold", 14)
    c.setFillColor(colors.HexColor("#1a5c2a"))  # Dunkelgrün
    c.drawString(11 * mm, H - 16 * mm, "HAG")
    c.setFont("Helvetica-Bold", 14)
    c.drawString(23 * mm, H - 16 * mm, "LEITNER")
    c.setFillColor(BLACK)

    c.setFont("Helvetica-Bold", 7)
    c.drawString(11 * mm, H - 20 * mm, "BOHRTECHNIK")
    c.setFont("Helvetica", 5.5)
    c.drawString(11 * mm, H - 23 * mm, "www.hagleitner-bohrungen.at")
    c.drawString(11 * mm, H - 26 * mm, "Erdwärmebohrung  •  Brunnenbau")
    c.drawString(11 * mm, H - 29 * mm, "Erdwärmeanlagen  •  Aufschlussbohrung")

    # Firmenadresse (Mitte oben)
    box(65, 8, 70, 28)
    c.setFont("Helvetica-Bold", 8)
    c.drawString(66 * mm, H - 13 * mm, "Hagleitner Bohrtechnik GmbH")
    c.setFont("Helvetica", 7)
    c.drawString(66 * mm, H - 17 * mm, "Aschauer Straße 102")
    c.drawString(66 * mm, H - 20 * mm, "6365 Kirchberg - Austria")
    c.drawString(66 * mm, H - 23 * mm, "T. +43 5357 - 35549 - 24")
    c.drawString(66 * mm, H - 26 * mm, "F. +43 5357 - 35748")
    c.drawString(66 * mm, H - 29 * mm, "info@hagleitner-bohrungen.at")

    # Bauvorhaben (rechts oben)
    box(135, 8, 65, 28)
    c.setFont("Helvetica-Bold", 8)
    c.drawString(136 * mm, H - 13 * mm, "Bauvorhaben:")
    c.setFont("Helvetica", 8)
    # Zweizeilige Adresse
    bv = data.get("bauvorhaben", "")
    c.drawString(136 * mm, H - 18 * mm, bv[:45])
    c.drawString(136 * mm, H - 22 * mm, bv[45:90] if len(bv) > 45 else "")
    c.setFont("Helvetica-Bold", 8)
    c.drawString(136 * mm, H - 26 * mm, "Auftraggeber:")
    c.setFont("Helvetica", 8)
    c.drawString(136 * mm, H - 30 * mm, data.get("auftraggeber", ""))

    # ── Zeile: Bohrung / Schurf / Schacht-Nr. ───────────────────────────────
    box(margin_l, 36, 120, 7)
    box(130, 36, 70, 7)
    text("Bohrung / Schurf / Schacht-Nr.:", 11, 41.5, size=8, bold=True)
    field_value(data.get("bohrung_nr", ""), 75, 41.5)
    text("Bericht Nr.:", 131, 41.5, size=8, bold=True)
    field_value(data.get("bericht_nr", ""), 155, 41.5, size=9)

    # ── Zeile: Gelände (GOK) ─────────────────────────────────────────────────
    box(margin_l, 43, 120, 7)
    box(130, 43, 70, 7)
    text("Gelände (GOK) ............m bezogen auf:", 11, 48.5, size=8)
    text("Datum:", 131, 48.5, size=8, bold=True)
    field_value(data.get("datum", ""), 148, 48.5, size=8)

    # ── Zeile: Bohrrichtung ──────────────────────────────────────────────────
    box(margin_l, 50, 190, 7)
    text("Bohrrichtung:", 11, 55.5, size=8)

    # Drei Optionen mit Umzirkelung der gewählten
    bohrrichtung = data.get("bohrrichtung", "").strip().lower()

    # Positionen der drei Begriffe (x_mm, Text, key)
    optionen = [
        (36,  "vertikal",   "vertikal"),
        (58,  "horizontal", "horizontal"),
        (84,  "schräg",     "schraeg"),
    ]

    for x_opt, label, key in optionen:
        c.setFont("Helvetica", 8)
        x_px, y_px = pt(x_opt, 55.5)
        c.drawString(x_px, y_px, label)

        # Trennstrich " / " nach den ersten zwei Optionen
        if key != "schraeg":
            slash_x = x_opt + c.stringWidth(label, "Helvetica", 8) / mm + 1.5
            text("/", slash_x, 55.5, size=8)

        # Kreis zeichnen wenn diese Option gewählt ist
        if bohrrichtung == key or bohrrichtung == label:
            text_w = c.stringWidth(label, "Helvetica", 8) / mm
            cx = (x_opt + text_w / 2) * mm
            cy = H - 53.5 * mm          # vertikal zentriert auf den Text
            rx = (text_w / 2 + 1.5) * mm
            ry = 3.2 * mm
            c.setLineWidth(0.8)
            c.ellipse(cx - rx, cy - ry, cx + rx, cy + ry, fill=0)
            c.setLineWidth(0.5)

    text("Winkel horizontal: ......................................", 100, 55.5, size=8)
    text("Winkel Nordrichtung im Uhr.: .................", 150, 55.5, size=8)

    # ── Block: Wasserspiegel / Verrohrung / Arbeitszeit ──────────────────────
    box(margin_l, 57, 60, 20)   # Wasserspiegel
    box(70, 57, 70, 20)         # Verrohrung
    box(140, 57, 60, 20)        # Arbeitszeit + Wetter

    text("Wasserspiegel ab GOK:", 11, 62, size=7.5, bold=True)
    text("um .......................... Uhr:", 11, 66, size=7)
    field_value(data.get("wasserspiegel_1", ""), 39, 66, size=8)
    text("um .......................... Uhr:", 11, 73, size=7)
    field_value(data.get("wasserspiegel_2", ""), 39, 73, size=8)

    text("Verrohrung ab GOK:", 71, 62, size=7.5, bold=True)
    text("Ø ......................... bis ........................", 71, 66.5, size=7)
    field_value(data.get("verrohrung_1_von", ""), 83, 66, size=8)
    field_value(data.get("verrohrung_1_bis", ""), 108, 66, size=8)
    text("Ø ......................... bis ........................", 71, 72, size=7)
    field_value(data.get("verrohrung_2_von", ""), 83, 72, size=8)
    field_value(data.get("verrohrung_2_bis", ""), 108, 72, size=8)

    text("Arbeitszeit: von .................. bis .................. Uhr", 141, 62, size=7)
    field_value(data.get("arbeitszeit_von", ""), 168, 62, size=8)
    field_value(data.get("arbeitszeit_bis", ""), 183, 62, size=8)
    text("Wetter und Temperatur:", 141, 71, size=7)
    field_value(data.get("wetter", ""), 141, 75, size=8)

    # ════════════════════════════════════════════════════════════════════════
    # SCHICHTEN-TABELLE
    # ════════════════════════════════════════════════════════════════════════
    table_top = 77
    col_x =    [10,  22,  33,  48,  68,  155, 170, 182]
    col_w =    [12,  11,  15,  20,  87,   15,  12,   18]
    #            1    2    3    4    5      6    7     8

    # Header-Hintergrund
    box(margin_l, table_top, page_w, 13, fill=colors.HexColor("#e8e8e8"))

    # Spalten-Trennlinien
    for i in range(len(col_x)):
        cx = col_x[i]
        line(cx, table_top, cx, table_top + 13)

    # Rechte Begrenzung
    line(200, table_top, 200, table_top + 13)

    # Horizontale Linie nach 1. Header-Zeile
    line(10, table_top + 5, 200, table_top + 5)
    # Linie nach 2. Header-Zeile
    line(10, table_top + 9, 200, table_top + 9)

    # Header-Texte Zeile 1
    text("Aufschluss-", 10.5, table_top + 4, size=6)
    text("ort", 10.5, table_top + 7.5, size=6)
    text("Krone", 22.5, table_top + 4, size=6)
    text("Tiefe ab GOK", 35, table_top + 4, size=6, align="center")
    text("in mm", 35, table_top + 7.5, size=6, align="center")

    # Spalte 5 Header (über mehrere Zeilen)
    c.setFont("Helvetica-Bold", 7)
    c.drawCentredString(111 * mm, H - (table_top + 4) * mm, "Beschreibung der Schichten")
    c.setFont("Helvetica", 5.5)
    c.drawCentredString(111 * mm, H - (table_top + 7) * mm, "(Bodenart / Gesteinsart, Einschlüsse,")
    c.drawCentredString(111 * mm, H - (table_top + 10) * mm, "besonderer Art, Farbe und Beschaffenheit,")
    c.drawCentredString(111 * mm, H - (table_top + 13) * mm, "Besonderheiten beim Bohren)")

    text("Wasser-", 155.5, table_top + 4, size=5.5)
    text("beob-", 155.5, table_top + 7.5, size=5.5)
    text("achtung", 155.5, table_top + 11, size=5.5)

    text("Proben", 176, table_top + 4, size=6, align="center")
    text("Art", 172, table_top + 9, size=6)
    text("Tiefe", 182.5, table_top + 7.5, size=5.5)
    text("ab GOK", 182.5, table_top + 11, size=5.5)

    # Nummerierung
    line(10, table_top + 13, 200, table_top + 13)
    for i, num in enumerate(["1", "2", "3", "4", "5", "6", "7", "8"]):
        cx = col_x[i]
        cw = col_w[i]
        text(num, cx + cw / 2, table_top + 17, size=7, align="center")
    line(10, table_top + 13 + 4, 200, table_top + 13 + 4)

    sub_header_y = table_top + 13
    text("von", col_x[2] + col_w[2] / 2, sub_header_y + 3.5, size=6, align="center")
    text("bis", col_x[3] + col_w[3] / 2, sub_header_y + 3.5, size=6, align="center")
    line(col_x[2], sub_header_y, col_x[2], sub_header_y + 4)
    line(col_x[3], sub_header_y, col_x[3], sub_header_y + 4)

    # Header Bohrwerkzeug
    text("Bohrwerk-", 10.5, table_top + 7.5, size=5.5)
    text("zeug", 10.5, table_top + 10.5, size=5.5)
    text("Spülung", 10.5, table_top + 13.5, size=5.5)
    text("Kronen Ø", 22.5, table_top + 7.5, size=5.5)
    text("(Bohr-Ø)", 22.5, table_top + 10.5, size=5.5)

    # ── Datenzeilen ──────────────────────────────────────────────────────────
    row_h = 8  # mm pro Zeile
    data_start_y = table_top + 21
    schichten = data.get("schichten", [])

    for i in range(14):  # 14 Zeilen
        row_y = data_start_y + i * row_h
        row_y_bottom = row_y + row_h

        # Trennlinie
        line(10, row_y_bottom, 200, row_y_bottom)

        # Vertikale Spaltenlinien
        for cx in col_x:
            line(cx, row_y, cx, row_y_bottom)
        line(200, row_y, 200, row_y_bottom)

        # Daten einfügen (wenn vorhanden)
        if i < len(schichten):
            s = schichten[i]
            field_value(s.get("von", ""),     col_x[2] + 1, row_y + 5.5, size=8)
            field_value(s.get("bis", ""),     col_x[3] + 1, row_y + 5.5, size=8)
            field_value(s.get("beschreibung", ""), col_x[4] + 2, row_y + 5.5, size=8)
            field_value(s.get("wasser", ""),  col_x[5] + 1, row_y + 5.5, size=7)
            field_value(s.get("probe_art", ""), col_x[6] + 1, row_y + 5.5, size=7)
            field_value(s.get("probe_tiefe", ""), col_x[7] + 1, row_y + 5.5, size=7)

    # ── Lageskizze ───────────────────────────────────────────────────────────
    sketch_y = data_start_y + 14 * row_h
    box(margin_l, sketch_y, page_w, 55)
    text("Lageskizze:", 11, sketch_y + 5, size=8, bold=True)
    field_value(data.get("lageskizze", ""), 35, sketch_y + 5, size=8)

    # ── Fußzeile ─────────────────────────────────────────────────────────────
    footer_y = sketch_y + 55
    box(margin_l, footer_y, page_w, 7)
    text("Bohrgerät:", 11, footer_y + 5, size=8, bold=True)
    field_value(data.get("bohrgeraet", ""), 35, footer_y + 5, size=8)
    text("Fortsetzungsbericht Nr.:", 120, footer_y + 5, size=8, bold=True)
    field_value(data.get("fortsetzung_nr", ""), 165, footer_y + 5, size=8)

    sig_y = footer_y + 7
    box(margin_l, sig_y, 95, 14)
    box(105, sig_y, 95, 14)
    text("Bohrgeräteführer (Name, Unterschrift):", 11, sig_y + 5, size=7.5, bold=True)
    field_value(data.get("bohrmeister", ""), 11, sig_y + 11, size=8)
    text("Für den Auftraggeber (Name, Unterschrift):", 106, sig_y + 5, size=7.5, bold=True)
    field_value(data.get("auftraggeber_unterschrift", ""), 106, sig_y + 11, size=8)


def generate_bohrprotokoll(data: dict, output_path: str):
    """Hauptfunktion: Erstellt das Bohrprotokoll-PDF."""
    c = canvas.Canvas(output_path, pagesize=A4)
    c.setTitle(f"Bohrprotokoll - {data.get('bericht_nr', '')}")
    draw_bohrprotokoll(c, data)
    c.save()
    print(f"✓ PDF erstellt: {output_path}")


# ════════════════════════════════════════════════════════════════════════════
# BEISPIEL-DATEN (entspricht dem Scan Naumanngasse)
# In der Praxis kommen diese Daten aus Google Sheets
# ════════════════════════════════════════════════════════════════════════════
beispiel_daten = {
    # Kopfzeile
    "bauvorhaben":          "Naumanngasse 38a, 5020 Salzburg",
    "auftraggeber":         "Frodinger",
    "bohrung_nr":           "",
    "bericht_nr":           "5431",
    "datum":                "30.03 - 8.04.2026",

    # Bohrrichtung: "vertikal", "horizontal" oder "schraeg"
    "bohrrichtung":         "vertikal",

    # Technische Parameter
    "wasserspiegel_1":      "10m",
    "wasserspiegel_2":      "",
    "verrohrung_1_von":     "Ø 152/100",
    "verrohrung_1_bis":     "16,00",
    "verrohrung_2_von":     "",
    "verrohrung_2_bis":     "",
    "arbeitszeit_von":      "",
    "arbeitszeit_bis":      "",
    "wetter":               "",

    # Schichtenfolge
    "schichten": [
        {"von": "0,00",  "bis": "0,30",   "beschreibung": "Humus",                      "wasser": "", "probe_art": "", "probe_tiefe": ""},
        {"von": "0,30",  "bis": "10,00",  "beschreibung": "mG, gG, gS",                 "wasser": "", "probe_art": "", "probe_tiefe": ""},
        {"von": "10,00", "bis": "60,00",  "beschreibung": "Seeton (Blau)",               "wasser": "", "probe_art": "", "probe_tiefe": ""},
        {"von": "60,00", "bis": "74,00",  "beschreibung": "Ton, schluffig (Beige)",      "wasser": "", "probe_art": "", "probe_tiefe": ""},
        {"von": "74,00", "bis": "180,00", "beschreibung": "Konglomerat",                 "wasser": "", "probe_art": "", "probe_tiefe": ""},
        {"von": "",      "bis": "",       "beschreibung": "2x 180m Ø40 Duplex",          "wasser": "", "probe_art": "", "probe_tiefe": ""},
        {"von": "",      "bis": "",       "beschreibung": "2x mit Zement Verpresst",     "wasser": "", "probe_art": "", "probe_tiefe": ""},
    ],

    # Fußzeile
    "lageskizze":                   "lt. Plan",
    "bohrgeraet":                   "Rotomax XL 1",
    "fortsetzung_nr":               "",
    "bohrmeister":                  "",
    "auftraggeber_unterschrift":    "",
}

if __name__ == "__main__":
    output = "/mnt/user-data/outputs/Bohrprotokoll_Naumanngasse.pdf"
    os.makedirs(os.path.dirname(output), exist_ok=True)
    generate_bohrprotokoll(beispiel_daten, output)
