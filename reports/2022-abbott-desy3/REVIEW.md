# Adversarial review of the first draft

Read the draft of `REPORT.md` against the files it cites, looking for numbers copied wrong,
tolerances applied loosely, a verdict stronger than the evidence, and method changed after the
fact. Five things came back. Four were real and are fixed in the report; one stands.

## 1. A number in the draft was invented — blocker

The draft said that dropping the PolyChord weight column moves S_8 to **0.7729**, "a 0.003
shift". Nothing in `runs/out/` held that number: it was written from intuition and never
computed. Running it (`runs/out/weights_matter.json`) gives **0.7245**, a shift of 0.0515 —
seventeen times what the draft claimed, and three published sigmas rather than a fifth of one.

The argument the sentence was making survives and gets stronger. The sentence did not, and is
replaced by the measured value in both places it appeared.

This is the failure mode the review exists for: a plausible-looking figure in a supporting
clause, where no table would ever force it to be checked.

## 2. "400 lines before the first table" — fixed

The draft placed the paper's one definition of the interval "400 lines before the first
table". That count came from our `pdftotext` dump, not from the paper: it is an artifact of
how the PDF was flattened, and it would be wrong for anyone reading the published two-column
version. Replaced by what is actually checkable — that the sentence appears once, and that the
table captions, figure captions and abstract say only "68% CL".

Verified against the source: Table II's caption reads "The mean and 68% CL are provided for
each cosmological parameter", and Fig. 7's reads "marginalized constraints (mean and 68% CL)".

## 3. The bandwidth drift was understated — fixed

The draft said that at bandwidth 1.5 σ_8 and w drift out "by 0.002 and 0.012". The sweep in
`runs/out/bw_*.json` says 0.0023 and 0.016. The direction was right, the w figure was 25% low.

## 4. "most plotting code does this by default" — fixed

The draft justified the percentile reading by claiming it is what most plotting code does by
default. We did not check it, and it is doubtful for the two packages a cosmologist would actually
reach for: both ChainConsumer and getdist offer density-based summaries, and neither is a
plain quantile by construction. We are not installing them to find out, because the argument
does not need it. The claim is narrowed to what is true — that
percentiles are what you get from `numpy.percentile` and from helpers that default to
quantiles — and the argument does not depend on it.

## 5. Is the verdict too harsh on ourselves, or too soft on them?

Both readings were tested and the draft lands in the right place, but the balance needed
stating explicitly, so a paragraph was added.

Against us: the four failures are ours. We froze the percentile rule when Section V of the
paper states a different one. A reader could reasonably say the frozen verdict of 6 of 10
tells them nothing about the paper and everything about our reading, and they would be right.
That is why the header carries both numbers and why the verdict is not quietly re-scored.

Against them: one sentence in Section V is the only place the interval is defined, and the
difference it makes is not cosmetic — 17% on one side of w and 39% on the other. A caption
line would close it.

What was added: the note that one of the four failures, Ω_m in wCDM, misses by 0.0003 against
a tolerance of 0.002. Calling that a failure without saying it is a near miss would overstate
the case.

## 6. What the review could not settle

Whether the bandwidth we use is the one behind the published numbers. Our Gaussian KDE with
Silverman's rule reproduces all seven bounds of the two 3x2pt chains between 0.6 and 1.0 times
that bandwidth, and the authors' plotting script passes `kde=1.5` to ChainConsumer, where two
of the bounds drift out. So either the table was not made with the plotting script's setting,
or ChainConsumer's smoothing at 1.5 is not ours at 1.5. The report says the published values
sit at the narrow end of the range and claims nothing beyond that.

## Standing at the end of the review

Verdict unchanged: Partially reproduced, 6 of 10 under the frozen rule, 10 of 10 under the
rule the paper describes. Every central value reproduces to the last printed digit under both.
