# Reproduction scope

The default entry point reads six aggregate JSON inputs and writes regenerated tables, figures and a new aggregate-regeneration receipt. It has no model-training or prediction command. All file writes follow explicit CLI calls. Importing the analysis modules does not regenerate outputs.

## Output mapping

Table 1 records the frozen S/P/C recipes. Table 2 uses within-crop equal-region RMSE and its relative contrasts from `SCORES.json`. Table 3 derives adverse counts from `SEASON_SUMMARY.json`. Supplementary Table S1 transcribes the 116 site-season C−S records in `ALL_CONTRASTS.json` at their stored precision. Figure 1 uses the same crop-level regional macro contrasts as Table 2. Figure 2 uses the same site-season C−S values as S1.

Crop-level post hoc rows in `ALL_CONTRASTS.json` pool individual days within a crop. They answer a different aggregation question from the equal-region macro scores used in the primary estimand. The renderer and validator use the declared aggregation for each output.

## Source and historical execution

`config/analysis_protocol.json` records eight inputs, Ridge and random-forest settings, crop weights and scaling, validation axes and the primary estimand. `config/cohort_split_summary.json` records aggregate coverage, the 15 executed folds and hashes of the original cohort and memberships. The original execution fit 120 estimators and produced 52,284 repeated OOF records. No fitting, new prediction or model replay is part of this aggregate release preparation.

The archived model environment was Python 3.11.13, scikit-learn 1.9.0, pandas 2.3.3 and NumPy 2.4.6. Rendering versions are recorded separately in `environment/verified_runtime.json`. The package does not reconstruct provider-native observations or refit the historical models. Such work would require the exact original inputs, approved source access and the full execution environment.

## Observation reuse

Of 1,912 rice site-days, 1,510 overlap the companion within-site predictor comparison and 1,076 overlap the three reported test-tower validations. The unique union contains 1,628 days. The 2,445 maize days include the companion principal 642 cases and the 2,431-case point-input reference comparison. The principal cases include 480 hindcast training cases. The 437 hindcast evaluation cases from 2010–2011 do not overlap this panel. These sets overlap each other and should not be summed. Shared observations retain their original source attribution.

## Layout portability

Use Arial and the recorded rendering dependency versions to reproduce the submitted TIFFs. The software records the resolved font filename and SHA-256 in its receipt. Arial is supplied by the local system and retains its own terms. When a fallback font is used, review bounding-box and contrast checks and inspect the final images at the intended publication width.

CSV and Markdown/HTML table values remain independent of the plotting font. Small raster differences across environments should be assessed separately from changes in plotted numeric values.
