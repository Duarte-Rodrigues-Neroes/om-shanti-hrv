# O que temos, o que está partido, e o que isso faz aos números

Resumo de uma página. Detalhe no relatório e no `RUNBOOK.md`.

---

## 1. O que temos

**16 gravações** de 8 bandas Polar H10, em **três dias diferentes** (11, 12 e 13
de setembro). Cada gravação tem `rr_intervals.csv` (batimento a batimento),
`ecg_raw.csv` (130 Hz) e `metrics.json`.

Depois de filtrar, **9 entram na análise**:

| | quantas | o que são |
|---|---|---|
| Canto | 3 | `livre_1h` com ≥ 15 min de RR |
| Repouso | 6 | `rest_5min_manha`, gravações dedicadas de ~5 min |
| Descartadas | 7 | RR curto demais para a janela de canto |

---

## 2. Os cinco problemas

### ① Não há linha de base dentro das gravações de canto ⚠️ o mais grave

Tu disseste: *"os últimos 15 minutos são canto"*. Medimos o rácio
banda-lenta/HF ao longo de toda a gravação e ele **sobe ao minuto 2–4 e fica
alto até ao fim**. Não há degrau nenhum na fronteira dos 15 minutos.

Ou seja: estas gravações parecem ser canto quase do início ao fim. Comparar
"últimos 15 min" contra "os 15 anteriores" é comparar canto com canto — e dá,
como esperado, diferenças de 1 a 5 %.

**Efeito:** o contraste dentro da gravação não mede nada. Tivemos de usar as
gravações `rest_5min_manha` como linha de base.

### ② As gravações param sozinhas a meio

As séries RR **não têm buracos** — não é ruído, é truncagem. Mas **5 das 7
gravações longas terminam muito antes do fim da sessão declarada**:

| Banda | Sessão diz | RR vai até | Perde |
|---|---|---|---|
| HM15 (11/9) | 45,9 min | 22,6 min | **23,3 min** |
| HM02 (12/9) | 22,4 min | 2,3 min | 20,1 min |
| HM11 (12/9) | 22,6 min | 6,2 min | 16,4 min |
| HM15 (13/9) | 50,1 min | 1,7 min | 48,4 min |
| HM13 (11/9) | 8,3 min | 1,1 min | 7,2 min |

**Efeito:** nessas, a janela dos últimos 15 minutos **não tem sinal nenhum**.
De 7 gravações de canto sobraram 2 com a janela completa (HM13 e HM16).

### ③ Não é um desenho emparelhado

Repouso e canto são de **pessoas diferentes, em dias diferentes**. Nenhum
participante tem as duas condições com qualidade utilizável.

**Efeito:** a comparação é entre grupos, não dentro da mesma pessoa. Perde-se
todo o poder estatístico de medidas repetidas, que era o ponto do desenho
original.

### ④ Três bandas não têm gravação de canto

HM01, HM07 e HM09 só têm `rest_5min_manha`.

**Efeito:** n de canto = 3 (com uma delas, HM15, de qualidade duvidosa porque o
RR acabou cedo).

### ⑤ Uma gravação de repouso está corrompida

HM07 tem RR bruto até **11 220 ms** — intervalos de 11 segundos. São batimentos
falhados (rácios de 2×, 3×, 11× face à mediana). 41 % dos batimentos precisaram
de correção.

**Efeito:** foi excluída dos agregados. Nota: excluí-la **melhora** o resultado
(o máximo do repouso cai de 0,87 para 0,53), por isso a conclusão não dependia
dela.

---

## 3. O que sobrou, e aguenta

Apesar de tudo isto, há um resultado limpo:

**Durante o canto o espectro colapsa numa risca estreita perto de 0,08 Hz** —
cerca de 5 ciclos por minuto. O rácio banda-lenta/HF separa as condições **sem
sobreposição**:

| | mediana | intervalo | n |
|---|---|---|---|
| Repouso | 0,39 | −0,24 … 0,53 | 5 |
| **Canto** | **0,98** | **0,97 … 1,44** | **3** |

Em escala linear: o canto **quadruplica** o domínio da banda lenta (2,5× → 9,5×).

**O RMSSD e a frequência cardíaca não mudam.** O que muda é a *forma* do
espectro, não a *quantidade* de variabilidade. Isto é consistente com respiração
lenta imposta pelo canto — não é evidência de "mais relaxamento".

Com n = 3 contra 5 e sem emparelhamento, isto é uma **observação exploratória**.
Dizer que os intervalos não se cruzam é tudo o que esta dimensão amostral
suporta, e é por isso que não há p-values no relatório.

---

## 4. Três mudanças que resolvem quase tudo na próxima

1. **Anotar num papel a hora a que o canto começa.** Trinta segundos de caneta
   eliminam o problema ①, que é o mais grave de todos.
2. **Gravar o repouso como ficheiro separado, no mesmo dia, para toda a gente.**
   Resolve ③ e ④: passa a haver comparação dentro da mesma pessoa.
3. **Verificar a meio da sessão que cada telemóvel ainda está a gravar.** O
   problema ② custou 5 das 7 gravações e é puramente operacional — a app parece
   estar a gravar quando já não está.
