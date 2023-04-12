import pandas as pd
import numpy as np
import os, sys, glob
import humanize
import re
import xlrd

import json
import itertools
#from urllib.request import urlopen
#import requests, xmltodict
import time, datetime
import math
from pprint import pprint
import gc
from tqdm import tqdm
tqdm.pandas()
import pickle

import logging
import zipfile
import warnings
import argparse

import numexpr as ne

#import numba
# numba.set_num_threads(numba.get_num_threads())
# numba.set_num_threads(2)
# from g import logger
from utils_io_kis import logger
if len(logger.handlers) > 1:
    for handler in logger.handlers:
        logger.removeHandler(handler)

# import g
from utils_io_kis import unzip_file
# from utils_io_kis import save_df_to_pickle
from utils_kis import restore_df_from_pickle, save_df_to_pickle, get_humanize_filesize, save_df_to_excel
from utils_kis import exract_esklp_date, find_last_fn_pickle, find_last_file
# from extend_functions import *
# from xml_utils import load_smnn, create_smnn_list_df, reformat_smnn_list_df
# from xml_utils import load_klp_list, create_klp_list_dict_df, reformat_klp_list_dict_df

# from dictionaries import doze_vol_handler_types, doze_vol_pharm_form_handlers
from parse_utils import load_form_standard_unify_dict, extract_single_names_03
from parse_utils import def_mnn_mis, parse_mis_position_07, init_parse_kis
from parse_utils import read_selection_25000, apply_parse_kis, read_selection
# from g import klp_list_dict_df, smnn_list_df, klp_srch_list, klp_srch_list_columns 
from parse_utils import klp_list_dict_df, smnn_list_df, klp_srch_list, klp_srch_list_columns 
from g import code_klp_id, mnn_standard_id, code_smnn_id, trade_name_id, trade_name_capitalize_id, \
form_standard_unify_id, lim_price_barcode_str_id, num_reg_id, lf_norm_name_id, dosage_norm_name_id
from g import dict__tn_lat__tn_ru_orig
from parse_utils import apply_upd_parse_kis

# fn_esklp_xml_active_zip = 'esklp_20221110_active_21.5_00001.xml.zip'
# path_kis_source = 'D:/DPP/01_parsing/data/kis/source/'
# path_kis_work = 'D:/DPP/01_parsing/data/kis/temp/'
# path_kis_processed = 'D:/DPP/01_parsing/data/kis/processed/'
# path_esklp_processed = 'D:/DPP/01_parsing/data/esklp/processed/'
# path_supp_dicts = 'D:/DPP/01_parsing/data/supp_dicts/'
smnn_prefix = 'smnn_list_df_esklp'
klp_prefix = 'klp_list_dict_df_esklp'
smnn_prefix = 'smnn_list_df_esklp_active'
klp_prefix = 'klp_list_dict_df_esklp_active'
smnn_prefix_active = 'smnn_list_df_esklp_active'
smnn_prefix_full = 'smnn_list_df_esklp_full'
klp_prefix_active = 'klp_list_dict_df_esklp_active'
klp_prefix_full = 'klp_list_dict_df_esklp_full'

xlsx_suffix = '.xlsx'
pickle_suffix = '.pickle'

fn_dict_MISposition_MNN_form = 'Справочник_ЛП_ЖНВЛП_МНН_.xlsx'
fn_dict_MISposition_group = 'Справочник_ЛС_РМ.xlsx'
fn_tz_excel = 'Техническое задание_пример таблицы.xlsx'

fn_selection_63000_positions = 'Справочник_ЛП_РМ_02092022_25000_positions.xlsx'
fn_LF_EAS = 'lf_EAS.xlsx'
fn_f_pharm_form_tn_lat_tn_ru = 'ФОРМЫ ВЫПУСКА+ПЕРВИЧ УПАК_ТОРГОВЫЕ_для парсинга.xlsx'

#

# def parse_opt():
#     parser = argparse.ArgumentParser()
#     parser.add_argument('--source_xlsx', '-s', type=str, default='selections_02092022_25000_positions.xlsx',
#         help="File '*.xlsx' in dir 'D:/DPP/01_parsing/data/kis/source/'")
#     parser.add_argument('--col_name', '-cn', type=str, default='NAME',
#         help="Column name for parsing")
#     parser.add_argument('--esklp_date', '-k', type=str, default='last',
#         help="Date of ESKLP file in format 'DD.MM.YYYY' in dir 'D:/DPP/01_parsing/data/esklp/processed/'")
#     parser.add_argument('--part', '-p', type=str, default='all',
#         help="'Части для выполнения алгоритма' in dir 'D:/DPP/01_parsing/data/kis/temp/'")
#     # parser.add_argument('--pickle_file', '-pf', type=str, default='last',
#     #     help="File 'znvlp_YYYYYMMDD_esklp_YYYYMMDD_p*.pickle' in dir 'D:/DPP/01_parsing/data/kis/temp/'")
#     parser.add_argument('--excel_save', '-xl', type=bool, default=True,
#         help="Необходимость сохранения в Excel 'kis_esklp_YYYYMMDD_p*.xlsx' in dir 'D:/DPP/01_parsing/data/znvlp/processed/'")
#     parser.add_argument('--mode', '-m', type=str, default='run',
#         help="run/test")
#     parser.add_argument('--beg_rec', '-b', type=int, default=0,
#         help="Номер начальнйо записи выборки")
#     parser.add_argument('--end_rec', '-e', type=int, default=np.inf,
#         help="Номер конечной записи выборки")
#     parser.add_argument('--i_row', '-i', type=int, default=0,
#         help="Номер записи для теста")
#     parser.add_argument('--update_cols', '-cu', type=str, default=None,
#         help="Поля корретировки (через +, если несколько): ")        
#     parser.add_argument('--fulfillment', '-f', type=str, default='a',
#         help="Полнота справочника - active/full")
#     parser.add_argument('--dir_source', '-ds', type=str, default='s',
#         help="Data source directoty,  default: s-> 'D:/DPP/01_parsing/data/kis/source/'\n p-> 'D:/DPP/01_parsing/data/esklp/processed/'")
#     opt = parser.parse_args()
#     return opt

# def main (source_xlsx='selections_02092022_25000_positions.xlsx', 
def parse_kis (source_xlsx, sheet_name, col_name,
    path_kis_source, path_kis_work, path_kis_processed, path_esklp_processed, path_supp_dicts,
    esklp_date ='last', part = 'all', 
    pickle_file = 'last', 
    update_cols = None,
    fulfillment = 'a',
    dir_source = 's',
    excel_save = True, mode = 'run', 
    beg_rec = 0, end_rec = np.inf, i_row =0,
    
    ):
    # пока некорреткно работает если brg_rec > 0
    global smnn_list_df, klp_list_dict_df, selection_df, esklp_date_format
  
    # numba.set_num_threads(int(numba.get_num_threads()/2))
    # Номенклатура_КИС

    if source_xlsx is None:
        logger.error('No source xlsx file name')
        sys.exit(2)
    elif ((dir_source == 's') and not os.path.exists(os.path.join(path_kis_source,  source_xlsx)))\
         or ((dir_source == 'p') and not os.path.exists(os.path.join(path_kis_processed,  source_xlsx)))\
         or ((dir_source not in ['s', 'p']) and not os.path.exists(os.path.join(dir_source,  source_xlsx))):
        logger.error('Not found source xlsx file')
        sys.exit(2)
    
    if fulfillment == 'a':
        smnn_prefix = smnn_prefix_active
        klp_prefix = klp_prefix_active
    else:
        smnn_prefix = smnn_prefix_full
        klp_prefix = klp_prefix_full

    if esklp_date == 'last':
        fn_smnn_list_df_pickle = find_last_file(path_esklp_processed, smnn_prefix, pickle_suffix)
        fn_klp_list_dict_df_pickle = find_last_file(path_esklp_processed, klp_prefix, pickle_suffix)
        smnn_date = exract_esklp_date (fn_smnn_list_df_pickle, smnn_prefix)
        klp_date = exract_esklp_date (fn_klp_list_dict_df_pickle, klp_prefix)
        if smnn_date != klp_date:
            logger.error('Dates of smnn & klp files are differeте or files are not found')
            sys.exit(2)
        else: 
            esklp_date_format = smnn_date
    else: 
        esklp_date_format = ''.join(esklp_date.split('.')[::-1])
        fn_smnn_list_df_pickle = find_last_file(path_esklp_processed, smnn_prefix + '_' + esklp_date_format,  pickle_suffix)
        fn_klp_list_dict_df_pickle = find_last_file(path_esklp_processed, klp_prefix + '_' + esklp_date_format,  pickle_suffix)
    print(esklp_date_format)
    
    if fn_smnn_list_df_pickle is None or fn_klp_list_dict_df_pickle is None:
        logger.error('smnn &/| klp files are not found')
        sys.exit(2)


    
    smnn_list_df = restore_df_from_pickle(smnn_prefix, 
        path_esklp_processed, fn_smnn_list_df_pickle)
    
    klp_list_dict_df = restore_df_from_pickle(klp_prefix, 
        path_esklp_processed, fn_klp_list_dict_df_pickle)

         
    init_parse_kis(klp_list_dict_df, smnn_list_df, path_supp_dicts)
    
    # numba.set_num_threads(int(numba.get_num_threads()/2))
    # numba.set_num_threads(2)
    # e = zvnlp_df.shape[0]
    if mode=='run':
        if part == 'all':
            b, e = beg_rec, None if end_rec==np.inf else end_rec
            if (dir_source == 's'): path_source = path_kis_source
            elif (dir_source == 'p'): path_source = path_kis_processed
            else: path_source = dir_source
            if source_xlsx == 'selections_02092022_25000_positions.xlsx':
                # df_sel_25000, mis_position_col_name = read_selection_25000(path_kis_source,  source_xlsx, sheet_name ='Total', b=b, e=e)
                df_sel_25000, mis_position_col_name = read_selection_25000(path_source,  source_xlsx, sheet_name ='Total', b=b, e=e)
            else:
                # df_sel_25000, mis_position_col_name = read_selection(path_kis_source,  source_xlsx, col_name, sheet_name = None, b=0, e=np.inf)
                # df_sel_25000, mis_position_col_name = read_selection(path_kis_source,  source_xlsx, col_name, sheet_name = None, b=b, e=e)
                df_sel_25000, mis_position_col_name = read_selection(path_source,  source_xlsx, col_name, sheet_name = sheet_name, b=b, e=e)
            # df_sel_25000 = apply_parse_kis(df_sel_25000, mis_position_col_name, debug=True, debug_print=True, b=b, e=e)      
            df_sel_25000 = apply_parse_kis(df_sel_25000, mis_position_col_name, debug=False, debug_print=False) #, b=b, e=e)      
            # df_sel_25000 = apply_parse_kis(df_sel_25000, mis_position_col_name, debug=True, debug_print=False) #, b=b, e=e)      
            
            tmp_fn_main = source_xlsx.split('.')[0] + '_esklp_' + esklp_date_format + '_parsed'
            if excel_save:
                tmp_fn_main_xlsx = save_df_to_excel(df_sel_25000, path_kis_processed, tmp_fn_main) #, b=b, e=e)
        # elif part == 'p1':
        # elif 'p1' in part:
        #     # apply_p1_lp_date() 
        #     tmp_fn_main = source_xlsx.split('.')[0] + '_esklp_' + esklp_date_format + '_parsed'
        #     # print(zvnlp_df[zvnlp_df['proc_tag']=='lp_date'].shape) # 30479
            
        
        else:
            logger.error(f"Не определены этапы расчетов")
            sys.exit(2)
        
        # tmp_fn_main_pickle = save_df_to_pickle(zvnlp_df, path_znvlp_work, tmp_fn_main)

        # if '_all_steps' in tmp_fn_main or excel_save:
        if part in ['all', 'p7'] or excel_save:
            a = 0

    elif mode=='upd':
        if update_cols is None:
            logger.error(f"Для режима корректировки не определены параметры")
            sys.exit(2)
        else:
            update_cols_lst = update_cols.split('+')
            correct_cols = []
            if 'tn' in update_cols_lst:
                correct_cols.append('tn_correct')
            if 'fu' in update_cols_lst:
                correct_cols.append('pharm_form_type_correct')
            if 'dz' in update_cols_lst:
                correct_cols.append('dosage_parsing_value_str_correct')    
            if 'vol' in update_cols_lst:
                correct_cols.extend(['vol_correct', 'vol_unit_correct'])
            print(f"correct_cols: {correct_cols}, {update_cols_lst}")

            # if part == 'all':
            b, e = beg_rec, None if end_rec==np.inf else end_rec
            if (dir_source == 's'): path_source = path_kis_source
            elif (dir_source == 'p'): path_source = path_kis_processed
            else: path_source = dir_source
            if source_xlsx == 'selections_02092022_25000_positions.xlsx':
                df_sel_25000, mis_position_col_name = read_selection_25000(path_source,  source_xlsx, sheet_name ='Total', b=b, e=e)
            else:
                df_sel_25000, mis_position_col_name = read_selection(path_source,  source_xlsx, col_name, sheet_name = None, b=0, e=np.inf)
            # df_sel_25000 = apply_parse_kis(df_sel_25000, mis_position_col_name, debug=True, debug_print=True, b=b, e=e)      
            if not set(correct_cols).issubset(df_sel_25000.columns):
                logger.error(f"Нет указанных коректировочных полей: {', '.join(correct_cols)} в файле для корректировки")
                sys.exit(2)
            df_sel_25000 = apply_upd_parse_kis(df_sel_25000, mis_position_col_name, 
                correct_cols,
                debug=False, debug_print=False, b=b, e=e)      
            
            # tmp_fn_main = source_xlsx.split('.')[0] + '_esklp_' + esklp_date_format + '_upd'
            tmp_fn_main = source_xlsx.split('.')[0] + '_upd_' + update_cols
            if excel_save:
                tmp_fn_main_xlsx = save_df_to_excel(df_sel_25000, path_kis_processed, tmp_fn_main) #, b=b, e=e

    elif mode=='test':
        # i_row = 871
        ss = ['Дипроспан сусп д/ин 2мг+5мг/мл амп 1мл №1х1 Шеринг-Плау Лабо Бельгия'
            'Мексиприм р-р для в/в и в/м 50 мг/мл 5 мл амп N 5x1 Полисан НТФФ ООО Россия',
            ]
        b, e = beg_rec, None if end_rec==np.inf else end_rec
        df_sel_25000, mis_position_col_name = read_selection_25000(path_kis_source,  source_xlsx, sheet_name ='Total', b=b, e=e)
        mis_position = df_sel_25000.iloc[i_row] [mis_position_col_name]
        print(i_row, mis_position)
        _ = parse_mis_position_07(mis_position, select_by_tn=True, debug=True, debug_print=True)
        # for i,mis_position in enumerate(ss[:]):

        #     mis_position = df_sel_25000.loc[i_row:i_row+1, mis_position_col_name] #[0]

        #     print(i, mis_position)

        #     tn_ru, tn_lat, tn_ru_ext, tn_lat_ext, tn_ru_orig, tn_ru_ext_clean, tn_true,\
        #     tn_by_tn, mnn_by_tn,\
        #     tn_ru_clean, \
        #     pharm_form_type, pharm_form, \
        #     mnn_from_tn_ru_ext,  mnn_local_dict, mnn_true, ath_name, ath_code, is_znvlp, is_narcotic, form_standard,\
        #     doze_group, doze_proc, doze, doze_unit, pseudo_vol, pseudo_vol_unit, comlex_doze_list, comlex_doze_str, vol, vol_unit,\
        #     pack_1_form_unify, pack_1_form,  pack_1_num, pack_2_form_unify, pack_2_form, pack_2_num, consumer_total_parsing, \
        #     dosage_standard_value_str, dosage_standard_value, dosage_standard_unit, \
        #     dosage_parsing_value_str, dosage_parsing_value,	dosage_parsing_unit,\
        #     c_doze,\
        #     lp_pack_1_num, lp_pack_2_num, lp_unit_okei, lp_unit, lp_consumer_total, lp_consumer_total_calc,\
        #     c_vol, name_ei_lp =\
        #             parse_mis_position_07(mis_position, select_by_tn=True, debug=True, debug_print=True)

            #


# if __name__ == '__main__':
#     if len(sys.argv) > 1: # есть аргументы в командной строке
#         opt = parse_opt()
#         main(**vars(opt))
#     else:
#         main()

# запуск   
# py parse_kis.py -s="selections_02092022_25000_positions.xlsx" -m test
# py parse_kis.py -s="selections_02092022_25000_positions.xlsx" -k 23.09.2022 -m test
# py parse_kis.py -s="ph_f_unify.xlsx" -k 23.11.2022 -m upd -cu tn+fu -cn "Лекарства.Наименование" -xl 1
# py parse_kis.py -s="ph_f_unify.xlsx" -k 08.12.2022 -f a -m upd -cu fu -cn "Лекарства.Наименование"
# py parse_kis.py -s="ph_f_unify.xlsx" -k 08.12.2022 -f f -m upd -cu fu -cn "Лекарства.Наименование"
# py parse_kis.py -s="Все ЛС 21-22_от_Димы (все списания_2021, 2022).xlsx" -k 23.11.2022 -m run -cn "Лекарства.Наименование" -xl 1

# py parse_kis.py -s="20230220_Sofa_уникальные ЛП.xlsx" -k 19.01.2023 -m run -cn "Наименование" -xl 1
