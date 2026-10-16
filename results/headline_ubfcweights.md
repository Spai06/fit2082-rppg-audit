# Headline results - ubfcweights

Settings: windows=windows_UBFC-rPPG, drop_post_exercise=False, RQ3 response=log_abs_err

Windows: {'windows_in': 5280, 'after_common_windows': 5280, 'subjects': 33, 'videos': 660}

## RQ1b - MMPD overall (30 s windows)

| family     | method           |   n_subjects |   n_windows |   MAE |   MAE_CI_low |   MAE_CI_high |   RMSE |   MAPE |   Pearson |   SNR_dB |   MAE_subject |   Pearson_subject |
|:-----------|:-----------------|-------------:|------------:|------:|-------------:|--------------:|-------:|-------:|----------:|---------:|--------------:|------------------:|
| baseline   | Mean-HR baseline |           33 |        1320 | 12.77 |        10.93 |         14.8  |  16.15 |  15.86 |     -0.7  |   nan    |         12.77 |             -1    |
| supervised | PhysNet          |           33 |        1320 | 10.8  |         8.72 |         13.04 |  17.28 |  13.36 |      0.32 |    -4.18 |         10.8  |              0.59 |
| supervised | EfficientPhys    |           33 |        1320 | 14.09 |        11.43 |         17.05 |  22.06 |  15.35 |      0.2  |    -4.34 |         14.09 |              0.51 |
| supervised | TS-CAN           |           33 |        1320 | 14.69 |        12.02 |         17.67 |  22.48 |  15.96 |      0.19 |    -4.7  |         14.69 |              0.53 |
| supervised | DeepPhys         |           33 |        1320 | 17.93 |        14.87 |         21.4  |  25.72 |  19.49 |      0.09 |    -5.48 |         17.93 |              0.3  |


## Group sizes (count before interpreting anything)

|            |   n_subjects |
|:-----------|-------------:|
| (3, '3')   |           17 |
| (4, '4-6') |            4 |
| (5, '4-6') |            6 |
| (6, '4-6') |            6 |


Videos per lighting x motion cell:

| light        |   Rotation |   Stationary |   Talking |   Walking |
|:-------------|-----------:|-------------:|----------:|----------:|
| Incandescent |         33 |           66 |        33 |        33 |
| LED-high     |         33 |           66 |        33 |        33 |
| LED-low      |         33 |           66 |        33 |        33 |
| Nature       |         33 |           66 |        33 |        33 |


## RQ2 - tests (Holm-corrected across methods x factors)

| method        | factor     | test                                |    stat |      p | n        | effect                                                             |   p_holm |
|:--------------|:-----------|:------------------------------------|--------:|-------:|:---------|:-------------------------------------------------------------------|---------:|
| DeepPhys      | skin_group | Mann-Whitney U (subject MAE)        | 39.5    | 0.0005 | 17 vs 16 | 4-6 minus 3: +10.95 bpm                                            |   0.0033 |
| DeepPhys      | light      | Friedman (paired, subject x light)  |  5.936  | 0.1148 | 33       | Incandescent=16.84 / LED-high=17.70 / LED-low=17.03 / Nature=20.15 |   0.4591 |
| DeepPhys      | motion     | Friedman (paired, subject x motion) | 66.5488 | 0      | 33       | Rotation=16.44 / Stationary=14.94 / Talking=10.76 / Walking=32.58  |   0      |
| EfficientPhys | skin_group | Mann-Whitney U (subject MAE)        | 24      | 0.0001 | 17 vs 16 | 4-6 minus 3: +10.59 bpm                                            |   0.0005 |
| EfficientPhys | light      | Friedman (paired, subject x light)  |  5.2774 | 0.1526 | 33       | Incandescent=12.99 / LED-high=13.17 / LED-low=14.34 / Nature=15.86 |   0.4591 |
| EfficientPhys | motion     | Friedman (paired, subject x motion) | 54.0821 | 0      | 33       | Rotation=12.08 / Stationary=11.58 / Talking=7.84 / Walking=27.37   |   0      |
| PhysNet       | skin_group | Mann-Whitney U (subject MAE)        | 45      | 0.0011 | 17 vs 16 | 4-6 minus 3: +6.53 bpm                                             |   0.0056 |
| PhysNet       | light      | Friedman (paired, subject x light)  |  3.997  | 0.2618 | 33       | Incandescent=10.67 / LED-high=9.84 / LED-low=10.76 / Nature=11.92  |   0.5236 |
| PhysNet       | motion     | Friedman (paired, subject x motion) | 25.0884 | 0      | 33       | Rotation=10.05 / Stationary=9.99 / Talking=7.60 / Walking=16.35    |   0.0001 |
| TS-CAN        | skin_group | Mann-Whitney U (subject MAE)        | 31      | 0.0002 | 17 vs 16 | 4-6 minus 3: +9.77 bpm                                             |   0.0012 |
| TS-CAN        | light      | Friedman (paired, subject x light)  |  3.0823 | 0.3791 | 33       | Incandescent=14.01 / LED-high=14.70 / LED-low=13.93 / Nature=16.10 |   0.5236 |
| TS-CAN        | motion     | Friedman (paired, subject x motion) | 48.8909 | 0      | 33       | Rotation=13.09 / Stationary=13.16 / Talking=9.09 / Walking=24.92   |   0      |


## RQ3 - mixed-effects variance attribution

| family     |   n_subjects |   n_windows |   R2_marginal |   R2_conditional |   subject_variance_share |   dR2_skin tone |   LRT_p_skin tone |   dR2_light |   LRT_p_light |   dR2_motion |   LRT_p_motion |   dR2_exercise |   LRT_p_exercise |
|:-----------|-------------:|------------:|--------------:|-----------------:|-------------------------:|----------------:|------------------:|------------:|--------------:|-------------:|---------------:|---------------:|-----------------:|
| supervised |           33 |        5280 |        0.2927 |           0.3657 |                    0.073 |          0.0947 |                 0 |      0.0023 |        0.0003 |       0.1799 |              0 |         0.0378 |                0 |


### Do supervised and unsupervised methods react the same way? (LRT)




## Face-crop outcome per video

| face_crop   |   count |
|:------------|--------:|
| native      |     556 |
| upscaled    |      65 |
| whole-frame |      39 |

