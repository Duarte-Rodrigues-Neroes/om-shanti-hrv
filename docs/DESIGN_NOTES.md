# DESIGN_NOTES — o que foi extraído do `reference/`

O `reference/` contém o design system neroes (tokens CSS, brand readme,
logótipos) e uma folha de relatório de sessão individual. O vocabulário visual
foi **extraído e reconstruído**, não copiado: o original é um sheet de um
participante construído sobre um runtime de canvas, e este relatório é uma
página de coorte com nove secções.

O que passou para `polarmed/report/theme.py`:

## Cor

Base petrol, não preto. Escada de superfícies do fundo do gráfico à carta
elevada:

| Token | Valor | Uso aqui |
|---|---|---|
| `INK_900` | `#0C1D24` | fundo da página, leito dos gráficos |
| `INK_700` | `#152E38` | a folha |
| `INK_600` | `#1B3A46` | cartões de métrica |
| `HEADER` | `#0B333C` | faixa de cabeçalho e rodapé |

Acentos da marca: teal `#2E9296` (primário), verde `#479B7E`, azul `#3A67AE`,
e brass `#B8873C` usado com parcimónia. Variantes luminosas
(`#43BEC3`, `#5BBC99`, `#5B8AD4`, `#D4A455`) para linhas de dados sobre escuro.
O ember `#C4685A` é uma adição documentada do design system — a marca não tem
vermelho, mas estados degradados precisam de uma cor.

### Onde divergi, e porquê

O triádico da marca é todo frio, e teal contra verde é precisamente o par que a
deuteranopia colapsa. Com uma cor por gravação isso seria ilegível. Separei os
dois usos da cor:

- **Papéis semânticos** (poucos, fixos, com significado) usam a paleta da marca:
  repouso = azul `#5B8AD4`, canto = teal `#43BEC3`, excluído = ember.
  Duas cores bem separadas em matiz *e* em luminância.
- **Identidade de gravação** (muitas, sem significado intrínseco) far-se-ia por
  hover e toggle de legenda, não por matiz.

## Tipografia

- **Sora** — títulos (600, tracking −2,5 % nos tamanhos grandes) e corpo (400, 15/1,6).
- **IBM Plex Mono** — etiquetas, navegação, cabeçalhos de tabela e **todos os
  valores numéricos**, em maiúsculas com tracking de 0,14 em (0,22 em nos
  eyebrows de secção).
- **Newsreader itálico** — exclusivamente para a citação de visão.

Números sempre com `font-variant-numeric: tabular-nums`, para que as colunas
alinhem.

As três famílias estão embebidas como woff2 base64 (subset latino) em vez de
carregadas do Google Fonts: o relatório tem de abrir sem rede.

## Forma e linha

Tudo a 1px, «instrument weight»: `rgba(169,191,197,0.16)` para bordas,
`0.09` para divisórias. Raios pequenos — 10px em cartões, 6–8px em leitos de
gráfico, `999px` (pill) em botões e badges. Sem gradientes no chrome.

## Gráficos

O leito é `INK_900` embutido, grelha pontilhada de baixo contraste, linhas de
1,5–2px nas variantes luminosas. O template Plotly em
`theme.plotly_layout()` deriva diretamente destes tokens para que as figuras
não pareçam coladas de outro documento.

O que **não** adotei do original: o glow gaussiano das linhas. No sheet
individual há uma ou duas séries; aqui há nove sobrepostas, e o glow torna-as
ilegíveis umas sobre as outras.

## Estrutura da página

Do original vêm os eyebrows numerados de secção (`01 — O RESULTADO` em mono
caps, seguidos de uma régua de 1px), os cartões de estatística com etiqueta
mono / valor Sora 34px / nota de rodapé sob uma divisória, e a faixa de
cabeçalho e rodapé em `#0B333C`.

Acrescentei uma navegação lateral fixa, que o original não tem porque é uma
folha única. Abaixo de 900px desaparece e a página passa a coluna única.

## Voz

O brand readme distingue duas vozes e proíbe misturá-las: **MEASURED** (mono,
factual, sempre com a atribuição) e **Vision** (Newsreader itálico, nunca com
números). Respeitado: a única frase em serifa itálica é a citação do apêndice,
e não contém nenhum valor.

A regra de conformidade do design system — nunca «cura», «trata», «garantido»,
«provado» — está automatizada: `theme.FORBIDDEN_TERMS` faz o build falhar se a
prosa gerada contiver qualquer um desses termos, mais «significativo» e «tónus
vagal», que esta análise não suporta. A verificação corre apenas sobre a prosa
autorada, nunca sobre o Plotly minificado nem sobre os blobs base64 das fontes,
onde qualquer sequência de bytes aparece por acaso.
