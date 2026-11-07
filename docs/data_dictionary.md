# Aggregate data dictionary

| File or field | Meaning and units |
|---|---|
| SCORES.json / metrics | RMSE, MAE, signed bias and NSE for the stored OOF groups, 456 rows |
| macro_region_rmse | Within-crop mean of the three regional RMSEs, 24 rows |
| crop_contrasts | Relative changes in the within-crop regional macro score, 24 rows |
| overall_contrasts | Arithmetic mean of the two unrounded crop percentages, 12 rows |
| ALL_CONTRASTS.json | 444 paired crop, region and site-season contrasts |
| SEASON_SUMMARY.json | 24 axis/model/crop/contrast summaries |
| CROSS_AXIS_SIGNS.json | Descriptive recurrence of adverse site-seasons across axes |
| FIGURE_SOURCE.json | Ordered points and site-season matrix used by the figures |
| TABLE_SOURCE.json | Archived table recipes and source values for provenance |
| INPUT_MANIFEST.json | SHA-256 of the six public aggregate input files |
| axis | cluster_loso or year_loyo |
| family | Ridge or RF |
| arm | S crop-specific, P unconditioned pooling, C crop-conditioned pooling |
| contrast | First arm minus comparator, for example C-S |
| n | Retained site-days in the specified aggregate group |
| site_season | Retained site-year subset, potentially only part of a growing season |
| rmse, mae, bias | g C m−2 d−1. Bias is prediction minus reference |
| nse | Dimensionless Nash–Sutcliffe efficiency |
| relative_percent, delta_percent | 100 × (arm RMSE / comparator RMSE − 1), percent |
| delta_rmse | Arm minus comparator RMSE, g C m−2 d−1 |
| delta_mse | Change in mean squared error, (g C m−2 d−1)² |
| delta_sse | Change in summed squared error, same squared units summed over n |
| delta_squared_bias | Change in squared mean signed error, squared GPP units |
| delta_centered_error_variance | Change in population centered residual variance, squared GPP units |
| worse_rmse, worse_mae | Strict increase using unrounded metric values on the same days |

Positive relative changes indicate higher RMSE for the first arm. Figure 2 rounds to one decimal place and preserves the sign of values that round to zero. S1 retains the full stored numeric precision. Table 2 reports RMSE to four decimal places and percentages to two decimal places.
