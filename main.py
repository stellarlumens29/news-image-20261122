#!/usr/bin/env python3
"""The Sunday Ledger - one front page summing up Sunday 22 November 2026.

Draws a 1024x1024 newspaper front page with a pinned world map and 50
verified stories of the day, using only the Python standard library. The
image is fully deterministic: no clock, no randomness, no network, no
external files. Run: MAKEFUN_OUTPUT_DIR=out python3 main.py (or /output
in the sandbox).

Layout: masthead, a six-number "day in numbers" strip, a seven-region
bar, three illustrated lead cards, six small cards, a full-width pinned
world map, a 41-story index in three columns, and a date-check footer
that names the older stories deliberately left out.
"""

import os
import math
import struct
import zlib

W = 1024
H = 1024

PAPER = (249, 247, 242)
CARD = (255, 255, 255)
INK = (26, 26, 27)
RED = (215, 25, 33)
DARKRED = (170, 18, 24)
GREY = (96, 96, 100)
OCEAN = (216, 228, 236)
LAND = (148, 166, 184)
LANDLINE = (74, 88, 102)
GRAT = (196, 210, 220)
WHITE = (255, 255, 255)
LIGHT = (238, 234, 226)
GOLD = (184, 134, 11)

REGION_COLORS = [
    ("EUROPE", 10, (37, 99, 168)),
    ("ASIA", 10, (192, 57, 43)),
    ("MIDDLE EAST", 9, (183, 121, 31)),
    ("AFRICA", 2, (123, 75, 166)),
    ("AMERICAS", 12, (15, 118, 110)),
    ("OCEANIA", 5, (46, 125, 50)),
    ("GLOBAL", 2, (55, 71, 79)),
]

# ---------------------------------------------------------------- font ----
# A 5x7 pixel font, one row per string, "#" = on. Uppercase only; all text
# is uppercased before drawing, so only these glyphs are needed.
FONT = {
    "A": ("01110", "10001", "10001", "11111", "10001", "10001", "10001"),
    "B": ("11110", "10001", "10001", "11110", "10001", "10001", "11110"),
    "C": ("01110", "10001", "10000", "10000", "10000", "10001", "01110"),
    "D": ("11110", "10001", "10001", "10001", "10001", "10001", "11110"),
    "E": ("11111", "10000", "10000", "11110", "10000", "10000", "11111"),
    "F": ("11111", "10000", "10000", "11110", "10000", "10000", "10000"),
    "G": ("01110", "10001", "10000", "10111", "10001", "10001", "01111"),
    "H": ("10001", "10001", "10001", "11111", "10001", "10001", "10001"),
    "I": ("01110", "00100", "00100", "00100", "00100", "00100", "01110"),
    "J": ("00111", "00010", "00010", "00010", "00010", "10010", "01100"),
    "K": ("10001", "10010", "10100", "11000", "10100", "10010", "10001"),
    "L": ("10000", "10000", "10000", "10000", "10000", "10000", "11111"),
    "M": ("10001", "11011", "10101", "10101", "10001", "10001", "10001"),
    "N": ("10001", "11001", "10101", "10011", "10001", "10001", "10001"),
    "O": ("01110", "10001", "10001", "10001", "10001", "10001", "01110"),
    "P": ("11110", "10001", "10001", "11110", "10000", "10000", "10000"),
    "Q": ("01110", "10001", "10001", "10001", "10101", "10010", "01101"),
    "R": ("11110", "10001", "10001", "11110", "10100", "10010", "10001"),
    "S": ("01111", "10000", "10000", "01110", "00001", "00001", "11110"),
    "T": ("11111", "00100", "00100", "00100", "00100", "00100", "00100"),
    "U": ("10001", "10001", "10001", "10001", "10001", "10001", "01110"),
    "V": ("10001", "10001", "10001", "10001", "10001", "01010", "00100"),
    "W": ("10001", "10001", "10001", "10101", "10101", "11011", "10001"),
    "X": ("10001", "10001", "01010", "00100", "01010", "10001", "10001"),
    "Y": ("10001", "10001", "01010", "00100", "00100", "00100", "00100"),
    "Z": ("11111", "00001", "00010", "00100", "01000", "10000", "11111"),
    "0": ("01110", "10001", "10011", "10101", "11001", "10001", "01110"),
    "1": ("00100", "01100", "00100", "00100", "00100", "00100", "01110"),
    "2": ("01110", "10001", "00001", "00010", "00100", "01000", "11111"),
    "3": ("11111", "00010", "00100", "00010", "00001", "10001", "01110"),
    "4": ("00010", "00110", "01010", "10010", "11111", "00010", "00010"),
    "5": ("11111", "10000", "11110", "00001", "00001", "10001", "01110"),
    "6": ("00110", "01000", "10000", "11110", "10001", "10001", "01110"),
    "7": ("11111", "00001", "00010", "00100", "01000", "01000", "01000"),
    "8": ("01110", "10001", "10001", "01110", "10001", "10001", "01110"),
    "9": ("01110", "10001", "10001", "01111", "00001", "00010", "01100"),
    " ": ("00000", "00000", "00000", "00000", "00000", "00000", "00000"),
    ".": ("00000", "00000", "00000", "00000", "00000", "01100", "01100"),
    ",": ("00000", "00000", "00000", "00000", "01100", "00100", "01000"),
    ":": ("00000", "01100", "01100", "00000", "01100", "01100", "00000"),
    ";": ("00000", "01100", "01100", "00000", "01100", "00100", "01000"),
    "-": ("00000", "00000", "00000", "11111", "00000", "00000", "00000"),
    "+": ("00000", "00100", "00100", "11111", "00100", "00100", "00000"),
    "%": ("11001", "11010", "00010", "00100", "01000", "01011", "10011"),
    "$": ("00100", "01111", "10100", "01110", "00101", "11110", "00100"),
    "/": ("00001", "00010", "00010", "00100", "01000", "01000", "10000"),
    "(": ("00010", "00100", "01000", "01000", "01000", "00100", "00010"),
    ")": ("01000", "00100", "00010", "00010", "00010", "00100", "01000"),
    "'": ("00100", "00100", "01000", "00000", "00000", "00000", "00000"),
    "&": ("01100", "10010", "10100", "01000", "10101", "10010", "01101"),
    "!": ("00100", "00100", "00100", "00100", "00100", "00000", "00100"),
    "?": ("01110", "10001", "00001", "00010", "00100", "00000", "00100"),
    "=": ("00000", "00000", "11111", "00000", "11111", "00000", "00000"),
    "#": ("01010", "01010", "11111", "01010", "11111", "01010", "01010"),
    "*": ("00000", "10101", "01110", "11111", "01110", "10101", "00000"),
}


def text_width(text, scale):
    return len(text) * 6 * scale - scale


def truncate(text, max_width, scale):
    if text_width(text, scale) <= max_width:
        return text
    while text and text_width(text + "...", scale) > max_width:
        text = text[:-1]
    return text + "..."


def wrap(text, max_chars):
    """Greedy word wrap; returns a list of lines, each <= max_chars."""
    words = text.split(" ")
    lines = []
    cur = ""
    for w in words:
        if not cur:
            cur = w
        elif len(cur) + 1 + len(w) <= max_chars:
            cur += " " + w
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines

# -------------------------------------------------------------- stories ----
# (number, headline, outlet, longitude, latitude, region)
# Headlines are one line each in the index; the 9 card stories also carry
# a chip, a dateline and a summary in CARDS below. Every story was verified
# against live reporting of Sunday 22 November 2026 (Reuters, AP, AFP,
# IANS, Xinhua, Al Jazeera, China Daily, CoinMarketCap, TBS, Yonhap, ANI,
# Daily Jagran, BBC/Reuters wires via EuropeSays, NAMPA, AutoHebdo).
STORIES = [
    (1, "COP31 NEARS DEAL AS SUNDAY VOTE LOOMS", "REUTERS", 30.7, 36.9, "GLOBAL"),
    (2, "IRAN HITS US BASES IN BAHRAIN", "IANS", 50.6, 26.2, "MIDDLE EAST"),
    (3, "INDIA DECLARE ON RECORD 720-9", "AFP", 174.8, -41.3, "OCEANIA"),
    (4, "ZELENSKY: BRIDGE STRIKES FAIR", "TBS", 30.5, 50.4, "EUROPE"),
    (5, "ZELENSKY: NATO BEST GUARANTEE", "EUROPE SAYS", 30.5, 50.4, "EUROPE"),
    (6, "HONG KONG VOTES FOR 723 SEATS", "CHINA DAILY", 114.2, 22.3, "ASIA"),
    (7, "PALMOWSKI WINS VEGAS FINALE", "AUTOHEBDO", -115.1, 36.2, "AMERICAS"),
    (8, "FRANCE SET FOR SA FINAL", "AFP", 2.36, 48.93, "EUROPE"),
    (9, "BITCOIN NEAR $60,200, UP 1.9%", "COINMARKETCAP", -74.0, 40.7, "GLOBAL"),
    (10, "HOUTHIS EDGE CLOSER TO ADEN", "AL JAZEERA", 45.0, 12.8, "MIDDLE EAST"),
    (11, "SAUDI SACKS COALITION COMMANDER", "AL JAZEERA", 46.7, 24.7, "MIDDLE EAST"),
    (12, "YEMEN CALLS HOUTHIS TERRORISTS", "AL JAZEERA", 44.2, 15.4, "MIDDLE EAST"),
    (13, "IRAQ MOVES ON KATAIB HEZBOLLAH", "AL JAZEERA", 44.4, 33.3, "MIDDLE EAST"),
    (14, "US HITS CARGO SHIP OFF OMAN", "AL JAZEERA", 59.5, 22.5, "MIDDLE EAST"),
    (15, "TRUMP WANTS PERMANENT IRAN DEAL", "AL JAZEERA", -77.0, 38.9, "AMERICAS"),
    (16, "TRUMP FAVOURS IRAN OIL SQUEEZE", "BREITBART", -77.0, 38.9, "AMERICAS"),
    (17, "GAZA AID PLEA FROM FOUR NATIONS", "PARIS EYE", 34.5, 31.5, "MIDDLE EAST"),
    (18, "ISRAELI STRIKE KILLS 3 IN GAZA", "HUB247", 34.5, 31.5, "MIDDLE EAST"),
    (19, "EISENKOT TAPPED TO FORM GOVT", "PARIS EYE", 35.2, 31.8, "MIDDLE EAST"),
    (20, "US DETAILS $12BN VENEZUELA OIL", "PARIS EYE", -66.9, 10.5, "AMERICAS"),
    (21, "TINUBU ARRIVES IN BRAZIL", "ACCESS24", -47.9, -15.8, "AMERICAS"),
    (22, "BRAVA TAKES PESCADA CLUSTER", "VOLTSDAILY", -37.0, -5.0, "AMERICAS"),
    (23, "BRAZIL CRUDE TO EU DOUBLES", "VOLTSDAILY", -43.2, -22.9, "AMERICAS"),
    (24, "MEXICO SOLAR TO TRIPLE BY 2035", "VOLTSDAILY", -99.1, 19.4, "AMERICAS"),
    (25, "COLUMBUS STUN MESSI'S MIAMI 3-0", "AP", -82.9, 40.0, "AMERICAS"),
    (26, "KC CURRENT WIN FIRST NWSL TITLE", "AP", -94.6, 39.1, "AMERICAS"),
    (27, "NY UNVEILS 5 GW NUCLEAR PLAN", "VOLTSDAILY", -73.8, 42.7, "AMERICAS"),
    (28, "CANADA JOINS NATO INNOVATION FUND", "XINHUA", -75.7, 45.4, "AMERICAS"),
    (29, "NATO VOWS TO DEFEND POLAND", "HUB247", 21.0, 52.2, "EUROPE"),
    (30, "TORIES ATTACK BURNHAM EU DEAL", "HILLINGDON TIMES", -0.1, 51.5, "EUROPE"),
    (31, "EU EYES 3% BIG-TECH LEVY", "INSIGHT INTL", 4.4, 50.8, "EUROPE"),
    (32, "FIA BACKS V8 RETURN FOR 2030", "POLLAR", 2.35, 48.86, "EUROPE"),
    (33, "FLUCK OF SPITTING IMAGE DIES, 85", "LBC", -0.1, 51.5, "EUROPE"),
    (34, "FRANCE IN 4TH WEEKEND OF PROTESTS", "PARIS EYE", 4.8, 45.8, "EUROPE"),
    (35, "GEORGIA MOURNS BUILDING DEAD", "MEDIANEWS", 44.8, 41.7, "EUROPE"),
    (36, "MELBOURNE STABBINGS SPARK PLEDGE", "EUROPE SAYS", 145.0, -37.8, "OCEANIA"),
    (37, "SYDNEY HEATWAVE PEAKS AT 31C", "BOM", 151.2, -33.9, "OCEANIA"),
    (38, "AUKUS ROW: AUSTRALIA HITS BACK", "REUTERS", 149.1, -35.3, "OCEANIA"),
    (39, "MODI OPENS NITISH SETU BRIDGE", "DAILY JAGRAN", 85.1, 25.6, "ASIA"),
    (40, "AKVAN GROUNDS 14 RANCHI FLIGHTS", "DAILY JAGRAN", 85.3, 23.3, "ASIA"),
    (41, "JAPAN TO TRAIN LIVE-FIRE IN INDIA", "DAILY JAGRAN", 77.2, 28.6, "ASIA"),
    (42, "CUMMINS KEEPS TEST CAPTAINCY", "DAILY JAGRAN", 151.2, -33.9, "OCEANIA"),
    (43, "BHANGU, INDIA HOCKEY COACH, DIES", "DAILY JAGRAN", 75.6, 31.3, "ASIA"),
    (44, "ADVANI WINS SNOOKER OPENER", "DAILY JAGRAN", 77.6, 13.0, "ASIA"),
    (45, "INDIA WOMEN BEAT KOREA 2-1", "ANI", 77.4, 23.3, "ASIA"),
    (46, "KOREA MINISTER QUITS OVER AI CHEATS", "EIN", 127.0, 37.5, "ASIA"),
    (47, "KOREA EXPORTS TOP $1 TRILLION", "YONHAP", 127.0, 37.5, "ASIA"),
    (48, "KOREAN NAVY CHIEF VISITS JAPAN", "WISEVOTER", 139.7, 35.7, "ASIA"),
    (49, "NIGERIA SIGNS DIGITAL PACT", "LEGALBRIEF", 3.4, 6.5, "AFRICA"),
    (50, "TINUBU NAMES CLIMATE COUNCIL CHIEF", "ACCESS24", 7.5, 9.1, "AFRICA"),
]

# Card stories 1-9: (chip, dateline, summary). The chip is the red label,
# the dateline sits above the headline, the summary is wrapped to fit.
CARDS = {
    1: ("COP31: NEAR DEAL", "1 ANTALYA, TURKIYE - CLIMATE",
        "NEW PACKAGE AFTER TWO DAYS OVERTIME. FOSSIL FUELS STILL UNNAMED. "
        "OBJECTIONS DUE 0300 GMT, VOTE AT 0600 GMT SUNDAY."),
    2: ("BAHRAIN: US BASES HIT", "2 MANAMA - WAR",
        "IRGC CLAIMS MISSILE AND DRONE STRIKES ON TWO US PATRIOT RADARS. "
        "BAHRAIN SAYS A CIVILIAN PLANT BURNED, NO ONE HURT."),
    3: ("WELLINGTON: 720-9", "3 WELLINGTON - CRICKET",
        "PANT 128 AND RAHUL 136 POWER INDIA TO A RECORD TOTAL IN NEW "
        "ZEALAND. LEAD 352 AT THE DECLARATION."),
    4: ("KYIV: BRIDGE", "4 KYIV - WAR",
        "STRIKES ON THE CRIMEA BRIDGE ARE A FAIR RESPONSE, HE SAYS."),
    5: ("KYIV: NATO", "5 KYIV - SECURITY",
        "NATO MEMBERSHIP IS THE CLEAREST GUARANTEE, HE SAYS."),
    6: ("HONG KONG: VOTE", "6 HONG KONG - ELECTION",
        "856 CANDIDATES CHASE 723 SEATS. TURNOUT 69.6% BY 11 AM."),
    7: ("VEGAS: PALMOWSKI", "7 LAS VEGAS - MOTORSPORT",
        "PALMOWSKI WINS THE F1 ACADEMY FINALE FROM POLE."),
    8: ("PARIS: RUGBY FINAL", "8 SAINT-DENIS - RUGBY",
        "FRANCE BEAT ARGENTINA 45-17 TO REACH THE FINAL."),
    9: ("MARKETS: BITCOIN", "9 NEW YORK - MARKETS",
        "BITCOIN NEAR $60,200, UP ABOUT 1.9% ON THE DAY."),
}

# The day in numbers: (big figure, caption line 1, caption line 2).
NUMBERS = [
    ("14", "DAY OF COP31", "NO DEAL YET"),
    ("2", "BAHRAIN BASES", "IRAN STRIKES"),
    ("720", "INDIA RECORD", "DECLARE 720-9"),
    ("$60,200", "BITCOIN", "UP 1.9%"),
    ("69.6%", "HK TURNOUT", "AT 11 AM"),
    ("$1TN", "KOREA EXPORTS", "FIRST TIME"),
]

# Simplified continent outlines as (lon, lat) rings, equirectangular.
CONTINENTS = [
    # North America
    [(-168, 66), (-140, 70), (-120, 72), (-95, 80), (-75, 73), (-55, 60),
     (-65, 45), (-75, 38), (-80, 32), (-85, 30), (-87, 26), (-90, 21),
     (-94, 18), (-97, 16), (-102, 18), (-106, 22), (-110, 25), (-114, 29),
     (-118, 33), (-122, 38), (-125, 42), (-125, 49), (-140, 60),
     (-155, 58), (-168, 66)],
    # Greenland
    [(-55, 60), (-45, 60), (-32, 68), (-22, 70), (-30, 76), (-55, 76),
     (-60, 70), (-55, 60)],
    # South America
    [(-80, 10), (-75, 5), (-60, 0), (-50, 0), (-35, -8), (-40, -20),
     (-48, -28), (-58, -35), (-65, -41), (-70, -50), (-70, -55),
     (-73, -40), (-75, -20), (-80, -5), (-80, 10)],
    # Africa
    [(-17, 15), (-10, 30), (0, 36), (10, 37), (20, 32), (32, 31),
     (35, 28), (40, 15), (43, 11), (48, 10), (51, 12), (44, 0),
     (40, -10), (35, -20), (32, -29), (25, -34), (18, -35), (15, -25),
     (12, -15), (9, 4), (-8, 5), (-17, 15)],
    # Eurasia
    [(-10, 36), (-9, 43), (-2, 48), (0, 50), (5, 53), (8, 57), (18, 56),
     (21, 55), (28, 59), (30, 60), (25, 65), (30, 70), (40, 68),
     (55, 69), (70, 72), (90, 75), (110, 76), (130, 72), (150, 70),
     (170, 66), (178, 65), (170, 60), (160, 60), (158, 52), (142, 50),
     (140, 40), (135, 35), (130, 33), (127, 35), (122, 38), (120, 32),
     (110, 20), (108, 10), (105, 8), (100, 8), (97, 15), (92, 21),
     (88, 22), (80, 15), (77, 8), (75, 15), (72, 20), (66, 25),
     (60, 25), (57, 26), (52, 26), (48, 29), (48, 30), (44, 29),
     (40, 31), (36, 36), (30, 36), (26, 38), (22, 37), (18, 40),
     (12, 44), (8, 44), (3, 43), (-2, 37), (-9, 37), (-10, 36)],
    # United Kingdom
    [(-5, 50), (-3, 53), (-5, 56), (-2, 58), (0, 53), (1, 51), (-5, 50)],
    # Japan
    [(130, 31), (132, 33), (135, 34), (138, 35), (140, 38), (141, 41),
     (143, 43), (145, 44), (141, 45), (140, 40), (137, 37), (133, 35),
     (130, 31)],
    # Australia
    [(114, -22), (113, -26), (115, -33), (118, -35), (124, -33),
     (129, -32), (132, -32), (136, -35), (140, -38), (145, -38),
     (150, -37), (153, -32), (153, -27), (150, -22), (146, -19),
     (142, -15), (142, -11), (137, -12), (135, -15), (132, -12),
     (130, -13), (126, -14), (122, -17), (118, -20), (114, -22)],
    # New Zealand
    [(167, -45), (170, -42), (174, -38), (176, -38), (178, -37),
     (175, -40), (172, -43), (168, -46), (167, -45)],
    # Indonesia
    [(95, 5), (98, 3), (100, 0), (104, -3), (107, -6), (110, -7),
     (114, -8), (118, -9), (120, -10), (119, -8), (115, -5), (110, -5),
     (105, 0), (100, 2), (95, 5)],
    # Madagascar
    [(44, -16), (47, -15), (50, -16), (49, -20), (47, -24), (44, -25),
     (43, -21), (44, -16)],
    # Iceland
    [(-22, 64), (-15, 64), (-14, 66), (-20, 66), (-22, 64)],
]

# Display nudges (pixels) so pins in tight clusters do not cover each
# other. Map is 976x190, so clusters are tighter than on a tall map.
# Every pair of pin centres is >= 15 px apart (verified by check_pins.py).
PIN_DXDY = {
    # Europe / Middle East zone
    30: (-18, -15), 31: (-2, -21), 8: (-20, 5), 32: (16, -9),
    33: (2, 23), 34: (23, 7), 29: (-3, -12), 4: (-17, 0), 5: (11, -18),
    1: (-3, 8), 35: (13, -15), 13: (-8, 18), 17: (-22, 18),
    18: (4, 30), 19: (14, -11), 2: (13, -15), 11: (4, 14),
    10: (-2, 21), 12: (16, -11), 14: (5, 13),
    # India zone
    41: (-15, -13), 43: (13, -18), 39: (13, -14), 45: (14, 6),
    40: (15, 10), 44: (-14, 11),
    # Oceania zone
    36: (-15, -13), 38: (-4, -16), 37: (-16, 13), 42: (12, 9), 3: (-2, 13),
    # North America zone
    26: (-15, -14), 25: (-15, 15), 15: (-13, -14), 28: (5, -17),
    16: (17, 10), 9: (-15, 12), 27: (18, -6), 20: (13, 8),
    # East Asia zone
    6: (-14, 13), 46: (-14, -13), 47: (16, 15), 48: (3, -13),
    # Africa zone
    49: (-15, 12), 50: (8, -13),
    # South America zone
    21: (-10, -10), 23: (10, 10),
}

MAP_X, MAP_Y, MAP_W, MAP_H = 24, 576, 976, 190


def lonlat_to_xy(lon, lat):
    x = MAP_X + (lon + 180.0) / 360.0 * MAP_W
    y = MAP_Y + (90.0 - lat) / 180.0 * MAP_H
    return int(round(x)), int(round(y))


# --------------------------------------------------------------- canvas ----
class Canvas:
    def __init__(self, w, h, bg):
        self.w = w
        self.h = h
        self.px = bytearray(bg * (w * h))

    def set(self, x, y, color):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.px[i], self.px[i + 1], self.px[i + 2] = color

    def rect(self, x, y, w, h, color):
        x0 = max(0, x)
        y0 = max(0, y)
        x1 = min(self.w, x + w)
        y1 = min(self.h, y + h)
        for yy in range(y0, y1):
            base = (yy * self.w + x0) * 3
            for xx in range(x0, x1):
                i = base + (xx - x0) * 3
                self.px[i], self.px[i + 1], self.px[i + 2] = color

    def hline(self, x, y, w, color):
        self.rect(x, y, w, 1, color)

    def vline(self, x, y, h, color):
        self.rect(x, y, 1, h, color)

    def circle(self, cx, cy, r, color):
        for yy in range(cy - r, cy + r + 1):
            dy = yy - cy
            dx = int((r * r - dy * dy) ** 0.5)
            for xx in range(cx - dx, cx + dx + 1):
                self.set(xx, yy, color)

    def ring(self, cx, cy, r, color):
        for yy in range(cy - r, cy + r + 1):
            dy = yy - cy
            outer = int((r * r - dy * dy) ** 0.5)
            inner = int(((r - 2) * (r - 2) - dy * dy) ** 0.5) if abs(dy) < r - 2 else -1
            for xx in range(cx - outer, cx + outer + 1):
                if abs(xx - cx) > inner:
                    self.set(xx, yy, color)

    def polygon(self, pts, fill, line):
        # Scanline fill, even-odd rule, then draw the outline.
        xs = [p[0] for p in pts]
        ys = [p[1] for p in pts]
        for y in range(max(0, min(ys)), min(self.h, max(ys) + 1)):
            nodes = []
            n = len(pts)
            for i in range(n):
                x1, y1 = pts[i]
                x2, y2 = pts[(i + 1) % n]
                if (y1 <= y < y2) or (y2 <= y < y1):
                    xi = x1 + (y - y1) * (x2 - x1) / (y2 - y1)
                    nodes.append(xi)
            nodes.sort()
            for k in range(0, len(nodes) - 1, 2):
                for x in range(int(nodes[k]), int(nodes[k + 1]) + 1):
                    self.set(x, y, fill)
        n = len(pts)
        for i in range(n):
            self._seg(pts[i], pts[(i + 1) % n], line)

    def _seg(self, a, b, color):
        x1, y1 = a
        x2, y2 = b
        steps = max(abs(x2 - x1), abs(y2 - y1), 1)
        for s in range(steps + 1):
            x = int(round(x1 + (x2 - x1) * s / steps))
            y = int(round(y1 + (y2 - y1) * s / steps))
            self.set(x, y, color)
            self.set(x + 1, y, color)

    def star(self, cx, cy, r, color):
        # Four-point sparkle: two crossed diamonds.
        for d in range(-r, r + 1):
            self.set(cx + d, cy, color)
            self.set(cx, cy + d, color)
            self.set(cx + d // 2, cy + d // 2, color)
            self.set(cx + d // 2, cy - d // 2, color)

    def text(self, x, y, s, color, scale=1):
        s = s.upper()
        cx = x
        for ch in s:
            glyph = FONT.get(ch, FONT[" "])
            for row in range(7):
                bits = glyph[row]
                for col in range(5):
                    if bits[col] == "1":
                        self.rect(cx + col * scale, y + row * scale,
                                  scale, scale, color)
            cx += 6 * scale
        return cx - x - scale

    def text_center(self, y, s, color, scale=1):
        w = text_width(s.upper(), scale)
        self.text((self.w - w) // 2, y, s, color, scale)


def chunk(kind, data):
    c = struct.pack(">I", len(data)) + kind + data
    c += struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)
    return c


def write_png(canvas, path):
    raw = bytearray()
    for y in range(canvas.h):
        raw.append(0)
        start = y * canvas.w * 3
        raw += canvas.px[start:start + canvas.w * 3]
    ihdr = struct.pack(">IIBBBBB", canvas.w, canvas.h, 8, 2, 0, 0, 0)
    png = b"\x89PNG\r\n\x1a\n"
    png += chunk(b"IHDR", ihdr)
    png += chunk(b"IDAT", zlib.compress(bytes(raw), 9))
    png += chunk(b"IEND", b"")
    with open(path, "wb") as f:
        f.write(png)
    return len(png)


# ---------------------------------------------------------------- draw -----
def draw_icon(c, kind, x, y, w, h):
    """Small geometric illustration inside a lead card's icon area."""
    if kind == 1:
        # Globe + thermometer: climate summit running hot.
        cx, cy, r = x + 52, y + h // 2, 26
        c.ring(cx, cy, r, INK)
        c.vline(cx, cy - r, 2 * r, INK)
        c.hline(cx - r, cy, 2 * r, INK)
        c.circle(cx, cy, r - 10, (90, 160, 200))
        tx = x + w - 46
        c.rect(tx, y + 8, 10, h - 26, INK)
        c.rect(tx + 2, y + 10, 6, h - 30, WHITE)
        c.rect(tx + 2, y + h - 34, 6, 22, RED)
        c.circle(tx + 5, y + h - 12, 9, RED)
        c.ring(tx + 5, y + h - 12, 9, DARKRED)
    elif kind == 2:
        # Night skyline + three missile arcs with bursts.
        c.rect(x, y, w, h, (24, 32, 54))
        for bx, bh in ((x + 18, 34), (x + 62, 52), (x + 112, 28), (x + 158, 44),
                       (x + 208, 36), (x + 252, 50)):
            c.rect(bx, y + h - bh, 34, bh, (52, 66, 96))
        for sx, sy in ((x + 60, y + 18), (x + 150, y + 10), (x + 240, y + 22)):
            c.star(sx, sy, 7, GOLD)
            c._seg((sx - 26, sy + 12), (sx - 6, sy + 2), GOLD)
    else:
        # Cricket: green pitch, three stumps, a bat and a red ball.
        c.rect(x, y, w, h, (34, 120, 60))
        c.rect(x, y + h - 18, w, 18, (120, 90, 60))
        c.rect(x + w // 2 - 40, y + 8, 80, h - 26, (210, 190, 150))
        for sx in (x + w // 2 - 14, x + w // 2, x + w // 2 + 14):
            c.rect(sx - 2, y + h - 44, 4, 26, GOLD)
        c.rect(x + w // 2 - 16, y + h - 48, 32, 4, GOLD)
        c._seg((x + 30, y + 14), (x + 66, y + h - 52), (210, 170, 110))
        c._seg((x + 34, y + 14), (x + 70, y + h - 52), (210, 170, 110))
        c._seg((x + 38, y + 14), (x + 74, y + h - 52), (210, 170, 110))
        c._seg((x + 66, y + h - 52), (x + 84, y + h - 30), (210, 170, 110))
        c._seg((x + 70, y + h - 52), (x + 88, y + h - 30), (210, 170, 110))
        c.circle(x + w - 40, y + 22, 7, RED)
        c.ring(x + w - 40, y + 22, 7, DARKRED)


def draw_lead_card(c, num, x, y, w, h):
    story = STORIES[num - 1]
    chip, dateline, summary = CARDS[num]
    c.rect(x, y, w, h, CARD)
    c.rect(x, y, w, h, INK)  # border via outline trick below
    c.rect(x + 1, y + 1, w - 2, h - 2, CARD)
    c.rect(x, y, w, 3, INK)
    # Red chip.
    c.rect(x + 10, y + 10, text_width(chip, 1) + 12, 16, RED)
    c.text(x + 16, y + 14, chip, WHITE, 1)
    # Icon area.
    draw_icon(c, num, x + 10, y + 32, w - 20, 58)
    # Dateline, headline, summary, outlet.
    c.text(x + 10, y + 98, dateline, RED, 1)
    yy = y + 110
    for line in wrap(story[1], 24):
        c.text(x + 10, yy, line, INK, 2)
        yy += 16
    yy += 4
    for line in wrap(summary, 48):
        c.text(x + 10, yy, line, INK, 1)
        yy += 9
    c.text(x + 10, y + h - 16, "SOURCE: " + story[2], GREY, 1)


def draw_small_card(c, num, x, y, w, h):
    story = STORIES[num - 1]
    chip, dateline, summary = CARDS[num]
    c.rect(x, y, w, h, CARD)
    c.rect(x, y, w, 3, RED)
    c.rect(x, y, 1, h, INK)
    c.rect(x + w - 1, y, 1, h, INK)
    c.rect(x, y + h - 1, w, 1, INK)
    c.text(x + 8, y + 10, chip, RED, 1)
    yy = y + 26
    for line in wrap(story[1], 12):
        c.text(x + 8, yy, line, INK, 2)
        yy += 16
    yy += 2
    for line in wrap(summary, 25):
        c.text(x + 8, yy, line, INK, 1)
        yy += 9
    c.text(x + 8, y + h - 14, story[2], GREY, 1)


def draw():
    c = Canvas(W, H, PAPER)

    # Masthead.
    c.text(24, 8, "THE WORLD IN ONE DAY", RED, 1)
    right = "50 STORIES - 7 REGIONS - EVERY ONE DATED SUNDAY 22 NOVEMBER 2026"
    c.text(W - 24 - text_width(right, 1), 8, right, GREY, 1)
    c.text_center(24, "SUNDAY 22 NOVEMBER 2026", INK, 6)
    c.text_center(74,
                  "COP31 NEARS A DEAL - IRAN HITS US BASES IN BAHRAIN - "
                  "INDIA DECLARE ON RECORD 720-9",
                  GREY, 2)
    c.rect(24, 96, 976, 3, INK)
    c.rect(24, 101, 976, 1, INK)

    # The day in numbers: six stat boxes.
    box_w, gap = 156, 8
    for i, (big, cap1, cap2) in enumerate(NUMBERS):
        bx = 24 + i * (box_w + gap)
        c.rect(bx, 108, box_w, 48, CARD)
        c.rect(bx, 108, box_w, 1, INK)
        c.rect(bx, 108 + 47, box_w, 1, INK)
        c.rect(bx, 108, 1, 48, INK)
        c.rect(bx + box_w - 1, 108, 1, 48, INK)
        bw = text_width(big, 3)
        c.text(bx + (box_w - bw) // 2, 112, big, RED, 3)
        cw1 = text_width(cap1, 1)
        c.text(bx + (box_w - cw1) // 2, 136, cap1, INK, 1)
        cw2 = text_width(cap2, 1)
        c.text(bx + (box_w - cw2) // 2, 145, cap2, GREY, 1)

    # Region bar: seven equal segments with counts.
    seg_w = 976 // 7
    for i, (name, count, color) in enumerate(REGION_COLORS):
        sx = 24 + i * seg_w
        wseg = seg_w if i < 6 else 976 - 6 * seg_w
        c.rect(sx, 162, wseg, 20, color)
        label = "%s %d" % (name, count)
        lw = text_width(label, 1)
        c.text(sx + (wseg - lw) // 2, 167, label, WHITE, 1)

    # Lead cards: stories 1-3.
    lead_w = 320
    for i, num in enumerate((1, 2, 3)):
        draw_lead_card(c, num, 24 + i * (lead_w + 8), 190, lead_w, 210)

    # Small cards: stories 4-9, six across.
    small_w = 156
    for i, num in enumerate((4, 5, 6, 7, 8, 9)):
        draw_small_card(c, num, 24 + i * (small_w + 8), 408, small_w, 152)

    # World map.
    c.text(24, 566, "WHERE IT HAPPENED - EACH NUMBER IS THE STORY WITH THAT "
                    "NUMBER ON THIS PAGE", RED, 1)
    c.rect(MAP_X, MAP_Y, MAP_W, MAP_H, OCEAN)
    for lon in range(-150, 181, 30):
        x, _ = lonlat_to_xy(lon, 0)
        c.vline(x, MAP_Y, MAP_H, GRAT)
    for lat in range(-60, 91, 30):
        _, y = lonlat_to_xy(0, lat)
        c.hline(MAP_X, y, MAP_W, GRAT)
    for ring in CONTINENTS:
        pts = [lonlat_to_xy(lon, lat) for lon, lat in ring]
        c.polygon(pts, LAND, LANDLINE)
    c.rect(MAP_X, MAP_Y, MAP_W, 2, INK)
    c.rect(MAP_X, MAP_Y + MAP_H - 2, MAP_W, 2, INK)
    c.rect(MAP_X, MAP_Y, 2, MAP_H, INK)
    c.rect(MAP_X + MAP_W - 2, MAP_Y, 2, MAP_H, INK)

    # Numbered pins, one per story.
    for num, _headline, _outlet, lon, lat, _region in STORIES:
        x, y = lonlat_to_xy(lon, lat)
        dx, dy = PIN_DXDY.get(num, (0, 0))
        x += dx
        y += dy
        c.circle(x, y, 7, RED)
        c.ring(x, y, 7, DARKRED)
        label = str(num)
        lw = text_width(label, 1)
        c.text(x - lw // 2, y - 3, label, WHITE, 1)

    # Stories 10-50: the index, three columns.
    c.text(24, 776, "ALSO ON SUNDAY 22 NOVEMBER 2026 - 41 MORE STORIES",
           RED, 2)
    cols = (STORIES[9:23], STORIES[23:37], STORIES[37:50])
    for col_x, col in ((24, cols[0]), (352, cols[1]), (680, cols[2])):
        yy = 796
        for num, headline, outlet, _lon, _lat, _region in col:
            line = "%02d %s - %s" % (num, headline, outlet)
            line = truncate(line, 312, 1)
            c.text(col_x, yy, line, INK, 1)
            yy += 11

    # Date-check footer.
    c.rect(24, 950, 976, 1, INK)
    c.rect(24, 956, 976, 40, CARD)
    c.rect(24, 956, 976, 1, RED)
    c.rect(24, 995, 976, 1, RED)
    c.rect(24, 956, 1, 40, RED)
    c.rect(999, 956, 1, 40, RED)
    c.text(32, 962,
           "DATE CHECK - LEFT OUT AS OLDER NEWS: PERU AND TIMOR-LESTE "
           "QUAKES (FRI-SAT), RUSSIA 400-DRONE BARRAGE (THU-FRI),",
           DARKRED, 1)
    c.text(32, 974,
           "SPARTA II FIRE, BEPICOLOMBO MERCURY ORBIT, UK-EU RESET DEAL "
           "AND ESTONIA BORDER CLOSURE (FRI-SAT). EVERY STORY HERE IS SUNDAY.",
           INK, 1)
    c.text_center(1004, "TOTAL VERIFIED STORIES: 50 - ORIGINAL DRAWINGS",
                  GREY, 1)
    return c


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, "entry.png")
    size = write_png(draw(), path)
    print("wrote %s (%d bytes)" % (path, size))


if __name__ == "__main__":
    main()
