**Veredito geral: o relatório se sustenta, mas precisa de correções.** O veredito "Partially reproduced" está certo pela regra congelada, e a nota 1 aos autores continua de pé: o artigo não explica a diferença em lugar nenhum. Achei cinco erros que precisam ser corrigidos. Em dois deles o relatório chama de hipótese ou de explicação suficiente uma coisa que os próprios arquivos baixados já resolvem: a primeira confirmo, a segunda derrubo. A nota 4 deve sair.

Os scripts de conferência estão em `E:\Ciencia\noturno\2024-desi-bao-vi\review_scratch\`: `bbn.py`, `offset.py`, `rdh.py` e `run.sh`. Não alterei nada do rerun.

## Achados

**1. must-fix.** Trechos: "Our hypothesis, untested, is that the first class is the full two-dimensional (ω_b, N_eff) BBN likelihood evaluated at N_eff = 3.044 … We did not open the likelihood code; it lives in a NERSC path … that is not in the public release." Também a nota 1 ("Our guess is … but we could not check") e o item de "Not tested" sobre a classe `schoneberg2024`.
- **O problema:** a hipótese pode ser testada com um arquivo que já está na pasta. O `data/official/desi-bao-all_schoneberg2024-bbn/chain.updated.yaml`, nas linhas do bloco `bbn_likelihoods.schoneberg2024`, traz a gaussiana 2D inteira:
  - `quantities: [omegabh2, nnu]`
  - `mean: [0.02196, 3.034]`
  - `cov: [[4.0311226e-07, 7.30390042e-05], [7.30390042e-05, 0.0452831584]]`
- **A conta (meu `bbn.py`):**
  - A condicional em N_eff = 3.044 dá ω_b = **0.0219761 ± 0.0005341**, com ρ = 0.5406. O ajuste de parábola que fiz sobre `chi2__bbn` dá 0.0219761 ± 0.0005341, rms 1.1e-6. A concordância é exata.
  - O `chi2__bbn` no mínimo vale 0.0022, que é exatamente (3.044−3.034)²/0.04528, o termo do N_eff. Isso confirma de novo que é a 2D avaliada em N_eff fixo.
  - A marginal dessa 2D é 0.02196 ± 0.000635, ou seja, a Eq. (2.9).
- **Texto corrigido para a explicação do C3:** "The chain's own `chain.updated.yaml` gives the BBN term as a 2D Gaussian in (ω_b, N_eff) with mean (0.02196, 3.034) and the covariance above, i.e. the ΛCDM+N_eff result of Eq. (2.9). Conditioned at N_eff = 3.044 it gives ω_b = 0.021976 ± 0.000534, exactly what the `chi2__bbn` column shows." Na nota 1, trocar "Our guess is … we could not check" por essa constatação, citando o arquivo. Tirar o item correspondente de "Not tested" e o rótulo de hipótese em "How this report was made".
- **Uma nuance para a nota 1:** o artigo explica uma escolha paralela. Para o θ*, as linhas 801 a 804 dizem que a largura foi aumentada em uns 75% "to accommodate … ΛCDM+N_eff". Para o BBN não há frase equivalente. Além disso, a condicional (σ 0.000534) é mais estreita que a Eq. (2.8) (σ 0.00055). Então não dá para justificar a escolha como "mais conservadora" na largura. O que ela faz é deslocar a média em −0.37σ. Vale perguntar nesses termos.

**2. must-fix.** Trechos: na tabela de resultados, "C1 … (Table 3, Eq. 4.2)" e "C2 … (Eq. 4.3 block / JCAP Eq. 15)". Na nota 4, "printed in the Eq. (4.3) block". No `claims.json`, "Eq. 4.2 group" e "arXiv Eq. 4.3 block".
- **O problema:** Ω_m e r_d h são a **Eq. (4.1)** (paper.txt, linha 1244). A Eq. (4.2) é a métrica de tensão (linha 1354). A Eq. (4.3) é H0 = 69.29 ± 0.87 com DESI + r_d do CMB (linha 1370). A nota aos autores aponta para a equação errada.
- A afirmação de que "JCAP Eq. 15" é a numeração da JCAP não tem fonte. A JCAP também numera por seção. Ou se confirma no PDF da JCAP, ou se tira.
- **Texto corrigido:** "C1 Ω_m, DESI BAO alone (Table 3, Eq. 4.1)" e "C2 r_d h, same fit (Eq. 4.1)".

**3. must-fix.** Trechos: "A uniform rescaling of the published covariance by 0.99397 … would reproduce their χ² exactly" e, na nota 3, "Scaling the published covariance by 0.99397 would reproduce your values." Também o log, que fala em "late covariance update".
- **O problema:** a conta só fecha no ponto de melhor ajuste. Ao longo da posterior, o reescalonamento é refutado. Ele prevê Δχ² = 0.00606·χ², com inclinação +0.006 e piso de 0.0768. Em 600 amostras (meu `offset.py`) medi:
  - diferença de 0.0760, desvio-padrão 0.0105, mínimo **0.0446**, máximo 0.107;
  - inclinação de Δχ² contra o χ² deles: **−0.0005**, correlação −0.10;
  - resíduo depois de aplicar o modelo de 0.99397: desvio de 0.017, pior que o de uma constante (0.0105).
- **Explicação mais simples:** procurei e não achei.
  - Os dois arquivos DR1 do `bao_data` têm um único commit, `75b9557d34` de 2024-04-05. O clone `--depth 1` não escondeu versão nenhuma.
  - A cadeia dos autores não lê esses arquivos. Ela lê `bao_data/desi_gaussian_bao_ALL_GCcomb_{mean,cov}.txt`, sem o "2024_", dentro do pacote interno da NERSC. O relatório não menciona isso, e é o fato mais útil para a pergunta.
  - Arredondar o vetor para 3 ou 4 casas não muda nada (+0.075). Arredondar para 2 casas piora (+0.136).
- **Texto corrigido:** "The offset is flat across the posterior (slope −0.0005 against their χ², sd 0.0105 over 600 samples), so it is not a covariance rescaling, which would scale with χ². Their run reads `desi_gaussian_bao_ALL_GCcomb_*.txt` from the internal package, not the public `desi_2024_*` files; the public files have a single commit (2024-04-05)." Escrever o ± como "sd across samples". Acho que a nota 3 pode cair para um P.S. Não muda nenhum parâmetro.

**4. must-fix (tirar a nota).** Trechos: na nota 4, "That looks like truncation rather than rounding … 101.9 would be the rounded value". Em "Alternative readings", "Printed as 101.8 that is truncation".
- **O problema:** a média cai bem em cima da fronteira de arredondamento e depende do burn-in (meu `rdh.py`):
  - burn-in 0: 101.848, que arredonda para 101.8, o que bate com o `burn_in: 0` da própria cadeia;
  - burn-in 30%: 101.866;
  - burn-in 50%: 101.856;
  - médias por cadeia de 101.81 a 101.90.
- Além disso, o próprio artigo imprime **r_d h = (101.9 ± 1.3) Mpc (ΛCDM)** na Seção 6 (paper.txt, linha 2238). A nota não traz nada novo e não vale o tempo dos autores.
- **Texto corrigido para "Alternative readings":** "The chain mean is 101.85–101.87 depending on burn-in (101.848 with none), on the rounding edge; the paper prints 101.8 in Eq. (4.1) and Sec. 8 and 101.9 in Sec. 6. Not pursued." O `claims.json` do C2 também deixou passar a linha 2238.

**5. must-fix.** Trecho na nota 2: "A note in the VAC README mapping chain directories to the rows of Table 3 would help, since … the directory names do not say which prior each carries."
- **O problema:** já existe a página de documentação do VAC (https://data.desi.lbl.gov/doc/releases/dr1/vac/bao-cosmo-params/, para onde aponta o `README.md` de 160 bytes). Ela descreve as duas variantes:
  - `schoneberg2024-bbn` como "A BBN prior on the baryon density";
  - `-fixed-nnu` como "A more restrictive version … derived by fixing N_eff rather than marginalising over it".
- O que falta na página é o mapa entre pasta e linha da Tabela 3. E o "more restrictive" engana no ΛCDM base: a fixed-nnu (σ 0.00055) é a **mais larga**, já que a padrão dá σ 0.000534.
- **Texto corrigido:** "The VAC documentation page describes the two variants but does not map them to Table 3, and calls `-fixed-nnu` 'more restrictive', although in base ΛCDM it is the wider of the two (σ 0.00055 vs 0.000534)."
- Dá para juntar a nota 2 com a nota 1.

**6. minor.** Trecho: "The release also ships a sibling … And it gives H0 = 68.669 ± 0.806."
- **O problema:** o valor sai só de 2 das 4 cadeias. Está no `diagnose_sibling.log` ("2 of 4 chains") e no `check_sibling.sh`, que baixa só `chain.1` e `chain.2`. Também é sensível ao burn-in: com todas as linhas dá 68.651 ± 0.816.
- A conclusão não muda, mas a concordância "0.027σ" vira algo entre 0.03σ e 0.05σ.
- **Texto corrigido:** "H0 = 68.669 ± 0.806 (chains 1–2 of 4, 30% burn-in; 68.651 with no burn-in)."

**7. minor.** Trecho: na tabela de ω_b, "−0.0044 (−0.006σ)" e "to 0.006σ and 0.027σ".
- **O problema:** −0.00438/0.8 = −0.0055, que dá −0.005σ. O −0.006 do `variant_bbn.json` é o desvio contra o número impresso, 68.53, e não contra a cadeia.
- **Texto corrigido:** "−0.0044 (−0.005σ)".

**8. minor.** Trecho, na tabela de checagens: "Our D_M against CAMB's own (1+z)D_A | identical".
- **O problema:** a checagem é tautológica. O `probe.py` (linhas 75 a 77) compara duas saídas do próprio CAMB, e o nosso código não tem integral própria de distância. Ela não descarta nenhum bug nosso. A checagem (b) do `claims.json` ("our distance integrals") ficou vazia.
- **Texto corrigido:** "CAMB comoving distance vs CAMB (1+z)D_A, flat-space identity (consistency of how we call CAMB, not an independent check)".

**9. minor.** O campo `"frozen_at": "2026-11-08T21:05:00Z"` do `claims.json` não bate com o horário real.
- O `claims.json` foi gravado às 21:02:18 −03:00, o que equivale a 00:02Z do dia 09.
- O relatório cita 21:02:22, que é o horário do `claims.sha256`, e está certo.
- A linha do tempo prova o congelamento antes de qualquer cálculo: o venv só ficou pronto às 21:04:21 e o primeiro log é das 21:05:49. Vale citar isso, porque é uma evidência mais forte que o mtime e mostra que nada podia rodar antes do congelamento.
- Nota técnica: o hash não está ancorado fora da máquina.

**10. minor.** Trecho: "`runs/scripts/` — every script, 10 files".
- **O problema:** são 15 arquivos: 10 `.py`, 4 `.sh` e 1 `.yaml`.
- Dois detalhes da triagem: o r_d h da Seção 8 está na linha 2632, não 2631. O `claims.json` diz que não haveria MCMC do cobaya, e houve um, como checagem extra. Isso está declarado no relatório, mas não diz que foi um acréscimo ao que estava congelado.
- Os autores usaram cobaya 3.4.1 (no yaml), não 3.5.

## O que conferi e está correto

- **Hash:** o SHA-256 do `claims.json` bate com o `claims.sha256`. A linha do tempo é congelamento às 21:02:18, depois venv às 21:04, `probe` às 21:05 e `fit` às 21:07 a 21:12.
- **Faixas e conta do C3:** recalculei a partir do `claims.json`. As faixas são [0.292, 0.298]/[0.0135, 0.0165], [101.54, 102.06]/[1.17, 1.43] e [68.37, 68.69]/[0.72, 0.88]. Para o C3: 0.16124/0.8 = 0.2016σ, passando da borda por 0.00124, que dá 0.0015σ. As larguras ficam −2.5%, −2.5% e +1.6%.
- **Veredito:** "Partially reproduced" é o rótulo certo pela regra congelada.
- **A nota 1 é nova:**
  - o artigo inteiro (v3, de 4 de novembro de 2024) não diz que o resultado DESI+BBN no ΛCDM usa a 2D condicionada; a Seção 2.4.1 diz que adota a Eq. (2.8) para o ΛCDM;
  - o artigo do DR2 (2503.14738, §IV.1) só diz "As in DR1" e reimprime 0.02218 ± 0.00055;
  - a página do VAC não explica;
  - não há issue sobre isso no `CobayaSampler/bao_data` (só a #7, do DR2) nem no `cobaya`.
- **Rederivei do arquivo de cadeia** com os meus scripts: 0.021976 ± 0.000534 para a cadeia BBN, 0.022180 ± 0.000550 para a fixed-nnu, e a marginal de ω_b em 0.021979 ± 0.000533. O H0 da cadeia dá 68.530 ± 0.805, contra 68.527 ± 0.808 sem burn-in.
- **Números do relatório contra os logs:** todos os outros batem (`fit`, `crosscheck`, `diagnose_*`, `chi2_*`, `variant_bbn`, `analyse_chains`):
  - χ² 12.751088 contra 12.751089;
  - r_drag −9.6e-6;
  - AccuracyBoost estável a 1.4e-7;
  - spline 4.0e-6;
  - massa nas bordas;
  - grade 12.73770 contra 12.73826;
  - sensibilidade a h;
  - −0.024σ e +0.022σ contra a cadeia só de BAO;
  - MCMC com R−1 de 0.00038 e ESS entre 6279 e 6770, +0.0111, o que dá +0.014σ;
  - CPU de 1826 s, 5:21 de relógio, pico de 2.97 GB de memória.
- **Vetor de dados:** confere com a Tabela 1 (linhas 577 a 583), inclusive os erros e o ρ que conferi à mão em LRG1 e Lyα.
- **Nota 5:** procede. `base/desi-bao-all/` não tem `chain.input.yaml`, e as outras duas pastas têm. É de pouco valor e pode virar P.S.
- **`dark_energy_model: ppf`** não muda nada, e as colunas de χ² são idênticas bit a bit.

Fontes externas: [VAC docs](https://data.desi.lbl.gov/doc/releases/dr1/vac/bao-cosmo-params/), [VAC README](https://data.desi.lbl.gov/public/dr1/vac/dr1/bao-cosmo-params/v1.0/README.md), [DESI DR2 II](https://arxiv.org/html/2503.14738v3).
