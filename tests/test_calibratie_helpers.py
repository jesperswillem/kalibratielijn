import numpy as np
import pandas as pd
from scipy import stats

from src.calibratie_helpers import summarize_calibration


def test_perfecte_rechte_lijn():
    data = pd.DataFrame({
        "concentratie": [0, 1, 2, 3, 4],
        "respons": [1, 3, 5, 7, 9],
    })
    summary, detail = summarize_calibration(data)
    assert np.isclose(summary["a_intercept"], 1.0)
    assert np.isclose(summary["b_helling"], 2.0)
    assert np.isclose(summary["SS_residu"], 0.0)
    assert np.isclose(summary["r_kwadraat"], 1.0)


def test_vergelijken_met_scipy_linregress():
    data = pd.DataFrame({
        "concentratie": [0.1, 0.1, 0.2, 0.2, 0.3, 0.3],
        "respons": [0.101, 0.089, 0.212, 0.210, 0.312, 0.299],
    })
    summary, detail = summarize_calibration(data)
    linreg = stats.linregress(data["concentratie"], data["respons"])
    assert np.isclose(summary["a_intercept"], linreg.intercept)
    assert np.isclose(summary["b_helling"], linreg.slope)
    assert np.isclose(summary["correlatie_r"], linreg.rvalue)
