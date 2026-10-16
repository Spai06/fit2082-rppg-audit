# Headline results

Settings: windows=windows, drop_post_exercise=False, RQ3 response=log_abs_err

## RQ1a - UBFC-rPPG reproduction (whole video, FFT)

| method        |   MAE |   MAE_published |   MAE_diff |   RMSE |   MAPE |   Pearson |   Pearson_published |   SNR | within_tolerance   |
|:--------------|------:|----------------:|-----------:|-------:|-------:|----------:|--------------------:|------:|:-------------------|
| CHROM         |  3.98 |            4.06 |      -0.08 |   8.72 |   3.78 |      0.89 |                0.89 | -1.53 | yes                |
| DeepPhys      |  1.21 |            1.21 |       0    |   2.9  |   1.42 |      0.99 |                0.99 |  0.87 | yes                |
| EfficientPhys |  2.07 |            2.07 |       0    |   6.32 |   2.1  |      0.94 |                0.94 | -0.06 | yes                |
| GREEN         | 19.82 |           19.73 |       0.09 |  31.49 |  18.78 |      0.37 |                0.37 | -5.6  | yes                |
| ICA           | 14.7  |           16    |      -1.3  |  23.71 |  14.34 |      0.53 |                0.44 | -4.71 | yes                |
| LGI           | 15.8  |           15.8  |      -0    |  28.55 |  14.7  |      0.36 |                0.36 | -4.08 | yes                |
| OMIT          | 15.8  |          nan    |     nan    |  28.55 |  14.7  |      0.36 |              nan    | -4.09 | no published value |
| PBV           | 15.07 |           15.9  |      -0.83 |  25.27 |  14.38 |      0.5  |                0.48 | -4.59 | yes                |
| POS           |  4    |            4.08 |      -0.08 |   7.58 |   3.86 |      0.92 |                0.92 | -1.19 | yes                |
| PhysNet       |  1.63 |            0.98 |       0.65 |   3.79 |   1.68 |      0.98 |                0.99 | -0.89 | yes                |
| TS-CAN        |  1.3  |            1.3  |      -0    |   2.87 |   1.5  |      0.99 |                0.99 |  0.75 | yes                |


Windows: {'windows_in': 13200, 'after_common_windows': 13200, 'subjects': 33, 'videos': 660}

## RQ1b - MMPD overall (30 s windows)

| family       | method           |   n_subjects |   n_windows |   MAE |   MAE_CI_low |   MAE_CI_high |   RMSE |   MAPE |   Pearson |   SNR_dB |   MAE_subject |   Pearson_subject |
|:-------------|:-----------------|-------------:|------------:|------:|-------------:|--------------:|-------:|-------:|----------:|---------:|--------------:|------------------:|
| baseline     | Mean-HR baseline |           33 |        1320 | 12.77 |        10.93 |         14.8  |  16.15 |  15.86 |     -0.7  |   nan    |         12.77 |             -1    |
| supervised   | TS-CAN           |           33 |        1320 | 14.64 |        11.81 |         17.63 |  22.6  |  15.78 |      0.2  |    -4.65 |         14.64 |              0.53 |
| supervised   | PhysNet          |           33 |        1320 | 14.84 |        12.25 |         17.67 |  21.56 |  16.48 |      0.19 |    -5.41 |         14.84 |              0.44 |
| supervised   | EfficientPhys    |           33 |        1320 | 14.99 |        12.33 |         17.89 |  22.61 |  16.27 |      0.19 |    -4.83 |         14.99 |              0.55 |
| supervised   | DeepPhys         |           33 |        1320 | 17.46 |        14.54 |         20.7  |  25.39 |  18.93 |      0.07 |    -5.41 |         17.46 |              0.34 |
| unsupervised | POS              |           33 |        1320 | 13.04 |        11.05 |         15.27 |  18.5  |  15.14 |      0.2  |    -5.56 |         13.04 |              0.55 |
| unsupervised | CHROM            |           33 |        1320 | 14.36 |        12.34 |         16.54 |  19.78 |  16.67 |      0.09 |    -5.69 |         14.36 |              0.42 |
| unsupervised | LGI              |           33 |        1320 | 17.78 |        15.24 |         20.62 |  24.03 |  19.81 |      0.09 |    -6.41 |         17.78 |              0.36 |
| unsupervised | OMIT             |           33 |        1320 | 17.89 |        15.3  |         20.76 |  24.16 |  19.92 |      0.08 |    -6.4  |         17.89 |              0.35 |
| unsupervised | PBV              |           33 |        1320 | 19.17 |        16.71 |         21.9  |  25.07 |  21.43 |      0.01 |    -6.79 |         19.17 |              0.33 |
| unsupervised | GREEN            |           33 |        1320 | 20.72 |        17.85 |         23.85 |  27.26 |  22.94 |      0.01 |    -6.78 |         20.72 |              0.26 |


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


## RQ1c - our per-group MAE vs the MMPD paper's Table II (classical methods)

Their protocol differs (whole 1-minute videos, their own filter settings), so compare the pattern, not the absolute values.

| factor    |   n_cells |   Spearman_rho |   our_mean |   published_mean |
|:----------|----------:|---------------:|-----------:|-----------------:|
| light     |        17 |          0.948 |     16.419 |           11.726 |
| motion    |        20 |          0.795 |     16.723 |           14.19  |
| skin_tone |        20 |          0.929 |     19.092 |           13.1   |


## RQ2 - tests (Holm-corrected across methods x factors)

| method        | factor     | test                                |    stat |      p | n        | effect                                                             |   p_holm |
|:--------------|:-----------|:------------------------------------|--------:|-------:|:---------|:-------------------------------------------------------------------|---------:|
| CHROM         | skin_group | Mann-Whitney U (subject MAE)        | 49.5    | 0.0019 | 17 vs 16 | 4-6 minus 3: +6.48 bpm                                             |   0.0214 |
| CHROM         | light      | Friedman (paired, subject x light)  |  6.3556 | 0.0955 | 33       | Incandescent=12.41 / LED-high=14.06 / LED-low=15.22 / Nature=15.75 |   0.5732 |
| CHROM         | motion     | Friedman (paired, subject x motion) | 33.247  | 0      | 33       | Rotation=10.42 / Stationary=16.63 / Talking=10.83 / Walking=17.29  |   0      |
| DeepPhys      | skin_group | Mann-Whitney U (subject MAE)        | 35      | 0.0003 | 17 vs 16 | 4-6 minus 3: +10.48 bpm                                            |   0.0044 |
| DeepPhys      | light      | Friedman (paired, subject x light)  |  4.3313 | 0.2278 | 33       | Incandescent=16.50 / LED-high=17.08 / LED-low=16.67 / Nature=19.60 |   0.6505 |
| DeepPhys      | motion     | Friedman (paired, subject x motion) | 70.4954 | 0      | 33       | Rotation=13.84 / Stationary=15.58 / Talking=9.78 / Walking=32.53   |   0      |
| EfficientPhys | skin_group | Mann-Whitney U (subject MAE)        | 19      | 0      | 17 vs 16 | 4-6 minus 3: +11.06 bpm                                            |   0.0005 |
| EfficientPhys | light      | Friedman (paired, subject x light)  |  4.9149 | 0.1781 | 33       | Incandescent=14.06 / LED-high=14.56 / LED-low=14.33 / Nature=16.99 |   0.6505 |
| EfficientPhys | motion     | Friedman (paired, subject x motion) | 59.5897 | 0      | 33       | Rotation=11.35 / Stationary=14.04 / Talking=8.80 / Walking=26.71   |   0      |
| GREEN         | skin_group | Mann-Whitney U (subject MAE)        | 57      | 0.0047 | 17 vs 16 | 4-6 minus 3: +8.75 bpm                                             |   0.0375 |
| GREEN         | light      | Friedman (paired, subject x light)  |  9.7822 | 0.0205 | 33       | Incandescent=19.99 / LED-high=20.20 / LED-low=19.46 / Nature=23.22 |   0.1436 |
| GREEN         | motion     | Friedman (paired, subject x motion) | 48.8232 | 0      | 33       | Rotation=15.19 / Stationary=21.18 / Talking=15.68 / Walking=30.36  |   0      |
| LGI           | skin_group | Mann-Whitney U (subject MAE)        | 41      | 0.0007 | 17 vs 16 | 4-6 minus 3: +8.71 bpm                                             |   0.008  |
| LGI           | light      | Friedman (paired, subject x light)  | 20.5258 | 0.0001 | 33       | Incandescent=16.41 / LED-high=15.63 / LED-low=17.70 / Nature=21.40 |   0.0024 |
| LGI           | motion     | Friedman (paired, subject x motion) | 53.2979 | 0      | 33       | Rotation=11.51 / Stationary=18.20 / Talking=13.52 / Walking=27.49  |   0      |
| OMIT          | skin_group | Mann-Whitney U (subject MAE)        | 40      | 0.0006 | 17 vs 16 | 4-6 minus 3: +8.94 bpm                                             |   0.0076 |
| OMIT          | light      | Friedman (paired, subject x light)  | 18.3739 | 0.0004 | 33       | Incandescent=16.26 / LED-high=16.15 / LED-low=17.70 / Nature=21.43 |   0.0052 |
| OMIT          | motion     | Friedman (paired, subject x motion) | 49.9091 | 0      | 33       | Rotation=11.52 / Stationary=18.41 / Talking=13.64 / Walking=27.46  |   0      |
| PBV           | skin_group | Mann-Whitney U (subject MAE)        | 49.5    | 0.0019 | 17 vs 16 | 4-6 minus 3: +8.10 bpm                                             |   0.0214 |
| PBV           | light      | Friedman (paired, subject x light)  |  5.1284 | 0.1626 | 33       | Incandescent=18.20 / LED-high=19.08 / LED-low=17.85 / Nature=21.54 |   0.6505 |
| PBV           | motion     | Friedman (paired, subject x motion) | 55.9455 | 0      | 33       | Rotation=13.16 / Stationary=20.18 / Talking=15.03 / Walking=27.30  |   0      |
| POS           | skin_group | Mann-Whitney U (subject MAE)        | 33      | 0.0002 | 17 vs 16 | 4-6 minus 3: +7.18 bpm                                             |   0.0035 |
| POS           | light      | Friedman (paired, subject x light)  | 14.4512 | 0.0024 | 33       | Incandescent=11.83 / LED-high=11.72 / LED-low=13.34 / Nature=15.27 |   0.0214 |
| POS           | motion     | Friedman (paired, subject x motion) | 35.8073 | 0      | 33       | Rotation=9.72 / Stationary=14.69 / Talking=10.31 / Walking=15.79   |   0      |
| PhysNet       | skin_group | Mann-Whitney U (subject MAE)        | 15      | 0      | 17 vs 16 | 4-6 minus 3: +10.82 bpm                                            |   0.0003 |
| PhysNet       | light      | Friedman (paired, subject x light)  |  5.9354 | 0.1148 | 33       | Incandescent=13.92 / LED-high=13.33 / LED-low=14.85 / Nature=17.25 |   0.574  |
| PhysNet       | motion     | Friedman (paired, subject x motion) | 43.7393 | 0      | 33       | Rotation=11.93 / Stationary=14.05 / Talking=10.39 / Walking=23.77  |   0      |
| TS-CAN        | skin_group | Mann-Whitney U (subject MAE)        | 30.5    | 0.0002 | 17 vs 16 | 4-6 minus 3: +10.72 bpm                                            |   0.0026 |
| TS-CAN        | light      | Friedman (paired, subject x light)  |  3.5818 | 0.3103 | 33       | Incandescent=13.17 / LED-high=14.27 / LED-low=14.60 / Nature=16.53 |   0.6505 |
| TS-CAN        | motion     | Friedman (paired, subject x motion) | 57.4559 | 0      | 33       | Rotation=11.17 / Stationary=13.43 / Talking=8.65 / Walking=26.52   |   0      |


## RQ3 - mixed-effects variance attribution

| family       |   n_subjects |   n_windows |   R2_marginal |   R2_conditional |   subject_variance_share |   dR2_skin tone |   LRT_p_skin tone |   dR2_light |   LRT_p_light |   dR2_motion |   LRT_p_motion |   dR2_exercise |   LRT_p_exercise |
|:-------------|-------------:|------------:|--------------:|-----------------:|-------------------------:|----------------:|------------------:|------------:|--------------:|-------------:|---------------:|---------------:|-----------------:|
| supervised   |           33 |        5280 |        0.3088 |           0.3973 |                   0.0884 |          0.1205 |                 0 |      0.0041 |             0 |       0.1741 |              0 |         0.0411 |                0 |
| unsupervised |           33 |        7920 |        0.2024 |           0.2737 |                   0.0713 |          0.0753 |                 0 |      0.0132 |             0 |       0.0757 |              0 |         0.0273 |                0 |


### Do supervised and unsupervised methods react the same way? (LRT)

| factor    | interaction        |   df |       LR |      p |
|:----------|:-------------------|-----:|---------:|-------:|
| skin tone | skin tone x family |    1 |  82.6997 | 0      |
| light     | light x family     |    3 |   7.3457 | 0.0617 |
| motion    | motion x family    |    3 | 311.24   | 0      |
| exercise  | exercise x family  |    1 |   7.1581 | 0.0075 |


## Face-crop outcome per video

| face_crop   |   count |
|:------------|--------:|
| native      |     556 |
| upscaled    |      65 |
| whole-frame |      39 |

