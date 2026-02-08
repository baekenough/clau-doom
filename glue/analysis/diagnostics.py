"""Residual diagnostic checks for ANOVA assumptions."""
from __future__ import annotations

import numpy as np
from dataclasses import dataclass

from glue.analysis.statistical_tests import anderson_darling_test, levene_test


@dataclass
class DiagnosticSummary:
    """Summary of all diagnostic checks."""
    normality_pass: bool
    normality_p: float
    equal_variance_pass: bool
    equal_variance_p: float
    independence_pass: bool  # Based on run-order check
    overall_pass: bool

    def format_summary(self) -> str:
        lines = ["## Residual Diagnostics", ""]

        status = "PASS" if self.normality_pass else "FAIL"
        lines.append(f"- Normality (Anderson-Darling): **{status}** (p={self.normality_p:.3f})")

        status = "PASS" if self.equal_variance_pass else "FAIL"
        lines.append(f"- Equal Variance (Levene): **{status}** (p={self.equal_variance_p:.3f})")

        status = "PASS" if self.independence_pass else "FAIL"
        lines.append(f"- Independence (Run Order): **{status}**")

        overall = "PASS" if self.overall_pass else "FAIL"
        lines.append(f"\n**Overall: {overall}**")

        return "\n".join(lines)


def compute_residuals(data: dict[str, np.ndarray]) -> np.ndarray:
    """Compute residuals (observed - group mean) for all groups."""
    residuals = []
    for group_data in data.values():
        group_mean = np.mean(group_data)
        residuals.extend(group_data - group_mean)
    return np.array(residuals)


def check_independence(residuals: np.ndarray, threshold: float = 0.3) -> bool:
    """Check independence via lag-1 autocorrelation of run-order residuals."""
    if len(residuals) < 3:
        return True
    mean_r = np.mean(residuals)
    centered = residuals - mean_r

    numerator = np.sum(centered[:-1] * centered[1:])
    denominator = np.sum(centered ** 2)

    if denominator == 0:
        return True

    autocorr = numerator / denominator
    return abs(autocorr) < threshold


def run_diagnostics(data: dict[str, np.ndarray]) -> DiagnosticSummary:
    """Run full diagnostic battery on grouped data."""
    residuals = compute_residuals(data)

    # Normality of residuals
    ad_stat, ad_p = anderson_darling_test(residuals)
    normality_pass = ad_p > 0.05

    # Equal variance
    arrays = list(data.values())
    lev_stat, lev_p = levene_test(*arrays)
    variance_pass = lev_p > 0.05

    # Independence
    independence_pass = check_independence(residuals)

    return DiagnosticSummary(
        normality_pass=normality_pass,
        normality_p=ad_p,
        equal_variance_pass=variance_pass,
        equal_variance_p=lev_p,
        independence_pass=independence_pass,
        overall_pass=normality_pass and variance_pass and independence_pass,
    )
