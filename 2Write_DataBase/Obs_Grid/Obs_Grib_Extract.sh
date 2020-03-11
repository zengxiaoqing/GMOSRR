
./compile.sh

inow_HM=$(date --date="today" +"%H%M")
inow_dt=$(date --date="today" +"%Y%m%d%H")
inow_M=$(date --date="today" +"%M") #����
yd_date=$(date --date="yesterday" +"%Y%m%d")


#��ʱ�˿�
python3 Obs_Grib_Extract.pyc -ndel


#��ȥ12Сʱ
for ih in $(seq 1 12); do
{
  echo $ih
  iago_dh=$(date --date="today -$ih hours" +"%Y%m%d%H")
  python3 Obs_Grib_Extract.pyc -ndel -bd ${iago_dh:0:8} -ed ${iago_dh:0:8} -bh ${iago_dh:8:9} -eh ${iago_dh:8:9}
}
done


#���첹��ȱ�ٵ�
if [[ "$inow_HM" == "1200" ]] || [[ "$inow_HM" == "1230" ]] || \
   [[ "$inow_HM" == "2300" ]] || [[ "$inow_HM" == "2330" ]] ; then
  for fhour in $(seq 4 52); do
  {
    iago_dh=$(date --date="today -$ih hours" +"%Y%m%d%H")
    python3 Obs_Grib_Extract.pyc -ndel -bd ${iago_dh:0:8} -ed ${iago_dh:0:8} -bh ${iago_dh:8:9} -eh ${iago_dh:8:9}
  }
  done
fi
