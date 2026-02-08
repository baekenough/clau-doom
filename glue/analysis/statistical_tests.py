"""Statistical tests for DOE experiment analysis.

Implements the required battery of tests for comparing experimental conditions:
- Welch's t-test for pairwise comparisons
- Mann-Whitney U (non-parametric alternative)
- Cohen's d effect size
- Anderson-Darling normality test
- Levene's test for equal variance
- Holm-Bonferroni correction for multiple comparisons
"""
from __future__ import annotations

import numpy as np
from dataclasses import dataclass
from scipy import stats


@dataclass
class PairwiseResult:
    """Result of a pairwise comparison between two conditions."""
    condition_a: str
    condition_b: str
    metric: str
    mean_a: float
    mean_b: float
    std_a: float
    std_b: float
    n_a: int
    n_b: int

    # Welch's t-test
    t_statistic: float
    p_value_welch: float
    df_welch: float

    # Mann-Whitney U
    u_statistic: float
    p_value_mann_whitney: float

    # Effect size
    cohens_d: float

    # Confidence interval for difference
    ci_lower: float
    ci_upper: float
    ci_level: float  # e.g., 0.95

    def is_significant(self, alpha: float = 0.05) -> bool:
        return self.p_value_welch < alpha

    def format_stat_markers(self) -> str:
        """Generate [STAT:...] markers for research documents."""
        markers = []
        markers.append(f"[STAT:p={self.p_value_welch:.4f}]")
        markers.append(f"[STAT:t=t({self.df_welch:.0f})={self.t_statistic:.3f}]")
        markers.append(f"[STAT:effect_size=Cohen's d={self.cohens_d:.2f}]")
        markers.append(f"[STAT:ci={int(self.ci_level*100)}%: {self.ci_lower:.2f}-{self.ci_upper:.2f}]")
        markers.append(f"[STAT:n={self.n_a}+{self.n_b}]")
        return " ".join(markers)


@dataclass
class NormalityResult:
    """Result of normality testing."""
    condition: str
    metric: str
    n: int
    ad_statistic: float
    ad_p_value: float
    is_normal: bool  # p > 0.05

    def format_stat_marker(self) -> str:
        return f"[STAT:normality=AD({self.n})={self.ad_statistic:.3f}, p={self.ad_p_value:.3f}]"


@dataclass
class VarianceResult:
    """Result of equal variance testing."""
    conditions: list[str]
    metric: str
    levene_statistic: float
    levene_p_value: float
    variances_equal: bool  # p > 0.05

    def format_stat_marker(self) -> str:
        return f"[STAT:variance=Levene={self.levene_statistic:.3f}, p={self.levene_p_value:.3f}]"


def welch_t_test(a: np.ndarray, b: np.ndarray) -> tuple[float, float, float]:
    """Welch's t-test (unequal variance assumed)."""
    result = stats.ttest_ind(a, b, equal_var=False)
    # Welch-Satterthwaite degrees of freedom
    na, nb = len(a), len(b)
    va, vb = np.var(a, ddof=1), np.var(b, ddof=1)
    num = (va/na + vb/nb)**2
    den = (va/na)**2/(na-1) + (vb/nb)**2/(nb-1)
    df = num / den if den > 0 else min(na, nb) - 1
    return float(result.statistic), float(result.pvalue), float(df)


def mann_whitney_u(a: np.ndarray, b: np.ndarray) -> tuple[float, float]:
    """Mann-Whitney U test (non-parametric alternative)."""
    result = stats.mannwhitneyu(a, b, alternative='two-sided')
    return float(result.statistic), float(result.pvalue)


def cohens_d(a: np.ndarray, b: np.ndarray) -> float:
    """Cohen's d effect size (pooled standard deviation)."""
    na, nb = len(a), len(b)
    pooled_std = np.sqrt(((na-1)*np.var(a, ddof=1) + (nb-1)*np.var(b, ddof=1)) / (na+nb-2))
    if pooled_std == 0:
        return 0.0
    return float((np.mean(a) - np.mean(b)) / pooled_std)


def confidence_interval_diff(a: np.ndarray, b: np.ndarray, level: float = 0.95) -> tuple[float, float]:
    """Confidence interval for difference in means (Welch)."""
    diff = np.mean(a) - np.mean(b)
    se = np.sqrt(np.var(a, ddof=1)/len(a) + np.var(b, ddof=1)/len(b))
    # Welch df
    na, nb = len(a), len(b)
    va, vb = np.var(a, ddof=1), np.var(b, ddof=1)
    num = (va/na + vb/nb)**2
    den = (va/na)**2/(na-1) + (vb/nb)**2/(nb-1)
    df = num / den if den > 0 else min(na, nb) - 1
    t_crit = stats.t.ppf((1 + level) / 2, df)
    return float(diff - t_crit * se), float(diff + t_crit * se)


def anderson_darling_test(data: np.ndarray) -> tuple[float, float]:
    """Anderson-Darling normality test. Returns (statistic, p_value)."""
    try:
        # scipy >= 1.17: use method='interpolate' for direct p-value
        result = stats.anderson(data, dist='norm', method='interpolate')
        return float(result.statistic), float(result.pvalue)
    except TypeError:
        # scipy < 1.17: fall back to critical value table lookup
        result = stats.anderson(data, dist='norm')
        stat = result.statistic
        sig_levels = result.significance_level  # [15, 10, 5, 2.5, 1]
        crit_values = result.critical_values

        if stat < crit_values[0]:
            p_approx = sig_levels[0] / 100.0  # > 0.15
        elif stat > crit_values[-1]:
            p_approx = sig_levels[-1] / 100.0  # < 0.01
        else:
            for i in range(len(crit_values) - 1):
                if crit_values[i] <= stat <= crit_values[i+1]:
                    p_approx = sig_levels[i+1] / 100.0
                    break
            else:
                p_approx = 0.05

        return float(stat), float(p_approx)


def levene_test(*groups: np.ndarray) -> tuple[float, float]:
    """Levene's test for equality of variances."""
    result = stats.levene(*groups)
    return float(result.statistic), float(result.pvalue)


def holm_bonferroni(p_values: list[float], alpha: float = 0.05) -> list[bool]:
    """Holm-Bonferroni correction for multiple comparisons.
    Returns list of booleans: True if significant after correction."""
    n = len(p_values)
    indexed = sorted(enumerate(p_values), key=lambda x: x[1])
    significant = [False] * n

    for rank, (orig_idx, p) in enumerate(indexed):
        adjusted_alpha = alpha / (n - rank)
        if p <= adjusted_alpha:
            significant[orig_idx] = True
        else:
            break  # All remaining are non-significant

    return significant


def pairwise_comparison(
    data_a: np.ndarray,
    data_b: np.ndarray,
    condition_a: str,
    condition_b: str,
    metric: str,
    ci_level: float = 0.95,
) -> PairwiseResult:
    """Run full pairwise comparison battery."""
    t_stat, p_welch, df = welch_t_test(data_a, data_b)
    u_stat, p_mw = mann_whitney_u(data_a, data_b)
    d = cohens_d(data_a, data_b)
    ci_lo, ci_hi = confidence_interval_diff(data_a, data_b, ci_level)

    return PairwiseResult(
        condition_a=condition_a,
        condition_b=condition_b,
        metric=metric,
        mean_a=float(np.mean(data_a)),
        mean_b=float(np.mean(data_b)),
        std_a=float(np.std(data_a, ddof=1)),
        std_b=float(np.std(data_b, ddof=1)),
        n_a=len(data_a),
        n_b=len(data_b),
        t_statistic=t_stat,
        p_value_welch=p_welch,
        df_welch=df,
        u_statistic=u_stat,
        p_value_mann_whitney=p_mw,
        cohens_d=d,
        ci_lower=ci_lo,
        ci_upper=ci_hi,
        ci_level=ci_level,
    )


def test_normality(data: np.ndarray, condition: str, metric: str) -> NormalityResult:
    """Test normality of a single condition's data."""
    stat, p = anderson_darling_test(data)
    return NormalityResult(
        condition=condition,
        metric=metric,
        n=len(data),
        ad_statistic=stat,
        ad_p_value=p,
        is_normal=p > 0.05,
    )


def test_equal_variance(groups: dict[str, np.ndarray], metric: str) -> VarianceResult:
    """Test equal variance across conditions."""
    arrays = list(groups.values())
    stat, p = levene_test(*arrays)
    return VarianceResult(
        conditions=list(groups.keys()),
        metric=metric,
        levene_statistic=stat,
        levene_p_value=p,
        variances_equal=p > 0.05,
    )
