# Verificacao cega: DES Y3 3x2pt (Abbott et al. 2022, PRD 105, 023520)

Recontagem dos dez resumos de posterior que o artigo imprime, a partir das cadeias
publicas que os proprios autores publicaram no DES DR. Trabalho feito isolado, sem
olhar nenhuma rodada anterior.

Pasta: `E:\Ciencia\noturno\2022-abbott-desy3-cego`

## 1. O que eu pre-registrei

`claims_cego.json` (sha256 em `claims_cego.sha256`:
`f860343032604a94953cdcf8d3137222f1c117247384103d968dc1b2c49485c7`), escrito antes de
baixar qualquer arquivo.

A frase de metodos do artigo e "the mean in each parameter, along with the 68%
confidence limit (CL) of posterior volume around the mean". Pre-registrei cinco
leituras possiveis:

| | definicao | receita |
|---|---|---|
| **D1** (principal) | 34% de volume de cada lado da media | `[Q(F(media)-0.34), Q(F(media)+0.34)]` |
| D2 | quantis iguais 16/84, citados em relacao a media | `Q(0.16)-media`, `Q(0.84)-media` |
| D3 | intervalo de maior densidade (HPD) de 68%, citado em relacao a media | menor intervalo com 68% do volume |
| D4 | simetrico em x em torno da media | menor `d` com `P(m-d<x<m+d)=0.68` |
| D5 | quantis iguais em torno da mediana | `Q(0.16)-mediana`, `Q(0.84)-mediana` |

Escolhi **D1** como principal porque e a leitura literal de "68% de volume **em torno
da media**": a media e o ponto de referencia e metade do volume e contada para cada
lado dela.

Tolerancia pre-registrada, sem afrouxar depois:

- valor central: `max(0.002, 0.20*sigma)`. 0.002 e meia unidade do ultimo digito
  impresso. Para `w` (2 casas): `max(0.01, 0.20*sigma)`.
- limites: `max(0.002, 0.15*|limite impresso|)`. Para `w`: `max(0.01, 0.15*|limite|)`.

Pre-processamento tambem fixado antes: usar a coluna `weight` do arquivo (lida pelo
nome no cabecalho), nenhum burn-in (nested sampling), e `S_8 = sigma_8*sqrt(Om/0.3)`
calculado linha a linha antes de marginalizar.

## 2. Dados

Baixados com `curl`, TLS ligado, de
`https://desdr-server.ncsa.illinois.edu/despublic/y3a2_files/chains/`:

| arquivo | bytes | sha256 | amostras | neff (Kish) |
|---|---|---|---|---|
| chain_3x2pt_lcdm_SR_maglim.txt | 16.351.854 | `2ba4415560c8a02ccb8da0b7d5cf4552c088a1cc981c1ee96fda90bba31563ff` | 22.619 | 6.310 |
| chain_3x2pt_wcdm_SR_maglim.txt | 17.683.697 | `12cbf1b1c4629960a9fa42b56723224c727023b0983ac6d90dea4f09bfaae627` | 23.652 | 6.506 |
| chain_all_lcdm.txt | 50.762.197 | `57b2257df22a12f1400251987c46038c5411fd6633b2286cc91c69fe4dc1109c` | 45.932 | 8.243 |
| read_chains_y3a2.py | 1.322 | `35bc04cefc39d3a216c50e0ffe247826b960508e004a04dbd9a6225ffbca5821` | - | - |

Os pesos ja vem normalizados (somam 1) e o maior peso e 2e-4 da soma, entao nenhuma
amostra domina. Todas as colunas foram localizadas pelo nome no cabecalho.

## 3. Os numeros e a tabela de comparacao

Coluna "impresso" = o que o artigo diz. Cada celula de definicao traz `+limite -limite`
e OK/X pela tolerancia pre-registrada. `D3s` e o HPD calculado sobre a marginal 1D
suavizada (ver secao 5); nao estava no pre-registro.

| cadeia | par | impresso | media | D1 (pre-reg) | D2 16/84 | D3 HPD cru | D3s HPD suave | D4 simetrico | D5 mediana |
|---|---|---|---|---|---|---|---|---|---|
| 3x2pt lcdm | S_8 | 0.776 +0.017 -0.017 | 0.7760 OK | +0.0185 -0.0173 OK | +0.0178 -0.0178 OK | +0.0157 -0.0198 **X** | +0.0176 -0.0187 OK | +0.0178 -0.0178 OK | +0.0182 -0.0174 OK |
| 3x2pt lcdm | Omega_m | 0.339 +0.032 -0.031 | 0.3388 OK | +0.0303 -0.0316 OK | +0.0309 -0.0311 OK | +0.0294 -0.0325 OK | +0.0313 -0.0319 OK | +0.0310 -0.0310 OK | +0.0306 -0.0314 OK |
| 3x2pt lcdm | sigma_8 | 0.733 +0.039 -0.049 | 0.7330 OK | +0.0516 -0.0398 **X** | +0.0449 -0.0450 **X** | +0.0370 -0.0517 OK | +0.0404 -0.0503 OK | +0.0449 -0.0449 **X** | +0.0484 -0.0415 **X** |
| 3x2pt wcdm | S_8 | 0.775 +0.026 -0.024 | 0.7745 OK | +0.0236 -0.0263 OK | +0.0250 -0.0247 OK | +0.0253 -0.0241 OK | +0.0264 -0.0239 OK | +0.0248 -0.0248 OK | +0.0240 -0.0257 OK |
| 3x2pt wcdm | Omega_m | 0.352 +0.035 -0.041 | 0.3516 OK | +0.0394 -0.0375 OK | +0.0373 -0.0390 OK | +0.0331 -0.0429 OK | +0.0352 -0.0422 OK | +0.0383 -0.0383 OK | +0.0387 -0.0377 OK |
| 3x2pt wcdm | sigma_8 | 0.719 +0.037 -0.044 | 0.7185 OK | +0.0447 -0.0383 **X** | +0.0419 -0.0404 OK | +0.0373 -0.0445 OK | +0.0391 -0.0445 OK | +0.0412 -0.0412 OK | +0.0434 -0.0388 **X** |
| 3x2pt wcdm | w | -0.98 +0.32 -0.20 | -0.9808 OK | +0.2284 -0.3581 **X** | +0.2668 -0.2773 **X** | +0.3185 -0.1996 OK | +0.3280 -0.2053 OK | +0.2707 -0.2707 **X** | +0.2330 -0.3111 **X** |
| all lcdm | S_8 | 0.812 +0.008 -0.008 | 0.8120 OK | +0.0077 -0.0083 OK | +0.0079 -0.0080 OK | +0.0082 -0.0076 OK | +0.0084 -0.0077 OK | +0.0080 -0.0080 OK | +0.0078 -0.0081 OK |
| all lcdm | Omega_m | 0.306 +0.004 -0.005 | 0.3062 OK | +0.0045 -0.0042 OK | +0.0043 -0.0044 OK | +0.0042 -0.0045 OK | +0.0044 -0.0045 OK | +0.0043 -0.0043 OK | +0.0044 -0.0043 OK |
| all lcdm | h | 0.680 +0.004 -0.003 | 0.6802 OK | +0.0034 -0.0035 OK | +0.0034 -0.0034 OK | +0.0032 -0.0036 OK | +0.0035 -0.0035 OK | +0.0034 -0.0034 OK | +0.0034 -0.0034 OK |

Contagem de limites dentro da tolerancia, de 10:

```
D1 (pre-registro)      7/10
D2 quantis 16/84       8/10
D3 HPD cru             9/10
D3s HPD suavizado     10/10
D4 simetrico em x      8/10
D5 mediana             7/10
valores centrais      10/10
```

## 4. Veredito

**Os dez valores centrais reproduzem**, todos como a media ponderada da marginal, e
quase todos batendo no ultimo digito impresso (0.7760, 0.3388, 0.7330, 0.7745, 0.3516,
0.7185, -0.9808, 0.8120, 0.3062, 0.6802). Isso confirma a primeira metade da frase de
metodos sem ambiguidade nenhuma.

**Os limites nao reproduzem pela minha regra principal (D1): 7 de 10.** Pelo
pre-registro isso cai em `REPRODUZ_COM_OUTRA_DEFINICAO`: uma unica definicao
alternativa, o HPD de 68% da marginal suavizada (D3s), passa em **todos os 10**. O
resultado do artigo reproduz; o que nao se sustenta e a descricao que a secao de
metodos da do procedimento.

Veredito: **REPRODUZ_COM_OUTRA_DEFINICAO**.

O caso que decide e o `w`, porque e o unico alvo com assimetria forte. O artigo imprime
`-0.98 +0.32 -0.20`: cauda longa para cima. A minha D1 da `+0.23 -0.36`, assimetria no
sentido oposto, errando por quase o dobro do limite. So o HPD acerta o sinal e o
tamanho (`+0.3185 -0.1996` cru, `+0.3280 -0.2053` suave). O `sigma_8` do 3x2pt LCDM diz
a mesma coisa de forma mais branda: o impresso e `+0.039 -0.049` e, das seis
definicoes, so as duas de HPD reproduzem esse par.

A consequencia e que o intervalo impresso **nao e centrado no valor central impresso**.
O numero a esquerda e a media; os dois limites sao as pontas do intervalo de maior
densidade menos essa media. No `w`, o intervalo vai de -1.18 a -0.66 e a media -0.98
nao esta no meio dele. A frase "68% de volume de posterior em torno da media" descreve
uma coisa (contar volume a partir da media) e o numero impresso e outra (HPD, que nao
usa a media para nada). A media entra so como ponto de referencia para escrever a
diferenca.

## 5. O passo 5: o que eu investiguei quando a D1 falhou

**Primeiro, as outras quatro definicoes pre-registradas.** Nenhuma fecha os dez: D2 e
D4 morrem no `w` e no `sigma_8` LCDM, D5 morre nesses dois mais o `sigma_8` wCDM. O
padrao e claro: toda definicao baseada em quantil produz limites quase simetricos, e o
artigo imprime assimetria de verdade em tres alvos.

**Depois, o HPD.** O HPD cru, procurando o menor intervalo direto na CDF ponderada,
fecha 9 de 10. O unico que falha e o `S_8` do 3x2pt LCDM: eu acho `+0.0157 -0.0198`
contra `+-0.017` impresso, e o limite de baixo fica 0.0028 fora de uma tolerancia de
0.00255. Falha apertada, e suspeita: o posterior de `S_8` nesse caso e quase simetrico,
entao um HPD fortemente assimetrico ali e sinal de ruido, nao de fisica. Com neff de
6.310, a busca do menor intervalo na CDF crua e instavel. Ela escolhe onde o ruido de
amostragem fez a densidade parecer mais alta, e isso enviesa o intervalo para menos que
a largura verdadeira.

**Entao testei o HPD sobre a marginal suavizada (D3s)**, que e o que GetDist e o
ChainConsumer de fato fazem: histograma ponderado de 2.000 bins, convolucao com kernel
gaussiano de largura dada pela regra de Scott sobre o neff, e corte no nivel de
densidade cujo contorno encerra 68% do volume. Isso fecha **10 de 10**, incluindo o
`S_8` LCDM (`+0.0176 -0.0187`) e o `w` (`+0.3280 -0.2053`).

**Teste de que isso nao e ajuste fino da banda.** Variei a banda de 0.5 a 3.0 vezes a
regra de Scott:

```
smooth=0.50   10/10 OK   pior desvio = 0.59 da tolerancia
smooth=0.75   10/10 OK   pior desvio = 0.59
smooth=1.00   10/10 OK   pior desvio = 0.66
smooth=1.50   10/10 OK   pior desvio = 0.84
smooth=2.00    8/10      pior desvio = 1.05   (falha S_8 lcdm, w)
smooth=3.00    5/10      pior desvio = 2.03
```

Qualquer banda entre 0.5 e 1.5 Scott reproduz os dez, e o pior desvio nunca passa de
84% da tolerancia. So suavizacao exagerada (2x ou mais) estraga. Entao o resultado e do
HPD, nao da escolha de banda. Vale notar que o proprio script dos autores configura o
ChainConsumer com `kde=1.5`, dentro dessa faixa.

Conclusao do passo 5: a definicao que reproduz todos os dez e o **intervalo de 68% de
maior densidade da marginal 1D suavizada, com a media como valor central reportado**.
Nao e o que a frase de metodos descreve.

## 6. O script dos autores, `read_chains_y3a2.py`

Sao 35 linhas que leem duas colunas de uma cadeia, montam `S_8` e plotam no
ChainConsumer. Ele **nao faz o que diz fazer**, e nao por pouco.

O script le as colunas por indice fixo, com comentarios afirmando o indice:

```python
om=float(words[0])      # "omegam is the 1st entry on each line"
sigma8=float(words[30]) # "sigma8 is the 31 entry in each line"
w.append(float(words[36]))  # "weight, it is column 37"
```

Conferi os cabecalhos. Nas tres cadeias que baixei, nenhuma das duas ultimas
afirmacoes e verdadeira:

| cadeia | ncol | omega_m | sigma_8 | weight | o que o script pega em 30 / 36 |
|---|---|---|---|---|---|
| chain_3x2pt_lcdm_SR_maglim | 38 | 0 ok | **31** | **37** | `bias_ta` / `post` |
| chain_3x2pt_wcdm_SR_maglim | 39 | 0 ok | **32** | **38** | `alpha2` / `like` |
| chain_all_lcdm | 61 | 0 ok | **54** | **60** | `alpha2` / `planck--ps_a_100_100` |

E o detalhe que fecha o caso: o script nomeia um arquivo especifico,
`chain_2x2pt_wcdm_SR_maglim_NLbias.txt`. Peguei so o cabecalho dele (request de range,
4 KB) e sao 43 colunas, com `omega_m` em 0, `sigma_8` em **36** e `weight` em **42**.
O script esta errado ate no arquivo que ele proprio nomeia, por um deslocamento de
exatamente 6, que e o numero de colunas `b2e_sig8sq_bin*` que a parametrizacao NLbias
acrescentou. A leitura mais simples e que a cadeia foi republicada depois do script e
ninguem reconferiu os indices.

Rodado como esta, o script nao quebra: ele acha 43 campos e le numeros de verdade em 30
e 36. So que plota `bias_lens--b2e_sig8sq_bin4` no lugar de `sigma_8` e pesa tudo com
`sigma_8` no lugar de `weight`. Erro silencioso, que sai como um grafico plausivel.

So a primeira coluna (`omega_m` em 0) e confiavel, e ela e a mesma em todas as cadeias
do diretorio. A pratica que o proprio comentario recomenda ("as described on the first
line") e a certa; o codigo e que nao a segue. Ler pelo cabecalho, como fiz aqui,
resolve.

## O que eu nao consegui verificar

- **O codigo de resumo que o DES usou de fato.** Eu mostro que o HPD suavizado
  reproduz os dez numeros e que nenhuma das cinco leituras literais da frase de metodos
  reproduz. Isso identifica a definicao por eliminacao e por acerto numerico, nao por
  inspecao do codigo. Nao baixei `cosmosis`, `ChainConsumer` nem `getdist` para
  confrontar a implementacao linha a linha.
- **A banda de suavizacao exata.** Sei que qualquer coisa entre 0.5 e 1.5 Scott
  reproduz, e nao consigo separar qual foi usada: a diferenca entre essas bandas fica
  abaixo do ultimo digito impresso.
- **A cadeia "all" nao discrimina definicao nenhuma.** Os limites impressos ali sao
  0.003 a 0.008, e meu piso de tolerancia (0.002) e largo comparado a isso. As seis
  definicoes passam nos tres alvos dessa cadeia. Esses tres alvos confirmam o valor
  central e mais nada; quem decide a definicao sao os sete alvos das cadeias 3x2pt.
- **Se os arquivos publicos sao exatamente as cadeias usadas no artigo.** Assumi que
  sim porque os nomes e os valores centrais batem no terceiro digito. Nao tenho como
  checar isso de fora.
- **Nada alem dos dez alvos encomendados.** Nao recalculei nenhuma outra linha de
  tabela do artigo, nem a tensao com o Planck, nem bondade de ajuste.
- **A versao publicada do artigo.** Trabalhei com os valores de alvo que me foram
  passados; nao abri o PDF para conferir se o texto impresso e exatamente esse.

## Arquivos

```
claims_cego.json / claims_cego.sha256   pre-registro, intocado desde o passo 1
sha256_dados.txt                        hashes dos arquivos baixados
dados/                                  as tres cadeias e o script dos autores
cab_2x2pt.txt                           cabecalho do chain_2x2pt_wcdm_SR_maglim_NLbias
analisa.py                              leitura por cabecalho, estatistica ponderada, D1..D5
passo5.py                               HPD cru vs HPD suavizado
tabela.py / resultados.json             tabela de comparacao e veredito por alvo
robustez.py                             varredura de banda de suavizacao
tabela_saida.txt                        saida bruta da tabela
```
