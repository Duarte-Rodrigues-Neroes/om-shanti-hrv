# polarmed — pipeline ECG/HRV para canto de mantra

Pipeline reprodutível que, dada uma pasta de gravações Polar H10, produz
métricas de HRV, um `bundle.json` com todos os números e um relatório HTML
autocontido em `docs/index.html`.

O relatório abre por duplo clique **sem rede**: o Plotly, as fontes da marca e
o logótipo estão embebidos no ficheiro.

---

## Arranque rápido

```powershell
& "$env:LOCALAPPDATA\Programs\Python\Python311\python.exe" -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt

# assets de terceiros (Plotly + fontes). Unica etapa que precisa de rede.
python tools/vendor_assets.py

# corrida completa
python -m polarmed.cli run --source .\data\sessao --out .\out\2026-09-13
start .\docs\index.html
```

> **Python 3.11.** Não use o 3.14 do PATH — o stack científico
> (scipy, scikit-learn, NeuroKit2) não está validado nessa versão.

---

## Como os dados chegam

A pasta partilhada do Drive está ligada por link, o que permite descarregar
sem autenticação nenhuma:

```powershell
python tools/fetch_drive_session.py            # tudo
python tools/fetch_drive_session.py --skip-ecg # so RR + metadados, muito mais rapido
```

Os IDs dos ficheiros estão listados explicitamente em
`tools/fetch_drive_session.py` porque *listar* uma pasta exige autenticação,
mas *descarregar* um ficheiro partilhado por link não.

### Estrutura esperada

```
data/sessao/
└── HM13/                    # banda
    └── 2026-09-11/          # data
        └── livre_1h_2/      # medicao
            ├── rr_intervals.csv   seq,rr_ms,timestamp_ms
            ├── ecg_raw.csv        seq,voltage_uv,timestamp_ms  (130 Hz)
            └── metrics.json       metadados + HRV da propria app
```

`metrics.json` é a **única fonte de tempo absoluto** — os timestamps dos CSV
começam em zero. As `hrv_metrics` que a app já calculou são lidas apenas para
verificação cruzada e nunca entram no relatório: são computadas sobre no máximo
os primeiros 1000 batimentos, o que numa gravação de 42 minutos descreve os
primeiros doze e mais nada.

---

## O recorte das fases

**As fases são ancoradas no fim da gravação, não no início.** A única
informação disponível sobre o protocolo é que o troço final de cada leitura
corresponde ao canto. Ninguém registou o início do repouso, vários
participantes não o fizeram, e alguns ainda caminhavam quando a gravação
começou.

```
[ descarte ][ baseline ][ guard ][        mantra        ]
^                                                       ^
inicio (ruidoso, cortado por deteção de artefacto)   ultimo batimento valido
```

- A âncora é o **último batimento válido**, não a duração declarada: várias
  gravações declaram uma duração muito maior do que a série RR que de facto
  contêm.
- A `baseline` recebe a **mesma duração** do `mantra`, para que os espectros
  sejam comparáveis.
- A `guard` nunca entra em métrica nenhuma.
- O descarte inicial é **detetado dos dados** (taxa de correção em janela
  deslizante até assentar), não fixado. Uma gravação limpa não perde nada.

Tudo isto são parâmetros:

```powershell
python -m polarmed.cli run --source .\data\sessao --out .\out\teste `
    --mantra-min 20 --guard-min 5 --min-baseline-min 8
```

O recorte usado aparece no cabeçalho do relatório e no `run_manifest.json`,
junto ao hash da configuração — para que um relatório antigo possa sempre ser
ligado ao recorte exato que o produziu.

---

## Estrutura

```
polarmed/
├── config.py          modelo Pydantic; config/default.yaml e a fonte de verdade
├── models.py          contratos de dados
├── analysis.py        driver por gravacao
├── io/                timestamps, parsers, descoberta
├── signal/            limpeza de RR, segmentacao ancorada no fim
├── metrics/           dominio do tempo, espectro, janela deslizante
└── report/            tema, bundle, gerador do site
```

**Invariante:** nenhum módulo a jusante de `signal/phases.py` conhece números de
fase. Recebem objetos `Segment` com `t_start_s` e `t_end_s`.

---

## Testes

```powershell
pytest -q
pytest --cov=polarmed/signal --cov=polarmed/metrics --cov-report=term-missing
```

As métricas de domínio do tempo são testadas contra valores calculáveis à mão,
não contra outra implementação.

---

## Privacidade

`data/`, `out/` e qualquer ficheiro com RR individuais estão no `.gitignore`
desde o primeiro commit, tal como `drive_token.json` e restantes credenciais.
O relatório usa apenas pseudónimos de banda e não publica séries RR individuais.
Nenhum push é feito sem confirmação explícita.
