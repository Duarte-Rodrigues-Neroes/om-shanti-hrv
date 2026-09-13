"""Render the cohort report to a single self-contained HTML file.

Everything is inlined - Plotly, the brand webfonts as base64 woff2, the logo,
and the data as a JSON island. The page must open by double-click with no
network, because the room where it gets shown may not have any.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from polarmed.report import theme
from polarmed.report.build import sanitise

ASSETS = Path(__file__).resolve().parent / "assets"


def _asset(name: str) -> str:
    path = ASSETS / name
    if not path.exists():
        raise FileNotFoundError(
            f"{path} em falta - corra `python tools/vendor_assets.py` primeiro"
        )
    return path.read_text(encoding="utf-8")


def fmt(value: Any, digits: int = 1, dash: str = "—") -> str:
    if value is None:
        return dash
    try:
        return f"{float(value):.{digits}f}"
    except (TypeError, ValueError):
        return str(value)


def check_prose(prose: str) -> list[str]:
    """Fail the build on language the data does not support (PLAN.md 4.2, 4.5).

    Run against the authored prose only, never the finished page: the vendored
    Plotly bundle and the base64 font blobs contain arbitrary byte sequences,
    and matching "cura" inside a minified library is a false positive that would
    make the guard useless.
    """
    lowered = prose.lower()
    return [term for term in theme.FORBIDDEN_TERMS if term.lower() in lowered]


# --------------------------------------------------------------------------
# Page fragments
# --------------------------------------------------------------------------

CSS = f"""
*{{box-sizing:border-box}}
body{{margin:0;background:{theme.INK_900};color:{theme.TEXT_2};
  font-family:{theme.FONT_SANS};font-size:15px;line-height:1.6;
  -webkit-font-smoothing:antialiased;text-rendering:optimizeLegibility}}
h1,h2,h3{{color:{theme.TEXT_1};font-weight:600;line-height:1.25;
  letter-spacing:-0.015em;margin:0}}
a{{color:{theme.TEAL_BRIGHT};text-decoration:none}}
a:hover{{color:{theme.TEXT_1}}}
.wrap{{display:flex;gap:0;max-width:1240px;margin:0 auto;padding:28px 16px 72px;
  align-items:flex-start}}

/* --- sticky section nav --- */
nav{{position:sticky;top:28px;flex:0 0 210px;padding:8px 20px 8px 4px}}
nav .brand{{margin-bottom:22px}}
nav .brand img{{height:40px;width:auto;display:block}}
nav ol{{list-style:none;margin:0;padding:0;
  border-left:1px solid {theme.BORDER_1}}}
nav li a{{display:block;padding:7px 0 7px 14px;font-family:{theme.FONT_MONO};
  font-size:10px;font-weight:500;letter-spacing:0.13em;text-transform:uppercase;
  color:{theme.TEXT_3};border-left:2px solid transparent;margin-left:-1px;
  transition:color .12s cubic-bezier(.2,.7,.3,1)}}
nav li a:hover{{color:{theme.TEXT_1};border-left-color:{theme.TEAL}}}

/* --- sheet --- */
main{{flex:1;min-width:0;background:{theme.INK_700};
  border:1px solid {theme.BORDER_1};border-radius:10px;overflow:hidden}}
header.sheet{{background:{theme.HEADER};padding:26px 38px;display:flex;
  align-items:center;justify-content:space-between;gap:24px;flex-wrap:wrap}}
.eyebrow{{font-family:{theme.FONT_MONO};font-size:10px;font-weight:500;
  letter-spacing:0.22em;text-transform:uppercase;color:{theme.TEXT_3}}}
.eyebrow.accent{{color:{theme.TEAL}}}
section{{padding:34px 38px}}
section+section{{border-top:1px solid {theme.DIVIDER}}}
.sechead{{display:flex;align-items:baseline;gap:14px;margin-bottom:18px}}
.sechead .rule{{flex:1;height:1px;background:{theme.DIVIDER}}}
p{{margin:0 0 14px;max-width:74ch;text-wrap:pretty}}
p:last-child{{margin-bottom:0}}
.lead{{font-size:16px;color:{theme.TEXT_2}}}

/* --- metric cards --- */
.cards{{display:grid;grid-template-columns:repeat(auto-fit,minmax(210px,1fr));
  gap:12px;margin:22px 0}}
.card{{background:{theme.INK_600};border:1px solid {theme.BORDER_1};
  border-radius:10px;padding:18px;display:flex;flex-direction:column;gap:10px}}
.card .lbl{{font-family:{theme.FONT_MONO};font-size:9px;font-weight:500;
  letter-spacing:0.2em;text-transform:uppercase;color:{theme.TEXT_3}}}
.card .val{{font-size:34px;font-weight:600;letter-spacing:-0.03em;line-height:1;
  color:{theme.TEXT_1};font-variant-numeric:tabular-nums}}
.card .unit{{font-family:{theme.FONT_MONO};font-size:11px;letter-spacing:.09em;
  color:{theme.TEXT_3};margin-left:6px}}
.card .foot{{font-size:12.5px;line-height:1.5;color:{theme.TEXT_2};
  padding-top:10px;border-top:1px solid {theme.DIVIDER}}}

/* --- callouts --- */
.note{{border-left:2px solid {theme.BRASS};background:rgba(184,135,60,.07);
  padding:14px 18px;border-radius:0 6px 6px 0;margin:18px 0;font-size:14px}}
.note.hard{{border-left-color:{theme.EMBER};background:rgba(196,104,90,.08)}}
.note.good{{border-left-color:{theme.GREEN};background:rgba(71,155,126,.07)}}
.note b{{color:{theme.TEXT_1};font-weight:600}}

/* --- charts --- */
.chartbed{{background:{theme.INK_900};border:1px solid {theme.BORDER_1};
  border-radius:8px;padding:10px;margin:16px 0}}
.cap{{font-family:{theme.FONT_MONO};font-size:10px;letter-spacing:.12em;
  text-transform:uppercase;color:{theme.TEXT_3};margin:10px 2px 0}}
.ctrl{{display:flex;gap:8px;flex-wrap:wrap;margin:14px 0 2px}}
.ctrl button{{font-family:{theme.FONT_MONO};font-size:10px;font-weight:500;
  letter-spacing:.13em;text-transform:uppercase;padding:7px 15px;
  border-radius:999px;border:1px solid {theme.BORDER_1};cursor:pointer;
  background:transparent;color:{theme.TEXT_2};
  transition:all .12s cubic-bezier(.2,.7,.3,1)}}
.ctrl button:hover{{border-color:{theme.BORDER_2};color:{theme.TEXT_1}}}
.ctrl button[aria-pressed="true"]{{background:{theme.TEAL};color:#0E2129;
  border-color:{theme.TEAL}}}

/* --- tables --- */
.scroll{{overflow-x:auto;margin:16px 0}}
table{{border-collapse:collapse;width:100%;font-size:13px;min-width:640px}}
th{{font-family:{theme.FONT_MONO};font-size:9px;font-weight:500;
  letter-spacing:.17em;text-transform:uppercase;color:{theme.TEXT_3};
  text-align:right;padding:9px 11px;border-bottom:1px solid {theme.BORDER_1};
  white-space:nowrap}}
th:first-child,td:first-child{{text-align:left}}
td{{padding:9px 11px;border-bottom:1px solid {theme.DIVIDER};text-align:right;
  font-variant-numeric:tabular-nums;white-space:nowrap}}
tr:hover td{{background:rgba(169,191,197,.03)}}
.mono{{font-family:{theme.FONT_MONO};font-size:12px;letter-spacing:.04em}}
.pill{{display:inline-block;font-family:{theme.FONT_MONO};font-size:10px;
  font-weight:500;letter-spacing:.09em;padding:2px 9px;border-radius:999px}}
.pill.ok{{color:{theme.GREEN_BRIGHT};background:rgba(91,188,153,.14)}}
.pill.warn{{color:{theme.BRASS_BRIGHT};background:rgba(212,164,85,.14)}}
.pill.bad{{color:{theme.EMBER};background:rgba(196,104,90,.16)}}
.pill.rest{{color:{theme.BLUE_BRIGHT};background:rgba(91,138,212,.14)}}
.pill.chant{{color:{theme.TEAL_BRIGHT};background:rgba(67,190,195,.14)}}
.dim{{color:{theme.TEXT_3}}}

/* --- vision quote --- */
.quote{{border-top:1px solid {theme.BORDER_1};border-bottom:1px solid {theme.BORDER_1};
  padding:28px 0;margin:28px 0;display:flex;gap:16px;align-items:flex-start}}
.quote .dot{{width:7px;height:7px;border-radius:50%;background:{theme.BRASS};
  flex:none;margin-top:13px}}
.quote p{{font-family:{theme.FONT_SERIF};font-style:italic;font-size:22px;
  line-height:1.42;color:{theme.TEXT_1};margin:0;max-width:40ch}}

footer{{background:{theme.HEADER};border-top:1px solid {theme.BORDER_1};
  padding:30px 38px;display:flex;flex-direction:column;gap:14px}}
footer p{{font-size:12px;line-height:1.6;color:{theme.TEXT_3};max-width:78ch}}

@media (max-width:900px){{
  nav{{display:none}}
  .wrap{{padding:14px 12px 48px}}
  section{{padding:26px 18px}}
  header.sheet{{padding:20px 18px}}
  footer{{padding:24px 18px}}
}}
@media print{{
  body{{background:#fff}}
  nav,.ctrl{{display:none}}
  main{{border:0}}
  section{{break-inside:avoid}}
}}
"""


def section_head(number: str, title: str) -> str:
    return (
        f'<div class="sechead"><span class="eyebrow">{number} — {title}</span>'
        f'<span class="rule"></span></div>'
    )


def stat_card(label: str, value: str, unit: str, foot: str) -> str:
    return f"""<div class="card">
  <span class="lbl">{label}</span>
  <div><span class="val">{value}</span><span class="unit">{unit}</span></div>
  <div class="foot">{foot}</div>
</div>"""


def render(bundle: dict[str, Any], out_path: Path) -> Path:
    # NaN is not JSON; it would parse as a JS literal but break JSON.parse.
    bundle = sanitise(bundle)
    recordings = bundle["recordings"]
    comparison = bundle["comparison"]
    separation = bundle["separation"]

    rest = [r for r in recordings if r["kind"] == "repouso"]
    chant = [r for r in recordings if r["kind"] == "canto"]

    slow_rest = comparison["slow_hf_log"]["repouso"]
    slow_chant = comparison["slow_hf_log"]["canto"]
    hr_rest = comparison["mean_HR"]["repouso"]
    hr_chant = comparison["mean_HR"]["canto"]
    rmssd_rest = comparison["RMSSD"]["repouso"]
    rmssd_chant = comparison["RMSSD"]["canto"]

    # Linear-scale reading of the log ratio: how many times more power sits in
    # the slow band than in HF. Easier to say out loud than a log difference.
    fold_rest = 10 ** slow_rest["median"] if slow_rest["median"] is not None else None
    fold_chant = 10 ** slow_chant["median"] if slow_chant["median"] is not None else None

    nav_items = [
        ("s1", "01 Resultado"),
        ("s2", "02 Métodos"),
        ("s3", "03 Tacogramas"),
        ("s4", "04 Assinatura lenta"),
        ("s5", "05 Repouso vs canto"),
        ("s6", "06 Ao longo da sessão"),
        ("s7", "07 Contexto"),
        ("s8", "08 Qualidade"),
        ("s9", "09 Apêndice"),
    ]
    nav_html = "".join(
        f'<li><a href="#{anchor}">{label}</a></li>' for anchor, label in nav_items
    )

    # ---- quality table ----
    quality_rows = []
    for r in sorted(recordings, key=lambda x: (x["session_date"], x["band_id"])):
        covers = r["covers_session_end"]
        pill = (
            '<span class="pill ok">completa</span>'
            if covers
            else f'<span class="pill bad">-{fmt(r["truncated_min"])} min</span>'
        )
        kind_pill = (
            '<span class="pill rest">repouso</span>'
            if r["kind"] == "repouso"
            else '<span class="pill chant">canto</span>'
        )
        quality_rows.append(
            f"<tr><td class='mono'>{r['band_id']}</td>"
            f"<td class='mono dim'>{r['session_date'][5:]}</td>"
            f"<td class='mono dim'>{r['measurement']}</td>"
            f"<td>{kind_pill}</td>"
            f"<td>{fmt(r['stated_min'])}</td>"
            f"<td>{fmt(r['rr_min'])}</td>"
            f"<td>{r['n_beats']}</td>"
            f"<td>{fmt(r['pct_corrected'], 2)}</td>"
            f"<td>{pill}</td></tr>"
        )

    # ---- cohort table ----
    cohort_rows = []
    for r in sorted(recordings, key=lambda x: (x["kind"], x["band_id"])):
        m = r["window_metrics"]
        kind_pill = (
            '<span class="pill rest">repouso</span>'
            if r["kind"] == "repouso"
            else '<span class="pill chant">canto</span>'
        )
        if not r.get("in_aggregates", True):
            kind_pill += ' <span class="pill bad">fora dos agregados</span>'
        cohort_rows.append(
            f"<tr><td class='mono'>{r['band_id']}</td>"
            f"<td>{kind_pill}</td>"
            f"<td>{fmt(r['slow_hf_log'], 2)}</td>"
            f"<td>{fmt(m.get('peak_freq_hz'), 4)}</td>"
            f"<td>{fmt(m.get('spectral_concentration'), 2)}</td>"
            f"<td>{fmt(m.get('RMSSD'))}</td>"
            f"<td>{fmt(m.get('mean_HR'))}</td>"
            f"<td>{fmt(m.get('SDNN'))}</td>"
            f"<td>{fmt(m.get('pNN50'))}</td></tr>"
        )

    def range_cell(stats: dict) -> str:
        if not stats["n"]:
            return "<td class='dim'>—</td>"
        return (
            f"<td>{fmt(stats['median'], 2)} "
            f"<span class='dim'>[{fmt(stats['min'], 2)}, {fmt(stats['max'], 2)}]</span>"
            f"</td>"
        )

    comparison_rows = []
    labels = {
        "slow_hf_log": ("Rácio banda lenta / HF", "log₁₀"),
        "peak_freq_hz": ("Frequência do pico", "Hz"),
        "spectral_concentration": ("Concentração espectral", "fração"),
        "RMSSD": ("RMSSD", "ms"),
        "mean_HR": ("Frequência cardíaca", "bpm"),
        "SDNN": ("SDNN", "ms"),
        "pNN50": ("pNN50", "%"),
    }
    for key, (label, unit) in labels.items():
        stats = comparison[key]
        comparison_rows.append(
            f"<tr><td>{label}</td><td class='mono dim'>{unit}</td>"
            f"{range_cell(stats['repouso'])}{range_cell(stats['canto'])}"
            f"<td class='mono dim'>{stats['repouso']['n']} / {stats['canto']['n']}</td></tr>"
        )

    warnings_html = "".join(f"<li>{w}</li>" for w in bundle["warnings"])

    sep_note = (
        f"""<div class="note good"><b>As duas condições não se sobrepõem.</b>
    Todas as janelas de canto têm um rácio banda-lenta/HF superior
    ({fmt(separation['chant_min'], 2)} log₁₀) ao maior valor observado em
    repouso ({fmt(separation['rest_max'], 2)} log₁₀). Com
    {separation['n_rest']} gravações de repouso e {separation['n_chant']} de
    canto, dizer que os intervalos não se cruzam é mais informativo do que
    qualquer teste — e é tudo o que esta dimensão amostral suporta.</div>"""
        if separation["separated"]
        else """<div class="note"><b>Os intervalos sobrepõem-se.</b> O rácio
    banda-lenta/HF não separa as duas condições nesta amostra.</div>"""
    )

    data_json = json.dumps(bundle, ensure_ascii=False, allow_nan=False)

    html = f"""<!doctype html>
<html lang="pt-PT">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Om Shanti · assinatura cardíaca do canto em grupo</title>
<style>{_asset("fonts.css")}</style>
<style>{CSS}</style>
</head>
<body>
<div class="wrap">

<nav aria-label="Secções">
  <div class="brand"><img src="{_asset("logo.txt")}" alt="neroes"></div>
  <ol>{nav_html}</ol>
</nav>

<main>
  <header class="sheet">
    <div>
      <div class="eyebrow accent" style="margin-bottom:8px">Estudo exploratório · ECG / HRV</div>
      <h1 style="font-size:30px;letter-spacing:-0.025em">A assinatura cardíaca do canto de Om Shanti</h1>
    </div>
    <div style="text-align:right">
      <div class="eyebrow">Gerado</div>
      <div class="mono" style="color:{theme.TEXT_2};font-size:12px">{bundle["generated_at"][:16].replace("T", " ")} UTC</div>
    </div>
  </header>

  <!-- ============================ 01 ============================ -->
  <section id="s1">
    {section_head("01", "O resultado")}
    <p class="lead">Durante o canto, a variabilidade da frequência cardíaca destes
    participantes organiza-se quase toda numa única oscilação lenta, perto de
    0,08&nbsp;Hz — cerca de cinco ciclos por minuto. Em repouso essa concentração
    é muito menor. É o efeito mais claro presente nestes dados, e é visível em
    todas as gravações de canto sem exceção.</p>

    <div class="cards">
      {stat_card("Banda lenta / HF · canto", fmt(fold_chant, 1), "×",
                 f"Mediana de {slow_chant['n']} janelas de canto. Há {fmt(fold_chant, 1)}× "
                 f"mais potência em 0,05–0,12 Hz do que em toda a banda HF.")}
      {stat_card("Banda lenta / HF · repouso", fmt(fold_rest, 1), "×",
                 f"Mediana de {slow_rest['n']} gravações de repouso dedicadas. "
                 f"A mesma medida, na mesma coorte.")}
      {stat_card("Frequência cardíaca", fmt(hr_chant['median']), "bpm",
                 f"Contra {fmt(hr_rest['median'])} bpm em repouso. "
                 f"Praticamente inalterada — o efeito não é de ativação.")}
    </div>

    {sep_note}

    <div class="note hard"><b>Três limitações que condicionam tudo o resto.</b>
    <br>· <b>Não é um desenho emparelhado.</b> As gravações de repouso e as de
    canto são de pessoas diferentes, em dias diferentes. Nenhum participante tem
    as duas condições com qualidade utilizável, por isso a comparação é entre
    grupos e não dentro da mesma pessoa.
    <br>· <b>Não há linha de base dentro das gravações de canto.</b> A oscilação
    lenta já está instalada ao minuto 2–4 de cada gravação e mantém-se até ao
    fim (secção 06). Os «últimos 15 minutos» não se distinguem dos 15 anteriores,
    porque ambos parecem ser canto.
    <br>· <b>São três gravações de canto e seis de repouso.</b> Qualquer número
    aqui descreve estas nove gravações e não uma população.</div>
  </section>

  <!-- ============================ 02 ============================ -->
  <section id="s2">
    {section_head("02", "Como foi medido")}
    <p>Bandas de peito Polar H10, intervalos RR nativos a resolução de
    milissegundo. O ECG bruto a 130&nbsp;Hz foi descarregado mas não é usado
    nestes resultados: a série RR do sensor é mais fiável do que a deteção de
    picos sobre um ECG contaminado pelo esforço vocal.</p>

    <p><b>Janela de canto.</b> A única informação disponível sobre o protocolo é
    que o troço final de cada leitura corresponde ao canto. As janelas são por
    isso medidas <i>para trás</i>, a partir do último batimento válido —
    {fmt(bundle["chant_window_min"], 0)} minutos. Nas gravações de repouso usa-se
    a gravação inteira.</p>

    <p><b>Espectro.</b> Welch com janela de Hann de
    {fmt(bundle["spectral"]["window_s"], 0)}&nbsp;s, sobreposição de
    {int(bundle["spectral"]["overlap"] * 100)}&nbsp;%, <i>detrend</i> linear por
    segmento, <span class="mono">nfft</span> {bundle["spectral"]["nfft"]}.
    Os mesmos parâmetros em todas as condições: comparar espectros estimados
    sobre janelas de duração diferente introduz uma diferença sistemática que
    não é fisiologia. A banda VLF não é reportada — exigiria janelas de cinco
    minutos ou mais e não é estimável assim.</p>

    <p><b>A medida principal</b> é um rácio, não uma potência absoluta:
    <span class="mono">log₁₀( P(0,05–0,12&nbsp;Hz) / P(0,15–0,40&nbsp;Hz) )</span>.
    A potência absoluta na banda lenta varia por um fator de dez entre pessoas,
    o que obrigaria a um limiar por participante. O rácio é adimensional e mede
    exatamente o fenómeno: a arritmia sinusal respiratória deixa de estar em
    ~0,25&nbsp;Hz e passa a estar em ~0,1&nbsp;Hz.</p>

    <div class="note"><b>Sobre o LF/HF.</b> Não é apresentado como «balanço
    simpático-vagal» e não deve ser lido assim aqui. Quando a respiração desce
    para ~0,1&nbsp;Hz, a potência da arritmia respiratória desloca-se da banda HF
    para a LF, e o rácio sobe sem qualquer alteração do tónus simpático. Pela
    mesma razão, um aumento de RMSSD durante respiração lenta é em parte
    consequência mecânica do padrão respiratório — inseparável, com estes dados,
    de uma alteração da modulação vagal propriamente dita.</div>
  </section>

  <!-- ============================ 03 ============================ -->
  <section id="s3">
    {section_head("03", "Tacogramas")}
    <p>Intervalo entre batimentos ao longo do tempo. A oscilação lenta e ampla
    nas gravações de canto é visível a olho: ondas de 10 a 15 segundos com
    amplitude de 200 a 400&nbsp;ms.</p>
    {'<div class="note"><b>Séries individuais omitidas.</b> Esta versão foi '
      'gerada em <span class="mono">--publish-mode ' + bundle.get("publish_mode", "aggregate") +
      '</span>, que não publica dados batimento-a-batimento. Os painéis de '
      'tacograma ficam vazios por decisão, não por falta de dados. Use '
      '<span class="mono">--publish-mode full</span> para a versão local.</div>'
      if bundle.get("omitted") else ""}
    <div class="ctrl" id="tacoCtrl">
      <button data-mode="all" aria-pressed="true">Todas</button>
      <button data-mode="canto" aria-pressed="false">Só canto</button>
      <button data-mode="repouso" aria-pressed="false">Só repouso</button>
      <span style="flex:1"></span>
      <button id="rawToggle" aria-pressed="false">Sinal bruto</button>
    </div>
    <div class="chartbed"><div id="taco"></div></div>
    <p style="margin-top:26px">Ampliando 90 segundos do meio de cada janela, a
    onda torna-se evidente. É este o fenómeno que domina o espectro da secção
    seguinte.</p>
    <div class="chartbed"><div id="exc"></div></div>
    <div class="cap">Excerto de 90 s · teal = canto, azul = repouso ·
      mesma escala vertical nas duas condições</div>

    <div class="cap" style="margin-top:22px">Eixo x: minutos desde o início · eixo y: intervalo RR (ms) ·
      suavizado a 10 s para leitura, apenas na figura ·
      eixo y limitado ao intervalo das gravações que passam o critério de
      qualidade · clique na legenda para isolar uma banda</div>
  </section>

  <!-- ============================ 04 ============================ -->
  <section id="s4">
    {section_head("04", "A assinatura respiratória lenta")}
    <p>Densidade espectral de potência do tacograma. Nas gravações de canto o
    espectro colapsa numa risca estreita perto de 0,08&nbsp;Hz. As gravações de
    repouso, medidas com exatamente os mesmos parâmetros, têm o pico mais baixo,
    mais largo e muito menos dominante.</p>
    <div class="ctrl" id="specCtrl">
      <button data-scale="log" aria-pressed="true">Escala log</button>
      <button data-scale="linear" aria-pressed="false">Escala linear</button>
    </div>
    <div class="chartbed"><div id="spec"></div></div>
    <div class="cap">Banda sombreada: 0,05–0,12 Hz, a região da respiração lenta ·
      teal = canto, azul = repouso</div>

    <div class="note"><b>A banda lenta está contida na LF.</b> Os valores de
    <span class="mono">SLOW</span> (0,05–0,12&nbsp;Hz) e de
    <span class="mono">LF</span> (0,04–0,15&nbsp;Hz) medem em larga medida a
    mesma potência e não constituem evidência independente um do outro.</div>
  </section>

  <!-- ============================ 05 ============================ -->
  <section id="s5">
    {section_head("05", "Repouso versus canto")}
    <p>Cada ponto é uma gravação. Mediana e intervalo completo, com o n de cada
    condição — nunca uma média sem dispersão.</p>
    <div class="chartbed"><div id="dots"></div></div>
    <div class="cap">Pontos individuais com jitter horizontal · a barra marca a mediana</div>

    <div class="scroll"><table>
      <thead><tr><th>Medida</th><th>Unidade</th>
        <th>Repouso · mediana [min, máx]</th>
        <th>Canto · mediana [min, máx]</th><th>n rep / canto</th></tr></thead>
      <tbody>{"".join(comparison_rows)}</tbody>
    </table></div>

    <p>A leitura honesta: <b>o que muda é a forma do espectro, não a quantidade
    de variabilidade.</b> O RMSSD e a frequência cardíaca são praticamente
    iguais nas duas condições. O que distingue o canto é a organização da
    variabilidade numa única oscilação lenta.</p>
  </section>

  <!-- ============================ 06 ============================ -->
  <section id="s6">
    {section_head("06", "Ao longo da sessão")}
    <p>O rácio banda-lenta/HF em janela deslizante de 120&nbsp;s, passo de
    10&nbsp;s, ao longo de cada gravação de canto. É este painel que torna
    visível a assunção que a segmentação não consegue testar.</p>
    <div class="chartbed"><div id="slide"></div></div>
    <div class="cap">Cada linha tracejada marca, para a gravação da mesma cor,
      o instante em que começam os últimos 15 minutos</div>

    <div class="note hard"><b>A oscilação lenta já lá está muito antes dos
    últimos 15 minutos.</b> Em todas as gravações longas o rácio sobe nos
    primeiros 2 a 4 minutos e mantém-se estável até ao fim. Não há degrau na
    fronteira dos 15 minutos. A explicação mais simples é que estas gravações
    captam canto (ou respiração lenta pausada) durante quase toda a sua
    duração — e portanto <b>não contêm uma linha de base sem canto</b>. É por
    isso que as gravações dedicadas de repouso são a única comparação possível.</div>
  </section>

  <!-- ============================ 07 ============================ -->
  <section id="s7">
    {section_head("07", "Métricas de contexto")}
    <p>Apresentadas sem interpretação forte, para referência e comparação
    externa. Uma linha por gravação.</p>
    <div class="scroll"><table>
      <thead><tr><th>Banda</th><th>Condição</th><th>Lenta/HF log₁₀</th>
        <th>Pico Hz</th><th>Concentr.</th><th>RMSSD ms</th>
        <th>FC bpm</th><th>SDNN ms</th><th>pNN50 %</th></tr></thead>
      <tbody>{"".join(cohort_rows)}</tbody>
    </table></div>
  </section>

  <!-- ============================ 08 ============================ -->
  <section id="s8">
    {section_head("08", "Qualidade e cobertura")}
    <p>O problema dominante nestes dados não é ruído — é <b>truncagem</b>. As
    séries RR não têm buracos, mas várias terminam muito antes do fim da sessão
    que declaram. Quando isso acontece, a janela dos últimos 15 minutos da
    sessão não tem sinal nenhum.</p>
    <div class="scroll"><table>
      <thead><tr><th>Banda</th><th>Data</th><th>Medição</th><th>Condição</th>
        <th>Declarada min</th><th>RR até min</th><th>Batimentos</th>
        <th>Corrigidos %</th><th>Cobertura</th></tr></thead>
      <tbody>{"".join(quality_rows)}</tbody>
    </table></div>

    <p class="dim" style="font-size:13.5px">Gravações excluídas da análise, com a
    razão:</p>
    <ul class="dim" style="font-size:13.5px;max-width:74ch">{warnings_html}</ul>
  </section>

  <!-- ============================ 09 ============================ -->
  <section id="s9">
    {section_head("09", "Apêndice")}
    <p><b>Recorte usado nesta corrida.</b> <span class="mono">{bundle["phase_summary"]}</span></p>
    <p><b>Hash da configuração.</b> <span class="mono">{bundle["config_sha256"][:32]}…</span><br>
    Qualquer versão anterior deste relatório pode ser ligada ao recorte exato que
    a produziu através deste valor.</p>
    <p><b>Bandas espectrais.</b>
    {" · ".join(f"{k} {v[0]}–{v[1]} Hz" for k, v in bundle["spectral"]["bands"].items())}</p>

    <div class="quote">
      <span class="dot"></span>
      <p>Medir bem é mais difícil do que medir muito.</p>
    </div>

    <p class="dim" style="font-size:13px">Pseudónimos de banda apenas. Nenhum nome
    de participante aparece nos dados, nos ficheiros ou nesta página. Os
    intervalos RR individuais não são publicados neste relatório.</p>
  </section>

  <footer>
    <div class="eyebrow">neroes · Lisboa</div>
    <p>Não é um dispositivo médico; não diagnostica nem trata qualquer condição.
    Estes valores descrevem nove gravações de curta duração num contexto não
    controlado, e constituem uma observação exploratória e não uma avaliação
    clínica. O desenho não é emparelhado e a dimensão amostral não permite
    inferência sobre qualquer população.</p>
  </footer>
</main>
</div>

<script>{_asset("plotly.min.js")}</script>
<script id="bundle" type="application/json">{data_json}</script>
<script>
const DATA = JSON.parse(document.getElementById('bundle').textContent);
const T = {json.dumps({
    "ink900": theme.INK_900, "text1": theme.TEXT_1, "text2": theme.TEXT_2,
    "text3": theme.TEXT_3, "rest": theme.ROLE_REST, "chant": theme.ROLE_CHANT,
    "ramp": theme.BAND_RAMP, "border": theme.BORDER_1,
})};
const LAYOUT = {json.dumps(theme.plotly_layout())};
const CFG = {{displayModeBar:false, responsive:true}};

/* A publish mode may strip beat-level series. Panels that need them must say
   so, not throw and take every later panel down with them. */
function hasSeries(o, key) {{
  return o && Array.isArray(o[key]) && o[key].length > 0;
}}
function omitted(id, what) {{
  document.getElementById(id).innerHTML =
    '<div style="padding:38px 18px;text-align:center;font-family:' +
    "'IBM Plex Mono',monospace" + ';font-size:11px;letter-spacing:.14em;' +
    'text-transform:uppercase;color:{theme.TEXT_3}">' + what + '</div>';
}}

function baseLayout(extra) {{
  return Object.assign(JSON.parse(JSON.stringify(LAYOUT)), extra || {{}});
}}

/* ---------------- 03 tacogramas ---------------- */
let tacoMode = 'all', tacoRaw = false;
function drawTaco(mode) {{
  tacoMode = mode;
  if (!DATA.recordings.some(r => hasSeries(r.tacogram, 'rr_ms'))) {{
    omitted('taco', 'séries individuais omitidas nesta versão');
    return;
  }}
  const traces = DATA.recordings
    .filter(r => mode === 'all' || r.kind === mode)
    .map((r, i) => ({{
      x: tacoRaw ? r.tacogram.t_raw_min : r.tacogram.t_min,
      y: tacoRaw ? r.tacogram.rr_raw_ms : r.tacogram.rr_ms,
      name: r.band_id + ' · ' + r.kind,
      type: 'scattergl', mode: 'lines',
      line: {{width: tacoRaw ? 0.7 : 1.4, color: r.kind === 'canto' ? T.chant : T.rest}},
      opacity: tacoRaw ? 0.5 : 0.85, hovertemplate: '%{{y:.0f}} ms · %{{x:.1f}} min<extra>' + r.key + '</extra>'
    }}));
  Plotly.react('taco', traces, baseLayout({{
    height: 380,
    xaxis: Object.assign({{}}, LAYOUT.xaxis, {{title: {{text:'MINUTOS'}}}}),
    yaxis: Object.assign({{}}, LAYOUT.yaxis,
      {{title: {{text:'RR (ms)'}}, range: DATA.taco_range_ms}})
  }}), CFG);
}}
drawTaco('all');
document.querySelectorAll('#tacoCtrl button').forEach(b => b.onclick = () => {{
  document.querySelectorAll('#tacoCtrl button').forEach(x =>
    x.setAttribute('aria-pressed', String(x === b)));
  drawTaco(b.dataset.mode);
}});
document.getElementById('rawToggle').onclick = function () {{
  tacoRaw = !tacoRaw;
  this.setAttribute('aria-pressed', String(tacoRaw));
  this.textContent = tacoRaw ? 'Suavizado' : 'Sinal bruto';
  drawTaco(tacoMode);
}};

/* ---------------- 03b excerto ampliado ---------------- */
(function () {{
  const pick = k => DATA.recordings.filter(r => r.kind === k && r.in_aggregates
    && hasSeries(r.excerpt, 't_s') && r.excerpt.t_s.length > 20);
  const chosen = [pick('canto')[0], pick('repouso')[0]].filter(Boolean);
  if (!chosen.length) {{ omitted('exc', 'séries individuais omitidas nesta versão'); return; }}
  const traces = chosen.map(r => ({{
    x: r.excerpt.t_s, y: r.excerpt.rr_ms,
    name: r.band_id + ' · ' + r.kind, type: 'scatter', mode: 'lines',
    line: {{width: 2, color: r.kind === 'canto' ? T.chant : T.rest, shape: 'spline'}},
    hovertemplate: '%{{y:.0f}} ms · %{{x:.0f}} s<extra>' + r.band_id + '</extra>'
  }}));
  Plotly.newPlot('exc', traces, baseLayout({{
    height: 300,
    xaxis: Object.assign({{}}, LAYOUT.xaxis, {{title:{{text:'SEGUNDOS'}}, range:[0,90]}}),
    yaxis: Object.assign({{}}, LAYOUT.yaxis, {{title:{{text:'RR (ms)'}}}})
  }}), CFG);
}})();

/* ---------------- 04 espectros ---------------- */
function drawSpec(scale) {{
  const withSpectra = DATA.recordings.filter(r => hasSeries(r.spectrum, 'psd'));
  if (!withSpectra.length) {{ omitted('spec', 'espectros indisponíveis'); return; }}
  const traces = withSpectra.map(r => ({{
    x: r.spectrum.freq_hz, y: r.spectrum.psd, name: r.band_id + ' · ' + r.kind,
    type: 'scatter', mode: 'lines',
    line: {{width: 1.6, color: r.kind === 'canto' ? T.chant : T.rest}},
    opacity: r.kind === 'canto' ? 0.95 : 0.55,
    hovertemplate: '%{{x:.3f}} Hz · %{{y:.0f}} ms²/Hz<extra>' + r.key + '</extra>'
  }}));
  Plotly.react('spec', traces, baseLayout({{
    height: 380,
    xaxis: Object.assign({{}}, LAYOUT.xaxis, {{title:{{text:'FREQUÊNCIA (Hz)'}}, range:[0.02,0.45]}}),
    yaxis: Object.assign({{}}, LAYOUT.yaxis, {{title:{{text:'PSD (ms²/Hz)'}}, type: scale}}),
    shapes: [{{type:'rect', xref:'x', yref:'paper', x0:0.05, x1:0.12, y0:0, y1:1,
      fillcolor:'rgba(67,190,195,0.07)', line:{{width:0}}, layer:'below'}}]
  }}), CFG);
}}
drawSpec('log');
document.querySelectorAll('#specCtrl button').forEach(b => b.onclick = () => {{
  document.querySelectorAll('#specCtrl button').forEach(x =>
    x.setAttribute('aria-pressed', String(x === b)));
  drawSpec(b.dataset.scale);
}});

/* ---------------- 05 pontos individuais ---------------- */
(function () {{
  const groups = [['repouso', T.rest], ['canto', T.chant]];
  const traces = [];
  groups.forEach(([kind, colour], gi) => {{
    const rows = DATA.recordings.filter(r => r.kind === kind && r.slow_hf_log !== null);
    traces.push({{
      x: rows.map((_, i) => gi + (i - (rows.length - 1) / 2) * 0.055),
      y: rows.map(r => r.slow_hf_log),
      text: rows.map(r => r.band_id), type: 'scatter', mode: 'markers+text',
      textposition: 'middle right',
      textfont: {{family: 'IBM Plex Mono, monospace', size: 9, color: T.text3}},
      marker: {{size: 13, color: colour, line: {{width: 1, color: T.ink900}}}},
      name: kind, hovertemplate: '%{{text}} · %{{y:.2f}} log₁₀<extra></extra>'
    }});
    const vals = rows.map(r => r.slow_hf_log).sort((a, b) => a - b);
    const med = vals.length % 2 ? vals[(vals.length - 1) / 2]
      : (vals[vals.length / 2 - 1] + vals[vals.length / 2]) / 2;
    traces.push({{
      x: [gi - 0.2, gi + 0.2], y: [med, med], type: 'scatter', mode: 'lines',
      line: {{color: colour, width: 2.5}}, showlegend: false, hoverinfo: 'skip'
    }});
  }});
  Plotly.newPlot('dots', traces, baseLayout({{
    height: 340, showlegend: false,
    xaxis: Object.assign({{}}, LAYOUT.xaxis, {{tickvals:[0,1],
      ticktext:['REPOUSO','CANTO'], range:[-0.5,1.5], gridcolor:'rgba(0,0,0,0)'}}),
    yaxis: Object.assign({{}}, LAYOUT.yaxis, {{title:{{text:'LOG₁₀ ( LENTA / HF )'}}}})
  }}), CFG);
}})();

/* ---------------- 06 janela deslizante ---------------- */
(function () {{
  const chant = DATA.recordings.filter(
    r => r.kind === 'canto' && hasSeries(r.sliding, 'slow_hf'));
  if (!chant.length) {{ omitted('slide', 'série deslizante indisponível'); return; }}
  const traces = [];
  chant.forEach((r, i) => {{
    traces.push({{
      x: r.sliding.t_min, y: r.sliding.slow_hf, name: r.band_id,
      type: 'scatter', mode: 'lines',
      line: {{width: 1.8, color: T.ramp[i % T.ramp.length]}},
      connectgaps: false,
      hovertemplate: '%{{x:.1f}} min · %{{y:.2f}} log₁₀<extra>' + r.band_id + '</extra>'
    }});
  }});
  const shapes = chant.map((r, i) => ({{
    type: 'line', xref: 'x', yref: 'paper',
    x0: r.rr_min - DATA.chant_window_min, x1: r.rr_min - DATA.chant_window_min,
    y0: 0, y1: 1,
    line: {{color: T.ramp[i % T.ramp.length], width: 1, dash: 'dash'}}
  }}));
  Plotly.newPlot('slide', traces, baseLayout({{
    height: 360, shapes: shapes,
    xaxis: Object.assign({{}}, LAYOUT.xaxis, {{title:{{text:'MINUTOS DESDE O INÍCIO'}}}}),
    yaxis: Object.assign({{}}, LAYOUT.yaxis, {{title:{{text:'LOG₁₀ ( LENTA / HF )'}}}})
  }}), CFG);
}})();
</script>
</body>
</html>"""

    prose = html.split('<script>', 1)[0]
    problems = check_prose(prose)
    if problems:
        raise ValueError(
            "termos proibidos no relatorio gerado (PLAN.md 4.2/4.5): "
            + ", ".join(problems)
        )

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(html, encoding="utf-8")
    return out_path
