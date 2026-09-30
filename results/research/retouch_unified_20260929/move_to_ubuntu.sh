#!/bin/bash
# Free local disk: copy inactive datasets to the Ubuntu box (~/AIGC_cold/), verify file count AND total bytes, only then
# delete the local copy. Every step is appended to archive/MOVE_LOG_20260929.txt.
cd /c/My_Project/AIGC
LOG=archive/MOVE_LOG_20260929.txt; R=gsplat-ubuntu
echo "=== $(date) move inactive datasets to $R:~/AIGC_cold" >> $LOG
ssh -n $R "mkdir -p ~/AIGC_cold"
for d in FaceForensics_masks_c23 retouchingffhq_vendor_train ffhq_hires_real ffhq_paired_real FaceForensics_raw sbi_data ffpp_real_for_teammates; do
  [ -d "$d" ] || continue
  ln=$(find "$d" -type f | wc -l); lb=$(find "$d" -type f -printf "%s\n" | awk '{s+=$1} END {printf "%d", s}')
  tar cf - "$d" | ssh $R "cd ~/AIGC_cold && tar xf -"
  rn=$(ssh -n $R "find ~/AIGC_cold/$d -type f | wc -l"); rb=$(ssh -n $R "find ~/AIGC_cold/$d -type f -printf '%s\n' | awk '{s+=\$1} END {printf \"%d\", s}'")
  if [ "$ln" = "$rn" ] && [ "$lb" = "$rb" ]; then
    rm -rf "$d"; echo "$d: $ln files, $lb bytes -> ~/AIGC_cold/$d VERIFIED, local deleted" >> $LOG
  else
    echo "$d: MISMATCH local $ln/$lb remote $rn/$rb -> local KEPT" >> $LOG
  fi
done
# vendor_single: already on the Ubuntu box (~/AIGC_sbifix/vendor_single); delete locally once local RU2 training has finished
until [ -f results/research/retouch_unified_20260929/meta_ru_ru2_effb4_s20260929.json ]; do sleep 60; done
ln=$(find vendor_single -type f | wc -l); rn=$(ssh -n $R "find ~/AIGC_sbifix/vendor_single -type f | wc -l")
if [ "$ln" = "$rn" ]; then rm -rf vendor_single; echo "vendor_single: $ln files present on ~/AIGC_sbifix/vendor_single, local deleted" >> $LOG
else echo "vendor_single: MISMATCH $ln vs $rn -> local KEPT" >> $LOG; fi
echo "=== done $(date)" >> $LOG
