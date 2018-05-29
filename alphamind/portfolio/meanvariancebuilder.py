# -*- coding: utf-8 -*-
"""
Created on 2017-6-27

@author: cheng.li
"""

import numpy as np
from typing import Union
from typing import Tuple
from typing import Optional
from alphamind.cython.optimizers import QPOptimizer
from alphamind.cython.optimizers import CVOptimizer
from alphamind.portfolio.riskmodel import RiskModel
from alphamind.portfolio.riskmodel import FullRiskModel
from alphamind.portfolio.riskmodel import FactorRiskModel


def _create_bounds(lbound,
                   ubound,
                   bm,
                   risk_exposure,
                   risk_target):
    lbound = lbound - bm
    ubound = ubound - bm

    if risk_exposure is not None:
        cons_mat = risk_exposure.T
        bm_risk = cons_mat @ bm

        clbound = risk_target[0] - bm_risk
        cubound = risk_target[1] - bm_risk
    else:
        cons_mat = None
        clbound = None
        cubound = None

    return lbound, ubound, cons_mat, clbound, cubound


def _create_result(optimizer, bm):
    if optimizer.status() == 0 or optimizer.status() == 1:
        status = 'optimal'
    else:
        status = optimizer.status()

    return status, optimizer.feval(), optimizer.x_value() + bm


def mean_variance_builder(er: np.ndarray,
                          risk_model: RiskModel,
                          bm: np.ndarray,
                          lbound: Union[np.ndarray, float],
                          ubound: Union[np.ndarray, float],
                          risk_exposure: Optional[np.ndarray],
                          risk_target: Optional[Tuple[np.ndarray, np.ndarray]],
                          lam: float=1.) -> Tuple[str, float, np.ndarray]:
    lbound, ubound, cons_mat, clbound, cubound = _create_bounds(lbound, ubound, bm, risk_exposure, risk_target)

    if isinstance(risk_model, FullRiskModel):
        cov = risk_model.get_cov()
        optimizer = QPOptimizer(er,
                                cov,
                                lbound,
                                ubound,
                                cons_mat,
                                clbound,
                                cubound,
                                lam)
    elif isinstance(risk_model, FactorRiskModel):
        cov = None
        factor_cov = risk_model.get_factor_cov()
        factor_loading = risk_model.get_risk_exp()
        idsync = risk_model.get_idsync()
        optimizer = QPOptimizer(er,
                                cov,
                                lbound,
                                ubound,
                                cons_mat,
                                clbound,
                                cubound,
                                lam,
                                factor_cov,
                                factor_loading,
                                idsync)
    else:
        raise ValueError("{0} is not recognized as valid risk model".format(risk_model))

    return _create_result(optimizer, bm)


def target_vol_builder(er: np.ndarray,
                       risk_model: RiskModel,
                       bm: np.ndarray,
                       lbound: Union[np.ndarray, float],
                       ubound: Union[np.ndarray, float],
                       risk_exposure: Optional[np.ndarray],
                       risk_target: Optional[Tuple[np.ndarray, np.ndarray]],
                       vol_target: float = 1.)-> Tuple[str, float, np.ndarray]:
    lbound, ubound, cons_mat, clbound, cubound = _create_bounds(lbound, ubound, bm, risk_exposure, risk_target)

    if isinstance(risk_model, FullRiskModel):
        cov = risk_model.get_cov()
        optimizer = CVOptimizer(er,
                                cov,
                                lbound,
                                ubound,
                                cons_mat,
                                clbound,
                                cubound,
                                0.,
                                vol_target)
    elif isinstance(risk_model, FactorRiskModel):
        cov = None
        factor_cov = risk_model.get_factor_cov()
        factor_loading = risk_model.get_risk_exp()
        idsync = risk_model.get_idsync()
        optimizer = CVOptimizer(er,
                                cov,
                                lbound,
                                ubound,
                                cons_mat,
                                clbound,
                                cubound,
                                0.,
                                vol_target,
                                factor_cov,
                                factor_loading,
                                idsync)
    else:
        raise ValueError("{0} is not recognized as valid risk model".format(risk_model))

    return _create_result(optimizer, bm)



