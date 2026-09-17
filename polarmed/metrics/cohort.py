"""Agregação entre gravações: o que se moveu com o canto, e com que consistência.

Metodologia transposta do projeto Mantra_EEG (`neroes-tech/Mantra_EEG`,
`src/mantraeeg/stats.py` e `cohort.py`), que resolve para EEG o mesmo problema
que aqui se põe para ECG. Três decisões governam este módulo, todas na direção
conservadora:

- **A unidade é a gravação, não a janela.** Juntar as janelas deslizantes de
  toda a gente num só saco daria intervalos estreitíssimos e falsos: janelas
  dentro da mesma pessoa não são independentes umas das outras — com 120 s de
  janela e 10 s de passo, janelas vizinhas partilham 92 % das amostras. Cada
  gravação contribui **um** número, e a estatística corre sobre esses.
- **A consistência do sinal conta mais do que a magnitude.** Com três
  gravações, "as três subiram" diz mais do que uma média com um intervalo
  enorme. O teste de sinal não assume distribuição nenhuma.
- **Dentro de cada gravação**, o intervalo de confiança vem de um bootstrap
  **por blocos**, com comprimento de bloco estimado da autocorrelação. Um
  bootstrap comum trataria janelas sobrepostas como independentes e devolveria
  um intervalo várias vezes mais estreito do que o honesto.

O que isto **não** é: demonstração de que o canto causa alguma coisa. Sem um
braço de controlo — as mesmas pessoas, os mesmos minutos, em silêncio — a
variação encontrada pode ser o efeito de estar sentado e quieto durante meia
hora. :func:`aggregate` devolve esse aviso com os dados, não em rodapé.
"""

from __future__ import annotations

import math
from dataclasses import dataclass

import numpy as np

#: Mínimo de janelas por fase para uma gravação contribuir com um marcador.
#: Abaixo disto o bootstrap por blocos não tem material para reamostrar.
MIN_EPOCHS = 8


@dataclass(frozen=True, slots=True)
class Estimate:
    """Uma estimativa com intervalo de confiança por bootstrap por blocos."""

    value: float
    ci_low: float
    ci_high: float
    block_len: int
    n: int

    @property
    def n_effective(self) -> float:
        """Amostras independentes, aproximadamente ``n / comprimento do bloco``.

        Com poucas, nenhum intervalo é de confiar: a decisão certa é recusar-se
        a concluir, não produzir um intervalo apertado a partir de nada.
        """
        return self.n / self.block_len if self.block_len else float("nan")

    @property
    def crosses_zero(self) -> bool:
        return bool(
            np.isfinite(self.ci_low)
            and np.isfinite(self.ci_high)
            and self.ci_low <= 0.0 <= self.ci_high
        )

    @property
    def excludes_zero(self) -> bool:
        return bool(np.isfinite(self.ci_low)) and not self.crosses_zero


# --------------------------------------------------------------------------- #
# Dimensão de efeito
# --------------------------------------------------------------------------- #
def cliffs_delta(a: np.ndarray, b: np.ndarray) -> float:
    """``P(b > a) - P(a > b)``. Robusto, não paramétrico.

    Invariante a qualquer reescalonamento monótono, portanto normalizar os
    dados antes de o calcular não faz nada — a inferência corre em unidades
    cruas.
    """
    a = np.asarray(a, dtype=np.float64)
    b = np.asarray(b, dtype=np.float64)
    a, b = a[np.isfinite(a)], b[np.isfinite(b)]
    if a.size == 0 or b.size == 0:
        return float("nan")
    greater = int((b[:, None] > a[None, :]).sum())
    less = int((b[:, None] < a[None, :]).sum())
    return (greater - less) / (a.size * b.size)


def interpret_delta(delta: float) -> str:
    """Rótulos convencionais para o delta de Cliff."""
    magnitude = abs(delta)
    if not np.isfinite(magnitude):
        return "indeterminado"
    if magnitude < 0.147:
        return "desprezável"
    if magnitude < 0.33:
        return "pequeno"
    if magnitude < 0.474:
        return "médio"
    return "grande"


def median_difference(a: np.ndarray, b: np.ndarray) -> float:
    """``mediana(b) - mediana(a)``, nas unidades do marcador."""
    return float(np.median(b) - np.median(a))


# --------------------------------------------------------------------------- #
# Comprimento de bloco, a partir da autocorrelação
# --------------------------------------------------------------------------- #
def decorrelation_lag(x: np.ndarray, threshold: float = 0.3679) -> int:
    """Primeiro lag em que a autocorrelação cai abaixo de ``threshold`` (1/e)."""
    x = np.asarray(x, dtype=np.float64)
    x = x[np.isfinite(x)]
    n = x.size
    if n < 4:
        return 1
    centred = x - x.mean()
    denom = float(np.dot(centred, centred))
    if denom <= 0:
        return 1
    acf = np.correlate(centred, centred, mode="full")[n - 1 :] / denom
    below = np.nonzero(acf < threshold)[0]
    return int(below[0]) if below.size else n // 2


def auto_block_length(
    x: np.ndarray,
    hop_s: float,
    window_s: float,
    max_length_s: float = 600.0,
    multiplier: float = 2.0,
) -> int:
    """Comprimento de bloco em janelas, estimado da autocorrelação e limitado.

    O piso existe porque janelas deslizantes sobrepostas partilham amostras:
    nenhum bloco honesto pode ser mais curto do que a própria sobreposição.
    Não se limita o bloco em função de ``n`` — um bloco comparável ao
    comprimento da série torna o bootstrap degenerado, mas a resposta a isso é
    **denunciar** através de :attr:`Estimate.n_effective`, não encolher o bloco
    e fixar ``n_effective`` por construção.
    """
    lag = decorrelation_lag(x)
    epochs = int(np.ceil(multiplier * lag))
    floor = max(int(np.ceil(window_s / hop_s)), 2)
    ceiling = max(int(np.floor(max_length_s / hop_s)), floor)
    return int(np.clip(epochs, floor, ceiling))


def _stationary_indices(
    n: int, block_len: int, rng: np.random.Generator
) -> np.ndarray:
    """Índices de uma reamostra pelo bootstrap estacionário (Politis-Romano).

    Blocos de comprimento geométrico, e não fixo: evita artefactos das
    fronteiras rígidas e mantém a série reamostrada estacionária.
    """
    if n <= 0:
        return np.zeros(0, dtype=int)
    p = 1.0 / max(block_len, 1)
    out = np.empty(n, dtype=int)
    i = 0
    while i < n:
        out[i] = rng.integers(n)
        i += 1
        while i < n and rng.random() >= p:
            out[i] = (out[i - 1] + 1) % n
            i += 1
    return out


def block_bootstrap_ci(
    a: np.ndarray,
    b: np.ndarray,
    statistic,
    hop_s: float,
    window_s: float,
    n_boot: int = 2000,
    ci_level: float = 0.95,
    seed: int = 0,
) -> Estimate:
    """IC por bootstrap estacionário por blocos, para duas séries de janelas.

    Cada réplica reamostra **as duas** séries por blocos, preservando a
    dependência temporal que a sobreposição das janelas deixa.
    """
    a = np.asarray(a, dtype=np.float64)
    b = np.asarray(b, dtype=np.float64)
    a, b = a[np.isfinite(a)], b[np.isfinite(b)]
    if a.size < MIN_EPOCHS or b.size < MIN_EPOCHS:
        return Estimate(
            float("nan"), float("nan"), float("nan"), 0, int(min(a.size, b.size))
        )

    block = max(
        auto_block_length(a, hop_s, window_s),
        auto_block_length(b, hop_s, window_s),
    )
    rng = np.random.default_rng(seed)
    replicates = np.empty(n_boot)
    for i in range(n_boot):
        ra = a[_stationary_indices(a.size, block, rng)]
        rb = b[_stationary_indices(b.size, block, rng)]
        replicates[i] = statistic(ra, rb)

    finite = replicates[np.isfinite(replicates)]
    observed = statistic(a, b)
    if finite.size < n_boot // 10:
        return Estimate(
            observed, float("nan"), float("nan"), block, int(min(a.size, b.size))
        )
    alpha = (1.0 - ci_level) / 2.0
    return Estimate(
        value=float(observed),
        ci_low=float(np.percentile(finite, 100 * alpha)),
        ci_high=float(np.percentile(finite, 100 * (1 - alpha))),
        block_len=block,
        n=int(min(a.size, b.size)),
    )


# --------------------------------------------------------------------------- #
# Entre gravações
# --------------------------------------------------------------------------- #
def sign_test_p(n_up: int, n: int) -> float:
    """Teste de sinal bilateral exato. Sem aproximações, que ``n`` é pequeno."""
    if n == 0:
        return 1.0
    extreme = min(n_up, n - n_up)
    tail = sum(math.comb(n, k) for k in range(extreme + 1))
    return min(1.0, 2.0 * tail / (2.0**n))


def min_attainable_sign_p(n: int) -> float:
    """O p mais pequeno que ``n`` gravações conseguem produzir.

    Com três gravações vale 0,25: a unanimidade não consegue descer daí, por
    mais perfeita que seja. Publicar um p sem este número ao lado convida a
    uma leitura errada em qualquer das direções.
    """
    return sign_test_p(n, n) if n else 1.0


def median_ci_by_recording(
    values: np.ndarray, draws: int = 4000, seed: int = 11
) -> tuple[float, float]:
    """IC de 95 % da mediana, por reamostragem das **gravações**.

    Reamostrar gravações e não janelas é o que impede o intervalo de encolher
    artificialmente: a unidade independente é a pessoa que se sentou, não o
    pedaço de dois minutos.
    """
    values = np.asarray(values, dtype=np.float64)
    values = values[np.isfinite(values)]
    if values.size < 3:
        return float("nan"), float("nan")
    rng = np.random.default_rng(seed)
    idx = rng.integers(0, values.size, size=(draws, values.size))
    medians = np.median(values[idx], axis=1)
    return float(np.percentile(medians, 2.5)), float(np.percentile(medians, 97.5))


@dataclass(frozen=True, slots=True)
class MarkerAggregate:
    """O que um marcador fez ao longo de todas as gravações."""

    key: str
    label: str
    unit: str
    n_recordings: int
    median_delta: float
    ci_low: float
    ci_high: float
    n_up: int
    sign_p: float
    min_sign_p: float
    per_recording: tuple[tuple[str, float, float, float], ...]
    """``(gravação, baseline, canto, delta)``, um por gravação."""
    cliffs: tuple[tuple[str, float], ...]
    """``(gravação, delta de Cliff)`` calculado sobre as janelas de cada uma."""

    @property
    def n_down(self) -> int:
        return self.n_recordings - self.n_up

    @property
    def direction(self) -> str:
        if not np.isfinite(self.median_delta) or self.median_delta == 0:
            return "sem variação"
        return "subiu" if self.median_delta > 0 else "desceu"

    @property
    def unanimous(self) -> bool:
        return self.n_recordings > 0 and self.n_up in (0, self.n_recordings)

    @property
    def consistent(self) -> bool:
        """O sentido repete-se mais do que o acaso explica.

        Com três gravações isto é sempre falso: o p mínimo atingível é 0,25.
        A propriedade existe para que a página o diga por extenso, em vez de
        apresentar unanimidade como se fosse prova.
        """
        return self.sign_p < 0.05
