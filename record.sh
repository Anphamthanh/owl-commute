#!/bin/bash
# Records live GDOT camera frames near KSU + live Big Owl Bus feed (Passio system 66).
# Every 2 min during 6:30-10:30 AM and 3:30-6:30 PM rush, every 15 min otherwise. Stops Fri Nov 20 6:30 PM.
D=~/projects/ksu/hackathon/data; UA='Mozilla/5.0 Chrome/146'
CAMS="22594 22595 25475 22508 22502 25460 22503 22505 21594 20479 21622 20873 23401 23419 21609 20466"
END=$(date -j -f "%Y-%m-%d %H:%M" "2026-11-20 18:30" +%s)
while [ $(date +%s) -lt $END ]; do
  T=$(date +%Y%m%d-%H%M%S); mkdir -p $D/$T
  for c in $CAMS; do curl -s -m 20 -A "$UA" "https://511ga.org/map/Cctv/$c" -o $D/$T/cam_$c.png & done
  curl -s -m 20 -X POST 'https://passio3.com/www/mapGetData.php?getBuses=2&deviceId=1' -d 'json={"s0":"66","sA":1}' -o $D/$T/buses.json &
  wait
  H=$((10#$(date +%H)*60 + 10#$(date +%M)))
  if { [ $H -ge 390 ] && [ $H -le 630 ]; } || { [ $H -ge 930 ] && [ $H -le 1110 ]; }; then sleep 120; else sleep 900; fi
done
