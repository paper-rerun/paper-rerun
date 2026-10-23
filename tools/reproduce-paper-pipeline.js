export const meta = {
  name: 'reproduce-paper-pipeline',
  description: 'Reproduce one paper by claim blocks: claims map, check, frozen env, per-block execution, blind verification, report, adversarial review',
  phases: [
    { title: 'Claims', detail: 'map verifiable claims and fix definitions before running; second agent checks against the paper' },
    { title: 'Env', detail: 'build and freeze the environment once' },
    { title: 'Run', detail: 'one agent per claim block, GPU in a queue' },
    { title: 'Verify', detail: 'blind recomputation from the lockfile with metric rewritten from scratch' },
    { title: 'Report', detail: 'write REPORT.md text' },
    { title: 'Review', detail: 'adversarial review of the report' },
  ],
}

const P = args
const ROOT = P.root          // Windows path
const WROOT = P.wroot        // WSL path
const COMMON = `
You are one stage of a multi-agent reproduction pipeline for a volunteer project that checks whether published computational results hold.
Paper: ${P.paper}
Code: ${P.repo}
Working folder (Windows): ${ROOT}   (WSL: ${WROOT}). Stay inside it; never write outside it (check that variables in paths expand before running mkdir/cp).
Rules:
- Read E:\\Ciencia\\README.md for project rules. Do NOT open ${P.offlimits} or any other folder under E:\\Ciencia\\artigos: that is an earlier independent attempt and this run must stay independent of it.
- Machine: Ryzen 9 3900X, WSL2 Ubuntu 24.04 (31 GB RAM, passwordless sudo, uv at ~/.local/bin/uv), RTX 2070 SUPER 8 GB. Work in WSL: wsl -d Ubuntu -- bash -lc "...".
- Every GPU command runs under: flock /mnt/e/Ciencia/.gpu.lock <cmd>. Set MPLBACKEND=Agg; never open windows.
- Long commands: run_in_background and wait for the notification; do not poll in tight loops.
- Never change the authors' method or hyperparameters to make numbers match. Only environment, dependencies, paths, obvious crashes.
- If the same failure survives 3 different fix attempts, stop and report it.
- Publish nothing (no issues, PRs, pushes, uploads).
`

const DEF = { type: 'object', properties: {
  name: { type: 'string' }, value: { type: 'string' }, source_quote: { type: 'string' }, ambiguity_note: { type: 'string' } },
  required: ['name', 'value', 'source_quote', 'ambiguity_note'] }
const CLAIM = { type: 'object', properties: {
  id: { type: 'string' }, block: { type: 'string' }, text: { type: 'string' },
  paper_value: { type: 'number' }, unit: { type: 'string' }, location: { type: 'string' },
  tolerance: { type: 'number' }, tolerance_basis: { type: 'string' }, conditions: { type: 'string' } },
  required: ['id', 'block', 'text', 'paper_value', 'unit', 'location', 'tolerance', 'tolerance_basis', 'conditions'] }
const CLAIMS = { type: 'object', properties: {
  sources_read: { type: 'array', items: { type: 'string' } },
  definitions: { type: 'array', items: DEF },
  claims: { type: 'array', items: CLAIM },
  issues: { type: 'array', items: { type: 'string' } } },
  required: ['sources_read', 'definitions', 'claims', 'issues'] }
const ENV = { type: 'object', properties: {
  repo_commit: { type: 'string' }, lockfile_path: { type: 'string' }, setup_script: { type: 'string' },
  activate_cmd: { type: 'string' }, weights: { type: 'string' }, data_paths: { type: 'string' }, notes: { type: 'string' } },
  required: ['repo_commit', 'lockfile_path', 'setup_script', 'activate_cmd', 'weights', 'data_paths', 'notes'] }
const RES = { type: 'object', properties: {
  results: { type: 'array', items: { type: 'object', properties: {
    claim_id: { type: 'string' }, value: { type: 'number' }, n: { type: 'number' }, command: { type: 'string' }, output_path: { type: 'string' } },
    required: ['claim_id', 'value', 'n', 'command', 'output_path'] } },
  problems: { type: 'array', items: { type: 'string' } },
  extra_analyses: { type: 'array', items: { type: 'string' } } },
  required: ['results', 'problems', 'extra_analyses'] }
const REVIEW = { type: 'object', properties: {
  issues: { type: 'array', items: { type: 'object', properties: {
    severity: { type: 'string', enum: ['blocker', 'major', 'minor'] }, where: { type: 'string' }, problem: { type: 'string' }, fix: { type: 'string' } },
    required: ['severity', 'where', 'problem', 'fix'] } } },
  required: ['issues'] }

// CLAIMS
phase('Claims')
const draft = await agent(`${COMMON}
STAGE: claims map. Read the paper itself (open-access full text and supplementary information; ${P.paperHint}) and write the list of verifiable numeric claims for this target: ${P.target}.
For each claim: id, block (group claims that share one computation, e.g. one test split), exact paper value, unit, where it is (figure/table/page), tolerance and its basis (seed variability the paper reports, rounding, figure-reading precision), and conditions (model, checkpoint, number of samples, temperature, test set).
CRUCIAL: fix every definition the computation needs BEFORE anyone runs anything (which residues count, what counts as the ligand / context atoms, distance cutoff, which atoms, which chain, how recovery is averaged: per-protein median or pooled, which test-set id lists). Quote the paper text for each. Where the paper is ambiguous, pick the most literal reading of the paper text, record the ambiguity in ambiguity_note, and do not pick based on expected results. Do not run any model.
Save the result as ${ROOT}\\claims.json too if you can; your structured return is what counts.`, { label: 'claims-map', schema: CLAIMS })

const claims = await agent(`${COMMON}
STAGE: independent check of a claims map. Another agent extracted the claims below. Open the paper and SI yourself and check every number, location, unit, condition and definition against the source text. Fix anything wrong, add any target claim it missed, and list each change in issues. Keep the definitions literal to the paper text: do not change a definition to one you expect to "work better". Return the full corrected map.
MAP:
${JSON.stringify(draft)}`, { label: 'claims-check', schema: CLAIMS, effort: 'high' })
log(`claims: ${claims.claims.length}, definitions: ${claims.definitions.length}, check issues: ${claims.issues.length}`)

// ENV
phase('Env')
const env = await agent(`${COMMON}
STAGE: environment. Clone the authors' repo into ${WROOT}/repo, build one environment under ${WROOT}/env and freeze it (lockfile + setup script that rebuilds it from scratch + an activate command that also sets MPLBACKEND=Agg). Start from the versions the authors used (their requirements, env files, commit dates) before trying latest versions. Download the released weights and the test-set structures/data the claims need into ${WROOT}/data. Run the repo's smallest example on the GPU once to prove it works.
Claims (for knowing what data is needed): ${JSON.stringify(claims.claims.map(c => ({ id: c.id, block: c.block, conditions: c.conditions })))}
Definitions: ${JSON.stringify(claims.definitions)}`, { label: 'env', schema: ENV })

// RUN + VERIFY
const blocks = [...new Set(claims.claims.map(c => c.block))]
log(`blocks: ${blocks.join(', ')}`)

const runOne = b => agent(`${COMMON}
STAGE: execution of block "${b}". Use the frozen environment (${env.activate_cmd}; setup in ${env.setup_script}; weights ${env.weights}; data ${env.data_paths}). Do not reinstall or upgrade packages.
Compute exactly these claims, using exactly the fixed definitions (no alternatives in the main result):
CLAIMS: ${JSON.stringify(claims.claims.filter(c => c.block === b))}
DEFINITIONS: ${JSON.stringify(claims.definitions)}
Write outputs under ${WROOT}/exec/${b}/ (raw model outputs, your scoring script, logs). If you believe a definition is wrong, you may run an alternative AFTER the main result and report it only in extra_analyses, with numbers.`, { label: `run:${b}`, phase: 'Run', schema: RES })

const verifyAll = () => agent(`${COMMON}
STAGE: blind verification. You must NOT read anything under ${WROOT}/exec/ (another agent's results) until you have returned. Rebuild the environment from scratch in ${WROOT}/verify/env using only the lockfile ${env.lockfile_path} and setup script ${env.setup_script} (copy and adapt paths; record any difference). Reuse the downloaded weights/data in ${env.data_paths} read-only.
Then recompute every claim below. Write the scoring/metric code yourself from the definitions below, from scratch; do not use the authors' evaluation scripts for the metric (use their inference code to generate sequences, that's the method). Output under ${WROOT}/verify/.
CLAIMS: ${JSON.stringify(claims.claims)}
DEFINITIONS: ${JSON.stringify(claims.definitions)}`, { label: 'verify-blind', phase: 'Verify', schema: RES, effort: 'high' })

const [execs, ver] = await Promise.all([
  pipeline(blocks, (b) => runOne(b)),
  verifyAll(),
])
const execResults = execs.filter(Boolean).flatMap(r => r.results)
const verResults = ver ? ver.results : []

// Compare in code
const table = claims.claims.map(c => {
  const e = execResults.find(r => r.claim_id === c.id)
  const v = verResults.find(r => r.claim_id === c.id)
  const okPaper = e ? Math.abs(e.value - c.paper_value) <= c.tolerance : false
  const okBlind = e && v ? Math.abs(e.value - v.value) <= c.tolerance : false
  return { id: c.id, block: c.block, paper: c.paper_value, tol: c.tolerance, exec: e ? e.value : null, blind: v ? v.value : null, matches_paper: okPaper, blind_agrees: okBlind }
})
log(`matches paper: ${table.filter(t => t.matches_paper).length}/${table.length}; blind agrees: ${table.filter(t => t.blind_agrees).length}/${table.length}`)

// REPORT
phase('Report')
const evidence = JSON.stringify({ claims, env, exec: execs, blind: ver, table })
const report = await agent(`${COMMON}
STAGE: report. Write the full REPORT.md text in English following the template in E:\\Ciencia\\README.md. Return ONLY the markdown text; do not write files.
Verdict rules: Reproduced only if every claim matches the paper within tolerance AND the blind verification agrees. Partially reproduced if some do. Not reproduced if the main claims don't. Alternatives from extra_analyses go in a separate section and never change the verdict. List every definition with its paper quote and ambiguity note. Include a "Pipeline" section: claims map + independent check, frozen env, per-block execution, blind recomputation with independently written metric, adversarial review.
EVIDENCE: ${evidence}`, { label: 'report', phase: 'Report' })

phase('Review')
const review = await agent(`${COMMON}
STAGE: adversarial review. Your job is to find what is wrong with this reproduction report. Check against the paper and the evidence: paper numbers copied wrong, tolerances misapplied, verdict stronger than the evidence, definitions changed after seeing results, method changes hidden as "environment fixes", blind verification that was not actually blind or independent, missing caveats. You may open the paper and the files under ${ROOT}. Default to flagging when unsure, but every issue needs a concrete fix.
REPORT:
${report}
EVIDENCE: ${evidence}`, { label: 'review', phase: 'Review', schema: REVIEW, effort: 'high' })

return { table, claims, env, exec: execs, blind: ver, report, review }