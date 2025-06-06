# OCR Benchmark Report

## Speed Benchmark

| File | Mistral Whole | Mistral WebAPI | Mistral Split | Mistral Split WebAPI | Datalab Whole |
|---|---|---|---|---|---|
| Report_mock.pdf | 2.06s | 3.78s | 6.32s | 1.74s | 4.56s |
| attention.pdf | 11.51s | 11.24s | 32.02s | 12.89s | 36.58s |
| PrimaryCircuit.pdf | 17.69s | 15.14s | 25.55s | 15.66s | 30.37s |
| CV - Yuxuan Wang.pdf | 3.19s | 2.62s | 7.56s | 2.83s | 8.33s |
| NBA.pdf | 17.85s | 21.64s | 42.69s | 10.99s | 45.5s |
| Diego_Maradona.pdf | 19.82s | 16.19s | 30.72s | 15.15s | 36.66s |
| 2021PVAG.pdf | 12.75s | 14.15s | 25.93s | 7.99s | 0s |

## Nb splitting 

| File | Mistral Whole | 2 parts | 4 parts | 8 parts | 16 parts |
|---|---|---|---|---|---|
| Report_mock.pdf | 2.06s | 2.22s | 1.74s | 3.87s | 3.28s |
| attention.pdf | 11.51s | 16.49s | 12.89s | 14.17s | 11.57s |
| PrimaryCircuit.pdf | 17.69s | 15.35s | 15.66s | 18.2s | 24.54s |
| CV - Yuxuan Wang.pdf | 3.19s | 2.61s | 2.83s | 2.59s | 2.11s |
| NBA.pdf | 17.85s | 14.39s | 10.99s | 12.94s | 17.37s |
| Diego_Maradona.pdf | 19.82s | 10.82s | 15.15s | 14.4s | 11.75s |
| 2021PVAG.pdf | 12.75s | 9.46s | 7.99s | 8.19s | 7.54s |

## Accuracy Benchmark (Similarity)

| File | Similarity |
|---|---|
| attention | 0.9305 |
| report_mock | 0.7857 |
| Diego_Maradona | 0.8408 |
| cv - yuxuan wang | 0.9762 |
| nba | 0.8441 |
| 2021pvag | 0.9380 |
| primarycircuit | 0.0642 |

