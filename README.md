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
quarto publish gh-pages                  # deploy to GitHub Pages
```

## Timing

The slot is 25 minutes (MS8, Monday 16 November, 10:00–10:25, Room 251B): about 20 minutes of
talk, then questions. Each slide's speaker notes open with its budget and the elapsed time it
should finish by, e.g. `⏱ 1:30 · by 9:25`. The notes mark the slides that can be cut for a
shorter talk (*Why this curve*, *Consistency*, *Mostly pairwise*, *Memorization*), each with a one-sentence
fallback. A bracketed `[MDS26 …]` line in the opener is specific to this session.

| Part | Slides | Ends by |
|:--|:--|--:|
| Opener | title, *How much do they interact?* | 2:20 |
| § I Euler calculus | *The profile*, *Three configurations*, *Why not persistence*, *Why this curve* | 7:30 |
| § II Computation and stability | *Computation*, *Stability*, *Consistency* | 11:10 |
| § III Certified interaction | *Every number carries a test*, *Monsoon*, *Disentanglement*, *Mostly pairwise*, *Memorization* | 18:35 |
| Close | *What remains*, *Thank you* | 19:50 |
