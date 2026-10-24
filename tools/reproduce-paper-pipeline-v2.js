export const meta = {
  name: 'reproduce-paper-pipeline-v2',
  description: 'Reproduce one paper by claim blocks: claims map + check, frozen env, sequential execution, blind recomputation, report, adversarial review, revision',
  phases: [
    { title: 'Claims', detail: 'map verifiable claims and fix definitions before running; second agent checks against the paper' },
    { title: 'Env', detail: 'build and freeze the environment once' },
    { title: 'Run', detail: 'one agent per claim block, one block at a time' },
    { title: 'Verify', detail: 'blind recomputation after execution, pre-registered metric first' },
    { title: 'Report', detail: 'write REPORT.md text' },
    { title: 'Review', detail: 'adversarial review of the report' },
    { title: 'Revise', detail: 'fix every review point against the files' },
  ],
}

const P = args
const ROOT = P.root
const WROOT = P.wroot
const COMMON = `
You are one stage of a multi-agent reproduction pipeline for a volunteer project that checks whether published computational results hold.
Paper: ${P.paper}
Code: ${P.repo}
Working folder (Windows): ${ROOT}   (WSL: ${WROOT}). Stay inside it.
Rules:
- Read E:\\Ciencia\\README.md for project rules. Do NOT open anything under E:\\Ciencia\\artigos, E:\\Ciencia\\pipeline\\ (except your own working folder), or ${P.offlimits}: those are other, independent attempts.
- Machine: Ryzen 9 3900X, WSL2 Ubuntu 24.04 (31 GB RAM, passwordless sudo, uv at ~/.local/bin/uv), RTX 2070 SUPER 8 GB. Work in WSL.
- IMPORTANT shell gotcha: this harness expands $VAR and $(...) inside single-quoted 'wsl -d Ubuntu -- bash -lc "..."' commands BEFORE WSL sees them, so variables come back empty (that once created folders in the WSL root). Put any command that uses variables into a .sh file inside the working folder and run that file.
- Every GPU command runs under: flock /mnt/e/Ciencia/.gpu.lock <cmd>. Set MPLBACKEND=Agg; never open windows.
- Make long runs restartable (write per-item results as you go) and run them with run_in_background; wait for the notification instead of polling.
- Never change the authors' method or hyperparameters to make numbers match. Only environment, dependencies, paths, obvious crashes.
- If the same failure survives 3 different fix attempts, stop and report it.
- Publish nothing (no issues, PRs, pushes, uploads).
Paper-specific notes from triage: ${P.triage}
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

phase('Claims')
const draft = await agent(`${COMMON}
STAGE: claims map. Read the paper itself (full text and supplementary information) and write the list of verifiable numeric claims for this target: ${P.target}.
For each claim: id, block (group claims that share one computation), exact paper value, unit, location (figure/table/page), tolerance and its basis, and conditions (model, checkpoint, samples, test set).
CRUCIAL: fix every definition the computation needs BEFORE anything runs, quoting the paper. Where the paper is ambiguous, pick the most literal reading of the text and record the ambiguity; never pick based on expected results.
If the authors publish per-item results (source data, per-assay or per-structure tables), download them into ${WROOT}/sources/ and use them: check which definition their per-item values imply, and set each tolerance from the statistic's own resolution (e.g. bootstrap of the authors' per-item values) when the paper gives none. Record both in the claims.
Do not run any model. Save ${ROOT}\\claims.json if you can; your structured return is what counts.`, { label: 'claims-map', schema: CLAIMS })

const claims = await agent(`${COMMON}
STAGE: independent check of a claims map. Open the paper, SI and any authors' per-item data yourself and check every number, location, unit, condition, tolerance and definition against the sources. Fix anything wrong, add missed target claims, list each change in issues. Keep definitions literal to the paper text unless the authors' own per-item data contradicts it, in which case say so explicitly. Return the full corrected map.
MAP:
${JSON.stringify(draft)}`, { label: 'claims-check', schema: CLAIMS, effort: 'high' })
log(`claims: ${claims.claims.length}, definitions: ${claims.definitions.length}, check issues: ${claims.issues.length}`)

phase('Env')
const env = await agent(`${COMMON}
STAGE: environment. Clone the authors' repo into ${WROOT}/repo, build one environment under ${WROOT}/env and freeze it (lockfile + setup script that rebuilds from scratch + activate command that sets MPLBACKEND=Agg). Start from the versions the authors used (requirements, env files, commit dates) before trying latest. Download released weights and the test data the claims need into ${WROOT}/data. Run the smallest example on the GPU once.
Claims: ${JSON.stringify(claims.claims.map(c => ({ id: c.id, block: c.block, conditions: c.conditions })))}
Definitions: ${JSON.stringify(claims.definitions)}`, { label: 'env', schema: ENV })

// One block at a time: in v1, four agents queueing on the GPU lock got runs killed
phase('Run')
const blocks = [...new Set(claims.claims.map(c => c.block))]
const execs = []
for (const b of blocks) {
  const r = await agent(`${COMMON}
STAGE: execution of block "${b}". Use the frozen environment (${env.activate_cmd}; setup ${env.setup_script}; weights ${env.weights}; data ${env.data_paths}). Do not reinstall or upgrade packages.
Compute exactly these claims with exactly the fixed definitions, on the FULL test set (no sampling at this stage, however long it takes):
CLAIMS: ${JSON.stringify(claims.claims.filter(c => c.block === b))}
DEFINITIONS: ${JSON.stringify(claims.definitions)}
Write outputs under ${WROOT}/exec/${b}/. Alternatives you think matter go AFTER the main result, in extra_analyses, with numbers.`, { label: `run:${b}`, phase: 'Run', schema: RES })
  execs.push(r)
}
const execResults = execs.filter(Boolean).flatMap(r => r.results)

// Blind runs after execution so it cannot see the other stage's processes
const ver = await agent(`${COMMON}
STAGE: blind verification. Do NOT read anything under ${WROOT}/exec/. Rebuild the environment from scratch in ${WROOT}/verify/env from the lockfile ${env.lockfile_path} and setup script ${env.setup_script}. Reuse the downloaded weights/data in ${env.data_paths} read-only.
Recompute every claim below with your own seeds and metric code written from scratch from the definitions (use the authors' inference code to generate predictions; that is the method).
If recomputing every claim in full would take more than ~4 h of GPU, you may recompute a random sample of items for the most expensive claims; draw it with a fixed seed and save it BEFORE computing anything, and say so in problems. (Only this blind stage may sample; execution stages compute in full.)
FIRST compute exactly the pre-registered definitions below and report those values in results. Only after that, if you think a definition is wrong, compute alternatives and put them in extra_analyses.
Output under ${WROOT}/verify/.
CLAIMS: ${JSON.stringify(claims.claims)}
DEFINITIONS: ${JSON.stringify(claims.definitions)}`, { label: 'verify-blind', phase: 'Verify', schema: RES, effort: 'high' })
const verResults = ver ? ver.results : []

const table = claims.claims.map(c => {
  const e = execResults.find(r => r.claim_id === c.id)
  const v = verResults.find(r => r.claim_id === c.id)
  return {
    id: c.id, block: c.block, paper: c.paper_value, tol: c.tolerance,
    exec: e ? e.value : null, blind: v ? v.value : null,
    exec_matches_paper: e ? Math.abs(e.value - c.paper_value) <= c.tolerance : false,
    blind_matches_paper: v ? Math.abs(v.value - c.paper_value) <= c.tolerance : false,
    runs_agree: e && v ? Math.abs(e.value - v.value) <= c.tolerance : false,
  }
})
log(`exec matches paper: ${table.filter(t => t.exec_matches_paper).length}/${table.length}; runs agree: ${table.filter(t => t.runs_agree).length}/${table.length}`)

const evidence = JSON.stringify({ claims, env, exec: execs, blind: ver, table })

phase('Report')
const report = await agent(`${COMMON}
STAGE: report. Write the full REPORT.md text in English following the template in E:\\Ciencia\\README.md (Pipeline variant of "How this report was made"; links: method https://github.com/paper-rerun/paper-rerun/blob/main/METHOD.md, contact https://github.com/paper-rerun/paper-rerun/issues). Return ONLY the markdown.
Verdict: decided only by the pre-registered definitions and tolerances, applied to both runs. Alternatives go in a separate "Alternative readings" section, labeled as chosen after seeing data. Check every number you print against the files.
EVIDENCE: ${evidence}`, { label: 'report', phase: 'Report' })

phase('Review')
const review = await agent(`${COMMON}
STAGE: adversarial review. Find what is wrong with this report: paper numbers copied wrong, tolerances misapplied, verdict stronger than evidence, definitions changed after seeing results, method changes hidden as environment fixes, blind verification not actually blind, missing caveats, numbers that don't match the files under ${ROOT}. Every issue needs a concrete fix.
REPORT:
${report}
EVIDENCE: ${evidence}`, { label: 'review', phase: 'Review', schema: REVIEW, effort: 'high' })

phase('Revise')
const revised = await agent(`${COMMON}
STAGE: revision. Fix every blocker, major and minor issue below in the report, checking each fix against the files under ${ROOT} (do not trust the reviewer or the draft blindly). Keep the verdict rules: pre-registered definitions and tolerances decide; alternatives never change the verdict. Return ONLY the full corrected REPORT.md markdown.
ISSUES: ${JSON.stringify(review.issues)}
REPORT:
${report}`, { label: 'revise', phase: 'Revise', effort: 'high' })

return { table, claims, env, exec: execs, blind: ver, report, review, revised }
