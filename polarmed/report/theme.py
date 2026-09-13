"""Design tokens extracted from the neroes design system in ``reference/``.

The vocabulary is reconstructed here rather than copied: the reference is a
single-participant sheet built on a canvas runtime, and this report is a
multi-section cohort page. What carries across is the system - petrol ink
surfaces, 1px instrument hairlines, mono labels in wide caps, luminous data on
dark beds - not the markup.

See ``docs/DESIGN_NOTES.md`` for what was extracted and why.
"""

from __future__ import annotations

# --- Petrol ink ladder: surfaces, deep to raised -------------------------
INK_900 = "#0C1D24"  # inset wells, chart beds
INK_800 = "#10262F"
INK_700 = "#152E38"  # page base
INK_600 = "#1B3A46"  # cards
INK_500 = "#224552"  # raised / hover
HEADER = "#0B333C"  # header and footer bands

# --- Brand accents -------------------------------------------------------
TEAL = "#2E9296"
GREEN = "#479B7E"
BLUE = "#3A67AE"
BRASS = "#B8873C"

TEAL_BRIGHT = "#43BEC3"
GREEN_BRIGHT = "#5BBC99"
BLUE_BRIGHT = "#5B8AD4"
BRASS_BRIGHT = "#D4A455"
EMBER = "#C4685A"  # degraded / excluded - the brand has no red

# --- Text ----------------------------------------------------------------
TEXT_1 = "#E9F2F3"
TEXT_2 = "#A9BFC5"
TEXT_3 = "#6E8B93"

BORDER_1 = "rgba(169,191,197,0.16)"
BORDER_2 = "rgba(169,191,197,0.28)"
DIVIDER = "rgba(169,191,197,0.09)"

FONT_SANS = "'Sora','Avenir Next','Segoe UI',system-ui,sans-serif"
FONT_MONO = "'IBM Plex Mono','SFMono-Regular',Menlo,monospace"
FONT_SERIF = "'Newsreader',Georgia,serif"

# --- Semantic roles ------------------------------------------------------
# Few, fixed, and meaningful - these get the brand palette (PLAN.md 4.9).
ROLE_REST = BLUE_BRIGHT
ROLE_CHANT = TEAL_BRIGHT
ROLE_GUARD = TEXT_3
ROLE_EXCLUDED = EMBER
ROLE_GOOD = GREEN_BRIGHT
ROLE_WARN = BRASS_BRIGHT

# Many, unordered, not meaningful - band identity is carried by hover and
# legend, not by hue, because teal/green/blue collapse under deuteranopia.
BAND_RAMP = [
    "#43BEC3", "#5BBC99", "#5B8AD4", "#D4A455",
    "#2E9296", "#479B7E", "#3A67AE", "#B8873C",
    "#7FD4D8", "#8FD3B8", "#8FAFE0", "#E3C489",
]


def band_colour(index: int) -> str:
    return BAND_RAMP[index % len(BAND_RAMP)]


def plotly_layout(height: int = 340, showlegend: bool = True) -> dict:
    """Shared Plotly layout so figures read as part of the page, not pasted in."""
    return {
        "height": height,
        "paper_bgcolor": "rgba(0,0,0,0)",
        "plot_bgcolor": INK_900,
        "font": {"family": FONT_SANS, "size": 12, "color": TEXT_2},
        "margin": {"l": 58, "r": 18, "t": 28, "b": 46},
        "showlegend": showlegend,
        "legend": {
            "font": {"family": FONT_MONO, "size": 10, "color": TEXT_2},
            "bgcolor": "rgba(0,0,0,0)",
            "orientation": "h",
            "yanchor": "bottom",
            "y": 1.02,
            "x": 0,
        },
        "xaxis": {
            "gridcolor": DIVIDER,
            "zerolinecolor": BORDER_1,
            "linecolor": BORDER_1,
            "tickfont": {"family": FONT_MONO, "size": 10, "color": TEXT_3},
            "title": {"font": {"family": FONT_MONO, "size": 10, "color": TEXT_3}},
        },
        "yaxis": {
            "gridcolor": DIVIDER,
            "zerolinecolor": BORDER_1,
            "linecolor": BORDER_1,
            "tickfont": {"family": FONT_MONO, "size": 10, "color": TEXT_3},
            "title": {"font": {"family": FONT_MONO, "size": 10, "color": TEXT_3}},
        },
        "hoverlabel": {
            "bgcolor": INK_600,
            "bordercolor": BORDER_2,
            "font": {"family": FONT_MONO, "size": 11, "color": TEXT_1},
        },
    }


# Compliance and honesty guards. The build fails if generated prose contains
# any of these (PLAN.md 4.2 and 4.5).
FORBIDDEN_TERMS = (
    "significativo",
    "significativa",
    "significativamente",
    "tónus vagal",
    "tonus vagal",
    "prova que",
    "comprova",
    "demonstra que",
    "cura",
)
