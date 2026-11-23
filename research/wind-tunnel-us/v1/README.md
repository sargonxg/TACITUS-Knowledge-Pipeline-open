# Wind Tunnel US institutional-confidence benchmark

<img src="assets/kite.webp" width="85" height="88" align="right" alt="Kite, Wind Tunnel’s teal pixel bird">

This release compares three methods against weighted 2024 General Social Survey distributions on the same 12 recurring confidence questions.

| Method | Mean total variation | Mean Brier score |
| --- | ---: | ---: |
| Earlier human survey, 2022 | 2.5 pp | 0.293 |
| One national Vertex call per item | 7.5 pp | 0.298 |
| Census-weighted Vertex pretest | 8.2 pp | 0.299 |

Lower is better. Total variation is the proportion of answer mass that would have to move to match the target. The multiclass Brier score is half the expected sum of squared errors against the observed categories. All items have equal weight.

## Reproduce the scores

From this directory, run `node score.mjs verify benchmark.json` with Node 20 or later. The script checks the distribution shape, item uniqueness and stored scores. The [data contract](benchmark.schema.json) documents the released fields. The observed and previous distributions include the number who answered, the eligible count and the weighted denominator.

## Study design

The 2022 and 2024 General Social Survey public cross-sections contribute substantive codes 1–3, weighted with WTSSNRPS. The study covers US adults living in households. It excludes the split labor-union item. Form presentation, survey mode, field period and language coverage can differ between releases. The model task used the substantive instrument text and the 2024 context.

The numeric recipe asks Gemini on Vertex AI for answer distributions. The national call uses the same question and scale once. The stratified runs use the same question across 12 age-by-education cells. Their shares are averaged using the fitted household-adult masses from the 2020–2024 ACS demographic artifact.

This is a retrospective check. The target wave was public before generation and may have appeared in model training. The results apply to these institutional-confidence items. The aggregate files and source identifiers are sufficient to recompute the scores. Values from the two human waves are survey estimates with the instrument and sampling properties documented by NORC.

## Sources and rights

- Davern, Michael et al. *General Social Survey 1972–2024*. NORC at the University of Chicago, 2026. The comparison uses the 2022 and 2024 public cross-sections, [documentation and codebooks](https://gss.norc.org/get-documentation.html), [Stata releases](https://gss.norc.org/get-the-data/stata.html), and [NORC’s attribution and terms](https://gss.norc.org/terms-and-conditions.html).
- U.S. Census Bureau. *2020–2024 ACS five-year estimates and Public Use Microdata Sample*. [Source and accuracy documentation](https://www.census.gov/programs-surveys/acs/microdata/documentation.html).
- Bisbee et al. *Synthetic Replacements for Human Survey Data? The Perils of Large Language Models.* [Political Analysis](https://doi.org/10.1017/pan.2024.5).
- Tjuatja et al. *Do LLMs Exhibit Human-like Response Biases?* [Transactions of the Association for Computational Linguistics](https://aclanthology.org/2024.tacl-1.56/).
- The modeled and derived aggregate distributions, data contract and scoring code in this directory are TACITUS release artifacts. The cited surveys and instruments retain their original terms.

[Read the technical overview](https://tacitus.me/research/wind-tunnel/) · [Inspect the US model](https://windtunnel.tacitus.me/audiences/us/) · [Explore benchmark items](https://windtunnel.tacitus.me/audiences/us/benchmark)
