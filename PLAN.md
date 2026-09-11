# PLAN.md — Pipeline ECG/HRV para meditação com mantra (Om Shanti)

**Estado:** aprovado. Este documento é a fonte de verdade do projeto.

**Revisão 2026-09-11 — estrutura do Drive verificada.** O §2 foi reescrito contra o conteúdo real da pasta de exemplo, que divergia da declaração anterior em cinco pontos: há um nível de **data** entre banda e medição (4 níveis, não 3); o formato **não** é Polar Sensor Logger mas `ecg_raw.csv` / `rr_intervals.csv` / `metrics.json`; **não existem ficheiros de acelerómetro**; são **31 bandas**, não 3–20; e o `session_type` está disponível como metadado, o que torna o filtro por nome de pasta um recurso secundário. A ausência de ACC obrigou a substituir por **EDR** o validador de onset (§4.4), a medição de `resp_rate_hz` (§4.2) e a validação do repouso pós-mantra (§4.1b) — em todos os casos com perda de fiabilidade declarada por escrito, não disfarçada.

---

## 1. Contexto

Sessões de meditação em grupo com canto vocalizado de "Om Shanti". Vários participantes com Polar H10; exportação via Polar Sensor Logger (Android) para Google Drive. É preciso um pipeline reprodutível que, dado apenas o caminho de uma pasta, produza métricas, estatística e um relatório HTML autocontido, projetável no próprio dia, sem rede e sem autenticação.

Esta primeira iteração valida o sistema inteiro com dados reais de exemplo e com dados sintéticos realistas. No dia da sessão real, só muda o `--source`.

**Estado do repositório:** vazio, exceto `relatoriotemlpate.zip`, que contém o design system Neroes completo (tokens CSS, readme de marca, logos PNG) e uma folha de relatório de referência. É esse o material do `reference/` de §8.1.

**Ambiente verificado:** Python 3.11.9 em `C:\Users\Usuario\AppData\Local\Programs\Python\Python311\python.exe` (pip 24.0, site-packages limpo). O python do PATH é o 3.14.6 — não é o que usamos: o stack científico (scipy, scikit-learn, NeuroKit2) tem suporte muito mais maduro em 3.11. O venv é criado explicitamente a partir do 3.11.

---

## 2. Fonte de dados

### 2.1 Dados de exemplo — verificados no Drive em 2026-09-11

```
https://drive.google.com/drive/folders/12hCG-_3MniU1CYMf2kPa0Co1MsyXgT0I?usp=sharing
```

Pasta `during_retreat`, com as pastas irmãs `pre_post_retreat` e `preparation_tests`.

> **Esta pasta é uma amostra truncada.** As gravações partilhadas têm dezenas de segundos a poucos minutos (24 s, 74 s, 121 s nas medições `livre_1h` de HM00, HM05 e HM13); as reais são mais longas. A amostra serve para **fixar formatos de ficheiro e estrutura de pastas** e para exercitar os parsers. **Nenhuma conclusão sobre duração, qualidade ou fisiologia é tirada dela**, e nenhum limiar é afinado a partir dela.

A pasta é descarregada localmente para `data/exemplo/`. `GoogleDriveApiSource` (Fase 8) automatiza o passo; até lá o acesso é por pasta local.

### 2.2 Estrutura real — verificada, substitui a declaração anterior

Quatro níveis, não três: há um nível de **data** entre a banda e a medição.

```
during_retreat/
├── HM00/                          # banda — 31 descobertas (HM00…HM34, com falhas)
│   └── 2026-08-08/                # data da sessão
│       ├── livre_1h/              # medição
│       │   ├── ecg_raw.csv
│       │   ├── rr_intervals.csv
│       │   └── metrics.json
│       ├── rest_5min_tarde/
│       └── rest_5min_tarde_2 … _5/
├── HM05/
│   └── 2026-08-03/ … 2026-08-08/  # até 6 datas por banda
└── HM34/
```

- `band_id` deriva da pasta de **1.º nível** (`HM00`, `HM05`, …), normalizada para maiúsculas sem espaços.
- `session_date` deriva da pasta de **2.º nível**, confirmada contra `metrics.json`.
- `measurement_folder` é a pasta de **3.º nível**.
- **São 31 bandas, não 3–20.** Tudo o que itera sobre bandas tem de aguentar esta ordem de grandeza: paleta, legendas, matriz de sincronia (31×31) e o peso do HTML. O orçamento de 6 MB para `index.html` é recalculado em função disto na Fase 7.

### 2.3 Formatos de ficheiro — verificados, não são Polar Sensor Logger

A exportação **não** usa a nomenclatura nem o formato do Polar Sensor Logger. Não há epoch de 2000 em nanossegundos, não há separador `;`, e **não existem ficheiros ACC nem HR**.

**`ecg_raw.csv`** — separador `,`, decimal `.`

```
seq,voltage_uv,timestamp_ms
0,620,0
1,581,7
```

`timestamp_ms` é **relativo ao início da gravação** (começa em 0). Taxa verificada: **130.0 Hz** exatos.

**`rr_intervals.csv`** — separador `,`

```
seq,rr_ms,timestamp_ms
0,783,0
1,824,783
```

`timestamp_ms` é o tempo cumulativo do batimento; `rr_ms` inteiro.

**`metrics.json`** — metadados + HRV pré-calculada pela app

```json
{"metadata":   {"session_id","participant_code","session_date","session_time",
                "session_type","duration_s","has_ecg","ecg_samples","n_rr_raw","exported_at"},
 "hrv_metrics":{"n_rr","mean_rr","hr_resting_mean","hr_min","hr_max",
                "sdnn","rmssd","lnrmssd","pnn50","data_quality_pct","quality_flag"}}
```

Duas regras sobre este ficheiro:

1. **`session_time` é a única fonte de tempo absoluto.** Como os timestamps dos CSV começam em 0, `t0_utc = session_date + session_time`. Sem `metrics.json` não há relógio absoluto: a gravação continua a ser analisada mas **não entra na análise de sincronia**, e isso é registado como aviso, nunca como erro.
2. **As `hrv_metrics` da app são lidas mas nunca usadas como resultado.** Entram em `metrics_recording.csv` com o prefixo `app_` e servem de **verificação cruzada** contra os nossos valores. Divergência de RMSSD acima de `app_metric_tolerance_pct` (default 5 %) é aviso no `quality_report.csv`. O pipeline calcula sempre os seus próprios valores a partir do RR bruto.

O parser do Polar Sensor Logger (`;`, epoch 2000 ns, `ECG_*.txt` / `HR_*.txt` / `RR_*.txt`) **mantém-se implementado** — a app de logging pode mudar até ao dia da sessão, e o sniffer escolhe pelo conteúdo, não pelo nome. Mas o formato acima é o caminho de produção.

### 2.4 Filtro de medições — `session_type` primeiro, nome da pasta em recurso

`metrics.json` traz `"session_type": "free"`, metadado legível por máquina. É mais fiável do que o token no nome da pasta e passa a ser a via primária.

Ordem de decisão, por medição:

1. **`session_type` do `metrics.json`**, comparado com `session_types_included` em config (default `["free"]`). Regista `filter_matched_on = metadata`.
2. **Token no nome da pasta**, quando não há `metrics.json` ou o campo falta. Token em config (`measurement_filter`, default `"livre"`), com normalização NFKD + remoção de diacríticos + `casefold()`, comparação por tokens separados por `_`, `-`, espaço e `.`. `Livre`, `LIVRE` e `sessao_livre_2` correspondem; `livremente` não. Regista `filter_matched_on = folder`.
3. Se nenhuma via resolver, `filter_matched_on = none` e a medição fica `parse_status = unresolved`. Nunca é processada em silêncio.

Se as duas vias **discordarem** (p. ex. pasta `rest_5min_tarde` com `session_type: free`), o pipeline não escolhe: regista a discrepância no `quality_report.csv`, segue o metadado, e imprime a lista completa no `inventory.md`.

`--measurement-filter ""` com `--session-types ""` desativa ambos e processa tudo.

Medições que não passam entram no `inventory.csv` com `parse_status = skipped_by_filter`. **Não são `unresolved`** — essa distinção é o que mantém o inventário legível.

O `inventory.md` imprime sempre, no topo: número de bandas e respetivos IDs; por banda, as datas e medições, com quantas passaram o filtro; e uma **matriz banda × sessão** com o estado de cada célula (ok / em falta / excluída). Banda com zero medições após o filtro é aviso destacado, não silêncio.

### 2.5 Agrupamento em sessões

Com o nível de data explícito, a via primária é **data + clustering temporal dentro da data**, verificada contra os nomes de medição.

- **Via primária:** agrupar por `session_date` (pasta de 2.º nível, confirmada contra `metrics.json`) e, dentro de cada data, fazer clustering de `t0_utc` através de todas as bandas. Intervalo superior a `session_gap_hours` (default 2.0) abre sessão nova. `session_id` = `S1`, `S2`, … por ordem cronológica global.
- **Via de verificação:** agrupamento por nome de pasta de medição. Se discordarem, o pipeline **não escolhe**: emite aviso destacado, imprime as duas atribuições lado a lado e continua com a via temporal. `--session-map` (CSV `band_id,session_date,measurement_folder,session_id`) permite override manual.

---

## 3. Decisões confirmadas

| # | Decisão | Escolha |
|---|---|---|
| A | Entregável | Só site de coorte (§8.2, 12 secções). O template serve de vocabulário visual, não de estrutura. |
| B | Fontes | woff2 embebidas em base64. Vendoring único em `assets/fonts/`, subset latin, injetadas como `data:` URI. Offline garantido, identidade preservada. |
| C | Recorte de fases | `rest` 0–3 · `guard` 3–6 · `mantra` 6→fim · `rest_post` (opcional, §4.1b). Tudo em config, tudo alterável por flag. |
| D | Gráficos | Híbrido. Plotly (bundle parcial, inline) para painéis interativos; SVG à mão, no estilo do template, para sparklines e cartões de sumário. |
| E | Fonte de dados | Pasta local espelhada do Drive (§2), estrutura `banda/data/medição` verificada. Filtro por `session_type` do `metrics.json`, token da pasta em recurso. `band_id` da pasta de 1.º nível. |
| F | Amostra do Drive | Truncada. Serve para fixar formatos e parsers; **não** para afinar limiares nem tirar conclusões (§2.1). |
| G | Segmentação no dia real | **Gravação contínua**, conforme §0: ~3 min de silêncio, transição, canto. Mantêm-se os offsets, a `guard` e a deteção de onset. |
| H | Respiração | **EDR a partir do ECG**, já que não há acelerómetro. Validador de segunda linha, com `resp_confidence` por janela (§4.4). |

---

## 4. Decisões metodológicas e objeções resolvidas

### 4.1 O contraste repouso vs mantra não tem controlo, e a deriva temporal é um confundidor total

Este é o problema mais sério do desenho. O repouso são os minutos 0–3 e o mantra são os minutos 6–30. Qualquer coisa que desça monotonicamente ao longo de meia hora sentado — e a frequência cardíaca desce, por acomodação postural, digestão, simples repouso prolongado — produz exatamente o "efeito" que se procura, sem qualquer contributo do canto.

**Mitigação analítica.** O painel 7 (progressão repouso → início → meio → fim) deixa de ser um painel descritivo e passa a ser o **controlo interpretativo** do painel 5. Se o RMSSD subir de repouso para o início do canto e depois estabilizar durante os 25 min seguintes, o padrão é compatível com um efeito do canto. Se subir de forma aproximadamente linear ao longo de todas as épocas, o padrão é indistinguível de deriva. O pipeline calcula explicitamente `mantra_drift_slope` (declive de RMSSD e de HR ao longo das épocas de mantra), que entra no `metrics_group.csv` e no painel, e o relatório apresenta os dois painéis lado a lado com esta leitura escrita por extenso.

A limitação é escrita **na capa do relatório**, não no fim.

### 4.1b Repouso pós-mantra — observação oportunista, determinada pelos dados

A mitigação de §4.1 diagnostica a deriva mas não a exclui. O que a excluiria era um período de repouso após o canto: se a métrica sobe durante o mantra e **regressa na direção da linha de base** depois, uma deriva monotónica não explica o padrão, porque a deriva não reverte. A reversibilidade é a assinatura de um efeito de estado.

**Restrição real e assumida:** num contexto de festival, com participantes voluntários, **não é possível garantir que as pessoas permaneçam sentadas e em silêncio após o "Om Shanti"**. Não há conformidade a impor, e o plano não a pressupõe.

Mas o desenho não precisa de conformidade — precisa de **observação**. A banda está sobre o tórax e o acelerómetro diz, segundo a segundo, quem ficou parado e quem se levantou. O `rest_post` passa de fase assumida a **facto determinado pelos dados, por gravação**.

**Implementação:**

> **Não há acelerómetro.** A exportação verificada (§2.3) não produz ACC, pelo que a versão anterior deste plano — que determinava o repouso pós-mantra por imobilidade medida — não é implementável. A substituição por EDR recupera parte da capacidade e é **mensuravelmente mais fraca**; o que se perde está escrito abaixo.

- `detect_mantra_end_edr()` estima, por gravação, o instante em que a oscilação respiratória lenta (~0.1 Hz) desaparece da respiração derivada do ECG. O canto de grupo não termina em uníssono, por isso o fim é por pessoa, tal como o início.
- **Proxy de movimento, já que não há ACC:** duas grandezas que o ECG fornece e que sobem com atividade muscular — a potência residual na banda de EMG (40–60 Hz, após limpeza) e a `pct_corrected` por janela. `rest_post_valid` é verdadeiro se ambas permanecerem abaixo dos respetivos limiares de config durante pelo menos `rest_post_min_s` (default 120 s) **contínuos**. Caso contrário `rest_post_valid = False` com `rest_post_invalid_reason` preenchido (`movimento_emg`, `artefacto_rr`, `gravacao_terminou`, `sem_ecg`, `duracao_insuficiente`).
- **Limitação a assumir por escrito:** um proxy de EMG deteta *contração muscular*, não *deslocação*. Alguém que se levante e saia devagar produz menos EMG torácico do que alguém que fique sentado a mexer-se. O proxy é enviesado e não é equivalente ao acelerómetro. Por isso `rest_post` desce um degrau de confiança e o relatório passa a dizer *"sem movimento muscular detetável no ECG"*, nunca *"permaneceu imóvel"*.
- O contraste `mantra_vs_rest_post` corre **apenas sobre as gravações válidas**, com `n_effective` impresso ao lado, pela mesma mecânica já usada nas métricas não-lineares (§4.6). Se 3 de 6 participantes ficarem quietos, são 3 controlos intra-sujeito, e com esta dimensão amostral isso é material.
- Se `n_effective = 0`, o painel é omitido com a razão escrita, e a secção de limitações imprime: *"não foi possível observar repouso pós-mantra em nenhum participante; a deriva temporal é caracterizada mas não excluída."*

**Nudges de protocolo que não dependem de conformidade** (RUNBOOK.md, secção do dia da sessão):

- Não anunciar o fim. Não há palmas nem instrução de encerramento; o facilitador segura o silêncio durante ~3 minutos.
- **As gravações param quando o operador as parar**, não quando o participante decidir. Este é o único ponto verdadeiramente controlável, e é o que garante que existe sinal para analisar em quem ficou.
- Não pedir explicitamente às pessoas que fiquem paradas. Pedir cria pressão social, e uma conformidade coagida introduz o seu próprio artefacto.

**Viés de auto-seleção — a escrever no relatório, não a omitir.** Quem permanece sentado não é uma amostra aleatória da sala. Participantes mais envolvidos, mais calmos ou com mais prática têm maior probabilidade de ficar, e são plausivelmente os mesmos com perfil autonómico distinto. Por isso:

- o contraste `mantra_vs_rest_post` é **sempre marcado como exploratório**, nunca pode ser o `primary_endpoint`, e o código recusa essa configuração;
- o relatório imprime, junto ao painel, quantos participantes tinham janela válida, quantos não tinham e porquê;
- a leitura autorizada é *"nos participantes em que foi possível observar, o padrão reverteu / não reverteu"*, e não *"o efeito é reversível"*.

Isto vale consideravelmente mais do que nada, e é honestamente menos do que um controlo desenhado. As duas frases ficam no relatório.

### 4.2 O aviso do LF/HF aplica-se, em grau menor, ao RMSSD — o marcador primário

O LF/HF colapsa quando a respiração desce para 0.1 Hz. Mas a mesma física afeta o marcador primário. Respirar lenta e profundamente aumenta mecanicamente a amplitude da arritmia sinusal respiratória, e o RMSSD mede em grande parte essa amplitude. Um aumento de RMSSD durante canto lento é, em parte, consequência do padrão respiratório — não uma medida independente de "tónus vagal aumentado".

Isto não invalida o marcador; a via mecanicista proposta (expiração prolongada → aferência vagal) passa precisamente por aqui. Mas a frase "aumento do tónus vagal" afirma mais do que os dados suportam.

**Duas medidas:**

1. **Linguagem.** O relatório usa consistentemente *"aumento da modulação vagal da frequência cardíaca"*. O painel 5 inclui uma nota de uma frase a dizer que o efeito é inseparável da mudança do padrão respiratório que o produz. Uma lista de termos proibidos no `report/theme.py` faz falhar o build se `"tónus vagal"` aparecer no texto gerado.

2. **Medir em vez de apenas caveatear.** Derivamos a respiração do ECG (EDR, §4.4). `resp_rate_hz` e `resp_peak_power` passam a ser **colunas reportadas por época** no `metrics_epoch.csv` e a ser desenhadas por cima do painel 7, não apenas usadas como validador de onset. Isto permite uma dissociação empírica: se a frequência respiratória estabilizar nos primeiros minutos de canto e permanecer constante durante os 25 min seguintes, mas o RMSSD continuar a subir, então a subida tardia **não** é atribuível a mudança respiratória. Se as duas curvas forem paralelas, não se separam, e o relatório di-lo.

Quando não há ECG numa gravação (só RR), as colunas ficam vazias e o painel assinala-o. Quando há ECG mas a qualidade do EDR é baixa — o que o canto torna provável, ver §4.4 — a coluna leva `resp_confidence` e os valores abaixo do limiar não são desenhados.

### 4.3 A janela do Welch tem de ser idêntica nas duas fases

Repouso tem 180 s. Com janelas de 128 s e 50 % de sobreposição, sobra ~1 segmento — sem média, variância enorme. Com 256 s, não cabe de todo. O mantra tem 24 min e daria dezenas de segmentos. Comparar as duas fases com números de segmentos tão diferentes introduz uma diferença sistemática que não tem nada a ver com fisiologia.

**Parâmetros fixos para todas as comparações entre fases e entre épocas:**

| Parâmetro | Valor |
|---|---|
| Janela | Hann, 60 s (`nperseg = 240` a 4 Hz) |
| Sobreposição | 50 % |
| Detrend | linear, por segmento |
| `nfft` | 1024 (zero-padding — ver §4.3b) |
| Segmentos no repouso (180 s) | 5 |
| Resolução espectral real | ~0.0167 Hz |

**Consequências honestas, assumidas:**

- A **VLF sai do relatório**. 0.003–0.04 Hz exigiria janelas de ≥ 5 min e não é estimável aqui.
- O limite inferior da LF a 0.04 Hz fica **marginal** (2–3 bins) e leva flag de fiabilidade em todas as linhas.
- Uma segunda passagem com janelas longas (256 s) corre **só na fase de mantra**, para as métricas que a toleram, gravada em ficheiro separado `metrics_mantra_longwindow.csv` e claramente identificada como **não comparável com o repouso**. Nunca entra nos contrastes.

Cada linha de métrica espectral leva `welch_window_s`, `n_welch_segments` e `nfft`. Sem isso não se sabe o que se está a comparar.

### 4.3b Resolução de leitura da frequência de pico

`peak_freq_hz` é a leitura central do painel 9 — a transição de ~0.25 Hz para ~0.10 Hz é o fenómeno visual principal. Mas com bins de 0.0167 Hz, 0.100 Hz e 0.117 Hz são **bins adjacentes**, e a curva sai em escada.

**Solução:** `nfft = 1024` (zero-padding de 240 → 1024 amostras) dá uma grelha de leitura de 0.0039 Hz, seguida de **interpolação parabólica** sobre os três bins em torno do máximo para estimativa sub-bin.

**Nota metodológica que fica no docstring e no relatório:** o zero-padding melhora a *granularidade de leitura* do pico, não a *resolução espectral real*, que continua determinada pela janela de 60 s. Dois picos genuinamente separados por menos de ~0.025 Hz continuam a não ser resolúveis. Isto é aceitável porque o que se quer aqui é localizar **um** pico com precisão, não separar dois.

### 4.4 Deteção de onset — estatística de rácio, com o ACC como segundo validador

O método (espectrograma da série RR + ponto de mudança) é a via principal, com duas alterações e um validador.

**Alteração 1 — a estatística de deteção é um rácio, não uma potência absoluta.** A potência absoluta em 0.05–0.12 Hz varia por um fator de dez entre pessoas, o que obriga a um limiar por sujeito e é frágil.

```
S(t) = log10( P(0.05–0.12 Hz) / P(0.15–0.40 Hz) )
```

Adimensional, auto-normaliza contra a amplitude global da HRV, e mede exatamente o fenómeno: a RSA deixa de estar em 0.25 Hz e passa a estar em 0.1 Hz. Deteção por CUSUM sobre `S(t)`, com linha de base na mediana dos primeiros 2 min.

**Alteração 2 — reportar também a frequência de pico.** `peak_freq_hz` por janela é a leitura mais direta e é o que se mostra no painel 9.

**Validador adicional: EDR — respiração derivada do ECG.** A versão anterior deste plano preferia o acelerómetro e argumentava contra o EDR. O argumento continua correto; o acelerómetro é que não existe (§2.3). Passa a EDR, com o custo declarado:

- **O que se mantém:** o EDR é independente da via RR, que é a propriedade que interessa num validador. Deriva de `ecg_raw.csv` por modulação de amplitude da onda R (e, como segunda via, pela modulação da área do complexo QRS, menos sensível a deriva de linha de base).
- **O custo, reconhecido:** o canto vocalizado gera artefacto de EMG que contamina precisamente a amplitude da onda R — o portador do sinal. O EDR é portanto **menos fiável exatamente na fase em que mais interessa**. Isto não se contorna com este hardware; mitiga-se e mede-se.
- **Mitigação:** filtro passa-banda de 0.04–0.5 Hz sobre a série de amplitudes antes da estimação; `resp_confidence` por janela, definida como a concentração espectral no pico dominante (fração da potência 0.04–0.5 Hz contida em ±0.02 Hz do pico). Janelas com `resp_confidence` abaixo do limiar de config são descartadas e contadas, não interpoladas.
- **Consequência assumida:** o EDR é **validador de segunda linha**, não par do detetor por RR. Se as duas vias discordarem, prevalece a via RR e a discrepância é reportada. Nunca se usa o EDR sozinho para justificar um recorte.

`detect_mantra_onset_rr()` é a via oficial; `detect_respiration_edr()` corre quando há `ecg_raw.csv` e entra no `quality_report.csv` como segunda coluna de onset, sempre acompanhada de `resp_confidence`.

**Nenhum destes altera a segmentação automaticamente.** Emitem aviso e sugerem o valor de `--mantra-start`. A decisão é do operador.

### 4.5 Com n = 5–6 participantes, nem o p-value nem o bootstrap funcionam

**Aritmética, não opinião.** No Wilcoxon signed-rank bilateral, o p mínimo atingível é **0.063 para n = 5** e **0.031 para n = 6**. Com 5 participantes, nenhum resultado — por mais perfeito que seja — pode ser "significativo".

**E o bootstrap também não.** Um IC 95 % por bootstrap sobre a mediana de 5 valores é enganador: a distribuição de reamostragem assume pouquíssimos valores distintos, e o intervalo resultante dá uma falsa impressão de suavidade e de precisão.

**Substituição:** intervalo de confiança **exato e livre de distribuição** para a mediana, por estatísticas de ordem. Para n = 5 isso corresponde essencialmente a `[mín, máx]` com cobertura ≈ 94 %, e é isso que se reporta, **com a cobertura real impressa ao lado** (nunca arredondada para "95 %"). Para n ≥ 8 o bootstrap volta a ser aceitável e o código escolhe automaticamente, registando qual usou na coluna `ci_method`.

**Ordem de apresentação no relatório**, imposta pelo código:

1. o delta individual de cada participante;
2. quantos se movem em cada direção (`n_up` / `n_down`);
3. a mediana do delta com IC exato e cobertura real;
4. o tamanho de efeito.

O p-value vai para o apêndice, com `p_min_attainable` impresso ao lado. **A palavra "significativo" não aparece no site** — está na lista de termos proibidos e faz falhar o build. A função de formatação recusa-se a emitir `"p <"` sem `n` e sem `p_min_attainable`.

**Independência:** 3 sessões × 6 pessoas não são 18 observações independentes. Os agregados são sempre calculados primeiro **dentro** do participante (mediana através das sessões) e só depois **através** de participantes.

### 4.6 Métricas não-lineares não são fiáveis em 180 s

O repouso tem 180 s, o que a ~60 bpm dá ~180 batimentos. DFA α1 e SampEn precisam de mais do que isso para serem estáveis.

**Limiares explícitos em config:**

| Métrica | Mínimo de batimentos | Abaixo disso |
|---|---|---|
| SampEn | 250 | `reliability = insufficient`, valor não calculado |
| DFA α1 | 300 | `reliability = insufficient`, valor não calculado |
| Métricas espectrais | 2 segmentos de Welch | `reliability = limited` |
| Domínio do tempo | 60 batimentos | `reliability = limited` |

Um segmento com `reliability = insufficient` para uma métrica é **automaticamente excluído do contraste** dessa métrica, e o relatório imprime o `n` efetivo por métrica, que pode ser diferente do `n` global. Na prática isto significa que, com o recorte atual, **não haverá contraste repouso-vs-mantra para SampEn nem para DFA α1**. Isso fica escrito, e não se disfarça com um valor calculado sobre dados insuficientes.

### 4.7 Endpoint primário declarado antes de ver os dados

Com 5–6 participantes, ~25 métricas, 3 contrastes e 4 níveis de época, o número de comparações possíveis é da ordem das centenas. Sem um resultado principal declarado à partida, qualquer achado é indistinguível de uma pesca.

**Campo obrigatório em `config/default.yaml`:**

```yaml
primary_endpoint:
  metric: RMSSD
  contrast: rest_vs_mantra
  direction: increase        # hipótese direcional declarada
  declared_on: "YYYY-MM-DD"  # antes de qualquer corrida com dados reais
```

O `run_manifest.json` regista este bloco e o hash da config. O relatório:

- apresenta o endpoint primário numa secção própria, **em primeiro lugar**, com o rótulo "resultado primário, declarado antes da análise";
- marca **todos** os restantes resultados com "exploratório" de forma visível e não removível;
- imprime `declared_on` ao lado, para que se veja que foi fixado antes.

O pipeline **recusa correr sem `primary_endpoint` preenchido**. Não há default silencioso.

### 4.8 SLOW e LF não são evidências independentes

A banda lenta (0.05–0.12 Hz) está quase inteiramente contida na LF (0.04–0.15 Hz). `SLOW_abs` e `LF_abs` são, em larga medida, a mesma medida com nomes diferentes.

Ambas são reportadas — a SLOW é a mais interpretável para este protocolo, a LF é a convenção da literatura e permite comparação externa — mas o relatório imprime, no painel que as mostra: *"a banda lenta está contida na LF; os dois valores não constituem evidência independente."* Um teste verifica que a nota está presente sempre que ambas as colunas aparecem na mesma figura.

### 4.9 A paleta da marca não é distinguível por daltónicos com 6–20 bandas

O triádico da marca é teal / verde / azul — todos frios, e teal vs verde é precisamente o par que a deuteranopia colapsa. Com uma cor por banda e até 20 bandas, é impossível. Mas o requisito e a identidade não estão em conflito, porque as bandas individuais **não têm significado semântico** — são só "muitas linhas".

**Separar os dois usos da cor:**

- **Papéis semânticos** (poucos, fixos, com significado) usam a paleta da marca: `rest` = azul `#5B8AD4`, `mantra` = teal `#43BEC3`, `rest_post` = azul mais claro, `guard` = cinza hachurado, excluído = ember `#C4685A`, média do grupo = teal com glow, banda de dispersão = teal a 16 %.
- **Identidade de banda** (muitas, sem significado) usa uma rampa sequencial ordenada por luminância dentro da família petrol→teal→brass, com opacidade baixa. A distinção entre linhas individuais faz-se por **hover e toggle de legenda**, não por cor.

Contraste de todos os papéis semânticos verificado contra `--ink-900` com rácio mínimo 4.5:1, e simulação de deuteranopia/protanopia no teste de tema.

### 4.10 Ordem de execução: o gerador sintético vem antes dos parsers

Não é possível escrever nem testar um parser sem um ficheiro para parsear. O gerador nasce **mínimo na Fase 2** (ficheiros com formato correto, conteúdo trivial, estrutura de pastas `HM*/…livre…/` idêntica à real) e cresce com o pipeline. A **Fase 5** endurece-o para fidelidade fisiológica completa, `ground_truth.csv` e os 10 casos-limite, e é aí que fica o critério de aceitação. O site é construído depois de tudo isto.

### 4.11 Alinhamento — `--align` default `recording_start`

`group_start` parece mais correto — as fases são um facto do grupo, não de cada ficheiro — mas tem um modo de falha assimétrico e destrutivo: se o t0 do grupo for o arranque mais tardio e uma pessoa carregar em gravar 6 minutos depois das outras, o offset de todos desloca-se 6 minutos e o repouso de toda a gente é destruído por uma única banda. `recording_start` degrada localmente: só a banda que se enganou fica mal segmentada, e o validador de onset apanha-a. O desvio face ao grupo é **sempre** calculado e reportado.

**Ponto de arquitetura:** o alinhamento para **fases** e o alinhamento para **sincronia** são problemas separados. O painel de sincronia interpessoal usa sempre o relógio absoluto, independentemente de `--align` — comparar séries de pessoas diferentes exige um eixo temporal comum. `--align` governa apenas a origem dos offsets de fase.

`group_start` fica implementado e disponível para quando o `inventory.md` mostrar que os arranques estão apertados.

### 4.12 Banda ≠ pessoa — `participants.csv` opcional

`band_id, session_id, participant_id`, com `session_id` vazio a significar "aplica-se a todas as sessões". Na ausência do ficheiro, `participant_id = band_id` e o dashboard imprime, no cabeçalho e no painel de qualidade: *"sem mapeamento participante↔banda; assume-se uma pessoa por banda"*. As spaghetti lines dos painéis 5, 6 e 7 ligam `participant_id`, nunca `band_id`.

### 4.13 Guard alargada para 3–6 min

Duas razões distintas:

- **Latência comportamental (a maior).** Entre "parem de estar em silêncio" e "o grupo está efetivamente a cantar em uníssono" há instruções, pessoas a acomodar-se e as primeiras vocalizações a desencontrarem-se. É facilmente 1–3 minutos e não é observável.
- **Latência fisiológica (menor, mas real).** A amplitude da RSA responde a uma mudança de padrão respiratório em dezenas de segundos. Mas as métricas precisam de janela: o RMSSD estabiliza em ~60 s, uma estimativa espectral em ~2 min. Uma fase de mantra que comece com 90 s de regime transitório enviesa **para baixo** o efeito que se quer medir.

Custo: ~1 minuto de 25–30 min de canto. Ganho: reduz materialmente a probabilidade de contaminar o contraste principal.

`--rest-start` (default 0.0) existe para descartar os primeiros segundos de artefacto de manuseamento do telemóvel, se o inventário o justificar.

### 4.14 NeuroKit2 vs implementação própria — híbrido, com a fronteira no que é a afirmação científica

- **Implementação própria, testada contra valores analíticos:** todo o domínio do tempo (RMSSD, SDNN, pNN50, CVNN, SD1, SD2), DFA α1, e a chamada ao Welch (via `scipy.signal.welch` diretamente). São dez linhas cada, e poder testar o valor exato vale mais do que a dependência. Mais importante: as opções do Welch são **a decisão metodológica**, e não podem estar enterradas nos defaults de um pacote.
- **NeuroKit2:** limpeza de ECG (`ecg_clean`), deteção de picos R (`ecg_peaks`), simulação de ECG sintético (`ecg_simulate`) e SampEn. É engenharia de sinal madura; reimplementar um Pan-Tompkins não acrescenta nada.
- **Não usar `hrv-analysis` nem `pyhrv`.** `pyhrv` arrasta `biosppy` e traz plotting matplotlib embutido que não vamos usar; `hrv-analysis` tem manutenção irregular. `scipy` + `numpy` + NeuroKit2 cobre tudo com menos superfície.

Versões fixadas em `requirements.txt` e registadas em `run_manifest.json`.

### 4.15 Sobreposição de tacogramas — três eixos

Além do eixo em minutos e em % da sessão, um terceiro modo: **eixo alinhado ao onset detetado**. Se as pessoas começarem a cantar em instantes diferentes, é o único dos três em que o efeito é visível em vez de ser borrado pela média.

---

## 5. Arquitetura e fluxo de dados

```
--source ─▶ DataSource ─▶ discover ─▶ measurement_filter ─▶ sniff+parse ─▶ inventory.csv/.md
                                                                               │
                                                        group_sessions(tempo ▸ pastas)
                                                                               │
                                                     ┌─────────────────────────▼─────────┐
                                                     │  RR extraction (3 vias)           │
                                                     │  native_rr ▸ ecg_peaks ▸ hr1hz    │
                                                     └─────────────────────────┬─────────┘
                                                                               │
                                          rr_clean ─▶ resample 4 Hz ─▶ Recording
                                                                               │
                    ┌──────────────────────────────────────────────────────────┼──────────────────┐
                    │                                                          │                  │
           segment_phases(config)                              detect_mantra_onset_rr()   detect_respiration_acc()
                    │                                                          └────────┬─────────┘
               Segment[]                                                                │ (avisa + alimenta resp_rate_hz)
                    │                                                                   ▼
      ┌─────────────┼─────────────┐                                           quality_report.csv
      ▼             ▼             ▼
 time_domain   frequency    nonlinear
      └─────────────┼─────────────┘
                    ▼
       metrics_recording.csv + metrics_epoch.csv
                    │
       aggregate ─▶ stats ─▶ synchrony(+permutation null)
                    │
                    ▼
         report/site.py ─▶ docs/index.html (+ report.md)
```

**Invariante arquitetural fundamental:** nenhum módulo a jusante de `signal/phases.py` conhece os números 0, 3, 6. Recebem `Segment` objects com `name`, `t_start_s`, `t_end_s`. Trocar `--mantra-start` recalcula tudo sem que uma única linha a jusante saiba que algo mudou. Um teste impõe isto: um grep de literais numéricos de offset fora de `config/` e `phases.py` falha o build.

**Segundo invariante:** o token `"livre"` não existe fora de `config/`. O mesmo teste de grep cobre-o.

**Degradação graciosa:** cada gravação é processada num `try/except` que regista a falha em `quality_report.csv` com a razão e continua. O pipeline só aborta se nenhuma gravação sobreviver. O `run.log` termina sempre com um resumo: descobertas / filtradas / processadas / com aviso / excluídas / falhadas.

---

## 6. Contratos de dados

Pydantic v2 para o que é validado na fronteira (config, `participants.csv`, `FileRecord`); dataclasses `frozen` para o que circula em memória. Todas as unidades no nome do campo.

### 6.1 `FileRecord` → `inventory.csv`

```
path, rel_path
band_id                                  # da pasta de 1.º nível (HM00, HM05, …)
session_date                             # da pasta de 2.º nível, confirmada contra metrics.json
measurement_folder                       # nome da pasta de 3.º nível
session_type                             # do metrics.json, quando existe
passes_filter: bool                      # correspondeu a measurement_filter
filter_matched_on: {metadata, folder, filename, none}
folder_session_hint
signal_type: {ECG, RR, METRICS, HR, ACC, UNKNOWN}   # HR/ACC só para o parser legado PSL
detected_by: {content, header, filename}  # content tem precedência
delimiter, decimal, encoding
timestamp_kind: {polar2000_ns, unix_ns, unix_ms, iso8601, none, unknown}
t_start_utc, t_end_utc, duration_s
n_rows, n_samples, fs_estimated_hz        # dos deltas, nunca do nome da coluna
parse_status: {ok, partial, unresolved, skipped_by_filter}
note                                      # razão, quando não é ok
```

### 6.2 `Recording` (em memória, um por banda × sessão)

```
band_id, session_id, participant_id
measurement_folder
rr_source: {native_rr, hr_column_rr, ecg_peaks, hr_1hz}
t0_utc                  # instante em que esta gravação começou
t_align_utc             # origem dos offsets de fase, conforme --align
group_t0_offset_s       # desvio face à mediana do grupo (sempre calculado)
rr_ms[], rr_t_s[]       # série limpa; t_s desde t_align_utc
corrected_mask[]        # bool, quais foram interpolados
pct_corrected: float
quality_flag: {good, warn, excluded}
rr_4hz[], hr_4hz[], t_4hz_s[]
ecg_uv[], ecg_t_s[]                      # 130 Hz, de ecg_raw.csv, quando existe
emg_residual_power[]                     # 40–60 Hz — proxy de movimento, §4.1b
resp_rate_hz?, resp_peak_power?, resp_confidence?   # EDR, §4.2/§4.4
mantra_end_edr_min?                      # fim do canto detetado por EDR, por pessoa
rest_post_valid: bool                    # §4.1b — determinado por EDR+EMG, não assumido
rest_post_duration_s?
rest_post_invalid_reason?                # movimento_emg | artefacto_rr | gravacao_terminou | sem_ecg | duracao_insuficiente
app_metrics: dict                        # hrv_metrics do metrics.json, só verificação cruzada (§2.3)
source_files[]
```

### 6.3 `Segment` (o único sítio com números de fase)

```
name: str               # "rest" | "guard" | "mantra" | "rest_post" | "inicio" | "meio" | "fim"
level: {phase, epoch}
t_start_s, t_end_s
included_in_metrics: bool          # guard = False, sempre
reliability: {full, limited, insufficient}
reliability_reason: str            # ex. "180 batimentos < 300: DFA a1 não fiável"
```

### 6.4 `metrics_recording.csv` — uma linha por banda × sessão

Identificação (`band_id`, `session_id`, `participant_id`, `measurement_folder`), qualidade (`rr_source`, `duration_s`, `n_beats`, `pct_corrected`, `quality_flag`, `excluded_reason`), onset (`assumed_mantra_start_min`, `detected_onset_min`, `onset_confidence`, `onset_delta_min`, `edr_onset_min`, `edr_onset_confidence`), verificação cruzada da app (`app_rmssd`, `app_sdnn`, `app_pnn50`, `app_quality_flag`, `app_metric_delta_pct`) e as métricas da gravação inteira.

### 6.5 `metrics_epoch.csv` — formato longo, uma linha por segmento

```
band_id, session_id, participant_id, level, segment,
t_start_s, t_end_s, duration_s, n_beats, reliability, reliability_reason,
mean_HR, min_HR, max_HR, mean_RR, SDNN, RMSSD, pNN50, CVNN, SD1, SD2, SD1_SD2,
LF_abs, HF_abs, LF_nu, HF_nu, LF_HF, total_power,
SLOW_abs, SLOW_rel, slow_peak_freq_hz, spectral_concentration,
resp_rate_hz, resp_peak_power,
SampEn, DFA_a1,
welch_window_s, n_welch_segments, nfft, fs_interp_hz
```

`guard` não aparece neste ficheiro. Um teste assert-a a sua ausência em todos os CSV de métricas.

### 6.6 Restantes artefactos

- `metrics_group.csv` — agregados (por sessão, por banda, global); sempre com `n`, `median`, `iqr_low`, `iqr_high`, `mean`, `sd`.
- `stats_contrasts.csv` — `contrast` (`rest_vs_mantra`, `mantra_vs_rest_post`, `epoch_progression`), `metric`, `n`, `n_effective`, `median_delta`, `ci_low`, `ci_high`, `ci_coverage_real`, `ci_method`, `effect_size`, `effect_kind`, `n_up`, `n_down`, `p_value`, `p_min_attainable`, `test`, `is_primary`.
- `quality_report.csv` — uma linha por gravação, com todas as flags e avisos.
- `run_manifest.json` — timestamp, versões de todas as bibliotecas, hash SHA-256 da config efetiva, bloco `primary_endpoint`, `measurement_filter` usado, offsets usados, lista de ficheiros processados com hash, `--publish-mode`, versão do git.
- `synchrony.csv` — índice de grupo ao longo do tempo, banda nula de permutação, matriz par-a-par por fase.

---

## 7. Estrutura do repositório

```
ECG_OM/
├── PLAN.md  README.md  RUNBOOK.md  requirements.txt  .gitignore
├── config/default.yaml
├── reference/                    # extraído de relatoriotemlpate.zip
│   ├── Relatorio Sessao Neroes.dc.html
│   └── _ds/ … tokens/ …  assets/ …
├── polarmed/
│   ├── cli.py  config.py  models.py  logging_setup.py
│   ├── io/      source.py sniff.py parsers.py timestamps.py inventory.py sessions.py filters.py
│   ├── signal/  rr_extract.py rr_clean.py resample.py phases.py onset.py respiration.py quality.py
│   ├── metrics/ time_domain.py frequency.py nonlinear.py sliding.py
│   │             synchrony.py aggregate.py stats.py
│   └── report/  theme.py figures.py sparkline.py site.py templates/ assets/
├── tools/  make_synthetic_data.py  vendor_assets.py
├── tests/  (espelha a estrutura de polarmed/) + tests/data/
├── docs/                         # artefacto gerado; index.html, DESIGN_NOTES.md
├── data/   out/   scratch/       # todos em .gitignore
└── .github/workflows/pages.yml
```

`.gitignore` **desde o primeiro commit**: `data/`, `out/`, `scratch/`, `*.ipynb`, `venv/`, `__pycache__/`, `*.edf`, `RR_*.txt`, `ECG_*.txt`, `HR_*.txt`, `ACC_*.txt`, `participants.csv`, `ground_truth.csv`, `session_map.csv`.

---

## 8. Plano de fases e critérios de aceitação

Cada fase termina com `pytest -q` verde e um commit próprio.

### Fase 1 — Esqueleto

Repo inicializado, venv 3.11, `requirements.txt` fixado, `config/default.yaml` com todos os limiares **incluindo `measurement_filter` e `primary_endpoint`**, `polarmed.cli` com todas as flags a fazer parse e a imprimir a config efetiva, logging para consola + `out/<run>/run.log`.

**Aceite quando:** `python -m polarmed.cli run --source x --out y --rest-end 2 --mantra-start 6 --dry-run` imprime a config resolvida com os offsets corretos e escreve `run_manifest.json`; e o pipeline **recusa correr** com `primary_endpoint` em falta, com mensagem explícita. `.gitignore` no primeiro commit.

### Fase 2 — Ingestão + filtro + gerador sintético mínimo

`DataSource`/`LocalFolderSource`, descoberta de bandas por pasta de primeiro nível, `measurement_filter` (§2.3), sniffer, parsers (Polar ECG/HR/RR/ACC, Elite HRV, CSV genérico, EDF), conversão do epoch 2000 em ns, `inventory.csv`/`.md` com matriz banda × sessão, `group_sessions()` temporal com verificação por pastas e aviso de discrepância.

**Aceite quando:**
1. **A estrutura real do `data/exemplo/` (§2.2) é confirmada contra o inventário gerado**, e §2.2 é corrigida no mesmo commit se divergir.
2. As **31** bandas `HM*` são descobertas, o `band_id` corresponde à pasta de 1.º nível e a `session_date` à de 2.º nível.
3. O filtro resolve por `session_type` do `metrics.json` quando existe, e só cai para o token da pasta quando não existe; medições que não passam aparecem com `parse_status = skipped_by_filter`, nunca `unresolved`; discordâncias entre as duas vias são reportadas.
3b. O `ecg_raw.csv` é lido com `fs` estimada em 130.0 ± 0.5 Hz a partir dos deltas, e o `t0_utc` é reconstruído de `session_date` + `session_time`; uma medição sem `metrics.json` é processada mas marcada como fora da análise de sincronia.
3c. As `hrv_metrics` da app são lidas para colunas `app_*` e a divergência de RMSSD face ao nosso cálculo é reportada.
4. `Livre`, `LIVRE` e `sessao_livre_2` correspondem; `livremente` não.
5. Os intrusos (`notas.txt`, `.DS_Store`, PDF) aparecem em `unresolved` com razão.
6. O ficheiro com cabeçalho corrompido dá `parse_status = partial` sem exceção.
7. O teste de timestamp converte um valor conhecido de epoch-2000-ns para UTC ao milissegundo.
8. O agrupamento temporal e o por pastas são ambos calculados e a discrepância é reportada sem o pipeline escolher sozinho.

### Fase 3 — Processamento de sinal

Extração RR pelas 3 vias com registo da origem; limpeza (plausibilidade 300–2000 ms, ectópicos por mediana móvel de 5 batimentos, interpolação cúbica, `pct_corrected`); reamostragem 4 Hz; `segment_phases()` incluindo `rest_post`; `detect_mantra_onset_rr()` com a estatística de rácio; `detect_mantra_end_edr()`; `detect_respiration_edr()` produzindo `resp_rate_hz` e `resp_confidence`; validação de `rest_post_valid` por janela de imobilidade (§4.1b); desvio de t0 do grupo.

**Aceite quando:** os três caminhos de RR são exercitados pelos casos-limite (banda só-HR, banda só-ECG); a gravação com 25 % de ectópicos recebe `quality_flag = excluded`; o dropout de 40 s não parte a reamostragem; uma gravação sintética com EMG elevado aos 90 s do pós-mantra recebe `rest_post_valid = False` com razão `movimento_emg`, e uma com 150 s limpos recebe `True`; uma gravação só-RR recebe `False` com razão `sem_ecg` e não quebra o pipeline; o EDR devolve `resp_confidence` baixa em janelas com EMG injetado e essas janelas são descartadas, não interpoladas; e **nenhum número de offset nem o token `livre` existem fora de `config/` e `phases.py`** (teste de grep).

### Fase 4 — Métricas e estatística

Domínio do tempo; Welch de 60 s phase-matched com `nfft = 1024` e interpolação parabólica do pico (§4.3, §4.3b); banda lenta 0.05–0.12 Hz; concentração espectral; não-lineares com os limiares de §4.6; épocas dentro do mantra; agregados hierárquicos; contrastes pareados com IC exato por estatísticas de ordem (§4.5); Friedman + Wilcoxon com Holm; `mantra_drift_slope`; sincronia com nulo de permutação entre sessões.

**Aceite quando:**
1. RMSSD e SDNN batem certo, ao `1e-9`, contra um sinal de valor analítico conhecido.
2. A interpolação parabólica recupera a frequência de um seno sintético de 0.103 Hz com erro < 0.002 Hz.
3. `guard` não aparece em nenhum CSV.
4. A fase de mantra curta demais emite aviso e não produz épocas sobrepostas.
5. Um segmento de 180 s recebe `reliability = insufficient` para DFA α1 e SampEn e é excluído desses contrastes, com `n_effective` correto.
6. O formatador de p-value recusa emitir sem `n` e `p_min_attainable`.
7. Com n = 5 o `ci_method` é `exact_order_statistic` e `ci_coverage_real` não é 0.95.
8. O contraste marcado `is_primary = True` corresponde ao bloco `primary_endpoint` da config.

### Fase 5 — Dados sintéticos de fidelidade total + endurecimento

6 bandas × 3 sessões **na estrutura de pastas `HM*/…livre…/`**, com medições não-`livre` de distração; RSA dependente da fase (0.20–0.30 Hz no repouso → 0.09–0.11 Hz no canto, rampa de 30–60 s, amplitude maior); `true_onset_min` em `ground_truth.csv`; duas gravações com onset ≈ 8.5 min; ECG sintético coerente com os RR, com modulação de amplitude respiratória (para o EDR ter o que detetar) e episódios de EMG injetado; **conformidade mista no pós-mantra — metade das gravações com imobilidade prolongada e regresso parcial à linha de base, a outra metade com movimento precoce ou gravação terminada cedo**; e os 10 casos-limite.

**Aceite quando:** `detect_mantra_onset_rr()` recupera `true_onset_min` dentro de ±45 s na maioria das gravações; o aviso dispara nas duas gravações atrasadas; um teste verifica que os picos R do ECG sintético reconstroem a série RR gerada; o filtro exclui corretamente as medições de distração; e a cobertura em `signal/` e `metrics/` é ≥ 80 %.

> **Honestidade sobre este teste:** os dados sintéticos são gerados com o mesmo modelo de fenómeno que o detetor procura. O teste valida a **implementação**, não o desempenho em dados reais. Fica escrito no docstring do teste e no `RUNBOOK.md`.

### Fase 6 — Tema, `DESIGN_NOTES.md` e secção de amostra ⟵ **portão de aprovação**

Extrair `relatoriotemlpate.zip` para `reference/`, vendorizar fontes (`tools/vendor_assets.py`, **única etapa que precisa de rede**, corre uma vez), `assets/theme.css` com as variáveis, template Plotly derivado dos tokens, `docs/DESIGN_NOTES.md`.

**Aceite quando:** é mostrada uma página com uma secção renderizada (capa + painel 5, repouso vs mantra) e é **aprovada antes de gerar o site todo**. Verificação automática de contraste ≥ 4.5:1 e simulação de daltonismo.

### Fase 7 — Site completo

As 12 secções, nav lateral, offsets e `measurement_filter` impressos no cabeçalho, `report.md`, `--publish-mode {full,aggregate,anonymous}`.

**Aceite quando:** `docs/index.html` abre offline por duplo clique com o mesmo aspeto que servido em HTTP; `--publish-mode aggregate` não deixa nenhum RR individual nem ID real em `docs/` (teste que faz grep ao HTML gerado); o painel de sincronia só existe se o nulo de permutação estiver presente; nenhuma média aparece sem `n` e sem dispersão; o resultado primário aparece antes de tudo o resto e os exploratórios estão marcados; e os termos proibidos (`"significativo"`, `"tónus vagal"`) não aparecem.

### Fase 8 — Acessórios

`GoogleDriveApiSource` com cache em disco, apontando por defeito para a pasta de §2.1; workflow de GitHub Actions para Pages (criado mas **não ativado** sem confirmação); `README.md` e `RUNBOOK.md` em português.

---

## 9. Riscos e mitigação

| Risco | Mitigação |
|---|---|
| Deriva temporal confundida com efeito do mantra | Painel 7 como controlo interpretativo; `mantra_drift_slope`; `rest_post` oportunista (§4.1b) quando observável; limitação na capa |
| Participantes não permanecem sentados após o canto | Assumido como incontrolável. `rest_post_valid` determinado por EDR + proxy de EMG por gravação (mais fraco que ACC, §4.1b); contraste corre sobre o subconjunto válido com `n_effective`; viés de auto-seleção escrito no relatório; marcado exploratório e proibido como endpoint primário |
| Efeito do RMSSD inseparável da mudança respiratória | `resp_rate_hz` reportada por época (§4.2); linguagem controlada por lista de termos proibidos |
| Sobre-interpretação com n pequeno | Endpoint primário declarado (§4.7); sem p-values no corpo; IC exato em vez de bootstrap; deltas individuais em primeiro plano |
| Estrutura do Drive diferente da declarada | **Verificada em 2026-09-11 e §2.2–§2.5 reescritas** (4 níveis, formato próprio, sem ACC, 31 bandas). Parser do Polar Sensor Logger mantido para o caso de a app mudar até ao dia |
| Amostra do Drive é truncada e não representa durações reais | §2.1 proíbe afinar limiares ou tirar conclusões a partir dela; os limiares de duração vivem em config e só se validam com dados sintéticos de fidelidade total (Fase 5) |
| 31 bandas em vez de 3–20 | Paleta sequencial em vez de categórica (§4.9); matriz de sincronia 31×31 com heatmap em vez de pares; orçamento do HTML recalculado na Fase 7 |
| Filtro `livre` demasiado estrito ou demasiado lasso | Matching normalizado por tokens; `--measurement-filter ""` desativa; matriz banda × sessão no inventário expõe bandas com zero medições |
| Sessões mal agrupadas entre bandas | Via temporal primária, verificação por pastas, discrepância reportada sem escolha automática; `--session-map` para override manual |
| Artefacto de EMG do canto degrada o ECG **e o EDR** | Via RR nativa preferida e independente do ECG; EDR rebaixado a validador de segunda linha com `resp_confidence` por janela (§4.4); `pct_corrected` por fase, não só por gravação; limiares em config, não afinados antes dos dados reais |
| Grupo atrasa-se e contamina o repouso | Guard alargada (§4.13) + validador de onset por RR e por EDR + aviso destacado |
| Relógios das bandas desalinhados | `group_t0_offset_s` sempre calculado; aviso > 60 s; sincronia omitida com razão se o desvio for intolerável |
| Não-lineares calculadas sobre dados insuficientes | Limiares de batimentos em config (§4.6); exclusão automática do contraste; `n_effective` reportado por métrica |
| Wheels do stack científico em Windows | venv fixado em 3.11.9, versões pinadas, `run_manifest.json` regista tudo |
| Bundle Plotly inline torna o ficheiro pesado | Bundle parcial (scatter/heatmap apenas); orçamento de 6 MB para `index.html`; teste que falha se exceder |
| Fontes vendorizadas incham o repo | Subset latin apenas, woff2; ~200–350 KB total; `assets/fonts/LICENSES.md` |
| Dados fisiológicos num histórico Git público | `.gitignore` no primeiro commit; `--publish-mode aggregate` por defeito; nenhum push sem confirmação |

---

## 10. Privacidade

Nenhum push acontece sem confirmação explícita.

1. **Repo privado + Pages privado.** Mais seguro. Exige plano pago do GitHub.
2. **Repo público, só agregados.** *Recomendado e default.* CSVs individuais e dados brutos em `.gitignore`; o HTML embebe apenas séries agregadas e IDs pseudonimizados. As séries individuais dos painéis 3 e 8 passam a ser desenhadas a partir de dados já agregados ou omitidas.
3. **Público totalmente anonimizado.** IDs aleatórios regenerados a cada corrida (o que quebra a comparação entre corridas), sem data exata nem local.

`--publish-mode {full,aggregate,anonymous}` controla exatamente o que entra em `docs/`. `full` é para uso local e o pipeline **recusa-o** se detetar um remote git público configurado, a menos que se passe `--i-know-what-im-doing`.

**Pendente, a resolver na Fase 6:** as referências citadas no relatório (Inbaraj et al. 2022, *Int J Yoga*; ECA em hipertensos, *Ann Neurosci* 2025) são verificadas contra a fonte antes de entrarem no site publicado. Nenhuma citação é publicada sem confirmação.

---

## 11. Verificação de ponta a ponta

```powershell
# ambiente
& "$env:LOCALAPPDATA\Programs\Python\Python311\python.exe" -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt

# 0. dados de exemplo reais (descarregar a pasta do Drive para data/exemplo/)
python -m polarmed.cli inventory --source .\data\exemplo --out .\out\inventario
#    → confirmar a matriz banda x sessao e o filtro "livre"

# 1. gerar dados sinteticos e validar tudo
python -m polarmed.cli synth --out .\data\synthetic --bands 6 --sessions 3 --edge-cases
python -m polarmed.cli run   --source .\data\synthetic --out .\out\dryrun
pytest -q --cov=polarmed/signal --cov=polarmed/metrics --cov-fail-under=80

# 2. correr sobre os dados reais de exemplo
python -m polarmed.cli run --source .\data\exemplo --out .\out\exemplo

# 3. provar que os offsets e o filtro sao mesmo parametros
python -m polarmed.cli run --source .\data\exemplo --out .\out\recorte-b `
    --rest-end 2 --mantra-start 6 --measurement-filter livre
#    → metricas, estatistica e site recalculados; cabecalho mostra o novo recorte

# 4. abrir offline
start .\docs\index.html
```

**Confirmações manuais no fim:**

- `inventory.md` classifica tudo, e a matriz banda × sessão não tem células inesperadamente vazias;
- só medições `livre` foram processadas, e as restantes aparecem como `skipped_by_filter`;
- o aviso de onset aparece nas gravações atrasadas;
- `guard` não existe em nenhum CSV de métricas;
- o resultado primário aparece em primeiro lugar e está rotulado como declarado à partida;
- o painel de `rest_post` mostra quantos participantes tinham janela válida e porquê os restantes não tinham, e está marcado como exploratório;
- `docs/index.html` legível projetado a 3 m.
