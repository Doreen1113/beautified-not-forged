#!/bin/bash
# Ship the RU line's data and code to the Ubuntu box (same relative layout under ~/AIGC_sbifix).
set -e
L=/c/My_Project/AIGC; R=gsplat-ubuntu; RB='~/AIGC_sbifix'
ssh -n $R "mkdir -p $RB/ffhq_originals $RB/FFHQ_four_process $RB/FFHQ_megvii_four_process $RB/FFHQ_ali_process $RB/results/research/retouch_unified_20260929 $RB/results/research/alipair_zeroshot_20260929 $RB/checkpoints/research/retouch_unified_20260929"
scp -q -r $L/ffhq_originals/Part7 $L/ffhq_originals/Part2 $R:$RB/ffhq_originals/
scp -q -r $L/FFHQ_four_process/Whitening_Smoothing_FaceLifting_EyeEnlarging $L/FFHQ_four_process/four_process.txt $L/FFHQ_four_process/clean_output $R:$RB/FFHQ_four_process/
scp -q -r $L/FFHQ_megvii_four_process/Whitening_Smoothing_FaceLifting_EyeEnlarging $L/FFHQ_megvii_four_process/clean_output $R:$RB/FFHQ_megvii_four_process/
for d in EyeEnlarging FaceLifting Smoothing Whitening; do for lv in 30 60 90; do scp -q -r $L/FFHQ_ali_process/${d}_${lv} $R:$RB/FFHQ_ali_process/; done; done
scp -q $L/results/research/retouch_unified_20260929/*.py $L/results/research/retouch_unified_20260929/*.tsv $L/results/research/retouch_unified_20260929/*.json $L/results/research/retouch_unified_20260929/*.npz $R:$RB/results/research/retouch_unified_20260929/
scp -q $L/results/research/alipair_zeroshot_20260929/boxes.json $R:$RB/results/research/alipair_zeroshot_20260929/
echo shipped
