"""A página da coorte: o que se moveu com o canto, nas três gravações.

Feita na linha do relatório de coorte do Mantra_EEG. A regra de composição é a
mesma: cada gráfico mostra uma coisa, cada número traz consigo quantas
gravações o sustentam, e o resultado principal pode muito bem ser **"ainda não
sabemos"** — a página tem de conseguir dizer isso sem parecer um fracasso.

O gráfico central não é uma média com barra de erro. É **um ponto por
gravação** sobre a mediana: quem está a ver percebe ao mesmo tempo o sentido e
a dispersão, e percebe sozinho porque é que três gravações não chegam para
afirmar nada. Uma barra sozinha esconderia exatamente isso.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np

from polarmed.report import theme
from polarmed.report.build import sanitise
from polarmed.report.site import CSS, _asset, check_prose, fmt, section_head


def _headline(markers: list[dict], n: int) -> tuple[str, str]:
    """A frase de topo, construída a partir do que os dados sustentam."""
    unanimous = [m for m in markers if m["unanimous"] and m["n"] == n]
    if not unanimous:
        return (
            "Ainda não sabemos",
            f"Em {n} gravações, nenhuma das medidas se moveu sempre no mesmo "
            f"sentido. Não é um resultado nulo — é um conjunto de dados pequeno "
            f"demais para distinguir um efeito real da variação normal de quem "
            f"está sentado e quieto durante meia hora.",
        )
    labels = [m["label"].lower() for m in unanimous]
    if len(labels) == 1:
        names, verb = labels[0], "moveu-se"
    else:
        names = ", ".join(labels[:-1]) + f" e {labels[-1]}"
        verb = "moveram-se"
    return (
        "O que se repetiu nas três",
        f"Em {n} gravações, {names} {verb} sempre no mesmo sentido do minuto "
        f"13 em diante. Com três gravações, a unanimidade não consegue produzir "
        f"um p abaixo de 0,25 — é o mínimo aritmeticamente atingível — por isso "
        f"isto é uma observação consistente, não uma demonstração. Continua a "
        f"faltar um braço de comparação em silêncio para separar o canto do "
        f"simples descanso.",
    )


def render(bundle: dict[str, Any], out_path: Path) -> Path:
    bundle = sanitise(bundle)
    recordings = bundle["recordings"]
    markers = bundle["markers"]
    protocol = bundle["protocol"]
    n = len(recordings)

    title, lede = _headline(markers, n)

    hr = next(m for m in markers if m["key"] == "hr")
    slow = next(m for m in markers if m["key"] == "slow_hf")
    rmssd = next(m for m in markers if m["key"] == "rmssd")

    def card(marker: dict, digits: int, suffix: str = "") -> str:
        arrow = "▲" if marker["median_delta"] > 0 else "▼"
        colour = theme.TEAL_BRIGHT if marker["unanimous"] else theme.TEXT_2
        return f"""<div class="card">
  <span class="lbl">{marker['label']}</span>
  <div><span class="val" style="color:{colour}">{arrow} {fmt(abs(marker['median_delta']), digits)}</span>
       <span class="unit">{marker['unit']}{suffix}</span></div>
  <div class="foot">{marker['n_up']} de {marker['n']} gravações subiram ·
    mediana entre gravações, com o intervalo a vir da reamostragem das
    gravações e não das janelas</div>
</div>"""

    # ---- tabela de marcadores ----
    rows = []
    for m in markers:
        ci = (
            f"{fmt(m['ci_low'], 3)} … {fmt(m['ci_high'], 3)}"
            if m["ci_low"] is not None
            else "—"
        )
        pill = (
            '<span class="pill ok">3 de 3</span>'
            if m["unanimous"]
            else f'<span class="pill warn">{m["n_up"]} de {m["n"]}</span>'
        )
        rows.append(
            f"<tr><td>{m['label']}</td><td class='mono dim'>{m['unit']}</td>"
            f"<td>{fmt(m['median_delta'], 3)}</td><td class='dim'>{ci}</td>"
            f"<td>{pill}</td><td class='mono dim'>{fmt(m['sign_p'], 2)}</td></tr>"
        )

    # ---- detalhe por gravação ----
    detail = []
    for r in recordings:
        cells = "".join(
            f"<td>{fmt(r['values'][m['key']][0], 2)} → "
            f"<b style='color:{theme.TEXT_1}'>{fmt(r['values'][m['key']][1], 2)}</b></td>"
            for m in markers
        )
        detail.append(
            f"<tr><td class='mono'>{r['label']}</td>"
            f"<td class='dim'>{fmt(r['window_min'])} min</td>{cells}</tr>"
        )
    detail_head = "".join(f"<th>{m['label']}</th>" for m in markers)

    # ---- bootstrap por blocos ----
    within_rows = []
    for key in ("slow_hf", "rmssd", "hr"):
        label = next(m["label"] for m in markers if m["key"] == key)
        for row in bundle["within"][key]:
            flag = (
                '<span class="pill ok">exclui zero</span>'
                if row["excludes_zero"]
                else '<span class="pill warn">inclui zero</span>'
            )
            thin = (
                f' <span class="pill bad">n efetivo {fmt(row["n_effective"])}</span>'
                if row["n_effective"] is not None and row["n_effective"] < 5
                else ""
            )
            within_rows.append(
                f"<tr><td>{label}</td><td class='mono'>{row['recording']}</td>"
                f"<td>{fmt(row['value'], 2)}</td>"
                f"<td class='dim'>{fmt(row['ci_low'], 2)} … {fmt(row['ci_high'], 2)}</td>"
                f"<td class='mono dim'>{row['block_len']}</td>"
                f"<td class='mono dim'>{row['n']}</td>"
                f"<td>{flag}{thin}</td></tr>"
            )

    quality_rows = "".join(
        f"<tr><td class='mono'>{r['label']}</td>"
        f"<td>{fmt(r['rr_end_min'])}</td>"
        f"<td>{fmt(r['baseline_range'][0])}–{fmt(r['baseline_range'][1])}</td>"
        f"<td>{fmt(r['chant_range'][0])}–{fmt(r['chant_range'][1])}</td>"
        f"<td>{r['n_beats_baseline']}</td><td>{r['n_beats_chant']}</td>"
        f"<td>{fmt(r['pct_corrected'], 2)}</td></tr>"
        for r in recordings
    )

    # Derivada dos dados, nunca escrita a mao: um identificador cravado na prosa
    # sobrevive a qualquer anonimizacao, porque nao esta em campo nenhum.
    shortest = min(recordings, key=lambda r: r["window_min"])
    others = [r for r in recordings if r is not shortest]
    if others and shortest["window_min"] < min(r["window_min"] for r in others):
        shortest_note = (
            f"A gravação {shortest['label']} tem a série RR a terminar aos "
            f"{fmt(shortest['rr_end_min'])} min, o que encurta a janela de canto "
            f"para {fmt(shortest['window_min'])} minutos e obriga a encurtar a "
            f"baseline na mesma medida. As restantes usam "
            f"{fmt(others[0]['window_min'])} minutos de cada lado."
        )
    else:
        shortest_note = (
            f"As {len(recordings)} gravações usam janelas de "
            f"{fmt(shortest['window_min'])} minutos de cada lado."
        )

    data_json = json.dumps(bundle, ensure_ascii=False, allow_nan=False)

    html = f"""<!doctype html>
<html lang="pt-PT">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Om Shanti · coorte de três gravações</title>
<style>{_asset("fonts.css")}</style>
<style>{CSS}</style>
<style>
.forest-row{{display:grid;grid-template-columns:200px 1fr;gap:14px;
  align-items:center;padding:9px 0;border-bottom:1px solid {theme.DIVIDER}}}
.forest-row .name{{font-size:13.5px;color:{theme.TEXT_2}}}
</style>
</head>
<body>
<div class="wrap">

<nav aria-label="Secções">
  <div class="brand"><img src="{_asset("logo.txt")}" alt="neroes"></div>
  <ol>
    <li><a href="#s1">01 Resultado</a></li>
    <li><a href="#s2">02 O gráfico</a></li>
    <li><a href="#s3">03 Por gravação</a></li>
    <li><a href="#s4">04 Dentro de cada</a></li>
    <li><a href="#s5">05 Traçados</a></li>
    <li><a href="#s6">06 Método</a></li>
    <li><a href="#s7">07 Qualidade</a></li>
  </ol>
</nav>

<main>
  <header class="sheet">
    <div>
      <div class="eyebrow accent" style="margin-bottom:8px">Coorte · 3 gravações · canto a partir do minuto 13</div>
      <h1 style="font-size:30px;letter-spacing:-0.025em">{title}</h1>
    </div>
    <div style="text-align:right">
      <div class="eyebrow">Gerado</div>
      <div class="mono" style="color:{theme.TEXT_2};font-size:12px">{bundle["generated_at"][:16].replace("T", " ")} UTC</div>
    </div>
  </header>

  <section id="s1">
    {section_head("01", "O resultado")}
    <p class="lead">{lede}</p>

    <div class="cards">
      {card(hr, 2, " ")}
      {card(rmssd, 1, " ")}
      {card(slow, 3, " ")}
    </div>

    <div class="note"><b>O que mudou face à leitura anterior.</b> Com o início
    do canto fixado ao minuto 13 pelo registo da sessão, cada gravação passa a
    conter as duas condições, e a comparação passa a ser <b>dentro do mesmo
    participante</b> — não entre pessoas diferentes em dias diferentes. É um
    desenho bastante mais forte, com o mesmo número de gravações.</div>

    <div class="note hard"><b>Os 13 minutos antes do canto não são repouso.</b>
    O domínio da respiração lenta já está alto na baseline das três gravações
    ({fmt(slow['per_recording'][0][1], 2)}, {fmt(slow['per_recording'][1][1], 2)} e
    {fmt(slow['per_recording'][2][1], 2)} em log₁₀, ou seja entre 6 e 39 vezes
    mais potência na banda lenta do que em toda a banda HF). Seja o que for que
    acontece antes do minuto 13 — preparação, meditação em silêncio — já envolve
    respiração lenta. Por isso o contraste aqui mede <b>canto contra
    meditação silenciosa</b>, e não canto contra repouso.</div>
  </section>

  <section id="s2">
    {section_head("02", "Um ponto por gravação")}
    <p>Cada linha é uma medida. Cada ponto é uma gravação: a variação entre a
    janela anterior ao minuto 13 e a janela de canto. A barra vertical marca a
    mediana das três.</p>
    <p class="dim" style="font-size:13.5px">Não há barras de erro aqui de
    propósito. Com três pontos, uma barra esconderia precisamente aquilo que
    interessa ver — quão pouco se sabe.</p>
    <div class="chartbed"><div id="forest"></div></div>
    <div class="cap">Eixo x: variação em desvios da própria baseline, para pôr
      medidas de unidades diferentes no mesmo eixo · linha vertical = sem variação</div>

    <div class="scroll"><table>
      <thead><tr><th>Medida</th><th>Unidade</th><th>Mediana da variação</th>
        <th>IC 95 % (reamostrando gravações)</th><th>Sentido</th><th>p do sinal</th></tr></thead>
      <tbody>{"".join(rows)}</tbody>
    </table></div>

    <div class="note"><b>Sobre o p do teste de sinal.</b> Com três gravações, o
    valor mais pequeno que consegue sair é <b>0,25</b>, mesmo com unanimidade
    perfeita. Não é um resultado fraco — é aritmética. Por isso a coluna existe
    mas não decide nada, e a página nunca a usa para afirmar seja o que for.</div>
  </section>

  <section id="s3">
    {section_head("03", "Cada gravação, cada medida")}
    <p>Valor na janela antes do minuto 13 → valor na janela de canto. As duas
    janelas têm a mesma duração dentro de cada gravação.</p>
    <div class="scroll"><table>
      <thead><tr><th>Gravação</th><th>Janela</th>{detail_head}</tr></thead>
      <tbody>{"".join(detail)}</tbody>
    </table></div>
  </section>

  <section id="s4">
    {section_head("04", "Dentro de cada gravação")}
    <p>O teste de sinal pergunta quantas gravações subiram. Esta tabela pergunta
    outra coisa: <b>dentro de cada pessoa, a diferença aguenta a
    autocorrelação das janelas?</b> As janelas deslizam 10 s com 120 s de
    largura, portanto janelas vizinhas partilham 92 % das amostras — tratá-las
    como independentes daria intervalos várias vezes mais estreitos do que o
    honesto.</p>
    <p>O bootstrap é por blocos, de comprimento estimado da autocorrelação de
    cada série.</p>
    <div class="scroll"><table>
      <thead><tr><th>Medida</th><th>Gravação</th><th>Diferença</th>
        <th>IC 95 %</th><th>Bloco</th><th>Janelas</th><th></th></tr></thead>
      <tbody>{"".join(within_rows)}</tbody>
    </table></div>
    <div class="note"><b>O n efetivo é o número a olhar.</b> É
    <span class="mono">janelas ÷ comprimento do bloco</span>: as amostras
    verdadeiramente independentes. Onde anda por 3 ou 4, o intervalo é
    indicativo e nada mais — e é assinalado.</div>
  </section>

  <section id="s5">
    {section_head("05", "Traçados")}
    <p>Intervalo entre batimentos ao longo de cada gravação. A zona sombreada a
    teal é o canto; a linha marca o minuto 13.</p>
    <div class="ctrl" id="recCtrl"></div>
    <div class="chartbed"><div id="taco"></div></div>
    <div class="cap">Eixo x: minutos desde o início · eixo y: intervalo RR (ms)</div>

    <p style="margin-top:26px">Espectro do tacograma nas duas janelas, com os
    mesmos parâmetros de estimação.</p>
    <div class="chartbed"><div id="spec"></div></div>
    <div class="cap">Banda sombreada: 0,05–0,12 Hz · azul = antes do minuto 13,
      teal = canto</div>
  </section>

  <section id="s6">
    {section_head("06", "Como foi medido")}
    <p><b>Segmentação.</b> O registo da sessão fixa o início do canto ao minuto
    {fmt(protocol['chant_start_min'], 0)}. Descarta-se o primeiro minuto
    (acomodação) e {fmt(protocol['guard_min'], 0)} minuto de guarda a seguir ao
    minuto 13, para a resposta autonómica assentar. As duas janelas recebem a
    mesma duração dentro de cada gravação; quando o canto disponível é mais
    curto do que a baseline possível, encurtam-se as duas.</p>

    <p><b>Unidade de análise: a gravação, não a janela.</b> Cada gravação
    contribui <b>um</b> número para a estatística entre gravações. Juntar as
    janelas de toda a gente num só saco daria intervalos estreitíssimos e
    falsos, porque janelas dentro da mesma pessoa não são independentes.</p>

    <p><b>Espectro.</b> Welch com janela de Hann de
    {fmt(bundle['spectral']['window_s'], 0)} s, sobreposição de
    {int(bundle['spectral']['overlap'] * 100)} %, detrend linear,
    <span class="mono">nfft</span> {bundle['spectral']['nfft']}. Idêntico nas
    duas condições. A VLF não é reportada: exigiria janelas de cinco minutos.</p>

    <p><b>Medida principal.</b>
    <span class="mono">log₁₀( P(0,05–0,12 Hz) / P(0,15–0,40 Hz) )</span> — um
    rácio, não uma potência absoluta, porque a potência na banda lenta varia por
    um fator de dez entre pessoas e obrigaria a um limiar por participante.</p>

    <div class="note"><b>Não há braço de controlo.</b> Sem as mesmas pessoas,
    nos mesmos minutos, em silêncio, qualquer variação encontrada pode ser o
    efeito de estar sentado e quieto durante meia hora. Isto não é uma nota de
    rodapé: é a limitação que governa tudo o que esta página pode afirmar.</div>

    <div class="note"><b>Sobre o LF/HF e o RMSSD.</b> Quando a respiração desce
    para ~0,1 Hz, a potência da arritmia respiratória desloca-se da banda HF
    para a LF, e o LF/HF sobe sem qualquer alteração do tónus simpático. Pela
    mesma razão, uma subida de RMSSD durante respiração lenta é em parte
    consequência mecânica do padrão respiratório — inseparável, com estes dados,
    de uma alteração da modulação vagal propriamente dita.</div>

    <p class="dim" style="font-size:13px">Metodologia estatística transposta do
    projeto Mantra_EEG (<span class="mono">neroes-tech/Mantra_EEG</span>):
    unidade = sessão, teste de sinal exato em primeiro lugar, bootstrap
    estacionário por blocos com comprimento estimado da autocorrelação, delta de
    Cliff como dimensão de efeito.</p>
  </section>

  <section id="s7">
    {section_head("07", "Qualidade e janelas")}
    <div class="scroll"><table>
      <thead><tr><th>Gravação</th><th>RR até (min)</th><th>Baseline (min)</th>
        <th>Canto (min)</th><th>Batim. baseline</th><th>Batim. canto</th>
        <th>Corrigidos %</th></tr></thead>
      <tbody>{quality_rows}</tbody>
    </table></div>
    <p class="dim" style="font-size:13.5px">{shortest_note}</p>

    <div class="quote">
      <span class="dot"></span>
      <p>Três gravações não fazem uma coorte. Fazem três observações bem medidas.</p>
    </div>

    <p><b>Recorte desta corrida.</b>
    <span class="mono">canto = minuto {fmt(protocol['chant_start_min'], 0)} em diante ·
    guarda {fmt(protocol['guard_min'], 0)} min · janelas deslizantes
    {fmt(protocol['sliding_window_s'], 0)} s / {fmt(protocol['sliding_hop_s'], 0)} s</span><br>
    <span class="mono">config {bundle['config_sha256'][:24]}…</span></p>
  </section>

  <footer>
    <div class="eyebrow">neroes · Lisboa</div>
    <p>Não é um dispositivo médico; não diagnostica nem trata qualquer condição.
    Estes valores descrevem três gravações num contexto não controlado e sem
    braço de comparação. Constituem uma observação exploratória e não permitem
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
    "text3": theme.TEXT_3, "base": theme.ROLE_REST, "chant": theme.ROLE_CHANT,
    "ramp": theme.BAND_RAMP, "ember": theme.EMBER, "brass": theme.BRASS_BRIGHT,
})};
const LAYOUT = {json.dumps(theme.plotly_layout())};
const CFG = {{displayModeBar:false, responsive:true}};
const base = e => Object.assign(JSON.parse(JSON.stringify(LAYOUT)), e||{{}});

/* ---------------- 02 forest: um ponto por gravacao ---------------- */
(function () {{
  const traces = [], ticks = [], labels = [];
  DATA.markers.forEach((m, row) => {{
    const y = DATA.markers.length - 1 - row;
    ticks.push(y); labels.push(m.label);
    // padroniza pela dispersao entre gravacoes para por tudo no mesmo eixo
    const deltas = m.per_recording.map(p => p[3]).filter(v => v !== null);
    const scale = Math.max(...deltas.map(Math.abs)) || 1;
    m.per_recording.forEach((p, i) => {{
      if (p[3] === null) return;
      traces.push({{
        x: [p[3] / scale], y: [y + (i - 1) * 0.16], type: 'scatter', mode: 'markers',
        marker: {{size: 12, color: T.ramp[i % T.ramp.length],
                 line: {{width: 1, color: T.ink900}}}},
        showlegend: false, hovertemplate: p[0] + ': ' + p[3].toFixed(3) +
          ' ' + m.unit + '<extra></extra>'
      }});
    }});
    if (m.median_delta !== null) {{
      traces.push({{
        x: [m.median_delta / scale, m.median_delta / scale],
        y: [y - 0.34, y + 0.34], type: 'scatter', mode: 'lines',
        line: {{color: m.unanimous ? T.chant : T.text3, width: 3}},
        showlegend: false, hoverinfo: 'skip'
      }});
    }}
  }});
  Plotly.newPlot('forest', traces, base({{
    height: 60 + DATA.markers.length * 52, showlegend: false,
    // os nomes das medidas sao longos; a margem do template nao lhes chega
    margin: {{l: 220, r: 24, t: 20, b: 52}},
    xaxis: Object.assign({{}}, LAYOUT.xaxis, {{
      title: {{text: 'VARIAÇÃO (normalizada por medida)'}}, range: [-1.35, 1.35],
      zeroline: true, zerolinecolor: T.text3, zerolinewidth: 2}}),
    yaxis: Object.assign({{}}, LAYOUT.yaxis, {{
      tickvals: ticks, ticktext: labels, gridcolor: 'rgba(0,0,0,0)',
      range: [-0.6, DATA.markers.length - 0.4]}})
  }}), CFG);
}})();

/* ---------------- 05 tacogramas + espectros ---------------- */
let current = 0;
function drawRecording(i) {{
  current = i;
  const r = DATA.recordings[i];
  Plotly.react('taco', [{{
    x: r.tacogram.t_min, y: r.tacogram.rr_ms, type: 'scattergl', mode: 'lines',
    line: {{width: 1, color: T.chant}}, showlegend: false,
    hovertemplate: '%{{y:.0f}} ms · %{{x:.1f}} min<extra></extra>'
  }}], base({{
    height: 320,
    shapes: [
      {{type:'rect', xref:'x', yref:'paper', x0:r.chant_range[0], x1:r.chant_range[1],
        y0:0, y1:1, fillcolor:'rgba(67,190,195,0.10)', line:{{width:0}}, layer:'below'}},
      {{type:'rect', xref:'x', yref:'paper', x0:r.baseline_range[0], x1:r.baseline_range[1],
        y0:0, y1:1, fillcolor:'rgba(91,138,212,0.10)', line:{{width:0}}, layer:'below'}},
      {{type:'line', xref:'x', yref:'paper', x0:13, x1:13, y0:0, y1:1,
        line:{{color:T.brass, width:2, dash:'dash'}}}}
    ],
    xaxis: Object.assign({{}}, LAYOUT.xaxis, {{title:{{text:'MINUTOS'}}}}),
    yaxis: Object.assign({{}}, LAYOUT.yaxis, {{title:{{text:'RR (ms)'}}}})
  }}), CFG);

  Plotly.react('spec', [
    {{x: r.spectra.baseline.freq_hz, y: r.spectra.baseline.psd, name: 'antes do min 13',
      type:'scatter', mode:'lines', line:{{width:1.8, color:T.base}}}},
    {{x: r.spectra.canto.freq_hz, y: r.spectra.canto.psd, name: 'canto',
      type:'scatter', mode:'lines', line:{{width:1.8, color:T.chant}}}}
  ], base({{
    height: 320,
    shapes: [{{type:'rect', xref:'x', yref:'paper', x0:0.05, x1:0.12, y0:0, y1:1,
      fillcolor:'rgba(67,190,195,0.07)', line:{{width:0}}, layer:'below'}}],
    xaxis: Object.assign({{}}, LAYOUT.xaxis, {{title:{{text:'FREQUÊNCIA (Hz)'}}, range:[0.02,0.45]}}),
    yaxis: Object.assign({{}}, LAYOUT.yaxis, {{title:{{text:'PSD (ms²/Hz)'}}, type:'log'}})
  }}), CFG);
}}

const ctrl = document.getElementById('recCtrl');
DATA.recordings.forEach((r, i) => {{
  const b = document.createElement('button');
  b.textContent = r.label;
  b.setAttribute('aria-pressed', String(i === 0));
  b.onclick = () => {{
    ctrl.querySelectorAll('button').forEach((x, j) =>
      x.setAttribute('aria-pressed', String(j === i)));
    drawRecording(i);
  }};
  ctrl.appendChild(b);
}});
drawRecording(0);
</script>
</body>
</html>"""

    problems = check_prose(html.split("<script>", 1)[0])
    if problems:
        raise ValueError("termos proibidos: " + ", ".join(problems))

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(html, encoding="utf-8")
    return out_path
