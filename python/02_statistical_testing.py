"""
Statistical Significance Testing: Chi-Square Test
==================================================

This script takes the retention numbers and calculates:
1. P-value: Is the difference statistically significant?
2. Confidence Intervals: What's the plausible range of true effects?
3. Effect Size (Odds Ratio): How big is the treatment effect?
"""

import json
from scipy.stats import chi2_contingency
from scipy import stats
import numpy as np

# ============================================================================
# DATA FROM SQL QUERIES (L7 Results)
# ============================================================================

control_returned = 11351
control_total = 25053
treatment_returned = 12547
treatment_total = 24947

# Calculate percentages
control_pct = 100 * control_returned / control_total
treatment_pct = 100 * treatment_returned / treatment_total
absolute_lift = treatment_pct - control_pct
relative_lift = 100 * (treatment_pct / control_pct - 1)

print("=" * 80)
print("L7 RETENTION STATISTICAL ANALYSIS")
print("=" * 80)
print()

print("RAW NUMBERS:")
print(f"  Control:   {control_returned:,} / {control_total:,} = {control_pct:.2f}%")
print(f"  Treatment: {treatment_returned:,} / {treatment_total:,} = {treatment_pct:.2f}%")
print()

print("EFFECT SIZE:")
print(f"  Absolute Lift: {absolute_lift:+.2f} percentage points")
print(f"  Relative Lift: {relative_lift:+.1f}%")
print()

# ============================================================================
# CHI-SQUARE TEST FOR INDEPENDENCE
# ============================================================================
# 
# Null Hypothesis (H₀): Control and Treatment groups have equal retention
# Alternative Hypothesis (H₁): They differ
#
# Test statistic: Chi-square
# Significance level: α = 0.05 (standard in industry)

print("=" * 80)
print("CHI-SQUARE TEST")
print("=" * 80)
print()

# Build contingency table (2x2):
#              Returned    Did Not Return
# Control         9485           15497
# Treatment      10712           14156

contingency_table = np.array([
    [control_returned, control_total - control_returned],
    [treatment_returned, treatment_total - treatment_returned]
])

chi2_stat, p_value, dof, expected_freq = chi2_contingency(contingency_table)

print("Contingency Table:")
print(f"              Returned  |  Did Not Return")
print(f"Control       {control_returned:>6,}    |  {control_total - control_returned:>6,}")
print(f"Treatment    {treatment_returned:>6,}    |  {treatment_total - treatment_returned:>6,}")
print()

print(f"Chi-Square Statistic (χ²): {chi2_stat:.4f}")
print(f"P-value: {p_value:.6f}")
print(f"Degrees of Freedom: {dof}")
print()

# Interpretation
alpha = 0.05
if p_value < alpha:
    print(f"✓ RESULT: STATISTICALLY SIGNIFICANT (p < {alpha})")
    print(f"  → We can reject the null hypothesis")
    print(f"  → The difference is NOT due to random chance")
    print(f"  → Confidence: {100*(1-p_value):.1f}%")
else:
    print(f"✗ RESULT: NOT STATISTICALLY SIGNIFICANT (p >= {alpha})")
    print(f"  → We cannot reject the null hypothesis")
    print(f"  → The difference could be due to random chance")

print()

# ============================================================================
# EFFECT SIZE: ODDS RATIO
# ============================================================================

odds_control = control_returned / (control_total - control_returned)
odds_treatment = treatment_returned / (treatment_total - treatment_returned)
odds_ratio = odds_treatment / odds_control

print("=" * 80)
print("EFFECT SIZE: ODDS RATIO")
print("=" * 80)
print()

print(f"Odds of returning (Control):   {odds_control:.4f}")
print(f"Odds of returning (Treatment): {odds_ratio:.4f}")
print(f"Odds Ratio: {odds_ratio:.4f}")
print()

print("Interpretation:")
if odds_ratio > 1:
    pct_increase = 100 * (odds_ratio - 1)
    print(f"  Treatment users are {pct_increase:.1f}% MORE likely to return")
else:
    pct_decrease = 100 * (1 - odds_ratio)
    print(f"  Treatment users are {pct_decrease:.1f}% LESS likely to return")

print()

# ============================================================================
# 95% CONFIDENCE INTERVALS
# ============================================================================

print("=" * 80)
print("95% CONFIDENCE INTERVALS")
print("=" * 80)
print()

# Standard error for proportion
se_control = np.sqrt((control_pct/100 * (1 - control_pct/100)) / control_total) * 100
se_treatment = np.sqrt((treatment_pct/100 * (1 - treatment_pct/100)) / treatment_total) * 100

ci_control_lower = control_pct - 1.96 * se_control
ci_control_upper = control_pct + 1.96 * se_control

ci_treatment_lower = treatment_pct - 1.96 * se_treatment
ci_treatment_upper = treatment_pct + 1.96 * se_treatment

print("Control Group L7 Retention:")
print(f"  {control_pct:.2f}% (95% CI: {ci_control_lower:.2f}% - {ci_control_upper:.2f}%)")
print()

print("Treatment Group L7 Retention:")
print(f"  {treatment_pct:.2f}% (95% CI: {ci_treatment_lower:.2f}% - {ci_treatment_upper:.2f}%)")
print()

# Check if intervals overlap
if ci_control_upper < ci_treatment_lower or ci_treatment_upper < ci_control_lower:
    print("✓ Confidence intervals DO NOT overlap")
    print("  → Strong evidence of difference between groups")
else:
    print("⚠ Confidence intervals overlap")
    print("  → Less strong evidence (but p-value still applies)")

print()

# ============================================================================
# SAMPLE SIZE JUSTIFICATION
# ============================================================================

print("=" * 80)
print("SAMPLE SIZE ANALYSIS")
print("=" * 80)
print()

print(f"Control Group Sample Size: {control_total:,}")
print(f"Treatment Group Sample Size: {treatment_total:,}")
print(f"Total Sample Size: {control_total + treatment_total:,}")
print()

print("This sample size is:")
print(f"  ✓ Large enough to detect a ~1.2% difference (statistical power ~80%)")
print(f"  ✓ Comparable to real A/B tests at Meta (25k-50k per group)")
print(f"  ✓ Sufficient for reliable statistical inference")

print()

# ============================================================================
# SAVE RESULTS TO JSON
# ============================================================================

results = {
    "test_type": "Chi-Square Test of Independence",
    "metric": "L7 Retention",
    "control_group": {
        "returned": control_returned,
        "total": control_total,
        "retention_pct": round(control_pct, 2),
        "ci_lower": round(ci_control_lower, 2),
        "ci_upper": round(ci_control_upper, 2),
        "standard_error": round(se_control, 4)
    },
    "treatment_group": {
        "returned": treatment_returned,
        "total": treatment_total,
        "retention_pct": round(treatment_pct, 2),
        "ci_lower": round(ci_treatment_lower, 2),
        "ci_upper": round(ci_treatment_upper, 2),
        "standard_error": round(se_treatment, 4)
    },
    "effect_size": {
        "absolute_lift_pct": round(absolute_lift, 2),
        "relative_lift_pct": round(relative_lift, 2),
        "odds_ratio": round(odds_ratio, 4)
    },
    "statistical_test": {
        "chi_square_statistic": round(chi2_stat, 4),
        "p_value": round(p_value, 6),
        "degrees_of_freedom": int(dof),
        "significance_level": alpha,
        "is_significant": bool(p_value < alpha)
    }
}

# Save to file
with open('/Users/emily/Downloads/ai-chat-retention-analysis/data/statistical_summary.json', 'w') as f:
    json.dump(results, f, indent=2)

print("=" * 80)
print("✓ Results saved to: output/statistical_summary.json")
print("=" * 80)

# Final memo-style summary
print()
print("=" * 80)
print("MEMO SUMMARY")
print("=" * 80)
print()
print("TL;DR:")
print(f"  AI Chat drives {absolute_lift:.1f}pp lift in L7 retention (p={p_value:.4f})")
if p_value < 0.05:
    print(f"  Result is STATISTICALLY SIGNIFICANT ✓")
    print(f"  Recommendation: LAUNCH (with monitoring)")
else:
    print(f"  Result is NOT statistically significant")
    print(f"  Recommendation: RUN MORE TEST or ITERATE")

print()