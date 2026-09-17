# SteadyVox – Multi‑Dataset Model Comparison

> **Disclaimer:** Research screening tool only — not a medical diagnosis.

## Classification Results

| Dataset | Model | Accuracy | F1 | Precision | Recall | ROC‑AUC |
|---------|-------|----------|-----|-----------|--------|---------|
| Oxford | Random Forest | 0.9487 | 0.9501 | 0.9573 | 0.9487 | 0.9862 |
| Oxford | MLP Classifier | 0.9487 | 0.9487 | 0.9487 | 0.9487 | 0.9931 |

## Regression Results

| Dataset | Model | RMSE | MAE | R² |
|---------|-------|------|-----|----|
| Telemonitoring (motor_updrs) | Gradient Boosting | 6.6932 | 5.4178 | 0.2981 |
| Telemonitoring (motor_updrs) | MLP Regressor | 6.3818 | 5.0499 | 0.3619 |
| Telemonitoring (total_updrs) | Gradient Boosting | 8.7888 | 6.9338 | 0.3029 |
| Telemonitoring (total_updrs) | MLP Regressor | 8.2183 | 6.3457 | 0.3905 |

## Notes

- **Oxford** (UCI ID 174): 195 instances, 23 features, binary classification (status: 0=healthy, 1=PD)
- **Istanbul** (UCI ID 470): 252 instances, multiple voice features, binary classification
- **Telemonitoring** (UCI ID 189): 5,875 instances, 16 voice features, regression targets: motor_UPDRS and total_UPDRS
- Datasets are kept **separate** (no merging) to preserve experimental integrity.
- All models use seed=42, test_size=0.2, StandardScaler on training data only.
- Classification uses stratified splitting; regression uses random splitting.

## Citations

1. Little, M.A., McSharry, P.E., Roberts, S.J., Costello, D.A.E., Moroz, I.M. (2007). "Exploiting Nonlinear Recurrence and Fractal Scaling Properties for Voice Disorder Detection". BioMedical Engineering OnLine, 6:23.
2. Sakar, C.O., et al. (2019). "A Comparative Analysis of Speech Signal Processing Algorithms for Parkinson's Disease Classification and the Use of the Tunable Q-Factor Wavelet Transform". Applied Soft Computing, 74, 255-263.
3. Tsanas, A., Little, M.A., McSharry, P.E., Ramig, L.O. (2010). "Accurate Telemonitoring of Parkinson's Disease Progression by Noninvasive Speech Tests". IEEE TBME, 57(4), 884-893.
