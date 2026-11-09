**Veredito: sound with corrections.** Não achei blocker. A inferência de gamma = 13/3 para `curn_hd.core` se sustenta. Mas a frase central da caveat 2 e da Nota 1 está errada: a cadeia da manchete está no histórico git do repo GitHub. Lida de lá, ela dá exatamente os números do paper. Então o relatório precisa de uma rodada de correção antes da reconta cega.

**Aviso de processo (meu, não do rerun).** Um `git show --stat 98a4783` que rodei para ver o commit fez lazy fetch de 219 MB para dentro de `sources/repo/.git/objects`: `pack-dd43f30c...` (23:40:47) e `pack-b5504016...` (23:40:49). Nenhum arquivo rastreado, log ou output do rerun mudou (`git status` limpo). Como os blobs já estavam locais, extraí 4 deles para `E:\Ciencia\noturno\2023-agazie-nanograv15\review_scratch\blobs\` (44 MB) com `GIT_NO_LAZY_FETCH=1`, sem novo download. Você decide se apaga os dois packs. Meus scripts e logs estão em `E:\Ciencia\noturno\2023-agazie-nanograv15\review_scratch\` (r1 a r4), rodados com 4 threads e nice 19.

## Achados

**1. must-fix: a cadeia da manchete está no GitHub, no histórico.**
- Texto do REPORT (linha 18): "The chain behind the paper's headline number is not on GitHub." Repete na linha 7, no "only on Google Drive" da linha 80 e na linha 33.
- O que está errado: o commit `9943979` (2024-02-08) adicionou `data_release/figure_1/figure1_data/`, e o `98a4783` (2024-02-11, "remove figure 1 data", junto com o PR #3) tirou a pasta. O blob `4923521a` é o `nano15_hd_chain_fg_long_050523.npy` (188.963 amostras). No mesmo commit estão `nano15_hd_chain_long_050523.npy`, `14f_PL_hd_crn.core` e `30fCP_30fiRN_3A_freespec_chain.core`.
- Evidência: `review_scratch/r1.log`. Lida pelo método do pré-registro, essa cadeia dá p05/p50/p95 = 1,8152 / 2,4039 / 3,0689 e-15, igual ao output guardado pelos autores e dentro de todas as bandas de C1. A cadeia vg dá 6,385e-15 e gamma 3,248, também igual.
- Texto corrigido: "The chain behind the headline number was in the GitHub repository from 9943979 (2024-02-08) to 98a4783 (2024-02-11) and is still in its git history (blob 4923521a). It is now distributed through Google Drive. Read from the history blob, it gives 2.4039 / 1.8152 / 3.0689 e-15." Na Nota 1, trocar a premissa por: "The Fig. 1 chains were removed from the repo in 98a4783 and now live only on Drive and in git history; a versioned archive would make them easy to find."
- O rerun deve calcular C1 desse blob, que é a fonte nomeada, e usar como C1 do veredito. O `curn_hd` vira extra.

**2. must-fix: a fonte de C1 foi escolhida depois do freeze, e o veredito depende disso.**
- Texto do REPORT (linha 19): "so it passes the rule we pre-registered for C1".
- O que está errado:
  - O `claims.json` (`pre_freeze_findings`) classificava `curn_hd` como "varied gamma".
  - A regra pede "an HD model". `curn_hd` é um product-space CURN+HD, e pegar o ramo HD é uma leitura feita depois do freeze.
  - Pela `verdict_rule`, sem core qualificado o veredito seria "Partially reproduced / headline not tested".
  - O pass é frágil. O p05 = 1,8788e-15 fica 0,021e-15 abaixo do teto 1,9e-15, e o erro de Monte Carlo do p05 por batch means é 0,027 a 0,034e-15 (`review_scratch/r4.log`). Ou seja, menos de 1 sigma da borda.
- Texto corrigido para a linha 19: "The pre-registration listed curn_hd as varied-gamma. Reading its HD branch as an hd13/3 chain is a post-freeze interpretation of the rule; the p05 lands within one Monte Carlo standard error (~0.03e-15) of the band edge." Com o achado 1 aplicado, o veredito "Reproduced" fica limpo.

**3. minor: a inferência de 13/3 está certa, mas o argumento escrito é fraco.**
- Texto do REPORT (linha 50): "The core has no gamma column, though, so it is a fixed-gamma run." E na linha 19: "the CURN branch matches the authors' CURN 13/3 maximum-likelihood amplitude".
- Evidências mais fortes que o relatório não usa:
  - O core tem as 141 colunas: 134 de pulsar, mais `chain_accept` e `pt_chain_accept`. Nada foi cortado.
  - No ee 3.0.3 o parâmetro se chama `gw_{orf}`, e gamma fixo vira `parameter.Constant`, que não entra em `params` (`blocks.py`, `gamma_val` vira `Constant`). Por isso não há coluna de gamma.
  - O p95 do ramo HD (3,15e-15) fica abaixo do p05 do core vg (3,78e-15). Um gamma variado não salvo fica descartado.
  - KS do ramo HD contra a cadeia fg longa: D = 0,069. Com cerca de 210 amostras efetivas, as duas não se distinguem.
- O ponto de ML (-14,673) cai no percentil 5,2 do ramo CURN (`r1.log`), quase na borda. "Matches" é forte demais.
- Texto corrigido: "falls at the 5th percentile of that branch, consistent with fixed gamma (a varied-gamma CURN sits at log10 A ~ -14.17)".

**4. minor: a citação do default de gamma não está no log citado.**
- Texto do REPORT (linha 50): "defaults to `gamma_common=None` ... (`logs/check_ee_and_hash.log`)".
- O log só mostra `1:793:def model_general(`. O `grep -A 12` para antes da linha 811, e o grep em `blocks.py` não imprimiu nada.
- O fato é verdadeiro: `env/ee_src/enterprise_extensions/models.py` tem `gamma_common=None` na linha 811 e passa como `gamma_val` na linha 1080.
- Texto corrigido: citar `env/ee_src/enterprise_extensions/models.py:811,1080`, ou refazer o grep e guardar o log.

**5. must-fix: S3 entra como pass de uma afirmação que o próprio relatório diz não ter medido.**
- Texto do REPORT: na tabela, "S3 ... | yes, but see the note below". Na linha 7: "all four computable secondary claims land inside the bands".
- O raciocínio do rótulo está certo: o 202 é hd13/3 vs curn13/3, e o S3b (TI, gamma variado, `ti_sample.py` com `model_2a`/`model_3a`, pasta "varied_gamma") é o teste real do HD_gamma/CURN_gamma.
- Mas aí S3 não testa a S3 pré-registrada. Ele é evidência para a S5 ("similar").
- A banda [156, 296] continua com sentido, porque é o intervalo do paper e não depende do nosso erro.
- O erro corrigido não é "roughly 5x". Pela autocorrelação, sai cerca de ±18; por batch means, de 23 a 25 (`review_scratch/r2.log`). Isso dá 5 a 7 vezes o 3,39.
- Texto corrigido: "S3 as pre-registered is not tested: curn_hd is a fixed-gamma run. Its 202 (±~20 accounting for autocorrelation) is an hd13/3 vs curn13/3 Bayes factor and supports S5 ('similar'). Three of the computable secondaries (S1, S2, S3b) land inside their bands."

**6. minor: as bandas não eram cegas para a maioria das secundárias.**
- Texto do REPORT (linhas 7 e 23): "land inside the bands fixed before any core was read".
- O que já se sabia antes do freeze, pelos outputs guardados dos autores (estão no próprio `claims.json`):
  - S1: 12,1139.
  - S2: dá para derivar do lnZ da célula 39, (7973032,854 - 7972999,679)/ln 10 = 14,41.
  - S3: 202,22.
  - S3b: 198,0.
  - E1: gamma 3,2492 (`nbdump_tutorials_parameter_est.txt`, linha 391).
  - E4: 7,85e-4.
- Só C1 no `curn_hd`, E2 e E3 eram desconhecidos.
- A banda de gamma do E1, [3,15, 3,25], não segue a regra que ela declara (daria [3,1, 3,3]), e o teto fica 0,0008 acima do valor já conhecido.
- Não vejo vazamento em C1: as bandas são os dígitos do paper ±0,1e-15, e os resultados ficam perto das bordas, não centrados.
- Texto corrigido: "Bands come from the paper's digits. For S1, S2, S3, S3b, E1 and E4 the authors' stored outputs were known before the freeze, so those are checks of the post-processing, not blind tests."

**7. minor: o relato do fetch antes do freeze está incompleto.**
- Texto do REPORT (linha 67): "a presence check (`scripts/cores_missing.sh`, `git cat-file -e`) lazily fetched the 8 core blobs".
- Pelos timestamps dos packs, `curn_14f_pl_vg` (23:24:59) e `curn_hd` (23:25:01) vieram pelo `git ls-tree -r -l` do `clone_sparse.sh`. Ele continuou rodando depois da última escrita do log (23:22:46) até o tmp_pack abortado às 23:25:03. Isso foi antes de o `cores_missing.sh` existir (23:25:22).
- Os outros 6 vieram entre 23:25:27 e 23:25:51.
- Nenhum log anterior ao freeze lê conteúdo de core.
- Texto corrigido: "Two core blobs were fetched by the `ls-tree -l` in clone_sparse.sh before it was stopped, and six by cores_missing.sh. None was decoded."

**8. must-fix (Nota 5): falta a discrepância concreta.**
- Texto do REPORT: "`pshift_bfs.npy` holds 5,097 values, while the text says 5,000 ... which the paper rounds to 10^-3".
- O paper (Sec. 3, `paper.txt` linhas 660-661) diz "exceed the observed value in five of the 5,000 phase shifts".
- O arquivo tem 4 de 5.097 acima de 226 (também 4 com ≥ 200). São 5 contra 4, e 5.000 contra 5.097.
- "Fig. 2's ±70 looks like it already accounts for that" é especulação. O App. B diz que usam bootstrap mais as técnicas de Markov-model de Cornish & Littenberg 2015 e Heck et al. 2019, e dá para citar isso.
- Texto corrigido: "The text says five of 5,000 phase shifts exceed the observed BF; the posted file has 5,097 values and 4 above 226. Is the file a different set?"

**9. minor (Nota 4): a leitura de unidade está certa, um detalhe está errado.**
- A leitura de log10 rho em [-9, -4] está certa: a Tabela 1 dá ρ_i[s²] log-Uniform[-18, -8], e o próprio `upper_left.ipynb` dos autores usa `rho_bins = np.linspace(-9, -4)`. Vale citar isso no lugar de "which we read as".
- Errado: "`log10_rho` samples reach -15.50 in every bin". Pelo `fs_range.log`, o mínimo do bin 2 é -14,97 e o do bin 3 é -15,19.
- O teto -11 do `gw_hd_log10_A` é o default do ee (`Uniform(-18, -11)`). Vale dizer isso.
- Texto corrigido: "reach about -15.5 in most bins (bins 2 and 3: -14.97, -15.19)".

**10. minor: o relatório se contradiz e tem números sem log.**
- A caveat 1 diz "covers the cores too", e a Nota 3 diz "ambiguous". A leitura literal está certa; é melhor escolher uma das duas palavras.
- Sem log: "about 1.1 GB: 720 MB of repo ... 351 MB of env" (o `check_ee_and_hash.log` só tem `ls /`). O 351 MB bate com o meu `du`; o 720 MB é plausível antes do meu fetch.
- O log da primeira rodada, que travou, não foi guardado. A versão do `compute_claims.py` com [-9, -4] também não: o .py foi editado 0,1 s depois do rename do log.
- "6 BLAS threads at most": o `fs_range.sh` não define limite de threads.

**11. Novidade das notas.** As issues #1, #2 e #4, os PRs #3 e #5 e o `known_issues.md` não cobrem nenhuma das cinco notas. A Nota 2 é nova e útil. A Nota 1 precisa ser reescrita (achado 1). As Notas 4 e 5 servem depois das correções.

## O que conferi e está certo

- `claims.json` com sha256 80d24441...c98acb, igual ao `claims.sha256`. O freeze foi às 23:29:19; o checkout dos cores, às 23:29:41.
- Todos os números das tabelas de C1, S1 a S3b e E1 a E4, as lnZ, tau 28,8 e 23,1, neff 210, a sensibilidade com burn = 0 e as diferenças 0,038 e 0,078 batem com `runs/compute_claims.log` e `runs/results.json`.
- O E2 só muda no 8º dígito entre [-9, -4] e [-15,5, -4], o que é esperado: a densidade é renormalizada por bin.
- O mapeamento rho(A) do E2 bate com o `free_spectrum`/`powerlaw` do enterprise.
- O TI usa as funções dos autores sem alteração (`git status` limpo). A troca de `extra_functions.rng` é fiel, porque `bootstrap()` lê o global na hora da chamada. As fórmulas de log10 BF e sigma reproduzem o `bfacs.log10_bf` (12,1139 ± 0,0853 com as lnZ dos autores). `simpson(y, x)` aceita x posicional no scipy 1.15.3.
- Os valores do paper conferem: 2,4 +0,7/-0,6; 6,4 +4,2/-2,7; 3,2 ± 0,6; 12,1 ± 0,1; 226 ± 70; 965; o limite das Tabelas 1 de [-18, -14] para 13/3.
- A citação do README está correta. O core vg é outra cadeia, diferente da Fig. 1b (6,329 contra 6,385, confirmado pela cadeia longa).
- O peso 300 vai para o modelo 0, que é o CURN, então BF = N_HD/N_CURN × 300 está certo.
