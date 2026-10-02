# Role Scorer report — 2026-10-01

*Bayesian Role Scorer (Ch.11). Weights: sponsorship 0.35, fit 0.3, role_quality 0 [role_quality weight is **[VERIFY]** — not pinned by the chapter]. Threshold 0.3. Profile requires sponsorship.*

**Summary:** 4 roles → Apply 3 · Consider 0 · Skip 1. **Skip rate 25%** (below the ~50% a healthy run skips; check the inputs).

| Role | Composite | Rec | Why | Audit (term · value · weight · source) |
|---|---|---|---|---|
| Pinterest, Inc. — University Grad Software Engineer 2027 (USA) | 0.555 | **Apply** | composite 0.555 ≥ 0.3, gates healthy | sponsorship 0.9·0.35 [model-judgment]; fit 0.8·0.3 [your-input] × liveness 1[record]×timeline 1[your-input] |
| Databricks, Inc. — Software Engineer, Web Products (Mountain View) | 0.525 | **Apply** | composite 0.525 ≥ 0.3, gates healthy | sponsorship 0.9·0.35 [model-judgment]; fit 0.7·0.3 [your-input] × liveness 1[record]×timeline 1[your-input] |
| Pinterest, Inc. — Software Engineer II, Big Data, tvScientific | 0.495 | **Apply** | composite 0.495 ≥ 0.3, gates healthy | sponsorship 0.9·0.35 [model-judgment]; fit 0.6·0.3 [your-input] × liveness 1[record]×timeline 1[your-input] |
| Chime Financial Inc — Deliberately dead URL (the repo's own example 404) | 0.000 | **Skip** | gated: liveness ≈ 0.000 (a closed gate zeroes the composite regardless of votes) | sponsorship 0.5·0.35 [model-judgment]; fit 0.8·0.3 [your-input] × liveness 0[record]×timeline 1[your-input] |

*Every term traces to its source. If you cannot explain a row term-by-term, distrust the recommendation before your confusion (Ch.11).*
