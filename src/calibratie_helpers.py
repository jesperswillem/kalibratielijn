"""Helperfuncties voor de onderwijsnotebook over kalibratielijnen.

De studentennotebook is bewust zelfstandig te draaien. Deze module bevat dezelfde
functies apart, zodat docenten of gevorderde studenten ze kunnen hergebruiken in
scripts, tests of eigen notebooks.
"""

from dataclasses import dataclass
import math

import numpy as np
import pandas as pd
from scipy import stats
import matplotlib.pyplot as plt

@dataclass
class CalibrationFit:
    """Resultaat van de rechte lijn y = intercept + slope * x."""
    intercept: float
    slope: float
    x_mean: float
    y_mean: float
    n: int
    sxx: float
    sum_x2: float
    correlation: float


def clean_calibration_data(df: pd.DataFrame) -> pd.DataFrame:
    """Controleer de kolommen en verwijder rijen zonder geldige concentratie/respons."""
    required = ["concentratie", "respons"]
    missing = [col for col in required if col not in df.columns]
    if missing:
        raise ValueError(f"Ontbrekende kolommen: {missing}")

    cleaned = df[required].copy()
    cleaned["concentratie"] = pd.to_numeric(cleaned["concentratie"], errors="coerce")
    cleaned["respons"] = pd.to_numeric(cleaned["respons"], errors="coerce")
    cleaned = cleaned.dropna().reset_index(drop=True)

    if len(cleaned) < 3:
        raise ValueError("Gebruik minimaal drie meetpunten. Voor statistische spreiding zijn meer punten beter.")
    if cleaned["concentratie"].nunique() < 2:
        raise ValueError("Er zijn minimaal twee verschillende concentraties nodig.")
    return cleaned


def fit_calibration_line(df: pd.DataFrame) -> CalibrationFit:
    """Bereken de beste rechte lijn volgens de kleinste-kwadratenmethode.

    De kleinste-kwadratenmethode kiest de lijn waarbij de som van de kwadraten
    van de residuen zo klein mogelijk is.
    """
    cleaned = clean_calibration_data(df)
    x = cleaned["concentratie"].to_numpy(dtype=float)
    y = cleaned["respons"].to_numpy(dtype=float)

    x_mean = float(np.mean(x))
    y_mean = float(np.mean(y))
    sxx = float(np.sum((x - x_mean) ** 2))
    sum_x2 = float(np.sum(x ** 2))

    slope = float(np.sum((x - x_mean) * (y - y_mean)) / sxx)
    intercept = float(y_mean - slope * x_mean)
    correlation = float(np.corrcoef(x, y)[0, 1])

    return CalibrationFit(
        intercept=intercept,
        slope=slope,
        x_mean=x_mean,
        y_mean=y_mean,
        n=len(cleaned),
        sxx=sxx,
        sum_x2=sum_x2,
        correlation=correlation,
    )


def make_detail_table(df: pd.DataFrame, fit: CalibrationFit) -> pd.DataFrame:
    """Maak een tabel met voorspellingen, residuen en kwadraten.

    Deze tabel is handig voor onderwijs, omdat je kunt zien waar de
    samenvattende getallen vandaan komen.
    """
    detail = clean_calibration_data(df)
    x = detail["concentratie"].to_numpy(dtype=float)
    y = detail["respons"].to_numpy(dtype=float)
    y_hat = fit.intercept + fit.slope * x
    residual = y - y_hat

    detail["voorspelde_respons"] = y_hat
    detail["residu"] = residual
    detail["residu_kwadraat"] = residual ** 2
    detail["x_min_xgem"] = x - fit.x_mean
    detail["x_min_xgem_kwadraat"] = (x - fit.x_mean) ** 2
    detail["yhat_min_ygem_kwadraat"] = (y_hat - fit.y_mean) ** 2
    detail["y_min_ygem_kwadraat"] = (y - fit.y_mean) ** 2
    return detail


def summarize_calibration(df: pd.DataFrame, alpha: float = 0.05) -> tuple[pd.Series, pd.DataFrame]:
    """Bereken de belangrijkste kengetallen voor de kalibratielijn."""
    fit = fit_calibration_line(df)
    detail = make_detail_table(df, fit)

    n = fit.n
    df_residual = n - 2
    ss_residual = float(detail["residu_kwadraat"].sum())
    ss_regression = float(detail["yhat_min_ygem_kwadraat"].sum())
    ss_total = float(detail["y_min_ygem_kwadraat"].sum())

    ms_residual = ss_residual / df_residual
    syx = math.sqrt(ms_residual)

    # Standaardfouten van intercept en helling
    se_slope = syx / math.sqrt(fit.sxx)
    se_intercept = syx * math.sqrt(1 / n + fit.x_mean**2 / fit.sxx)

    t_critical = float(stats.t.ppf(1 - alpha / 2, df_residual))
    slope_ci_half_width = t_critical * se_slope
    intercept_ci_half_width = t_critical * se_intercept

    # Determinatiecoëfficiënt: welk deel van de y-spreiding wordt door de lijn verklaard?
    r_squared = 1 - ss_residual / ss_total

    # Detectie- en kwantificatielimiet volgens de veelgebruikte benadering 3*Sy/x/b en 10*Sy/x/b
    lod = 3 * syx / fit.slope if not np.isclose(fit.slope, 0.0) else np.nan
    loq = 10 * syx / fit.slope if not np.isclose(fit.slope, 0.0) else np.nan

    # Goodness-of-fit F-toets voor de regressielijn als geheel
    df_regression = 1
    ms_regression = ss_regression / df_regression
    f_goodness = np.inf if np.isclose(ms_residual, 0.0) else ms_regression / ms_residual
    f_goodness_critical = float(stats.f.ppf(0.95, df_regression, df_residual))

    # Lack-of-fit: splits residuele spreiding in pure meetspreiding en modelafwijking
    lof = lack_of_fit_table(detail, fit)

    summary = pd.Series({
        "a_intercept": fit.intercept,
        "b_helling": fit.slope,
        "n_meetpunten": n,
        "vrijheidsgraden_residu": df_residual,
        "x_gemiddelde": fit.x_mean,
        "y_gemiddelde": fit.y_mean,
        "correlatie_r": fit.correlation,
        "r_kwadraat": r_squared,
        "SS_residu": ss_residual,
        "SS_regressie": ss_regression,
        "SS_totaal": ss_total,
        "MS_residu": ms_residual,
        "Sy_x": syx,
        "SE_intercept": se_intercept,
        "SE_helling": se_slope,
        "t_kritisch_95pct": t_critical,
        "intercept_CI_onder": fit.intercept - intercept_ci_half_width,
        "intercept_CI_boven": fit.intercept + intercept_ci_half_width,
        "helling_CI_onder": fit.slope - slope_ci_half_width,
        "helling_CI_boven": fit.slope + slope_ci_half_width,
        "LOD": lod,
        "LOQ": loq,
        "F_goodness_of_fit": f_goodness,
        "F_kritisch_goodness_of_fit": f_goodness_critical,
        "goodness_significant": f_goodness > f_goodness_critical,
        "SS_pure_error": lof.loc["pure_error", "SS"],
        "SS_lack_of_fit": lof.loc["lack_of_fit", "SS"],
        "F_lack_of_fit": lof.loc["lack_of_fit", "F"],
        "F_kritisch_lack_of_fit": lof.loc["lack_of_fit", "F_kritisch_95pct"],
        "lack_of_fit_significant": lof.loc["lack_of_fit", "F" ] > lof.loc["lack_of_fit", "F_kritisch_95pct"],
    })
    return summary, detail


def lack_of_fit_table(detail: pd.DataFrame, fit: CalibrationFit) -> pd.DataFrame:
    """Bereken pure error en lack-of-fit bij herhaalde concentraties.

    Pure error = spreiding tussen herhalingen binnen dezelfde concentratie.
    Lack-of-fit = afwijking van de groepsgemiddelden ten opzichte van de rechte lijn.
    """
    grouped = detail.groupby("concentratie", sort=True)
    number_of_groups = grouped.ngroups
    n = len(detail)

    # Pure error: binnen elke concentratie kijken we naar afwijking t.o.v. het groepsgemiddelde
    pure_error_ss = 0.0
    lack_of_fit_ss = 0.0
    for concentration, group in grouped:
        y_values = group["respons"].to_numpy(dtype=float)
        y_group_mean = float(np.mean(y_values))
        pure_error_ss += float(np.sum((y_values - y_group_mean) ** 2))

        yhat_group = fit.intercept + fit.slope * float(concentration)
        lack_of_fit_ss += len(group) * (y_group_mean - yhat_group) ** 2

    df_pure_error = n - number_of_groups
    df_lack_of_fit = number_of_groups - 2

    ms_pure_error = pure_error_ss / df_pure_error if df_pure_error > 0 else np.nan
    ms_lack_of_fit = lack_of_fit_ss / df_lack_of_fit if df_lack_of_fit > 0 else np.nan
    f_lack_of_fit = (np.inf if np.isclose(ms_pure_error, 0.0) else ms_lack_of_fit / ms_pure_error) if df_pure_error > 0 and df_lack_of_fit > 0 else np.nan
    f_critical = stats.f.ppf(0.95, df_lack_of_fit, df_pure_error) if df_pure_error > 0 and df_lack_of_fit > 0 else np.nan

    return pd.DataFrame({
        "SS": [pure_error_ss, lack_of_fit_ss, pure_error_ss + lack_of_fit_ss],
        "vrijheidsgraden": [df_pure_error, df_lack_of_fit, df_pure_error + df_lack_of_fit],
        "MS": [ms_pure_error, ms_lack_of_fit, np.nan],
        "F": [np.nan, f_lack_of_fit, np.nan],
        "F_kritisch_95pct": [np.nan, f_critical, np.nan],
    }, index=["pure_error", "lack_of_fit", "residu_totaal"])


def estimate_concentration(response: float, summary: pd.Series) -> float:
    """Schat een onbekende concentratie uit een gemeten respons."""
    return (response - summary["a_intercept"]) / summary["b_helling"]


def calibration_bounds(x_values: np.ndarray, summary: pd.Series) -> tuple[np.ndarray, np.ndarray]:
    """Bereken eenvoudige onder- en bovengrenzen voor de kalibratielijn.

    Deze grenzen gebruiken het 95%-betrouwbaarheidsinterval van het intercept
    en het 95%-betrouwbaarheidsinterval van de helling.

    Let op: dit is een didactische, eenvoudige manier om onzekerheid rond de lijn
    zichtbaar te maken. Het is niet hetzelfde als een formele simultane
    betrouwbaarheidsband voor de hele lijn.
    """
    lower = summary["intercept_CI_onder"] + summary["helling_CI_onder"] * x_values
    upper = summary["intercept_CI_boven"] + summary["helling_CI_boven"] * x_values
    return lower, upper


def plot_calibration(df: pd.DataFrame, summary: pd.Series, title: str = "Kalibratielijn") -> None:
    """Teken meetpunten, de berekende kalibratielijn en eenvoudige grenzen."""
    cleaned = clean_calibration_data(df)
    x = cleaned["concentratie"].to_numpy(dtype=float)
    y = cleaned["respons"].to_numpy(dtype=float)

    x_line = np.linspace(x.min(), x.max(), 100)
    y_line = summary["a_intercept"] + summary["b_helling"] * x_line
    y_lower, y_upper = calibration_bounds(x_line, summary)

    fig, ax = plt.subplots(figsize=(7, 4))
    ax.scatter(x, y, label="metingen")
    ax.plot(x_line, y_line, label="berekende lijn")
    ax.plot(x_line, y_lower, linestyle="--", label="ondergrens")
    ax.plot(x_line, y_upper, linestyle="--", label="bovengrens")
    ax.fill_between(x_line, y_lower, y_upper, alpha=0.15, label="gebied tussen grenzen")
    ax.set_xlabel("Concentratie")
    ax.set_ylabel("Respons")
    ax.set_title(title)
    ax.grid(True, alpha=0.3)
    ax.legend()
    plt.show()
