# -*- coding: gb18030 -*-

import os
import sys
import math
import warnings
warnings.simplefilter(action='ignore', category=(FutureWarning,RuntimeWarning))
import pygrib
import datetime
import numpy as np


for i in range(1,10):
  sRoot_Path = os.path.join(*[".."]*i)
  lib_path=os.path.join(sRoot_Path,"lib","pylib")
  if os.path.exists(lib_path):
    break
sys.path.append(lib_path)

import Module_MyFunction           as MMyfun
import Module_Arguments            as MArg
import Module_Global_Variable      as MGV
import Module_Global_Path          as MGP
import Module_2Write_DataBase      as M2WD
import Module_Obs_DataBase         as MObsDB


#������
if __name__=='__main__':

  #��ǰ����·��
  sCurrent_Path=os.getcwd()
  
  #�����ļ���ȷ������
  ltpath_para=sCurrent_Path.split(os.sep)

  #��ȡ����
  cls_arg = MArg.Class_Arguments(step="S2_Obs")
  args=cls_arg.dArgs(dspt=__file__)

  #ʵ����
  cls_myfun = MMyfun.Class_MyFunction()
  cls_gv    = MGV.Class_Global_Variable(iDebug=0)
  cls_gp    = MGP.Class_Global_Path()
  cls_s2wd  = M2WD.Class_EC_2Write_DataBase()
  cls_obsdb = MObsDB.Class_Obs_DataBase()

  #ȫ��·��
  cls_gp.dRead_Global_Path_ini(sRoot_Path)
  
  #���ʵ�����ݿ����
  cls_obsdb.dRObs_Grid_ini(sRoot_Path, cls_gv.sObs_Grid_file)
  
  #ʱ�亯��(BJ)
  ltdates = cls_myfun.ddates_between_two_date(args.begin_date, args.end_date, args.if_period)
  iN_day = len(ltdates)

  
  #��ˮ�ۻ�ʱ��
  lthour_span=[3,6,12,24]
  #�ۻ�ʱ����ļ���
  lt3h=np.arange(2,24,3).tolist()
  lt3h_span=[[f"03_{x:02d}_{y:02d}" for x,y in zip(lt3h[-1:]+lt3h[0:-1],lt3h)],lt3h]
  lt6h=np.arange(2,24,6).tolist()
  lt6h_span=[[f"06_{x:02d}_{y:02d}" for x,y in zip(lt6h[-1:]+lt6h[0:-1],lt6h)],lt6h]
  lt12h_span=[[f"12_{x:02d}_{y:02d}" for x,y in zip([8,20],[20,8])],[8,20]]
  lt24h_span=[[f"24_{x:02d}_{y:02d}" for x,y in zip([20,8],[20,8])],[8,20]]
  dyhour_span={3:lt3h_span,
               6:lt6h_span,
              12:lt12h_span,
              24:lt24h_span}
  
  # #1����Ҫ������ʱ��
  lt1day_hour=lt3h
  
  #����ѭ��
  for idy, sdate in enumerate(ltdates):
    #Сʱѭ��
    for ihr in lt1day_hour:
      shr=f"{ihr:02d}"
      sYMDH=sdate+shr
      #����Ŀǰʱ��Ķ���ȥ
      iYMDH=int(sYMDH)
      if iYMDH>cls_arg.inow_ymdh: continue
      dtYMDH=datetime.datetime.strptime(sdate+shr, '%Y%m%d%H')
      #��ˮ�ۻ�ʱ��ѭ��(3,6,12,24h)
      for ihour_span in lthour_span:
        sobs_dir_sub=f"Hour_{ihour_span:02d}Accu"
        if ihr not in dyhour_span[ihour_span][1]: continue
        print(f"{idy}:{sdate}_{ihr:02d} : {ihour_span}", flush=True)
        #��ȥxСʱ��ʱ��
        ltaccu_YMDH=[(dtYMDH-datetime.timedelta(hours=x)).strftime('%Y%m%d%H') for x in range(0,ihour_span+1)]
        #����ļ���
        if ltaccu_YMDH[0][-2:]=="00":
          send_hour="24"
        else:
          send_hour=ltaccu_YMDH[0][-2:]
        sout_obs_file= f"{ihour_span:02d}_{ltaccu_YMDH[-1][-2:]}_{send_hour}.GRB2"
        sout_sub_path=os.path.join(cls_obsdb.sObs_Main_Path, ltaccu_YMDH[0][0:4], ltaccu_YMDH[0][0:8], "Precipitation", sobs_dir_sub)
        if not os.path.exists(sout_sub_path): os.makedirs(sout_sub_path) 
        sout_abs_path=os.path.join(sout_sub_path, sout_obs_file)
        lout=os.path.exists(sout_abs_path)
        if (not lout) or (lout and args.update>=1): #����ļ�������orǿ�����
          #��Сʱ��ˮ�ļ�Ѱ��
          ltfiles_exist=[];ltfiles_path=[]
          for sbegin_YMDH, send_YMDH in zip(ltaccu_YMDH[1:],ltaccu_YMDH[0:-1]):
            if send_YMDH[-2:]=="00":send_YMDH="24"
            sfile_name= "01_"+sbegin_YMDH[-2:]+"_"+send_YMDH[-2:]+".GRB2"
            sIn_main_path=os.path.join(cls_obsdb.sObs_Main_Path, sbegin_YMDH[0:4], sbegin_YMDH[0:8], "Precipitation", "Hour_01Accu")
            sIn_abs_path=os.path.join(sIn_main_path, sfile_name)
            if os.path.exists(sIn_abs_path):
              ltfiles_exist.append(True)
              ltfiles_path.append(sIn_abs_path)
            else:
              ltfiles_exist.append(False)
          #��Сʱ��ˮ�ۻ�
          if all(ltfiles_exist): #ȫ���ļ�����
            cls_obsdb.dObs_Rain_Accu(ltfiles_path, sout_abs_path, ltaccu_YMDH[0])

  #�������н���ʱ��
  cls_myfun.dPrint_run_time()
  
