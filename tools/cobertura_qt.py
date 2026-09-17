"""Visualizador Qt: duracao declarada contra RR efetivamente gravado.

Mostra, para cada gravacao, a diferenca entre o que o ``metrics.json`` diz que
a sessao durou e o troco que tem mesmo intervalos RR escritos. A app parecia
estar a gravar; a serie RR conta outra historia.

Painel de cima  - uma barra por gravacao: cinzento = duracao declarada,
                  teal/azul = RR existente. O que sobra a direita e o buraco.
Painel do baixo - tacograma da gravacao selecionada, com a zona sem dados
                  sombreada e o fim declarado marcado.

Uso:
    python tools/cobertura_qt.py [data/sessao]
"""

from __future__ import annotations

import sys
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pyqtgraph as pg
from PySide6 import QtCore, QtGui, QtWidgets

from polarmed.config import load_config
from polarmed.io.parsers import discover_measurements, load_measurement
from polarmed.signal.rr_clean import clean_rr

# Paleta neroes (ver polarmed/report/theme.py)
INK_900, INK_700, INK_600 = "#0C1D24", "#152E38", "#1B3A46"
TEXT_1, TEXT_2, TEXT_3 = "#E9F2F3", "#A9BFC5", "#6E8B93"
TEAL, BLUE, EMBER, BRASS = "#43BEC3", "#5B8AD4", "#C4685A", "#D4A455"
BORDER = "#2A4652"

CHANT_WINDOW_MIN = 15.0

# Sora e IBM Plex Mono sao as fontes da marca mas nao estao instaladas no
# Windows. Qt nao faz fallback por familia como o CSS: uma familia ausente
# desenha caixas. Por isso pedimos aqui o que existe de certeza.
FONT_UI = "Segoe UI"
FONT_MONO = "Consolas"


@dataclass
class Rec:
    band: str
    date: str
    measurement: str
    kind: str
    declared_min: float
    rr_min: float
    n_beats: int
    pct_corrected: float
    t_min: np.ndarray
    rr_ms: np.ndarray

    @property
    def label(self) -> str:
        return f"{self.band} · {self.date[5:]} · {self.measurement}"

    @property
    def missing_min(self) -> float:
        return max(0.0, self.declared_min - self.rr_min)

    @property
    def coverage(self) -> float:
        return self.rr_min / self.declared_min if self.declared_min > 0 else 0.0

    @property
    def has_chant_window(self) -> bool:
        """Sobra sinal nos ultimos 15 minutos do relogio da sessao?"""
        return self.missing_min < 1.0 and self.rr_min >= CHANT_WINDOW_MIN


def load(source: Path) -> list[Rec]:
    cfg = load_config()
    out: list[Rec] = []
    for folder in discover_measurements(source):
        meas = load_measurement(folder)
        if meas.rr is None or meas.rr.values.size < 10:
            continue
        cleaned = clean_rr(meas.rr.values, meas.rr.timestamps_ms, cfg.rr)
        t = cleaned.t_s - cleaned.t_s[0]
        out.append(
            Rec(
                band=meas.band_id,
                date=meas.session_date,
                measurement=meas.measurement,
                kind="repouso" if "rest" in meas.measurement.lower() else "canto",
                declared_min=meas.stated_duration_s / 60.0,
                rr_min=float(t[-1]) / 60.0,
                n_beats=cleaned.n_beats,
                pct_corrected=cleaned.pct_corrected,
                t_min=t / 60.0,
                rr_ms=cleaned.rr_ms,
            )
        )
    # Pior cobertura primeiro: o problema fica no topo, nao enterrado.
    return sorted(out, key=lambda r: r.coverage)


class Window(QtWidgets.QMainWindow):
    def __init__(self, recs: list[Rec]):
        super().__init__()
        self.recs = recs
        self.setWindowTitle("Cobertura RR — declarado contra gravado")
        self.resize(1280, 860)

        pg.setConfigOptions(antialias=True, background=INK_900, foreground=TEXT_2)

        central = QtWidgets.QWidget()
        central.setStyleSheet(f"background:{INK_700};")
        layout = QtWidgets.QVBoxLayout(central)
        layout.setContentsMargins(16, 14, 16, 14)
        layout.setSpacing(12)
        self.setCentralWidget(central)

        layout.addWidget(self._header())
        layout.addWidget(self._coverage_plot(), stretch=3)
        layout.addWidget(self._detail_header())
        layout.addWidget(self._tacogram_plot(), stretch=4)
        layout.addWidget(self._footer())

        self.select(0)

    # ---------------------------------------------------------------- chrome
    def _label(self, text: str, size: int, colour: str, mono=False, bold=False):
        w = QtWidgets.QLabel(text)
        family = FONT_MONO if mono else FONT_UI
        weight = "600" if bold else "400"
        spacing = "letter-spacing:2px;" if mono else ""
        w.setStyleSheet(
            f"color:{colour};font-family:{family};font-size:{size}px;"
            f"font-weight:{weight};{spacing}background:transparent;"
        )
        return w

    def _header(self):
        box = QtWidgets.QWidget()
        v = QtWidgets.QVBoxLayout(box)
        v.setContentsMargins(4, 0, 4, 0)
        v.setSpacing(3)
        v.addWidget(self._label("COBERTURA DA SERIE RR", 10, TEAL, mono=True))
        v.addWidget(
            self._label(
                "Barra cinzenta = duração que o metrics.json declara. "
                "Barra colorida = troço que tem mesmo intervalos RR escritos.",
                14, TEXT_2,
            )
        )
        return box

    def _detail_header(self):
        self.detail_label = self._label("", 13, TEXT_1, mono=True)
        return self.detail_label

    def _footer(self):
        self.footer_label = self._label(
            "Clique numa barra ou use ↑ ↓ para mudar de gravação · "
            "arraste para deslocar, roda do rato para ampliar",
            11, TEXT_3,
        )
        return self.footer_label

    # ----------------------------------------------------------- top: barras
    def _coverage_plot(self):
        self.cov = pg.PlotWidget()
        self.cov.setMenuEnabled(False)
        self.cov.showGrid(x=True, y=False, alpha=0.18)
        self.cov.setLabel("bottom", "MINUTOS")
        self.cov.getAxis("bottom").setPen(BORDER)
        self.cov.getAxis("left").setPen(BORDER)

        n = len(self.recs)
        ticks = []
        for i, r in enumerate(self.recs):
            y = n - 1 - i  # pior no topo
            ticks.append((y, r.label))

            # declarado: o que a app dizia estar a gravar
            self.cov.addItem(
                pg.BarGraphItem(
                    x0=[0], y=[y], height=0.62, width=[r.declared_min],
                    brush=pg.mkBrush("#22333D"), pen=pg.mkPen(BORDER, width=1),
                )
            )
            # efetivo: o que existe mesmo
            colour = TEAL if r.kind == "canto" else BLUE
            self.cov.addItem(
                pg.BarGraphItem(
                    x0=[0], y=[y], height=0.62, width=[r.rr_min],
                    brush=pg.mkBrush(colour), pen=pg.mkPen(None),
                )
            )
            # o buraco, com a legenda dos minutos perdidos
            if r.missing_min > 0.5:
                text = pg.TextItem(
                    f"faltam {r.missing_min:.1f} min", color=EMBER, anchor=(0, 0.5)
                )
                text.setPos(r.rr_min + 0.4, y)
                font = QtGui.QFont(FONT_MONO, 8)
                text.setFont(font)
                self.cov.addItem(text)

        self.cov.getAxis("left").setTicks([ticks])
        self.cov.getAxis("left").setWidth(230)
        self.cov.setYRange(-0.6, n - 0.4)
        self.cov.setXRange(0, max(r.declared_min for r in self.recs) * 1.22)

        # linha dos 15 min: a janela de canto
        line = pg.InfiniteLine(
            pos=CHANT_WINDOW_MIN, angle=90,
            pen=pg.mkPen(BRASS, width=1, style=QtCore.Qt.DashLine),
            label="janela de canto = 15 min",
            labelOpts={"color": BRASS, "position": 0.04, "movable": False},
        )
        self.cov.addItem(line)

        self.cursor = pg.InfiniteLine(
            pos=0, angle=0, pen=pg.mkPen(TEXT_1, width=2, style=QtCore.Qt.DotLine)
        )
        self.cov.addItem(self.cursor)
        self.cov.scene().sigMouseClicked.connect(self._on_click)
        return self.cov

    def _on_click(self, event):
        point = self.cov.plotItem.vb.mapSceneToView(event.scenePos())
        index = len(self.recs) - 1 - int(round(point.y()))
        if 0 <= index < len(self.recs):
            self.select(index)

    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_Down:
            self.select(min(self.index + 1, len(self.recs) - 1))
        elif event.key() == QtCore.Qt.Key_Up:
            self.select(max(self.index - 1, 0))
        else:
            super().keyPressEvent(event)

    # ------------------------------------------------------ baixo: tacograma
    def _tacogram_plot(self):
        self.taco = pg.PlotWidget()
        self.taco.setMenuEnabled(False)
        self.taco.showGrid(x=True, y=True, alpha=0.18)
        self.taco.setLabel("bottom", "MINUTOS DESDE O INÍCIO DA GRAVAÇÃO")
        self.taco.setLabel("left", "INTERVALO RR (ms)")
        self.taco.getAxis("bottom").setPen(BORDER)
        self.taco.getAxis("left").setPen(BORDER)
        return self.taco

    def select(self, index: int):
        self.index = index
        r = self.recs[index]
        self.cursor.setPos(len(self.recs) - 1 - index)

        self.taco.clear()
        colour = TEAL if r.kind == "canto" else BLUE

        # zona sem dados: entre o fim do RR e o fim declarado
        if r.missing_min > 0.05:
            region = pg.LinearRegionItem(
                values=(r.rr_min, r.declared_min), movable=False,
                brush=pg.mkBrush(196, 104, 90, 38),
                pen=pg.mkPen(EMBER, width=1, style=QtCore.Qt.DashLine),
            )
            region.setZValue(-10)
            self.taco.addItem(region)

            note = pg.TextItem(
                f"SEM DADOS\n{r.missing_min:.1f} min", color=EMBER, anchor=(0.5, 0.5)
            )
            note.setFont(QtGui.QFont(FONT_MONO, 11, QtGui.QFont.Bold))
            note.setPos((r.rr_min + r.declared_min) / 2, float(np.median(r.rr_ms)))
            self.taco.addItem(note)

        # a janela que a analise QUERIA usar: ultimos 15 min do relogio
        window_start = r.declared_min - CHANT_WINDOW_MIN
        if window_start > 0:
            self.taco.addItem(
                pg.LinearRegionItem(
                    values=(window_start, r.declared_min), movable=False,
                    brush=pg.mkBrush(212, 164, 85, 26), pen=pg.mkPen(None),
                )
            )

        self.taco.plot(
            r.t_min, r.rr_ms, pen=pg.mkPen(colour, width=1.2),
            name=r.label, antialias=True,
        )
        self.taco.addItem(
            pg.InfiniteLine(
                pos=r.declared_min, angle=90,
                pen=pg.mkPen(EMBER, width=2),
                label="fim declarado", labelOpts={"color": EMBER, "position": 0.9},
            )
        )
        self.taco.addItem(
            pg.InfiniteLine(
                pos=r.rr_min, angle=90,
                pen=pg.mkPen(colour, width=2, style=QtCore.Qt.DashLine),
                label="último RR", labelOpts={"color": colour, "position": 0.75},
            )
        )

        self.taco.setXRange(0, r.declared_min * 1.03)
        lo, hi = float(np.percentile(r.rr_ms, 1)), float(np.percentile(r.rr_ms, 99))
        pad = max(60.0, (hi - lo) * 0.25)
        self.taco.setYRange(lo - pad, hi + pad)

        verdict = (
            "janela de canto utilizável"
            if r.has_chant_window
            else "janela de canto SEM DADOS — gravação descartada"
        )
        self.detail_label.setText(
            f"{r.label}   ·   declarado {r.declared_min:.1f} min   ·   "
            f"RR até {r.rr_min:.1f} min   ·   cobertura {r.coverage * 100:.0f}%   ·   "
            f"{r.n_beats} batimentos   ·   {r.pct_corrected:.1f}% corrigidos   ·   {verdict}"
        )
        self.detail_label.setStyleSheet(
            self.detail_label.styleSheet().replace(TEXT_1, TEXT_1)
            + f"color:{TEAL if r.has_chant_window else EMBER};"
        )


def main() -> int:
    source = Path(sys.argv[1] if len(sys.argv) > 1 else "data/sessao")
    recs = load(source)
    if not recs:
        print(f"nenhuma gravacao em {source}")
        return 1

    app = QtWidgets.QApplication(sys.argv)
    app.setFont(QtGui.QFont(FONT_UI, 9))
    window = Window(recs)
    window.show()
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
