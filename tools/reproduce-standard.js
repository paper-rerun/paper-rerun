export const meta = {
  name: 'reproduce-standard',
  description: 'Standard reproduction: pre-registered claims map, single agent run, adversarial review, revision',
  phases: [
    { title: 'Claims', detail: 'fix claims and definitions before anything runs, hash them' },
    { title: 'Reproduce', detail: 'single agent builds env, runs, writes report' },
    { title: 'Review', detail: 'adversarial review of the report' },
    { title: 'Revise', detail: 'fix every review point against the files' },
  ],
}

const P = args
const ROOT = P.root
const WROOT = P.wroot
const COMMON = `
Volunteer project that checks whether published computational results hold.
Paper: ${P.paper}
Code: ${P.repo}
Working folder (Windows): ${ROOT}   (WSL: ${WROOT}). Stay inside it.
Rules:
- Read E:\\Ciencia\\README.md (rules + REPORT.md template).
- Machine: Ryzen 9 3900X, WSL2 Ubuntu 24.04 (31 GB RAM, passwordless sudo, uv at ~/.local/bin/uv), RTX 2070 SUPER 8 GB. Work in WSL.
- Shell gotchas: (1) this harness expands $VAR and $(...) inside 'wsl -d Ubuntu -- bash -lc "..."' BEFORE WSL sees them, so put any command with variables in a .sh file inside the working folder; (2) Git Bash rewrites /mnt/... paths passed to wsl.exe, so call it as MSYS_NO_PATHCONV=1 wsl -d Ubuntu -- bash /mnt/e/...sh.
- Every GPU command runs under: flock /mnt/e/Ciencia/.gpu.lock <cmd>. Other people's jobs share the GPU. Set MPLBACKEND=Agg; never open windows.
- Make long runs restartable (per-item outputs, skip finished items) and run them in the background; wait for the notification instead of polling.
- Verify every download against the server size, and a checksum where one exists.
- Never change the authors' method or hyperparameters to make numbers match. Only environment, dependencies, paths, obvious crashes.
- If the same failure survives 3 different fix attempts, stop and report it.
- Publish nothing (no issues, PRs, pushes, uploads).
Triage notes: ${P.triage}
`

phase('Claims')
await agent(`${COMMON}
STAGE: pre-registration. Do not run any model and do not compute any result from our side.
Read the paper and SI and write ${ROOT}\\claims.json with:
- claims: id, exact paper value, unit, location (table/figure/page), tolerance and its basis, conditions (model, checkpoint, samples, test set) for this target: ${P.target}
- definitions: every choice the computation needs (metric, averaging, test-set file and version, scoring mode, windows, filters), each with a quote from the paper and an ambiguity note.
If the authors publish per-item results (source data, per-assay tables, released scores), download them into ${WROOT}/sources/ and use them to decide ambiguous definitions and tolerances (e.g. bootstrap of the authors' per-item values). Say so in the ambiguity note. Never decide a definition from numbers we computed.
Then write ${ROOT}\\claims.sha256 with the SHA-256 of claims.json and the time. From this moment claims.json must not change.
Return a short summary of the claims and the hash.`, { label: 'claims', phase: 'Claims' })

phase('Reproduce')
const report = await agent(`${COMMON}
TASK: reproduce the target end to end and write the report.
The claims and definitions are pre-registered in ${ROOT}\\claims.json (hash in claims.sha256). Do NOT edit claims.json. The verdict uses exactly those definitions and tolerances, on the FULL test set (no sampling). If you believe a definition is wrong, compute the alternative AFTER the main result and report it in a separate "Alternative readings" section; it never changes the verdict.
1. Build the environment from the versions the authors used, freeze it (lockfile + setup script) in ${WROOT}/env; weights and data in ${WROOT}/data.
2. Compute each claim; scripts, outputs and logs in ${WROOT}/runs/. Compare per item with the authors' released results when they exist.
3. Return the full REPORT.md text in English following the README template. Use the single-agent variant of "How this report was made", adding that a separate agent pre-registered the claims before any run and that a reviewer and a reviser agent checked the report. Links: method https://github.com/paper-rerun/paper-rerun/blob/main/METHOD.md, contact https://github.com/paper-rerun/paper-rerun/issues. Return ONLY the markdown.`, { label: 'reproduce', phase: 'Reproduce' })

phase('Review')
const REVIEW = { type: 'object', properties: {
  issues: { type: 'array', items: { type: 'object', properties: {
    severity: { type: 'string', enum: ['blocker', 'major', 'minor'] }, where: { type: 'string' }, problem: { type: 'string' }, fix: { type: 'string' } },
    required: ['severity', 'where', 'problem', 'fix'] } } },
  required: ['issues'] }
const review = await agent(`${COMMON}
STAGE: adversarial review. Find what is wrong with this report:
- check that the SHA-256 of ${ROOT}\\claims.json still matches claims.sha256 and that the report uses exactly its definitions and tolerances;
- paper numbers copied wrong (open the paper);
- tolerances misapplied, verdict stronger than the evidence, sampling passed off as a full run;
- method changes passed off as environment fixes;
- numbers that don't match the files under ${ROOT}; missing caveats.
Re-run cheap computations yourself if that settles a doubt. Every issue needs a concrete fix.
REPORT:
${report}`, { label: 'review', phase: 'Review', effort: 'high', schema: REVIEW })

phase('Revise')
const revised = await agent(`${COMMON}
STAGE: revision. Fix every issue below in the report, checking each fix against the files under ${ROOT}. Keep the verdict rules. Return ONLY the full corrected REPORT.md markdown.
ISSUES: ${JSON.stringify(review.issues)}
REPORT:
${report}`, { label: 'revise', phase: 'Revise', effort: 'high' })

return { report, review, revised }
