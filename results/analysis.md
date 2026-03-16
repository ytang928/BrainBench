# AI Brainteaser Benchmark v3: Comprehensive Analysis Report
*Generated: 2026-03-15*
*Dataset: 100 questions, 20 categories, 5 questions/category*
*Evaluation: 10 runs per question per model (v3), 3 runs (v1)*

---
## 1. Overall Leaderboard
### v3 English (Hard Set)
| Rank | Model | Accuracy (%) | Reliability (%) | Correct/Total |
|------|-------|:------------:|:---------------:|:-------------:|
| 1 | Claude Opus 4.6 Think | 80.3 | 74.0 | 241/300 |
| 2 | Claude Opus 4.6 | 77.3 | 71.0 | 232/300 |
| 3 | Claude Sonnet 4.6 | 76.7 | 69.0 | 230/300 |
| 4 | Claude Haiku 4.5 | 74.3 | 58.0 | 223/300 |
| 5 | GPT-5.4 Think | 74.0 | 64.0 | 222/300 |
| 6 | GPT-5.4 | 70.7 | 63.0 | 212/300 |
| 7 | GPT-4o Mini | 39.7 | 24.0 | 119/300 |
| 8 | GPT-4o | 39.7 | 27.0 | 119/300 |

### v3 Chinese
| Rank | Model | Accuracy (%) | Reliability (%) | Correct/Total |
|------|-------|:------------:|:---------------:|:-------------:|
| 1 | Claude Opus 4.6 | 83.3 | 76.0 | 250/300 |
| 2 | Claude Opus 4.6 Think | 80.0 | 75.0 | 240/300 |
| 3 | Claude Sonnet 4.6 | 73.0 | 66.0 | 219/300 |
| 4 | GPT-5.4 | 70.7 | 61.0 | 212/300 |
| 5 | Claude Haiku 4.5 | 69.7 | 57.0 | 209/300 |
| 6 | GPT-5.4 Think | 65.7 | 53.0 | 197/300 |
| 7 | GPT-4o | 37.0 | 26.0 | 111/300 |
| 8 | GPT-4o Mini | 32.3 | 16.0 | 97/300 |

### v1 Baseline Comparison (Easy Set)
| Model | v1 Accuracy (%) | v3 Accuracy (%) | Delta (pp) |
|-------|:---------------:|:---------------:|:----------:|
| GPT-4o | 74.0 | 39.7 | -34.3 |

*GPT-4o scored 74.0% on v1 (easy baseline) vs. 39.7% on v3 (hard set), confirming that v3 is substantially more challenging (34.3 percentage points harder).*

---
## 2. Per-Category Accuracy (v3 English)

Accuracy (%) by model and category. Categories sorted by average difficulty (hardest first).

| Model | Implicit physical co... | Wrong vantage point | Semantic scope trick | Default assumption h... | Pragmatic/social int... | Answer hiding in pla... | Negation/exception l... | Broken/dead device s... | Wrong test condition... | Red herring overload | Framing/anchoring tr... | Self-defeating actio... | Circular dependency | Naive physics error | Embedded false premi... | Goal-means mismatch | Temporal impossibili... | State/identity track... | Quantity/counting il... | Scale/growth intuiti... | Avg |
|-------|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| Claude Opus 4.6 Think | 67 | 40 | 40 | 87 | 67 | 87 | 60 | 80 | 80 | 80 | 80 | 80 | 80 | 93 | 100 | 100 | 100 | 87 | 100 | 100 | 80.3 |
| Claude Opus 4.6 | 73 | 33 | 60 | 67 | 33 | 67 | 60 | 60 | 80 | 80 | 80 | 80 | 87 | 93 | 100 | 100 | 100 | 93 | 100 | 100 | 77.3 |
| Claude Sonnet 4.6 | 40 | 47 | 53 | 67 | 67 | 60 | 67 | 80 | 93 | 80 | 47 | 80 | 100 | 87 | 100 | 100 | 100 | 80 | 87 | 100 | 76.7 |
| Claude Haiku 4.5 | 60 | 67 | 53 | 47 | 67 | 53 | 47 | 80 | 73 | 93 | 73 | 80 | 80 | 60 | 100 | 100 | 100 | 93 | 67 | 93 | 74.3 |
| GPT-5.4 Think | 47 | 53 | 53 | 60 | 80 | 80 | 47 | 73 | 87 | 73 | 80 | 80 | 80 | 60 | 87 | 87 | 80 | 80 | 93 | 100 | 74.0 |
| GPT-5.4 | 33 | 60 | 40 | 60 | 53 | 60 | 60 | 67 | 67 | 73 | 80 | 80 | 87 | 87 | 80 | 80 | 80 | 80 | 87 | 100 | 70.7 |
| GPT-4o Mini | 0 | 20 | 40 | 7 | 53 | 33 | 73 | 20 | 27 | 40 | 47 | 47 | 40 | 67 | 7 | 33 | 53 | 60 | 47 | 80 | 39.7 |
| GPT-4o | 0 | 0 | 60 | 20 | 33 | 33 | 73 | 27 | 0 | 40 | 80 | 53 | 33 | 40 | 33 | 27 | 13 | 67 | 73 | 87 | 39.7 |
| **Average** | **40.0** | **40.0** | **50.0** | **51.7** | **56.7** | **59.2** | **60.8** | **60.8** | **63.3** | **70.0** | **70.8** | **72.5** | **73.3** | **73.3** | **75.8** | **78.3** | **78.3** | **80.0** | **81.7** | **95.0** | **66.6** |

---
## 3. Thinking vs. Non-Thinking Analysis

Does extended thinking (reasoning mode) improve brainteaser performance?

### GPT-5.4 vs. GPT-5.4 Think

- **Overall accuracy delta:** +3.3 pp
- **Reliability delta:** +1.0 pp
- Categories where thinking helped: **9**/20
- Categories where thinking hurt: **4**/20
- Categories unchanged: **7**/20

**Biggest gains from thinking:**
  - Pragmatic/social intent: +26.7 pp
  - Answer hiding in plain sight: +20.0 pp
  - Wrong test conditions: +20.0 pp
  - Implicit physical constraint: +13.3 pp
  - Semantic scope trick: +13.3 pp

**Biggest losses from thinking:**
  - Naive physics error: -26.7 pp
  - Negation/exception logic: -13.3 pp
  - Circular dependency: -6.7 pp
  - Wrong vantage point: -6.7 pp

### Claude Opus 4.6 vs. Claude Opus 4.6 Think

- **Overall accuracy delta:** +3.0 pp
- **Reliability delta:** +3.0 pp
- Categories where thinking helped: **5**/20
- Categories where thinking hurt: **4**/20
- Categories unchanged: **11**/20

**Biggest gains from thinking:**
  - Pragmatic/social intent: +33.3 pp
  - Default assumption hijack: +20.0 pp
  - Answer hiding in plain sight: +20.0 pp
  - Broken/dead device self-reference: +20.0 pp
  - Wrong vantage point: +6.7 pp

**Biggest losses from thinking:**
  - Semantic scope trick: -20.0 pp
  - Implicit physical constraint: -6.7 pp
  - Circular dependency: -6.7 pp
  - State/identity tracking: -6.7 pp

### Summary

Thinking mode provides a modest benefit for GPT-5.4 (+3.3 pp) and also improves Claude Opus 4.6 (+3.0 pp). However, the effect is uneven across categories: thinking helps most with categories requiring deliberate multi-step reasoning (Default assumption hijack, Answer hiding in plain sight) but can actually hurt performance on categories where the intuitive first response is often correct.

---
## 4. Cross-Lingual Analysis (English vs. Chinese)

| Model | English (%) | Chinese (%) | Delta (pp) | Direction |
|-------|:----------:|:----------:|:----------:|:---------:|
| Claude Opus 4.6 Think | 80.3 | 80.0 | -0.3 | EN > CN |
| Claude Opus 4.6 | 77.3 | 83.3 | +6.0 | CN > EN |
| Claude Sonnet 4.6 | 76.7 | 73.0 | -3.7 | EN > CN |
| Claude Haiku 4.5 | 74.3 | 69.7 | -4.7 | EN > CN |
| GPT-5.4 Think | 74.0 | 65.7 | -8.3 | EN > CN |
| GPT-5.4 | 70.7 | 70.7 | +0.0 | Equal |
| GPT-4o Mini | 39.7 | 32.3 | -7.3 | EN > CN |
| GPT-4o | 39.7 | 37.0 | -2.7 | EN > CN |

**Average across all models:** English 66.6% vs. Chinese 64.0% (delta: -2.6 pp)

Models that improved in Chinese: Claude Opus 4.6
Models that degraded in Chinese: GPT-4o Mini, GPT-4o, GPT-5.4 Think, Claude Haiku 4.5, Claude Sonnet 4.6, Claude Opus 4.6 Think

Notable: Claude Opus 4.6 is the only model to score substantially *higher* in Chinese (83.3%) than English (77.3%), a +6.0 pp advantage. This may indicate stronger cross-lingual reasoning transfer or differences in how the model processes Chinese-language framing.

---
## 5. Category Difficulty Ranking

Categories ranked from hardest to easiest (average accuracy across all 8 models).

| Rank | Category | Avg Accuracy (%) | Hardest Model | Easiest Model |
|------|----------|:----------------:|:-------------:|:-------------:|
| 1 | Implicit physical constraint | 40.0 | GPT-4o Mini (0%) | Claude Opus 4.6 (73%) |
| 2 | Wrong vantage point | 40.0 | GPT-4o (0%) | Claude Haiku 4.5 (67%) |
| 3 | Semantic scope trick | 50.0 | GPT-4o Mini (40%) | GPT-4o (60%) |
| 4 | Default assumption hijack | 51.7 | GPT-4o Mini (7%) | Claude Opus 4.6 Think (87%) |
| 5 | Pragmatic/social intent | 56.7 | GPT-4o (33%) | GPT-5.4 Think (80%) |
| 6 | Answer hiding in plain sight | 59.2 | GPT-4o Mini (33%) | Claude Opus 4.6 Think (87%) |
| 7 | Negation/exception logic | 60.8 | GPT-5.4 Think (47%) | GPT-4o Mini (73%) |
| 8 | Broken/dead device self-reference | 60.8 | GPT-4o Mini (20%) | Claude Haiku 4.5 (80%) |
| 9 | Wrong test conditions | 63.3 | GPT-4o (0%) | Claude Sonnet 4.6 (93%) |
| 10 | Red herring overload | 70.0 | GPT-4o Mini (40%) | Claude Haiku 4.5 (93%) |
| 11 | Framing/anchoring trap | 70.8 | GPT-4o Mini (47%) | GPT-4o (80%) |
| 12 | Self-defeating action | 72.5 | GPT-4o Mini (47%) | GPT-5.4 (80%) |
| 13 | Circular dependency | 73.3 | GPT-4o (33%) | Claude Sonnet 4.6 (100%) |
| 14 | Naive physics error | 73.3 | GPT-4o (40%) | Claude Opus 4.6 (93%) |
| 15 | Embedded false premise | 75.8 | GPT-4o Mini (7%) | Claude Haiku 4.5 (100%) |
| 16 | Goal-means mismatch | 78.3 | GPT-4o (27%) | Claude Haiku 4.5 (100%) |
| 17 | Temporal impossibility | 78.3 | GPT-4o (13%) | Claude Haiku 4.5 (100%) |
| 18 | State/identity tracking | 80.0 | GPT-4o Mini (60%) | Claude Haiku 4.5 (93%) |
| 19 | Quantity/counting illusion | 81.7 | GPT-4o Mini (47%) | Claude Opus 4.6 (100%) |
| 20 | Scale/growth intuition failure | 95.0 | GPT-4o Mini (80%) | GPT-5.4 (100%) |

**Hardest category:** Implicit physical constraint (40.0%)
**Easiest category:** Scale/growth intuition failure (95.0%)

### Five Hardest Categories
1. **Implicit physical constraint** (40.0%) -- A surface-level cue (e.g., short distance) triggers a default response that ignores the physical constraint (e.g., the object must be physically present at the destination).
2. **Wrong vantage point** (40.0%) -- The default tool or position (mirror, driver's seat, window) seems like the obvious way to observe, but the target is on the wrong side, behind you, or occluded.
3. **Semantic scope trick** (50.0%) -- A key word ('have,' 'one of them,' 'from,' 'incorrectly') is interpreted with the wrong scope — e.g., 'have 28 days' read as 'have exactly 28' rather than 'have at least 28.'
4. **Default assumption hijack** (51.7%) -- A role, title, or scenario triggers an automatic assumption (surgeon = male, bus driver = driving, dark scene = nighttime) that blocks the correct interpretation.
5. **Pragmatic/social intent** (56.7%) -- A sentence that is grammatically a question (yes/no) is pragmatically a request, a demand, sarcasm, or a social ritual. Answering literally misses the point entirely.

### Five Easiest Categories
1. **Scale/growth intuition failure** (95.0%)
2. **Quantity/counting illusion** (81.7%)
3. **State/identity tracking** (80.0%)
4. **Temporal impossibility** (78.3%)
5. **Goal-means mismatch** (78.3%)

---
## 6. Most Discriminating Questions

Questions with the highest variance in accuracy across models (good for separating model tiers).

| Question | Category | Mean Acc (%) | Std Dev | Min | Max | Range |
|:--------:|----------|:-----------:|:-------:|:---:|:---:|:-----:|
| Q4 | Implicit physical constraint | 37.5 | 48.4 | 0 | 100 | 100 |
| Q28 | Embedded false premise | 54.2 | 47.0 | 0 | 100 | 100 |
| Q25 | Wrong vantage point | 41.7 | 46.4 | 0 | 100 | 100 |
| Q66 | Naive physics error | 66.7 | 44.1 | 0 | 100 | 100 |
| Q46 | Default assumption hijack | 33.3 | 44.1 | 0 | 100 | 100 |
| Q57 | Quantity/counting illusion | 45.8 | 43.9 | 0 | 100 | 100 |
| Q12 | Wrong test conditions | 41.7 | 43.3 | 0 | 100 | 100 |
| Q17 | Self-defeating action | 75.0 | 43.3 | 0 | 100 | 100 |
| Q22 | Wrong vantage point | 41.7 | 43.3 | 0 | 100 | 100 |
| Q27 | Embedded false premise | 75.0 | 43.3 | 0 | 100 | 100 |
| Q44 | Temporal impossibility | 75.0 | 43.3 | 0 | 100 | 100 |
| Q52 | Red herring overload | 75.0 | 43.3 | 0 | 100 | 100 |
| Q81 | Goal-means mismatch | 75.0 | 43.3 | 0 | 100 | 100 |
| Q85 | Goal-means mismatch | 75.0 | 43.3 | 0 | 100 | 100 |
| Q87 | Circular dependency | 75.0 | 43.3 | 0 | 100 | 100 |

### Universally Hard Questions (mean accuracy < 20% across all models)

- **Q18** (Self-defeating action): 0.0% mean accuracy
- **Q31** (Semantic scope trick): 0.0% mean accuracy
- **Q77** (Framing/anchoring trap): 0.0% mean accuracy
- **Q1** (Implicit physical constraint): 4.2% mean accuracy
- **Q50** (Default assumption hijack): 8.3% mean accuracy
- **Q10** (Broken/dead device self-reference): 12.5% mean accuracy
- **Q24** (Wrong vantage point): 12.5% mean accuracy
- **Q3** (Implicit physical constraint): 16.7% mean accuracy
- **Q91** (Answer hiding in plain sight): 16.7% mean accuracy
- **Q95** (Answer hiding in plain sight): 16.7% mean accuracy

### Universally Easy Questions (100% accuracy across all models)

- **Q9** (Broken/dead device self-reference)
- **Q16** (Self-defeating action)
- **Q19** (Self-defeating action)
- **Q35** (Semantic scope trick)
- **Q37** (State/identity tracking)
- **Q39** (State/identity tracking)
- **Q55** (Red herring overload)
- **Q62** (Scale/growth intuition failure)
- **Q64** (Scale/growth intuition failure)
- **Q65** (Scale/growth intuition failure)

---
## 7. Consistency and Reliability Analysis

Reliability = fraction of questions answered correctly in ALL runs. A model with 80% accuracy but 50% reliability gets many questions right sometimes but wrong other times -- indicating stochastic reasoning.

| Model | Accuracy (%) | Reliability (%) | Gap (pp) | Interpretation |
|-------|:----------:|:---------------:|:--------:|:---------------|
| Claude Opus 4.6 Think | 80.3 | 74.0 | 6.3 | Consistent |
| Claude Opus 4.6 | 77.3 | 71.0 | 6.3 | Consistent |
| Claude Sonnet 4.6 | 76.7 | 69.0 | 7.7 | Consistent |
| Claude Haiku 4.5 | 74.3 | 58.0 | 16.3 | High variance |
| GPT-5.4 Think | 74.0 | 64.0 | 10.0 | Moderate variance |
| GPT-5.4 | 70.7 | 63.0 | 7.7 | Consistent |
| GPT-4o Mini | 39.7 | 24.0 | 15.7 | High variance |
| GPT-4o | 39.7 | 27.0 | 12.7 | Moderate variance |

### Key Observations

- **Most consistent model:** Claude Opus 4.6 Think (reliability/accuracy ratio: 0.92)
- **Least consistent model:** GPT-4o Mini (reliability/accuracy ratio: 0.61)
- All models show a gap between accuracy and reliability, indicating that some questions are answered stochastically -- the model sometimes reasons correctly and sometimes falls into the trap on the same question.
- GPT-4o-mini has the largest accuracy-reliability gap (39.7 - 24.0 = 15.7 pp), suggesting its correct answers are least robust.

---
## 8. Model Family Analysis

### GPT Family (4o-mini -> 4o -> 5.4 -> 5.4-thinking)

- GPT-4o Mini -> GPT-4o: +0.0 pp
- GPT-4o -> GPT-5.4: +31.0 pp
- GPT-5.4 -> GPT-5.4 Think: +3.3 pp

*The jump from GPT-4o to GPT-5.4 (+31.0 pp) is the largest single improvement in the GPT family, suggesting substantial reasoning improvements in the 5.4 generation.*

### Claude Family (Haiku 4.5 -> Sonnet 4.6 -> Opus 4.6 -> Opus 4.6 Think)

- Claude Haiku 4.5 -> Claude Sonnet 4.6: +2.3 pp
- Claude Sonnet 4.6 -> Claude Opus 4.6: +0.7 pp
- Claude Opus 4.6 -> Claude Opus 4.6 Think: +3.0 pp

*The Claude family shows a flatter progression, with all models in the 74.3%-80.3% range. Even Claude Haiku 4.5 (74.3%) outperforms GPT-5.4 (70.7%) by a significant margin.*

### Cross-Family Comparison (Same Tier)

| Tier | GPT | Claude | Winner | Delta (pp) |
|------|-----|--------|--------|:----------:|
| Small | GPT-4o Mini (39.7%) | Claude Haiku 4.5 (74.3%) | Claude Haiku 4.5 | 34.7 |
| Medium | GPT-4o (39.7%) | Claude Sonnet 4.6 (76.7%) | Claude Sonnet 4.6 | 37.0 |
| Large | GPT-5.4 (70.7%) | Claude Opus 4.6 (77.3%) | Claude Opus 4.6 | 6.7 |
| Large+Think | GPT-5.4 Think (74.0%) | Claude Opus 4.6 Think (80.3%) | Claude Opus 4.6 Think | 6.3 |

*Claude models dominate at every tier on v3 English brainteasers, with advantages ranging from 6.3 to 37.0 pp.*

---
## 9. Key Takeaways for the Paper

1. **No model achieves human-level performance.** The best model (Claude Opus 4.6 Think) achieves 80.3% accuracy on v3, well below the near-perfect human performance expected on these commonsense questions. This confirms v3 as a challenging benchmark.

2. **Large accuracy spread.** Model accuracy ranges from 39.7% (GPT-4o) to 80.3% (Claude Opus 4.6 Think), a 40.7 pp spread. The benchmark discriminates effectively between model capabilities.

3. **Category-specific blind spots persist even in top models.** The hardest categories (Implicit physical constraint, Wrong vantage point, Semantic scope trick) achieve below 50% average accuracy. Even Claude Opus 4.6 Think scores below 50% on some categories.

4. **Thinking mode provides modest, uneven benefits.** GPT-5.4 thinking gains +3.3 pp; Opus 4.6 thinking gains +3.0 pp. Thinking helps on some categories but hurts on others, suggesting that extended reasoning can sometimes overthink simple brainteasers.

5. **Chinese performance is generally comparable to English** (average delta: -2.6 pp), but with notable exceptions. Claude Opus 4.6 actually performs better in Chinese (+6.0 pp), while most GPT models show slight degradation.

6. **Reliability remains a concern.** The accuracy-reliability gap averages 10.3 pp across all models, indicating significant stochastic behavior. Models that "know" the answer don't always give it.

7. **v3 is substantially harder than v1.** GPT-4o drops from 74.0% (v1) to 39.7% (v3), a 34.3 pp decline, validating the dataset revision.

8. **Claude family outperforms GPT family at every tier.** The smallest Claude model (Haiku 4.5, 74.3%) surpasses the largest non-thinking GPT (GPT-5.4, 70.7%), suggesting fundamental differences in commonsense reasoning architecture.

---

## Appendix: Plot Index

All plots saved to `results/plots/` and `paper/figures/` (PNG 300 DPI + PDF).

| Plot | Filename | Description |
|------|----------|-------------|
| 1 | `overall_accuracy_v3` | Horizontal bar chart, 8 models ranked by v3 English accuracy |
| 2 | `category_heatmap_v3` | Model x Category heatmap, sorted by difficulty |
| 3 | `consistency_vs_accuracy_v3` | Scatter: accuracy vs reliability, labeled |
| 4 | `category_difficulty_v3` | Bar chart of mean accuracy per category |
| 5 | `thinking_comparison` | Grouped bars: thinking vs non-thinking, by category |
| 6 | `chinese_vs_english` | Grouped bars: English vs Chinese accuracy per model |
| 7 | `model_tier_radar` | Radar chart: GPT-4o vs GPT-5.4 vs Claude Opus 4.6 |
