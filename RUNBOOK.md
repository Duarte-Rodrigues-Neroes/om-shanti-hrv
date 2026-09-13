# RUNBOOK — procedimento do dia

Documento operacional. O que fazer antes, durante e depois de uma sessão, e o
que verificar antes de mostrar o relatório a alguém.

---

## Antes da sessão

**Consentimento informado.** Cada participante tem de saber que está a ser
registado sinal cardíaco, para que fim, quem terá acesso e que pode pedir a
eliminação dos seus dados. Não se publicam dados individuais sem autorização
explícita, e o contexto identifica pessoas mesmo sem nomes — quem esteve
naquela sala, naquele dia.

**Equipamento.**

- [ ] Bandas humedecidas nos elétrodos. Banda seca dá artefacto e é a causa
      número um de gravações inutilizáveis.
- [ ] Bateria dos telemóveis acima de 50 %. Uma gravação de uma hora consome
      bastante.
- [ ] Anotar que banda foi para que participante, num papel. Se as bandas
      rodarem entre pessoas, é isto que permite reconstruir o mapeamento.

**O erro mais caro, aprendido nos dados de setembro de 2026:** em cinco das
sete gravações longas a série RR **terminou muito antes do fim da sessão** —
numa delas 23 minutos antes. A gravação parecia estar a decorrer. Portanto:

- [ ] Confirmar, a meio da sessão, que cada telemóvel ainda mostra sinal ativo.
- [ ] Não deixar o telemóvel bloquear nem a app ir para segundo plano.
- [ ] Parar as gravações **o operador**, não cada participante.

---

## Durante

- Anotar a hora de início do canto, num papel, com o relógio do telemóvel.
  Todo o desenho da análise depende de não saber isto; trinta segundos de
  caneta resolvem o problema.
- Anotar quem chegou atrasado, quem saiu, quem se mexeu muito.
- Se houver um período de repouso, **gravá-lo como ficheiro separado**
  (`rest_5min_*`), não como o início da gravação do canto. Foi o que salvou a
  análise de setembro: as gravações longas não continham nenhuma linha de base
  utilizável, e só as gravações de repouso dedicadas permitiram comparar.

---

## Depois — correr o pipeline

```powershell
.\.venv\Scripts\Activate.ps1
python tools/fetch_drive_session.py           # ou copiar a pasta para data/
python -m polarmed.cli run --source .\data\sessao --out .\out\<data>
```

---

## O que verificar ANTES de apresentar

### 1. `out/<data>/run.log`

Ler as linhas `WARNING`. Cada uma é uma gravação que não entrou na análise, com
a razão. Se forem mais do que uma ou duas, o problema está na aquisição e o
relatório vai ser fino.

### 2. Secção 08 do relatório, «Qualidade e cobertura»

A coluna **Cobertura** é a mais importante. `completa` significa que a série RR
chega ao fim da sessão declarada. Um valor `-N min` significa que faltam N
minutos no fim — e se a janela de canto são os últimos 15 minutos, uma
gravação com `-20 min` não tem sinal nenhum na janela que interessa.

Verificar também `Corrigidos %`. Acima de 15 % a gravação sai dos agregados
(continua visível, marcada). Acima de 40 % é lixo: normalmente batimentos
falhados, que aparecem como intervalos de 2×, 3× ou 5× a mediana.

### 3. Secção 06, «Ao longo da sessão»

Se o rácio banda-lenta/HF já estiver alto no minuto 2 e não houver degrau na
fronteira dos 15 minutos, então a gravação **não contém uma linha de base sem
canto** e o contraste dentro da gravação não mede nada. Foi exatamente o que
aconteceu em setembro. Nesse caso a comparação válida é contra as gravações
`rest_5min_*`.

### 4. O n

A capa diz quantas gravações entraram em cada condição. Se forem menos de
cinco por condição, não usar linguagem de grupo ao apresentar. O relatório já
impede a palavra «significativo» — o build falha se ela aparecer — mas a fala
não é verificada por ninguém.

---

## Se uma banda falhou

O pipeline nunca aborta por causa de um ficheiro mau: regista a razão e
continua. Uma gravação que falha aparece na secção 08 e no `run.log`. Não
apagar nada — a gravação truncada é informação sobre a aquisição.

---

## Recortar de outra maneira

Se souber que o canto durou 20 minutos e não 15:

```powershell
python -m polarmed.cli run --source .\data\sessao --out .\out\recorte-b --mantra-min 20
```

Métricas, comparação e site são recalculados. O novo recorte aparece no
cabeçalho do relatório e no `run_manifest.json`.

---

## Nota sobre os testes

O gerador de dados sintéticos (quando existir) produz dados com o mesmo modelo
de fenómeno que o detetor procura. Esses testes validam a **implementação**, não
o desempenho em dados reais. Um teste verde não é evidência de que a deteção de
onset funciona no terreno.
