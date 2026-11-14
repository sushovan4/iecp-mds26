# The Intersection Euler Characteristic Profile

Slides for a talk at the 2026 SIAM Conference on Mathematics of Data Science
(MDS26), minisymposium MS8, *Foundations and Applications of Topological
Descriptors in Data Analysis*, Monday, November 16, 2026.

Joint work with Kazuhiro Kawamura and Atish Mitra.

**Abstract:** <https://meetings.siam.org/sess/dsp_talk.cfm?p=159636>

## Build

```bash
quarto render index.qmd --to revealjs   # render to index.html
quarto preview index.qmd                 # live preview
QUARTO_PROFILE=public quarto publish gh-pages index.qmd   # deploy WITHOUT speaker notes
```

Always publish with `QUARTO_PROFILE=public`: the profile (`_quarto-public.yml`) runs
`tools/strip-notes.lua`, which removes every `::: {.notes}` block, so the public deck carries
no speaker notes. The plain `quarto render` keeps them for presenting from the speaker view (**S**).

## Timing

The slot is 25 minutes (MS8, Monday 16 November, 10:00–10:25, Room 251B): about 20 minutes of
talk, then questions. Each slide's speaker notes open with its budget and the elapsed time it
should finish by, e.g. `⏱ 1:30 · by 9:25`. The notes mark the slides that can be cut for a
shorter talk (*Why this curve*, *Memorization*), each with a one-sentence
fallback. A bracketed `[MDS26 …]` line in the opener is specific to this session.

| Part | Slides | Ends by |
|:--|:--|--:|
| Opener | title, *Several clouds, one space*, *How much do they interact?*, *Why not a barcode?* | 3:30 |
| § I Euler calculus | *The profile*, *Reading a profile*, *Why this curve*, *Why not the overlap's homology?* | 8:05 |
| § II Computation and stability | *Computation*, *Stability* (*Consistency* is a backup) | 11:15 |
| § III Certified interaction | *Every number carries a test*, *Monsoon*, *Disentanglement*, *Memorization* (*Mostly pairwise* is a backup) | 17:25 |
| Close | *What remains*, *Thank you* | 18:30 |
