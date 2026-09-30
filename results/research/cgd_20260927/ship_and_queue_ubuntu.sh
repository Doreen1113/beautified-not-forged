#!/bin/bash
# Wait for local part-edit generation (train donor + train sd) to finish, ship part edits + code to Ubuntu,
# then queue HYBPE and MASK arms after SUP-F ends. Logs: ship.log on this machine, ~/AIGC_sbifix/results/research/cgd_20260927/*.log there.
cd /c/My_Project/AIGC
PE=results/research/partedit_20260927
until grep -q "^DONE" $PE/gen_train_donor.log 2>/dev/null && grep -q "^DONE" $PE/gen_train_sd.log 2>/dev/null; do sleep 300; done
echo "generation done $(date)"
tar -cf - ffpp_partedit/train $PE/manifest_train_donor.tsv $PE/manifest_train_sd.tsv $PE/part_edit_gen.py \
    results/research/cgd_20260927/train_cgd.py docs/paper_v2/occlusion_regions.py \
  | ssh gsplat-ubuntu 'tar -xf - -C ~/AIGC_sbifix && echo shipped'
# train_cgd imports docs/paper_v2/make_figures via occlusion_regions? no: part_edit_gen imports occlusion_regions (index sets only) - not needed by train_cgd.
ssh gsplat-ubuntu 'cd ~/AIGC_sbifix/results/research/cgd_20260927 && cat > run_arms.sh <<EOF
#!/bin/bash
while pgrep -f "train_sbifix_sup.py --arm SUP" >/dev/null; do sleep 120; done
cd ~/AIGC_sbifix/results/research/cgd_20260927
for ARM in HYBPE MASK; do
  AIGC_BASE=\$HOME/AIGC_sbifix ~/venvs/sbifix/bin/python -u train_cgd.py --arm \$ARM --workers 16 > train_\${ARM}_s20260928.log 2>&1
done
EOF
chmod +x run_arms.sh && setsid nohup ./run_arms.sh > /dev/null 2>&1 < /dev/null & echo queued'
echo "queued $(date)"
