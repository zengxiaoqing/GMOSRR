#��̨����
#nohup /vdisk2/zxq/GMOSRR/2Write_DataBase/Obs_Grid/Obs_Grib_Extract_recal.sh >> /vdisk2/zxq/GMOSRR/2Write_DataBase/Obs_Grid/log.txt 2>&1 &

#�Զ��������ļ�
#sfile_name="Obs_Grid.ini"
#-gn $sfile_name

#������(����ʱ��)
ayBegin_hour=(01 02 03 04 05 06 07 08 09 10 11 12 13 14 15 16 17 18 19 20 21 22 23 24)
iupdate=0

#�趨��ʼ-��������(����ʱ��)
if [ $# == 2 ]; then
  begin_date=$1
  end_date=$2
else
  #�Զ���"��ʽΪ2017-04-04"
  begin_date="2019-11-01"
  end_date="2020-02-28"
fi
echo "date: "$begin_date" to "$end_date

#����ѭ��
beg_s=`date -d "$begin_date" +%s`
end_s=`date -d "$end_date" +%s`
while [ "$beg_s" -le "$end_s" ];do
  ted=`date -d @$beg_s +"%Y%m%d"`;
  #��ʱѭ��
  for bh in ${ayBegin_hour[@]}; do
  {
    echo $ted,$bh
    python3 Obs_Grib_Extract.pyc -u $iupdate -ndel -bd $ted -ed $ted -bh $bh -eh $bh
  }
  done
  beg_s=$((beg_s+86400)); #��������1��(24h=86400��)
done


