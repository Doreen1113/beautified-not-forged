# Addendum 60: dedicated operation classifiers, trained on Megvii + Tencent components (FFHQ Part7), tested on Alibaba (FFHQ Part2)

| op | AUROC L30 | L60 | L90 [CI] | paired rank L90 % | L90 after JPEG | cross AUROC on other ops' L90 renders |
|---|---|---|---|---|---|---|
| white | 0.5794 | 0.6327 | 0.69 [0.6808, 0.6992] | 86.1 | 0.7661 | {'eye': 0.5347, 'jaw': 0.5396, 'white': 0.69, 'smooth': 0.5139} |
| eye | 0.6406 | 0.6841 | 0.7218 [0.7133, 0.7305] | 94.9 | 0.5622 | {'eye': 0.7218, 'jaw': 0.5133, 'white': 0.5171, 'smooth': 0.7571} |
| jaw | 0.6362 | 0.6719 | 0.703 [0.696, 0.71] | 97.8 | 0.6534 | {'eye': 0.5477, 'jaw': 0.703, 'white': 0.5263, 'smooth': 0.6776} |
| smooth | 0.9872 | 0.9992 | 0.9987 [0.9983, 0.9991] | 100.0 | 0.9941 | {'eye': 0.5931, 'jaw': 0.6112, 'white': 0.708, 'smooth': 0.9987} |
