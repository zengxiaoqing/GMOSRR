# -*- coding: gb18030 -*-

import os
import sys
import math
import getopt
import pygrib
import datetime
import numpy as np
from multiprocessing  import Pool, cpu_count

for i in range(1,10):
  sRoot_Path = os.path.join(*[".."]*i)
  lib_path=os.path.join(sRoot_Path,"lib","pylib")
  if os.path.exists(lib_path):
    break
sys.path.append(lib_path)

import Module_Arguments            as MArg
import Module_MyFunction           as MMyfun
import Module_Model_Info           as MModel
import Module_Global_Path          as MGP
import Module_2Write_DataBase      as M2WD


#������
if __name__=='__main__':

  #��ǰ����·��
  sCurrent_Path=os.getcwd()
  
  #cpu���� 
  in_cpu_core = cpu_count()-1
  
  #�����ļ���ȷ������
  ltwork=sCurrent_Path.split(os.sep)
  # ģʽ�� ����
  sModel_name,sRegion=ltwork[-1].split("_")

  #ʵ����
  cls_myfun = MMyfun.Class_MyFunction(0)
  cls_model = MModel.ModelInfo()
  cls_gp    = MGP.Class_Global_Path()
  cls_s2wd  = M2WD.Class_GRAPES_3KM_2Write_DataBase(0)
  #��ȡ����
  cls_arg   = MArg.Class_Arguments(step="S2")
  args=cls_arg.dArgs(dspt=__file__)
  
  #ȫ��·��
  cls_gp.dRead_Global_Path_ini(sRoot_Path)
  
  #ģʽ��Ϣ
  sIn_Abs_path = os.path.join(sRoot_Path, "Parameter", sModel_name, "_".join([sModel_name,sRegion,"Info.ini"]))
  cls_model.ParseIni(sIn_Abs_path)

  #����·��
  if args.in_path is None:
    args.in_path = os.path.join(cls_gp.sResult_Main_Path,"1DownLoad_Data")

  #�������·�����
  if args.out_path is not None:
    if args.in_path.strip()==args.out_path.strip():
      print("Error:"+args.in_path.strip()+" == "+args.out_path.strip())
      sys.exit()
  
  #�и�������
  if args.grid_name is None:
    ltArea = [cls_model.latlon_info.lat_start, cls_model.latlon_info.lat_end, 
              cls_model.latlon_info.lon_start, cls_model.latlon_info.lon_end]
  else:
    sIn_Abs_path = os.path.join(sRoot_Path, "Parameter", sModel_name, args.grid_name)
    latlon_info=cls_model.dGridini(sIn_Abs_path)
    ltArea = [latlon_info.lat_start, latlon_info.lat_end, latlon_info.lon_start, latlon_info.lon_end] #(�ϱ�����)
  # #GRAPES_3KM��0.1�ֱ���,���Ȳ�����������ü�С0.1�������
  # ltArea[0]=ltArea[0]-0.0001
  # ltArea[1]=ltArea[1]+0.0001
  # GRAPES_3KM��0.03�ֱ���,���Ȳ�����������ü�С0.1�������
  ltArea[0] = ltArea[0] - 0.001
  ltArea[1] = ltArea[1] + 0.001
  ltArea[3] = ltArea[3] + 0.001

  #�ҳ�Ԥ��ʱЧ
  ndy_fhours=np.array(cls_model.ltforecast_hours)
  mask=np.logical_and(args.begin_fhour<=ndy_fhours,ndy_fhours<=args.end_fhour)
  ltforecast_hours=ndy_fhours[mask].tolist()

  #ʱ�亯��(BJ)
  ltdates = cls_myfun.ddates_between_two_date(args.begin_date, args.end_date, 0)
  iN_day = len(ltdates)

  #��Ҫ�����������
  #1|8:�ܽ�ˮ��, 6|1345:��, 7|6:CAPE
  # dyvar_save={"shortName":["acpcp","ncpcp","asnow","pwat","10u","10v","al",
  #                          "2t","tmax","tmin","2d","vis","sp","prmsl","orog"],
  #             "parameter_Category_Number":[[1,8],[6,1],[6,3],[6,4],[6,5],[7,6]],
  #             "key":[{"parameterName":"Temperature","typeOfLevel":"surface"},
  #                    {"parameterName":"Specific humidity","typeOfLevel":"heightAboveGround"}]
  #            }
  #1|8:�ܽ�ˮ�� 2|2:��ȥ1h���10��u�� 2|2:��ȥ1h���10��u��
  dyvar_save = {"shortName": ["2t", "2r", "prmsl", "10u", "10v", ],
                "parameter_Category_Number": [[1, 8]]}
  #��С�߳���
  if args.threads==None:
    iN_Process  = np.min([len(ltforecast_hours),in_cpu_core])
  else:
    iN_Process  = args.threads
  print("processes:",iN_Process)
  
  #����ѭ��
  for idy, seach_date in enumerate(ltdates):
    print(idy,":","_".join([seach_date,args.sbegin_hour]))
    #(����ʱ��)
    sBegin_Date_BJ = seach_date+args.sbegin_hour
    #(����ʱ��)
    sBegin_Date_UTC = cls_myfun.dBJT_to_UTC(sBegin_Date_BJ[0:4], sBegin_Date_BJ[4:6],\
                                            sBegin_Date_BJ[6:8], args.sbegin_hour)
    iyear_bj,  imonth_bj,  iday_bj, ihour_bj   = cls_myfun.ddate_hour_split_1(sBegin_Date_BJ)
    iyear_utc, imonth_utc, iday_utc, ihour_utc = cls_myfun.ddate_hour_split_1(sBegin_Date_UTC)
    #Ԥ��ʱЧ
    ltcycle=[]
    for ifrst_hour in ltforecast_hours:
      #if args.begin_hour in [2,14] and ifrst_hour>120:continue
      sfrst_hour="%03d"%ifrst_hour
      #print(idy,":","_".join([seach_date,args.sbegin_hour,"_%03d"%ifrst_hour]))
      #(����ʱ��)
      sForecast_Date_UTC = cls_myfun.dBefAftDate(iyear_utc, imonth_utc, iday_utc, ihour_utc,"Hour",ifrst_hour)
      #�����ļ���
      #sIn_file_name = "Z_NAFP_C_BABJ_"+ sForecast_Date_UTC + "0000_P_NWPC-GRAPES-3KM-CN-" + "%03d"%ifrst_hour+"00.grb2"
      sIn_file_name = "Z_NAFP_C_BABJ_"+sBegin_Date_UTC+"0000_P_NWPC-GRAPES-3KM-CN-"+sfrst_hour+"00.grb2"
      #�����ļ�����·��
      sIn_Abs_Path = os.path.join(args.in_path,sModel_name+"_"+sRegion, sBegin_Date_BJ[0:4],
                                  sBegin_Date_BJ[0:8],args.sbegin_hour, sIn_file_name)
      #����ļ�����·��
      if args.out_path==None:
        sDB_Main_Path = cls_model.GetDisk(seach_date)
      else:
        if args.out_path.strip()=="":
          sDB_Main_Path = cls_model.GetDisk(seach_date)
        else:
          sDB_Main_Path = args.out_path
      sOut_Sub_Path = os.path.join(sDB_Main_Path, sModel_name+"_"+sRegion, sBegin_Date_BJ[0:4],
                                   sBegin_Date_BJ[0:8],args.sbegin_hour)
      if os.path.exists(sIn_Abs_Path) and (not os.path.exists(sOut_Sub_Path)):os.makedirs(sOut_Sub_Path)
      sout_file_name="rmf.3km.gra."+sBegin_Date_UTC+sfrst_hour+".grb2"
      sOut_Abs_Path = os.path.join(sOut_Sub_Path,sout_file_name)
      if os.path.exists(sOut_Abs_Path):
        fsize = os.path.getsize(sOut_Abs_Path)  #��ȡ�����ݴ�С(bytes)
        #ɾ�������ļ�
        if fsize<=1.0:
          try:
            os.remove(sOut_Abs_Path)
          except OSError as e:
            print("Failed with:", e.strerror)
            print("Error code:", e.code)
        else:
          if args.update==0: continue #����&0�Ͳ��ø���
      ltcycle.append([sIn_Abs_Path,sOut_Abs_Path,ltArea,dyvar_save])
      #cls_s2wd.dS2_Extract(sIn_Abs_Path, sOut_Abs_Path, ltArea, dyvar_save)
      # #��ȡԭʼ���ݴ�С
      # if os.path.exists(sIn_Abs_Path): 
        # fRaw_size,sRaw_unit=cls_myfun.dGet_FileSize(sIn_Abs_Path)

    #���ʱ�β���
    pool = Pool(processes = iN_Process)
    pool_result = pool.map(cls_s2wd.dmulti_Extract, ltcycle)
    pool.close()
    pool.join()

  #�������н���ʱ��
  cls_myfun.dPrint_run_time()
  
