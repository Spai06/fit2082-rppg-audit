# Headline results - noexercise

Settings: windows=windows, drop_post_exercise=True, RQ3 response=log_abs_err

Windows: {'windows_in': 13200, 'after_dropping_post_exercise': 10560, 'after_common_windows': 10560, 'subjects': 33, 'videos': 528}

## RQ1b - MMPD overall (30 s windows)

| family       | method           |   n_subjects |   n_windows |   MAE |   MAE_CI_low |   MAE_CI_high |   RMSE |   MAPE |   Pearson |   SNR_dB |   MAE_subject |   Pearson_subject |
|:-------------|:-----------------|-------------:|------------:|------:|-------------:|--------------:|-------:|-------:|----------:|---------:|--------------:|------------------:|
| baseline     | Mean-HR baseline |           33 |        1056 | 11.35 |         9.42 |         13.48 |  14.34 |  14.65 |     -0.78 |   nan    |         11.35 |             -1    |
| supervised   | TS-CAN           |           33 |        1056 | 13.42 |        10.97 |         16    |  20.35 |  15.12 |      0.18 |    -4.6  |         13.42 |              0.69 |
| supervised   | PhysNet          |           33 |        1056 | 13.55 |        11.29 |         16.1  |  19.6  |  15.77 |      0.15 |    -5.26 |         13.55 |              0.54 |
| supervised   | EfficientPhys    |           33 |        1056 | 13.62 |        11.26 |         16.15 |  20.4  |  15.5  |      0.16 |    -4.73 |         13.62 |              0.66 |
| supervised   | DeepPhys         |           33 |        1056 | 16    |        13.45 |         18.86 |  23.23 |  18.09 |      0.02 |    -5.34 |         16    |              0.49 |
| unsupervised | POS              |           33 |        1056 | 11.79 |         9.94 |         13.83 |  16.53 |  14.55 |      0.21 |    -5.27 |         11.79 |              0.55 |
| unsupervised | CHROM            |           33 |        1056 | 12.8  |        11    |         14.74 |  17.44 |  15.87 |      0.11 |    -5.32 |         12.8  |              0.44 |
| unsupervised | LGI              |           33 |        1056 | 16.3  |        13.97 |         18.91 |  21.97 |  19.02 |      0.05 |    -6.08 |         16.3  |              0.38 |
| unsupervised | OMIT             |           33 |        1056 | 16.31 |        13.93 |         18.98 |  22.02 |  19.02 |      0.05 |    -6.07 |         16.31 |              0.37 |
| unsupervised | PBV              |           33 |        1056 | 17.01 |        14.71 |         19.61 |  22.36 |  19.94 |      0.01 |    -6.4  |         17.01 |              0.3  |
| unsupervised | GREEN            |           33 |        1056 | 18.56 |        16.02 |         21.39 |  24.25 |  21.47 |      0.02 |    -6.53 |         18.56 |              0.45 |


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
| Incandescent |         33 |           33 |        33 |        33 |
| LED-high     |         33 |           33 |        33 |        33 |
| LED-low      |         33 |           33 |        33 |        33 |
| Nature       |         33 |           33 |        33 |        33 |


## RQ1c - our per-group MAE vs the MMPD paper's Table II (classical methods)

Their protocol differs (whole 1-minute videos, their own filter settings), so compare the pattern, not the absolute values.

| factor    |   n_cells |   Spearman_rho |   our_mean |   published_mean |
|:----------|----------:|---------------:|-----------:|-----------------:|
| light     |        17 |          0.92  |     14.704 |           11.726 |
| motion    |        20 |          0.988 |     15.292 |           14.19  |
| skin_tone |        20 |          0.91  |     17.091 |           13.1   |


## RQ2 - tests (Holm-corrected across methods x factors)

| method        | factor     | test                                |    stat |      p | n        | effect                                                             |   p_holm |
|:--------------|:-----------|:------------------------------------|--------:|-------:|:---------|:-------------------------------------------------------------------|---------:|
| CHROM         | skin_group | Mann-Whitney U (subject MAE)        | 66      | 0.0123 | 17 vs 16 | 4-6 minus 3: +5.17 bpm                                             |   0.0859 |
| CHROM         | light      | Friedman (paired, subject x light)  |  7.1818 | 0.0663 | 33       | Incandescent=11.44 / LED-high=12.39 / LED-low=13.28 / Nature=14.10 |   0.2653 |
| CHROM         | motion     | Friedman (paired, subject x motion) | 20.0334 | 0.0002 | 33       | Rotation=10.42 / Stationary=12.68 / Talking=10.83 / Walking=17.29  |   0.0028 |
| DeepPhys      | skin_group | Mann-Whitney U (subject MAE)        | 36.5    | 0.0004 | 17 vs 16 | 4-6 minus 3: +8.84 bpm                                             |   0.0054 |
| DeepPhys      | light      | Friedman (paired, subject x light)  |  2.7447 | 0.4327 | 33       | Incandescent=15.34 / LED-high=15.57 / LED-low=15.10 / Nature=17.96 |   0.5698 |
| DeepPhys      | motion     | Friedman (paired, subject x motion) | 68.2661 | 0      | 33       | Rotation=13.84 / Stationary=7.83 / Talking=9.78 / Walking=32.53    |   0      |
| EfficientPhys | skin_group | Mann-Whitney U (subject MAE)        | 26      | 0.0001 | 17 vs 16 | 4-6 minus 3: +9.10 bpm                                             |   0.0014 |
| EfficientPhys | light      | Friedman (paired, subject x light)  |  8.5913 | 0.0352 | 33       | Incandescent=13.06 / LED-high=13.08 / LED-low=12.74 / Nature=15.59 |   0.1762 |
| EfficientPhys | motion     | Friedman (paired, subject x motion) | 60.9695 | 0      | 33       | Rotation=11.35 / Stationary=7.62 / Talking=8.80 / Walking=26.71    |   0      |
| GREEN         | skin_group | Mann-Whitney U (subject MAE)        | 60.5    | 0.0069 | 17 vs 16 | 4-6 minus 3: +7.06 bpm                                             |   0.062  |
| GREEN         | light      | Friedman (paired, subject x light)  | 11.6595 | 0.0086 | 33       | Incandescent=18.06 / LED-high=17.95 / LED-low=16.74 / Nature=21.49 |   0.0692 |
| GREEN         | motion     | Friedman (paired, subject x motion) | 46.4451 | 0      | 33       | Rotation=15.19 / Stationary=13.00 / Talking=15.68 / Walking=30.36  |   0      |
| LGI           | skin_group | Mann-Whitney U (subject MAE)        | 41      | 0.0007 | 17 vs 16 | 4-6 minus 3: +7.69 bpm                                             |   0.0081 |
| LGI           | light      | Friedman (paired, subject x light)  | 22.1159 | 0.0001 | 33       | Incandescent=15.09 / LED-high=14.12 / LED-low=15.86 / Nature=20.12 |   0.0012 |
| LGI           | motion     | Friedman (paired, subject x motion) | 46.7818 | 0      | 33       | Rotation=11.51 / Stationary=12.69 / Talking=13.52 / Walking=27.49  |   0      |
| OMIT          | skin_group | Mann-Whitney U (subject MAE)        | 41      | 0.0007 | 17 vs 16 | 4-6 minus 3: +7.98 bpm                                             |   0.0081 |
| OMIT          | light      | Friedman (paired, subject x light)  | 24.0826 | 0      | 33       | Incandescent=14.91 / LED-high=14.45 / LED-low=15.76 / Nature=20.11 |   0.0005 |
| OMIT          | motion     | Friedman (paired, subject x motion) | 47.1155 | 0      | 33       | Rotation=11.52 / Stationary=12.62 / Talking=13.64 / Walking=27.46  |   0      |
| PBV           | skin_group | Mann-Whitney U (subject MAE)        | 40.5    | 0.0006 | 17 vs 16 | 4-6 minus 3: +7.52 bpm                                             |   0.0081 |
| PBV           | light      | Friedman (paired, subject x light)  |  5.4421 | 0.1421 | 33       | Incandescent=16.00 / LED-high=16.85 / LED-low=15.45 / Nature=19.74 |   0.4264 |
| PBV           | motion     | Friedman (paired, subject x motion) | 49.304  | 0      | 33       | Rotation=13.16 / Stationary=12.56 / Talking=15.03 / Walking=27.30  |   0      |
| POS           | skin_group | Mann-Whitney U (subject MAE)        | 49      | 0.0018 | 17 vs 16 | 4-6 minus 3: +6.11 bpm                                             |   0.0183 |
| POS           | light      | Friedman (paired, subject x light)  | 19.789  | 0.0002 | 33       | Incandescent=10.91 / LED-high=10.50 / LED-low=11.83 / Nature=13.90 |   0.003  |
| POS           | motion     | Friedman (paired, subject x motion) | 29.8436 | 0      | 33       | Rotation=9.72 / Stationary=11.33 / Talking=10.31 / Walking=15.79   |   0      |
| PhysNet       | skin_group | Mann-Whitney U (subject MAE)        | 15      | 0      | 17 vs 16 | 4-6 minus 3: +9.30 bpm                                             |   0.0003 |
| PhysNet       | light      | Friedman (paired, subject x light)  |  9.2936 | 0.0256 | 33       | Incandescent=13.06 / LED-high=11.99 / LED-low=13.35 / Nature=15.81 |   0.1538 |
| PhysNet       | motion     | Friedman (paired, subject x motion) | 50.2454 | 0      | 33       | Rotation=11.93 / Stationary=8.13 / Talking=10.39 / Walking=23.77   |   0      |
| TS-CAN        | skin_group | Mann-Whitney U (subject MAE)        | 39      | 0.0005 | 17 vs 16 | 4-6 minus 3: +8.78 bpm                                             |   0.0071 |
| TS-CAN        | light      | Friedman (paired, subject x light)  |  3.7914 | 0.2849 | 33       | Incandescent=12.34 / LED-high=12.92 / LED-low=12.78 / Nature=15.62 |   0.5698 |
| TS-CAN        | motion     | Friedman (paired, subject x motion) | 52.2713 | 0      | 33       | Rotation=11.17 / Stationary=7.32 / Talking=8.65 / Walking=26.52    |   0      |


## RQ3 - model could not be fitted: RuntimeError('Mixed model failed with every optimiser: log_abs_err ~ skin_dark + light_LED_high + light_Incandescent + light_Nature + motion_Rotation + motion_Talking + motion_Walking + post_exercise + C(method)')

## Face-crop outcome per video

| face_crop   |   count |
|:------------|--------:|
| native      |     556 |
| upscaled    |      65 |
| whole-frame |      39 |

