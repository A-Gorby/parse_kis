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

import numba
import numexpr as ne

warnings.filterwarnings("ignore")

# from patterns import pattern_s_01, pattern_s_02
from g import dict__tn_lat__tn_ru_orig, dict__tn_lat_ext__tn_ru_orig
from g import smnn_list_df, klp_list_dict_df, klp_srch_list
# from g import logger
from utils_io_kis import logger
if len(logger.handlers) > 1:
    for handler in logger.handlers:
        logger.removeHandler(handler)

# from g import klp_list_dict_df, smnn_list_df, klp_srch_list, klp_srch_list_columns 
from patterns import pharm_form_pttn_list, pharm_form_types_list
from patterns import pack_form_pttn_list, pack_form_types_list
from dictionaries import vol_units_groups, doze_units_groups, doze_vol_handler_types
from dictionaries import units_total_lst, units_total_dict, doze_vol_pharm_form_handlers
from dictionaries import make_doze_ptn_str, make_vol_ptn_str
from dictionaries import recalc_doze_units_dict, base_doze_unit_esklp, base_vol_unit_esklp, base_pseudo_vol_unit_esklp

from g import klp_list_dict_df, klp_srch_list, klp_srch_list_columns 
from g import code_klp_id, mnn_standard_id, code_smnn_id, trade_name_id, trade_name_capitalize_id, \
form_standard_unify_id, lim_price_barcode_str_id, num_reg_id, lf_norm_name_id, dosage_norm_name_id

# path_kis_source = 'D:/DPP/01_parsing/data/kis/source/'
# path_kis_work = 'D:/DPP/01_parsing/data/kis/temp/'
# path_kis_processed = 'D:/DPP/01_parsing/data/kis/processed/'
# path_esklp_processed = 'D:/DPP/01_parsing/data/esklp/processed/'
# path_supp_dicts = 'D:/DPP/01_parsing/data/supp_dicts/'
smnn_prefix = 'smnn_list_df_esklp'
klp_prefix = 'klp_list_dict_df_esklp'
xlsx_suffix = '.xlsx'
pickle_suffix = '.pickle'

fn_dict_MISposition_MNN_form = 'Справочник_ЛП_ЖНВЛП_МНН_.xlsx'
fn_dict_MISposition_group = 'Справочник_ЛС_РМ.xlsx'
fn_tz_excel = 'Техническое задание_пример таблицы.xlsx'

def load_form_standard_unify_dict():
    fn_dict = "form_standard_unify_dict.pickle"
    path_supp_dicts = 'D:/DPP/01_parsing/data/supp_dicts/'
    # with open(path_supp_dicts + fn_dict, 'rb') as f:
    with open(os.path.join(path_supp_dicts, fn_dict), 'rb') as f:
        form_standard_unify_dict = pickle.load(f)
    return form_standard_unify_dict

# v4
def def_Ru_lat_00(name):
    if ord(name[0])>ord('z'): return True  # буква по номеру после z уже не латинская и первая не может быть цифрой
    else: return False

def def_Ru_lat(name):
    fl_lat, fl_ru = False, False
    for ch in name:
        if not fl_ru: 
            if ord(ch)>ord('z'): fl_ru = True  # буква по номеру после z уже не латинская и первая не может быть цифрой
        if not fl_lat: 
            if ord(ch)<=ord('z'): fl_lat = True
    if fl_ru: return True
    else: return False # fl_lat  предполагаем что если нет русских букв то чуду-юдо латинское

def extract_single_names_03(mnn_mis, debug = False):
    
    pattern_s_mnn = r"((?P<fst_wrd>[\w\.]+\-*[\w\.]*\s[A-Z]+)"\
                    r"|(?P<fst_wrd_var>[\w\.]+\-*|\+*[\w\.]*))"\
                    r"\s*"\
                    r"\((?P<wrd_in_brac>[\w\.]+\-*[\w\.]*)*\)"\
                    r"|(?P<snd_wrd>[\w\.]+\-*[\w\.]*)*"
    pattern_s_mnn = r"((?P<fst_wrd>[\w\.]+\-*[\w\.]*\s[A-Z]+)"\
                    r"|(?P<fst_wrd_var>[\w\.]+\-*[\w\.]*))"\
                    r"\s*"\
                    r"(\((?P<wrd_in_brac>[\w\.]+\-*[\w\.]*)*\))*"\
                    r"|(?P<snd_wrd>[\w\.]+\-*[\w\.]*)*"
    pattern_s_mnn = r"((?P<fst_wrd>[\w\.]+(\-|\+|\s)*[\w\.]*\s[A-Z]+)"\
                    r"|(?P<fst_wrd_var>[\w\.]+(\-|\+)*[\w\.]*(\-|\+)*[\w\.]*)"\
                    r")"\
                    r"\s*"\
                    r"(\((?P<wrd_in_brac>[\w\.]+(\-|\+|\s)*[\w\.]*(\-|\+)*[\w\.]*)*\))*"\
                    #r"|(?P<snd_wrd>[\w\.]+(\-|\+)*[\w\.]*(\-|\+|\s)*[\w\.]*)*"
    # при этом - выше - patterne программа зацикливалась
    pattern_s_mnn = r"((?P<fst_wrd_var2>[\w\.]+\.\s+[\w\.]*)"\
                    r"|(?P<fst_wrd>[\w\.]+(\-|\+)*[\w\.]*\s[A-Z]+))"\
                    r"|(?P<fst_wrd_var>[\w\.]+(\-|\+)*[\w\.]*(\-|\+)*[\w\.]*)"\
                    r"\s*"\
                    r"(\((?P<wrd_in_brac>[\w\.]+(\-|\+|\s)*[\w\.]*(\-|\+)*[\w\.]*)*\))*"\
                    r"|\s(?P<snd_wrd>[\w\.]+(\-|\+)*[\w\.]*(\-|\+)*[\w\.]*)*"
    pattern_s_mnn = r"((?P<fst_wrd_var2>\b[\w\.]+\.\s+[\w\.]*\b)"\
                    r"|(?P<fst_wrd>\b[\w\.]+(\-|\+)*[\w\.]*\s[A-Z]+)\b)"\
                    r"|(?P<fst_wrd_var>\b[\w\.]+(\-|\+)*[\w\.]*(\-|\+)*[\w\.]*\b)"\
                    r"\s*"\
                    r"(\((?P<wrd_in_brac>\b[\w\.]+(\-|\+|\s)*[\w\.]*(\-|\+)*[\w\.]*\b)*\))*"\
                    r"|\s(?P<snd_wrd>\b[\w\.]+(\-|\+)*[\w\.]*(\-|\+)*[\w\.]*\b)*"                    
               
    # Поскольку совпадения, которые вы ожидаете, представляют собой целые слова, я предлагаю улучшить шаблон, 1) добавив границы слов,
    # https://reddeveloper.ru/questions/python-re-findall-zavisayet-na-nekotorykh-saitakh-MbjWJ
    
    tn_ru, tn_lat = None, None
    #tn_add_total = None
    t = re.search(pattern_s_mnn, mnn_mis)
    #t = re.match(pattern_s_mnn, mnn_mis)
    if t is not None: 
        if debug:  print(t.groups())
        tn_1 = t.group('fst_wrd') or t.group('fst_wrd_var')
        tn_2 = t.group('snd_wrd')
        tn_add = t.group('wrd_in_brac')
        tn_add2 = t.group('fst_wrd_var2')
        if debug: print('fst_wrd:', tn_1, '-fst_wrd_var2:', tn_add2, '-snd_wrd:', tn_2, "-wrd_in_brac:", tn_add)
        tn_add = tn_add or tn_add2 # либо одно либо другое
        #if debug: print(tn_1, '-', tn_2, "-", tn_add, '-', t.group('fst_wrd_var'))
        
        if tn_1 is not None:
            if def_Ru_lat(tn_1): tn_ru = tn_1
            else: tn_lat = tn_1
        if tn_2 is not None:
            if def_Ru_lat(tn_2): 
                if tn_ru is not None: tn_ru += ' ' + tn_2
                else: tn_ru = tn_2
            elif not def_Ru_lat(tn_2): 
                if tn_lat is not None: tn_lat += ' ' + tn_2
                else: tn_lat = tn_2
        if tn_add is not None: 
            if debug: print("if tn_add is not None: ", tn_add)
            if def_Ru_lat(tn_add): 
                if tn_ru is not None: tn_ru += ' (' + tn_add + ')'
                else: tn_ru = tn_add
            #elif not def_Ru_lat(tn_add): 
            else:
                if tn_lat is not None: tn_lat += ' (' + tn_add + ')'
                else: tn_lat = tn_add
        #if debug: print(tn_ru, tn_lat)
    return tn_ru, tn_lat  #tn_ru_add,, tn_lat_add 

def parse_mis_position(mis_position, debug=False):
    #global pattern_s_mnn 
    pattern_s_mnn = r'(\w+|[A-Za-z]+\s*\(\w+|[A-Za-z]+\))|(\w+(\s*[A-Za-z]+)*|\w+)'
    pattern_s_mnn = r'(\B\s*\(\B\))|(\B)'
    pattern_s_mnn = r'^(\w+)\s*(\(\w+\))|^(\w+)\s*([A-Za-z]+)|^(\w+)'
    #pattern_s_mnn = r'(\b\s*\(\b-z]+\))|(\w+(\s*[A-Za-z]+)*|\w+)'
    pattern_s_mnn = r"((?P<fst_wrd_var2>[\w\.]+\.\s+[\w\.]*)"\
                    r"|(?P<fst_wrd>[\w\.]+(\-|\+)*[\w\.]*\s[A-Z]+))"\
                    r"|(?P<fst_wrd_var>[\w\.]+(\-|\+)*[\w\.]*(\-|\+)*[\w\.]*)"\
                    r"\s*"\
                    r"(\((?P<wrd_in_brac>[\w\.]+(\-|\+|\s)*[\w\.]*(\-|\+)*[\w\.]*)*\))*"\
                    r"|\s(?P<snd_wrd>[\w\.]+(\-|\+)*[\w\.]*(\-|\+)*[\w\.]*)*"
    mnn_mis, doze_unit, doze_unit_groups, vol_unparsed = None, None, None, None
    mnn_mis = re.match(pattern_s_mnn, mis_position)
    if mnn_mis: mnn_mis = mnn_mis.group()
    if type(mnn_mis)==str: mnn_mis = mnn_mis.strip()
    if debug: print(mnn_mis)
    if mnn_mis is not None:
        form_doze_pack = mis_position[len(mnn_mis)+1:]
        doze_unit = re.search(pattern_s_01, form_doze_pack.lower())
        doze_unit_groups = None
        if doze_unit is None:
            doze_unit = re.search(pattern_s_02, form_doze_pack.lower())
        if debug: print(doze_unit.groups())
        vol_unparsed = None
        if doze_unit is not None:
            doze_unit_groups = doze_unit.groups()
            doze_unit = doze_unit.group()
            vol_ind = form_doze_pack.lower().find(doze_unit)+ len(doze_unit)
            vol_unparsed = form_doze_pack[vol_ind+1:]
        else: vol_unparsed = form_doze_pack
    return mnn_mis, doze_unit, doze_unit_groups, vol_unparsed    

def def_mnn_mis(mis_position, debug=False):
    #if debug: print(mis_position)
    pattern_s_mnn = r'^(\w+)\s*(\(\w+\))|^(\w+)\s*([A-Za-z]+)|^(\w+)'
    #pattern_s_mnn = r'(\b\s*\(\b-z]+\))|(\w+(\s*[A-Za-z]+)*|\w+)'
    pattern_s_mnn = r"((?P<fst_wrd_var2>[\w\.]+\.\s+[\w\.]*)"\
                r"|(?P<fst_wrd>[\w\.]+(\-|\+)*[\w\.]*\s[A-Z]+))"\
                r"|(?P<fst_wrd_var>[\w\.]+(\-|\+)*[\w\.]*(\-|\+)*[\w\.]*)"\
                r"\s*"\
                r"(\((?P<wrd_in_brac>[\w\.]+(\-|\+|\s)*[\w\.]*(\-|\+)*[\w\.]*)*\))*"\
                r"|\s(?P<snd_wrd>[\w\.]+(\-|\+)*[\w\.]*(\-|\+)*[\w\.]*)*"
    pattern_s_mnn = r"((?P<fst_wrd_var2>\b[\w\.]+\.\s+[\w\.]*\b)"\
                r"|(?P<fst_wrd>\b[\w\.]+(\-|\+)*[\w\.]*\s[A-Z]+)\b)"\
                r"|(?P<fst_wrd_var>\b[\w\.]+(\-|\+)*[\w\.]*(\-|\+)*[\w\.]*\b)"\
                r"\s*"\
                r"(\((?P<wrd_in_brac>\b[\w\.]+(\-|\+|\s)*[\w\.]*(\-|\+)*[\w\.]*\b)*\))*"\
                r"|\s(?P<snd_wrd>\b[\w\.]+(\-|\+)*[\w\.]*(\-|\+)*[\w\.]*\b)*"                   
    mnn_mis_ = re.match(pattern_s_mnn, mis_position)
    if mnn_mis_: mnn_mis_ = mnn_mis_.group()
    else: mnn_mis_ = ''
    tn_ru_, tn_lat_ = extract_single_names_03(mnn_mis_, debug)
    return mnn_mis_, tn_ru_, tn_lat_

pattern_s_digits = r'(((\d+,\d+|\d+\.\d+|\d+)\s*((тыс)(.)*)*)\s*)'
pattern_s_mg = '(mg|мг)'
pattern_s_anti_ha_me_dml = '(((anti|анти)(-)*(xa|ха|xа|хa|ha|на|hа|nа))\s*(me|ме|мe)((\d+,\d+)|(\d+))\s*(ml|мл))'
pattern_s_anti_ha_me_mil = '(((anti|анти)(-)*(xa|ха|xа|хa|ha|на|hа|nа)*)\s*(me|ме|мe)/((\d+,\d+)|(\d+))*\s*(ml|мл))'
pattern_s_anti_ha_le_mil = '(((anti|анти)(-)*(xa|ха|xа|хa|ha|на|hа|nа)*)\s*(ле|le|лe)/((\d+,\d+)|(\d+))*\s*(ml|мл))'
pattern_s_anti_ha_mil = '(((anti|анти)(-)*(xa|ха|xа|хa|ha|на|hа|nа)*)/(\d+\,\d+|\d+)*(ml|мл))'
pattern_s_anti_ha_me = '(((anti|анти)(-)*(xa|ха|xа|хa|ha|на|hа|nа)*)\s*(me|ме|mе|мe))'
pattern_s_anti_ha_le = '(((anti|анти)(-)*(xa|ха|xа|хa|ha|на|hа|nа)*)\s*(ле|le|лe))'
pattern_s_me_anti_ha_mil = '((me|ме|mе|мe)\s*((anti|анти)(-)*(xa|ха|xа|хa|ha|на|hа|nа))\s*/(\d+,\d+|\d+)*(ml|мл))'
pattern_s_le_anti_ha_mil = '((ле|le|лe)\s*((anti|анти)(-)*(xa|ха|xа|хa|ha|на|hа|nа))\s*/(\d+,\d+|\d+)*(ml|мл))'
pattern_s_me_anti_ha = '((me|ме|mе|мe|ле)\s*((anti|анти)(-)*(xa|ха|xа|хa|ha|на|hа|nа)*))'
pattern_s_le_anti_ha = '((ле|le|лe)\s*((anti|анти)(-)*(xa|ха|xа|хa|ha|на|hа|nа)*))'
pattern_s_anti_ha = '((anti|анти)(-)*(xa|ха|xа|хa|ha|на|hа|nа)*)'
pattern_s_me_mil = '((me|ме|mе)/(\d+,\d+|\d+)*(ml|мл))'
pattern_s_le_mil = '((le|ле|lе|лe)/(\d+,\d+|\d+)*(ml|мл))'
pattern_s_me = '(me|ме|мe)'
pattern_s_le = '(le|ле|lе|лe)'
pattern_s_mil = '((ml|мл))'
    
pattern_s_mg_mil = '((мг|mg)/(мл|ml))'
pattern_s_digits_simple = '(\d+,\d+|\d+)'
pattern_s_digits_simple = '(\d+,\d+|\d+\.\d+|\d+)*'
pattern_s_digits_simple = '(\d+,\d+|\d+\.\d+|\d+)'

pattern_s_unit_01 = '('  +\
    pattern_s_anti_ha_me_mil +'|'+ pattern_s_anti_ha_le_mil +'|'+ pattern_s_anti_ha_mil \
    +'|'+ pattern_s_anti_ha_me +'|'+ pattern_s_anti_ha_le +'|'+ pattern_s_me_anti_ha_mil +'|'+ pattern_s_le_anti_ha_mil +'|'+\
    pattern_s_me_anti_ha + '|' + pattern_s_le_anti_ha + '|' + pattern_s_anti_ha + ')'
#pattern_s_anti_ha_me_ml +'|'+ pattern_s_anti_ha_ml +'|'+ pattern_s_anti_ha_me + '|'+ pattern_s_me_anti_ha_ml +'|'+ pattern_s_me_anti_ha_ml +'|'+ \
# есть конфликт паттернов - разносим    
pattern_s_unit_02 = '('  +\
     pattern_s_me_mil +'|'+ pattern_s_le_mil  +'|'+ pattern_s_le  +'|'+ pattern_s_me  +'|'+ pattern_s_mg_mil +'|'\
     + pattern_s_mg \
     + ')' #+ '|'+ pattern_s_mil
     
     #pattern_s_me_mil +'|'+ pattern_s_le_mil  \
#pattern_s_unit_03 = '('  +\
     #pattern_s_le  +'|'+ pattern_s_me  +'|'+ pattern_s_mg_ml +'|'+ pattern_s_mg     + ')'
pattern_s_01 = pattern_s_digits + pattern_s_unit_01
pattern_s_02 = pattern_s_digits + pattern_s_unit_02

def def_dosages_vol_unparsed_02(mis_position, mnn_mis, debug=False ):
    #form_doze_pack = mis_position[len(mnn_mis)+1:]
    if debug: print(f"def_dosages_vol_unparsed_02: type(mis_position): {type(mis_position)}")
    #form_doze_pack = mis_position[len(mnn_mis.strip()):]
    form_doze_pack = mis_position[len(mnn_mis):]
    doze_unit = re.search(pattern_s_01, form_doze_pack.lower())
    if debug: print("doze_unit pattern_s_01:", doze_unit)
    doze_unit_groups = None
    if doze_unit is None:
        doze_unit = re.search(pattern_s_02, form_doze_pack.lower())
        if debug: print("doze_unit pattern_s_02:", doze_unit)
    #if doze_unit: print(doze_unit.groups())
    vol_unparsed = None
    if doze_unit is not None:
        doze_unit_groups = doze_unit.groups()
        doze_unit = doze_unit.group()
        vol_ind = form_doze_pack.lower().find(doze_unit)+ len(doze_unit)
        #vol_unparsed = form_doze_pack[vol_ind+1:]
        vol_unparsed = form_doze_pack[vol_ind:]
    else: vol_unparsed = form_doze_pack
    if doze_unit is not None and len(doze_unit)>0:
        b = mis_position.lower().find(doze_unit)
        doze_unit_str = mis_position[b:b+len(doze_unit)]
    else: doze_unit_str = ''

    return doze_unit, doze_unit_groups, vol_unparsed, doze_unit_str    

def str2num(str_num):
    num = str_num
    try:
        num = int(num)
    except ValueError:
        num = float(num)
    else:
        pass
    return num

def def_k(t_groups):
    k = 1
    if t_groups:
        for g in t_groups:
            if g=='тыс':
                k=1000;  break
    return k

def split_norm_vol(vol):
    if vol is None: return (None, None)
    pattern_s_digits_simple = '(\s*\d+,\d+|\d+\.\d+|\d+)*'
    pattern_s_unit = '\s*(мл|mл|мl|ml|мл|мг|mg|mг)*'
    #if  vol is None: return (None, None)
    volume, unit = None, None
    #vol_unit = re.search(pattern_s_digits_simple + pattern_s_unit, vol)
    vol_unit = re.search(pattern_s_digits_simple + pattern_s_unit, vol.replace('/',''))
    if vol_unit: 
          #print(vol_unit.groups())
          if vol_unit.groups()[0]:
              volume = vol_unit.groups()[0].replace(',','.')
          unit = vol_unit.groups()[1]
    if unit is not None:
        if unit in ['мл','mл','мl', 'ml', 'мл']: 
            unit = 'мл'; 
            if volume is None: volume = 1
        elif unit in ['мг', 'mg', 'mг']: 
            unit = 'мг'; 
            if volume is None: volume = 1
        
    if volume is not None:
        volume = str2num(volume)
        
    return (volume, unit)
# vol_units  = [v['ptn']  for k, v in vol_units_groups.items() if v['ptn'] is not None]
vol_units = ['%'] + ['gr\\.*', 'л', 'Л\\**', 'кг', 'dos', 'доза', 'd', 'г', 'g\\.*', 'gr', 'ml', 'Л', 'литров', 'dosa', 'мл', 'Л\\.*', 'млфл', 'гр\\.*', 'доз', 'kg', 'l', 'дозы', 'л\\.*,*', 'doz', 'дм3', 'doza', 'д\\.*', 'g', 'дз', 'гр', 'dose']
vol_units_pttn = '|'.join([fr"({u})" for u in vol_units])

def def_pseudo_vol_vol_02(doze_unit, vol_unparsed, debug=False):
    pseudo_vol, vol = None, None
    # pseudo_vol_str, vol_str = '', ''
    pseudo_vol_str, vol_str = None, None
    
    # if doze_unit is not None:
    #     sw = 
    # 29.11.2022
    ptn_digits = r"((\d+,\d+)|(\d+\.\d+)|([\d\s]+\d+)|(\d+))"
    # pattern_s_pseudo_vol = fr"/(?P<pseudo_vol>\s*{ptn_digits})*\s*(?P<pseudo_vol_unit>{vol_units_pttn})"
    # pattern_s_vol = fr"(\s(?P<vol>{ptn_digits})\s*(?P<vol_unit>{vol_units_pttn}))"
    # pattern_s_pseudo_vol = fr"/(?P<pseudo_vol>\s*{ptn_digits})*\s*(?P<pseudo_vol_unit>{vol_units_pttn})\s|\.|,|$|\+"
    # pattern_s_vol = fr"(\s(?P<vol>{ptn_digits})\s*(?P<vol_unit>{vol_units_pttn}))\s|\.|,|$|\+"
    # pattern_s_vol = fr"(\s|\b(?P<vol>{ptn_digits})\s*(?P<vol_unit>{vol_units_pttn}))\s|\.|,|$|\+"
    # pattern_s_pseudo_vol = fr"/(?P<pseudo_vol>\s*{ptn_digits})*\s*(?P<pseudo_vol_unit>{vol_units_pttn})(?P<end>\s|\.|,|$|\+)"
    # pattern_s_vol = fr"(\s|\b(?P<vol>{ptn_digits})\s*(?P<vol_unit>{vol_units_pttn}))(?P<end>\s|\.|,|$|\+)"
    pattern_s_pseudo_vol = fr"/(?P<pseudo_vol>\s*{ptn_digits})*\s*(?P<pseudo_vol_unit>{vol_units_pttn})(?P<end>\s|\.|,|$|\+)"
    pattern_s_vol = fr"((?P<vol>\s|\b{ptn_digits})\s*(?P<vol_unit>{vol_units_pttn}))(?P<end>\s|\.|,|$|\+)"
    # на будущее
    # ptn_digits_excl_spaces = r"((\d+,\d+)|(\d+\.\d+)|(\d+))"
    # pattern_s_vol = fr"((?P<vol>\s|\b{ptn_digits_excl_spaces})\s*(?P<vol_unit>{vol_units_pttn}))(?P<end>\s|\.|,|$|\+)"
    
    # vol_units_pttn
    m_pseudo_vol = re.search(pattern_s_pseudo_vol, vol_unparsed, flags = re.I)
    if debug: print(f"def_pseudo_vol_vol_02: m_pseudo_vol: {m_pseudo_vol}")
    if m_pseudo_vol:
        pseudo_vol, pseudo_vol_unit = m_pseudo_vol.group('pseudo_vol'), m_pseudo_vol.group('pseudo_vol_unit')
        pseudo_vol_str = m_pseudo_vol.group().strip()
    m_vol = re.search(pattern_s_vol, vol_unparsed, flags = re.I)
    if debug: print(f"def_pseudo_vol_vol_02: m_vol: {m_vol}")
    if m_vol is not None:
        vol, vol_unit = m_vol.group('vol'), m_vol.group('vol_unit')
        vol_str = m_vol.group().strip()

    return pseudo_vol,vol, pseudo_vol_str, vol_str

def def_pseudo_vol_vol_02_00(doze_unit, vol_unparsed, debug=False):
    pattern_s_2vols = '/*((\d+,\d+|\d+\.\d+|\d+)*\s*(мл|ml|мl)*)\D*((\d+,\d+|\d+\.\d+|\d+)\s*(мл|ml|мl))'
    pattern_s_2vols = '/*((\d+,\d+|\d+.\d+|\d+)*\s*(мл|ml|мl|мг|mg|mг))\D*((\d+,\d+|\d+\.\d+|\d+)\s*(мл|ml|мl))'
    pattern_s_2vols = '/*((\d+,\d+|\d+.\d+|\d+)*\s*\)*(мл|ml|мl|мг|mg|mг))\D*((\d+,\d+|\d+\.\d+|\d+)\s*(мл|ml|мl))'
    pattern_s_2vols = '/*(\b(\d+,\d+|\d+.\d+|\d+)*\s*\)*(мл|ml|мl|мг|mg|mг)\b)\D*(\b(\d+,\d+|\d+\.\d+|\d+)\s*(мл|ml|мl)\b)'
    pattern_s_1vols = '/*(\s*(\d+,\d+|\d+\.\d+|\d+)*\s*(мл|ml|мl)*)'
    pattern_s_1vols = '/*(\s*(\d+,\d+|\d+\.\d+|\d+)*\s*(мл|ml|мl|мг|mg|mг))'

    ptn_digits = r"((\d+,\d+)|(\d+\.\d+)|([\d\s]+\d+)|(\d+))"
        
    # 29.11.2022
    pattern_s_2vols = '/*(\b(\d+,\d+|\d+.\d+|\d+)*\s*\)*(мл|ml|мl|мг|mg|mг)\b)\D*(\b(\d+,\d+|\d+\.\d+|\d+)\s*(мл|ml|мl)\b)'
    pattern_s_1vols = '/*(\s*(\d+,\d+|\d+\.\d+|\d+)*\s*(мл|ml|мl|мг|mg|mг))'
    pattern_s_2vols = fr"/*(\b{ptn_digits}*\s*\)*" + vol_units_pttn + r"\b)\D*(\b{ptn_digits}\s*" + vol_units_pttn + r"\b)"
    pattern_s_1vols = fr"/*(\s*{ptn_digits}*\s*{vol_units_pttn})"
    # vol_units_pttn
    
    pseudo_vol, vol = None, None
    pseudo_vol_str, vol_str = '', ''
    if doze_unit is None: doze_unit = ''
    if vol_unparsed is None: vol_unparsed = ''
    w = doze_unit + vol_unparsed
    #print('doze_unit before:', doze_unit, 'vol_unparsed:', vol_unparsed)
    if '/' in doze_unit: doze_unit = doze_unit[doze_unit.find('/'):]
    
    #if '/' in doze_unit: doze_unit = doze_unit[doze_unit.find('/'):].replace('/','') #; 
    #print('doze_unit:', doze_unit)
    if doze_unit.find('/')>-1: 
        vols = re.search(pattern_s_2vols, (doze_unit+vol_unparsed).lower())
    else:   
        vols = re.search(pattern_s_2vols, (vol_unparsed).lower())
    if vols: 
        #print('2vols***')
        pseudo_vol,vol = vols.groups()[0], vols.groups()[3]
        #print(vols.groups()); print(vols.group(0), vols.group(3))
        #if pseudo_vol.strip() in ['мл','mл','мl', 'ml', 'mg', 'мл']: pseudo_vol = None
        pseudo_vol_str = pseudo_vol
        pseudo_vol = split_norm_vol(pseudo_vol)
        vol_str = vol
        vol = split_norm_vol(vol)
        #print(vols.groups(), vols[0], vols[3])
    elif doze_unit.find('/')>-1 or -1<vol_unparsed.find('/')<2:# and\:
        #if True: #re.search(pattern_s_1vols, (doze_unit+vol_unparsed).lower()):
        #    pass
        if doze_unit.find('/')>-1:
            pseudo_vol = re.search(pattern_s_1vols, (doze_unit+vol_unparsed).lower())
        else:
            pseudo_vol = re.search(pattern_s_1vols, (vol_unparsed).lower())
        #print('pse_v***')
        if pseudo_vol: 
            #print("pseudo_vol.groups()", pseudo_vol.groups())
            pseudo_vol = pseudo_vol.group()
            #print('pseudo_vol', pseudo_vol)
            pseudo_vol_str = pseudo_vol
            pseudo_vol = split_norm_vol(pseudo_vol)
    else: 
        #vol = re.search(pattern_s_1vols, (doze_unit+vol_unparsed).lower())
        vol = re.search(pattern_s_1vols, (vol_unparsed).lower())
        #print('v***')
        if vol: 
            #print("vol.groups()", vol.groups())
            vol = vol.group()
            #print('vol', vol)
            vol_str = vol
            vol = split_norm_vol(vol)
    
    if vol_str is not None and len(vol_str)>0:
        #print(vol_str)
        m = re.search(vol_str, w.lower()) 
        if m: 
            #print('!!', m.span(), m.span()[0])
            w1 = w[:m.span()[0]] + w[m.span()[1]:]
            #print(w)
            vol_str = w [m.span()[0]: m.span()[1]]
        else: w1 = w
    else: w1 = w
    if pseudo_vol_str is not None and len(pseudo_vol_str)>0:
        #print(pseudo_vol_str)
        m = re.search(pseudo_vol_str, w1.lower()) 
        if m: 
            #print('!!', m.span(), m.span()[0])
            #print(w1)
            pseudo_vol_str = w1[m.span()[0]: m.span()[1]]
        
    #if b>-1:
     #   vol_str = w[b:]


    return pseudo_vol,vol, pseudo_vol_str, vol_str

def def_pseudo_vol_vol(doze_unit, vol_unparsed):
    pattern_s_2vols = '/*((\d+,\d+|\d+\.\d+|\d+)*\s*(мл|ml|мl)*)\D*((\d+,\d+|\d+\.\d+|\d+)\s*(мл|ml|мl))'
    pattern_s_2vols = '/*((\d+,\d+|\d+.\d+|\d+)*\s*(мл|ml|мl|мг|mg|mг))\D*((\d+,\d+|\d+\.\d+|\d+)\s*(мл|ml|мl))'
    pattern_s_2vols = '/*((\d+,\d+|\d+.\d+|\d+)*\s*\)*(мл|ml|мl|мг|mg|mг))\D*((\d+,\d+|\d+\.\d+|\d+)\s*(мл|ml|мl))'
    pattern_s_2vols = '/*(\b(\d+,\d+|\d+.\d+|\d+)*\s*\)*(мл|ml|мl|мг|mg|mг)\b)\D*(\b(\d+,\d+|\d+\.\d+|\d+)\s*(мл|ml|мl)\b)'
    pattern_s_1vols = '/*(\s*(\d+,\d+|\d+\.\d+|\d+)*\s*(мл|ml|мl)*)'
    pattern_s_1vols = '/*(\s*(\d+,\d+|\d+\.\d+|\d+)*\s*(мл|ml|мl|мг|mg|mг))'

    pseudo_vol, vol = None, None
    #print('doze_unit before:', doze_unit, 'vol_unparsed:', vol_unparsed)
    if '/' in doze_unit: doze_unit = doze_unit[doze_unit.find('/'):]
    
    #if '/' in doze_unit: doze_unit = doze_unit[doze_unit.find('/'):].replace('/','') #; 
    #print('doze_unit:', doze_unit)
    if doze_unit.find('/')>-1: 
        vols = re.search(pattern_s_2vols, (doze_unit+vol_unparsed).lower())
    else:   
        vols = re.search(pattern_s_2vols, (vol_unparsed).lower())
    if vols: 
        #print('2vols***')
        pseudo_vol,vol = vols.groups()[0], vols.groups()[3]
        #print(vols.groups()); print(vols.group(0), vols.group(3))
        #if pseudo_vol.strip() in ['мл','mл','мl', 'ml', 'mg', 'мл']: pseudo_vol = None
        pseudo_vol = split_norm_vol(pseudo_vol)
        vol = split_norm_vol(vol)
        #print(vols.groups(), vols[0], vols[3])
    elif doze_unit.find('/')>-1 or -1<vol_unparsed.find('/')<2:# and\:
        #if True: #re.search(pattern_s_1vols, (doze_unit+vol_unparsed).lower()):
        #    pass
        if doze_unit.find('/')>-1:
            pseudo_vol = re.search(pattern_s_1vols, (doze_unit+vol_unparsed).lower())
        else:
            pseudo_vol = re.search(pattern_s_1vols, (vol_unparsed).lower())
        #print('pse_v***')
        if pseudo_vol: 
            #print("pseudo_vol.groups()", pseudo_vol.groups())
            pseudo_vol = pseudo_vol.group()
            #print('pseudo_vol', pseudo_vol)
            pseudo_vol = split_norm_vol(pseudo_vol)
    else: 
        #vol = re.search(pattern_s_1vols, (doze_unit+vol_unparsed).lower())
        vol = re.search(pattern_s_1vols, (vol_unparsed).lower())
        #print('v***')
        if vol: 
            #print("vol.groups()", vol.groups())
            vol = vol.group()
            #print('vol', vol)
            vol = split_norm_vol(vol)
   
    return pseudo_vol,vol

def def_doze_measurement_unit(doze_unit, doze_unit_groups, vol_unparsed):
    
    global pattern_s_digits
    global pattern_s_digits_simple
    
    global pattern_s_anti_ha_me_mil 
    global pattern_s_anti_ha_le_mil 
    global pattern_s_anti_ha_mil 
    global pattern_s_anti_ha_me 
    global pattern_s_anti_ha_le 
    global pattern_s_me_anti_ha_mil
    global pattern_s_le_anti_ha_mil
    global pattern_s_me_anti_ha
    global pattern_s_le_anti_ha
    global pattern_s_anti_ha
    global pattern_s_me_mil
    global pattern_s_le_mil
    global pattern_s_me
    global pattern_s_le
    global pattern_s_mg_mil
    global pattern_s_mil
        
    doze = None
    if doze_unit is not None:
        k = def_k(doze_unit_groups) # есть Ли тыс.
        if re.search(pattern_s_digits_simple, doze_unit):
            doze = re.search(pattern_s_digits_simple, doze_unit)
            if doze is not None: doze = doze.group().replace(',','.')
        else: 
            #doze = re.search(pattern_s_digits_simple, doze_unit).group()
            doze = re.search(pattern_s_digits_simple, doze_unit)
            #doze = int(float(doze)*k)  ### 75мг+15.2мг or 75+15.2мг
            if doze is not None: doze = float(doze.group())*k  ### 75мг+15.2мг or 75+15.2мг
    else: doze = None; doze_unit=''
    measurement_unit = None
    #pseudo_vol, vol = None, None
    #print(re.search(pattern_s_anti_ha_me_ml, t_match).groups())
    if re.search(pattern_s_me_anti_ha_mil, doze_unit): measurement_unit = 'антиХа МЕ/мл'  #47
    elif re.search(pattern_s_anti_ha_me_mil, doze_unit): measurement_unit = 'антиХа МЕ/мл'  #85
    elif re.search(pattern_s_le_anti_ha_mil, doze_unit): measurement_unit = 'антиХа ЛЕ/мл'  #47
    elif re.search(pattern_s_anti_ha_le_mil, doze_unit): measurement_unit = 'антиХа ЛЕ/мл'  #85
    elif re.search(pattern_s_anti_ha_me, doze_unit): measurement_unit = 'антиХа МЕ'
    elif re.search(pattern_s_anti_ha_le, doze_unit): measurement_unit = 'антиХа ЛЕ'
    elif re.search(pattern_s_anti_ha, doze_unit): measurement_unit = 'антиХа МЕ'
    elif re.search(pattern_s_anti_ha_mil, doze_unit): measurement_unit = 'антиХа МЕ/мл'
    elif re.search(pattern_s_me_mil, doze_unit): measurement_unit = 'МЕ/мл'
    elif re.search(pattern_s_le_mil, doze_unit): measurement_unit = 'ЛЕ/мл'
    elif re.search(pattern_s_me, doze_unit): measurement_unit = 'МЕ'
    elif re.search(pattern_s_le, doze_unit): measurement_unit = 'ЛЕ'
    elif re.search(pattern_s_mg_mil, doze_unit): measurement_unit = 'мг/мл'
    elif re.search(pattern_s_mg, doze_unit): measurement_unit = 'мг'
    pseudo_vol,vol = def_pseudo_vol_vol(doze_unit, vol_unparsed)
    return doze, measurement_unit, pseudo_vol, vol 

def calc_dosage_per_farm_form_unit(dosage, measurement_unit, pseudo_vol, vol):
    dosage_per_farm_form_unit, farm_unit = None, None
    if dosage is None: 
        farm_unit = None
        #print('dosage is None')
        """
        if vol is not None and len(vol)>0: 
            dosage_per_farm_form_unit = vol[0]
            farm_unit = vol[1]
        """
    else: 
        #dosage = str2num(dosage)
        #print("dosage", dosage)
        if pseudo_vol==vol:
            if vol is not None: dosage_per_farm_form_unit = dosage
            else: dosage_per_farm_form_unit = dosage
        elif pseudo_vol is None: 
        #elif vol is None: 
            #print("vol",len(vol), vol)
            if vol is not None and len(vol)>0:
                dosage_per_farm_form_unit = dosage #vol[0]
            else: dosage_per_farm_form_unit = None
        else:
            if len(pseudo_vol)>0 and vol is not None and len(vol)>0:
                if pseudo_vol[0] == vol [0]: dosage_per_farm_form_unit = dosage
                #else: dosage_per_farm_form_unit = dosage/str2num(pseudo_vol[0])*str2num(vol[0])
                else: dosage_per_farm_form_unit = dosage/pseudo_vol[0]*vol[0]
            #elif len(pseudo_vol)>0:
            else: 
                dosage_per_farm_form_unit = float(dosage)

        #print("dosage_per_farm_form_unit:", dosage_per_farm_form_unit)
        #dosage_per_farm_form_unit = str2num(dosage_per_farm_form_unit)
    if measurement_unit is not None:
        if measurement_unit in ['антиХа МЕ/мл']: farm_unit = 'антиХа МЕ'
        elif measurement_unit in ['антиХа ЛЕ/мл']: farm_unit = 'антиХа ЛЕ'
        elif measurement_unit in ['ЛЕ/мл']: farm_unit = 'ЛЕ'
        elif measurement_unit in ['МЕ/мл']: farm_unit = 'МЕ'
        elif measurement_unit in ['мг/мл']: farm_unit = 'мг'
        else: farm_unit = measurement_unit
        
    
    # красивое окргуление
    #if dosage_per_farm_form_unit is not None and round(dosage_per_farm_form_unit) >0:
    if dosage_per_farm_form_unit is not None:
        try:
            d_p_ph_f = round(dosage_per_farm_form_unit)
            if d_p_ph_f >0  and not dosage_per_farm_form_unit%round(dosage_per_farm_form_unit):
                dosage_per_farm_form_unit = int(dosage_per_farm_form_unit)
        except Exception as err:
            print(err)
    
    return dosage_per_farm_form_unit, farm_unit


def extract_pharm_form(mis_position_unparsed, debug=False )->str:
    s = mis_position_unparsed
    pharm_form_type, pharm_form = '#Н/Д', '#Н/Д'
    pharm_forms, pharm_form_types = [], []

    for i, ph_form in enumerate(pharm_form_types_list): 
        if ph_form not in ['Ампула',]:
            srch_form = re.search(pharm_form_pttn_list[i], s, flags=re.I)
            if debug: print(srch_form, ph_form)
            if srch_form:
                pharm_form = srch_form.group()
                pharm_form_type = ph_form
                break
            elif ph_form == 'Раствор':
                srch_form = re.search(r"(?:(?<![a-zA-Z])sol\.)", s) # , flags=re.I (выбираем sol смаленькой буквы)
                # s = 'NOVOCAINI SOL. 0,25% 400мл N1 раствор для инъекций флакон'
                # s = 'Prednisoloni 30 мг 2 ml sol. N3'
                if srch_form:
                    pharm_form = srch_form.group()
                    pharm_form_type = ph_form
                    break

    return pharm_form_type, pharm_form    

def extract_pharm_form_02(mis_position_unparsed, debug=False )->str:
    s = mis_position_unparsed
    pharm_form_type, pharm_form, pharm_form_span = '#Н/Д', '#Н/Д', None
    pharm_forms, pharm_form_types = [], []

    for i, ph_form in enumerate(pharm_form_types_list): 
        if ph_form not in ['Ампула',]:
            srch_form = re.search(pharm_form_pttn_list[i], s, flags=re.I)
            if debug: print(srch_form, ph_form)
            if srch_form:
                pharm_form = srch_form.group()
                pharm_form_span = srch_form.span()
                pharm_form_type = ph_form
                break
            elif ph_form == 'Раствор':
                srch_form = re.search(r"(?:(?<![a-zA-Z])sol\.)", s) # , flags=re.I (выбираем sol смаленькой буквы)
                # s = 'NOVOCAINI SOL. 0,25% 400мл N1 раствор для инъекций флакон'
                # s = 'Prednisoloni 30 мг 2 ml sol. N3'
                if srch_form:
                    pharm_form = srch_form.group()
                    pharm_form_type = ph_form
                    pharm_form_span = srch_form.span()
                    break

    return pharm_form_type, pharm_form, pharm_form_span

def extract_TN_ext(mis_position, debug=False)->str:
    if debug: print(type(mis_position), mis_position)
    if type(mis_position)== pd.core.series.Series:
        if mis_position.get(mis_position_col_name): 
            mis_position = mis_position[mis_position_col_name]
    else: mis_position = str(mis_position)

    mnn_mis, tn_ru, tn_lat = def_mnn_mis(mis_position)
    if debug: print("extract_TN_ext: mnn_mis:-->", mnn_mis)
    #lf_unparsed = def_lf_unparsed(mis_position, debug=False)
    #print("lf_unparsed:-->", lf_unparsed))
    if mnn_mis is not None: 
        mnn_unparsed = re.sub(mnn_mis, "", mis_position)
    if debug: print("extract_TN_ext: mnn_unparsed:-->", mnn_unparsed)
    #pharm_form_type, pharm_form = extract_parm_form(mnn_unparsed)
    pharm_form_type, pharm_form, pharm_form_span = extract_pharm_form_02(mis_position, debug=debug)
    if debug: print (f"extract_TN_ext: pharm_form_type: '{pharm_form_type}', pharm_form: '{pharm_form}'" )

    doze_unit, doze_unit_groups, vol_unparsed, doze_unit_str = def_dosages_vol_unparsed_02(mis_position, mnn_mis, debug=debug )
    if debug: print (f"extract_TN_ext: doze_unit: '{doze_unit}', vol_unparsed: '{vol_unparsed}', doze_unit_str: '{doze_unit_str}'")
    pseudo_vol, vol, pseudo_vol_str, vol_str = def_pseudo_vol_vol_02(doze_unit, vol_unparsed, debug=debug)
    if debug: print (f"extract_TN_ext: pseudo_vol: '{pseudo_vol}', vol: '{vol}', pseudo_vol_str: '{pseudo_vol_str}', vol_str: '{vol_str}'")
    if doze_unit_str is not None and len(doze_unit_str)>0: b_doze_unit = mis_position.find(doze_unit_str)
    else: b_doze_unit = np.inf
    if vol_str is not None:  b_vol = mis_position.find(vol_str)
    else: b_vol = np.inf
    if pseudo_vol_str is not None:  b_pseudo_vol = mis_position.find(pseudo_vol_str)
    else: b_pseudo_vol = np.inf
    # if pharm_form is not None: b_pharm_form = mis_position.find(pharm_form)
    # if pharm_form is not None and (pharm_form != '#НД'): b_pharm_form = pharm_form_span[0]
    if pharm_form_span is not None: b_pharm_form = pharm_form_span[0]
    else: b_pharm_form = np.inf
    if debug: print(f"extract_TN_ext: b_doze_unit: {b_doze_unit}, b_vol: {b_vol}, b_pseudo_vol: {b_pseudo_vol}, b_pharm_form: {b_pharm_form}")
    # b_min = min(b_doze_unit or np.inf, b_vol or np.inf, b_pharm_form or np.inf)
    # b_min = min(b_doze_unit, b_vol, b_pseudo_vol, b_pharm_form)
    b_min = min(b_doze_unit or np.inf, b_vol or np.inf, b_pseudo_vol or np.inf, b_pharm_form or np.inf)
    # or np.inf - уходим от нуля
    
    if b_min>-1 and b_min<np.inf:
        try: 
            tn_ext = mis_position[:b_min].strip()
        except Exception as err:
            print(err)
            print("extract_TN_ext: b_doze_unit, b_vol, b_pharm_form", f"'{b_doze_unit}', '{b_vol}', '{b_pharm_form}'")
            print("extract_TN_ext: b_min, mis_position",b_min,  mis_position)
            sys.exit(2)
    # else: tn_ext=''
    else: tn_ext= None
    if debug: print(f"extract_TN_ext: tn_ext: '{tn_ext}'"); print()
    #return tn_ext v01
    #return [tn_ext, pharm_form_type, pharm_form]
    #return tn_ext, pharm_form_type, pharm_form
    return tn_ru, tn_lat, tn_ext, pharm_form_type, pharm_form

def extract_TN_ext_00_02(mis_position, debug=False)->str:
    if debug: print(type(mis_position), mis_position)
    if type(mis_position)== pd.core.series.Series:
        if mis_position.get(mis_position_col_name): 
            mis_position = mis_position[mis_position_col_name]
    else: mis_position = str(mis_position)

    mnn_mis, tn_ru, tn_lat = def_mnn_mis(mis_position)
    if debug: print("extract_TN_ext: mnn_mis:-->", mnn_mis)
    #lf_unparsed = def_lf_unparsed(mis_position, debug=False)
    #print("lf_unparsed:-->", lf_unparsed))
    if mnn_mis is not None: 
        mnn_unparsed = re.sub(mnn_mis, "", mis_position)
    if debug: print("extract_TN_ext: mnn_unparsed:-->", mnn_unparsed)
    #pharm_form_type, pharm_form = extract_parm_form(mnn_unparsed)
    pharm_form_type, pharm_form = extract_pharm_form(mis_position)
    if debug: print (f"extract_TN_ext: pharm_form_type: '{pharm_form_type}', pharm_form: '{pharm_form}'" )

    doze_unit, doze_unit_groups, vol_unparsed, doze_unit_str = def_dosages_vol_unparsed_02(mis_position, mnn_mis, debug=debug )
    if debug: print (f"extract_TN_ext: doze_unit: '{doze_unit}', vol_unparsed: '{vol_unparsed}', doze_unit_str: '{doze_unit_str}'")
    pseudo_vol, vol, pseudo_vol_str, vol_str = def_pseudo_vol_vol_02(doze_unit, vol_unparsed, debug=debug)
    if debug: print (f"extract_TN_ext: pseudo_vol: '{pseudo_vol}', vol: '{vol}', pseudo_vol_str: '{pseudo_vol_str}', vol_str: '{vol_str}'")
    if doze_unit_str is not None and len(doze_unit_str)>0: b_doze_unit = mis_position.find(doze_unit_str)
    else: b_doze_unit = np.inf
    if vol_str is not None:  b_vol = mis_position.find(vol_str)
    else: b_vol = np.inf
    if pseudo_vol_str is not None:  b_pseudo_vol = mis_position.find(pseudo_vol_str)
    else: b_pseudo_vol = np.inf
    if pharm_form is not None: b_pharm_form = mis_position.find(pharm_form)
    else: b_pharm_form = np.inf
    if debug: print(f"extract_TN_ext: b_doze_unit: {b_doze_unit}, b_vol: {b_vol}, b_pseudo_vol: {b_pseudo_vol}, b_pharm_form: {b_pharm_form}")
    # b_min = min(b_doze_unit or np.inf, b_vol or np.inf, b_pharm_form or np.inf)
    # b_min = min(b_doze_unit, b_vol, b_pseudo_vol, b_pharm_form)
    b_min = min(b_doze_unit or np.inf, b_vol or np.inf, b_pseudo_vol or np.inf, b_pharm_form or np.inf)
    # or np.inf - уходим от нуля
    
    if b_min>-1 and b_min<np.inf:
        try: 
            tn_ext = mis_position[:b_min].strip()
        except Exception as err:
            print(err)
            print("extract_TN_ext: b_doze_unit, b_vol, b_pharm_form", f"'{b_doze_unit}', '{b_vol}', '{b_pharm_form}'")
            print("extract_TN_ext: b_min, mis_position",b_min,  mis_position)
            # sys.exit(2)
    # else: tn_ext=''
    else: tn_ext= None
    if debug: print(f"extract_TN_ext: tn_ext: '{tn_ext}'"); print()
    #return tn_ext v01
    #return [tn_ext, pharm_form_type, pharm_form]
    #return tn_ext, pharm_form_type, pharm_form
    return tn_ru, tn_lat, tn_ext, pharm_form_type, pharm_form

def extract_TN_ext_00(mis_position, debug=False)->str:
    if debug: print(type(mis_position), mis_position)
    if type(mis_position)== pd.core.series.Series:
        if mis_position.get(mis_position_col_name): 
            mis_position = mis_position[mis_position_col_name]
    else: mis_position = str(mis_position)

    mnn_mis, tn_ru, tn_lat = def_mnn_mis(mis_position)
    if debug: print("mnn_mis:-->", mnn_mis)
    #lf_unparsed = def_lf_unparsed(mis_position, debug=False)
    #print("lf_unparsed:-->", lf_unparsed))
    if mnn_mis is not None: 
        mnn_unparsed = re.sub(mnn_mis, "", mis_position)
    #print("mnn_unparsed:-->", mnn_unparsed)
    #pharm_form_type, pharm_form = extract_parm_form(mnn_unparsed)
    pharm_form_type, pharm_form = extract_pharm_form(mis_position)
    if debug: print (F"pharm_form_type: '{pharm_form_type}', pharm_form: '{pharm_form}'" )

    doze_unit, doze_unit_groups, vol_unparsed, doze_unit_str = def_dosages_vol_unparsed_02(mis_position, mnn_mis )
    pseudo_vol, vol, pseudo_vol_str, vol_str = def_pseudo_vol_vol_02(doze_unit, vol_unparsed)
    
    if doze_unit_str is not None: b_doze_unit = mis_position.find(doze_unit_str)
    else: b_doze_unit = np.inf
    if vol_str is not None:  b_vol = mis_position.find(vol_str)
    else: b_vol = np.inf
    if pharm_form is not None: b_pharm_form = mis_position.find(pharm_form)
    else: b_pharm_form = np.inf
    if debug: print(f"b_doze_unit: {b_doze_unit}, b_vol: {b_vol}, b_pharm_form: {b_pharm_form}")
    b_min = min(b_doze_unit or np.inf, b_vol or np.inf, b_pharm_form or np.inf)
    if b_min>-1 and b_min<np.inf:
        try: 
            tn_ext = mis_position[:b_min].strip()
        except Exception as err:
            print(err)
            print("b_doze_unit, b_vol, b_pharm_form", f"'{b_doze_unit}', '{b_vol}', '{b_pharm_form}'")
            print("b_min, mis_position",b_min,  mis_position)
            sys.exit(2)
    else: tn_ext=''
    if debug: print(f"tn_ext: {tn_ext}"); print()
    #return tn_ext v01
    #return [tn_ext, pharm_form_type, pharm_form]
    #return tn_ext, pharm_form_type, pharm_form
    return tn_ru, tn_lat, tn_ext, pharm_form_type, pharm_form

def is_ru_lat_chars(name):
    fl_lat, fl_ru = False, False
    for ch in name:
        if not fl_ru: 
            if ord(ch)>ord('z'): fl_ru = True  # буква по номеру после z уже не латинская и первая не может быть цифрой
        if not fl_lat: 
            if ord(ch)<=ord('z'): fl_lat = True
        if fl_ru and fl_lat: return True

    return False

def update__tn_ru_ext__tn_lat_ext(tn_ext, debug=False):
    #на входе строка со скобками - по идее
    if debug: print("type(tn_ext)", type(tn_ext))
    if type(tn_ext) == pd.Series: # вошли из Apply
        if debug: print("tn_ext.keys()", tn_ext.keys())
        #tn_ext = tn_ext['tn_ext']
        tn_ext = tn_ext[0]
    if debug: print("type(tn_ext)", type(tn_ext), tn_ext)
    tn_ru_ext, tn_lat_ext = None, None
    p = r"(.+)\((.+)\)"
    if not(tn_ext is None or len(tn_ext)==0 or re.search(r"\(.+\)", tn_ext) is None):
        if is_ru_lat_chars(tn_ext):
            tn_1_tn_2 = re.search(p, tn_ext)
            if tn_1_tn_2:
                tn_1, tn_2 = tn_1_tn_2.groups()
                if debug: print(tn_1, tn_2)
                if def_Ru_lat(tn_1): 
                    tn_ru_ext = tn_1.strip()
                    if not def_Ru_lat(tn_2): tn_lat_ext = tn_2.strip()
                    else: # обе части русские  может быть и такое latin chars закрались после скобок
                        pass # считаем чтовтрая часть уточнение
                else:
                    tn_lat_ext = tn_1.strip()
                    if def_Ru_lat(tn_2): tn_ru_ext = tn_2.strip()
                    else: # обе части латинские может быть и такое русские  закрались после скобок
                        pass # считаем чтовтрая часть уточнение
    # Обработка исключений
    if tn_ru_ext is not None:
        if tn_ru_ext in ['тропические фрукты']: tn_ru_ext = None
    if tn_ext is not None and len(tn_ext)> 0:
        if tn_ru_ext is None:
            if def_Ru_lat(tn_ext): tn_ru_ext = tn_ext
        if tn_lat_ext is None: 
            if not def_Ru_lat(tn_ext): tn_lat_ext = tn_ext

    if debug: print(tn_ru_ext, tn_lat_ext)
    return tn_ru_ext, tn_lat_ext

def extract_MNN_from_tn_ru_ext(tn_ru_ext):
    tn_ru_ext_update, mnn_parsing = tn_ru_ext, None
    if tn_ru_ext is None: return tn_ru_ext_update, mnn_parsing
    m = re.search(r"(?:\(МНН\s.+\))|(?:\(*МНН\s[\w\+]+\)*)", tn_ru_ext)
    if m is not None: 
        mnn_parsing = m.group()
        tn_ru_ext_update = tn_ru_ext.replace(mnn_parsing,'').strip()
        mnn_parsing = re.sub("[\(\)]",'', mnn_parsing).replace('МНН','').strip()
    return tn_ru_ext_update, mnn_parsing

def extract_pharm_form_from_tn_ru_ext (tn_ru_ext):
    tn_ru_ext_update, pharm_form_parsing, pharm_form_type_parsing = tn_ru_ext, '#Н/Д', '#Н/Д'
    if tn_ru_ext is None: return tn_ru_ext_update, pharm_form_parsing
    pharm_form_pttn_list_for_tn_ru_ext = [p.replace(r"(?:\b",r"(?:" ) for p in  pharm_form_pttn_list]
    for i, ph_form in enumerate(pharm_form_types_list): 
        if ph_form not in ['Ампула',]:
            srch_form = re.search(pharm_form_pttn_list_for_tn_ru_ext[i], tn_ru_ext, flags=re.I)
            if srch_form:
                pharm_form_parsing = srch_form.group()
                pharm_form_type_parsing = ph_form
                break
    return tn_ru_ext_update, pharm_form_parsing, pharm_form_type_parsing

def update_tn_ru_ext_02(tn_ru_ext):
    if tn_ru_ext is None: return tn_ru_ext
    # уьираем то что в скобках
    tn_ru_ext_update = re.sub(r"\(.+\)*",'', tn_ru_ext).strip()
    # убираем  в конце строки ненужные симовлы
    tn_ru_ext_update = re.sub(r"([®\.,\(\)]\s*)|(№\s*\d*)$", '', tn_ru_ext_update).strip()
    # убираем цифры-опечатки в конце 'Парацетамол1' кроме 'АСС 100'
    tn_ru_ext_update = re.sub(r"(?<!\s|\d)\d+$", r"", tn_ru_ext_update)
    tn_ru_ext_update = re.sub(r"(?<=\s\d\s)|(?<=\s\d\d\s)|(?<=\s\d\d\d\s)|(?<=\s\d\d\d\d\s)(?:\d+)*$", r"", tn_ru_ext_update)
    # убираем неправильный дефис
    tn_ru_ext_update = re.sub('–','-', tn_ru_ext_update)
    # пересобираем слова с дефисом, убирая лишние пробелы
    tn_ru_ext_update = '-'.join([t.strip() for t in tn_ru_ext_update.split('-')])
    return tn_ru_ext_update

def correct_tn_ru_ext(tn_ru_ext):
    tn_ru_ext_clean_01, mnn_parsing = extract_MNN_from_tn_ru_ext(tn_ru_ext)
    tn_ru_ext_clean_02 = update_tn_ru_ext_02(tn_ru_ext_clean_01)
    tn_ru_ext_clean, pharm_form_parsing, pharm_form_type_parsing = extract_pharm_form_from_tn_ru_ext (tn_ru_ext_clean_02)
    return tn_ru_ext_clean, mnn_parsing, pharm_form_parsing, pharm_form_type_parsing    

### Comlex_doze
# v24.11.2022
# v23.11.2022
### Comlex_doze

def enhance_units_03(comlex_doze_parts_list, debug=False):
    # на взоде ['875', '35', '125 mg', '11', '22mkg/мл', '23мг|мл', '24 kg\мл']
    comlex_doze_list_enhanced = [] #comlex_doze_list
    ptn_digits = r"((\d+,\d+)|(\d+\.\d+)|([\d\s]+\d+)|(\d+))"
    ptn_digits = r"((\d+,\d+)|(\d+\.\d+)|(\d+))"
    ptn_mu = r"[^\d]*"
    last_mu = (None, None, None, None, None, None, None, None) # measurement unit
    fl_new_update = False
    for i, (item, doze, doze_unit, pseudo_vol, pseudo_vol_unit, base_doze_unit, k_doze, pseudo_vol_base_unit, k_vol) in enumerate(comlex_doze_parts_list[::-1]):
        # last_mu = (doze_unit, pseudo_vol, pseudo_vol_unit)
        # if fl_new_update:
        if i > 0:
            # if doze_unit is None or (doze_unit is not None and (doze_unit == '')) or pseudo_vol_unit is None:
            if doze_unit is None: # or pseudo_vol_unit is None:
                doze_unit, pseudo_vol, pseudo_vol_unit, base_doze_unit, k_doze, pseudo_vol_base_unit, k_vol = last_mu
                # last_mu = (doze_unit, pseudo_vol, pseudo_vol_unit, base_doze_unit, k)
                # print(f"last_mu: {last_mu}")
            elif pseudo_vol_unit is None and last_mu[1] is not None:
                pseudo_vol_unit = last_mu[1]
                pseudo_vol_base_unit, k_vol = last_mu[-2], last_mu[-1]
            elif doze_unit is not None and \
            ((last_mu[0] is not None and (doze_unit!=last_mu[0])) or last_mu[0] is None): # \
                # при смене doze_unit полностью переходим на новы набор units
                # pseudo_vol, pseudo_vol_unit = last_mu[1], last_mu[2]
                last_mu = (doze_unit, pseudo_vol, pseudo_vol_unit, base_doze_unit, k_doze, pseudo_vol_base_unit, k_vol)
            elif pseudo_vol_unit is not None and \
            ((last_mu[1] is not None and (pseudo_vol_unit !=last_mu[1])) or last_mu[1] is None):
                 last_mu = (doze_unit, pseudo_vol, pseudo_vol_unit, base_doze_unit, k_doze, pseudo_vol_base_unit, k_vol)
        else: 
            last_mu = (doze_unit, pseudo_vol, pseudo_vol_unit, base_doze_unit, k_doze, pseudo_vol_base_unit, k_vol)
            # fl_new_update = True
        
        comlex_doze_list_enhanced.append([item, doze, doze_unit, pseudo_vol, pseudo_vol_unit, base_doze_unit, k_doze, pseudo_vol_base_unit, k_vol])
    return comlex_doze_list_enhanced[::-1]

def enhance_units_02(comlex_doze_parts_list, debug=False):
    # на взоде ['875', '35', '125 mg', '11', '22mkg/мл', '23мг|мл', '24 kg\мл']
    comlex_doze_list_enhanced = [] #comlex_doze_list
    ptn_digits = r"((\d+,\d+)|(\d+\.\d+)|([\d\s]+\d+)|(\d+))"
    ptn_digits = r"((\d+,\d+)|(\d+\.\d+)|(\d+))"
    ptn_mu = r"[^\d]*"
    last_mu = (None, None, None, None, None) # measurement unit
    for i, (item, doze, doze_unit, pseudo_vol, pseudo_vol_unit, base_doze_unit, k) in enumerate(comlex_doze_parts_list[::-1]):
        # last_mu = (doze_unit, pseudo_vol, pseudo_vol_unit)
        if doze_unit is None or doze_unit == '':
            doze_unit, pseudo_vol, pseudo_vol_unit, base_doze_unit, k = last_mu
            # print(f"last_mu: {last_mu}")
        elif pseudo_vol_unit is None:
            pseudo_vol, pseudo_vol_unit = last_mu[1], last_mu[2]
        else: last_mu = (doze_unit, pseudo_vol, pseudo_vol_unit, base_doze_unit, k)
        
        comlex_doze_list_enhanced.append([item, doze, doze_unit, pseudo_vol, pseudo_vol_unit, base_doze_unit, k])
    return comlex_doze_list_enhanced[::-1]

def define_doze_parts_02(complex_doze_list, debug=False):
    ptn_digits = r"((\d+,\d+)|(\d+\.\d+)|(\d+))"
    ptn_mu = r"[^\d]*"
    comlex_doze_parts_list = []
    base_doze_unit, k_doze = None, None
    pseudo_vol_base_unit, k_vol = None, None
    for item in complex_doze_list:
        item = item.replace('\\','/').replace('|','/').strip()
        if '/' in item:
            m_doze = re.search(ptn_digits, item[:item.rfind('/')])
            if m_doze is not None:
                doze = m_doze.group()
            else: doze = None
            m_doze_unit = re.search(ptn_mu, re.sub(doze, '', (item[:item.rfind('/')])) if doze is not None else item)
            
            if m_doze_unit is not None: 
                doze_unit = m_doze_unit.group().strip()
                doze_unit = units_total_dict.get(doze_unit.lower())
            else:
                doze_unit = None
            m_pseudo_vol = re.search(ptn_digits, item[item.rfind('/')+1:])
            if m_pseudo_vol is not None:
                pseudo_vol = m_pseudo_vol.group()
                # try: 
                #     pseudo_vol = float(m_pseudo_vol.group())
                # except Exception as err:
                #     pseudo_vol = m_pseudo_vol.group()
            else: 
                pseudo_vol = None
            
            m_pseudo_vol_unit = re.search(ptn_mu, re.sub(pseudo_vol if pseudo_vol is not None else '', '', 
                                 (item[item.rfind('/')+1:])) if pseudo_vol is not None else item[item.rfind('/')+1:])
            if debug: print(f"define_doze_parts_02: m_pseudo_vol_unit: {m_pseudo_vol_unit}")
            if m_pseudo_vol_unit is not None:
                pseudo_vol_unit = m_pseudo_vol_unit.group().strip()
                pseudo_vol_unit = units_total_dict.get(pseudo_vol_unit.lower())
                if debug: print(f"define_doze_parts_02: pseudo_vol_unit: '{pseudo_vol_unit}'")
                pseudo_vol_base_unit_dict = base_pseudo_vol_unit_esklp.get(pseudo_vol_unit)
                
                if pseudo_vol_base_unit_dict is not None:
                    pseudo_vol_base_unit = pseudo_vol_base_unit_dict.get('base_unit')
                    k_vol = pseudo_vol_base_unit_dict.get('k')
                else:
                    pseudo_vol_base_unit = None
                    k_vol = None
            else:
                pseudo_vol_base_unit = None
                k_vol = None
        else:
            m_doze  = re.search(ptn_digits, item)
            if m_doze is not None:
                doze = m_doze.group()
            else: doze = None
            m_doze_unit = re.search(ptn_mu, re.sub(doze, '', item) if doze is not None else item)
            if m_doze_unit is not None: 
                doze_unit = m_doze_unit.group().strip()
                doze_unit = units_total_dict.get(doze_unit.lower())
                
            else:
                doze_unit = None
                
            pseudo_vol = None
            pseudo_vol_unit = None
        
        # if debug:  print(f"enhance_units_02: m_mu: {m_mu}")
        #         if m_doze_unit is not None:
        #             if '/' in item:
        #                 mu = m_mu.group().replace('\\','/').replace('|','/').strip() + item[item.rfind('/'):]
        #             else:
        #                 mu = m_mu.group().replace('\\','/').replace('|','/').strip()
        #             if debug:  print(f"enhance_units_02: mu: {mu}")

        #             if len(mu)==0: mu = None
        #         else: mu = None
        # base_doze_unit_pre = recalc_doze_units_dict.get(doze_unit)
        base_doze_unit_pre = base_doze_unit_esklp.get(doze_unit)
        if base_doze_unit_pre is not None:
            base_doze_unit = base_doze_unit_pre.get('base_unit')
            k_doze = base_doze_unit_pre.get('k')
        else: 
            base_doze_unit = None
            k_doze = None
        comlex_doze_parts_list.append([item, doze, doze_unit, pseudo_vol, pseudo_vol_unit, 
                                             base_doze_unit, k_doze, pseudo_vol_base_unit, k_vol])
    
    return comlex_doze_parts_list

def define_doze_parts(complex_doze_list, debug=False):
    ptn_digits = r"((\d+,\d+)|(\d+\.\d+)|(\d+))"
    ptn_mu = r"[^\d]*"
    comlex_doze_parts_list = []
    base_doze_unit, k = None, None
    for item in complex_doze_list:
        item = item.replace('\\','/').replace('|','/').strip()
        if '/' in item:
            m_doze = re.search(ptn_digits, item[:item.rfind('/')])
            if m_doze is not None:
                doze = m_doze.group()
            else: doze = None
            m_doze_unit = re.search(ptn_mu, re.sub(doze, '', (item[:item.rfind('/')])) if doze is not None else item)
            
            if m_doze_unit is not None: 
                doze_unit = m_doze_unit.group().strip()
                doze_unit = units_total_dict.get(doze_unit.lower())
            else:
                doze_unit = None
            m_pseudo_vol = re.search(ptn_digits, item[item.rfind('/')+1:])
            if m_pseudo_vol is not None:
                pseudo_vol = m_pseudo_vol.group()
                # try: 
                #     pseudo_vol = float(m_pseudo_vol.group())
                # except Exception as err:
                #     pseudo_vol = m_pseudo_vol.group()
            else: 
                pseudo_vol = None
            
            m_pseudo_vol_unit = re.search(ptn_mu, re.sub(pseudo_vol, '', (item[item.rfind('/')+1:])) if pseudo_vol is not None else item[item.rfind('/')+1:])
            if m_pseudo_vol_unit is not None:
                pseudo_vol_unit = m_pseudo_vol_unit.group().strip()
                pseudo_vol_unit = units_total_dict.get(pseudo_vol_unit.lower())
            else:
                pseudo_vol_unit = None
        else:
            m_doze  = re.search(ptn_digits, item)
            if m_doze is not None:
                doze = m_doze.group()
            else: doze = None
            m_doze_unit = re.search(ptn_mu, re.sub(doze, '', item) if doze is not None else item)
            if m_doze_unit is not None: 
                doze_unit = m_doze_unit.group().strip()
                doze_unit = units_total_dict.get(doze_unit.lower())
            else:
                doze_unit = None
                
            pseudo_vol = None
            pseudo_vol_unit = None
        
        # if debug:  print(f"enhance_units_02: m_mu: {m_mu}")
    #         if m_doze_unit is not None:
    #             if '/' in item:
    #                 mu = m_mu.group().replace('\\','/').replace('|','/').strip() + item[item.rfind('/'):]
    #             else:
    #                 mu = m_mu.group().replace('\\','/').replace('|','/').strip()
    #             if debug:  print(f"enhance_units_02: mu: {mu}")
                
    #             if len(mu)==0: mu = None
    #         else: mu = None
        base_doze_unit_pre = recalc_doze_units_dict.get(doze_unit)
        if base_doze_unit_pre is not None:
            base_doze_unit = base_doze_unit_pre.get('base_unit')
            k = base_doze_unit_pre.get('k')
        else: 
            base_doze_unit = None
            k = None
        comlex_doze_parts_list.append([item, doze, doze_unit, pseudo_vol, pseudo_vol_unit, base_doze_unit, k])
    
    return comlex_doze_parts_list

def calc_total_doze( complex_doze_list_enhanced, 
                    doze, doze_unit, pseudo_vol, pseudo_vol_unit, debug=False):
    # doze, doze_unit = None, None
    # [['40 мг/мл', '40', 'мг', None, 'мл', 'мг', 1.0, 'мл', 1.0], ['0.005 мг/мл', '0.005', 'мг', None, 'мл', 'мг', 1.0, 'мл', 1.0]]
    # pseudo_vol, pseudo_vol_unit = None, None
    if debug: print(f"calc_total_doze: complex_doze_list_enhanced: {complex_doze_list_enhanced}")
    complex_doze_list_enhanced_01 = [[e if e is not None else '' for e in el ] for el in complex_doze_list_enhanced ]
    if debug: print(f"calc_total_doze: complex_doze_list_enhanced_01: {complex_doze_list_enhanced_01}")
    # unit_types = [' '.join(el[2:]).strip() for el in complex_doze_list_enhanced_01]
    total_unit_types = [el[2].strip() + ('/' if len(el[4].strip())>0 else '') + (el[3].strip() + ' ' if len(el[3].strip())>0 else '' )  + el[4].strip() for el in complex_doze_list_enhanced_01]
    doze_unit_types = [el[2].strip() for el in complex_doze_list_enhanced_01]
    # base_doze_unit_types = [el[-2].strip() for el in complex_doze_list_enhanced_01]
    base_doze_unit_types = [el[5].strip() for el in complex_doze_list_enhanced_01]
    pseudo_vol_s = [el[3].strip() for el in complex_doze_list_enhanced_01]
    pseudo_vol_unit_types = [el[4].strip() for el in complex_doze_list_enhanced_01]
    
    
    if debug: print(f"calc_total_doze: total_unit_types: {total_unit_types}")
    # total_unit_types_set = list(set(total_unit_types))
    base_doze_unit_types_set = list(set(base_doze_unit_types))
    pseudo_vol_unit_types_set = list(set(pseudo_vol_unit_types))
    if debug: 
        print(f"calc_total_doze: base_doze_unit_types_set: {base_doze_unit_types_set}")
        print(f"calc_total_doze: pseudo_vol_unit_types_set: {pseudo_vol_unit_types_set}")
    if (len(base_doze_unit_types_set) == 1) and (len(pseudo_vol_unit_types_set) == 1):
        try:
            doze = sum([float(el[1].replace(',', '.')) * el[-1] for el in complex_doze_list_enhanced])
        except Exception as err:
            if debug: print(f"calc_total_doze:", err)
            doze = None
        # doze_unit = doze_unit_types[0]
        doze_unit = base_doze_unit_types[0]
        pseudo_vol = pseudo_vol_s[-1] if pseudo_vol_s[-1] != '' else None
        pseudo_vol_unit = pseudo_vol_unit_types[-1] if pseudo_vol_unit_types[-1] != '' else None
    #     elif len(total_unit_types_set) == 2:
    #         # unit_types = [el[2].strip() for el in complex_doze_list_enhanced_01]
    #         if debug: print(f"calc_total_doze: doze_unit_types: {doze_unit_types}")
    #         doze_unit_types_set = list(set(doze_unit_types))
    #         if len(doze_unit_types_set)==1:
    #             # total_unit_types_sorted = total_unit_types.sort(key=len)
    #             total_unit_types_sorted = sorted(total_unit_types, key=len)

    #             if debug: print(f"calc_total_doze: total_unit_types_sorted: {total_unit_types_sorted}")
    #             if total_unit_types_sorted[-1] == total_unit_types[-1]: # последний жлемент самый длинный
    #                 try:
    #                     doze = sum([float(el[1].replace(',', '.')) * el[-1] for el in complex_doze_list_enhanced])
    #                 except Exception as err:
    #                     if debug: print(f"calc_total_doze:", err)
    #                     doze = None

    #                 # doze_unit = doze_unit_types[-1]
    #                 doze_unit = base_doze_unit_types[-1]
    #                 pseudo_vol = pseudo_vol_s[-1] if pseudo_vol_s[-1] != '' else None
    #                 pseudo_vol_unit = pseudo_vol_unit_types[-1] if pseudo_vol_unit_types[-1] != '' else None
    #             # else: doze=None
    if doze_unit is not None and len(doze_unit) == 0:
        doze_unit = None
    # return doze, doze_unit
    return doze, doze_unit, pseudo_vol, pseudo_vol_unit

def complex_doze_handler_02(handler_group, unparsed_str, doze_str, 
                            doze, doze_unit, pseudo_vol, pseudo_vol_unit,
                            debug=False):
    complex_doze_list, complex_doze_str, complex_doze_list_enhanced = None, None, None
    complex_doze_ptn_str = doze_units_groups[handler_group]['cmplx_ptn_str']
    ptn_digit_plus = r"\d+[\.,\w\s]*\+"
    if complex_doze_ptn_str is not None:
        # заменим скобки на пробелы чтобы избежать 'Мадопар "125" капс 100мг+25мг'
        if debug: print(f"complex_doze_handler_02: complex_doze_ptn_str is not None")
        unparsed_str = re.sub(r"[\(\)]", ' ', unparsed_str)
        # уточняем положение группы цифр с +
        m_det = re.search(ptn_digit_plus , unparsed_str)
        if m_det is not None:
            
            # m = re.search(complex_doze_ptn_str, unparsed_str, flags=re.I)
            m = re.search(complex_doze_ptn_str, unparsed_str[m_det.span()[0]:], flags=re.I)

            if m is not None:
                if debug: print(f"complex_doze_handler_02: m is not None")
                complex_doze_str = m.group().strip()
                if complex_doze_str is not None and '+' in complex_doze_str:
                    if debug: print(f"complex_doze_handler_02: complex_doze_str is not None and '+' in complex_doze_str: '{complex_doze_str}'")
                    complex_doze_list = complex_doze_str.split('+')

                    # не обрабатывает '20mg/ml/12.5mg/ml'
                    # 125 mg (1 caps.)+80 mg (2 caps.) +180 mg (3 caps.) 
                    # complex_doze_list_pseudo_vol = define_pseudo_vol(complex_doze_list, debug=debug)
                    if debug: print(f"complex_doze_handler_02: complex_doze_list: {complex_doze_list}")
                    complex_doze_parts_list = define_doze_parts_02(complex_doze_list, debug=debug)
                    if debug: print(f"complex_doze_handler_02: complex_doze_parts_list: {complex_doze_parts_list}")
                    complex_doze_list_enhanced = enhance_units_03(complex_doze_parts_list, debug=debug)
                    if debug: print(f"complex_doze_handler_02: complex_doze_list_enhanced: {complex_doze_list_enhanced}")
                    doze, doze_unit, pseudo_vol, pseudo_vol_unit = calc_total_doze( complex_doze_list_enhanced, 
                            doze, doze_unit, pseudo_vol, pseudo_vol_unit, debug=debug)
                # else: complex_doze_list, complex_doze_str, doze, doze_unit = None, None, None, None
                else:
                    if debug: print(f"complex_doze_handler_02: NOT complex_doze_str is not None and '+' in complex_doze_str: '{complex_doze_str}'")
            else:
                if debug: print(f"complex_doze_handler_02: m is None")
        else:
            if debug: print(f"complex_doze_handler_02: m_det is None")
    else:
        if debug: print(f"complex_doze_handler_02: complex_doze_ptn_str is None")
    # return complex_doze_list, complex_doze_str, doze, doze_unit 
    return complex_doze_list_enhanced, complex_doze_str, doze, doze_unit, pseudo_vol, pseudo_vol_unit

### Comlex_doze
def enhance_units(comlex_doze_list):
    # на взоде ['875', '35', '125 mg', '11', '22mkg/мл', '23мг|мл', '24 kg\мл']
    comlex_doze_list_enhanced = [] #comlex_doze_list
    ptn_digits = r"((\d+,\d+)|(\d+\.\d+)|([\d\s]+\d+)|(\d+))"
    ptn_mu = r"[^\d]*"
    last_mu = '' # measurement unit
    for item in comlex_doze_list:
        m_digits = re.search(ptn_digits, item)
        if m_digits is not None:
            digits = m_digits.group()
        else: digits = None
        m_mu = re.search(ptn_mu, re.sub(digits, '', item) if digits is not None else item)
        if m_mu is not None:
            mu = m_mu.group().replace('\\','/').replace('|','/')
            if len(mu)==0: mu = None
        else: mu = None
        comlex_doze_list_enhanced.append([digits, mu])
    # last_mu = '' # measurement unit
    last_mu = None # measurement unit
    comlex_doze_list_enhanced_01 = []
    for i, doze_tuple in enumerate(comlex_doze_list_enhanced[::-1]):
        if doze_tuple[1] is None or doze_tuple[1]=='':
            # comlex_doze_list_enhanced[::-1][i] = last_mu
            doze_tuple[1] = last_mu
            # print(f"last_mu: {last_mu}")
        else: last_mu = doze_tuple[1]
        comlex_doze_list_enhanced_01.append(doze_tuple)
    return comlex_doze_list_enhanced_01[::-1]

def standardize_unit(comlex_doze_list_enhanced):
    comlex_doze_list = []
    for item in comlex_doze_list_enhanced:
        if item[0] is not None:
            digits_standard = item[0].replace(',','.')
        if item[1] is not None:
            mu_split = item[1].split('/')
            mu_standard = '/'.join([units_total_dict.get(mu.strip().lower(),'') for mu in mu_split])
        else: mu_standard = None
        comlex_doze_list.append([digits_standard, mu_standard])
    return comlex_doze_list

def complex_doze_handler(handler_group, unparsed_str, doze_str, debug=False):
    complex_doze_list, complex_doze_str = None, None
    complex_doze_ptn_str = doze_units_groups[handler_group]['cmplx_ptn_str']
    if complex_doze_ptn_str is not None:
        # заменим скобки на пробелы
        unparsed_str = re.sub(r"[\(\)]", ' ', unparsed_str)
        m = re.search(complex_doze_ptn_str, unparsed_str, flags=re.I)
        if m is not None:
            complex_doze_str = m.group().strip()
            if complex_doze_str is not None  and doze_str is not None and complex_doze_str.strip() == doze_str.strip(): # Юперио табл. п/пл/об. 100 мг ( 51.4 мг+48.6 мг) 
                m1 = re.search(complex_doze_ptn_str, re.sub(re.escape(doze_str), '', unparsed_str), flags=re.I)
                if m1 is not None:
                    complex_doze_str = m1.group().strip()
            if complex_doze_str is not None and '+' in complex_doze_str:
                complex_doze_list = complex_doze_str.split('+')
                # не обрабатывает '20mg/ml/12.5mg/ml'
                # 125 mg (1 caps.)+80 mg (2 caps.) +180 mg (3 caps.) 
                            
                complex_doze_list_enhanced = enhance_units(complex_doze_list)
                complex_doze_list = standardize_unit(complex_doze_list_enhanced)
            else: complex_doze_list, complex_doze_str = None, None

    return complex_doze_list, complex_doze_str


### Doze, pseudo_vol, vol handlers
def doze_handler (handler_group2, unparsed_string, is_special_doze=False, special_doze_ptn_str=None, debug=False):
  
    doze_proc, doze, doze_unit, doze_str, pseudo_vol, pseudo_vol_unit = None, None, None, None, None, None
    doze_proc_str = None #doze_proc_pre
    # заменим скобки на пробелы
    unparsed_string = re.sub(r"[\(\)]", ' ', unparsed_string)
    if doze_vol_handler_types[handler_group2][4]: #is_proc_dozed
        # ptn_proc = r"(?:((\d+,\d+)|(\d+\.\d+)|([\d\s]+\d+)|(\d+))\s*%)"
        ptn_proc = r"(?:((\d+,\d+)|(\d+\.\d+)|(\d+))\s*%)"
        m_proc = re.search(ptn_proc, unparsed_string, flags=re.I)
        if m_proc is not None:
            doze_proc_str = m_proc.group()
            doze_proc = doze_proc_str.replace('%','').replace(',','.').strip()
    if debug: print(f"doze_handler: doze_proc_str: '{doze_proc_str}'" )
    if doze_vol_handler_types[handler_group2][1] or doze_vol_handler_types[handler_group2][2]: # is doze or iz peudo_vol
        if not is_special_doze:
            ptn_str = doze_units_groups[handler_group2].get('ptn_str')
        elif special_doze_ptn_str is not None:
            ptn_str = special_doze_ptn_str
        else: return doze_proc, doze_proc_str, doze, doze_unit, doze_str, pseudo_vol, pseudo_vol_unit

        if debug: print(f"doze_handler: handler_group: {handler_group2}")
        if doze_proc_str is not None: 
            unparsed_string = re.sub(doze_proc_str.strip(), '', unparsed_string)
        if debug: print(f"doze_handler: unparsed_string: '{unparsed_string}'")
        m = re.search(ptn_str, unparsed_string, flags=re.I)
        if m is None: 
            if debug: 
                print(f"doze_handler: re.search(ptn_str, unparsed_string, flags=re.I): {m}")
                # print(f"doze_handler: ptn_str: {ptn_str}")
        elif m is not None: 
            # if debug: print(m.group('digits'), m.group('unit'))
            # doze, doze_unit, doze_str = m.group('digits').strip(), m.group('unit').strip(), m.group()
            # pseudo_vol, pseudo_vol_unit = m.group('digits_pseudo'), m.group('unit_pseudo')
            # if pseudo_vol is not None: pseudo_vol = pseudo_vol.replace(r"/",r'')
            doze_str = m.group()
            doze_substrs = [(k,v) for k,v in m.groupdict().items() if v is not None]
            if debug: print(f"doze_handler: doze_substrs: ", doze_substrs)
            # [('doze_digits_000', '20'), ('doze_unit_000', 'мг'), ('digits_pseudo_000', '0.5'), ('unit_pseudo_000', 'мл')]
            if len (doze_substrs) > 0 : 
                if debug: print(f"doze_handler: if len (doze_substrs) > 0 :")
                doze_substrs_dict = {}
                doze_substrs_dict['doze_digits'] = [doze_substr[1] for doze_substr in doze_substrs if doze_substr[0].startswith('doze_digits')]
                doze_substrs_dict['doze_unit'] = [doze_substr[1] for doze_substr in doze_substrs if doze_substr[0].startswith('doze_unit')]
                doze_substrs_dict['digits_pseudo'] = [doze_substr[1] for doze_substr in doze_substrs if doze_substr[0].startswith('digits_pseudo')]
                doze_substrs_dict['unit_pseudo'] = [doze_substr[1] for doze_substr in doze_substrs if doze_substr[0].startswith('unit_pseudo')]
                if debug: 
                    print(f"doze_handler: doze_substrs_dict['doze_unit']: ", doze_substrs_dict['doze_unit'])
                    print(f"doze_handler: doze_substrs_dict['unit_pseudo']: ", doze_substrs_dict['unit_pseudo'])
                if len(doze_substrs_dict['doze_digits']) > 0:
                    doze = doze_substrs_dict['doze_digits'][0]
                    if doze is not None: 
                        doze = doze.replace(',','.').replace(' ','')
                        doze = re.sub('[^A-Za-z0-9\.]+', '',doze)
                        if len(doze) > 0 and doze[-1]=='+': doze=doze[:-1]
                    if debug and len(doze_substrs_dict['doze_digits']) > 1:
                        print('doze_handler: doze_digits', 'are strange', doze_substrs_dict['doze_digits'])
                if len(doze_substrs_dict['doze_unit']) > 0:
                    doze_unit = doze_substrs_dict['doze_unit'][0]
                    if debug: print(f"doze_handler: doze_unit before stand_dict: {doze_unit}")
                    doze_unit = units_total_dict.get(doze_unit.strip().lower())
                    if debug: print(f"doze_handler: doze_unit after stand_dict: {doze_unit}")
                    if debug and len(doze_substrs_dict['doze_unit']) > 1:
                        print('doze_handler: doze_unit', 'are strange', doze_substrs_dict['doze_unit'])
                if len(doze_substrs_dict['digits_pseudo']) > 0:
                    pseudo_vol = doze_substrs_dict['digits_pseudo'][0]
                    if pseudo_vol is not None: 
                        pseudo_vol = pseudo_vol.replace(',','.').replace(' ','')
                        pseudo_vol = re.sub('[^A-Za-z0-9\.]+', '', pseudo_vol)
                    if debug and len(doze_substrs_dict['digits_pseudo']) > 1:
                        print('doze_handler: digits_pseudo', 'are strange', doze_substrs_dict['digits_pseudo'])
                if len(doze_substrs_dict['unit_pseudo']) > 0:
                    pseudo_vol_unit = doze_substrs_dict['unit_pseudo'][0]
                    pseudo_vol_unit = units_total_dict.get(pseudo_vol_unit.strip().lower())
                    if debug and len(doze_substrs_dict['unit_pseudo']) > 1:
                        print('doze_handler: unit_pseudo', 'are strange', doze_substrs_dict['unit_pseudo'])
            
            
            
        #if not doze_vol_handler_types[handler_group][2]: pseudo_vol, pseudo_vol_unit = None, None
        if pseudo_vol_unit is not None and pseudo_vol_unit=='': pseudo_vol_unit = None
        #if pseudo_vol is None and doze_vol_handler_types[handler_group][2]: 
        # if pseudo_vol is None and pseudo_vol_unit is not None: 
        #     pseudo_vol = '1'
        if debug: print(f"doze_handler: final: doze_proc: {doze_proc}, doze_proc_str: {doze_proc_str}", 
                      f"doze: {doze}, doze_unit: {doze_unit}, doze_str: '{doze_str}', pseudo_vol: {pseudo_vol}, pseudo_vol_unit: {pseudo_vol_unit}")

    return doze_proc, doze_proc_str, doze, doze_unit, doze_str, pseudo_vol, pseudo_vol_unit
           

def pseudo_vol_handler (handler_group3):
    pseudo_vol, pseudo_vol_unit, pseudo_vol_str = None, None, None
    return pseudo_vol, pseudo_vol_unit, pseudo_vol_str

def vol_handler (handler_group4, ptn_str, mis_position, tn_ru_ext, tn_lat_ext, doze_str, debug=False):
    # global doze_vol_handler_types 
    vol, vol_unit, vol_str = None, None, None
    if debug: print(f"vol_handler: doze_str: '{doze_str}'")
    if debug: print(f"vol_handler: ptn_str: '{ptn_str}'")
    if doze_vol_handler_types[handler_group4][3] or handler_group4 in [6]: # is_vol или особый вариант для порошки лиофидизаты
        if doze_str is not None:
            try: 
                sw = re.sub(re.escape(doze_str.strip()), '', mis_position)
                # sw = re.sub(doze_str.strip(), '', mis_position)
            except Exception as err:
                print("vol_handler: ERROR re.sub(re.escape(doze_str)!", err)
                print(f"vol_handler: mis_position: '{mis_position}', doze_str: '{doze_str}'")
                sw = mis_position
        else: sw = mis_position
        if debug: print(F"vol_handler: sw after re.sub(re.escape(doze_str): '{sw}'")
        # Berotec N 100mkg/dosa 200 доз N1 аэрозоль
        try:
            if tn_ru_ext is not None: sw = re.sub(re.escape(tn_ru_ext), '', sw)
            if tn_lat_ext is not None: sw = re.sub(re.escape(tn_lat_ext), '', sw)
            if debug:
                print(f"vol_handler: sw: '{sw}', tn_ru_ext: '{tn_ru_ext}', tn_lat_ext: '{tn_lat_ext}'")
        except Exception as err:
            print("ERROR! : re.sub(tn_ru_ext, '', sw)", err)
            print(f"vol_handler: sw: '{sw}', tn_ru_ext: '{tn_ru_ext}', tn_lat_ext: '{tn_lat_ext}'")
        # заменим скобки на пробелы
        # sw = re.sub(r"[\(\)]", ' ', sw)
        # пока возможно не будем
        if debug: print(F"vol_handler: sw='{sw}'")
        #sw = re.sub(r"(N|№)\s*[\d\w]*\b", '', sw)
        sw = re.sub(r"(N|№)[\s\d+xXхХ]*\b|$", '', sw, flags=re.I)
        # чистим от N 2x5 до первой буквы
        #print(vol_units_groups[i].get('ptn_str'))
        m = re.search(ptn_str, sw, flags=re.I)
        if m is not None:
            if debug: print("vol_handler:",f"'{sw}',  \n-->vol: '{m.group('digits')}', '{m.group('unit')}'")
            # vol, vol_unit, vol_str = m.group('digits').replace(',','.').replace(' ','').strip(), m.group('unit'), m.group()
            # vol = re.sub('[^A-Za-z0-9\.]+', '', m.group('digits')) #m.group('digits').replace(',','.').replace(' ','') 
            vol = re.sub('[^A-Za-z0-9\.,]+', '', m.group('digits')) #m.group('digits').replace(',','.').replace(' ','') 
            if vol is not None:
                vol = vol.replace(',','.').strip()
                try: 
                    vpl = float(vol)
                except Exception as err:
                    print("vol_handler: ", err, f"float(vol): {vol}")
                    print(f"vol_handler: mis_position", mis_position)
            vol_unit, vol_str = m.group('unit').strip(), m.group()
            if vol_unit is not None: vol_unit = units_total_dict.get(vol_unit.strip().lower())
            if debug: print(f"vol_handler: vol: {vol}, vol_unit: {vol_unit}, vol_str: '{vol_str}'")
    return vol, vol_unit, vol_str


def is_one_number_in_string(mis_position, debug=False):
    rez = None
    if debug: print(f"is_one_number_in_string: на входе: mis_position: '{mis_position}'")
    mis_position_cut = re.sub(r"(?<=\s)(N|№)[\s\d+xXхХ]*\b|$", '', mis_position) # чистим от N10x1
    if debug: print(f"is_one_number_in_string: чистим от N10x1: mis_position_cut: '{mis_position_cut}'")
    mis_position_cut = re.sub(r"(?:\d\d\.\d\d\.\d\d\d\d)|(?:\d\d\.\d\d\d\d)", '', mis_position_cut) # читстим от  06.2022г.
    if debug: print(f"is_one_number_in_string: mis_position_cut: '{mis_position_cut}'")
    # lst = re.findall(r"\d+,\d+|\d+\.\d+|[\d\s]+\d+|\d+",  mis_position_cut)
    #lst = re.findall(r"(?:(\d+,\d+)|(\d+\.\d+)|([\d\s]+\d+)|(\d+))",  mis_position_cut)
    #lst = re.findall(r"(?<=\w(N|№))(?:\d+,\d+)|(?:\d+\.\d+)|(?:\d+)",  mis_position_cut)
    # lst = re.findall(r"(?:\d+[,\.]*\d*)", mis_position_cut)
    lst = re.findall(r"(?:\s\d+[,\.]*\d*\s|$)", mis_position_cut) # 02.12.2022
    # if len(lst)==1: return lst[0]
    if len(lst)==1: rez = lst[0]
    else: rez = None
    return rez 
    
def post_process_doze_vol(mis_position, handler_group1, tn_ru_ext, tn_lat_ext, doze_proc_str, doze, doze_unit, 
                          doze_str, pseudo_vol, pseudo_vol_unit, vol, vol_unit, vol_str, debug=False):
    ptn_digits = r'(?P<digits>(\d+,\d+|\d+\.\d+|\d+))'
    if debug: print(f"post_process_doze_vol: на входе: mis_position: '{mis_position}'")
    if debug: print(f"post_process_doze_vol: doze_proc_str: {doze_proc_str}, doze_str: {doze_str}")
    if doze_proc_str is not None:
        sw = re.sub(doze_proc_str.strip(), '', mis_position )
    else: sw = mis_position
    if debug: print(f"post_process_doze_vol: mis_position -> sw: '{sw}'")
    if doze_str is not None:
        # sw = re.sub(doze_str.strip(), '', sw)
        sw = re.sub(re.escape(doze_str.strip()), '', sw)
    # else: sw = sw
    if debug: print(f"post_process_doze_vol: sw -> sw: '{sw}'")
    one_number = is_one_number_in_string(sw, debug=debug) #mis_poistion
    if debug: print(f"post_process_doze_vol: handler_group: {handler_group1}, one_number: '{one_number}'")
    if debug: print(f"post_process_doze_vol: vol: {vol}, vol_unit: {vol_unit}")
    # if one_number is not None and doze_unit is None and pseudo_vol_unit is None and vol_unit is None:
    if one_number is not None:
        if handler_group1 in [0, 6, 8]: # если стоит одно число => это дозировка, ставим это число, в поле "ед. измер." - ставим "-"
            if doze_unit is None and pseudo_vol_unit is None and vol_unit is None:
                # handler_numder, is_is_dosed, is_pseudo_vol, is_vol
                # [0, True, False, False] # Таблетки...
                # [6, True, False, False] 
                # [8, False, False, False] # если есть одно число - ставим в дозировку
                #if doze is None:
                doze, doze_unit, doze_str, pseudo_vol, pseudo_vol_unit, vol, vol_unit, vol_str = \
                    re.sub('[^A-Za-z0-9\.,]+', '', one_number.replace(',','.')), None, None, None, None, None, None, None
            elif handler_group1 in [0] and doze_unit is not None and pseudo_vol_unit is not None:
                if doze_unit is not None: doze_unit = units_total_dict.get(doze_unit.strip().lower())
                # if debug: print(f"post_process_doze_vol: pseudo_vol_unit before: '{pseudo_vol_unit}'")
                if pseudo_vol_unit is not None: pseudo_vol_unit = units_total_dict.get(pseudo_vol_unit.strip().lower())
                # if debug: print(f"post_process_doze_vol: pseudo_vol_unit after: '{pseudo_vol_unit}'")
                if vol_unit is not None: vol_unit = units_total_dict.get(vol_unit.strip().lower())
                if doze_unit.lower() in ['мг', 'мкг'] and pseudo_vol_unit.lower() in ['доз(а)']:
                    # doze_unit = 'мг' 
                    pseudo_vol_unit = None
            elif handler_group1 in [6] and doze_unit is not None and pseudo_vol_unit is not None:
                if doze_unit is not None: doze_unit = units_total_dict.get(doze_unit.strip().lower())
                # if debug: print(f"post_process_doze_vol: pseudo_vol_unit before: '{pseudo_vol_unit}'")
                if pseudo_vol_unit is not None: pseudo_vol_unit = units_total_dict.get(pseudo_vol_unit.strip().lower())
                # if debug: print(f"post_process_doze_vol: pseudo_vol_unit after: '{pseudo_vol_unit}'")
                if vol_unit is not None: vol_unit = units_total_dict.get(vol_unit.strip().lower())
                if doze_unit.lower() in ['мг', 'мкг'] and pseudo_vol_unit.lower() in ['мл']:
                    # doze_unit = 'мг' 
                    pseudo_vol_unit = None
        elif handler_group1 in [1]: # если стоит одно число => это объем, ставим это число, в поле "ед. измер." - ставим "-"
            if doze_unit is None and pseudo_vol_unit is None and vol_unit is None:
                # [1, True, True, True]
                if debug: 
                    print(f"post_process_doze_vol: if doze_unit is None and pseudo_vol_unit is None and vol_unit is None:")
                doze, doze_unit, doze_str, pseudo_vol, pseudo_vol_unit, vol, vol_unit, vol_str = \
                  None, None, None, None, None, re.sub('[^A-Za-z0-9\.,]+', '', one_number.replace(',','.')), None, None
                if doze_unit is not None: doze_unit = units_total_dict.get(doze_unit.strip().lower())
                if pseudo_vol_unit is not None: pseudo_vol_unit = units_total_dict.get(pseudo_vol_unit.strip().lower())
                if vol_unit is not None: vol_unit = units_total_dict.get(vol_unit.strip().lower())
        elif handler_group1 in [4]: # если стоит одно число => это объем
            # сначала ищем "ед.измер. псевдо-объема" и число перед ним - ставим в соот-щие ячейки
            # потом ищем дозировку
            # потом ищем объем

            # [4, False, False, True]
            if doze_unit is None and pseudo_vol_unit is None and vol_unit is None:
                doze, doze_unit, doze_str, pseudo_vol, pseudo_vol_unit, vol, vol_unit, vol_str = \
                  None, None, None, None, None, re.sub('[^A-Za-z0-9\.,]+', '', one_number.replace(',','.')), None, None
                if doze_unit is not None: doze_unit = units_total_dict.get(doze_unit.strip().lower())
                if pseudo_vol_unit is not None: pseudo_vol_unit = units_total_dict.get(pseudo_vol_unit.strip().lower())
                if vol_unit is not None: vol_unit = units_total_dict.get(vol_unit.strip().lower())
        elif handler_group1 in [5,7]:
            if debug: 
                print(f"post_process_doze_vol: handler_group1 in [5,7]")
                print(f"doze, doze_unit, pseudo_vol, pseudo_vol_unit, vol, vol_unit\n", doze, doze_unit, pseudo_vol, pseudo_vol_unit, vol, vol_unit)
            
            if doze_unit is None and pseudo_vol_unit is None and vol_unit is None:
                # [5, True, True, True]
                # 1) если стоит одно число (без ед. измер дозировки и объема) - то это объем 
                doze, doze_unit, doze_str, pseudo_vol, pseudo_vol_unit, vol, vol_unit, vol_str = \
                  None, None, None, None, None, re.sub('[^A-Za-z0-9\.,]+', '', one_number.replace(',','.')), None, None
                if doze_unit is not None: doze_unit = units_total_dict.get(doze_unit.strip().lower())
                if pseudo_vol_unit is not None: pseudo_vol_unit = units_total_dict.get(pseudo_vol_unit.strip().lower())
                if vol_unit is not None: vol_unit = units_total_dict.get(vol_unit.strip().lower())

                #2) если есть дозировка + ед. измер дозировки, потом число - то это объем
                # надо проверить
                # если находит 2 "объема" или 2 "дозировки"???
                # elif handler_group1 in [8]: 
            elif handler_group1 in [5]  and doze_unit is not None and pseudo_vol_unit is not None:
                if debug: print(f"post_process_doze_vol: мл/мл -> мг/мл")
                if doze_unit.lower() in ['ml', 'мл'] and pseudo_vol_unit.lower() in ['ml', 'мл']:
                    doze_unit = 'мг'
                if doze_unit is not None: units_total_dict.get(doze_unit.strip().lower())
                if pseudo_vol_unit is not None: pseudo_vol_unit = units_total_dict.get(pseudo_vol_unit.strip().lower())
                if vol_unit is not None: vol_unit = units_total_dict.get(vol_unit.strip().lower())

    elif handler_group1 in [0]:
        if doze_unit is not None and pseudo_vol_unit is not None:
            # if debug: print(f"post_process_doze_vol: мг/доз(а) -> мг")
            # if vol_unit.lower() in ['ml', 'мл'] and pseudo_vol_unit.lower() in ['ml', 'мл']:
            #     vol_unit = 'мг'
            if doze_unit is not None: doze_unit = units_total_dict.get(doze_unit.strip().lower())
            if pseudo_vol_unit is not None: pseudo_vol_unit = units_total_dict.get(pseudo_vol_unit.strip().lower())
            if vol_unit is not None: vol_unit = units_total_dict.get(vol_unit.strip().lower())
            if doze_unit.lower() in ['мг', 'мкг'] and pseudo_vol_unit.lower() in ['доз(а)']:
                # doze_unit = 'мг' 
                pseudo_vol_unit = None
            # elif doze_unit.lower() in ['мкг'] and pseudo_vol_unit.lower() in ['доз(а)]:
            #     doze_unit = 'мкг'
            #     pseudo_vol_unit = None
            
    elif handler_group1 in [5]:
        if doze_unit is not None and pseudo_vol_unit is not None:
            if debug: print(f"post_process_doze_vol: handler_group in [5]")
            # if vol_unit.lower() in ['ml', 'мл'] and pseudo_vol_unit.lower() in ['ml', 'мл']:
            #     vol_unit = 'мг'
            if doze_unit.lower() in ['ml', 'мл'] and pseudo_vol_unit.lower() in ['ml', 'мл']:
                doze_unit = 'мг'
            if debug: print(f"post_process_doze_vol: before pre final:",
                f"doze: {doze}, doze_unit: {doze_unit}, pseudo_vol:{pseudo_vol}, pseudo_vol_unit:{pseudo_vol_unit}, vol: {vol}, vol_unit: {vol_unit}")
            if doze_unit is not None: doze_unit = units_total_dict.get(doze_unit.strip().lower())
            if pseudo_vol_unit is not None: pseudo_vol_unit = units_total_dict.get(pseudo_vol_unit.strip().lower())
            if vol_unit is not None: vol_unit = units_total_dict.get(vol_unit.strip().lower())
            if debug: print(f"post_process_doze_vol: after pre final:",
                f"doze: {doze}, doze_unit: {doze_unit}, pseudo_vol:{pseudo_vol}, pseudo_vol_unit:{pseudo_vol_unit}, vol: {vol}, vol_unit: {vol_unit}")
    elif handler_group1 in [7] and doze is None:
        # [7, True, True, True]
        if debug: print(f"post_process_doze_vol: if handler_group1 in [7] and doze is None")
        if debug: print(f"post_process_doze_vol: vol: {vol}, vol_unit: '{vol_unit}', vol_str: '{vol_str}'")
        if vol is not None and vol_unit is not None:
            if debug: print(f"post_process_doze_vol: if vol is not None and vol_unit is not None")
            # 3) если стоит объем и ЕИ объема, то просто число - это дозировка
            # one_number = is_one_number_in_string(re.sub(vol_str, '', mis_position), debug=False)
            # просто так не работает бывает попадается два объема
            # пароверяем есть л второй объем (пока з алкадываемся на два максимум
            ptn_str = vol_units_groups[handler_group1].get('ptn_str')
            vol2, vol_unit2, vol_str2 = \
                vol_handler (handler_group1, ptn_str, re.sub(vol_str.strip(), '', sw), '', '', doze_str, debug=debug)
                # vol_handler (handler_group1, ptn_str, re.sub(vol_str.strip(), '', sw), tn_ru_ext, tn_lat_ext, doze_str, debug=debug)
            if debug: print(f"post_process_doze_vol: vol2: {vol2}, vol_unit2: '{vol_unit2}', vol_str2: '{vol_str2}'")
            fl_vol2 = False
            if vol2 is not None and vol_unit2 is not None:
                # выбираем предпочтение доаз vs мл
                vol_unit2_pre = units_total_dict.get(vol_unit2.strip().lower())
                if vol_unit2_pre is None: 
                    print(f"post_process_doze_vol: units_total_dict.get(vol_unit2) is None: vol_unit2: '{vol_unit2}'")
                    vol_unit2 = '' #vol_unit2_pre  # страховка
                    vol_str2 = ''
                else:
                    vol_unit2 = vol_unit2_pre
                    
                if vol_unit2 in ['доз(а)'] and vol_unit in ['мл']:
                    vol = vol2
                    vol_unit = vol_unit2 
                    fl_vol2 = True
                    # vol_str = vol_str2 
                # обратно по умолчанию остается
            if vol_str2 is None: vol_str2 = ''
            if vol_str is not None and vol_str2 is not None:
                one_number = is_one_number_in_string(re.sub(vol_str2.strip(), '', re.sub(vol_str.strip(), '', sw)), debug=debug)
            elif vol_str is not None:
                one_number = is_one_number_in_string(re.sub(vol_str.strip(), '', sw), debug=debug)
                
            if one_number is not None:
                #doze = one_number.replace(',','.').strip()
                doze = re.sub('[^A-Za-z0-9\.,]+', '', one_number.replace(',','.'))
            if fl_vol2: 
                vol_str = vol_str2
                fl_vol2 = False
    elif handler_group1 in [6]:
        if debug: print(f"post_process_doze_vol: elif handler_group1 in [6]:")
        if doze_unit is not None and pseudo_vol_unit is not None and \
            doze_unit in ('мг', 'мкг', 'mg', 'mkg', 'МЕ', 'ME') and pseudo_vol_unit in ('доза', 'доз', 'doza', 'doz', 'dosa', 'dos', 'd.', 'd'):
            if debug: print(f"post_process_doze_vol: doze_unit in ('мг', 'мкг', 'mg', 'mkg', 'МЕ', 'ME')")
            ptn_digits = r'(?P<digits>(\d+,\d+)|(\d+\.\d+)|(\d+))'
            ptn_str = r"(?:" + ptn_digits + r")\s*" +\
                r"(?P<unit>" +  "|".join(['(?:' + p + r")" for p in ('доза', 'доз', 'doza', 'doz', 'dosa', 'dos', 'd.', 'd')]) + r")\.*,*(\s*|$)" 
            vol, vol_unit, vol_str = vol_handler (handler_group1, ptn_str, mis_position, tn_ru_ext, tn_lat_ext,
                                                  doze_str, debug=debug)
        elif doze_unit is not None and pseudo_vol_unit is not None:
            if doze_unit is not None: doze_unit = units_total_dict.get(doze_unit.strip().lower())
            # if debug: print(f"post_process_doze_vol: pseudo_vol_unit before: '{pseudo_vol_unit}'")
            if pseudo_vol_unit is not None: pseudo_vol_unit = units_total_dict.get(pseudo_vol_unit.strip().lower())
            # if debug: print(f"post_process_doze_vol: pseudo_vol_unit after: '{pseudo_vol_unit}'")
            if vol_unit is not None: vol_unit = units_total_dict.get(vol_unit.strip().lower())
            if doze_unit.lower() in ['мг', 'мкг'] and pseudo_vol_unit.lower() in ['мл']:
                # doze_unit = 'мг' 
                pseudo_vol_unit = None
        elif doze is None and doze_unit is None:
            local_units = [('мг', 'мкг', 'mg', 'mkg', 'МЕ', 'ME', 'мл', 'ml'), ('доза', 'доз', 'doza', 'doz', 'dosa', 'dos', 'd.', 'd')] 
            ptns_lst_pre = list(itertools.product(*local_units))
            ptns_lst = [i[0]+'/'+ i[1]  for i in ptns_lst_pre]
            special_doze_ptn_str = make_doze_ptn_str(ptns_lst)
            # print(special_doze_ptn_str)
            doze_proc, doze_proc_str, doze, doze_unit, doze_str, pseudo_vol, pseudo_vol_unit = \
                   doze_handler (handler_group1, sw, is_special_doze=True, special_doze_ptn_str=special_doze_ptn_str, debug=debug)
            special_vol_ptn_str = make_vol_ptn_str(['доза', 'доз', 'doza', 'doz', 'dosa', 'dos', 'd.', 'd'])
            vol, vol_unit, vol_str = \
                vol_handler (handler_group1, special_vol_ptn_str, mis_position, tn_ru_ext, tn_lat_ext, doze_str, debug=debug)
    
    elif handler_group1 in [8] :
        if vol is None and doze is not None and doze_unit is not None:
            # 2) если есть дозировка + ЕИ дозировки, потом число - то это объем, 
            one_number = is_one_number_in_string(re.sub(doze_str, '', sw), debug=False)
            if one_number is not None:
                # vol = one_number.replace(',','.').strip()
                vol = re.sub('[^A-Za-z0-9\.,]+', '', one_number.replace(',','.'))
            
        if doze is None and vol is not None and vol_unit is not None:
            # 3) если стоит объем и ЕИ объема, то просто число - это дозировка
            one_number = is_one_number_in_string(re.sub(vol_str, '', sw), debug=False)
            if one_number is not None:
                # doze = one_number.replace(',','.').strip()
                doze = re.sub('[^A-Za-z0-9\.,]+', '', one_number.replace(',','.'))

    return doze, doze_unit, doze_str, pseudo_vol, pseudo_vol_unit, vol, vol_unit, vol_str

def extract_doze_vol_02(mis_position, tn_ru_ext, tn_lat_ext, pharm_form_unify, pharm_form, debug=False):
    # global doze_units_groups, vol_units_groups, doze_vol_handler_types, doze_vol_pharm_form_handlers
    handler_group, doze_proc, doze, doze_unit, doze_str, pseudo_vol, pseudo_vol_unit, vol, vol_unit, vol_str = \
    None, None, None, None, None, None, None, None, None, None
    doze_proc_str = None
    complex_doze_list, complex_doze_str = None, None
    if debug: print(f"extract_doze_vol_02: на входе: mis_position: '{mis_position}'")
    if pharm_form_unify is None: pharm_form_unify = 'ph_f_undefined'
    if doze_vol_pharm_form_handlers.get(pharm_form_unify) is not None:
        handler_group, is_dosed, is_pseudo_vol, is_vol, is_proc_dozed = doze_vol_pharm_form_handlers[pharm_form_unify]
        if debug: print("extract_doze_vol_02:", pharm_form_unify, "-->", handler_group, is_dosed, is_pseudo_vol, is_vol)
        
        if is_dosed: 
            doze_proc, doze_proc_str, doze, doze_unit, doze_str, pseudo_vol, pseudo_vol_unit = \
                doze_handler (handler_group, mis_position, debug=debug)
                
            if debug: 
                print(f"extract_doze_vol_02: afte doze_handler: doze_proc: {doze_proc}, doze_proc_str: '{doze_proc_str}'", 
                    f"doze: {doze}, doze_unit: '{doze_unit}', doze_str: '{doze_str}', pseudo_vol: {pseudo_vol}, pseudo_vol_unit: {pseudo_vol_unit}")
                    # doze_proc, doze_proc_str, doze, doze_unit, doze_str, pseudo_vol, pseudo_vol_unit)
        #if is_pseudo_vol: pseudo_vol, pseudo_vol_unit, pseudo_vol_str = pseudo_vol_handler (handler_group)
        if is_vol: 
            ptn_str = vol_units_groups[handler_group].get('ptn_str')
            vol, vol_unit, vol_str = \
                vol_handler (handler_group, ptn_str, mis_position, tn_ru_ext, tn_lat_ext, doze_str, debug=debug)
        
        doze, doze_unit, doze_str, pseudo_vol, pseudo_vol_unit, vol, vol_unit, vol_str=\
        post_process_doze_vol(mis_position, handler_group, tn_ru_ext, tn_lat_ext, doze_proc_str, doze, doze_unit, 
                              doze_str, pseudo_vol, pseudo_vol_unit, vol, vol_unit, vol_str, debug=debug)
        
        # if is_dosed:
        if is_dosed and '+' in mis_position:
            # complex_doze_list, complex_doze_str = complex_doze_handler(handler_group, mis_position, doze_str, debug=debug)
            complex_doze_list, complex_doze_str, doze, doze_unit, pseudo_vol, pseudo_vol_unit =\
                complex_doze_handler_02(handler_group, mis_position, doze_str, doze, doze_unit, pseudo_vol, pseudo_vol_unit, debug=debug)
        else: complex_doze_list, complex_doze_str = None, None

    else: pass #return doze, doze_unit, doze_str, pseudo_vol, pseudo_vol_unit, vol, vol_unit, vol_str
    # if debug: print(f"Extract_doze_vol: doze_group: {handler_group}, doze: {doze}, doze_unit: {doze_unit}, pseudo_vol: {pseudo_vol}, pseudo_vol_unit:{pseudo_vol_unit}, vol: {vol}, vol_unit: {vol_unit}")
   
    return handler_group, doze_proc, doze, doze_unit, doze_str, pseudo_vol, pseudo_vol_unit, complex_doze_list, complex_doze_str, vol, vol_unit, vol_str


def extract_doze_vol_02_00(mis_position, tn_ru_ext, tn_lat_ext, pharm_form_unify, pharm_form, debug=False):
    # global doze_units_groups, vol_units_groups, doze_vol_handler_types, doze_vol_pharm_form_handlers
    handler_group, doze_proc, doze, doze_unit, doze_str, pseudo_vol, pseudo_vol_unit, vol, vol_unit, vol_str = \
    None, None, None, None, None, None, None, None, None, None
    doze_proc_str = None
    complex_doze_list, complex_doze_str = None, None
    if debug: print(f"extract_doze_vol_02: на входе: mis_position: '{mis_position}'")
    if pharm_form_unify is None: pharm_form_unify = 'ph_f_undefined'
    if doze_vol_pharm_form_handlers.get(pharm_form_unify) is not None:
        handler_group, is_dosed, is_pseudo_vol, is_vol, is_proc_dozed = doze_vol_pharm_form_handlers[pharm_form_unify]
        if debug: print("extract_doze_vol_02:", pharm_form_unify, "-->", handler_group, is_dosed, is_pseudo_vol, is_vol)
        
        if is_dosed: 
            doze_proc, doze_proc_str, doze, doze_unit, doze_str, pseudo_vol, pseudo_vol_unit = \
                doze_handler (handler_group, mis_position, debug=debug)
                
            if debug: 
                print(f"extract_doze_vol_02: afte doze_handler: doze_proc: {doze_proc}, doze_proc_str: '{doze_proc_str}'", 
                    f"doze: {doze}, doze_unit: '{doze_unit}', doze_str: '{doze_str}', pseudo_vol: {pseudo_vol}, pseudo_vol_unit: {pseudo_vol_unit}")
                    # doze_proc, doze_proc_str, doze, doze_unit, doze_str, pseudo_vol, pseudo_vol_unit)
        #if is_pseudo_vol: pseudo_vol, pseudo_vol_unit, pseudo_vol_str = pseudo_vol_handler (handler_group)
        if is_vol: 
            ptn_str = vol_units_groups[handler_group].get('ptn_str')
            vol, vol_unit, vol_str = \
                vol_handler (handler_group, ptn_str, mis_position, tn_ru_ext, tn_lat_ext, doze_str, debug=debug)
        
        doze, doze_unit, doze_str, pseudo_vol, pseudo_vol_unit, vol, vol_unit, vol_str=\
        post_process_doze_vol(mis_position, handler_group, tn_ru_ext, tn_lat_ext, doze_proc_str, doze, doze_unit, 
                              doze_str, pseudo_vol, pseudo_vol_unit, vol, vol_unit, vol_str, debug=debug)
        
        if is_dosed:
            complex_doze_list, complex_doze_str = complex_doze_handler(handler_group, mis_position, doze_str, debug=debug)
        else: complex_doze_list, complex_doze_str = None, None

    else: pass #return doze, doze_unit, doze_str, pseudo_vol, pseudo_vol_unit, vol, vol_unit, vol_str
    # if debug: print(f"Extract_doze_vol: doze_group: {handler_group}, doze: {doze}, doze_unit: {doze_unit}, pseudo_vol: {pseudo_vol}, pseudo_vol_unit:{pseudo_vol_unit}, vol: {vol}, vol_unit: {vol_unit}")
   
    return handler_group, doze_proc, doze, doze_unit, doze_str, pseudo_vol, pseudo_vol_unit, complex_doze_list, complex_doze_str, vol, vol_unit, vol_str


def empty_f(): # v 22.11.2022 ### Comlex_doze
    pass
    # v 22.11.2022
    ### Comlex_doze
    # def enhance_units(comlex_doze_list):
    #     # на взоде ['875', '35', '125 mg', '11', '22mkg/мл', '23мг|мл', '24 kg\мл']
    #     comlex_doze_list_enhanced = [] #comlex_doze_list
    #     ptn_digits = r"((\d+,\d+)|(\d+\.\d+)|([\d\s]+\d+)|(\d+))"
    #     ptn_mu = r"[^\d]*"
    #     last_mu = '' # measurement unit
    #     for item in comlex_doze_list:
    #         m_digits = re.search(ptn_digits, item)
    #         if m_digits is not None:
    #             digits = m_digits.group()
    #         else: digits = None
    #         m_mu = re.search(ptn_mu, re.sub(digits, '', item) if digits is not None else item)
    #         if m_mu is not None:
    #             mu = m_mu.group().replace('\\','/').replace('|','/')
    #             if len(mu)==0: mu = None
    #         else: mu = None
    #         comlex_doze_list_enhanced.append([digits, mu])
    #     # last_mu = '' # measurement unit
    #     last_mu = None # measurement unit
    #     comlex_doze_list_enhanced_01 = []
    #     for i, doze_tuple in enumerate(comlex_doze_list_enhanced[::-1]):
    #         if doze_tuple[1] is None or doze_tuple[1]=='':
    #             # comlex_doze_list_enhanced[::-1][i] = last_mu
    #             doze_tuple[1] = last_mu
    #             # print(f"last_mu: {last_mu}")
    #         else: last_mu = doze_tuple[1]
    #         comlex_doze_list_enhanced_01.append(doze_tuple)
    #     return comlex_doze_list_enhanced_01[::-1]

    # def standardize_unit(comlex_doze_list_enhanced):
    #     comlex_doze_list = []
    #     for item in comlex_doze_list_enhanced:
    #         if item[0] is not None:
    #             digits_standard = item[0].replace(',','.')
    #         if item[1] is not None:
    #             mu_split = item[1].split('/')
    #             mu_standard = '/'.join([units_total_dict.get(mu.strip().lower(),'') for mu in mu_split])
    #         else: mu_standard = None
    #         comlex_doze_list.append([digits_standard, mu_standard])
    #     return comlex_doze_list

    # def complex_doze_handler(handler_group, unparsed_str, doze_str, debug=False):
    #     complex_doze_list, complex_doze_str = None, None
    #     complex_doze_ptn_str = doze_units_groups[handler_group]['cmplx_ptn_str']
    #     if complex_doze_ptn_str is not None:
    #         # заменим скобки на пробелы
    #         unparsed_str = re.sub(r"[\(\)]", ' ', unparsed_str)
    #         m = re.search(complex_doze_ptn_str, unparsed_str, flags=re.I)
    #         if m is not None:
    #             complex_doze_str = m.group().strip()
    #             if complex_doze_str is not None  and doze_str is not None and complex_doze_str.strip() == doze_str.strip(): # Юперио табл. п/пл/об. 100 мг ( 51.4 мг+48.6 мг) 
    #                 m1 = re.search(complex_doze_ptn_str, re.sub(re.escape(doze_str), '', unparsed_str), flags=re.I)
    #                 if m1 is not None:
    #                     complex_doze_str = m1.group().strip()
    #             if complex_doze_str is not None and '+' in complex_doze_str:
    #                 complex_doze_list = complex_doze_str.split('+')
    #                 # не обрабатывает '20mg/ml/12.5mg/ml'
    #                 # 125 mg (1 caps.)+80 mg (2 caps.) +180 mg (3 caps.) 
                                
    #                 complex_doze_list_enhanced = enhance_units(complex_doze_list)
    #                 complex_doze_list = standardize_unit(complex_doze_list_enhanced)
    #             else: complex_doze_list, complex_doze_str = None, None

    #     return complex_doze_list, complex_doze_str

    # ### Doze, pseudo_vol, vol handlers
    # def doze_handler (handler_group2, unparsed_string, is_special_doze=False, special_doze_ptn_str=None, debug=False):
    
    #     doze_proc, doze, doze_unit, doze_str, pseudo_vol, pseudo_vol_unit = None, None, None, None, None, None
    #     doze_proc_str = None #doze_proc_pre
    #     # заменим скобки на пробелы
    #     unparsed_string = re.sub(r"[\(\)]", ' ', unparsed_string)
    #     if doze_vol_handler_types[handler_group2][4]: #is_proc_dozed
    #         # ptn_proc = r"(?:((\d+,\d+)|(\d+\.\d+)|([\d\s]+\d+)|(\d+))\s*%)"
    #         ptn_proc = r"(?:((\d+,\d+)|(\d+\.\d+)|(\d+))\s*%)"
    #         m_proc = re.search(ptn_proc, unparsed_string, flags=re.I)
    #         if m_proc is not None:
    #             doze_proc_str = m_proc.group()
    #             doze_proc = doze_proc_str.replace('%','').replace(',','.').strip()
    #     if debug: print(f"doze_handler: doze_proc_str: '{doze_proc_str}'" )
    #     if doze_vol_handler_types[handler_group2][1] or doze_vol_handler_types[handler_group2][2]: # is doze or iz peudo_vol
    #         if not is_special_doze:
    #             ptn_str = doze_units_groups[handler_group2].get('ptn_str')
    #         elif special_doze_ptn_str is not None:
    #             ptn_str = special_doze_ptn_str
    #         else: return doze_proc, doze_proc_str, doze, doze_unit, doze_str, pseudo_vol, pseudo_vol_unit

    #         if debug: print(f"doze_handler: handler_group: {handler_group2}")
    #         if doze_proc_str is not None: 
    #             unparsed_string = re.sub(doze_proc_str, '', unparsed_string)
    #         if debug: print(f"doze_handler: unparsed_string: '{unparsed_string}'")
    #         m = re.search(ptn_str, unparsed_string, flags=re.I)
    #         if m is None: 
    #             if debug: 
    #                 print(f"doze_handler: re.search(ptn_str, unparsed_string, flags=re.I): {m}")
    #                 # print(f"doze_handler: ptn_str: {ptn_str}")
    #         elif m is not None: 
    #             # if debug: print(m.group('digits'), m.group('unit'))
    #             # doze, doze_unit, doze_str = m.group('digits').strip(), m.group('unit').strip(), m.group()
    #             # pseudo_vol, pseudo_vol_unit = m.group('digits_pseudo'), m.group('unit_pseudo')
    #             # if pseudo_vol is not None: pseudo_vol = pseudo_vol.replace(r"/",r'')
    #             doze_str = m.group()
    #             doze_substrs = [(k,v) for k,v in m.groupdict().items() if v is not None]
    #             if debug: print(f"doze_handler: doze_substrs: ", doze_substrs)
    #             # [('doze_digits_000', '20'), ('doze_unit_000', 'мг'), ('digits_pseudo_000', '0.5'), ('unit_pseudo_000', 'мл')]
    #             if len (doze_substrs) > 0 : 
    #                 if debug: print(f"doze_handler: if len (doze_substrs) > 0 :")
    #                 doze_substrs_dict = {}
    #                 doze_substrs_dict['doze_digits'] = [doze_substr[1] for doze_substr in doze_substrs if doze_substr[0].startswith('doze_digits')]
    #                 doze_substrs_dict['doze_unit'] = [doze_substr[1] for doze_substr in doze_substrs if doze_substr[0].startswith('doze_unit')]
    #                 doze_substrs_dict['digits_pseudo'] = [doze_substr[1] for doze_substr in doze_substrs if doze_substr[0].startswith('digits_pseudo')]
    #                 doze_substrs_dict['unit_pseudo'] = [doze_substr[1] for doze_substr in doze_substrs if doze_substr[0].startswith('unit_pseudo')]
    #                 if debug: 
    #                     print(f"doze_handler: doze_substrs_dict['doze_unit']: ", doze_substrs_dict['doze_unit'])
    #                     print(f"doze_handler: doze_substrs_dict['unit_pseudo']: ", doze_substrs_dict['unit_pseudo'])
    #                 if len(doze_substrs_dict['doze_digits']) > 0:
    #                     doze = doze_substrs_dict['doze_digits'][0]
    #                     if doze is not None: 
    #                         doze = doze.replace(',','.').replace(' ','')
    #                         doze = re.sub('[^A-Za-z0-9\.]+', '',doze)
    #                         if len(doze) > 0 and doze[-1]=='+': doze=doze[:-1]
    #                     if debug and len(doze_substrs_dict['doze_digits']) > 1:
    #                         print('doze_handler: doze_digits', 'are strange', doze_substrs_dict['doze_digits'])
    #                 if len(doze_substrs_dict['doze_unit']) > 0:
    #                     doze_unit = doze_substrs_dict['doze_unit'][0]
    #                     if debug: print(f"doze_handler: doze_unit before stand_dict: {doze_unit}")
    #                     doze_unit = units_total_dict.get(doze_unit.strip().lower())
    #                     if debug: print(f"doze_handler: doze_unit after stand_dict: {doze_unit}")
    #                     if debug and len(doze_substrs_dict['doze_unit']) > 1:
    #                         print('doze_handler: doze_unit', 'are strange', doze_substrs_dict['doze_unit'])
    #                 if len(doze_substrs_dict['digits_pseudo']) > 0:
    #                     pseudo_vol = doze_substrs_dict['digits_pseudo'][0]
    #                     if pseudo_vol is not None: 
    #                         pseudo_vol = pseudo_vol.replace(',','.').replace(' ','')
    #                         pseudo_vol = re.sub('[^A-Za-z0-9\.]+', '', pseudo_vol)
    #                     if debug and len(doze_substrs_dict['digits_pseudo']) > 1:
    #                         print('doze_handler: digits_pseudo', 'are strange', doze_substrs_dict['digits_pseudo'])
    #                 if len(doze_substrs_dict['unit_pseudo']) > 0:
    #                     pseudo_vol_unit = doze_substrs_dict['unit_pseudo'][0]
    #                     pseudo_vol_unit = units_total_dict.get(pseudo_vol_unit.strip().lower())
    #                     if debug and len(doze_substrs_dict['unit_pseudo']) > 1:
    #                         print('doze_handler: unit_pseudo', 'are strange', doze_substrs_dict['unit_pseudo'])
                
                
                
    #         #if not doze_vol_handler_types[handler_group][2]: pseudo_vol, pseudo_vol_unit = None, None
    #         if pseudo_vol_unit is not None and pseudo_vol_unit=='': pseudo_vol_unit = None
    #         #if pseudo_vol is None and doze_vol_handler_types[handler_group][2]: 
    #         # if pseudo_vol is None and pseudo_vol_unit is not None: 
    #         #     pseudo_vol = '1'
    #         if debug: print(f"doze_handler: final: doze_proc: {doze_proc}, doze_proc_str: {doze_proc_str}", 
    #                       f"doze: {doze}, doze_unit: {doze_unit}, doze_str: '{doze_str}', pseudo_vol: {pseudo_vol}, pseudo_vol_unit: {pseudo_vol_unit}")

    #     return doze_proc, doze_proc_str, doze, doze_unit, doze_str, pseudo_vol, pseudo_vol_unit
            

    # def pseudo_vol_handler (handler_group3):
    #     pseudo_vol, pseudo_vol_unit, pseudo_vol_str = None, None, None
    #     return pseudo_vol, pseudo_vol_unit, pseudo_vol_str

    # def vol_handler (handler_group4, ptn_str, mis_position, tn_ru_ext, tn_lat_ext, doze_str, debug=False):
    #     # global doze_vol_handler_types 
    #     vol, vol_unit, vol_str = None, None, None
    #     if debug: print(f"vol_handler: doze_str: '{doze_str}'")
    #     if debug: print(f"vol_handler: ptn_str: '{ptn_str}'")
    #     if doze_vol_handler_types[handler_group4][3] or handler_group4 in [6]: # is_vol или особый вариант для порошки лиофидизаты
    #         if doze_str is not None:
    #             try: 
    #                 sw = re.sub(re.escape(doze_str), '', mis_position)
    #             except Exception as err:
    #                 print("ERROR!", err)
    #                 print(f"vol_handler: mis_position: '{mis_position}', doze_str: '{doze_str}'")
    #                 sw = mis_position
    #         else: sw = mis_position
    #         # Berotec N 100mkg/dosa 200 доз N1 аэрозоль
    #         try:
    #             if tn_ru_ext is not None: sw = re.sub(re.escape(tn_ru_ext), '', sw)
    #             if tn_lat_ext is not None: sw = re.sub(re.escape(tn_lat_ext), '', sw)
    #         except Exception as err:
    #             print("ERROR! : re.sub(tn_ru_ext, '', sw)", err)
    #             print(f"vol_handler: sw: '{sw}', tn_ru_ext: '{tn_ru_ext}', tn_lat_ext: '{tn_lat_ext}'")
    #         # заменим скобки на пробелы
    #         # sw = re.sub(r"[\(\)]", ' ', sw)
    #         # пока возможно не будем
    #         if debug: print(F"vol_handler: sw='{sw}'")
    #         #sw = re.sub(r"(N|№)\s*[\d\w]*\b", '', sw)
    #         sw = re.sub(r"(N|№)[\s\d+xXхХ]*\b|$", '', sw)
    #         #print(vol_units_groups[i].get('ptn_str'))
    #         m = re.search(ptn_str, sw, flags=re.I)
    #         if m is not None:
    #             if debug: print("vol_handler:",f"'{sw}',  -->vol: '{m.group('digits')}', '{m.group('unit')}'")
    #             # vol, vol_unit, vol_str = m.group('digits').replace(',','.').replace(' ','').strip(), m.group('unit'), m.group()
    #             vol = re.sub('[^A-Za-z0-9\.]+', '', m.group('digits')) #m.group('digits').replace(',','.').replace(' ','') 
    #             vol_unit, vol_str = m.group('unit').strip(), m.group()
    #             if vol_unit is not None: vol_unit = units_total_dict.get(vol_unit.strip().lower())
    #             if debug: print(f"vol_handler: {vol}: {vol}, vol_unit: {vol_unit}, vol_str: '{vol_str}'")
    #     return vol, vol_unit, vol_str

    # def is_one_number_in_string(mis_position, debug=False):
    #     rez = None
    #     if debug: print(f"is_one_number_in_string: на входе: mis_position: '{mis_position}'")
    #     mis_position_cut = re.sub(r"(?<=\s)(N|№)[\s\d+xXхХ]*\b|$", '', mis_position) # чистим от N10x1
    #     if debug: print(f"is_one_number_in_string: чистим от N10x1: mis_position_cut: '{mis_position_cut}'")
    #     mis_position_cut = re.sub(r"(?:\d\d\.\d\d\.\d\d\d\d)|(?:\d\d\.\d\d\d\d)", '', mis_position_cut) # читстим от  06.2022г.
    #     if debug: print(f"is_one_number_in_string: mis_position_cut: '{mis_position_cut}'")
    #     # lst = re.findall(r"\d+,\d+|\d+\.\d+|[\d\s]+\d+|\d+",  mis_position_cut)
    #     #lst = re.findall(r"(?:(\d+,\d+)|(\d+\.\d+)|([\d\s]+\d+)|(\d+))",  mis_position_cut)
    #     #lst = re.findall(r"(?<=\w(N|№))(?:\d+,\d+)|(?:\d+\.\d+)|(?:\d+)",  mis_position_cut)
    #     lst = re.findall(r"(?:\d+[,\.]*\d*)", mis_position_cut)
    #     # if len(lst)==1: return lst[0]
    #     if len(lst)==1: rez = lst[0]
    #     else: rez = None
    #     return rez 
        
    # def post_process_doze_vol(mis_position, handler_group1, tn_ru_ext, tn_lat_ext, doze_proc_str, doze, doze_unit, 
    #                           doze_str, pseudo_vol, pseudo_vol_unit, vol, vol_unit, vol_str, debug=False):
    #     ptn_digits = r'(?P<digits>(\d+,\d+|\d+\.\d+|\d+))'
    #     if debug: print(f"post_process_doze_vol: на входе: mis_position: '{mis_position}'")
    #     if debug: print(f"post_process_doze_vol: doze_proc_str: {doze_proc_str}, doze_str: {doze_str}")
    #     if doze_proc_str is not None:
    #         sw = re.sub(doze_proc_str.strip(), '', mis_position )
    #     else: sw = mis_position
    #     if debug: print(f"post_process_doze_vol: mis_position -> sw: '{sw}'")
    #     if doze_str is not None:
    #         # sw = re.sub(doze_str.strip(), '', sw) # 14794-14795 bad escape \m at position 5
    #         # sw = re.sub(re.escape(doze_str.strip(), '', sw)
    #         sw = sw.replace(doze_str.strip(),'')
    #     # else: sw = sw
    #     if debug: print(f"post_process_doze_vol: sw -> sw: '{sw}'")
    #     one_number = is_one_number_in_string(sw, debug=debug) #mis_poistion
    #     if debug: print(f"post_process_doze_vol: handler_group: {handler_group1}, one_number: '{one_number}'")
    #     if debug: print(f"post_process_doze_vol: vol: {vol}, vol_unit: {vol_unit}")
    #     # if one_number is not None and doze_unit is None and pseudo_vol_unit is None and vol_unit is None:
    #     if one_number is not None:
    #         if handler_group1 in [0, 6, 8]: # если стоит одно число => это дозировка, ставим это число, в поле "ед. измер." - ставим "-"
    #             if doze_unit is None and pseudo_vol_unit is None and vol_unit is None:
    #                 # handler_numder, is_is_dosed, is_pseudo_vol, is_vol
    #                 # [0, True, False, False] # Таблетки...
    #                 # [6, True, False, False] 
    #                 # [8, False, False, False] # если есть одно число - ставим в дозировку
    #                 #if doze is None:
    #                 doze, doze_unit, doze_str, pseudo_vol, pseudo_vol_unit, vol, vol_unit, vol_str = \
    #                     re.sub('[^A-Za-z0-9\.]+', '', one_number.replace(',','.')), None, None, None, None, None, None, None
    #             elif handler_group1 in [0] and doze_unit is not None and pseudo_vol_unit is not None:
    #                 if doze_unit is not None: doze_unit = units_total_dict.get(doze_unit.strip().lower())
    #                 # if debug: print(f"post_process_doze_vol: pseudo_vol_unit before: '{pseudo_vol_unit}'")
    #                 if pseudo_vol_unit is not None: pseudo_vol_unit = units_total_dict.get(pseudo_vol_unit.strip().lower())
    #                 # if debug: print(f"post_process_doze_vol: pseudo_vol_unit after: '{pseudo_vol_unit}'")
    #                 if vol_unit is not None: vol_unit = units_total_dict.get(vol_unit.strip().lower())
    #                 if doze_unit.lower() in ['мг', 'мкг'] and pseudo_vol_unit.lower() in ['доз(а)']:
    #                     # doze_unit = 'мг' 
    #                     pseudo_vol_unit = None
    #             elif handler_group1 in [6] and doze_unit is not None and pseudo_vol_unit is not None:
    #                 if doze_unit is not None: doze_unit = units_total_dict.get(doze_unit.strip().lower())
    #                 # if debug: print(f"post_process_doze_vol: pseudo_vol_unit before: '{pseudo_vol_unit}'")
    #                 if pseudo_vol_unit is not None: pseudo_vol_unit = units_total_dict.get(pseudo_vol_unit.strip().lower())
    #                 # if debug: print(f"post_process_doze_vol: pseudo_vol_unit after: '{pseudo_vol_unit}'")
    #                 if vol_unit is not None: vol_unit = units_total_dict.get(vol_unit.strip().lower())
    #                 if doze_unit.lower() in ['мг', 'мкг'] and pseudo_vol_unit.lower() in ['мл']:
    #                     # doze_unit = 'мг' 
    #                     pseudo_vol_unit = None
    #         elif handler_group1 in [1]: # если стоит одно число => это объем, ставим это число, в поле "ед. измер." - ставим "-"
    #             if doze_unit is None and pseudo_vol_unit is None and vol_unit is None:
    #                 # [1, True, True, True]
    #                 doze, doze_unit, doze_str, pseudo_vol, pseudo_vol_unit, vol, vol_unit, vol_str = \
    #                   None, None, None, None, None, re.sub('[^A-Za-z0-9\.]+', '', one_number.replace(',','.')), None, None
    #                 if doze_unit is not None: doze_unit = units_total_dict.get(doze_unit.strip().lower())
    #                 if pseudo_vol_unit is not None: pseudo_vol_unit = units_total_dict.get(pseudo_vol_unit.strip().lower())
    #                 if vol_unit is not None: vol_unit = units_total_dict.get(vol_unit.strip().lower())
    #         elif handler_group1 in [4]: # если стоит одно число => это объем
    #             # [4, False, False, True]
    #             if doze_unit is None and pseudo_vol_unit is None and vol_unit is None:
    #                 doze, doze_unit, doze_str, pseudo_vol, pseudo_vol_unit, vol, vol_unit, vol_str = \
    #                   None, None, None, None, None, re.sub('[^A-Za-z0-9\.]+', '', one_number.replace(',','.')), None, None
    #                 if doze_unit is not None: doze_unit = units_total_dict.get(doze_unit.strip().lower())
    #                 if pseudo_vol_unit is not None: pseudo_vol_unit = units_total_dict.get(pseudo_vol_unit.strip().lower())
    #                 if vol_unit is not None: vol_unit = units_total_dict.get(vol_unit.strip().lower())
    #         elif handler_group1 in [5,7]:
    #             if debug: 
    #                 print(f"post_process_doze_vol: handler_group1 in [5,7]")
    #                 print(f"doze, doze_unit, pseudo_vol, pseudo_vol_unit, vol, vol_unit\n", doze, doze_unit, pseudo_vol, pseudo_vol_unit, vol, vol_unit)
                
    #             if doze_unit is None and pseudo_vol_unit is None and vol_unit is None:
    #                 # [5, True, True, True]
    #                 # 1) если стоит одно число (без ед. измер дозировки и объема) - то это объем 
    #                 doze, doze_unit, doze_str, pseudo_vol, pseudo_vol_unit, vol, vol_unit, vol_str = \
    #                   None, None, None, None, None, re.sub('[^A-Za-z0-9\.]+', '', one_number.replace(',','.')), None, None
    #                 if doze_unit is not None: doze_unit = units_total_dict.get(doze_unit.strip().lower())
    #                 if pseudo_vol_unit is not None: pseudo_vol_unit = units_total_dict.get(pseudo_vol_unit.strip().lower())
    #                 if vol_unit is not None: vol_unit = units_total_dict.get(vol_unit.strip().lower())

    #                 #2) если есть дозировка + ед. измер дозировки, потом число - то это объем
    #                 # надо проверить
    #                 # если находит 2 "объема" или 2 "дозировки"???
    #                 # elif handler_group1 in [8]: 
    #             elif handler_group1 in [5]  and doze_unit is not None and pseudo_vol_unit is not None:
    #                 if debug: print(f"post_process_doze_vol: мл/мл -> мг/мл")
    #                 if doze_unit.lower() in ['ml', 'мл'] and pseudo_vol_unit.lower() in ['ml', 'мл']:
    #                     doze_unit = 'мг'
    #                 if doze_unit is not None: units_total_dict.get(doze_unit.strip().lower())
    #                 if pseudo_vol_unit is not None: pseudo_vol_unit = units_total_dict.get(pseudo_vol_unit.strip().lower())
    #                 if vol_unit is not None: vol_unit = units_total_dict.get(vol_unit.strip().lower())

    #     elif handler_group1 in [0]:
    #         if doze_unit is not None and pseudo_vol_unit is not None:
    #             # if debug: print(f"post_process_doze_vol: мг/доз(а) -> мг")
    #             # if vol_unit.lower() in ['ml', 'мл'] and pseudo_vol_unit.lower() in ['ml', 'мл']:
    #             #     vol_unit = 'мг'
    #             if doze_unit is not None: doze_unit = units_total_dict.get(doze_unit.strip().lower())
    #             if pseudo_vol_unit is not None: pseudo_vol_unit = units_total_dict.get(pseudo_vol_unit.strip().lower())
    #             if vol_unit is not None: vol_unit = units_total_dict.get(vol_unit.strip().lower())
    #             if doze_unit.lower() in ['мг', 'мкг'] and pseudo_vol_unit.lower() in ['доз(а)']:
    #                 # doze_unit = 'мг' 
    #                 pseudo_vol_unit = None
    #             # elif doze_unit.lower() in ['мкг'] and pseudo_vol_unit.lower() in ['доз(а)]:
    #             #     doze_unit = 'мкг'
    #             #     pseudo_vol_unit = None
                
    #     elif handler_group1 in [5]:
    #         if doze_unit is not None and pseudo_vol_unit is not None:
    #             if debug: print(f"post_process_doze_vol: мл/мл -> мг/мл")
    #             # if vol_unit.lower() in ['ml', 'мл'] and pseudo_vol_unit.lower() in ['ml', 'мл']:
    #             #     vol_unit = 'мг'
    #             if doze_unit.lower() in ['ml', 'мл'] and pseudo_vol_unit.lower() in ['ml', 'мл']:
    #                 doze_unit = 'мг'
    #             if doze_unit is not None: doze_unit = units_total_dict.get(doze_unit.strip().lower())
    #             if pseudo_vol_unit is not None: pseudo_vol_unit = units_total_dict.get(pseudo_vol_unit.strip().lower())
    #             if vol_unit is not None: vol_unit = units_total_dict.get(vol_unit.strip().lower())
    #     elif handler_group1 in [7] and doze is None:
    #           # [7, True, True, True]
    #           if vol is not None and vol_unit is not None:
    #                 # 3) если стоит объем и ЕИ объема, то просто число - это дозировка
    #               # one_number = is_one_number_in_string(re.sub(vol_str, '', mis_position), debug=False)
    #               one_number = is_one_number_in_string(re.sub(vol_str, '', sw), debug=False)
    #               if one_number is not None:
    #                   #doze = one_number.replace(',','.').strip()
    #                   doze = re.sub('[^A-Za-z0-9\.]+', '', one_number.replace(',','.'))
    #     elif handler_group1 in [6]:
    #         if doze_unit is not None and pseudo_vol_unit is not None and \
    #             doze_unit in ('мг', 'мкг', 'mg', 'mkg', 'МЕ', 'ME') and pseudo_vol_unit in ('доза', 'доз', 'doza', 'doz', 'dosa', 'dos', 'd.', 'd'):
    #             ptn_digits = r'(?P<digits>(\d+,\d+)|(\d+\.\d+)|(\d+))'
    #             ptn_str = r"(?:" + ptn_digits + r")\s*" +\
    #                 r"(?P<unit>" +  "|".join(['(?:' + p + r")" for p in ('доза', 'доз', 'doza', 'doz', 'dosa', 'dos', 'd.', 'd')]) + r")\.*,*(\s*|$)" 
    #             vol, vol_unit, vol_str = vol_handler (handler_group1, ptn_str, mis_position, tn_ru_ext, tn_lat_ext, doze_str, debug=debug)
    #         elif doze_unit is not None and pseudo_vol_unit is not None:
    #             if doze_unit is not None: doze_unit = units_total_dict.get(doze_unit.strip().lower())
    #             # if debug: print(f"post_process_doze_vol: pseudo_vol_unit before: '{pseudo_vol_unit}'")
    #             if pseudo_vol_unit is not None: pseudo_vol_unit = units_total_dict.get(pseudo_vol_unit.strip().lower())
    #             # if debug: print(f"post_process_doze_vol: pseudo_vol_unit after: '{pseudo_vol_unit}'")
    #             if vol_unit is not None: vol_unit = units_total_dict.get(vol_unit.strip().lower())
    #             if doze_unit.lower() in ['мг', 'мкг'] and pseudo_vol_unit.lower() in ['мл']:
    #                 # doze_unit = 'мг' 
    #                 pseudo_vol_unit = None
    #         elif doze is None and doze_unit is None:
    #             local_units = [('мг', 'мкг', 'mg', 'mkg', 'МЕ', 'ME', 'мл', 'ml'), ('доза', 'доз', 'doza', 'doz', 'dosa', 'dos', 'd.', 'd')] 
    #             ptns_lst_pre = list(itertools.product(*local_units))
    #             ptns_lst = [i[0]+'/'+ i[1]  for i in ptns_lst_pre]
    #             special_doze_ptn_str = make_doze_ptn_str(ptns_lst)
    #             # print(special_doze_ptn_str)
    #             doze_proc, doze_proc_str, doze, doze_unit, doze_str, pseudo_vol, pseudo_vol_unit = \
    #                    doze_handler (handler_group1, sw, is_special_doze=True, special_doze_ptn_str=special_doze_ptn_str, debug=debug)
    #             special_vol_ptn_str = make_vol_ptn_str(['доза', 'доз', 'doza', 'doz', 'dosa', 'dos', 'd.', 'd'])
    #             vol, vol_unit, vol_str = \
    #                 vol_handler (handler_group1, special_vol_ptn_str, mis_position, tn_ru_ext, tn_lat_ext, doze_str, debug=debug)
        
    #     elif handler_group1 in [8] :
    #         if vol is None and doze is not None and doze_unit is not None:
    #             # 2) если есть дозировка + ЕИ дозировки, потом число - то это объем, 
    #             one_number = is_one_number_in_string(re.sub(doze_str, '', sw), debug=False)
    #             if one_number is not None:
    #                 # vol = one_number.replace(',','.').strip()
    #                 vol = re.sub('[^A-Za-z0-9\.]+', '', one_number.replace(',','.'))
                
    #         if doze is None and vol is not None and vol_unit is not None:
    #             # 3) если стоит объем и ЕИ объема, то просто число - это дозировка
    #             one_number = is_one_number_in_string(re.sub(vol_str, '', sw), debug=False)
    #             if one_number is not None:
    #                 # doze = one_number.replace(',','.').strip()
    #                 doze = re.sub('[^A-Za-z0-9\.]+', '', one_number.replace(',','.'))

    #     return doze, doze_unit, doze_str, pseudo_vol, pseudo_vol_unit, vol, vol_unit, vol_str

    # def extract_doze_vol_02(mis_position, tn_ru_ext, tn_lat_ext, pharm_form_unify, pharm_form, debug=False):
    #     # global doze_units_groups, vol_units_groups, doze_vol_handler_types, doze_vol_pharm_form_handlers
    #     handler_group, doze_proc, doze, doze_unit, doze_str, pseudo_vol, pseudo_vol_unit, vol, vol_unit, vol_str = \
    #     None, None, None, None, None, None, None, None, None, None
    #     doze_proc_str = None
    #     complex_doze_list, complex_doze_str = None, None
    #     if debug: print(f"extract_doze_vol_02: на входе: mis_position: '{mis_position}'")
    #     if pharm_form_unify is None: pharm_form_unify = 'ph_f_undefined'
    #     if doze_vol_pharm_form_handlers.get(pharm_form_unify) is not None:
    #         handler_group, is_dosed, is_pseudo_vol, is_vol, is_proc_dozed = doze_vol_pharm_form_handlers[pharm_form_unify]
    #         if debug: print("extract_doze_vol_02:", pharm_form_unify, "-->", handler_group, is_dosed, is_pseudo_vol, is_vol)
            
    #         if is_dosed: 
    #             doze_proc, doze_proc_str, doze, doze_unit, doze_str, pseudo_vol, pseudo_vol_unit = \
    #                 doze_handler (handler_group, mis_position, debug=debug)
                    
    #             if debug: 
    #                 print(f"extract_doze_vol_02: afte doze_handler: doze_proc: {doze_proc}, doze_proc_str: {doze_proc_str}", 
    #                       f"doze: {doze}, doze_unit: {doze_unit}, doze_str: '{doze_str}', pseudo_vol: {pseudo_vol}, pseudo_vol_unit: {pseudo_vol_unit}")
    #                       # doze_proc, doze_proc_str, doze, doze_unit, doze_str, pseudo_vol, pseudo_vol_unit)
    #         #if is_pseudo_vol: pseudo_vol, pseudo_vol_unit, pseudo_vol_str = pseudo_vol_handler (handler_group)
    #         if is_vol: 
    #             ptn_str = vol_units_groups[handler_group].get('ptn_str')
    #             vol, vol_unit, vol_str = \
    #                 vol_handler (handler_group, ptn_str, mis_position, tn_ru_ext, tn_lat_ext, doze_str, debug=debug)
            
    #         doze, doze_unit, doze_str, pseudo_vol, pseudo_vol_unit, vol, vol_unit, vol_str=\
    #         post_process_doze_vol(mis_position, handler_group, tn_ru_ext, tn_lat_ext, doze_proc_str, doze, doze_unit, 
    #                               doze_str, pseudo_vol, pseudo_vol_unit, vol, vol_unit, vol_str, debug=debug)
            
    #         if is_dosed:
    #             complex_doze_list, complex_doze_str = complex_doze_handler(handler_group, mis_position, doze_str, debug=debug)
    #         else: complex_doze_list, complex_doze_str = None, None

    #     else: pass #return doze, doze_unit, doze_str, pseudo_vol, pseudo_vol_unit, vol, vol_unit, vol_str
    #     # if debug: print(f"Extract_doze_vol: doze_group: {handler_group}, doze: {doze}, doze_unit: {doze_unit}, pseudo_vol: {pseudo_vol}, pseudo_vol_unit:{pseudo_vol_unit}, vol: {vol}, vol_unit: {vol_unit}")
    
    #     return handler_group, doze_proc, doze, doze_unit, doze_str, pseudo_vol, pseudo_vol_unit, complex_doze_list, complex_doze_str, vol, vol_unit, vol_str



    # v21.11.2022
    # def enhance_units(comlex_doze_list):
    #     # на взоде ['875', '35', '125 mg', '11', '22mkg/мл', '23мг|мл', '24 kg\мл']
    #     comlex_doze_list_enhanced = [] #comlex_doze_list
    #     ptn_digits = r"((\d+,\d+)|(\d+\.\d+)|([\d\s]+\d+)|(\d+))"
    #     ptn_mu = r"[^\d]*"
    #     last_mu = '' # measurement unit
    #     for item in comlex_doze_list:
    #         m_digits = re.search(ptn_digits, item)
    #         if m_digits is not None:
    #             digits = m_digits.group()
    #         else: digits = None
    #         m_mu = re.search(ptn_mu, re.sub(digits, '', item) if digits is not None else item)
    #         if m_mu is not None:
    #             mu = m_mu.group().replace('\\','/').replace('|','/')
    #             if len(mu)==0: mu = None
    #         else: mu = None
    #         comlex_doze_list_enhanced.append([digits, mu])
    #     # last_mu = '' # measurement unit
    #     last_mu = None # measurement unit
    #     comlex_doze_list_enhanced_01 = []
    #     for i, doze_tuple in enumerate(comlex_doze_list_enhanced[::-1]):
    #         if doze_tuple[1] is None or doze_tuple[1]=='':
    #             # comlex_doze_list_enhanced[::-1][i] = last_mu
    #             doze_tuple[1] = last_mu
    #             # print(f"last_mu: {last_mu}")
    #         else: last_mu = doze_tuple[1]
    #         comlex_doze_list_enhanced_01.append(doze_tuple)
    #     return comlex_doze_list_enhanced_01[::-1]

    # def standardize_unit(comlex_doze_list_enhanced):
    #     comlex_doze_list = []
    #     for item in comlex_doze_list_enhanced:
    #         if item[0] is not None:
    #             digits_standard = item[0].replace(',','.')
    #         if item[1] is not None:
    #             mu_split = item[1].split('/')
    #             mu_standard = '/'.join([units_total_dict.get(mu.strip().lower(),'') for mu in mu_split])
    #         else: mu_standard = None
    #         comlex_doze_list.append([digits_standard, mu_standard])
    #     return comlex_doze_list

    # def complex_doze_handler(handler_group, unparsed_str, doze_str, debug=False):
    #     complex_doze_list, complex_doze_str = None, None
    #     complex_doze_ptn_str = doze_units_groups[handler_group]['cmplx_ptn_str']
    #     if complex_doze_ptn_str is not None:
    #         m = re.search(complex_doze_ptn_str, unparsed_str, flags=re.I)
    #         if m is not None:
    #             complex_doze_str = m.group().strip()
    #             if complex_doze_str is not None  and doze_str is not None and complex_doze_str.strip() == doze_str.strip(): # Юперио табл. п/пл/об. 100 мг ( 51.4 мг+48.6 мг) 
    #                 m1 = re.search(complex_doze_ptn_str, re.sub(re.escape(doze_str), '', unparsed_str), flags=re.I)
    #                 if m1 is not None:
    #                     complex_doze_str = m1.group().strip()
    #             if complex_doze_str is not None and '+' in complex_doze_str:
    #                 complex_doze_list = complex_doze_str.split('+')
    #                 # не обрабатывает '20mg/ml/12.5mg/ml'
    #                 # 125 mg (1 caps.)+80 mg (2 caps.) +180 mg (3 caps.) 
                                
    #                 complex_doze_list_enhanced = enhance_units(complex_doze_list)
    #                 complex_doze_list = standardize_unit(complex_doze_list_enhanced)
    #             else: complex_doze_list, complex_doze_str = None, None

    #     return complex_doze_list, complex_doze_str

    # ### Doze, pseudo_vol, vol handlers
    # def doze_handler (handler_group2, unparsed_string, is_special_doze=False, special_doze_ptn_str=None, debug=False):
    
    #     doze_proc, doze, doze_unit, doze_str, pseudo_vol, pseudo_vol_unit = None, None, None, None, None, None
    #     doze_proc_str = None #doze_proc_pre
    #     if doze_vol_handler_types[handler_group2][4]: #is_proc_dozed
    #         # ptn_proc = r"(?:((\d+,\d+)|(\d+\.\d+)|([\d\s]+\d+)|(\d+))\s*%)"
    #         ptn_proc = r"(?:((\d+,\d+)|(\d+\.\d+)|(\d+))\s*%)"
    #         m_proc = re.search(ptn_proc, unparsed_string, flags=re.I)
    #         if m_proc is not None:
    #             doze_proc_str = m_proc.group()
    #             doze_proc = doze_proc_str.replace('%','').replace(',','.').strip()
    #     if debug: print(f"doze_handler: doze_proc_str: '{doze_proc_str}'" )
    #     if doze_vol_handler_types[handler_group2][1] or doze_vol_handler_types[handler_group2][2]: # is doze or iz peudo_vol
    #         if not is_special_doze:
    #             ptn_str = doze_units_groups[handler_group2].get('ptn_str')
    #         elif special_doze_ptn_str is not None:
    #             ptn_str = special_doze_ptn_str
    #         else: return doze_proc, doze_proc_str, doze, doze_unit, doze_str, pseudo_vol, pseudo_vol_unit

    #         if debug: print(f"handler_group: {handler_group2}")
    #         if doze_proc_str is not None: 
    #             unparsed_string = re.sub(doze_proc_str, '', unparsed_string)
    #         if debug: print(f"doze_handler: unparsed_string: '{unparsed_string}'")
    #         m = re.search(ptn_str, unparsed_string, flags=re.I)
    #         if m is None: 
    #             if debug: 
    #                 print(f"doze_handler: re.search(ptn_str, unparsed_string, flags=re.I): {m}")
    #                 # print(f"doze_handler: ptn_str: {ptn_str}")
    #         elif m is not None: 
    #             # if debug: print(m.group('digits'), m.group('unit'))
    #             # doze, doze_unit, doze_str = m.group('digits').strip(), m.group('unit').strip(), m.group()
    #             # pseudo_vol, pseudo_vol_unit = m.group('digits_pseudo'), m.group('unit_pseudo')
    #             # if pseudo_vol is not None: pseudo_vol = pseudo_vol.replace(r"/",r'')
    #             doze_str = m.group()
    #             doze_substrs = [(k,v) for k,v in m.groupdict().items() if v is not None]
    #             if debug: print("doze", doze_substrs)
    #             # [('doze_digits_000', '20'), ('doze_unit_000', 'мг'), ('digits_pseudo_000', '0.5'), ('unit_pseudo_000', 'мл')]
    #             if len (doze_substrs) > 0 : 
    #                 doze_substrs_dict = {}
    #                 doze_substrs_dict['doze_digits'] = [doze_substr[1] for doze_substr in doze_substrs if doze_substr[0].startswith('doze_digits')]
    #                 doze_substrs_dict['doze_unit'] = [doze_substr[1] for doze_substr in doze_substrs if doze_substr[0].startswith('doze_unit')]
    #                 doze_substrs_dict['digits_pseudo'] = [doze_substr[1] for doze_substr in doze_substrs if doze_substr[0].startswith('digits_pseudo')]
    #                 doze_substrs_dict['unit_pseudo'] = [doze_substr[1] for doze_substr in doze_substrs if doze_substr[0].startswith('unit_pseudo')]
                
    #                 if len(doze_substrs_dict['doze_digits']) > 0:
    #                     doze = doze_substrs_dict['doze_digits'][0]
    #                     if doze is not None: 
    #                         doze = doze.replace(',','.').replace(' ','')
    #                         doze = re.sub('[^A-Za-z0-9\.]+', '',doze)
    #                         if len(doze) > 0 and doze[-1]=='+': doze=doze[:-1]
    #                     if debug and len(doze_substrs_dict['doze_digits']) > 1:
    #                         print('doze_digits', 'are strange', doze_substrs_dict['doze_digits'])
    #                 if len(doze_substrs_dict['doze_unit']) > 0:
    #                     doze_unit = doze_substrs_dict['doze_unit'][0]
    #                     doze_unit = units_total_dict.get(doze_unit.strip().lower())
    #                     if debug and len(doze_substrs_dict['doze_unit']) > 1:
    #                         print('doze_unit', 'are strange', doze_substrs_dict['doze_unit'])
    #                 if len(doze_substrs_dict['digits_pseudo']) > 0:
    #                     pseudo_vol = doze_substrs_dict['digits_pseudo'][0]
    #                     if pseudo_vol is not None: 
    #                         pseudo_vol = pseudo_vol.replace(',','.').replace(' ','')
    #                         pseudo_vol = re.sub('[^A-Za-z0-9\.]+', '', pseudo_vol)
    #                     if debug and len(doze_substrs_dict['digits_pseudo']) > 1:
    #                         print('digits_pseudo', 'are strange', doze_substrs_dict['digits_pseudo'])
    #                 if len(doze_substrs_dict['unit_pseudo']) > 0:
    #                     pseudo_vol_unit = doze_substrs_dict['unit_pseudo'][0]
    #                     pseudo_vol_unit = units_total_dict.get(pseudo_vol_unit.strip().lower())
    #                     if debug and len(doze_substrs_dict['unit_pseudo']) > 1:
    #                         print('unit_pseudo', 'are strange', doze_substrs_dict['unit_pseudo'])
                
                
                
    #         #if not doze_vol_handler_types[handler_group][2]: pseudo_vol, pseudo_vol_unit = None, None
    #         if pseudo_vol_unit is not None and pseudo_vol_unit=='': pseudo_vol_unit = None
    #         #if pseudo_vol is None and doze_vol_handler_types[handler_group][2]: 
    #         # if pseudo_vol is None and pseudo_vol_unit is not None: 
    #         #     pseudo_vol = '1'

    #     return doze_proc, doze_proc_str, doze, doze_unit, doze_str, pseudo_vol, pseudo_vol_unit
            

    # def pseudo_vol_handler (handler_group3):
    #     pseudo_vol, pseudo_vol_unit, pseudo_vol_str = None, None, None
    #     return pseudo_vol, pseudo_vol_unit, pseudo_vol_str

    # def vol_handler (handler_group4, ptn_str, mis_position, tn_ru_ext, tn_lat_ext, doze_str, debug=False):
    #     # global doze_vol_handler_types 
    #     vol, vol_unit, vol_str = None, None, None
    #     if debug: print(f"vol_handler: doze_str: '{doze_str}'")
    #     if debug: print(f"vol_handler: ptn_str: '{ptn_str}'")
    #     if doze_vol_handler_types[handler_group4][3] or handler_group4 in [6]: # is_vol или особый вариант для порошки лиофидизаты
    #         if doze_str is not None:
    #             try: 
    #                 sw = re.sub(re.escape(doze_str), '', mis_position)
    #             except Exception as err:
    #                 print("ERROR!", err)
    #                 print(f"vol_handler: mis_position: '{mis_position}', doze_str: '{doze_str}'")
    #                 sw = mis_position
    #         else: sw = mis_position
    #         # Berotec N 100mkg/dosa 200 доз N1 аэрозоль
    #         try:
    #             if tn_ru_ext is not None: sw = re.sub(re.escape(tn_ru_ext), '', sw)
    #             if tn_lat_ext is not None: sw = re.sub(re.escape(tn_lat_ext), '', sw)
    #         except Exception as err:
    #             print("ERROR! : re.sub(tn_ru_ext, '', sw)", err)
    #             print(f"vol_handler: sw: '{sw}', tn_ru_ext: '{tn_ru_ext}', tn_lat_ext: '{tn_lat_ext}'")
    #         if debug: print(F"vol_handler: sw='{sw}'")
    #         #sw = re.sub(r"(N|№)\s*[\d\w]*\b", '', sw)
    #         sw = re.sub(r"(N|№)[\s\d+xXхХ]*\b|$", '', sw)
    #         #print(vol_units_groups[i].get('ptn_str'))
    #         m = re.search(ptn_str, sw, flags=re.I)
    #         if m is not None:
    #             if debug: print("vol_handler:",f"'{sw}',  -->vol: '{m.group('digits')}', '{m.group('unit')}'")
    #             # vol, vol_unit, vol_str = m.group('digits').replace(',','.').replace(' ','').strip(), m.group('unit'), m.group()
    #             vol = re.sub('[^A-Za-z0-9\.]+', '', m.group('digits')) #m.group('digits').replace(',','.').replace(' ','') 
    #             vol_unit, vol_str = m.group('unit').strip(), m.group()
    #             if vol_unit is not None: vol_unit = units_total_dict.get(vol_unit.strip().lower())
    #             if debug: print(f"vol_handler: {vol}: {vol}, vol_unit: {vol_unit}, vol_str: '{vol_str}'")
    #     return vol, vol_unit, vol_str

    # def is_one_number_in_string(mis_position, debug=False):
    #     rez = None
    #     mis_position_cut = re.sub(r"(?<=\s)(N|№)[\s\d+xXхХ]*\b|$", '', mis_position) # чистим от N10x1
    #     mis_position_cut = re.sub(r"(?:\d\d\.\d\d\.\d\d\d\d)|(?:\d\d\.\d\d\d\d)", '', mis_position_cut) # читстим от  06.2022г.
    #     if debug: print(f"mis_position_cut: '{mis_position_cut}'")
    #     # lst = re.findall(r"\d+,\d+|\d+\.\d+|[\d\s]+\d+|\d+",  mis_position_cut)
    #     #lst = re.findall(r"(?:(\d+,\d+)|(\d+\.\d+)|([\d\s]+\d+)|(\d+))",  mis_position_cut)
    #     #lst = re.findall(r"(?<=\w(N|№))(?:\d+,\d+)|(?:\d+\.\d+)|(?:\d+)",  mis_position_cut)
    #     lst = re.findall(r"(?:\d+[,\.]*\d*)", mis_position_cut)
    #     # if len(lst)==1: return lst[0]
    #     if len(lst)==1: rez = lst[0]
    #     else: rez = None
    #     return rez 
        
    # def post_process_doze_vol(mis_position, handler_group1, tn_ru_ext, tn_lat_ext, doze_proc_str, doze, doze_unit, doze_str, pseudo_vol, pseudo_vol_unit, vol, vol_unit, vol_str, debug=False):
    #     ptn_digits = r'(?P<digits>(\d+,\d+|\d+\.\d+|\d+))'
    #     if doze_proc_str is not None:
    #         sw = re.sub(doze_proc_str, '', mis_position )
    #     else: sw = mis_position
    #     one_number = is_one_number_in_string(sw, debug=debug) #mis_poistion
    #     if debug: print(f"post_process_doze_vol: handler_group: {handler_group1}, one_number: '{one_number}'")
    #     if debug: print(f"post_process_doze_vol: vol: {vol}, vol_unit: {vol_unit}")
    #     # if one_number is not None and doze_unit is None and pseudo_vol_unit is None and vol_unit is None:
    #     if one_number is not None:
    #         if handler_group1 in [0, 6, 8]: # если стоит одно число => это дозировка, ставим это число, в поле "ед. измер." - ставим "-"
    #             if doze_unit is None and pseudo_vol_unit is None and vol_unit is None:
    #                 # handler_numder, is_is_dosed, is_pseudo_vol, is_vol
    #                 # [0, True, False, False] # Таблетки...
    #                 # [6, True, False, False] 
    #                 # [8, False, False, False] # если есть одно число - ставим в дозировку
    #                 #if doze is None:
    #                 doze, doze_unit, doze_str, pseudo_vol, pseudo_vol_unit, vol, vol_unit, vol_str = \
    #                     re.sub('[^A-Za-z0-9\.]+', '', one_number.replace(',','.')), None, None, None, None, None, None, None
    #             elif handler_group1 in [0] and doze_unit is not None and pseudo_vol_unit is not None:
    #                 if doze_unit is not None: doze_unit = units_total_dict.get(doze_unit.strip().lower())
    #                 # if debug: print(f"post_process_doze_vol: pseudo_vol_unit before: '{pseudo_vol_unit}'")
    #                 if pseudo_vol_unit is not None: pseudo_vol_unit = units_total_dict.get(pseudo_vol_unit.strip().lower())
    #                 # if debug: print(f"post_process_doze_vol: pseudo_vol_unit after: '{pseudo_vol_unit}'")
    #                 if vol_unit is not None: vol_unit = units_total_dict.get(vol_unit.strip().lower())
    #                 if doze_unit.lower() in ['мг', 'мкг'] and pseudo_vol_unit.lower() in ['доз(а)']:
    #                     # doze_unit = 'мг' 
    #                     pseudo_vol_unit = None
    #             elif handler_group1 in [6] and doze_unit is not None and pseudo_vol_unit is not None:
    #                 if doze_unit is not None: doze_unit = units_total_dict.get(doze_unit.strip().lower())
    #                 # if debug: print(f"post_process_doze_vol: pseudo_vol_unit before: '{pseudo_vol_unit}'")
    #                 if pseudo_vol_unit is not None: pseudo_vol_unit = units_total_dict.get(pseudo_vol_unit.strip().lower())
    #                 # if debug: print(f"post_process_doze_vol: pseudo_vol_unit after: '{pseudo_vol_unit}'")
    #                 if vol_unit is not None: vol_unit = units_total_dict.get(vol_unit.strip().lower())
    #                 if doze_unit.lower() in ['мг', 'мкг'] and pseudo_vol_unit.lower() in ['мл']:
    #                     # doze_unit = 'мг' 
    #                     pseudo_vol_unit = None
    #         elif handler_group1 in [1]: # если стоит одно число => это объем, ставим это число, в поле "ед. измер." - ставим "-"
    #             if doze_unit is None and pseudo_vol_unit is None and vol_unit is None:
    #                 # [1, True, True, True]
    #                 doze, doze_unit, doze_str, pseudo_vol, pseudo_vol_unit, vol, vol_unit, vol_str = \
    #                   None, None, None, None, None, re.sub('[^A-Za-z0-9\.]+', '', one_number.replace(',','.')), None, None
    #                 if doze_unit is not None: doze_unit = units_total_dict.get(doze_unit.strip().lower())
    #                 if pseudo_vol_unit is not None: pseudo_vol_unit = units_total_dict.get(pseudo_vol_unit.strip().lower())
    #                 if vol_unit is not None: vol_unit = units_total_dict.get(vol_unit.strip().lower())
    #         elif handler_group1 in [4]: # если стоит одно число => это объем
    #             # [4, False, False, True]
    #             if doze_unit is None and pseudo_vol_unit is None and vol_unit is None:
    #                 doze, doze_unit, doze_str, pseudo_vol, pseudo_vol_unit, vol, vol_unit, vol_str = \
    #                   None, None, None, None, None, re.sub('[^A-Za-z0-9\.]+', '', one_number.replace(',','.')), None, None
    #                 if doze_unit is not None: doze_unit = units_total_dict.get(doze_unit.strip().lower())
    #                 if pseudo_vol_unit is not None: pseudo_vol_unit = units_total_dict.get(pseudo_vol_unit.strip().lower())
    #                 if vol_unit is not None: vol_unit = units_total_dict.get(vol_unit.strip().lower())
    #         elif handler_group1 in [5,7]:
    #             if debug: 
    #                 print(f"post_process_doze_vol: handler_group1 in [5,7]")
    #                 print(f"doze, doze_unit, pseudo_vol, pseudo_vol_unit, vol, vol_unit\n", doze, doze_unit, pseudo_vol, pseudo_vol_unit, vol, vol_unit)
                
    #             if doze_unit is None and pseudo_vol_unit is None and vol_unit is None:
    #                 # [5, True, True, True]
    #                 # 1) если стоит одно число (без ед. измер дозировки и объема) - то это объем 
    #                 doze, doze_unit, doze_str, pseudo_vol, pseudo_vol_unit, vol, vol_unit, vol_str = \
    #                   None, None, None, None, None, re.sub('[^A-Za-z0-9\.]+', '', one_number.replace(',','.')), None, None
    #                 if doze_unit is not None: doze_unit = units_total_dict.get(doze_unit.strip().lower())
    #                 if pseudo_vol_unit is not None: pseudo_vol_unit = units_total_dict.get(pseudo_vol_unit.strip().lower())
    #                 if vol_unit is not None: vol_unit = units_total_dict.get(vol_unit.strip().lower())

    #                 #2) если есть дозировка + ед. измер дозировки, потом число - то это объем
    #                 # надо проверить
    #                 # если находит 2 "объема" или 2 "дозировки"???
    #                 # elif handler_group1 in [8]: 
    #             elif handler_group1 in [5]  and doze_unit is not None and pseudo_vol_unit is not None:
    #                 if debug: print(f"post_process_doze_vol: мл/мл -> мг/мл")
    #                 if doze_unit.lower() in ['ml', 'мл'] and pseudo_vol_unit.lower() in ['ml', 'мл']:
    #                     doze_unit = 'мг'
    #                 if doze_unit is not None: units_total_dict.get(doze_unit.strip().lower())
    #                 if pseudo_vol_unit is not None: pseudo_vol_unit = units_total_dict.get(pseudo_vol_unit.strip().lower())
    #                 if vol_unit is not None: vol_unit = units_total_dict.get(vol_unit.strip().lower())

    #     elif handler_group1 in [0]:
    #         if doze_unit is not None and pseudo_vol_unit is not None:
    #             # if debug: print(f"post_process_doze_vol: мг/доз(а) -> мг")
    #             # if vol_unit.lower() in ['ml', 'мл'] and pseudo_vol_unit.lower() in ['ml', 'мл']:
    #             #     vol_unit = 'мг'
    #             if doze_unit is not None: doze_unit = units_total_dict.get(doze_unit.strip().lower())
    #             if pseudo_vol_unit is not None: pseudo_vol_unit = units_total_dict.get(pseudo_vol_unit.strip().lower())
    #             if vol_unit is not None: vol_unit = units_total_dict.get(vol_unit.strip().lower())
    #             if doze_unit.lower() in ['мг', 'мкг'] and pseudo_vol_unit.lower() in ['доз(а)']:
    #                 # doze_unit = 'мг' 
    #                 pseudo_vol_unit = None
    #             # elif doze_unit.lower() in ['мкг'] and pseudo_vol_unit.lower() in ['доз(а)]:
    #             #     doze_unit = 'мкг'
    #             #     pseudo_vol_unit = None
                
    #     elif handler_group1 in [5]:
    #         if doze_unit is not None and pseudo_vol_unit is not None:
    #             if debug: print(f"post_process_doze_vol: мл/мл -> мг/мл")
    #             # if vol_unit.lower() in ['ml', 'мл'] and pseudo_vol_unit.lower() in ['ml', 'мл']:
    #             #     vol_unit = 'мг'
    #             if doze_unit.lower() in ['ml', 'мл'] and pseudo_vol_unit.lower() in ['ml', 'мл']:
    #                 doze_unit = 'мг'
    #             if doze_unit is not None: doze_unit = units_total_dict.get(doze_unit.strip().lower())
    #             if pseudo_vol_unit is not None: pseudo_vol_unit = units_total_dict.get(pseudo_vol_unit.strip().lower())
    #             if vol_unit is not None: vol_unit = units_total_dict.get(vol_unit.strip().lower())
    #     elif handler_group1 in [7] and doze is None:
    #           # [7, True, True, True]
    #           if vol is not None and vol_unit is not None:
    #                 # 3) если стоит объем и ЕИ объема, то просто число - это дозировка
    #               # one_number = is_one_number_in_string(re.sub(vol_str, '', mis_position), debug=False)
    #               one_number = is_one_number_in_string(re.sub(vol_str, '', sw), debug=False)
    #               if one_number is not None:
    #                   #doze = one_number.replace(',','.').strip()
    #                   doze = re.sub('[^A-Za-z0-9\.]+', '', one_number.replace(',','.'))
    #     elif handler_group1 in [6]:
    #         if doze_unit is not None and pseudo_vol_unit is not None and \
    #             doze_unit in ('мг', 'мкг', 'mg', 'mkg', 'МЕ', 'ME') and pseudo_vol_unit in ('доза', 'доз', 'doza', 'doz', 'dosa', 'dos', 'd.', 'd'):
    #             ptn_digits = r'(?P<digits>(\d+,\d+)|(\d+\.\d+)|(\d+))'
    #             ptn_str = r"(?:" + ptn_digits + r")\s*" +\
    #                 r"(?P<unit>" +  "|".join(['(?:' + p + r")" for p in ('доза', 'доз', 'doza', 'doz', 'dosa', 'dos', 'd.', 'd')]) + r")\.*,*(\s*|$)" 
    #             vol, vol_unit, vol_str = vol_handler (handler_group1, ptn_str, mis_position, tn_ru_ext, tn_lat_ext, doze_str, debug=debug)
    #         elif doze_unit is not None and pseudo_vol_unit is not None:
    #             if doze_unit is not None: doze_unit = units_total_dict.get(doze_unit.strip().lower())
    #             # if debug: print(f"post_process_doze_vol: pseudo_vol_unit before: '{pseudo_vol_unit}'")
    #             if pseudo_vol_unit is not None: pseudo_vol_unit = units_total_dict.get(pseudo_vol_unit.strip().lower())
    #             # if debug: print(f"post_process_doze_vol: pseudo_vol_unit after: '{pseudo_vol_unit}'")
    #             if vol_unit is not None: vol_unit = units_total_dict.get(vol_unit.strip().lower())
    #             if doze_unit.lower() in ['мг', 'мкг'] and pseudo_vol_unit.lower() in ['мл']:
    #                 # doze_unit = 'мг' 
    #                 pseudo_vol_unit = None
    #         elif doze is None and doze_unit is None:
    #             local_units = [('мг', 'мкг', 'mg', 'mkg', 'МЕ', 'ME', 'мл', 'ml'), ('доза', 'доз', 'doza', 'doz', 'dosa', 'dos', 'd.', 'd')] 
    #             ptns_lst_pre = list(itertools.product(*local_units))
    #             ptns_lst = [i[0]+'/'+ i[1]  for i in ptns_lst_pre]
    #             special_doze_ptn_str = make_doze_ptn_str(ptns_lst)
    #             # print(special_doze_ptn_str)
    #             doze_proc, doze_proc_str, doze, doze_unit, doze_str, pseudo_vol, pseudo_vol_unit = \
    #                    doze_handler (handler_group1, sw, is_special_doze=True, special_doze_ptn_str=special_doze_ptn_str, debug=debug)
    #             special_vol_ptn_str = make_vol_ptn_str(['доза', 'доз', 'doza', 'doz', 'dosa', 'dos', 'd.', 'd'])
    #             vol, vol_unit, vol_str = \
    #                 vol_handler (handler_group1, special_vol_ptn_str, mis_position, tn_ru_ext, tn_lat_ext, doze_str, debug=debug)
        
    #     elif handler_group1 in [8] :
    #         if vol is None and doze is not None and doze_unit is not None:
    #             # 2) если есть дозировка + ЕИ дозировки, потом число - то это объем, 
    #             one_number = is_one_number_in_string(re.sub(doze_str, '', sw), debug=False)
    #             if one_number is not None:
    #                 # vol = one_number.replace(',','.').strip()
    #                 vol = re.sub('[^A-Za-z0-9\.]+', '', one_number.replace(',','.'))
                
    #         if doze is None and vol is not None and vol_unit is not None:
    #             # 3) если стоит объем и ЕИ объема, то просто число - это дозировка
    #             one_number = is_one_number_in_string(re.sub(vol_str, '', sw), debug=False)
    #             if one_number is not None:
    #                 # doze = one_number.replace(',','.').strip()
    #                 doze = re.sub('[^A-Za-z0-9\.]+', '', one_number.replace(',','.'))

    #     return doze, doze_unit, doze_str, pseudo_vol, pseudo_vol_unit, vol, vol_unit, vol_str

    # def extract_doze_vol_02(mis_position, tn_ru_ext, tn_lat_ext, pharm_form_unify, pharm_form, debug=False):
    #     # global doze_units_groups, vol_units_groups, doze_vol_handler_types, doze_vol_pharm_form_handlers
    #     handler_group, doze_proc, doze, doze_unit, doze_str, pseudo_vol, pseudo_vol_unit, vol, vol_unit, vol_str = \
    #     None, None, None, None, None, None, None, None, None, None
    #     doze_proc_str = None
    #     complex_doze_list, complex_doze_str = None, None
    #     if pharm_form_unify is None: pharm_form_unify = 'ph_f_undefined'
    #     if doze_vol_pharm_form_handlers.get(pharm_form_unify) is not None:
    #         handler_group, is_dosed, is_pseudo_vol, is_vol, is_proc_dozed = doze_vol_pharm_form_handlers[pharm_form_unify]
    #         if debug: print(pharm_form_unify, "-->", handler_group, is_dosed, is_pseudo_vol, is_vol)
            
    #         if is_dosed: 
    #             doze_proc, doze_proc_str, doze, doze_unit, doze_str, pseudo_vol, pseudo_vol_unit = \
    #                 doze_handler (handler_group, mis_position, debug=debug)
                    
    #             if debug: 
    #                 print("extract_doze_vol_02: doze_proc, doze_proc_str, doze, doze_unit, doze_str, pseudo_vol, pseudo_vol_unit\n",
    #                       doze_proc, doze_proc_str, doze, doze_unit, doze_str, pseudo_vol, pseudo_vol_unit)
    #         #if is_pseudo_vol: pseudo_vol, pseudo_vol_unit, pseudo_vol_str = pseudo_vol_handler (handler_group)
    #         if is_vol: 
    #             ptn_str = vol_units_groups[handler_group].get('ptn_str')
    #             vol, vol_unit, vol_str = \
    #                 vol_handler (handler_group, ptn_str, mis_position, tn_ru_ext, tn_lat_ext, doze_str, debug=debug)
            
    #         doze, doze_unit, doze_str, pseudo_vol, pseudo_vol_unit, vol, vol_unit, vol_str=\
    #         post_process_doze_vol(mis_position, handler_group, tn_ru_ext, tn_lat_ext, doze_proc_str, doze, doze_unit, doze_str, pseudo_vol, pseudo_vol_unit, vol, vol_unit, vol_str, debug=debug)
            
    #         if is_dosed:
    #             complex_doze_list, complex_doze_str = complex_doze_handler(handler_group, mis_position, doze_str, debug=debug)
    #         else: complex_doze_list, complex_doze_str = None, None

    #     else: pass #return doze, doze_unit, doze_str, pseudo_vol, pseudo_vol_unit, vol, vol_unit, vol_str
    #     # if debug: print(f"Extract_doze_vol: doze_group: {handler_group}, doze: {doze}, doze_unit: {doze_unit}, pseudo_vol: {pseudo_vol}, pseudo_vol_unit:{pseudo_vol_unit}, vol: {vol}, vol_unit: {vol_unit}")
    
    #     return handler_group, doze_proc, doze, doze_unit, doze_str, pseudo_vol, pseudo_vol_unit, complex_doze_list, complex_doze_str, vol, vol_unit, vol_str


    # v old
    # def enhance_units(comlex_doze_list):
    #     # на взоде ['875', '35', '125 mg', '11', '22mkg/мл', '23мг|мл', '24 kg\мл']
    #     comlex_doze_list_enhanced = [] #comlex_doze_list
    #     ptn_digits = r"((\d+,\d+)|(\d+\.\d+)|([\d\s]+\d+)|(\d+))"
    #     ptn_mu = r"[^\d]*"
    #     last_mu = '' # measurement unit
    #     for item in comlex_doze_list:
    #         m_digits = re.search(ptn_digits, item)
    #         if m_digits is not None:
    #             digits = m_digits.group()
    #         else: digits = None
    #         m_mu = re.search(ptn_mu, re.sub(digits, '', item) if digits is not None else item)
    #         if m_mu is not None:
    #             mu = m_mu.group().replace('\\','/').replace('|','/')
    #             if len(mu)==0: mu = None
    #         else: mu = None
    #         comlex_doze_list_enhanced.append([digits, mu])
    #     # last_mu = '' # measurement unit
    #     last_mu = None # measurement unit
    #     comlex_doze_list_enhanced_01 = []
    #     for i, doze_tuple in enumerate(comlex_doze_list_enhanced[::-1]):
    #         if doze_tuple[1] is None or doze_tuple[1]=='':
    #             # comlex_doze_list_enhanced[::-1][i] = last_mu
    #             doze_tuple[1] = last_mu
    #             # print(f"last_mu: {last_mu}")
    #         else: last_mu = doze_tuple[1]
    #         comlex_doze_list_enhanced_01.append(doze_tuple)
    #     return comlex_doze_list_enhanced_01[::-1]

    # def standardize_unit(comlex_doze_list_enhanced):
    #     comlex_doze_list = []
    #     for item in comlex_doze_list_enhanced:
    #         if item[0] is not None:
    #             digits_standard = item[0].replace(',','.')
    #         if item[1] is not None:
    #             mu_split = item[1].split('/')
    #             mu_standard = '/'.join([units_total_dict.get(mu.strip().lower(),'') for mu in mu_split])
    #         else: mu_standard = None
    #         comlex_doze_list.append([digits_standard, mu_standard])
    #     return comlex_doze_list

    # def complex_doze_handler(handler_group, unparsed_str, doze_str, debug=False):
    #     complex_doze_list, complex_doze_str = None, None
    #     complex_doze_ptn_str = doze_units_groups[handler_group]['cmplx_ptn_str']
    #     if complex_doze_ptn_str is not None:
    #         m = re.search(complex_doze_ptn_str, unparsed_str, flags=re.I)
    #         if m is not None:
    #             complex_doze_str = m.group().strip()
    #             if complex_doze_str is not None  and doze_str is not None and complex_doze_str.strip() == doze_str.strip(): # Юперио табл. п/пл/об. 100 мг ( 51.4 мг+48.6 мг) 
    #                 m1 = re.search(complex_doze_ptn_str, re.sub(re.escape(doze_str), '', unparsed_str), flags=re.I)
    #                 if m1 is not None:
    #                     complex_doze_str = m1.group().strip()
    #             if complex_doze_str is not None and '+' in complex_doze_str:
    #                 complex_doze_list = complex_doze_str.split('+')
    #                 # не обрабатывает '20mg/ml/12.5mg/ml'
    #                 # 125 mg (1 caps.)+80 mg (2 caps.) +180 mg (3 caps.) 
                                
    #                 complex_doze_list_enhanced = enhance_units(complex_doze_list)
    #                 complex_doze_list = standardize_unit(complex_doze_list_enhanced)
    #             else: complex_doze_list, complex_doze_str = None, None

    #     return complex_doze_list, complex_doze_str

    # ### Doze, pseudo_vol, vol handlers
    # def doze_handler (handler_group2, unparsed_string, is_special_doze=False, special_doze_ptn_str=None, debug=False):
    
    #     doze_proc, doze, doze_unit, doze_str, pseudo_vol, pseudo_vol_unit = None, None, None, None, None, None
    #     doze_proc_str = None #doze_proc_pre
    #     if doze_vol_handler_types[handler_group2][4]: #is_proc_dozed
    #         # ptn_proc = r"(?:((\d+,\d+)|(\d+\.\d+)|([\d\s]+\d+)|(\d+))\s*%)"
    #         ptn_proc = r"(?:((\d+,\d+)|(\d+\.\d+)|(\d+))\s*%)"
    #         m_proc = re.search(ptn_proc, unparsed_string, flags=re.I)
    #         if m_proc is not None:
    #             doze_proc_str = m_proc.group()
    #             doze_proc = doze_proc_str.replace('%','').replace(',','.').strip()
    #     if debug: print(f"doze_handler: doze_proc_str: '{doze_proc_str}'" )
    #     if doze_vol_handler_types[handler_group2][1] or doze_vol_handler_types[handler_group2][2]: # is doze or iz peudo_vol
    #         if not is_special_doze:
    #             ptn_str = doze_units_groups[handler_group2].get('ptn_str')
    #         elif special_doze_ptn_str is not None:
    #             ptn_str = special_doze_ptn_str
    #         else: return doze_proc, doze_proc_str, doze, doze_unit, doze_str, pseudo_vol, pseudo_vol_unit

    #         if debug: print(f"handler_group: {handler_group2}")
    #         if doze_proc_str is not None: 
    #             unparsed_string = re.sub(doze_proc_str, '', unparsed_string)
    #         if debug: print(f"doze_handler: unparsed_string: '{unparsed_string}'")
    #         m = re.search(ptn_str, unparsed_string, flags=re.I)
    #         if m is None: 
    #             if debug: 
    #                 print(f"doze_handler: re.search(ptn_str, unparsed_string, flags=re.I): {m}")
    #                 print(f"doze_handler: ptn_str: {ptn_str}")
    #         elif m is not None: 
    #             # if debug: print(m.group('digits'), m.group('unit'))
    #             # doze, doze_unit, doze_str = m.group('digits').strip(), m.group('unit').strip(), m.group()
    #             # pseudo_vol, pseudo_vol_unit = m.group('digits_pseudo'), m.group('unit_pseudo')
    #             # if pseudo_vol is not None: pseudo_vol = pseudo_vol.replace(r"/",r'')
    #             doze_str = m.group()
    #             doze_substrs = [(k,v) for k,v in m.groupdict().items() if v is not None]
    #             if debug: print("doze", doze_substrs)
    #             # [('doze_digits_000', '20'), ('doze_unit_000', 'мг'), ('digits_pseudo_000', '0.5'), ('unit_pseudo_000', 'мл')]
    #             if len (doze_substrs) > 0 : 
    #                 doze_substrs_dict = {}
    #                 doze_substrs_dict['doze_digits'] = [doze_substr[1] for doze_substr in doze_substrs if doze_substr[0].startswith('doze_digits')]
    #                 doze_substrs_dict['doze_unit'] = [doze_substr[1] for doze_substr in doze_substrs if doze_substr[0].startswith('doze_unit')]
    #                 doze_substrs_dict['digits_pseudo'] = [doze_substr[1] for doze_substr in doze_substrs if doze_substr[0].startswith('digits_pseudo')]
    #                 doze_substrs_dict['unit_pseudo'] = [doze_substr[1] for doze_substr in doze_substrs if doze_substr[0].startswith('unit_pseudo')]
                
    #                 if len(doze_substrs_dict['doze_digits']) > 0:
    #                     doze = doze_substrs_dict['doze_digits'][0]
    #                     if doze is not None: 
    #                         doze = doze.replace(',','.').replace(' ','')
    #                         doze = re.sub('[^A-Za-z0-9\.]+', '',doze)
    #                         if len(doze) > 0 and doze[-1]=='+': doze=doze[:-1]
    #                     if debug and len(doze_substrs_dict['doze_digits']) > 1:
    #                         print('doze_digits', 'are strange', doze_substrs_dict['doze_digits'])
    #                 if len(doze_substrs_dict['doze_unit']) > 0:
    #                     doze_unit = doze_substrs_dict['doze_unit'][0]
    #                     doze_unit = units_total_dict.get(doze_unit.strip().lower())
    #                     if debug and len(doze_substrs_dict['doze_unit']) > 1:
    #                         print('doze_unit', 'are strange', doze_substrs_dict['doze_unit'])
    #                 if len(doze_substrs_dict['digits_pseudo']) > 0:
    #                     pseudo_vol = doze_substrs_dict['digits_pseudo'][0]
    #                     if pseudo_vol is not None: 
    #                         pseudo_vol = pseudo_vol.replace(',','.').replace(' ','')
    #                         pseudo_vol = re.sub('[^A-Za-z0-9\.]+', '', pseudo_vol)
    #                     if debug and len(doze_substrs_dict['digits_pseudo']) > 1:
    #                         print('digits_pseudo', 'are strange', doze_substrs_dict['digits_pseudo'])
    #                 if len(doze_substrs_dict['unit_pseudo']) > 0:
    #                     pseudo_vol_unit = doze_substrs_dict['unit_pseudo'][0]
    #                     pseudo_vol_unit = units_total_dict.get(pseudo_vol_unit.strip().lower())
    #                     if debug and len(doze_substrs_dict['unit_pseudo']) > 1:
    #                         print('unit_pseudo', 'are strange', doze_substrs_dict['unit_pseudo'])
                
                
                
    #         #if not doze_vol_handler_types[handler_group][2]: pseudo_vol, pseudo_vol_unit = None, None
    #         if pseudo_vol_unit is not None and pseudo_vol_unit=='': pseudo_vol_unit = None
    #         #if pseudo_vol is None and doze_vol_handler_types[handler_group][2]: 
    #         # if pseudo_vol is None and pseudo_vol_unit is not None: 
    #         #     pseudo_vol = '1'

    #     return doze_proc, doze_proc_str, doze, doze_unit, doze_str, pseudo_vol, pseudo_vol_unit
            

    # def pseudo_vol_handler (handler_group3):
    #     pseudo_vol, pseudo_vol_unit, pseudo_vol_str = None, None, None
    #     return pseudo_vol, pseudo_vol_unit, pseudo_vol_str

    # def vol_handler (handler_group4, ptn_str, mis_position, tn_ru_ext, tn_lat_ext, doze_str, debug=False):
    #     # global doze_vol_handler_types 
    #     vol, vol_unit, vol_str = None, None, None
    #     if debug: print(f"vol_handler: doze_str: '{doze_str}'")
    #     if debug: print(f"vol_handler: ptn_str: '{ptn_str}'")
    #     if doze_vol_handler_types[handler_group4][3] or handler_group4 in [6]: # is_vol или особый вариант для порошки лиофидизаты
    #         if doze_str is not None:
    #             try: 
    #                 sw = re.sub(re.escape(doze_str), '', mis_position)
    #             except Exception as err:
    #                 print("ERROR!", err)
    #                 print(f"vol_handler: mis_position: '{mis_position}', doze_str: '{doze_str}'")
    #                 sw = mis_position
    #         else: sw = mis_position
    #         # Berotec N 100mkg/dosa 200 доз N1 аэрозоль
    #         try:
    #             if tn_ru_ext is not None: sw = re.sub(re.escape(tn_ru_ext), '', sw)
    #             if tn_lat_ext is not None: sw = re.sub(re.escape(tn_lat_ext), '', sw)
    #         except Exception as err:
    #             print("ERROR! : re.sub(tn_ru_ext, '', sw)", err)
    #             print(f"vol_handler: sw: '{sw}', tn_ru_ext: '{tn_ru_ext}', tn_lat_ext: '{tn_lat_ext}'")
    #         if debug: print(F"vol_handler: sw='{sw}'")
    #         #sw = re.sub(r"(N|№)\s*[\d\w]*\b", '', sw)
    #         sw = re.sub(r"(N|№)[\s\d+xXхХ]*\b|$", '', sw)
    #         #print(vol_units_groups[i].get('ptn_str'))
    #         m = re.search(ptn_str, sw, flags=re.I)
    #         if m is not None:
    #             if debug: print("vol_handler:",f"'{sw}',  -->vol: '{m.group('digits')}', '{m.group('unit')}'")
    #             # vol, vol_unit, vol_str = m.group('digits').replace(',','.').replace(' ','').strip(), m.group('unit'), m.group()
    #             vol = re.sub('[^A-Za-z0-9\.]+', '', m.group('digits')) #m.group('digits').replace(',','.').replace(' ','') 
    #             vol_unit, vol_str = m.group('unit').strip(), m.group()
    #             if vol_unit is not None: vol_unit = units_total_dict.get(vol_unit.strip().lower())
    #             if debug: print(f"vol_handler: {vol}: {vol}, vol_unit: {vol_unit}, vol_str: '{vol_str}'")
    #     return vol, vol_unit, vol_str

    # def is_one_number_in_string(mis_position, debug=False):
    #     rez = None
    #     mis_position_cut = re.sub(r"(?<=\s)(N|№)[\s\d+xXхХ]*\b|$", '', mis_position) # чистим от N10x1
    #     mis_position_cut = re.sub(r"(?:\d\d\.\d\d\.\d\d\d\d)|(?:\d\d\.\d\d\d\d)", '', mis_position_cut) # читстим от  06.2022г.
    #     if debug: print(f"mis_position_cut: '{mis_position_cut}'")
    #     # lst = re.findall(r"\d+,\d+|\d+\.\d+|[\d\s]+\d+|\d+",  mis_position_cut)
    #     #lst = re.findall(r"(?:(\d+,\d+)|(\d+\.\d+)|([\d\s]+\d+)|(\d+))",  mis_position_cut)
    #     #lst = re.findall(r"(?<=\w(N|№))(?:\d+,\d+)|(?:\d+\.\d+)|(?:\d+)",  mis_position_cut)
    #     lst = re.findall(r"(?:\d+[,\.]*\d*)", mis_position_cut)
    #     # if len(lst)==1: return lst[0]
    #     if len(lst)==1: rez = lst[0]
    #     else: rez = None
    #     return rez 
        
    # def post_process_doze_vol(mis_position, handler_group1, tn_ru_ext, tn_lat_ext, doze_proc_str, doze, doze_unit, doze_str, pseudo_vol, pseudo_vol_unit, vol, vol_unit, vol_str, debug=False):
    #     ptn_digits = r'(?P<digits>(\d+,\d+|\d+\.\d+|\d+))'
    #     if doze_proc_str is not None:
    #         sw = re.sub(doze_proc_str, '', mis_position )
    #     else: sw = mis_position
    #     one_number = is_one_number_in_string(sw, debug=debug) #mis_poistion
    #     if debug: print(f"post_process_doze_vol: handler_group: {handler_group1}, one_number: '{one_number}'")
    #     if debug: print(f"post_process_doze_vol: vol: {vol}, vol_unit: {vol_unit}")
    #     # if one_number is not None and doze_unit is None and pseudo_vol_unit is None and vol_unit is None:
    #     if one_number is not None:
    #         if handler_group1 in [0, 6, 8]: # если стоит одно число => это дозировка, ставим это число, в поле "ед. измер." - ставим "-"
    #             if doze_unit is None and pseudo_vol_unit is None and vol_unit is None:
    #                 # handler_numder, is_is_dosed, is_pseudo_vol, is_vol
    #                 # [0, True, False, False] # Таблетки...
    #                 # [6, True, False, False] 
    #                 # [8, False, False, False] # если есть одно число - ставим в дозировку
    #                 #if doze is None:
    #                 doze, doze_unit, doze_str, pseudo_vol, pseudo_vol_unit, vol, vol_unit, vol_str = \
    #                     re.sub('[^A-Za-z0-9\.]+', '', one_number.replace(',','.')), None, None, None, None, None, None, None
    #         elif handler_group1 in [1]: # если стоит одно число => это объем, ставим это число, в поле "ед. измер." - ставим "-"
    #             if doze_unit is None and pseudo_vol_unit is None and vol_unit is None:
    #                 # [1, True, True, True]
    #                 doze, doze_unit, doze_str, pseudo_vol, pseudo_vol_unit, vol, vol_unit, vol_str = \
    #                   None, None, None, None, None, re.sub('[^A-Za-z0-9\.]+', '', one_number.replace(',','.')), None, None
    #                 if doze_unit is not None: doze_unit = units_total_dict.get(doze_unit.strip().lower())
    #                 if pseudo_vol_unit is not None: pseudo_vol_unit = units_total_dict.get(pseudo_vol_unit.strip().lower())
    #                 if vol_unit is not None: vol_unit = units_total_dict.get(vol_unit.strip().lower())
    #         elif handler_group1 in [4]: # если стоит одно число => это объем
    #             # [4, False, False, True]
    #             if doze_unit is None and pseudo_vol_unit is None and vol_unit is None:
    #                 doze, doze_unit, doze_str, pseudo_vol, pseudo_vol_unit, vol, vol_unit, vol_str = \
    #                   None, None, None, None, None, re.sub('[^A-Za-z0-9\.]+', '', one_number.replace(',','.')), None, None
    #                 if doze_unit is not None: doze_unit = units_total_dict.get(doze_unit.strip().lower())
    #                 if pseudo_vol_unit is not None: pseudo_vol_unit = units_total_dict.get(pseudo_vol_unit.strip().lower())
    #                 if vol_unit is not None: vol_unit = units_total_dict.get(vol_unit.strip().lower())
    #         elif handler_group1 in [5,7]:
    #             if debug: 
    #                 print(f"post_process_doze_vol: handler_group1 in [5,7]")
    #                 print(f"doze, doze_unit, pseudo_vol, pseudo_vol_unit, vol, vol_unit\n", doze, doze_unit, pseudo_vol, pseudo_vol_unit, vol, vol_unit)
                
    #             if doze_unit is None and pseudo_vol_unit is None and vol_unit is None:
    #                 # [5, True, True, True]
    #                 # 1) если стоит одно число (без ед. измер дозировки и объема) - то это объем 
    #                 doze, doze_unit, doze_str, pseudo_vol, pseudo_vol_unit, vol, vol_unit, vol_str = \
    #                   None, None, None, None, None, re.sub('[^A-Za-z0-9\.]+', '', one_number.replace(',','.')), None, None
    #                 if doze_unit is not None: doze_unit = units_total_dict.get(doze_unit.strip().lower())
    #                 if pseudo_vol_unit is not None: pseudo_vol_unit = units_total_dict.get(pseudo_vol_unit.strip().lower())
    #                 if vol_unit is not None: vol_unit = units_total_dict.get(vol_unit.strip().lower())

    #                 #2) если есть дозировка + ед. измер дозировки, потом число - то это объем
    #                 # надо проверить
    #                 # если находит 2 "объема" или 2 "дозировки"???
    #                 # elif handler_group1 in [8]: 
    #             elif handler_group1 in [5]  and doze_unit is not None and pseudo_vol_unit is not None:
    #                 if debug: print(f"post_process_doze_vol: мл/мл -> мг/мл")
    #                 if doze_unit.lower() in ['ml', 'мл'] and pseudo_vol_unit.lower() in ['ml', 'мл']:
    #                     doze_unit = 'мг'
    #                 if doze_unit is not None: units_total_dict.get(doze_unit.strip().lower())
    #                 if pseudo_vol_unit is not None: pseudo_vol_unit = units_total_dict.get(pseudo_vol_unit.strip().lower())
    #                 if vol_unit is not None: vol_unit = units_total_dict.get(vol_unit.strip().lower())

        
    #     elif handler_group1 in [5]:
    #         if doze_unit is not None and pseudo_vol_unit is not None:
    #             if debug: print(f"post_process_doze_vol: мл/мл -> мг/мл")
    #             # if vol_unit.lower() in ['ml', 'мл'] and pseudo_vol_unit.lower() in ['ml', 'мл']:
    #             #     vol_unit = 'мг'
    #             if doze_unit.lower() in ['ml', 'мл'] and pseudo_vol_unit.lower() in ['ml', 'мл']:
    #                 doze_unit = 'мг'
    #             if doze_unit is not None: doze_unit = units_total_dict.get(doze_unit.strip().lower())
    #             if pseudo_vol_unit is not None: pseudo_vol_unit = units_total_dict.get(pseudo_vol_unit.strip().lower())
    #             if vol_unit is not None: vol_unit = units_total_dict.get(vol_unit.strip().lower())
    #     elif handler_group1 in [7] and doze is None:
    #           # [7, True, True, True]
    #           if vol is not None and vol_unit is not None:
    #                 # 3) если стоит объем и ЕИ объема, то просто число - это дозировка
    #               # one_number = is_one_number_in_string(re.sub(vol_str, '', mis_position), debug=False)
    #               one_number = is_one_number_in_string(re.sub(vol_str, '', sw), debug=False)
    #               if one_number is not None:
    #                   #doze = one_number.replace(',','.').strip()
    #                   doze = re.sub('[^A-Za-z0-9\.]+', '', one_number.replace(',','.'))
    #     elif handler_group1 in [6]:
    #         if doze_unit is not None and pseudo_vol_unit is not None and \
    #             doze_unit in ('мг', 'мкг', 'mg', 'mkg', 'МЕ', 'ME') and pseudo_vol_unit in ('доза', 'доз', 'doza', 'doz', 'dosa', 'dos', 'd.', 'd'):
    #             ptn_digits = r'(?P<digits>(\d+,\d+)|(\d+\.\d+)|(\d+))'
    #             ptn_str = r"(?:" + ptn_digits + r")\s*" +\
    #                 r"(?P<unit>" +  "|".join(['(?:' + p + r")" for p in ('доза', 'доз', 'doza', 'doz', 'dosa', 'dos', 'd.', 'd')]) + r")\.*,*(\s*|$)" 
    #             vol, vol_unit, vol_str = vol_handler (handler_group1, ptn_str, mis_position, tn_ru_ext, tn_lat_ext, doze_str, debug=debug)
    #         elif doze is None and doze_unit is None:
    #             local_units = [('мг', 'мкг', 'mg', 'mkg', 'МЕ', 'ME', 'мл', 'ml'), ('доза', 'доз', 'doza', 'doz', 'dosa', 'dos', 'd.', 'd')] 
    #             ptns_lst_pre = list(itertools.product(*local_units))
    #             ptns_lst = [i[0]+'/'+ i[1]  for i in ptns_lst_pre]
    #             special_doze_ptn_str = make_doze_ptn_str(ptns_lst)
    #             # print(special_doze_ptn_str)
    #             doze_proc, doze_proc_str, doze, doze_unit, doze_str, pseudo_vol, pseudo_vol_unit = \
    #                    doze_handler (handler_group1, sw, is_special_doze=True, special_doze_ptn_str=special_doze_ptn_str, debug=debug)
    #             special_vol_ptn_str = make_vol_ptn_str(['доза', 'доз', 'doza', 'doz', 'dosa', 'dos', 'd.', 'd'])
    #             vol, vol_unit, vol_str = \
    #                 vol_handler (handler_group1, special_vol_ptn_str, mis_position, tn_ru_ext, tn_lat_ext, doze_str, debug=debug)
        
    #     elif handler_group1 in [8] :
    #         if vol is None and doze is not None and doze_unit is not None:
    #             # 2) если есть дозировка + ЕИ дозировки, потом число - то это объем, 
    #             one_number = is_one_number_in_string(re.sub(doze_str, '', sw), debug=False)
    #             if one_number is not None:
    #                 # vol = one_number.replace(',','.').strip()
    #                 vol = re.sub('[^A-Za-z0-9\.]+', '', one_number.replace(',','.'))
                
    #         if doze is None and vol is not None and vol_unit is not None:
    #             # 3) если стоит объем и ЕИ объема, то просто число - это дозировка
    #             one_number = is_one_number_in_string(re.sub(vol_str, '', sw), debug=False)
    #             if one_number is not None:
    #                 # doze = one_number.replace(',','.').strip()
    #                 doze = re.sub('[^A-Za-z0-9\.]+', '', one_number.replace(',','.'))

    #     return doze, doze_unit, doze_str, pseudo_vol, pseudo_vol_unit, vol, vol_unit, vol_str

    # def extract_doze_vol_02(mis_position, tn_ru_ext, tn_lat_ext, pharm_form_unify, pharm_form, debug=False):
    #     # global doze_units_groups, vol_units_groups, doze_vol_handler_types, doze_vol_pharm_form_handlers
    #     handler_group, doze_proc, doze, doze_unit, doze_str, pseudo_vol, pseudo_vol_unit, vol, vol_unit, vol_str = \
    #     None, None, None, None, None, None, None, None, None, None
    #     doze_proc_str = None
    #     complex_doze_list, complex_doze_str = None, None
    #     if pharm_form_unify is None: pharm_form_unify = 'ph_f_undefined'
    #     if doze_vol_pharm_form_handlers.get(pharm_form_unify) is not None:
    #         handler_group, is_dosed, is_pseudo_vol, is_vol, is_proc_dozed = doze_vol_pharm_form_handlers[pharm_form_unify]
    #         if debug: print(pharm_form_unify, "-->", handler_group, is_dosed, is_pseudo_vol, is_vol)
            
    #         if is_dosed: 
    #             doze_proc, doze_proc_str, doze, doze_unit, doze_str, pseudo_vol, pseudo_vol_unit = \
    #                 doze_handler (handler_group, mis_position, debug=debug)
                    
    #             if debug: 
    #                 print("extract_doze_vol_02: doze_proc, doze_proc_str, doze, doze_unit, doze_str, pseudo_vol, pseudo_vol_unit\n",
    #                       doze_proc, doze_proc_str, doze, doze_unit, doze_str, pseudo_vol, pseudo_vol_unit)
    #         #if is_pseudo_vol: pseudo_vol, pseudo_vol_unit, pseudo_vol_str = pseudo_vol_handler (handler_group)
    #         if is_vol: 
    #             ptn_str = vol_units_groups[handler_group].get('ptn_str')
    #             vol, vol_unit, vol_str = \
    #                 vol_handler (handler_group, ptn_str, mis_position, tn_ru_ext, tn_lat_ext, doze_str, debug=debug)
            
    #         doze, doze_unit, doze_str, pseudo_vol, pseudo_vol_unit, vol, vol_unit, vol_str=\
    #         post_process_doze_vol(mis_position, handler_group, tn_ru_ext, tn_lat_ext, doze_proc_str, doze, doze_unit, doze_str, pseudo_vol, pseudo_vol_unit, vol, vol_unit, vol_str, debug=debug)
            
    #         if is_dosed:
    #             complex_doze_list, complex_doze_str = complex_doze_handler(handler_group, mis_position, doze_str, debug=debug)
    #         else: complex_doze_list, complex_doze_str = None, None

    #     else: pass #return doze, doze_unit, doze_str, pseudo_vol, pseudo_vol_unit, vol, vol_unit, vol_str
    #     # if debug: print(f"Extract_doze_vol: doze_group: {handler_group}, doze: {doze}, doze_unit: {doze_unit}, pseudo_vol: {pseudo_vol}, pseudo_vol_unit:{pseudo_vol_unit}, vol: {vol}, vol_unit: {vol_unit}")
    
    #     return handler_group, doze_proc, doze, doze_unit, doze_str, pseudo_vol, pseudo_vol_unit, complex_doze_list, complex_doze_str, vol, vol_unit, vol_str
    pass    

def extract_pack_form(mis_position_unparsed, debug=False )->str:
    # pack_form_unify, pack_form, pack_position = '#Н/Д', '#Н/Д', -1
    pack_form_unify, pack_form, pack_position = None, None, -1
    
    for i, pack_form_type in enumerate(pack_form_types_list): 
        srch_form = re.search(pack_form_pttn_list[i], mis_position_unparsed, flags=re.I)
        # if debug: print(pack_form_type, srch_form)
        if srch_form:
            pack_form = srch_form.group()
            pack_form_unify = pack_form_type
            pack_position = mis_position_unparsed.find(pack_form)
            break

    return pack_form_unify, pack_form, pack_position

def extract_n_packs(mis_position, debug=False):
    pack_1_num, pack_2_num, n_packs_str = None, None, None
    ptn_packs = r"\s(?P<n>(N|№)\s*[\d+xXхХ\*]+)\b|$"
    ptn_packs_digits = r"(?P<pack1_num>\d+)[xXхХ\*]*(?P<pack2_num>\d+)*"
    m = re.search(ptn_packs, mis_position, flags = re.I)
    if m is not None:
        n_packs_str = m.group()
        m_digits = re.search(ptn_packs_digits, n_packs_str, flags = re.I)
        if debug: print(f"extract_n_packs: m_digits: {m_digits}")
        if m_digits is not None:
            if debug: print(m_digits.groupdict())
            pack_1_num, pack_2_num = m_digits.group('pack1_num'), m_digits.group('pack2_num')

    return pack_1_num, pack_2_num, n_packs_str

def extract_n_packs_00(mis_position, debug=False):
    pack_1_num, pack_2_num, n_packs_str = None, None, None
    ptn_packs = r"\s(N|№)\s*[\d+xXхХ\*]*\b|$"
    ptn_packs_digits = r"(?P<pack1_num>\d+)[xXхХ\*]*(?P<pack2_num>\d+)*"
    m = re.search(ptn_packs, mis_position, flags = re.I)
    if m is not None:
        n_packs_str = m.group()
        m_digits = re.search(ptn_packs_digits, n_packs_str, flags = re.I)
        if m_digits is not None:
            if debug: print(m_digits.groupdict())
            pack_1_num, pack_2_num = m_digits.group('pack1_num'), m_digits.group('pack2_num')

    return pack_1_num, pack_2_num, n_packs_str

def extract_n_packs_00(mis_position, debug=False):
    pack_1_num, pack_2_num, n_packs_str = None, None, None
    ptn_packs = r"(N|№)\s*[\d+xXхХ\*]*\b|$"
    ptn_packs_digits = r"(?P<pack1_num>\d+)[xXхХ\*]*(?P<pack2_num>\d+)*"
    m = re.search(ptn_packs, mis_position, flags = re.I)
    if m is not None:
        n_packs_str = m.group()
        m_digits = re.search(ptn_packs_digits, n_packs_str, flags = re.I)
        if m_digits is not None:
            if debug: print(m_digits.groupdict())
            pack_1_num, pack_2_num = m_digits.group('pack1_num'), m_digits.group('pack2_num')

    return pack_1_num, pack_2_num, n_packs_str

def extract_packs(mis_position, debug=False):
    pack_1_form_unify, pack_1_form, pack_1_num, pack_2_form_unify, pack_2_form, pack_2_num = None, None, None, None, None, None
    
    pack_1_form_unify, pack_1_form, pack_position_01 = extract_pack_form(mis_position, debug=debug)
    if pack_1_form is not None:  # == pack_position_01 > -1
        pack_form_unify_02, pack_form_02, pack_position_02 = extract_pack_form(re.sub(pack_1_form, '', mis_position), debug=debug)
        if pack_form_02 is not None:
            if pack_position_02 > -1:
                if pack_position_02 < pack_position_01:
                    pack_2_form_unify, pack_2_form = pack_1_form_unify, pack_1_form
                    # меняем местами если похиция второй найденной pack формы  меньше 1-ой
                    pack_1_form_unify, pack_1_form = pack_form_unify_02, pack_form_02
                else:
                    pack_2_form_unify, pack_2_form = pack_form_unify_02, pack_form_02
            else: # НИ чего не нашли
                pass
        else: # НИ чего не нашли - страхуемся
                pass

    pack_1_num, pack_2_num, n_packs_str = extract_n_packs(mis_position, debug=debug)
    

    return pack_1_form_unify, pack_1_form,  pack_1_num, pack_2_form_unify, pack_2_form, pack_2_num, n_packs_str

def calc_consumer_total(pack_1_num, pack_2_num, debug = False ):
    consumer_total_parsing = None
    if pack_1_num is None and pack_2_num is None:  consumer_total_parsing = 1
    # elif pack_1_num is not None and pack_2_num is None: consumer_total_parsing = int(pack_1_num) # ? float
    # elif pack_1_num is None and pack_2_num is not None: consumer_total_parsing = int(pack_2_num) # ? float
    # else: consumer_total_parsing = int(pack_1_num) * int(pack_2_num) 
    elif pack_1_num is not None and pack_2_num is None: consumer_total_parsing = float(pack_1_num)
    elif pack_1_num is None and pack_2_num is not None: consumer_total_parsing = float(pack_2_num)
    else: consumer_total_parsing = float(pack_1_num) * float(pack_2_num) 
    return consumer_total_parsing 



    # klp_srch_list_columns = [ 'code_klp', 'mnn_standard', 'code_smnn', 'trade_name', 'trade_name','form_standard_unify', 
    #                          'lim_price_barcode_str', 'num_reg',
    #                           'lf_norm_name', 'dosage_norm_name']
    # klp_srch_list = klp_list_dict_df[klp_srch_list_columns].values
    # code_klp_id, mnn_standard_id, code_smnn_id, trade_name_id, trade_name_capitalize_id, \
    # form_standard_unify_id, lim_price_barcode_str_id, num_reg_id, lf_norm_name_id, dosage_norm_name_id = [0,1,2,3,4,5,6,7,8,9]
    # print(code_klp_id, mnn_standard_id, code_smnn_id, trade_name_id, trade_name_capitalize_id, 
    # form_standard_unify_id, lim_price_barcode_str_id, num_reg_id, lf_norm_name_id, dosage_norm_name_id)

    # for r in klp_srch_list:
    #    r[trade_name_capitalize_id] = r[trade_name_id].capitalize()    
    
def np_unique_nan(lst: np.array, debug = False)->np.array: # a la version 2.4
    lst_unique = None
    if lst is None or (((type(lst)==float) or (type(lst)==np.float64)) and np.isnan(lst)):
        # if debug: print('np_unique_nan:','lst is None or (((type(lst)==float) or (type(lst)==np.float64)) and math.isnan(lst))')
        lst_unique = lst
    else:
        data_types_set = list(set([type(i) for i in lst]))
        if debug: print('np_unique_nan:', 'lst:', lst, 'data_types_set:', data_types_set)
        if ((type(lst)==list) or (type(lst)==np.ndarray)):
            if debug: print('np_unique_nan:','if ((type(lst)==list) or (type(lst)==np.ndarray)):')
            if len(data_types_set) > 1: # несколько типов данных
                if list not in data_types_set and dict not in data_types_set and tuple not in data_types_set and type(None) not in data_types_set:
                    lst_unique = np.array(list(set(lst)), dtype=object)
                else:
                    lst_unique = lst
            elif len(data_types_set) == 1:
                if debug: print("np_unique_nan: elif len(data_types_set) == 1:")
                if list in data_types_set:
                    lst_unique = np.unique(np.array(lst, dtype=object))
                elif  np.ndarray in data_types_set:
                    # print('elif  np.ndarray in data_types_set :')
                    lst_unique = np.unique(lst.astype(object))
                    # lst_unique = np_unique_nan(lst_unique)
                    lst_unique = np.asarray(lst, dtype = object)
                    # lst_unique = np.unique(lst_unique)
                elif type(None) in data_types_set:
                    # lst_unique = np.array(list(set(lst)))
                    lst_unique = np.array(list(set(list(lst))))
                elif dict in  data_types_set:
                    lst_unique = lst
                    # np.unique(lst)
                elif type(lst) == np.ndarray:
                    if debug: print("np_unique_nan: type(lst) == np.ndarray")
                    if (lst.dtype.kind == 'f') or  (lst.dtype == np.float64) or  (float in data_types_set):
                        if debug: print("np_unique_nan: (lst.dtype.kind == 'f')")
                        lst_unique = np.unique(lst.astype(float))
                        # if debug: print("np_unique_nan: lst_unique predfinal:", lst_unique)
                        # lst_unique = np.array(list(set(list(lst))))
                        # if debug: print("np_unique_nan: lst_unique predfinal v2:", lst_unique)
                        # if np.isnan(lst).all():
                        #     lst_unique = np.nan
                        #     if debug: print("np_unique_nan: lst_unique predfinal v3:", lst_unique)
                    elif (lst.dtype.kind == 'S') :
                        if debug: print("np_unique_nan: lst.dtype == string")
                        lst_unique = np.array(list(set(list(lst))))
                        if debug: print(f"np_unique_nan: lst_unique 0: {lst_unique}")
                    elif lst.dtype == object:
                        if debug: print("np_unique_nan: lst.dtype == object")
                        if (type(lst[0])==str) or (type(lst[0])==np.str_) :
                            try:
                                lst_unique = np.unique(lst)
                            except Exception as err:
                                lst_unique = np.array(list(set(list(lst))))
                        else:
                            lst_unique = np.array(list(set(list(lst))))
                        if debug: print(f"np_unique_nan: lst_unique 0: {lst_unique}")
                    else:
                        if debug: print("np_unique_nan: else 0")
                        lst_unique = np.unique(lst)
                else:
                    if debug: print('np_unique_nan:','else i...')
                    lst_unique = np.array(list(set(lst)))
                    
            elif len(data_types_set) == 0:
                lst_unique = None
            else:
                # print('else')
                lst_unique = np.array(list(set(lst)))
        else: # другой тип данных
            if debug: print('np_unique_nan:','другой тип данных')
            # lst_unique = np.unique(np.array(list(set(lst)),dtype=object))
            # lst_unique = np.unique(np.array(list(set(lst)))) # Исходим из того что все елеменыт спсика одного типа
            lst_unique = lst
    if type(lst_unique) == np.ndarray:
        if debug: print('np_unique_nan: final: ', "if type(lst_unique) == np.ndarray")
        if lst_unique.shape[0]==1: 
            if debug: print('np_unique_nan: final: ', "lst_unique.shape[0]==1")
            lst_unique = lst_unique[0]
            if debug: print(f"np_unique_nan: final after: lst_unique: {lst_unique}")
            if (type(lst_unique) == np.ndarray) and (lst_unique.shape[0]==1):  # двойная вложенность
                if debug: print('np_unique_nan: final: ', 'one more', "lst_unique.shape[0]==1")
                lst_unique = lst_unique[0]
        elif lst_unique.shape[0]==0: lst_unique = None
    if debug: print(f"np_unique_nan: return: lst_unique: {lst_unique}")
    if debug: print(f"np_unique_nan: return: type(lst_unique): {type(lst_unique)}")
    return lst_unique

def np_unique_nan_01a(lst: np.array, debug = False)->np.array: # a la version 2.4
    lst_unique = None
    if lst is None or (((type(lst)==float) or (type(lst)==np.float64)) and np.isnan(lst)):
        # if debug: print('np_unique_nan:','lst is None or (((type(lst)==float) or (type(lst)==np.float64)) and math.isnan(lst))')
        lst_unique = lst
    else:
        data_types_set = list(set([type(i) for i in lst]))
        if debug: print('np_unique_nan:', 'lst:', lst, 'data_types_set:', data_types_set)
        if ((type(lst)==list) or (type(lst)==np.ndarray)):
            if debug: print('np_unique_nan:','if ((type(lst)==list) or (type(lst)==np.ndarray)):')
            if len(data_types_set) > 1: # несколько типов данных
                if list not in data_types_set and dict not in data_types_set and tuple not in data_types_set and type(None) not in data_types_set:
                    lst_unique = np.array(list(set(lst)), dtype=object)
                else:
                    lst_unique = lst
            elif len(data_types_set) == 1:
                if debug: print("np_unique_nan: elif len(data_types_set) == 1:")
                if list in data_types_set:
                    lst_unique = np.unique(np.array(lst, dtype=object))
                elif  np.ndarray in data_types_set:
                    # print('elif  np.ndarray in data_types_set :')
                    lst_unique = np.unique(lst.astype(object))
                    # lst_unique = np_unique_nan(lst_unique)
                    lst_unique = np.asarray(lst, dtype = object)
                    # lst_unique = np.unique(lst_unique)
                elif type(None) in data_types_set:
                    # lst_unique = np.array(list(set(lst)))
                    lst_unique = np.array(list(set(list(lst))))
                elif dict in  data_types_set:
                    lst_unique = lst
                    # np.unique(lst)
                elif type(lst) == np.ndarray:
                    if debug: print("np_unique_nan: type(lst) == np.ndarray")
                    if (lst.dtype.kind == 'f') or  (lst.dtype == np.float64) or  (float in data_types_set):
                        if debug: print("np_unique_nan: (lst.dtype.kind == 'f')")
                        lst_unique = np.unique(lst.astype(float))
                        # if debug: print("np_unique_nan: lst_unique predfinal:", lst_unique)
                        # lst_unique = np.array(list(set(list(lst))))
                        # if debug: print("np_unique_nan: lst_unique predfinal v2:", lst_unique)
                        # if np.isnan(lst).all():
                        #     lst_unique = np.nan
                        #     if debug: print("np_unique_nan: lst_unique predfinal v3:", lst_unique)
                    elif (lst.dtype.kind == 'S') :
                        if debug: print("np_unique_nan: lst.dtype == string")
                        lst_unique = np.array(list(set(list(lst))))
                        if debug: print(f"np_unique_nan: lst_unique 0: {lst_unique}")
                    elif lst.dtype == object:
                        if debug: print("np_unique_nan: lst.dtype == object")
                        lst_unique = np.array(list(set(list(lst))))
                        if debug: print(f"np_unique_nan: lst_unique 0: {lst_unique}")
                    else:
                        if debug: print("np_unique_nan: else 0")
                        lst_unique = np.unique(lst)
                else:
                    if debug: print('np_unique_nan:','else i...')
                    lst_unique = np.array(list(set(lst)))
                    
            elif len(data_types_set) == 0:
                lst_unique = None
            else:
                # print('else')
                lst_unique = np.array(list(set(lst)))
        else: # другой тип данных
            if debug: print('np_unique_nan:','другой тип данных')
            # lst_unique = np.unique(np.array(list(set(lst)),dtype=object))
            # lst_unique = np.unique(np.array(list(set(lst)))) # Исходим из того что все елеменыт спсика одного типа
            lst_unique = lst
    if type(lst_unique) == np.ndarray:
        if debug: print('np_unique_nan: final: ', "if type(lst_unique) == np.ndarray")
        if lst_unique.shape[0]==1: 
            if debug: print('np_unique_nan: final: ', "lst_unique.shape[0]==1")
            lst_unique = lst_unique[0]
            if debug: print(f"np_unique_nan: final after: lst_unique: {lst_unique}")
            if (type(lst_unique) == np.ndarray) and (lst_unique.shape[0]==1):  # двойная вложенность
                if debug: print('np_unique_nan: final: ', 'one more', "lst_unique.shape[0]==1")
                lst_unique = lst_unique[0]
        elif lst_unique.shape[0]==0: lst_unique = None
    if debug: print(f"np_unique_nan: return: lst_unique: {lst_unique}")
    if debug: print(f"np_unique_nan: return: type(lst_unique): {type(lst_unique)}")
    return lst_unique

def to_float(value):
    #обсобенность [nan, 10, None] переводит [10. nan] т.е частично делает unique
    float_value = None
    if ((type(value)==str) or (type(value)==np.str_)): # основной сценарий
        try:
            float_value = float(value)
        except:
            float_value = value 
    elif ((type(value)==list) or (type(value)==np.ndarray)):
        # print("elif ((type(value)==list) or (type(value)==np.ndarray))")
        float_value = []
        for v in value:
            # if v is not None and not (((type(v)==float) or (type(v)== np.float64)) and np.isnan(v)):
            if v is not None:
                try:
                    float_value.append(float(v))
                except:
                    float_value.append(v)
            else: float_value.append(np.nan)
        # print("float_value: step 1", float_value)
        # data_types_set = list(set([type(i) for i in value]))
        data_types_set2 = list(set([type(i) for i in float_value]))
        if len(data_types_set2) > 1: # несколько типов данных
            float_value = np.array(float_value, dtype = object)
        elif len(data_types_set2) == 1: # один тип данных
            float_value = np.array(float_value)
        else: 
            float_value = None
    else:
        try:
            float_value = float(value)
        except:
            float_value = value # пока так чтобы не попортить

    return float_value   

    #   if code_klp_lst is not None and ((type(code_klp_lst)==np.ndarray) or ((type(code_klp_lst)==list))) and  len(code_klp_lst)>0:
    #     # if code_klp_lst is not None and ((type(code_klp_lst)==np.ndarray) and  (code_klp_lst.shape[0] > 0)):
    #         # srch_list = '|'.join([r"(?:" + code_klp + r")" for code_klp in code_klp_lst])
    #         # bar_code_srch_list = ' or '. join([f"'{bar_code}' in lim_price_barcode_str" for bar_code in bar_code_list])
    #         # return_values_pre = klp_list_dict_df[klp_list_dict_df['code_klp'].str.contains(srch_list, regex=True)][return_values_cols_list].values
    #         query_str = ' or '. join([f"code_klp == '{code_klp}'" for code_klp in code_klp_lst])
    #         # query_str = f"code_klp == {code_klp_lst}"
    #         # ValueError: multi-line expressions are only valid in the context of data, use DataFrame.eval
    #         if debug: print(f"select_klp_by_code_klp: query_str: '{query_str}'")
    #         return_values_pre = klp_list_dict_df.query(query_str)[return_values_cols_list].values
    #         if debug: print(f"select_klp_by_code_klp: step1: return_values_pre.shape", return_values_pre.shape, return_values_pre )
    #         return_values = []
    #         for i in range(n_cols):
    #             # lst = np_unique_nan_wrapper(return_values_pre[:,i])
    #             lst = np_unique_nan(return_values_pre[:,i], debug=debug)
    #             return_values.append(lst)
    #             if debug: print(f"select_klp_by_code_klp: i: {i}, lst.dtype.kind: {lst.dtype.kind}, {lst.dtype},  lst: {lst}")

def select_cols_values_from_smnn(cols_srch, cols_return_lst, cols_check_duplicates, check_col_names=False, debug=True):
    return_values, num_records = None, 0
    if type(cols_return_lst)==list and type(cols_srch)==dict: 
        cols_srch_lst = list(cols_srch.keys())
        if check_col_names and not(set(cols_srch_lst + cols_return_lst).issubset(list(smnn_list_df.columns))):
            if debug: print("select_cols_values_from_smnn: any return cols not in smnn_list_df.columns")
            return return_values, num_records
        #for k,v in cols_srch.items()
        if check_col_names and not(set(cols_srch_lst + cols_return_lst).issubset(list(smnn_list_df.columns))):
            if debug: print("select_cols_values_from_smnn: any return cols not in smnn_list_df.columns")
            return return_values, num_records
    else: 
        if debug: print("select_cols_values_from_smnn: wrong format of cols_srch, cols_return_lst")
        return return_values, num_records
    if debug: print("select_cols_values_from_smnn: cols_srch: "); pprint(cols_srch)
    #mask_srch_lst = [(smnn_list_df[k].str.contains(v['ptn'][0] + v['s_srch'] + v['ptn'][1], flags=v['flags'], regex = True)) for k,v in cols_srch.items()]
    # try: 
    #mask_srch_lst = [smnn_list_df[k].str.contains(v['ptn'][0]  + v['s_srch'] + v['ptn'][1], flags=v['flags'], regex = v['regex'])
    mask_srch_lst = [smnn_list_df[k].str.contains( v['s_srch'], flags=v['flags'], regex = v['regex'])\
                                            if v['s_srch'] is not None else smnn_list_df[k].isnull() \
                                            for k,v in cols_srch.items()]
    for i, m in enumerate(mask_srch_lst):
        if i == 0: mask_srch = m
        else:  mask_srch = mask_srch & m
    #df = smnn_list_df[mask_srch]
    # df_dd = smnn_list_df[mask_srch].drop_duplicates(subset=cols_check_duplicates)[cols_return_lst]
    df_dd = smnn_list_df[mask_srch][cols_return_lst]
    num_records = df_dd.shape[0]
    # if debug: display(df_dd)
    #cols_return_lst
    #return_values = df_dd.values.T
    return_values = list(df_dd.values.T)
    # return_values = df_dd.values.T
    if debug: print( return_values)
    for i, rv in enumerate(return_values):
        if len(rv)==1: return_values[i] = rv[0]
        else: 
            # w_value = list(np.unique(rv))
            # w_value = np_unique_nan_ext(rv)
            w_value = np_unique_nan(rv)
            # ??????
            if len(w_value)==1: w_value = w_value[0]
            # array([list(['B05CB01', 'B05XA03', 'V07AB']), list(['~', 'B05CB01'])],dtype=object)
            # if type(w_value)== np.ndarray:
            #     w_value = np.asarray(w_value).reshape(-1)
            return_values[i] = w_value
    # except Exception as err: 
    #     print("ERROR: select_cols_values_from_smnn:")
    #     print(err)
    #     print(f"cols_return_lst: {cols_return_lst}, cols_check_duplicates: {cols_check_duplicates}")
    #     print(f"cols_srch.items(): '{cols_srch.items}'")
    #     # pprint(cols_srch)
        
    return return_values, num_records

def select_klp_mnn_by_tn__pharm_form_type(trade_name, pharm_form_type, strict_select = False, debug=False):
    # 9 сек на 200 записей входного файла
    if debug: print(trade_name, pharm_form_type)
    mnn_lst, code_smnn_lst, num_records = None, None, 0
    if trade_name is None: return mnn_lst, code_smnn_lst, num_records
    
    mask_pharm_form_srch = klp_srch_list[:,form_standard_unify_id]==pharm_form_type
    if strict_select: 
        mask_tn_srch = klp_srch_list[:,trade_name_id]==trade_name
        # mask_tn_srch = klp_srch_list[:,trade_name_capitalize_id]==trade_name.capitalize()
    else:  
        mask_tn_srch = klp_srch_list[:,trade_name_capitalize_id]==trade_name.capitalize()
    
    
    trade_name_klp_lst = klp_srch_list[mask_tn_srch & mask_pharm_form_srch]
    num_records = len(trade_name_klp_lst)
    if debug: print("select_klp_mnn_by_tn__pharm_form_type: trade_name_klp_lst, len(trade_name_klp_lst), num_records:", len(trade_name_klp_lst), num_records) #, trade_name_klp_lst)

    if num_records == 0 or trade_name_klp_lst is None: 
        if debug: print("select_klp_mnn_by_tn__pharm_form_type: if num_records == 0 or trade_name_klp_lst is None")
        return mnn_lst, code_smnn_lst, num_records
    # elif num_records == 1: 
    #     mnn = trade_name_klp_lst[0, mnn_standard_id]
    #     code_smnn = trade_name_klp_lst[0, code_smnn_is]
    else: 
        #mnn_lst = np_unique_nan_wrapper(trade_name_klp_lst[:, mnn_standard_id])
        # mnn_lst = np_unique_nan(trade_name_klp_lst[:, mnn_standard_id])
        mnn_lst = np_unique_nan(trade_name_klp_lst[:, mnn_standard_id])
        # if mnn_lst.shape[0]>1:
        #     code_smnn_lst = np.array([np.array([code_smnn for mnn_l in mnn_lst if mnn_l==mnn]) for mnn, code_smnn in trade_name_klp_lst[:, [mnn_standard_id, code_smnn_id] ]])
        #     code_smnn_lst = np_unique_nan(code_smnn_lst)
        #     #code_smnn_lst = np.asarray([c for c in code_smnn_lst if not math.isnan(c)])
        # else: code_smnn_lst = np.asarray([trade_name_klp_lst[0, code_smnn_id]])
        code_smnn_lst = np_unique_nan(trade_name_klp_lst[:, code_smnn_id]) # нет целостности не по всем кодам есть записи в SMNN 
        
    if debug: print(f"select_klp_mnn_by_tn__pharm_form_type: num_records: {num_records}")
    if debug: print(f"select_klp_mnn_by_tn__pharm_form_type: mnn_lst: {mnn_lst}") #, trade_name_klp_lst[:, mnn_standard_id])
    if debug: print(f"select_klp_mnn_by_tn__pharm_form_type: code_smnn_lst: {code_smnn_lst}") #, trade_name_klp_lst[:, code_smnn_id])
    return mnn_lst, code_smnn_lst, num_records

    #   if code_klp_lst is not None and ((type(code_klp_lst)==np.ndarray) or ((type(code_klp_lst)==list))) and  len(code_klp_lst)>0:
    #         query_str = ' or '. join([f"code_klp == '{code_klp}'" for code_klp in code_klp_lst])
    #         # query_str = f"code_klp == {code_klp_lst}"
    #         # ValueError: multi-line expressions are only valid in the context of data, use DataFrame.eval
    #         if debug: print(f"select_klp_by_code_klp: query_str: '{query_str}'")
    #         return_values_pre = klp_list_dict_df.query(query_str)[return_values_cols_list].values
    #         if debug: print(f"select_klp_by_code_klp: step1: return_values_pre.shape", return_values_pre.shape, return_values_pre )
    #         return_values = []
    #         for i in range(n_cols):
    #             # lst = np_unique_nan_wrapper(return_values_pre[:,i])
    #             lst = np_unique_nan(return_values_pre[:,i], debug=debug)
    #             return_values.append(lst)
    #             if debug: print(f"select_klp_by_code_klp: i: {i}, lst.dtype.kind: {lst.dtype.kind}, {lst.dtype},  lst: {lst}")

def select_cols_values_from_esklp_by_tn(tn, cols_return_lst = ['mnn_standard'], strict_select = True, check_col_names=False, debug=False):
    # 30 сек на 200 записей входного файла
    #if debug: print("debug")
    cols_d = ['mnn_standard']
    if check_col_names and not(type(cols_return_lst)==list and  set(cols_return_lst).issubset(list(klp_list_dict_df.columns))):
        print("any return cols not in klp_list_df.columns")
        return None, 0
    n_cols = len(cols_return_lst)
    return_values, num_records = np.array(n_cols * [None]), 0
    if tn is None: return return_values, num_records
    # try:
    #     # tn_esc = re.escape(tn)
    #     tn_esc = tn
    # except Exception as err:
    #     print(f"--> {tn}")
    #     print(err); print()
    # if strict_select: 
        # s_srch = r"(?<!.)" + tn_esc + r"(?!.+)"
    #     query_str = f"trade_name == '{tn_esc}'"
    # else:  
    #     # s_srch = r"^(?:" + tn_esc + r").*$"
    #     query_str = f"trade_name == '{tn_esc}'"
    tn_esc = tn
    query_str = f"trade_name == '{tn_esc}'"
    try:
        # dd_df_tn = klp_list_dict_df[(klp_list_dict_df['trade_name'].str.contains(s_srch, case =False, flags=re.I, regex = True))]\
        #   .drop_duplicates(subset=cols_return_lst) [cols_return_lst]
          # .drop_duplicates(subset=cols_d) [cols_return_lst] (тянуло не все)
        return_values_pre = klp_list_dict_df.query(query_str)[cols_return_lst].values
        num_records = return_values_pre.shape[0]
    except Exception as err: 
        # print(f"tn: '{tn}' -> {s_srch}")
        print(f"tn: '{tn}' -> query_str: {query_str}")
        print(err); print()
        return return_values, num_records
    
    if num_records == 0: return_values = np.array(n_cols * [None])

    else: 
        if debug: print(f"select_cols_values_from_esklp_by_tn: step1: return_values_pre.shape", return_values_pre.shape, return_values_pre )
        return_values = []
        for i in range(n_cols):
            # lst = np_unique_nan_wrapper(return_values_pre[:,i])
            lst = np_unique_nan(return_values_pre[:,i]) #, debug=debug)
            return_values.append(lst)
            if debug: print(f"select_klp_by_code_klp: i: {i}, lst.dtype.kind: {lst.dtype.kind}, {lst.dtype},  lst: {lst}")
        
        return_values = np.array(return_values, dtype=object)
        # return_values = return_values_pre # для проверки быстродействия
    # else: return_values = np.array(n_cols * [None])
                
    if debug: print(f"select_cols_values_from_esklp_by_tn(): num_records(): {num_records}")
    if debug: print(f"select_cols_values_from_esklp_by_tn(): return_values: {return_values}")
    return return_values, num_records

def select_cols_values_from_esklp_by_tn_00(tn, cols_return_lst = ['mnn_standard'], strict_select = True, check_col_names=False, debug=False):
    # 30 сек на 200 записей входного файла
    #if debug: print("debug")
    cols_d = ['mnn_standard']
    if check_col_names and not(type(cols_return_lst)==list and  set(cols_return_lst).issubset(list(klp_list_dict_df.columns))):
        print("any return cols not in klp_list_df.columns")
        return None, 0
    return_values, num_records = [], 0
    if tn is None: return return_values, num_records
    try:
        tn_esc = re.escape(tn)
    except Exception as err:
        print(f"--> {tn}")
        print(err); print()
    if strict_select: s_srch = r"(?<!.)" + tn_esc + r"(?!.+)"
    else:  s_srch = r"^(?:" + tn_esc + r").*$"
    try:
        dd_df_tn = klp_list_dict_df[(klp_list_dict_df['trade_name'].str.contains(s_srch, case =False, flags=re.I, regex = True))]\
          .drop_duplicates(subset=cols_return_lst) [cols_return_lst]
          # .drop_duplicates(subset=cols_d) [cols_return_lst] (тянуло не все)
        num_records = dd_df_tn.shape[0]
    except Exception as err: 
        print(f"tn: '{tn}' -> {s_srch}")
        print(err); print()
        return return_values, num_records
    
    if num_records == 0: return_values = []
    elif num_records == 1: 
        if len(cols_return_lst)==1:
            return_values = dd_df_tn[cols_return_lst].values[0][0]
        elif len(cols_return_lst)>1:
            #return_values = list(dd_df_tn[cols_return_lst].values[0])
            #pd_values = dd_df_tn[cols_return_lst].values[0]
            #return_values = pd_values.T
            return_values = dd_df_tn[cols_return_lst].values[0]
    else: 
        #return_values = [list(lst) for lst in  pd_values] 
        #return_values = pd_values.reshape(pd_values.shape[1], pd_values.shape[0])
        pd_values = dd_df_tn[cols_return_lst].values
        return_values = pd_values.T
        #return_values = dd_df_tn[cols_return_lst].values
                
    if debug: print(f"select_cols_values_from_esklp_by_tn(): num_records(): {num_records}")
    if debug: print(f"select_cols_values_from_esklp_by_tn(): return_values: {return_values}")
    return return_values, num_records

def def_tn_ru_orig(tn_lat_ext, tn_lat, debug= False):
    tn_ru_orig, mnn_orig = None, None
    if tn_lat_ext is not None:
        tn_ru_orig_dict = dict__tn_lat_ext__tn_ru_orig.get(tn_lat_ext.capitalize())
        if tn_ru_orig_dict is not None and tn_ru_orig_dict['num_positions']==1:
            if debug: print(type(tn_ru_orig_dict["positions"]), tn_ru_orig_dict.keys(), tn_ru_orig_dict["positions"])
            #tn_ru_orig = tn_ru_orig_dict["positions"] [0]['tn_ru_orig']
            #mnn_orig = tn_ru_orig_dict["positions"][0] ['МНН']
            tn_ru_orig_lst = tn_ru_orig_dict["positions"]
            if tn_ru_orig_lst is not None:
                tn_ru_orig = tn_ru_orig_lst[0]['tn_ru_orig']
                mnn_orig = tn_ru_orig_lst[0]['МНН']
            else: tn_ru_orig, mnn_orig = None, None
        else:
            """
            #tn_ru_orig = np.array(tn_ru_orig_dict["positions"])[:,0] #['tn_ru_orig']
            #mnn_orig = np.array(tn_ru_orig_dict["positions"])[:,1] #['МНН']
            tn_ru_orig_lst = tn_ru_orig_dict["positions"]
            if tn_ru_orig_lst is not None:
                tn_ru_orig = np.array(tn_ru_orig_lst)[:,0] #['tn_ru_orig']
                mnn_orig = np.array(tn_ru_orig_lst)[:,1] #['МНН']
            else: tn_ru_orig, mnn_orig = None, None
            """
            tn_ru_orig, mnn_orig = None, None
    if tn_ru_orig is None and tn_lat is not None:
        tn_ru_orig_dict = dict__tn_lat__tn_ru_orig.get(tn_lat.capitalize())
        if tn_ru_orig_dict is not None and tn_ru_orig_dict['num_positions']==1:
            if debug: print(type(tn_ru_orig_dict["positions"]), tn_ru_orig_dict.keys(), tn_ru_orig_dict["positions"])
            #tn_ru_orig = tn_ru_orig_dict["positions"][0] ['tn_ru_orig']
            #mnn_orig = tn_ru_orig_dict["positions"][0]['МНН']
            # Вессел Дуэ Ф посвящается
            tn_ru_orig_lst = tn_ru_orig_dict["positions"]
            if tn_ru_orig_lst is not None:
                tn_ru_orig = tn_ru_orig_lst[0]['tn_ru_orig']
                mnn_orig = tn_ru_orig_lst[0]['МНН']
            else: tn_ru_orig, mnn_orig = None, None
        else:
            """
            #tn_ru_orig = np.array(tn_ru_orig_dict["positions"])[:,0] #['tn_ru_orig']
            #mnn_orig = np.array(tn_ru_orig_dict["positions"])[:,1] #['МНН']
            tn_ru_orig_lst = tn_ru_orig_dict["positions"]
            if tn_ru_orig_lst is not None:
                tn_ru_orig = np.array(tn_ru_orig_lst)[:,0] #['tn_ru_orig']
                mnn_orig = np.array(tn_ru_orig_lst)[:,1] #['МНН']
            """
            tn_ru_orig, mnn_orig = None, None
    return tn_ru_orig, mnn_orig
                
def select_klp_mnn_tn_by_tn(trade_name, debug = False):
    mnn_by_tn, tn_by_tn = None, None
    if trade_name is not None and not (((type(trade_name)==float) or (type(trade_name)==np.float64)) and math.isnan(trade_name)):
        mask_tn_srch = klp_srch_list[:,trade_name_capitalize_id]==trade_name.capitalize()
        trade_name_klp_lst = klp_srch_list[mask_tn_srch]
        if debug: print(f"select_klp_mnn_tn_by_tn: len(trade_name_klp_lst): {len(trade_name_klp_lst)}")
        if len(trade_name_klp_lst) > 0:
            #    mnn_true, tn_true = np_unique_nan_wrapper(trade_name_klp_lst[:, 
            # trade_name_id]), np_unique_nan_wrapper(trade_name_klp_lst[:, mnn_standard_id])
            mnn_by_tn = np_unique_nan(trade_name_klp_lst[:, mnn_standard_id]) #, debug=debug)
            tn_by_tn = np_unique_nan(trade_name_klp_lst[:, trade_name_id]) #, debug=debug)
            # mnn_by_tn = np_unique_nan_01a(trade_name_klp_lst[:, mnn_standard_id]) #, debug=debug)
            # tn_by_tn = np_unique_nan_01a(trade_name_klp_lst[:, trade_name_id]) #, debug=debug)
    if debug: 
        print(f"select_klp_mnn_tn_by_tn: tn: {trade_name} ->  mnn_by_tn: {mnn_by_tn}, tn_by_tn: {tn_by_tn}")
        print(f"types: mnn_by_tn: {type(mnn_by_tn)}, tn_by_tn: {type(tn_by_tn)}")
    return mnn_by_tn, tn_by_tn

def extract_dosage_standard(dosage_standard_value_str, debug=False):
    # на входе: # '{'grls_value': '300 ЛЕ/мл', 'dosage_unit': {'name': 'ЛЕ/мл', 'okei_code': '876', 'okei_name': 'усл. ед'} 
    # '300 ЛЕ/мл'
    dosage_standard_value, dosage_standard_unit = None, None
    # if dosage is not None and type(dosage)==dict:
    #     dosage_standard_value_str = dosage.get('grls_value')
    if dosage_standard_value_str is not None:
        try: #'numpy.ndarray'  and not (type(dosage_standard_value_str)==str)
            if (not (type(dosage_standard_value_str)==np.ndarray)) \
              and not (dosage_standard_value_str=='~') \
              and not (dosage_standard_value_str.lower()=='не указано') \
              and not ('+' in dosage_standard_value_str) : # не сложная дозировка
                dosage_standard_value = float(re.sub (r"[^(\d*\.\d*)]",'', dosage_standard_value_str))
                dosage_standard_unit = re.sub (r"[(\d*\.\d*)]",'', dosage_standard_value_str).strip() 
                # не србатывает при '10000 анти-Ха ЕД/мл'
        except Exception as err:
            # print(f"select_dosage_standard: dosage: {dosage}")
            print(f"select_dosage_standard: type(dosage_standard_value_str): {type(dosage_standard_value_str)}")
            print(f"select_dosage_standard: dosage_standard_value_str: {dosage_standard_value_str}")
    # return dosage_standard_value_str, dosage_standard_value, dosage_standard_unit
    return dosage_standard_value, dosage_standard_unit

def doze_pseudo_to_doze_parts_list_02(doze_str, doze, doze_unit, pseudo_vol, pseudo_vol_unit, debug = False):
    # doze_unit и pseudo_vol_unit уже оунифированы на стандартные значения
    doze_base_unit, k_doze = None, None
    pseudo_vol_base_unit, k_vol = None, None
    # base_unit_dict = recalc_doze_units_dict.get(doze_unit)
    if doze_unit is not None:
        base_doze_unit_dict = base_doze_unit_esklp.get(doze_unit)
        if base_doze_unit_dict is not None:
            doze_base_unit, k_doze = base_doze_unit_dict.get('base_unit'), base_doze_unit_dict.get('k')
    if pseudo_vol_unit is not None:
        pseudo_vol_base_unit_dict = base_pseudo_vol_unit_esklp.get(pseudo_vol_unit)
        if pseudo_vol_base_unit_dict is not None:
            pseudo_vol_base_unit, k_vol = pseudo_vol_base_unit_dict.get('base_unit'), pseudo_vol_base_unit_dict.get('k')

    return [[doze_str, doze, doze_unit, pseudo_vol, pseudo_vol_unit, doze_base_unit, k_doze, pseudo_vol_base_unit, k_vol]]


def doze_pseudo_to_doze_parts_list(doze_str, doze, doze_unit, pseudo_vol, pseudo_vol_unit, debug = False):
    # doze_unit и pseudo_vol_unit уже оунифированы на стандартные значения
    doze_base_unit, k = None, None
    # base_unit_dict = recalc_doze_units_dict.get(doze_unit)
    base_unit_dict = base_doze_unit_esklp.get(doze_unit)
    if base_unit_dict is not None:
        doze_base_unit, k = base_unit_dict.get('base_unit'), base_unit_dict.get('k')
    return [[doze_str, doze, doze_unit, pseudo_vol, pseudo_vol_unit, doze_base_unit, k]]

def make_one_position_doze_ztr_02 (doze, doze_unit, pseudo_vol, pseudo_vol_unit, 
                                   base_doze_unit, k_doze, pseudo_vol_base_unit, k_vol, debug = False ):
    dosage_parsing_str_position = None
    if debug:
        print(F"make_one_position_doze_ztr: inputs:", doze, doze_unit, pseudo_vol, pseudo_vol_unit, 
             base_doze_unit, k_doze, pseudo_vol_base_unit, k_vol)
    if ((type(doze)==str) or (type(doze)==np.str_)):
        # чтобы могло преобразоваться во float
        doze = doze.replace(',','.')
    if doze is not None:
        if k_doze is not None:
            try:
                doze = float(doze) * k_doze
                if doze.is_integer(): doze = int(doze)
            except Exception as err:
                print("make_one_position_doze_ztr_02:", err, "float(doze) * k_doze", doze, k_doze)
        if k_vol is not None and (k_vol != 0):
            try:
                doze = float(doze) / k_vol
                if doze.is_integer(): doze = int(doze)
            except Exception as err:
                print("make_one_position_doze_ztr_02:", err, "float(doze) / k_vol", doze, k_vol)
        dosage_parsing_str_position = (str(doze) if doze is not None else '') \
            + ' ' + (base_doze_unit if base_doze_unit is not None else '') \
            + ('/' if pseudo_vol_base_unit is not None else '') \
            + (pseudo_vol if pseudo_vol is not None or () else '') \
            + ( pseudo_vol_base_unit if pseudo_vol_base_unit is not None else '')
    
        
    return dosage_parsing_str_position

def make_one_position_doze_ztr_03 (doze, doze_unit, pseudo_vol, pseudo_vol_unit, 
                                   base_doze_unit, k_doze, pseudo_vol_base_unit, k_vol, debug = False ):
    dosage_parsing_str_position = None
    dosage_parsing_value, dosage_parsing_unit = None, None
    if debug:
        print(F"make_one_position_doze_ztr: inputs:", doze, doze_unit, pseudo_vol, pseudo_vol_unit, 
             base_doze_unit, k_doze, pseudo_vol_base_unit, k_vol)
    if ((type(doze)==str) or (type(doze)==np.str_)):
        # чтобы могло преобразоваться во float
        doze = doze.replace(',','.')
    if doze is not None:
        if k_doze is not None:
            try:
                doze = float(doze) * k_doze
                if doze.is_integer(): doze = int(doze)
            except Exception as err:
                print("make_one_position_doze_ztr_02:", err, "float(doze) * k_doze", doze, k_doze)
        if k_vol is not None and (k_vol != 0):
            try:
                doze = float(doze) / k_vol
                if doze.is_integer(): doze = int(doze)
            except Exception as err:
                print("make_one_position_doze_ztr_02:", err, "float(doze) / k_vol", doze, k_vol)
        # dosage_parsing_str_position = (str(doze) if doze is not None and k is not None else '') \
        # dosage_parsing_str_position = (str(doze) if doze is not None else '') \
        #     + ' ' + (base_doze_unit if base_doze_unit is not None else '') \
        #     + ('/' if pseudo_vol_base_unit is not None else '') \
        #     + (pseudo_vol if pseudo_vol is not None or () else '') \
        #     + ( pseudo_vol_base_unit if pseudo_vol_base_unit is not None else '')
        # dosage_parsing_value  = doze
        dosage_parsing_value  = float(doze) if ((type(doze)==str) or  (type(doze)==np.str_)) else doze
        # такое ьывает когда сложная дозировка без ЕИ и соотвественно все бреобразования ао float(intrger) прошли мимом
        if ((type(dosage_parsing_value) == float) or (type(dosage_parsing_value) == np.float64)) and dosage_parsing_value.is_integer():
            dosage_parsing_value = int(dosage_parsing_value)
        dosage_parsing_unit = (base_doze_unit if base_doze_unit is not None else '') \
            + ('/' if pseudo_vol_base_unit is not None else '') \
            + (pseudo_vol if pseudo_vol is not None or () else '') \
            + ( pseudo_vol_base_unit if pseudo_vol_base_unit is not None else '')
        dosage_parsing_str_position = (str(doze) if doze is not None else '') \
            + ' ' + dosage_parsing_unit
        
    return dosage_parsing_str_position, dosage_parsing_value, dosage_parsing_unit

def make_one_position_doze_ztr (doze, doze_unit, pseudo_vol, pseudo_vol_unit, base_doze_unit, k, debug = False ):
    dosage_parsing_str_position = None
    if debug:
        print(F"make_one_position_doze_ztr: inputs:", doze, doze_unit, pseudo_vol, pseudo_vol_unit, base_doze_unit, k)
    if ((type(doze)==str) or (type(doze)==np.str_)):
        # чтобы могло преобразоваться во float
        doze = doze.replace(',','.')
    doze_unit_esklp = base_doze_unit_esklp.get(doze_unit)
    if doze_unit_esklp is not None:
        base_doze_unit = doze_unit_esklp['base_unit']
    pseudo_vol_unit_esklp = base_doze_unit_esklp.get(pseudo_vol_unit)
    if pseudo_vol_unit is not None and pseudo_vol_unit_esklp is not None:
        pseudo_vol_unit = pseudo_vol_unit_esklp.get('base_unit')
        k_pseudo_vol_div = pseudo_vol_unit_esklp.get('k')
        if debug:
            print(F"make_one_position_doze_ztr: pseudo_vol_unit: '{pseudo_vol_unit}', k_pseudo_vol_div: {k_pseudo_vol_div}")
        try:
            if k_pseudo_vol_div != 0:
                doze = float(doze) / k_pseudo_vol_div
        except Exception as err:
            print("make_one_position_doze_ztr:", err, "float(doze) / k_pseudo_vol_div", doze, k_pseudo_vol_div)
        # if pseudo_vol_unit in ['кг', 'л']:
        #     if base_doze_unit_esklp.get(pseudo_vol_unit) is not None:
        #         k_pseudo_vol_mul = base_doze_unit_esklp.get(pseudo_vol_unit)['k']
        #         pseudo_vol_unit = base_doze_unit_esklp.get(pseudo_vol_unit)['base_unit']
        #         if debug:
        #             print(F"make_one_position_doze_ztr: pseudo_vol_unit: '{pseudo_vol_unit}', k_pseudo_vol_up: {k_pseudo_vol_down}")
        #         try:
        #             if k_pseudo_vol_down != 0:
        #                 doze = float(doze) / k_pseudo_vol_down
        #         except Exception as err:
        #             print(err, "float(doze) / k_pseudo_vol", doze, k_pseudo_vol)
    try:
        if doze is not None and k is not None:
            doze = float(doze)
            doze = doze * k
            if doze.is_integer(): doze = int(doze)
        elif doze is not None:
            doze = float(doze)
            if doze.is_integer(): doze = int(doze)
            
        dosage_parsing_str_position = (str(doze) if doze is not None and k is not None else '') \
            + ' ' + (base_doze_unit if base_doze_unit is not None else '') \
            + ('/' if pseudo_vol_unit is not None else '') \
            + (pseudo_vol if pseudo_vol is not None or () else '') \
            + ( pseudo_vol_unit if pseudo_vol_unit is not None else '')
    except Exception as err:
        print("make_one_position_doze_ztr:", err)
        
    return dosage_parsing_str_position

def make_doze_str_frmt_02(doze_parts_list, debug = False):
    # [['1 г', '1', 'г', None, None, 'мг', 1000.0, None, None], ['1 г', '1', 'г', None, None, 'мг', 1000.0, None, None]]
    dosage_parsing_str = None
    # на взоде пусто
    if doze_parts_list is None or len(doze_parts_list)==0:
        return dosage_parsing_str
    # простая дозировка
    elif (type(doze_parts_list) == list)  and not ((type(doze_parts_list)==str) or (type(doze_parts_list)==np.str_)) \
        and (len(doze_parts_list)==1): 
        item, doze, doze_unit, pseudo_vol, pseudo_vol_unit, base_doze_unit, k_doze, pseudo_vol_base_unit, k_vol = doze_parts_list[0]
        dosage_parsing_str = make_one_position_doze_ztr_02 (doze, doze_unit, pseudo_vol, pseudo_vol_unit, 
                                base_doze_unit, k_doze, pseudo_vol_base_unit, k_vol, debug = debug )
    # сложная дозировка
    else:
        # doze_unit_types = [el[2].strip() for el in doze_parts_list]
        # base_doze_unit_types = [el[-2].strip() for el in doze_parts_list]
        # pseudo_vol_unit_types = [el[4].strip() for el in doze_parts_list]
        doze_parts_list_01 = [[e if e is not None else '' for e in el ] for el in doze_parts_list ]
        doze_unit_types = [el[2].strip() for el in doze_parts_list_01]
        base_doze_unit_types = [el[5].strip() for el in doze_parts_list_01]
        pseudo_vol_unit_types = [el[4].strip() for el in doze_parts_list_01]
        pseudo_vol_base_unit_types = [el[7].strip() for el in doze_parts_list_01]
        
        base_doze_unit_types_set = list(set(base_doze_unit_types))
        pseudo_vol_base_unit_types_set = list(set(pseudo_vol_base_unit_types))
        if debug: 
            print(f"make_doze_str_frmt: base_doze_unit_types_set: {base_doze_unit_types_set}")
            print(f"make_doze_str_frmt: pseudo_vol_base_unit_types_set: {pseudo_vol_base_unit_types_set}")
        if (len(base_doze_unit_types_set) == 1) and (len(pseudo_vol_base_unit_types_set) == 1):
            dosage_parsing_str = ''
            if pseudo_vol_base_unit_types_set[0] is None: # нет псевдообъема
                for i, (item, doze, doze_unit, pseudo_vol, pseudo_vol_unit, base_doze_unit, k_doze, pseudo_vol_base_unit, k_vol) in enumerate(doze_parts_list):
                    add_str = make_one_position_doze_ztr_02 (doze, doze_unit, pseudo_vol, pseudo_vol_unit, 
                                    base_doze_unit, k_doze, pseudo_vol_base_unit, k_vol, debug = debug )
                    if add_str is not None:
                        dosage_parsing_str +=  add_str
            else:
                for i, (item, doze, doze_unit, pseudo_vol, pseudo_vol_unit, base_doze_unit, k_doze, pseudo_vol_base_unit, k_vol) in enumerate(doze_parts_list):
                    if i < (len(doze_parts_list)-1):
                        pseudo_vol, pseudo_vol_unit, pseudo_vol_base_unit = None, None, None
                        add_str = make_one_position_doze_ztr_02 (doze, doze_unit, pseudo_vol, pseudo_vol_unit, 
                                    base_doze_unit, k_doze, pseudo_vol_base_unit, k_vol, debug = debug )
                        if add_str is not None:
                            dosage_parsing_str +=  add_str + '+'
                    else: 
                        add_str = make_one_position_doze_ztr_02 (doze, doze_unit, pseudo_vol, pseudo_vol_unit, 
                                    base_doze_unit, k_doze, pseudo_vol_base_unit, k_vol, debug = debug )
                        if add_str is not None:
                            dosage_parsing_str +=  add_str
        else:
            dosage_parsing_str = ''
            if (len(base_doze_unit_types_set) == 2) and (len(pseudo_vol_base_unit_types_set) == 1)\
                and base_doze_unit_types_set[0] in ['ЕД', 'мг'] and base_doze_unit_types_set[1] in ['ЕД', 'мг']\
                and pseudo_vol_base_unit_types_set[0] == 'мл':
                for i, (item, doze, doze_unit, pseudo_vol, pseudo_vol_unit, base_doze_unit, k_doze, pseudo_vol_base_unit, k_vol) in enumerate(doze_parts_list):
                    if i < (len(doze_parts_list)-1):
                        pseudo_vol, pseudo_vol_unit, pseudo_vol_base_unit = None, None, None
                        add_str = make_one_position_doze_ztr_02 (doze, doze_unit, pseudo_vol, pseudo_vol_unit, 
                                      base_doze_unit, k_doze, pseudo_vol_base_unit, k_vol, debug = debug )
                        if add_str is not None:
                            dosage_parsing_str +=  add_str + '+'
                    else: 
                        add_str = make_one_position_doze_ztr_02 (doze, doze_unit, pseudo_vol, pseudo_vol_unit, 
                                      base_doze_unit, k_doze, pseudo_vol_base_unit, k_vol, debug = debug )
                        if add_str is not None:
                            dosage_parsing_str +=  add_str
            else:
                for i, (item, doze, doze_unit, pseudo_vol, pseudo_vol_unit, base_doze_unit, k_doze, pseudo_vol_base_unit, k_vol) in enumerate(doze_parts_list):
                    if i < (len(doze_parts_list)-1):
                        add_str = make_one_position_doze_ztr_02 (doze, doze_unit, pseudo_vol, pseudo_vol_unit, 
                                      base_doze_unit, k_doze, pseudo_vol_base_unit, k_vol, debug = debug )
                        if add_str is not None:
                            dosage_parsing_str +=  add_str + '+'
                    else: 
                        add_str = make_one_position_doze_ztr_02 (doze, doze_unit, pseudo_vol, pseudo_vol_unit, 
                                      base_doze_unit, k_doze, pseudo_vol_base_unit, k_vol, debug = debug )
                        if add_str is not None:
                            dosage_parsing_str +=  add_str
    return dosage_parsing_str

def make_doze_str_frmt_03(doze_parts_list, debug = False):
    dosage_parsing_str = None
    dosage_parsing_value, dosage_parsing_unit = None, None
    # на взоде пусто
    if doze_parts_list is None or len(doze_parts_list)==0:
        return dosage_parsing_str
    # простая дозировка
    elif (type(doze_parts_list) == list)  and not ((type(doze_parts_list)==str) or (type(doze_parts_list)==np.str_)) \
        and (len(doze_parts_list)==1): 
        item, doze, doze_unit, pseudo_vol, pseudo_vol_unit, base_doze_unit, k_doze, pseudo_vol_base_unit, k_vol = doze_parts_list[0]
        dosage_parsing_str, dosage_parsing_value, dosage_parsing_unit = make_one_position_doze_ztr_03 (doze, doze_unit, pseudo_vol, pseudo_vol_unit, 
                                base_doze_unit, k_doze, pseudo_vol_base_unit, k_vol, debug = debug )
         
    # сложная дозировка
    else:
        doze_sum = 0
        # doze_unit_types = [el[2].strip() for el in doze_parts_list]
        # base_doze_unit_types = [el[-2].strip() for el in doze_parts_list]
        # pseudo_vol_unit_types = [el[4].strip() for el in doze_parts_list]
        doze_parts_list_01 = [[e if e is not None else '' for e in el ] for el in doze_parts_list ]
        doze_unit_types = [el[2].strip() for el in doze_parts_list_01]
        base_doze_unit_types = [el[5].strip() for el in doze_parts_list_01]
        pseudo_vol_unit_types = [el[4].strip() for el in doze_parts_list_01]
        pseudo_vol_base_unit_types = [el[7].strip() for el in doze_parts_list_01]
        
        base_doze_unit_types_set = list(set(base_doze_unit_types))
        pseudo_vol_base_unit_types_set = list(set(pseudo_vol_base_unit_types))
        if debug: 
            print(f"make_doze_str_frmt: base_doze_unit_types_set: {base_doze_unit_types_set}")
            print(f"make_doze_str_frmt: pseudo_vol_base_unit_types_set: {pseudo_vol_base_unit_types_set}")
        if (len(base_doze_unit_types_set) == 1) and (len(pseudo_vol_base_unit_types_set) == 1):
            dosage_parsing_str = ''
            if pseudo_vol_base_unit_types_set[0] is None: # нет псевдообъема
                for i, (item, doze, doze_unit, pseudo_vol, pseudo_vol_unit, base_doze_unit, k_doze, pseudo_vol_base_unit, k_vol) in enumerate(doze_parts_list):
                    add_str, add_dosage, dosage_parsing_unit = make_one_position_doze_ztr_03 (doze, doze_unit, pseudo_vol, pseudo_vol_unit, 
                                    base_doze_unit, k_doze, pseudo_vol_base_unit, k_vol, debug = debug )
                    if add_str is not None:
                        dosage_parsing_str +=  add_str
                    if add_dosage is not None: 
                        doze_sum += add_dosage
                dosage_parsing_value = doze_sum
            else:
                for i, (item, doze, doze_unit, pseudo_vol, pseudo_vol_unit, base_doze_unit, k_doze, pseudo_vol_base_unit, k_vol) in enumerate(doze_parts_list):
                    if i < (len(doze_parts_list)-1):
                        pseudo_vol, pseudo_vol_unit, pseudo_vol_base_unit = None, None, None
                        add_str, add_dosage, _ = make_one_position_doze_ztr_03 (doze, doze_unit, pseudo_vol, pseudo_vol_unit, 
                                    base_doze_unit, k_doze, pseudo_vol_base_unit, k_vol, debug = debug )
                        if add_str is not None:
                            dosage_parsing_str +=  add_str + '+'
                        if add_dosage is not None: 
                            doze_sum += add_dosage
                    else: 
                        add_str, add_dosage, dosage_parsing_unit = make_one_position_doze_ztr_03 (doze, doze_unit, pseudo_vol, pseudo_vol_unit, 
                                    base_doze_unit, k_doze, pseudo_vol_base_unit, k_vol, debug = debug )
                        if add_str is not None:
                            dosage_parsing_str +=  add_str
                        if add_dosage is not None: 
                            doze_sum += add_dosage
                dosage_parsing_value = doze_sum
        else:
            dosage_parsing_str = ''
            if (len(base_doze_unit_types_set) == 2) and (len(pseudo_vol_base_unit_types_set) == 1)\
                and base_doze_unit_types_set[0] in ['ЕД', 'мг'] and base_doze_unit_types_set[1] in ['ЕД', 'мг']\
                and pseudo_vol_base_unit_types_set[0] == 'мл':
                for i, (item, doze, doze_unit, pseudo_vol, pseudo_vol_unit, base_doze_unit, k_doze, pseudo_vol_base_unit, k_vol) in enumerate(doze_parts_list):
                    if i < (len(doze_parts_list)-1):
                        pseudo_vol, pseudo_vol_unit, pseudo_vol_base_unit = None, None, None
                        add_str, add_dosage, _ = make_one_position_doze_ztr_03 (doze, doze_unit, pseudo_vol, pseudo_vol_unit, 
                                      base_doze_unit, k_doze, pseudo_vol_base_unit, k_vol, debug = debug )
                        if add_str is not None:
                            dosage_parsing_str +=  add_str + '+'
                        if add_dosage is not None: 
                            doze_sum += add_dosage
                    else: 
                        add_str, add_dosage, dosage_parsing_unit = make_one_position_doze_ztr_03 (doze, doze_unit, pseudo_vol, pseudo_vol_unit, 
                                      base_doze_unit, k_doze, pseudo_vol_base_unit, k_vol, debug = debug )
                        if add_str is not None:
                            dosage_parsing_str +=  add_str
                        if add_dosage is not None: 
                            doze_sum += add_dosage
                dosage_parsing_value = doze_sum
            else:
                for i, (item, doze, doze_unit, pseudo_vol, pseudo_vol_unit, base_doze_unit, k_doze, pseudo_vol_base_unit, k_vol) in enumerate(doze_parts_list):
                    if i < (len(doze_parts_list)-1):
                        add_str, add_dosage, _ = make_one_position_doze_ztr_03 (doze, doze_unit, pseudo_vol, pseudo_vol_unit, 
                                      base_doze_unit, k_doze, pseudo_vol_base_unit, k_vol, debug = debug )
                        if add_str is not None:
                            dosage_parsing_str +=  add_str + '+'
                        if add_dosage is not None: 
                            doze_sum += add_dosage
                    else: 
                        add_str, add_dosage, dosage_parsing_unit = make_one_position_doze_ztr_03 (doze, doze_unit, pseudo_vol, pseudo_vol_unit, 
                                      base_doze_unit, k_doze, pseudo_vol_base_unit, k_vol, debug = debug )
                        if add_str is not None:
                            dosage_parsing_str +=  add_str
                        if add_dosage is not None: 
                            doze_sum += add_dosage
                dosage_parsing_value = doze_sum
                
    return dosage_parsing_str, dosage_parsing_value, dosage_parsing_unit

def make_doze_str_frmt(doze_parts_list, debug = False):
    dosage_parsing_str = None
    # на взоде пусто
    if doze_parts_list is None or len(doze_parts_list)==0:
        return dosage_parsing_str
    # простая дозировка
    elif (type(doze_parts_list) == list)  and not ((type(doze_parts_list)==str) or (type(doze_parts_list)==np.str_)) \
        and (len(doze_parts_list)==1): 
        item, doze, doze_unit, pseudo_vol, pseudo_vol_unit, base_doze_unit, k = doze_parts_list[0]
        dosage_parsing_str = make_one_position_doze_ztr (doze, doze_unit, pseudo_vol, pseudo_vol_unit, base_doze_unit, k, debug = debug )
    # сложная дозировка
    else:
        # doze_unit_types = [el[2].strip() for el in doze_parts_list]
        # base_doze_unit_types = [el[-2].strip() for el in doze_parts_list]
        # pseudo_vol_unit_types = [el[4].strip() for el in doze_parts_list]
        doze_parts_list_01 = [[e if e is not None else '' for e in el ] for el in doze_parts_list ]
        doze_unit_types = [el[2].strip() for el in doze_parts_list_01]
        base_doze_unit_types = [el[-2].strip() for el in doze_parts_list_01]
        pseudo_vol_unit_types = [el[4].strip() for el in doze_parts_list_01]
        
        base_doze_unit_types_set = list(set(base_doze_unit_types))
        pseudo_vol_unit_types_set = list(set(pseudo_vol_unit_types))
        if debug: 
            print(f"make_doze_str_frmt: base_doze_unit_types_set: {base_doze_unit_types_set}")
            print(f"make_doze_str_frmt: pseudo_vol_unit_types_set: {pseudo_vol_unit_types_set}")
        if (len(base_doze_unit_types_set) == 1) and (len(pseudo_vol_unit_types_set) == 1):
            dosage_parsing_str = ''
            if pseudo_vol_unit_types_set[0] is None: # нет псевдообъема
                for i, (item, doze, doze_unit, pseudo_vol, pseudo_vol_unit, base_doze_unit, k) in enumerate(doze_parts_list):
                    dosage_parsing_str +=  make_one_position_doze_ztr (doze, doze_unit, pseudo_vol, pseudo_vol_unit, base_doze_unit, k, debug = debug )
            else:
                for i, (item, doze, doze_unit, pseudo_vol, pseudo_vol_unit, base_doze_unit, k) in enumerate(doze_parts_list):
                    if i < (len(doze_parts_list)-1):
                        pseudo_vol, pseudo_vol_unit = None, None
                        dosage_parsing_str +=  make_one_position_doze_ztr (doze, doze_unit, pseudo_vol, pseudo_vol_unit, base_doze_unit, k, debug = debug ) + '+'
                    else:
                        dosage_parsing_str +=  make_one_position_doze_ztr (doze, doze_unit, pseudo_vol, pseudo_vol_unit, base_doze_unit, k, debug = debug )
        else:
            dosage_parsing_str = ''
            for i, (item, doze, doze_unit, pseudo_vol, pseudo_vol_unit, base_doze_unit, k) in enumerate(doze_parts_list):
                if i < (len(doze_parts_list)-1):
                    dosage_parsing_str +=  make_one_position_doze_ztr (doze, doze_unit, pseudo_vol, pseudo_vol_unit, base_doze_unit, k, debug = debug ) + '+'
                else: 
                    dosage_parsing_str +=  make_one_position_doze_ztr (doze, doze_unit, pseudo_vol, pseudo_vol_unit, base_doze_unit, k, debug = debug )
    return dosage_parsing_str

def calc_parsing_doze_02(doze_proc, doze, doze_unit, pseudo_vol, pseudo_vol_unit, vol_unit, debug=False):
    if debug: print(f"calc_parsing_doze_02: doze_proc: {doze_proc}, doze: {doze}, doze_unit: '{doze_unit}', pseudo_vol: {pseudo_vol}, pseudo_vol_unit: '{pseudo_vol_unit}', vol_unit: '{vol_unit}'")
    dosage_parsing_value, dosage_parsing_unit = None, None
    
    proc_to_mg = 10
    if doze_unit is not None and 'тыс.' in doze_unit: 
        doze_unit = re.sub('тыс.', '', doze_unit).strip()
        k_doze = 1000
    elif doze_unit is not None and 'млн.' in doze_unit:
        doze_unit = re.sub('млн.', '', doze_unit).strip()
        k_doze = 1_000_000
    else: k_doze = 1
    
    
    # doze_parts_list = doze_pseudo_to_doze_parts_list_02(dosage_standard_value_str, doze, doze_unit, pseudo_vol, pseudo_vol_unit, debug = debug)
    
    if doze_unit in ['анти-Ха МЕ', 'анти-Xa МЕ', 'анти-Ха ЛЕ']: doze_unit = 'анти-Ха ЕД'
    # а) если "doze_proc" - не пусто, а "doze"- пусто = конвертор, расстановка в соо-щие поля
    if doze_proc is not None and doze is None:
        try:
            dosage_parsing_value = float(doze_proc) * proc_to_mg
            # dosage_parsing_unit = (doze_unit if doze_unit is not None else '') +\
            
            if vol_unit is not None:
                base_pseudo_vol_unit_esklp_dict = base_pseudo_vol_unit_esklp.get(vol_unit) # здесь vol_unit
            elif pseudo_vol_unit is not None:
                base_pseudo_vol_unit_esklp_dict = base_pseudo_vol_unit_esklp.get(pseudo_vol_unit) 
            else:
                base_pseudo_vol_unit_esklp_dict = None
            if debug: print(f"calc_parsing_doze_02: base_pseudo_vol_unit_esklp_dict: {base_pseudo_vol_unit_esklp_dict}")
            base_pseudo_vol_unit = None
            if base_pseudo_vol_unit_esklp_dict is not None:
                k_pseudo = base_pseudo_vol_unit_esklp_dict.get('k')
                if k_pseudo is not None and k_pseudo != 0:
                    dosage_parsing_value = dosage_parsing_value / k_pseudo
                base_pseudo_vol_unit = base_pseudo_vol_unit_esklp_dict.get('base_unit')
                # base_pseudo_vol_unit_dict = base_pseudo_vol_unit_esklp.get(pseudo_vol_unit)
                # if base_pseudo_vol_unit_dict is not None:
                #     base_pseudo_vol_unit = base_pseudo_vol_unit_dict.get('base_unit')
                # else:
                #     base_pseudo_vol_unit = None
            dosage_parsing_unit = 'мг' +\
                (('/' + base_pseudo_vol_unit) if base_pseudo_vol_unit is not None else '')
                # ??????????????? vol_unit
        except Exception as err:
            print("calc_parsing_doze_02:", err, "float(doze_proc)", f"doze_proc: {doze_proc}")
    # б) если "pseudo_vol_unit" - пусто, тогда "doze" и "doze_unit" - в поля "Дозировка" и "ЕИ дозировки"
    elif doze is not None and (((type(doze)==str) or (type(doze)==np.str_)) and (len(doze)>0) ) and pseudo_vol_unit is None:
        try:
            base_doze_unit_esklp_dict = base_doze_unit_esklp.get(doze_unit)
            if debug: print(f"calc_parsing_doze_02: base_doze_unit_esklp_dict: {base_doze_unit_esklp_dict}")
            if base_doze_unit_esklp_dict is not None:
                k = base_doze_unit_esklp_dict.get('k')
                if k is not None: 
                    dosage_parsing_value = float(doze) * k_doze * k
                
                base_doze_unit = base_doze_unit_esklp_dict.get('base_unit')
                dosage_parsing_unit = base_doze_unit
        except Exception as err:
            print("calc_parsing_doze_02: ", err, "float(doze)", f"doze: {doze}")

    # в) если "pseudo_vol_unit" - не пусто, pseudo_vol - пусто, то "doze" - в "Дозировка", 
      # "doze_unit" "/" "pseudo_vol_unit" - в "ЕИ дозировки"
    elif doze is not None and pseudo_vol_unit is not None and pseudo_vol is None:
        try:
            # dosage_parsing_value = float(doze) * k_doze
            # # dosage_parsing_unit = (doze_unit if doze_unit is not None else '') +\
            # #     (('/' + pseudo_vol_unit) if pseudo_vol_unit is not None else '')
            
            base_doze_unit_esklp_dict = base_doze_unit_esklp.get(doze_unit)
            if debug: print(f"calc_parsing_doze_02: base_doze_unit_esklp_dict: {base_doze_unit_esklp_dict}")
            if base_doze_unit_esklp_dict is not None:
                k = base_doze_unit_esklp_dict.get('k')
                if k is not None: 
                    dosage_parsing_value = float(doze) * k_doze * k
                else:
                    dosage_parsing_value = float(doze) * k_doze
                    if debug: print(f"calc_parsing_doze_02: error k is None")
                base_doze_unit = base_doze_unit_esklp_dict.get('base_unit')
                
            base_vol_unit_esklp_dict = base_vol_unit_esklp.get(pseudo_vol_unit)
            if debug: print(f"calc_parsing_doze_02: base_vol_unit_esklp_dict: {base_vol_unit_esklp_dict}")
            if base_vol_unit_esklp_dict is not None:
                k_pseudo = base_vol_unit_esklp_dict.get('k')
                if k_pseudo is not None and k_pseudo != 0:
                    dosage_parsing_value = dosage_parsing_value / k_pseudo
                # base_pseudo_vol_unit = base_vol_unit_esklp_dict.get('base_unit')
            base_pseudo_vol_unit_dict = base_pseudo_vol_unit_esklp.get(pseudo_vol_unit)
            if base_pseudo_vol_unit_dict is not None:
                base_pseudo_vol_unit = base_pseudo_vol_unit_dict.get('base_unit')
            else:
                base_pseudo_vol_unit = None
            dosage_parsing_unit = (base_doze_unit if base_doze_unit is not None else '') +\
                (('/' + base_pseudo_vol_unit) if base_pseudo_vol_unit is not None else '')
            
            
        except Exception as err:
            print("calc_parsing_doze_02: ", err, "float(doze)", f"doze: {doze}")
    # г) если "pseudo_vol_unit" - не пусто, pseudo_vol - не пусто, то "Дозировка" = doze/pseudo_vol , 
      # "doze_unit" "/" "pseudo_vol_unit" - в "ЕИ дозировки"
    elif doze is not None and pseudo_vol is not None:
        try:
            # dosage_parsing_value = float(doze)/float(pseudo_vol) * k_doze
            
            base_doze_unit_esklp_dict = base_doze_unit_esklp.get(doze_unit)
            if debug: print(f"calc_parsing_doze_02: base_doze_unit_esklp_dict: {base_doze_unit_esklp_dict}")
            if base_doze_unit_esklp_dict is not None:
                k = base_doze_unit_esklp_dict.get('k')
                if k is not None: 
                    dosage_parsing_value = float(doze) * k_doze * k
                    
                else:
                    dosage_parsing_value = float(doze) * k_doze
                    if debug: print(f"calc_parsing_doze_02: error k is None")
                base_doze_unit = base_doze_unit_esklp_dict.get('base_unit')
                
            base_vol_unit_esklp_dict = base_vol_unit_esklp.get(pseudo_vol_unit)
            if debug: print(f"calc_parsing_doze_02: base_vol_unit_esklp_dict: {base_vol_unit_esklp_dict}")
            if base_vol_unit_esklp_dict is not None:
                k_pseudo = base_vol_unit_esklp_dict.get('k')
                if k_pseudo is not None and k_pseudo != 0:
                    dosage_parsing_value = dosage_parsing_value / k_pseudo
                    
                # base_pseudo_vol_unit = base_vol_unit_esklp_dict.get('base_unit')
            base_pseudo_vol_unit_dict = base_pseudo_vol_unit_esklp.get(pseudo_vol_unit)
            if base_pseudo_vol_unit_dict is not None:
                base_pseudo_vol_unit = base_pseudo_vol_unit_dict.get('base_unit')
            else:
                base_pseudo_vol_unit = None
                
            
            # dosage_parsing_unit = (doze_unit if doze_unit is not None else '') +\
            #     (('/' + pseudo_vol_unit) if pseudo_vol_unit is not None else '')
            dosage_parsing_unit = (base_doze_unit if base_doze_unit is not None else '') +\
                (('/' + base_pseudo_vol_unit) if base_pseudo_vol_unit is not None else '')
        except Exception as err:
            print("calc_parsing_doze_02: ", err, "float(doze)/float(pseudo_vol)", f"doze: {doze}, pseudo_vol: {pseudo_vol}")
    # elif doze is not None and doze_unit is not None and (pseudo_vol_unit is not None or pseudo_vol_unit is None) :
    #     # уточнить у Жени
    #     # Эспумизан беби капли д/приема внутрь 100 мг/мл 30 мл фл с мерн колп N 1x1 Берлин-Хеми Германия
    #     # неправильное название через 'е'
    #     # но doze_group: 5, doze_proc: None, doze: 100, doze_unit: мг, pseudo_vol: None, pseudo_vol_unit:мл, vol: 30, vol_unit: мл
    #     try:
    #         dosage_parsing_value = float(doze) * k_doze
    #         dosage_parsing_unit = (doze_unit if doze_unit is not None else '') +\
    #             (('/' + pseudo_vol_unit) if pseudo_vol_unit is not None else '')
    #     except Exception as err:
    #         print("calc_parsing_doze: ", err, "float(doze)/float(pseudo_vol)", f"doze: {doze}, pseudo_vol: {pseudo_vol}")

    return dosage_parsing_value, dosage_parsing_unit

def calc_parsing_doze(doze_proc, doze, doze_unit, pseudo_vol, pseudo_vol_unit, vol_unit, debug=False):
    if debug: print(f"calc_parsing_doze: ", doze_proc, doze, doze_unit, pseudo_vol, pseudo_vol_unit, vol_unit)
    dosage_parsing_value, dosage_parsing_unit = None, None
    proc_to_mg = 10
    if doze_unit is not None and 'тыс.' in doze_unit: 
        doze_unit = re.sub('тыс.', '', doze_unit).strip()
        k_doze = 1000
    elif doze_unit is not None and 'млн.' in doze_unit:
        doze_unit = re.sub('млн.', '', doze_unit).strip()
        k_doze = 1_000_000
    else: k_doze = 1

    if doze_unit in ['анти-Ха МЕ', 'анти-Xa МЕ', 'анти-Ха ЛЕ']: doze_unit = 'анти-Ха ЕД'
    # а) если "doze_proc" - не пусто, а "doze"- пусто = конвертор, расстановка в соо-щие поля
    if doze_proc is not None and doze is None:
        try:
            dosage_parsing_value = float(doze_proc) * proc_to_mg
            # dosage_parsing_unit = (doze_unit if doze_unit is not None else '') +\
            dosage_parsing_unit = 'мг' +\
                (('/' + vol_unit) if vol_unit is not None else '')
                # ??????????????? vol_unit
        except Exception as err:
            print("calc_parsing_doze:", err, "float(doze_proc)", f"doze_proc: {doze_proc}")
    # б) если "pseudo_vol_unit" - пусто, тогда "doze" и "doze_unit" - в поля "Дозировка" и "ЕИ дозировки"
    elif doze is not None and (((type(doze)==str) or (type(doze)==np.str_)) and (len(doze)>0) ) and pseudo_vol_unit is None:
        try:
            dosage_parsing_value = float(doze) * k_doze
            dosage_parsing_unit = doze_unit
        except Exception as err:
            print("calc_parsing_doze: ", err, "float(doze)", f"doze: {doze}")

    # в) если "pseudo_vol_unit" - не пусто, pseudo_vol - пусто, то "doze" - в "Дозировка", 
      # "doze_unit" "/" "pseudo_vol_unit" - в "ЕИ дозировки"
    elif doze is not None and pseudo_vol_unit is not None and pseudo_vol is None:
        try:
            dosage_parsing_value = float(doze) * k_doze
            dosage_parsing_unit = (doze_unit if doze_unit is not None else '') +\
                (('/' + pseudo_vol_unit) if pseudo_vol_unit is not None else '')
        except Exception as err:
            print("calc_parsing_doze: ", err, "float(doze)", f"doze: {doze}")
    # г) если "pseudo_vol_unit" - не пусто, pseudo_vol - не пусто, то "Дозировка" = doze/pseudo_vol , 
      # "doze_unit" "/" "pseudo_vol_unit" - в "ЕИ дозировки"
    elif doze is not None and pseudo_vol is not None:
        try:
            dosage_parsing_value = float(doze)/float(pseudo_vol) * k_doze
            dosage_parsing_unit = (doze_unit if doze_unit is not None else '') +\
                (('/' + pseudo_vol_unit) if pseudo_vol_unit is not None else '')
        except Exception as err:
            print("calc_parsing_doze: ", err, "float(doze)/float(pseudo_vol)", f"doze: {doze}, pseudo_vol: {pseudo_vol}")
    # elif doze is not None and doze_unit is not None and (pseudo_vol_unit is not None or pseudo_vol_unit is None) :
    #     # уточнить у Жени
    #     # Эспумизан беби капли д/приема внутрь 100 мг/мл 30 мл фл с мерн колп N 1x1 Берлин-Хеми Германия
    #     # неправильное название через 'е'
    #     # но doze_group: 5, doze_proc: None, doze: 100, doze_unit: мг, pseudo_vol: None, pseudo_vol_unit:мл, vol: 30, vol_unit: мл
    #     try:
    #         dosage_parsing_value = float(doze) * k_doze
    #         dosage_parsing_unit = (doze_unit if doze_unit is not None else '') +\
    #             (('/' + pseudo_vol_unit) if pseudo_vol_unit is not None else '')
    #     except Exception as err:
    #         print("calc_parsing_doze: ", err, "float(doze)/float(pseudo_vol)", f"doze: {doze}, pseudo_vol: {pseudo_vol}")

    return dosage_parsing_value, dosage_parsing_unit

def form_dosage_parsing_value_str(dosage_parsing_value, dosage_parsing_unit, debug = False):
    dosage_parsing_value_str = None
    if type(dosage_parsing_value) == float:
        # if dosage_parsing_value - math.ceil(dosage_parsing_value) > 0: # с цифрами после запятой
        if dosage_parsing_value - int(dosage_parsing_value) > 0: # с цифрами после запятой
            # print("if dosage_parsing_value - math.ceil(dosage_parsing_value) > 0")
            dosage_parsing_value_str = str(dosage_parsing_value) + ' ' +  str(dosage_parsing_unit)
        else: 
            # dosage_parsing_value_str = str(math.ceil(dosage_parsing_value)) + ' ' +  str(dosage_parsing_unit)
            dosage_parsing_value_str = str(int(dosage_parsing_value)) + ' ' +  str(dosage_parsing_unit)
    elif type(dosage_parsing_value) == int:
        dosage_parsing_value_str = str(dosage_parsing_value) + ' ' +  str(dosage_parsing_unit)
    else: 
        if debug: print(f"type(dosage_parsing_value): {type(dosage_parsing_value)}")
        return dosage_parsing_value_str
    if debug: print(f"form_dosage_parsing_value_str: dosage_parsing_value_str: '{dosage_parsing_value_str}'")
    return dosage_parsing_value_str

def reformat_simple_dosage(dosage_standard_value_str, debug=False):
    dosage_standard_value_str_refrmt = None
    ptn_digits = r"((\d+,\d+)|(\d+\.\d+)|([\d\s]+\d+)|(\d+))"
    ptn_digits = r"((\d+,\d+)|(\d+\.\d+)|(\d+))"
    m_doze = re.search(ptn_digits, dosage_standard_value_str, flags=re.I)
    if m_doze is not None:
        doze = m_doze.group().strip()
    else: 
        doze = ''
    units = re.sub(doze, '', dosage_standard_value_str).strip()
    if '/' in dosage_standard_value_str:
        doze_unit = units[:units.rfind('/')]
        pseudo_vol_unit = units[units.rfind('/')+1:]
    else:
        doze_unit = units
        pseudo_vol_unit = None
    pseudo_vol = None
    if debug: print(f"reformat_simple_dosage: doze: '{doze}', doze_unit: '{doze_unit}', pseudo_vol_unit: '{pseudo_vol_unit}'")
    doze_parts_list = doze_pseudo_to_doze_parts_list_02(dosage_standard_value_str, doze, doze_unit, pseudo_vol, pseudo_vol_unit, debug = debug)
    dosage_standard_value_str_refrmt = make_doze_str_frmt_02(doze_parts_list, debug = debug)
    
    return dosage_standard_value_str_refrmt

def reformat_complex_dosage(complex_doze_str, debug=False):
    dosage_standard_value_str_refrmt = None
    complex_doze_list = complex_doze_str.split('+')
    if debug: print(f"reformat_complex_dosage: complex_doze_list: {complex_doze_list}")
    complex_doze_parts_list = define_doze_parts_02(complex_doze_list, debug=debug)
    if debug: print(f"reformat_complex_dosage: complex_doze_parts_list: {complex_doze_parts_list}")
    complex_doze_list_enhanced = enhance_units_03(complex_doze_parts_list, debug=debug)
    dosage_standard_value_str_refrmt = make_doze_str_frmt_02(complex_doze_list_enhanced, debug = debug)
    # enhance_units_03(comlex_doze_parts_list, debug=False)
    return dosage_standard_value_str_refrmt

def reformat_dosage_standard_value_str(dosage_standard_value_str, debug=False):
    dosage_standard_value_str_refrmt = None
    if dosage_standard_value_str is None or \
        (((type(dosage_standard_value_str)==str) or (type(dosage_standard_value_str)==np.str_)) and (len(dosage_standard_value_str)==0)):
        return None
    if type(dosage_standard_value_str) == np.ndarray:
        dosage_standard_value_str_refrmt = []
        for dosage_standard_value_str_el in dosage_standard_value_str:
            if '+' in dosage_standard_value_str_el: 
                dosage_standard_value_str_refrmt_el = reformat_complex_dosage(dosage_standard_value_str_el, debug=debug)
            else:
                dosage_standard_value_str_refrmt_el = reformat_simple_dosage(dosage_standard_value_str_el, debug=debug)
            dosage_standard_value_str_refrmt.append(dosage_standard_value_str_refrmt_el)
        # dosage_standard_value_str_refrmt = np.array(dosage_standard_value_str_refrmt)
    elif ((type(dosage_standard_value_str)==str) or (type(dosage_standard_value_str)==np.str_)) and (len(dosage_standard_value_str)>0):
        if '+' in dosage_standard_value_str: 
            dosage_standard_value_str_refrmt = reformat_complex_dosage(dosage_standard_value_str, debug=debug)
        else:
            dosage_standard_value_str_refrmt = reformat_simple_dosage(dosage_standard_value_str, debug=debug)
    else:
        return None
    return dosage_standard_value_str_refrmt

def compare_standard_parsing_doze(dosage_standard_value_str, dosage_parsing_value:float, dosage_parsing_unit, debug=False):
    if debug: print(f"compare_standard_parsing_doze: ", dosage_standard_value_str, dosage_parsing_value, dosage_parsing_unit)
    # if debug: print(f"compare_standard_parsing_doze: type(dosage_standard_value_str):",type(dosage_standard_value_str))
    # if debug: print(f"compare_standard_parsing_doze: type(dosage_parsing_value):",type(dosage_parsing_value))
    c_doze = None # doze_controlling
    dosage_parsing_value_str = None
    if dosage_standard_value_str is None and dosage_parsing_value is None and dosage_parsing_unit is None:
        return c_doze, dosage_parsing_value_str
    elif dosage_standard_value_str is not None and ((type(dosage_standard_value_str) ==str) or (type(dosage_standard_value_str) ==np.str_ )) \
          and dosage_standard_value_str.lower() in ['~', 'не указано']:
        c_doze = False
    elif dosage_standard_value_str is not None and dosage_parsing_value is not None and dosage_parsing_unit is not None:
        dosage_parsing_value_str = form_dosage_parsing_value_str(dosage_parsing_value, dosage_parsing_unit, debug = debug)

        if (type(dosage_standard_value_str)== str or type(dosage_standard_value_str)==np.str_) and dosage_parsing_value_str is not None:
            if dosage_standard_value_str == dosage_parsing_value_str:
                c_doze = True
            else: c_doze = False
        elif (type(dosage_standard_value_str)== np.ndarray) or (type(dosage_standard_value_str)==list):
            if dosage_parsing_value_str in dosage_standard_value_str:
                c_doze = True
            else: c_doze = False
        
    return c_doze, dosage_parsing_value_str

def compare_standard_parsing_doze_02(dosage_standard_value_str, dosage_parsing_value_str, debug=False):
    if debug: print(f"compare_standard_parsing_doze: ", dosage_standard_value_str, dosage_parsing_value_str)
    # if debug: print(f"compare_standard_parsing_doze: type(dosage_standard_value_str):",type(dosage_standard_value_str))
    # if debug: print(f"compare_standard_parsing_doze: type(dosage_parsing_value):",type(dosage_parsing_value))
    c_doze = None # doze_controlling
    i_doze = None # индекс правильной дозировки в списке, если None -> None, если str (и не список) -> -1
    if dosage_standard_value_str is None and dosage_parsing_value_str is None:
        return c_doze, i_doze
    elif dosage_standard_value_str is not None and ((type(dosage_standard_value_str) ==str) or (type(dosage_standard_value_str) ==np.str_ )) \
          and dosage_standard_value_str.lower() in ['~', 'не указано']:
        c_doze = False
        i_doze = None
    elif dosage_standard_value_str is not None and dosage_parsing_value_str is not None:
        
        if (type(dosage_standard_value_str)== str or type(dosage_standard_value_str)==np.str_) and dosage_parsing_value_str is not None:
            if dosage_standard_value_str == dosage_parsing_value_str:
                c_doze = True
                i_doze = -1
            else: 
                c_doze = False
                i_doze = None
        elif (type(dosage_standard_value_str)== np.ndarray) or (type(dosage_standard_value_str)==list):
            if dosage_parsing_value_str in dosage_standard_value_str:
                c_doze = True
                if type(dosage_standard_value_str)==np.ndarray:
                    dosage_standard_value_str = list(dosage_standard_value_str)
                    # np.where(dosage_standard_value_str==dosage_parsing_value_str) возвращает np.array со всеми совпавшими значениями
                i_doze = dosage_standard_value_str.index(dosage_parsing_value_str)
            else: 
                c_doze = False
                i_doze = None
        
    return c_doze, i_doze

def compare_standard_parsing_doze_02_00(dosage_standard_value_str, dosage_parsing_value_str, debug=False):
    if debug: print(f"compare_standard_parsing_doze: ", dosage_standard_value_str, dosage_parsing_value_str)
    # if debug: print(f"compare_standard_parsing_doze: type(dosage_standard_value_str):",type(dosage_standard_value_str))
    # if debug: print(f"compare_standard_parsing_doze: type(dosage_parsing_value):",type(dosage_parsing_value))
    c_doze = None # doze_controlling
    if dosage_standard_value_str is None and dosage_parsing_value_str is None:
        return c_doze
    elif dosage_standard_value_str is not None and ((type(dosage_standard_value_str) ==str) or (type(dosage_standard_value_str) ==np.str_ )) \
          and dosage_standard_value_str.lower() in ['~', 'не указано']:
        c_doze = False
    elif dosage_standard_value_str is not None and dosage_parsing_value_str is not None:
        
        if (type(dosage_standard_value_str)== str or type(dosage_standard_value_str)==np.str_) and dosage_parsing_value_str is not None:
            if dosage_standard_value_str == dosage_parsing_value_str:
                c_doze = True
            else: c_doze = False
        elif (type(dosage_standard_value_str)== np.ndarray) or (type(dosage_standard_value_str)==list):
            if dosage_parsing_value_str in dosage_standard_value_str:
                c_doze = True
            else: c_doze = False
        
    return c_doze

def to_doze_base_units( doze, doze_unit, pseudo_vol, pseudo_vol_unit):
    base_doze_unit, base_pseudo_vol_unit = None, None
    base_doze_unit_esklp_dict = base_doze_unit_esklp.get(doze_unit)
    if ((type(doze)==str) or (type(doze)==np.str_)):
        doze = doze.replace(',', '.')
    if base_doze_unit_esklp_dict is not None:
        k_doze = base_doze_unit_esklp_dict.get('k')
        if k_doze is not None and doze is not None: 
            try:
                doze = float(doze) * k_doze # * k для множителя тыс млн
            except Exception as err:
                print("to_doze_base_units:", err)

        base_doze_unit = base_doze_unit_esklp_dict.get('base_unit')
        
    base_pseudo_vol_unit_esklp_dict = base_pseudo_vol_unit_esklp.get(pseudo_vol_unit) 
    base_pseudo_vol_unit = None
    if base_pseudo_vol_unit_esklp_dict is not None:
        k_pseudo = base_pseudo_vol_unit_esklp_dict.get('k')
        if k_pseudo is not None and (k_pseudo != 0) and doze is not None:
            doze = float(doze) / k_pseudo
        base_pseudo_vol_unit = base_pseudo_vol_unit_esklp_dict.get('base_unit')
    if pseudo_vol is not None:
        try:
            pseudo_vol = float(pseudo_vol)
            # if pseudo_vol.is_integer():
            #     pseudo_vol = int (pseudo_vol)
            if (pseudo_vol != 0) and doze is not None:
                doze = float(doze) / pseudo_vol
        except Exception as err:
            print("to_doze_base_units:", err)
    return doze, base_doze_unit, base_pseudo_vol_unit

def extract_simple_dosage(dosage_value_str, debug=False):
    if dosage_value_str is None: return None, None
    if ((type(dosage_value_str)==str) or (type(dosage_value_str)==str)) and (dosage_value_str=='~'): 
        return '~', None
    dosage_value, dosage_unit = None, None
    ptn_digits = r"((\d+,\d+)|(\d+\.\d+)|([\d\s]+\d+)|(\d+))"
    ptn_digits = r"((\d+,\d+)|(\d+\.\d+)|(\d+))"
    m_doze = re.search(ptn_digits, dosage_value_str, flags=re.I)
    if m_doze is not None:
        doze = m_doze.group().strip()
    else: 
        doze = None
        return None, None
    if doze is not None:
        units = re.sub(doze, '', dosage_value_str).strip()
        try:
            doze = float(doze)
            if doze.is_integer():
                doze = int (doze)
        except Exception as err:
            print("extract_simple_dosage", err)

    if '/' in dosage_value_str:
        doze_unit = units[:units.rfind('/')]
        
        pseudo_vol_unit_block = units[units.rfind('/')+1:]
        m_pseudo_vol = re.search(ptn_digits, pseudo_vol_unit_block, flags=re.I)
        if m_pseudo_vol is not None:
            pseudo_vol = m_pseudo_vol.group().strip()
            pseudo_vol_unit = re.sub(pseudo_vol, '', pseudo_vol_unit_block).strip()
            pseudo_vol = pseudo_vol.replace(',','.')
            
        else:
            pseudo_vol_unit = pseudo_vol_unit_block.strip()
            pseudo_vol = None
        
        
    else:
        doze_unit = units.strip()

        pseudo_vol_unit = None
        pseudo_vol = None
    
    # base_doze_unit = None
    # base_pseudo_vol_unit = None
    doze, base_doze_unit, base_pseudo_vol_unit = to_doze_base_units( doze, doze_unit, pseudo_vol, pseudo_vol_unit)
        
    if debug: print(f"extract_simple_dosage: doze: '{doze}', doze_unit: '{doze_unit}', pseudo_vol_unit: '{pseudo_vol_unit}'")
    # doze_parts_list = doze_pseudo_to_doze_parts_list_02(dosage_standard_value_str, doze, doze_unit, pseudo_vol, pseudo_vol_unit, debug = debug)
    dosage_value = doze
    # dosage_unit = (doze_unit if doze_unit is not None else '') \
    #         + ('/' if pseudo_vol_unit is not None else '') \
    #         + (str(pseudo_vol) if pseudo_vol is not None else '') \
    #         + ( pseudo_vol_unit if pseudo_vol_unit is not None else '')
    dosage_unit = (base_doze_unit if base_doze_unit is not None else '') \
            + ('/' if base_pseudo_vol_unit is not None else '') \
            + ( base_pseudo_vol_unit if base_pseudo_vol_unit is not None else '')
            # + (str(pseudo_vol) if pseudo_vol is not None else '') \
    
    return dosage_value, dosage_unit
    
def extract_complex_dosage(complex_doze_str, debug=False):
    if complex_doze_str is None: return None, None
    complex_doze_list = complex_doze_str.split('+')
    if debug: print(f"extract_complex_dosage: complex_doze_list: {complex_doze_list}")
    complex_doze_parts_list = define_doze_parts_02(complex_doze_list, debug=debug)
    if debug: print(f"extract_complex_dosage: complex_doze_parts_list: {complex_doze_parts_list}")
    complex_doze_list_enhanced = enhance_units_03(complex_doze_parts_list, debug=debug)
    # dosage_standard_value_str_refrmt = make_doze_str_frmt_02(complex_doze_list_enhanced, debug = debug)
    # enhance_units_03(comlex_doze_parts_list, debug=False)
    doze_total = 0.0
    for i, (item, doze, doze_unit, pseudo_vol, pseudo_vol_unit, base_doze_unit, k_doze, pseudo_vol_base_unit, k_vol) in enumerate(complex_doze_list_enhanced):
        if doze is not None:
            # doze = doze.replace(',', '.')
            doze, base_doze_unit, base_pseudo_vol_unit = to_doze_base_units( doze, doze_unit, pseudo_vol, pseudo_vol_unit)
            doze_total += float(doze)
    # if pseudo_vol is not None:
    #     pseudo_vol = pseudo_vol.replace(',', '.')
    #     pseudo_vol = float(pseudo_vol)
    #     if pseudo_vol.is_integer():
    #         pseudo_vol = int(pseudo_vol)
    doze_total, base_doze_unit, base_pseudo_vol_unit = to_doze_base_units( doze_total, doze_unit, pseudo_vol, pseudo_vol_unit)
    # dosage_unit = (doze_unit if doze_unit is not None else '') \
    #         + ('/' if pseudo_vol_unit is not None else '') \
    #         + (str(pseudo_vol) if pseudo_vol is not None else '') \
    #         + ( pseudo_vol_unit if pseudo_vol_unit is not None else '')
    # if pseudo_vol is not None:
    #     pseudo_vol = float(pseudo_vol)
    #     if pseudo_vol != 0:
    #         doze_total = doze_total/pseudo_vol
    dosage_unit = (base_doze_unit if base_doze_unit is not None else '') \
            + ('/' if base_pseudo_vol_unit is not None else '') \
            + ( base_pseudo_vol_unit if base_pseudo_vol_unit is not None else '')
            # + (str(pseudo_vol) if pseudo_vol is not None else '') \
    if doze_total.is_integer():
        doze_total = int(doze_total)
    dosage_value = doze_total
    
    return dosage_value, dosage_unit

    


def form_mask_klp_srch_lst(col_values, col_id):
    mask_klp_srch_lst = klp_srch_list.shape[0]*[False]
    if col_id is not None and (col_id < 0 or col_id > klp_srch_list.shape[1]-1) \
        or col_id is None:
        return mask_klp_srch_lst
    if col_values is None: return mask_klp_srch_lst

    if type (col_values)==str or type (col_values)== np.str_:
        mask_klp_srch_lst = klp_srch_list[:, col_id] == col_values
    elif type (col_values)==list or type (col_values)== np.ndarray:
        for i, value in enumerate(col_values):
            if i == 0: mask_klp_srch_lst = (klp_srch_list[:, col_id] == value)
            else:  mask_klp_srch_lst = mask_klp_srch_lst | (klp_srch_list[:, col_id] == value)
    return mask_klp_srch_lst                    

def form_mask_klp_list_dict_df(col_values, col_name, debug=False):
    # пока по одной колонке
    mask_klp_list_dict_df = klp_list_dict_df.shape[0]*[False]
    if col_name is None or not (col_name in  klp_list_dict_df.columns):
    # if col_name is None :
        return mask_klp_list_dict_df
    
    if type (col_values)==str or type (col_values)== np.str_:
        mask_klp_list_dict_df = klp_list_dict_df[col_name] == col_values
    elif type (col_values)==list or type (col_values)== np.ndarray:
        for i, value in enumerate(col_values):
            if i == 0: mask_klp_list_dict_df = (klp_list_dict_df[col_name] == value)
            else:  mask_klp_list_dict_df = mask_klp_list_dict_df | (klp_list_dict_df[col_name] == value)
    return mask_klp_list_dict_df

def select_klp_packs_norm(tn_true,  form_standard, dosage_parsing_value_str, debug=False):
    # tn_true:  или str или list или np.ndarray
    # form_standard:  или str или list или np.ndarray
    # 'dosage_parsing_value_str' '7 мг/мл'
    # поиск по 'trade_name', 'lf_norm_name', 'dosage_norm_name': '7 мг/мл' == 'dosage_parsing_value_str'
    # lp_pack_1_num (pack_1_num) lp_pack_2_num (pack_2_num) lp_unit, lp_consumer_total (consumer_total)
    lp_pack_1_num, lp_pack_2_num, lp_unit_okei, lp_unit, lp_consumer_total, lp_consumer_total_calc = None, None, None, None, None, None
    return_values_cols = ['pack_1_num', 'pack_2_num', 'lp_unit_okei_name', 'lp_unit_name', 'consumer_total']
    
    if not (type(tn_true)==str) and ((type(tn_true)==list) or (type(tn_true)==np.ndarray)):
        tn_true_capitalize = [tn.capitalize() for tn in tn_true]
        # tn_true_capitalize = '['+ ','.join([f"'{tn.capitalize()}'" for tn in tn_true]) + ']'
        # tn_true_capitalize = '('+ ' or '.join([f"(trade_name =='{tn.capitalize()}')" for tn in tn_true]) + ')'
        if debug: print(f"select_klp_packs_norm: 'if not (type(tn_true)==str) and (type(tn_true)==list or type(tn_true)==np.ndarray)'", tn_true_capitalize)
        if debug: print(f"select_klp_packs_norm: tn_true_capitalize: '{tn_true_capitalize}'")
    elif ((type(tn_true)==str) or (type(tn_true) == np.str_)):
        # tn_true_capitalize = f"'{tn_true.capitalize()}'"
        tn_true_capitalize = [tn_true.capitalize()]
        # tn_true_capitalize =  f"(trade_name =='{tn_true.capitalize()}')"
        if debug: print(f"select_klp_packs_norm: 'elif type(tn_true)==str'", tn_true_capitalize)
    else: 
        tn_true_capitalize = [tn_true]
        # tn_true_capitalize =  f"(trade_name =='{tn_true.capitalize()}')"
        if debug: print(f"select_klp_packs_norm: 'else'", tn_true_capitalize)
    if ((type(form_standard)==list) or (type(form_standard)==np.ndarray)):
        form_standard_s = form_standard
    else:
        form_standard_s = [form_standard]
    #     query_str = f"(trade_name == '{tn_true_capitalize}') and (form_standard == '{form_standard}') and (dosage_norm_name == '{dosage_parsing_value_str}')"
    query_str = f"(trade_name.isin ({tn_true_capitalize})) and (form_standard == '{form_standard}') and (dosage_norm_name == '{dosage_parsing_value_str}')"
    query_str = f"(trade_name.isin ({tn_true_capitalize})) and (form_standard.isin({form_standard_s}) and (dosage_norm_name == '{dosage_parsing_value_str}')"
    query_str = "(trade_name.isin (@tn_true_capitalize)) and (form_standard.isin(@form_standard_s) and (dosage_norm_name == @dosage_parsing_value_str)"
    query_str = "trade_name.isin @tn_true_capitalize and form_standard.isin @form_standard_s and dosage_norm_name == @dosage_parsing_value_str"
    query_str = "trade_name in @tn_true_capitalize and form_standard in @form_standard_s and dosage_norm_name == @dosage_parsing_value_str"
    
    # query_str = f"(trade_name == {tn_true_capitalize}) and (form_standard == '{form_standard}') and (dosage_norm_name == '{dosage_parsing_value_str}')"
    # query_str = "(trade_name in @tn_true_capitalize) and (form_standard == @form_standard) and (dosage_norm_name == @dosage_parsing_value_str)"
    # query_str = "@tn_true_capitalize and (form_standard == @form_standard) and (dosage_norm_name == @dosage_parsing_value_str)"
    # query_str = f"{tn_true_capitalize} and (form_standard == '{form_standard}') and (dosage_norm_name == '{dosage_parsing_value_str}')"
    if debug: print(f"select_klp_packs_norm: query_str: '{query_str}'")
    try:
        return_values = klp_list_dict_df.query(query_str, engine='python')[return_values_cols].values
    except Exception as err:
        print(err, f"select_klp_packs_norm: query_str: '{query_str}'")
        print(f"select_klp_packs_norm: type(tn_true): {type(tn_true)}, type(form_standard): {type(form_standard)}")
        sys.exit(2)


    if debug: print(f"select_klp_packs_norm: step1: return_values.shape", return_values.shape, return_values[:5] )
    if return_values.shape[0] > 0:
        lp_pack_1_num = np_unique_nan(return_values[:,0])
        lp_pack_2_num = np_unique_nan(return_values[:,1])
        lp_unit_okei = np_unique_nan(return_values[:,2])
        lp_unit = np_unique_nan(return_values[:,3])
        lp_consumer_total = np_unique_nan(return_values[:,4])
        # lp_consumer_total_calc = np_unique_nan(np.array([float(s) for s in return_values[:,0]])*np.array([float(s) for s in return_values[
        lp_consumer_total_calc = to_float(lp_consumer_total)

    return lp_pack_1_num, lp_pack_2_num, lp_unit_okei, lp_unit, lp_consumer_total, lp_consumer_total_calc      

def select_klp_packs_norm_00(tn_true,  form_standard, dosage_parsing_value_str, debug=False):
    # tn_true:  или str или list или np.ndarray
    # form_standard:  или str или list или np.ndarray
    # 'dosage_parsing_value_str' '7 мг/мл'
    # поиск по 'trade_name', 'lf_norm_name', 'dosage_norm_name': '7 мг/мл' == 'dosage_parsing_value_str'
    # lp_pack_1_num (pack_1_num) lp_pack_2_num (pack_2_num) lp_unit, lp_consumer_total (consumer_total)
    lp_pack_1_num, lp_pack_2_num, lp_unit_okei, lp_unit, lp_consumer_total, lp_consumer_total_calc = None, None, None, None, None, None
    return_values_cols = ['pack_1_num', 'pack_2_num', 'lp_unit_okei_name', 'lp_unit_name', 'consumer_total']
    
    if not (type(tn_true)==str) and (type(tn_true)==list or type(tn_true)==np.ndarray):
        tn_true_capitalize = [tn.capitalize() for tn in tn_true]
        if debug: print(f"select_klp_packs_norm: 'if not (type(tn_true)==str) and (type(tn_true)==list or type(tn_true)==np.ndarray)'", tn_true_capitalize)
    elif type(tn_true)==str:
        tn_true_capitalize = tn_true.capitalize()
        if debug: print(f"select_klp_packs_norm: 'elif type(tn_true)==str'", tn_true_capitalize)
    else: 
        tn_true_capitalize = tn_true
        if debug: print(f"select_klp_packs_norm: 'else'", tn_true_capitalize)

    mask_trade_name = form_mask_klp_srch_lst(tn_true_capitalize, trade_name_capitalize_id)
    mask_lf_norm_name = form_mask_klp_srch_lst(form_standard, lf_norm_name_id)
    mask_dosage_norm_name = form_mask_klp_srch_lst(dosage_parsing_value_str, dosage_norm_name_id)
    
    code_klp_lst =  np.unique(klp_srch_list[mask_trade_name & mask_lf_norm_name & mask_dosage_norm_name, code_klp_id])
    if debug: print(f"select_klp_packs_norm: code_klp_lst.shape, code_klp_lst[:5]: ", code_klp_lst.shape, code_klp_lst[:5])
    # mask_code_klp = form_mask_klp_list_dict_df(code_klp_lst, 'code_klp', debug=debug)
    # return_values = klp_list_dict_df[mask_code_klp][return_values_cols].values
    #  Предыдущий варинат сильно замедлял hfcxtn: передвать несколько раз маски по 300тыс записей все-таки утомляет систему
    if code_klp_lst is not None and len(code_klp_lst)>0:
        srch_list = '|'.join([r"(?:" + code_klp + r")" for code_klp in code_klp_lst])
        return_values = klp_list_dict_df[klp_list_dict_df['code_klp'].str.contains(srch_list, regex=True)][return_values_cols].values
        if debug: print(f"select_klp_packs_norm: return_values.shape", return_values.shape, return_values[:5] )
        # lp_pack_1_num = np_unique_nan_wrapper(return_values[:,0])
        # lp_pack_2_num = np_unique_nan_wrapper(return_values[:,1])
        # lp_unit_okei = np_unique_nan_wrapper(return_values[:,2])
        # lp_unit = np_unique_nan_wrapper(return_values[:,3])
        # lp_consumer_total = np_unique_nan_wrapper(return_values[:,4])
        # lp_consumer_total_calc = np_unique_nan_wrapper(np.array([float(s) for s in return_values[:,0]])*np.array([float(s) for s in return_values[:,1]]))
        lp_pack_1_num = np_unique_nan(return_values[:,0])
        lp_pack_2_num = np_unique_nan(return_values[:,1])
        lp_unit_okei = np_unique_nan(return_values[:,2])
        lp_unit = np_unique_nan(return_values[:,3])
        lp_consumer_total = np_unique_nan(return_values[:,4])
        lp_consumer_total_calc = np_unique_nan(np.array([float(s) for s in return_values[:,0]])*np.array([float(s) for s in return_values[:,1]]))

    return lp_pack_1_num, lp_pack_2_num, lp_unit_okei, lp_unit, lp_consumer_total, lp_consumer_total_calc        

def select_klp_packs_norm_02(tn_true,  form_standard, dosage_standard_value_str_02, debug=False):
    # tn_true:  или str или list или np.ndarray
    # form_standard:  или str или list или np.ndarray
    # 'dosage_parsing_value_str' '7 мг/мл'
    # поиск по 'trade_name', 'lf_norm_name', 'dosage_norm_name': '7 мг/мл' == 'dosage_parsing_value_str'
    # lp_pack_1_num (pack_1_num) lp_pack_2_num (pack_2_num) lp_unit, lp_consumer_total (consumer_total)
    lp_pack_1_num, lp_pack_1_name, lp_pack_2_num, lp_pack_2_name, lp_unit_okei_name, lp_unit_name, lp_consumer_total, lp_consumer_total_calc,\
                        is_dosed, mass_volume_num, mass_volume_name = \
        None, None, None, None, None, None, None, None, None, None, None
    return_values_cols = ['pack_1_num', 'pack_1_name', 'pack_2_num', 'pack_2_name', 
                  'lp_unit_okei_name', 'lp_unit_name', 'consumer_total', 'is_dosed', 'mass_volume_num', 'mass_volume_name']
    # return_values_cols = ['pack_1_num', 'pack_2_num', 
    #               'lp_unit_okei_name', 'lp_unit_name', 'consumer_total', 'is_dosed', 'mass_volume_num', 'mass_volume_name']
    
    if not (type(tn_true)==str) and ((type(tn_true)==list) or (type(tn_true)==np.ndarray)):
        tn_true_capitalize = [tn.capitalize() for tn in tn_true]
        # 'Бромгексин Медисорб' переводит в 'Бромгексин медисорб' и не находит
        tn_true_lower = [tn.lower() for tn in tn_true]
        # query_str = "trade_name.str.lower() in @tn_true_lower"
        # tn_true_capitalize = '['+ ','.join([f"'{tn.capitalize()}'" for tn in tn_true]) + ']'
        # tn_true_capitalize = '('+ ' or '.join([f"(trade_name =='{tn.capitalize()}')" for tn in tn_true]) + ')'
        if debug: print(f"select_klp_packs_norm_02: 'if not (type(tn_true)==str) and (type(tn_true)==list or type(tn_true)==np.ndarray)'", tn_true_capitalize)
        if debug: print(f"select_klp_packs_norm_02: tn_true_capitalize: '{tn_true_capitalize}'")
    elif ((type(tn_true)==str) or (type(tn_true) == np.str_)):
        # tn_true_capitalize = f"'{tn_true.capitalize()}'"
        tn_true_capitalize = [tn_true.capitalize()]
        tn_true_lower = [tn_true.lower()]
        # tn_true_capitalize =  f"(trade_name =='{tn_true.capitalize()}')"
        if debug: print(f"select_klp_packs_norm_02: 'elif type(tn_true)==str'", tn_true_capitalize)
    else: 
        tn_true_capitalize = [tn_true]
        tn_true_lower = [tn_true]
        # tn_true_capitalize =  f"(trade_name =='{tn_true.capitalize()}')"
        if debug: print(f"select_klp_packs_norm_02: 'else'", tn_true_capitalize)
    if ((type(form_standard)==list) or (type(form_standard)==np.ndarray)):
        form_standard_s = form_standard
    else:
        form_standard_s = [form_standard]
    if debug: print(f"select_klp_packs_norm_02: type(form_standard_s) : {type(form_standard_s)}, form_standard_s: '{form_standard_s}'")
    #     query_str = f"(trade_name == '{tn_true_capitalize}') and (form_standard == '{form_standard}') and (dosage_norm_name == '{dosage_parsing_value_str}')"
    # query_str = f"(trade_name.isin ({tn_true_capitalize})) and (form_standard == '{form_standard}') and (dosage_norm_name == '{dosage_standard_value_str_02}')"
    # query_str = f"(trade_name.isin ({tn_true_capitalize})) and (form_standard.isin({form_standard_s}) and (dosage_norm_name == '{dosage_standard_value_str_02}')"
    # query_str = "(trade_name.isin (@tn_true_capitalize)) and (form_standard.isin(@form_standard_s) and (dosage_norm_name == @dosage_standard_value_str_02)"
    # query_str = "trade_name.isin @tn_true_capitalize and form_standard.isin @form_standard_s and dosage_norm_name == @dosage_standard_value_str_02"
    query_str = "trade_name in @tn_true_capitalize and form_standard in @form_standard_s and dosage_norm_name == @dosage_standard_value_str_02"
    query_str = "trade_name.str.lower() in @tn_true_lower and form_standard in @form_standard_s and dosage_norm_name == @dosage_standard_value_str_02"
    
    ### problen 
    # 500 млн.КОЕ vs 500000000 КОЕ  - dosage_norm_name vs dosage_standard_value_str
    query_str = "trade_name.str.lower() in @tn_true_lower and form_standard in @form_standard_s and dosage_standard_value_str_klp == @dosage_standard_value_str_02"
    
    # query_str = f"(trade_name == {tn_true_capitalize}) and (form_standard == '{form_standard}') and (dosage_norm_name == '{dosage_parsing_value_str}')"
    # query_str = "(trade_name in @tn_true_capitalize) and (form_standard == @form_standard) and (dosage_norm_name == @dosage_parsing_value_str)"
    # query_str = "@tn_true_capitalize and (form_standard == @form_standard) and (dosage_norm_name == @dosage_parsing_value_str)"
    # query_str = f"{tn_true_capitalize} and (form_standard == '{form_standard}') and (dosage_norm_name == '{dosage_parsing_value_str}')"
    if debug: print(f"select_klp_packs_norm: query_str: '{query_str}'")
    try:
        return_values = klp_list_dict_df.query(query_str, engine='python')[return_values_cols].values
    except Exception as err:
        print(err, f"select_klp_packs_norm: query_str: '{query_str}'")
        print(f"select_klp_packs_norm: type(tn_true): {type(tn_true)}, type(form_standard): {type(form_standard)}")
        sys.exit(2)


    if debug: print(f"select_klp_packs_norm: step1: return_values.shape", return_values.shape, return_values[:5] )
    if return_values.shape[0] > 0:
        lp_pack_1_num = np_unique_nan(return_values[:, 0])
        lp_pack_1_name = np_unique_nan(return_values[:, 1])
        lp_pack_2_num = np_unique_nan(return_values[:, 2])
        lp_pack_2_name = np_unique_nan(return_values[:, 3])
        lp_unit_okei_name = np_unique_nan(return_values[:, 4])
        lp_unit_name = np_unique_nan(return_values[:, 5])
        lp_consumer_total = np_unique_nan(return_values[:, 6])
        is_dosed = np_unique_nan(return_values[:, 7])
        mass_volume_num = np_unique_nan(return_values[:, 8])
        mass_volume_name = np_unique_nan(return_values[:, 9])
        # lp_pack_1_num = np_unique_nan(return_values[:, 0])
        # lp_pack_1_name = None
        # lp_pack_2_num = np_unique_nan(return_values[:, 1])
        # lp_pack_2_name = None
        # lp_unit_okei_name = np_unique_nan(return_values[:, 2])
        # lp_unit_name = np_unique_nan(return_values[:, 3])
        # lp_consumer_total = np_unique_nan(return_values[:, 4])
        # is_dosed = np_unique_nan(return_values[:, 5])
        # mass_volume_num = np_unique_nan(return_values[:, 6])
        # mass_volume_name = np_unique_nan(return_values[:, 7])
        
        # lp_consumer_total_calc = np_unique_nan(np.array([float(s) for s in return_values[:,0]])*np.array([float(s) for s in return_values[
        lp_consumer_total_calc = to_float(lp_consumer_total)

    return lp_pack_1_num, lp_pack_1_name, lp_pack_2_num, lp_pack_2_name, lp_unit_okei_name, lp_unit_name, lp_consumer_total, lp_consumer_total_calc,\
        is_dosed, mass_volume_num, mass_volume_name

def update_vol_exclude(vol, vol_unit, mass_volume_name, mass_volume_num, debug=False):
    # vol, vol_unit = None, None
    # есть еще ошибочная ситуация mass_volume_name [14.000, 5.000]	mass_volume_num [кг, литр]
    global smnn_list_df, klp_list_dict_df, zvnlp_df, znvlp_date  
    if mass_volume_name is not None and not (((type(mass_volume_name)==float) or (type(mass_volume_name)==np.float64)) and math.isnan(mass_volume_name)):
        if ((type(mass_volume_name)==str) or (type(mass_volume_name)==np.str_)) and  mass_volume_name in ["кг", "литр"]:
            if debug: 
                print('update_vol_exclude: if ((type(mass_volume_name)==str) or (type(mass_volume_name)==np.str_)) and  mass_volume_name in ["кг", "литр"]:')
                print(f"update_vol_exclude: vol: {vol}, mass_volume_num: {mass_volume_num}, new_vol: {float(mass_volume_num)*1000}")
            # vol, vol_unit = float(mass_volume_num)*1000, "мл"
            # vol, vol_unit = float(float(mass_volume_num)*1000), "мл"
            try:
                # vol, vol_unit = mass_volume_num*1000, "мл"
                # if ((type(mass_volume_num)==float) or (type(mass_volume_num)==np.float64)):
                if not ((type(mass_volume_num)==list) or (type(mass_volume_num)==np.ndarray)):
                    vol, vol_unit = float(float(mass_volume_num)*1000), "мл"
            #     # new_vol, vol_unit = float(mass_volume_num)*1000, "мл"
            except Exception as err:
                print(err)
                print(f"update_vol_exclude: mass_volume_name: {mass_volume_name}, mass_volume_num: {mass_volume_num}")

        elif ((type(mass_volume_name)==list) or (type(mass_volume_name)==np.ndarray)):
            pass
        # elif ((type(mass_volume_name)==list) or (type(mass_volume_name)==np.ndarray)) and\
        #     ('кг' in mass_volume_name or  "литр" in mass_volume_name):
        #     if debug: print('elif ((type(mass_volume_name)==list) or (type(mass_volume_name)==np.ndarray)) and("кг" in mass_volume_name or  "литр" in mass_volume_name):')
        #     # vol, vol_unit = float(mass_volume_num)*1000, "мл"
        #     vol, vol_unit = float(float(mass_volume_num)*1000), "мл"
            # try:
            #     # vol, vol_unit = mass_volume_num*1000, "мл"
            #     vol, vol_unit = float(mass_volume_num)*1000, "мл"
            #     # new_vol, vol_unit = float(mass_volume_num)*1000, "мл"
            # except Exception as err:
            #     print(err)
            #     print(f"mass_volume_name: {mass_volume_name}, mass_volume_num: {mass_volume_num}")
            # по алгоритму не правильно считает "литры" "кг" - это косяк ЕСКЛП. 
            # Соот-но прикручивем костыли: если mass_volume_name = "кг", "литр" =>vol*=mass_volume_num*1000, vol_unit* = "мл"
    return vol, vol_unit

def calc_volume(doze_group, ls_unit_name, pack_1_num, 
                form_standard, consumer_total, consumer_total_kis, dosage_parsing_unit, mass_volume_name, 
                mass_volume_num,
                debug=False):
                # cnt, debug=False, write=False):
    # 919 only size-1 arrays can be converted to Python scalars
    # global smnn_list_df, klp_list_dict_df, zvnlp_df, znvlp_date  
    
    # vol_pre, vol_unit_pre, vol, vol_unit = None, None, None, None
    # vol, vol_unit = None, None
    vol_calc, vol_unit_calc = None, None
    vol_empty, vol_unit_empty = "#НД", "#НД"
    value_ok = '**'
    value_no_data = "#НД"
    # update_cols_names = ['vol_pre', 'vol_unit_pre', 'vol', 'vol_unit']
    update_cols_names = ['vol_calc', 'vol_unit_calc']
    if doze_group is None: return vol_calc, vol_unit_calc
    if doze_group in [0,1,2,4,5,6,7,8,9]:
        if doze_group == 0:
            # vol, vol_unit = vol_empty, vol_unit_empty
            # vol, vol_unit = value_ok, value_ok
            vol_calc, vol_unit_calc = value_ok, value_ok
        elif doze_group == 1:
            if form_standard is not None\
                and ((((type(form_standard) == str) or  (type(form_standard)== np.str_)) and (form_standard == "ГЕЛЬ ДЛЯ ПОДКОЖНОГО ВВЕДЕНИЯ"))\
                        or "ГЕЛЬ ДЛЯ ПОДКОЖНОГО ВВЕДЕНИЯ" in form_standard): # если список
                vol_calc, vol_unit_calc = value_ok, value_ok
            elif ls_unit_name is not None and ((type(ls_unit_name)==str) or (type(ls_unit_name)==np.str_)) and (ls_unit_name == "г лекарственной формы"):
                vol_calc, vol_unit_calc = pack_1_num, 'г'
            elif ls_unit_name is not None and ((type(ls_unit_name)==str) or (type(ls_unit_name)==np.str_)) and (ls_unit_name == "мг действующего вещества"):
                vol, vol_unit = value_no_data, value_no_data
            else:
                vol_calc, vol_unit_calc = value_no_data, value_no_data
    #             if ls_unit_name == "г лекарственной формы":
    #                 vol_calc, vol_unit_calc = pack_1_num, 'г'
    #             elif ls_unit_name == "мг действующего вещества":
    #                 # vol, vol_unit = vol_empty, vol_unit_empty + 'мг'
    #                 if ((type(form_standard) == str) or  (type(form_standard)== np.str_)) and (form_standard == "ГЕЛЬ ДЛЯ ПОДКОЖНОГО ВВЕДЕНИЯ"):
    #                 # ГЕЛЬ ДЛЯ ПОДКОЖНОГО ВВЕДЕНИЯ
    #                     # vol_calc, vol_unit_calc = value_ok, vol_unit_calc
    #                     vol_calc, vol_unit_calc = value_ok, value_ok
    #                 else:
    #                     vol_calc, vol_unit_calc = value_no_data, value_no_data
                
    #             else:
    #                 vol_calc, vol_unit_calc = value_no_data, value_no_data
        elif doze_group == 2:
            if ls_unit_name is not None and ((type(ls_unit_name)==str) or (type(ls_unit_name)==np.str_)) and (ls_unit_name == "кг"):
                vol_calc, vol_unit_calc = pack_1_num, 'кг'
            else:
                vol_calc, vol_unit_calc = value_no_data, value_no_data
        elif doze_group == 4:
            if ls_unit_name is not None and ((type(ls_unit_name)==str) or (type(ls_unit_name)==np.str_)) and (ls_unit_name == "мл"):
                vol_calc, vol_unit_calc = pack_1_num, 'мл'
            else:
                vol_calc, vol_unit_calc = value_no_data, value_no_data
        elif doze_group == 5:
            if ls_unit_name is not None and ((type(ls_unit_name)==str) or (type(ls_unit_name)==np.str_)) and (ls_unit_name == "мл"):
                vol_calc, vol_unit_calc = pack_1_num, 'мл'
            elif ls_unit_name is not None and ((type(ls_unit_name)==str) or (type(ls_unit_name)==np.str_)) and (ls_unit_name == "г лекарственной формы"):
                vol_calc, vol_unit_calc = pack_1_num, 'г'
            elif ls_unit_name is not None and ((type(ls_unit_name)==str) or (type(ls_unit_name)==np.str_)) and (ls_unit_name == "доз(а)"):
                vol_calc, vol_unit_calc = pack_1_num, 'доз(а)'
            else:
                vol_calc, vol_unit_calc = value_no_data, value_no_data
        elif doze_group == 6:
            if form_standard is not None\
                and ((((type(form_standard) == str) or  (type(form_standard)== np.str_)) and (form_standard == "ПОРОШОК ДЛЯ ИНГАЛЯЦИЙ ДОЗИРОВАННЫЙ"))\
                        or "ПОРОШОК ДЛЯ ИНГАЛЯЦИЙ ДОЗИРОВАННЫЙ" in form_standard): # если список
            # if ((type(form_standard) == str) or  (type(form_standard)== np.str_)) and (form_standard == "ПОРОШОК ДЛЯ ИНГАЛЯЦИЙ ДОЗИРОВАННЫЙ"):
                # после восстанвления из Excel надо преобразовать строчный тип consumer_total во float, 
                # посокльку считываемый consumer_total_kis - float
                if debug: print(f"calc_volume: type(consumer_total): {type(consumer_total)}, type(consumer_total_kis): {type(consumer_total_kis)}")
                if (type(consumer_total) ==float) and (type(consumer_total_kis) ==float):
                    if debug: print(f"calc_volume: (type(consumer_total) ==float) and (type(consumer_total_kis) ==float)")
                    if (consumer_total == consumer_total_kis):
                        # vol, vol_unit = vol_empty, vol_unit_empty
                        # vol_calc, vol_unit_calc = value_ok, vol_unit_calc
                        vol_calc, vol_unit_calc = value_ok, value_ok
                    else:
                        vol_calc, vol_unit_calc = pack_1_num, ls_unit_name
                elif ((type(consumer_total) == str) or (type(consumer_total) == np.str_)) and ((type(consumer_total_kis) ==float) or (type(consumer_total_kis) ==np.float64)):
                    # ветка при восстановлении данных из Excel
                    if debug: print(f"calc_volume: ((type(consumer_total) == str) or (type(consumer_total) == np.str_)) and ((type(consumer_total_kis) ==float) or (type(consumer_total_kis) ==np.float64))")
                    try:
                        consumer_total = float(consumer_total)
                        if (consumer_total == consumer_total_kis):
                            # vol, vol_unit = vol_empty, vol_unit_empty
                            # vol_calc, vol_unit_calc = value_ok, vol_unit_calc
                            vol_calc, vol_unit_calc = value_ok, value_ok
                        else:
                            vol_calc, vol_unit_calc = pack_1_num, ls_unit_name
                    except Exception as err:
                        print(f"calc_volume: 'consumer_total = float(consumer_total) error': {i_row}", err)
                        vol_calc, vol_unit_calc = vol_empty + '#ERR', vol_unit_empty + '#ERR'

            elif dosage_parsing_unit in ["мл/доз(а)", "мг/доз(а)", "МЕ/доз(а)"]:
                vol_calc, vol_unit_calc = pack_1_num, ls_unit_name
            else:
                # vol, vol_unit = vol_empty, vol_unit_empty
                vol_calc, vol_unit_calc = value_ok, vol_unit_calc
        elif doze_group == 7:
            if ls_unit_name is not None and ((type(ls_unit_name)==str) or (type(ls_unit_name)==np.str_)) and (ls_unit_name == "мл"):
                vol_calc, vol_unit_calc = pack_1_num, 'мл'
            elif ls_unit_name is not None and ((type(ls_unit_name)==str) or (type(ls_unit_name)==np.str_)) and (ls_unit_name == "г лекарственной формы"):
                vol_calc, vol_unit_calc = pack_1_num, 'г'
            elif ls_unit_name is not None and ((type(ls_unit_name)==str) or (type(ls_unit_name)==np.str_)) and (ls_unit_name == "доз(а)"):
                vol_calc, vol_unit_calc = pack_1_num, 'доз(а)'
            else:
                vol_calc, vol_unit_calc = value_no_data, value_no_data
        elif doze_group == 8:
            # if ls_unit_name == "г лекарственной формы":
            #     vol, vol_unit = pack_1_num, 'г'
            # elif ls_unit_name == "г действующего вещества":
            #     vol, vol_unit = pack_1_num, 'г'
            # else:
            #     vol, vol_unit = vol_empty, vol_unit_empty
            if ls_unit_name is not None and ((type(ls_unit_name)==str) or (type(ls_unit_name)==np.str_)) and (ls_unit_name in ["г лекарственной формы", "г действующего вещества"]):
                # если "dosage_standard_unit" = ЕД/г, мг/г
                if dosage_parsing_unit in ['ЕД/г', 'мг/г', 'МЕ/г']:
                    vol_calc, vol_unit_calc = pack_1_num, 'г'
                else:
                    vol_calc, vol_unit_calc = value_ok, value_ok
            else:
                vol_calc, vol_unit_calc = value_no_data, value_no_data

        elif doze_group == 9:
            # vol, vol_unit = vol_empty, vol_unit_empty
            # vol_calc, vol_unit_calc = value_ok, vol_unit_calc
            vol_calc, vol_unit_calc = value_ok, value_ok
        
        # if doze_group in [0,1,2,4,5,6,7,8,9]
        vol_calc, vol_unit_calc = update_vol_exclude(vol_calc, vol_unit_calc, mass_volume_name, mass_volume_num, debug)
        if debug: print(f"calc_volume: doze_group: {doze_group}, vol_calc: {vol_calc}, vol_unit_calc: {vol_unit_calc}")    
            # if debug: print(f"calc_volume: doze_group: {doze_group}, vol: {vol}, vol_unit: {vol_unit}")
    
    return vol_calc, vol_unit_calc

def calc_volume_02(doze_group, ls_unit_name, lp_pack_1_num, pack_1_num, 
                form_standard, consumer_total, consumer_total_kis, dosage_parsing_unit, mass_volume_name, 
                mass_volume_num,
                debug=False):
                # cnt, debug=False, write=False):
    # 919 only size-1 arrays can be converted to Python scalars
    # global smnn_list_df, klp_list_dict_df, zvnlp_df, znvlp_date  
    
    # vol_pre, vol_unit_pre, vol, vol_unit = None, None, None, None
    # vol, vol_unit = None, None
    vol_calc, vol_unit_calc = None, None
    vol_empty, vol_unit_empty = "#НД", "#НД"
    value_ok = '**'
    value_no_data = "#НД"
    # update_cols_names = ['vol_pre', 'vol_unit_pre', 'vol', 'vol_unit']
    update_cols_names = ['vol_calc', 'vol_unit_calc']
    if doze_group is None: return vol_calc, vol_unit_calc
    if doze_group in [0,1,2,4,5,6,7,8,9]:
        if doze_group == 0:
            # vol, vol_unit = vol_empty, vol_unit_empty
            # vol, vol_unit = value_ok, value_ok
            vol_calc, vol_unit_calc = value_ok, value_ok
        elif doze_group == 1:
            if form_standard is not None\
                and ((((type(form_standard) == str) or  (type(form_standard)== np.str_)) and (form_standard == "ГЕЛЬ ДЛЯ ПОДКОЖНОГО ВВЕДЕНИЯ"))\
                        or "ГЕЛЬ ДЛЯ ПОДКОЖНОГО ВВЕДЕНИЯ" in form_standard): # если список
                vol_calc, vol_unit_calc = value_ok, value_ok
            elif ls_unit_name is not None and ((type(ls_unit_name)==str) or (type(ls_unit_name)==np.str_)) and (ls_unit_name == "г лекарственной формы"):
                # vol_calc, vol_unit_calc = pack_1_num, 'г'
                vol_calc, vol_unit_calc = lp_pack_1_num, 'г'
            elif ls_unit_name is not None and ((type(ls_unit_name)==str) or (type(ls_unit_name)==np.str_)) and (ls_unit_name == "мг действующего вещества"):
                vol, vol_unit = value_no_data, value_no_data
            else:
                vol_calc, vol_unit_calc = value_no_data, value_no_data
    #             if ls_unit_name == "г лекарственной формы":
    #                 vol_calc, vol_unit_calc = pack_1_num, 'г'
    #             elif ls_unit_name == "мг действующего вещества":
    #                 # vol, vol_unit = vol_empty, vol_unit_empty + 'мг'
    #                 if ((type(form_standard) == str) or  (type(form_standard)== np.str_)) and (form_standard == "ГЕЛЬ ДЛЯ ПОДКОЖНОГО ВВЕДЕНИЯ"):
    #                 # ГЕЛЬ ДЛЯ ПОДКОЖНОГО ВВЕДЕНИЯ
    #                     # vol_calc, vol_unit_calc = value_ok, vol_unit_calc
    #                     vol_calc, vol_unit_calc = value_ok, value_ok
    #                 else:
    #                     vol_calc, vol_unit_calc = value_no_data, value_no_data
                
    #             else:
    #                 vol_calc, vol_unit_calc = value_no_data, value_no_data
        elif doze_group == 2:
            if ls_unit_name is not None and ((type(ls_unit_name)==str) or (type(ls_unit_name)==np.str_)) and (ls_unit_name == "кг"):
                # vol_calc, vol_unit_calc = pack_1_num, 'кг'
                vol_calc, vol_unit_calc = lp_pack_1_num, 'кг'
            else:
                vol_calc, vol_unit_calc = value_no_data, value_no_data
        elif doze_group == 4:
            if ls_unit_name is not None and ((type(ls_unit_name)==str) or (type(ls_unit_name)==np.str_)) and (ls_unit_name == "мл"):
                # vol_calc, vol_unit_calc = pack_1_num, 'мл'
                vol_calc, vol_unit_calc = lp_pack_1_num, 'мл'
            else:
                vol_calc, vol_unit_calc = value_no_data, value_no_data
        elif doze_group == 5:
            if ls_unit_name is not None and ((type(ls_unit_name)==str) or (type(ls_unit_name)==np.str_)) and (ls_unit_name == "мл"):
                # vol_calc, vol_unit_calc = pack_1_num, 'мл'
                vol_calc, vol_unit_calc = lp_pack_1_num, 'мл'
            elif ls_unit_name is not None and ((type(ls_unit_name)==str) or (type(ls_unit_name)==np.str_)) and (ls_unit_name == "г лекарственной формы"):
                # vol_calc, vol_unit_calc = pack_1_num, 'г'
                vol_calc, vol_unit_calc = lp_pack_1_num, 'г'
            elif ls_unit_name is not None and ((type(ls_unit_name)==str) or (type(ls_unit_name)==np.str_)) and (ls_unit_name == "доз(а)"):
                # vol_calc, vol_unit_calc = pack_1_num, 'доз(а)'
                vol_calc, vol_unit_calc = lp_pack_1_num, 'доз(а)'
            else:
                vol_calc, vol_unit_calc = value_no_data, value_no_data
        elif doze_group == 6:
            if form_standard is not None\
                and ((((type(form_standard) == str) or  (type(form_standard)== np.str_)) and (form_standard == "ПОРОШОК ДЛЯ ИНГАЛЯЦИЙ ДОЗИРОВАННЫЙ"))\
                        or "ПОРОШОК ДЛЯ ИНГАЛЯЦИЙ ДОЗИРОВАННЫЙ" in form_standard): # если список
            # if ((type(form_standard) == str) or  (type(form_standard)== np.str_)) and (form_standard == "ПОРОШОК ДЛЯ ИНГАЛЯЦИЙ ДОЗИРОВАННЫЙ"):
                # после восстанвления из Excel надо преобразовать строчный тип consumer_total во float, 
                # посокльку считываемый consumer_total_kis - float
                if debug: print(f"calc_volume: type(consumer_total): {type(consumer_total)}, type(consumer_total_kis): {type(consumer_total_kis)}")
                if (type(consumer_total) ==float) and (type(consumer_total_kis) ==float):
                    if debug: print(f"calc_volume: (type(consumer_total) ==float) and (type(consumer_total_kis) ==float)")
                    if (consumer_total == consumer_total_kis):
                        # vol, vol_unit = vol_empty, vol_unit_empty
                        # vol_calc, vol_unit_calc = value_ok, vol_unit_calc
                        vol_calc, vol_unit_calc = value_ok, value_ok
                    else:
                        vol_calc, vol_unit_calc = pack_1_num, ls_unit_name
                elif ((type(consumer_total) == str) or (type(consumer_total) == np.str_)) and ((type(consumer_total_kis) ==float) or (type(consumer_total_kis) ==np.float64)):
                    # ветка при восстановлении данных из Excel
                    if debug: print(f"calc_volume: ((type(consumer_total) == str) or (type(consumer_total) == np.str_)) and ((type(consumer_total_kis) ==float) or (type(consumer_total_kis) ==np.float64))")
                    try:
                        consumer_total = float(consumer_total)
                        if (consumer_total == consumer_total_kis):
                            # vol, vol_unit = vol_empty, vol_unit_empty
                            # vol_calc, vol_unit_calc = value_ok, vol_unit_calc
                            vol_calc, vol_unit_calc = value_ok, value_ok
                        else:
                            # vol_calc, vol_unit_calc = pack_1_num, ls_unit_name
                            vol_calc, vol_unit_calc = lp_pack_1_num, ls_unit_name
                    except Exception as err:
                        print(f"calc_volume: 'consumer_total = float(consumer_total) error': {i_row}", err)
                        vol_calc, vol_unit_calc = vol_empty + '#ERR', vol_unit_empty + '#ERR'

            elif dosage_parsing_unit in ["мл/доз(а)", "мг/доз(а)", "МЕ/доз(а)"]:
                # vol_calc, vol_unit_calc = pack_1_num, ls_unit_name
                vol_calc, vol_unit_calc = lp_pack_1_num, ls_unit_name
            else:
                # vol, vol_unit = vol_empty, vol_unit_empty
                vol_calc, vol_unit_calc = value_ok, value_ok # vol_unit_calc
        elif doze_group == 7:
            if ls_unit_name is not None and ((type(ls_unit_name)==str) or (type(ls_unit_name)==np.str_)) and (ls_unit_name == "мл"):
                # vol_calc, vol_unit_calc = pack_1_num, 'мл'
                vol_calc, vol_unit_calc = lp_pack_1_num, 'мл'
            elif ls_unit_name is not None and ((type(ls_unit_name)==str) or (type(ls_unit_name)==np.str_)) and (ls_unit_name == "г лекарственной формы"):
                # vol_calc, vol_unit_calc = pack_1_num, 'г'
                vol_calc, vol_unit_calc = lp_pack_1_num, 'г'
            elif ls_unit_name is not None and ((type(ls_unit_name)==str) or (type(ls_unit_name)==np.str_)) and (ls_unit_name == "доз(а)"):
                # vol_calc, vol_unit_calc = pack_1_num, 'доз(а)'
                vol_calc, vol_unit_calc = lp_pack_1_num, 'доз(а)'
            else:
                vol_calc, vol_unit_calc = value_no_data, value_no_data
        elif doze_group == 8:
            # if ls_unit_name == "г лекарственной формы":
            #     vol, vol_unit = pack_1_num, 'г'
            # elif ls_unit_name == "г действующего вещества":
            #     vol, vol_unit = pack_1_num, 'г'
            # else:
            #     vol, vol_unit = vol_empty, vol_unit_empty
            if ls_unit_name is not None and ((type(ls_unit_name)==str) or (type(ls_unit_name)==np.str_)) and (ls_unit_name in ["г лекарственной формы", "г действующего вещества"]):
                # если "dosage_standard_unit" = ЕД/г, мг/г
                if dosage_parsing_unit in ['ЕД/г', 'мг/г', 'МЕ/г']:
                    # vol_calc, vol_unit_calc = pack_1_num, 'г'
                    vol_calc, vol_unit_calc = lp_pack_1_num, 'г'
                else:
                    vol_calc, vol_unit_calc = value_ok, value_ok
            else:
                vol_calc, vol_unit_calc = value_no_data, value_no_data

        elif doze_group == 9:
            # vol, vol_unit = vol_empty, vol_unit_empty
            # vol_calc, vol_unit_calc = value_ok, vol_unit_calc
            vol_calc, vol_unit_calc = value_ok, value_ok
        
        # if doze_group in [0,1,2,4,5,6,7,8,9]
        vol_calc, vol_unit_calc = update_vol_exclude(vol_calc, vol_unit_calc, mass_volume_name, mass_volume_num, debug)
        if debug: print(f"calc_volume: doze_group: {doze_group}, vol_calc: {vol_calc}, vol_unit_calc: {vol_unit_calc}")    
            # if debug: print(f"calc_volume: doze_group: {doze_group}, vol: {vol}, vol_unit: {vol_unit}")
    
    return vol_calc, vol_unit_calc

def calc_volume(doze_group, ls_unit_name, pack_1_num, 
                form_standard, consumer_total, consumer_total_kis, dosage_parsing_unit, mass_volume_name, 
                mass_volume_num,
                debug=False):
                # cnt, debug=False, write=False):
    # 919 only size-1 arrays can be converted to Python scalars
    # global smnn_list_df, klp_list_dict_df, zvnlp_df, znvlp_date  
    
    # vol_pre, vol_unit_pre, vol, vol_unit = None, None, None, None
    # vol, vol_unit = None, None
    vol_calc, vol_unit_calc = None, None
    vol_empty, vol_unit_empty = "#НД", "#НД"
    value_ok = '**'
    value_no_data = "#НД"
    # update_cols_names = ['vol_pre', 'vol_unit_pre', 'vol', 'vol_unit']
    update_cols_names = ['vol_calc', 'vol_unit_calc']
    if doze_group is None: return vol_calc, vol_unit_calc
    if doze_group in [0,1,2,4,5,6,7,8,9]:
        if doze_group == 0:
            # vol, vol_unit = vol_empty, vol_unit_empty
            # vol, vol_unit = value_ok, value_ok
            vol_calc, vol_unit_calc = value_ok, value_ok
        elif doze_group == 1:
            if form_standard is not None\
                and ((((type(form_standard) == str) or  (type(form_standard)== np.str_)) and (form_standard == "ГЕЛЬ ДЛЯ ПОДКОЖНОГО ВВЕДЕНИЯ"))\
                        or "ГЕЛЬ ДЛЯ ПОДКОЖНОГО ВВЕДЕНИЯ" in form_standard): # если список
                vol_calc, vol_unit_calc = value_ok, value_ok
            elif ls_unit_name is not None and ((type(ls_unit_name)==str) or (type(ls_unit_name)==np.str_)) and (ls_unit_name == "г лекарственной формы"):
                vol_calc, vol_unit_calc = pack_1_num, 'г'
            elif ls_unit_name is not None and ((type(ls_unit_name)==str) or (type(ls_unit_name)==np.str_)) and (ls_unit_name == "мг действующего вещества"):
                vol, vol_unit = value_no_data, value_no_data
            else:
                vol_calc, vol_unit_calc = value_no_data, value_no_data
    #             if ls_unit_name == "г лекарственной формы":
    #                 vol_calc, vol_unit_calc = pack_1_num, 'г'
    #             elif ls_unit_name == "мг действующего вещества":
    #                 # vol, vol_unit = vol_empty, vol_unit_empty + 'мг'
    #                 if ((type(form_standard) == str) or  (type(form_standard)== np.str_)) and (form_standard == "ГЕЛЬ ДЛЯ ПОДКОЖНОГО ВВЕДЕНИЯ"):
    #                 # ГЕЛЬ ДЛЯ ПОДКОЖНОГО ВВЕДЕНИЯ
    #                     # vol_calc, vol_unit_calc = value_ok, vol_unit_calc
    #                     vol_calc, vol_unit_calc = value_ok, value_ok
    #                 else:
    #                     vol_calc, vol_unit_calc = value_no_data, value_no_data
                
    #             else:
    #                 vol_calc, vol_unit_calc = value_no_data, value_no_data
        elif doze_group == 2:
            if ls_unit_name is not None and ((type(ls_unit_name)==str) or (type(ls_unit_name)==np.str_)) and (ls_unit_name == "кг"):
                vol_calc, vol_unit_calc = pack_1_num, 'кг'
            else:
                vol_calc, vol_unit_calc = value_no_data, value_no_data
        elif doze_group == 4:
            if ls_unit_name is not None and ((type(ls_unit_name)==str) or (type(ls_unit_name)==np.str_)) and (ls_unit_name == "мл"):
                vol_calc, vol_unit_calc = pack_1_num, 'мл'
            else:
                vol_calc, vol_unit_calc = value_no_data, value_no_data
        elif doze_group == 5:
            if ls_unit_name is not None and ((type(ls_unit_name)==str) or (type(ls_unit_name)==np.str_)) and (ls_unit_name == "мл"):
                vol_calc, vol_unit_calc = pack_1_num, 'мл'
            elif ls_unit_name is not None and ((type(ls_unit_name)==str) or (type(ls_unit_name)==np.str_)) and (ls_unit_name == "г лекарственной формы"):
                vol_calc, vol_unit_calc = pack_1_num, 'г'
            elif ls_unit_name is not None and ((type(ls_unit_name)==str) or (type(ls_unit_name)==np.str_)) and (ls_unit_name == "доз(а)"):
                vol_calc, vol_unit_calc = pack_1_num, 'доз(а)'
            else:
                vol_calc, vol_unit_calc = value_no_data, value_no_data
        elif doze_group == 6:
            if form_standard is not None\
                and ((((type(form_standard) == str) or  (type(form_standard)== np.str_)) and (form_standard == "ПОРОШОК ДЛЯ ИНГАЛЯЦИЙ ДОЗИРОВАННЫЙ"))\
                        or "ПОРОШОК ДЛЯ ИНГАЛЯЦИЙ ДОЗИРОВАННЫЙ" in form_standard): # если список
            # if ((type(form_standard) == str) or  (type(form_standard)== np.str_)) and (form_standard == "ПОРОШОК ДЛЯ ИНГАЛЯЦИЙ ДОЗИРОВАННЫЙ"):
                # после восстанвления из Excel надо преобразовать строчный тип consumer_total во float, 
                # посокльку считываемый consumer_total_kis - float
                if debug: print(f"calc_volume: type(consumer_total): {type(consumer_total)}, type(consumer_total_kis): {type(consumer_total_kis)}")
                if (type(consumer_total) ==float) and (type(consumer_total_kis) ==float):
                    if debug: print(f"calc_volume: (type(consumer_total) ==float) and (type(consumer_total_kis) ==float)")
                    if (consumer_total == consumer_total_kis):
                        # vol, vol_unit = vol_empty, vol_unit_empty
                        # vol_calc, vol_unit_calc = value_ok, vol_unit_calc
                        vol_calc, vol_unit_calc = value_ok, value_ok
                    else:
                        vol_calc, vol_unit_calc = pack_1_num, ls_unit_name
                elif ((type(consumer_total) == str) or (type(consumer_total) == np.str_)) and ((type(consumer_total_kis) ==float) or (type(consumer_total_kis) ==np.float64)):
                    # ветка при восстановлении данных из Excel
                    if debug: print(f"calc_volume: ((type(consumer_total) == str) or (type(consumer_total) == np.str_)) and ((type(consumer_total_kis) ==float) or (type(consumer_total_kis) ==np.float64))")
                    try:
                        consumer_total = float(consumer_total)
                        if (consumer_total == consumer_total_kis):
                            # vol, vol_unit = vol_empty, vol_unit_empty
                            # vol_calc, vol_unit_calc = value_ok, vol_unit_calc
                            vol_calc, vol_unit_calc = value_ok, value_ok
                        else:
                            vol_calc, vol_unit_calc = pack_1_num, ls_unit_name
                    except Exception as err:
                        print(f"calc_volume: 'consumer_total = float(consumer_total) error': {i_row}", err)
                        vol_calc, vol_unit_calc = vol_empty + '#ERR', vol_unit_empty + '#ERR'

            elif dosage_parsing_unit in ["мл/доз(а)", "мг/доз(а)", "МЕ/доз(а)"]:
                vol_calc, vol_unit_calc = pack_1_num, ls_unit_name
            else:
                # vol, vol_unit = vol_empty, vol_unit_empty
                vol_calc, vol_unit_calc = value_ok, vol_unit_calc
        elif doze_group == 7:
            if ls_unit_name is not None and ((type(ls_unit_name)==str) or (type(ls_unit_name)==np.str_)) and (ls_unit_name == "мл"):
                vol_calc, vol_unit_calc = pack_1_num, 'мл'
            elif ls_unit_name is not None and ((type(ls_unit_name)==str) or (type(ls_unit_name)==np.str_)) and (ls_unit_name == "г лекарственной формы"):
                vol_calc, vol_unit_calc = pack_1_num, 'г'
            elif ls_unit_name is not None and ((type(ls_unit_name)==str) or (type(ls_unit_name)==np.str_)) and (ls_unit_name == "доз(а)"):
                vol_calc, vol_unit_calc = pack_1_num, 'доз(а)'
            else:
                vol_calc, vol_unit_calc = value_no_data, value_no_data
        elif doze_group == 8:
            # if ls_unit_name == "г лекарственной формы":
            #     vol, vol_unit = pack_1_num, 'г'
            # elif ls_unit_name == "г действующего вещества":
            #     vol, vol_unit = pack_1_num, 'г'
            # else:
            #     vol, vol_unit = vol_empty, vol_unit_empty
            if ls_unit_name is not None and ((type(ls_unit_name)==str) or (type(ls_unit_name)==np.str_)) and (ls_unit_name in ["г лекарственной формы", "г действующего вещества"]):
                # если "dosage_standard_unit" = ЕД/г, мг/г
                if dosage_parsing_unit in ['ЕД/г', 'мг/г', 'МЕ/г']:
                    vol_calc, vol_unit_calc = pack_1_num, 'г'
                else:
                    vol_calc, vol_unit_calc = value_ok, value_ok
            else:
                vol_calc, vol_unit_calc = value_no_data, value_no_data

        elif doze_group == 9:
            # vol, vol_unit = vol_empty, vol_unit_empty
            # vol_calc, vol_unit_calc = value_ok, vol_unit_calc
            vol_calc, vol_unit_calc = value_ok, value_ok
        
        # if doze_group in [0,1,2,4,5,6,7,8,9]
        vol_calc, vol_unit_calc = update_vol_exclude(vol_calc, vol_unit_calc, mass_volume_name, mass_volume_num, debug)
        if debug: print(f"calc_volume: doze_group: {doze_group}, vol_calc: {vol_calc}, vol_unit_calc: {vol_unit_calc}")    
            # if debug: print(f"calc_volume: doze_group: {doze_group}, vol: {vol}, vol_unit: {vol_unit}")
    
    return vol_calc, vol_unit_calc

def control_vol(doze_group, vol, vol_unit, vol_klp, vol_unit_klp, debug=False):
    vol_calc, vol_unit_calc, c_vol, c_vol_unit = None, None, None, None
    value_ok = '**'
    value_empty = '#НД'
    name_ei_lp = None
    
    if doze_group is not None:
        if doze_group in [0, 6, 8, 9, 10]: # 10+
            # если doze_group = 0 => и  vol = <пусто> => vol* = **, vol_unit* = **
            if vol is None:
                vol_calc, vol_unit_calc = value_ok, value_ok
            else:
                vol_calc, vol_unit_calc = vol, vol_unit
        elif doze_group in [1,2,3,4,5,7,11]: # 11+
            # если doze_group = 0 => и  vol = <пусто> => vol* = #НД , vol_unit* =  #НД
            if vol is None:
                vol_calc, vol_unit_calc = value_empty, value_empty
            else:
                vol_calc, vol_unit_calc = vol, vol_unit
                
        if vol_unit is not None and vol_unit in ['кг', 'л']:
            if vol_calc is not None:
                vol_calc = vol_calc * 1000
                vol_unit_calc = 'мл'
        
        # если vol* = vol_calc (или есть в списке)=> ИСТИНА, иначе ЛОЖЬ
        # если vol* = vol_calc (или есть в списке)=> ИСТИНА, иначе ЛОЖЬ
        if (((type(vol_klp)==float) or (type(vol_klp)==np.float64)) and (vol_calc == vol_klp)) \
            or (((type(vol_klp)==list) or (type(vol_klp)==np.ndarray)) and (vol_calc in vol_klp))\
            or (((type(vol_klp)==str) or (type(vol_klp)==np.str_))\
                and ((type(vol_calc)==str) or (type(vol_calc)==np.str_))\
                and (vol_calc == vol_klp)):
            c_vol = True
        else:
            c_vol = False
            
        # если vol_unit* = vol_unit_calc => ИСТИНА, иначе ЛОЖЬ
        if vol_unit_calc is not None and (((type(vol_unit_klp)==str) or (type(vol_unit_klp)==np.str_)) and (vol_unit_calc == vol_unit_klp)):
            c_vol_unit = True
        else:
            c_vol_unit = False
        
    return vol_calc, vol_unit_calc, c_vol, c_vol_unit

def compare_vol_norm_parsing(doze_group, lp_pack_1_num, lp_pack_2_num, lp_unit_okei, lp_unit, 
                             lp_consumer_total, lp_consumer_total_calc, consumer_total_parsing,
                             vol,
                             debug=False):
    if debug: print(f"compare_vol_norm_parsing: ", doze_group, lp_pack_1_num, lp_pack_2_num, lp_unit_okei, lp_unit, lp_consumer_total, lp_consumer_total_calc)
    c_vol = None #  volume controlling
    name_ei_lp = None
    if doze_group is not None:
        c_vol = False
        if doze_group in [0,9,10]:
            if ((type(lp_consumer_total_calc) == float) or (type(lp_consumer_total_calc) == np.float64)) \
                and ((type(consumer_total_parsing)==float) or (type(consumer_total_parsing)==np.float64)) \
                and (lp_consumer_total_calc == consumer_total_parsing):
                c_vol = True
                name_ei_lp = lp_unit
                # name_ei_lp = lp_unit_okei if (type(lp_unit_okei)==str or type(lp_unit_okei)==mp.str_) + lp_unit
            elif ((type(lp_consumer_total_calc) == list) or (type(lp_consumer_total_calc) == np.ndarray)) \
                and ((type(consumer_total_parsing)==float) or (type(consumer_total_parsing)==np.float64)):
                # and (type(consumer_total_parsing)==float) and consumer_total_parsing in lp_consumer_total_calc:
                try:
                    # if consumer_total_parsing in lp_consumer_total_calc:
                    if  np.isin(lp_consumer_total_calc, consumer_total_parsing).any():
                        c_vol = True
                        name_ei_lp = lp_unit
                except Exception as err:
                    print(err)
                    print(f"compare_vol_norm_parsing: consumer_total_parsing: {consumer_total_parsing}, lp_consumer_total_calc: {lp_consumer_total_calc}")
                    print(f"compare_vol_norm_parsing: type(consumer_total_parsing): {type(consumer_total_parsing)}, type(lp_consumer_total_calc): {type(lp_consumer_total_calc)}")
                    sys.exit(2)
        elif doze_group in [1,3,4,5,7,8,11]:
            # if (type(lp_pack_2_num) == str) and ((type(consumer_total_parsing)==float) or (type(consumer_total_parsing)==np.float64))\
            if ((type(lp_pack_2_num) == float) or (type(lp_pack_2_num) == np.float64)) and ((type(consumer_total_parsing)==float) or (type(consumer_total_parsing)==np.float64))\
                and (lp_pack_2_num == consumer_total_parsing):
                # and (float(lp_pack_2_num) == consumer_total_parsing):
                if lp_pack_1_num is not None and vol is not None:
                    # if (type(lp_pack_1_num) == str) or (type(lp_pack_1_num) ==np.str_):
                    if (type(lp_pack_1_num) == float) or (type(lp_pack_1_num) ==np.float64):
                        # if float(vol) == float(lp_pack_1_num):
                        if vol == lp_pack_1_num:
                            name_ei_lp = lp_unit
                            c_vol = True
                        else: 
                            name_ei_lp = 'vol != lp_pack_1_num'
                            c_vol = False
                    elif (type(lp_pack_1_num) == list) or (type(lp_pack_1_num) == np.ndarray):
                        # if float(vol) in [float(n) for n in lp_pack_1_num]:
                        # if vol in [float(n) for n in lp_pack_1_num]:
                        if vol in lp_pack_1_num:
                            name_ei_lp = lp_unit
                            c_vol = True
                        else:
                            name_ei_lp = 'vol != lp_pack_1_num'
                            c_vol = False
            elif ((type(lp_pack_2_num) == list) or (type(lp_pack_2_num) == np.ndarray)) \
                and ((type(consumer_total_parsing)==float) or (type(consumer_total_parsing)==np.float64)) \
                and consumer_total_parsing in lp_pack_2_num:
                # and consumer_total_parsing in [float(n) for n in lp_pack_2_num]:
                # if (type(lp_pack_1_num) == str) or (type(lp_pack_1_num) ==np.str_):
                if (type(lp_pack_1_num) == float) or (type(lp_pack_1_num) ==np.float64):
                    # if lp_pack_1_num is not None and vol is not None and (float(vol) == float(lp_pack_1_num)):
                    if lp_pack_1_num is not None and vol is not None and (vol == lp_pack_1_num):
                        name_ei_lp = lp_unit
                        c_vol = True
                    else: 
                        name_ei_lp = 'vol != lp_pack_1_num'
                        c_vol = False
                elif (type(lp_pack_1_num) ==list) or (type(lp_pack_1_num) ==np.ndarray):
                    # if lp_pack_1_num is not None and vol is not None and  float(vol) in [float(n) for n in lp_pack_1_num]:
                    # if lp_pack_1_num is not None and vol is not None and  float(vol) in [n for n in lp_pack_1_num]:
                    if lp_pack_1_num is not None and vol is not None and  vol in lp_pack_1_num:
                        name_ei_lp = lp_unit
                        c_vol = True
                    else:
                        name_ei_lp = 'vol != lp_pack_1_num'
                        c_vol = False
                #     pass
                # pass
        elif doze_group in [2]:
            pass
        elif doze_group in [6]:
            pass
    return c_vol, name_ei_lp

def calc_ls_totals(dosage_parsing_value, dosage_parsing_unit, vol_calc, vol_unit_calc, debug=False):
    ls_doze, ls_doze_unit, ls_vol, ls_vol_unit, ls_doze_vol, ls_doze_vol_unit = None, None, None, None, None, None
    value_ok = '**'
    value_no_data = '#НД'
    
    ls_doze, ls_doze_unit = dosage_parsing_value, dosage_parsing_unit
    ls_vol, ls_vol_unit = vol_calc, vol_unit_calc
        
    # ls_doze_vol, ls_doze_vol_unit
    if ((type(ls_vol) == str) or (type(ls_vol) == np.str)) and (ls_vol == value_ok):
        # ls_doze_vol, ls_doze_vol_unit = ls_doze, ls_doze_unit
        ls_doze_vol = ls_doze
        ls_doze_vol_unit = ls_doze_unit
        if ls_doze_vol_unit is not None and ((type(ls_doze_vol_unit)==str) or (type(ls_doze_vol_unit)==np.str_))\
            and '/' in ls_doze_vol_unit:
            ls_doze_vol_unit = ls_doze_vol_unit[:ls_doze_vol_unit.rfind('/')]
    elif (type(ls_doze) == str) or (type(ls_doze) == np.str) and (ls_doze == '~'):
        ls_doze_vol, ls_doze_vol_unit = ls_doze, '~'
    
    elif ((type(ls_doze_unit) == str) or (type(ls_doze_unit) == np.str)) \
        and ls_vol_unit is not None and ('/' in ls_doze_unit):
        if (ls_doze_unit[ls_doze_unit.rfind('/') + 1:] == ls_vol_unit) \
            or ((ls_doze_unit[ls_doze_unit.rfind('/') + 1:]=='доза') and (ls_vol_unit =='доз(а)')):
            # print("(ls_doze_unit[ls_doze_unit.rfind('/') + 1:] == ls_vol_unit)")
            try:
                ls_doze_vol = float(ls_doze) * float(ls_vol)
                # ls_doze_vol_unit = ls_doze_unit
                ls_doze_vol_unit = ls_doze_unit[:ls_doze_unit.rfind('/')]
            except Exception as err:
                print("calc_ls_totals:", err)
        else:
            ls_doze_vol, ls_doze_vol_unit = value_no_data, value_no_data
    else:
        ls_doze_vol, ls_doze_vol_unit = value_no_data, value_no_data
                                                                  
    return ls_doze, ls_doze_unit, ls_vol, ls_vol_unit, ls_doze_vol, ls_doze_vol_unit


mis_position_col_name = 'Наименование КИС/МИС '
# Wall time: 9.19 s
def get_tn_ru_ext_from_dict(tn_lat_ext, tn_lat):
    tn_ru_ext = None
    if tn_lat_ext is not None:
        tn_ru_ext_dict = dict__tn_lat_ext__tn_ru_orig.get(tn_lat_ext)
        if tn_ru_ext_dict is not None:
            tn_ru_ext = tn_ru_ext_dict["positions"][0]["tn_ru_orig"]

    elif tn_lat is not None:
        tn_ru_dict = dict__tn_lat_ext__tn_ru_orig.get(tn_lat)
        if tn_ru_dict is not None:
            tn_ru_ext = tn_ru_dict["positions"][0]["tn_ru_orig"]
    return tn_ru_ext

def choice_tn(tn_selected):
    tn_true = None
    if tn_selected is None: return None
    if ((type(tn_selected)==str) or (type(tn_selected)==np.str_)):
        return tn_selected
    if (type(tn_selected)==list): # спсиоск сам делаю не np.ndarray
        tn_selected = sorted(tn_selected, key=len, reverse=True)
        tn_true = tn_selected[0]
        return tn_true
    else: return tn_true

def print_debug(  mis_position, tn_ru, tn_lat, tn_ru_ext, tn_lat_ext, tn_ru_orig, tn_ru_ext_clean, 
        tn_selected, tn_true,
        tn_by_tn, mnn_by_tn,
        tn_ru_clean, 
        pharm_form_type, pharm_form, 
        mnn_from_tn_ru_ext,  mnn_local_dict, mnn_true, 
        ath_name, ath_code, is_znvlp, is_narcotic, form_standard,
        doze_group, doze_proc, doze, doze_unit, pseudo_vol, pseudo_vol_unit, complex_doze_list, complex_doze_str, vol, vol_unit,
        pack_1_form_unify, pack_1_form,  pack_1_num, pack_2_form_unify, pack_2_form, pack_2_num, n_packs_str, consumer_total_parsing,
        dosage_standard_value_str, dosage_standard_value, dosage_standard_unit, 
        dosage_standard_value_str_refrmt,
        dosage_parsing_value_str, dosage_parsing_value, dosage_parsing_unit,
        dosage_correct_value, dosage_correct_unit,
        c_doze,
        lp_pack_1_num, lp_pack_1_name, lp_pack_2_num, lp_pack_2_name, lp_unit_okei_name, lp_unit_name, lp_consumer_total, lp_consumer_total_calc,
        is_dosed, mass_volume_num, mass_volume_name,
        vol_klp, vol_unit_klp,
        vol_calc, vol_unit_calc,
        c_vol, c_vol_unit, name_ei_lp,
        c_pack, c_mnn, c_form,
        ls_doze, ls_doze_unit, ls_vol, ls_vol_unit, ls_doze_vol, ls_doze_vol_unit
               ):
    print(mis_position)
    print(f"doze_group: {doze_group}, doze_proc: {doze_proc}, doze: {doze}, doze_unit: '{doze_unit}', pseudo_vol: {pseudo_vol}, pseudo_vol_unit:'{pseudo_vol_unit}'")
    print(f"vol: {vol}, vol_unit: '{vol_unit}'")
    
    print(f"comlex_doze_list: '{complex_doze_list}', comlex_doze_str: '{complex_doze_str}'")
    print(f"dosage_standard_value_str: '{dosage_standard_value_str}', dosage_parsing_value_str: '{dosage_parsing_value_str}'")
    print(f"dosage_standard_value_str_refrmt: '{dosage_standard_value_str_refrmt}'")
    print(f"dosage_parsing_value: {dosage_parsing_value}, dosage_parsing_unit: {dosage_parsing_unit}")
    print(f"dosage_correct_value: {dosage_correct_value}, dosage_correct_unit:'{dosage_correct_unit}'")
    print(f"tn_lat: '{tn_lat}', tn_lat_ext: '{tn_lat_ext}', 'tn_ru: '{tn_ru}', tn_ru_clean: '{tn_ru_clean}'")
    print(f"tn_ru_orig: '{tn_ru_orig}', tn_ru_ext: '{tn_ru_ext}',  tn_ru_ext_clean: '{tn_ru_ext_clean}'")
    print(f"tn_by_tn: '{tn_by_tn}', tn_selected: '{tn_selected}', tn_true: '{tn_true}', mnn_by_tn: '{mnn_by_tn}', mnn_true: '{mnn_true}'")
    
    print(f"pharm_form_type: '{pharm_form_type}', pharm_form: '{pharm_form}'")
    print(f"form_standard: '{form_standard}', is_znvlp: '{is_znvlp}', ath_code: '{ath_code}', is_narcotic: '{is_narcotic}")
    
    print(f"pack_1_form_unify: '{pack_1_form_unify}', pack_1_form: '{pack_1_form}', pack_1_num: {pack_1_num}, "  
    f"pack_2_form_unify: '{pack_2_form_unify}', pack_2_form: '{pack_2_form}', pack_2_num: {pack_2_num}, n_packs_str: '{n_packs_str}'")
    # print(f"c_doze: {c_doze}")
    print(f"lp_pack_1_num: {lp_pack_1_num}, lp_pack_1_name: '{lp_pack_1_name}', lp_pack_2_num: {lp_pack_2_num}, lp_pack_2_name: '{lp_pack_2_name}'", 
          f"lp_unit_okei_name: '{lp_unit_okei_name}', lp_unit_name: '{lp_unit_name}', lp_consumer_total: {lp_consumer_total}, lp_consumer_total_calc: {lp_consumer_total_calc}")
    print(f"is_dosed: {is_dosed}, mass_volume_num: {mass_volume_num}, mass_volume_name: '{mass_volume_name}'")
    print(f"vol_klp: {vol_klp}, vol_unit_klp: '{vol_unit_klp}'")
    print(f"vol_calc: {vol_calc}, vol_unit_calc: '{vol_unit_calc}'")
    print(f"c_doze: {c_doze}, c_vol: {c_vol}, c_vol_unit: {c_vol_unit}, c_pack: {c_pack}, c_mnn: {c_mnn}, c_form: {c_form}")
    # print(f"mnn_true: '{mnn_true}', mnn_local_dict: '{mnn_local_dict}'") #, mnn_tn_ru_orig: '{mnn_tn_ru_orig}', mnn_tn_ru_ext: '{mnn_tn_ru_ext}', mnn_tn_ru: '{mnn_tn_ru}'")
    
    print(f"ls_doze: {ls_doze}, ls_doze_unit: '{ls_doze_unit}'")
    print(f"ls_vol: {ls_vol}, ls_vol_unit: '{ls_vol_unit}'")
    print(f"ls_doze_vol: {ls_doze_vol}, ls_doze_vol_unit: '{ls_doze_vol_unit}'")
    print()


def parse_mis_position_07(mis_position, select_by_tn=False, parse_dozes=True, debug=False, debug_print=False):
       
    # mnn_mis, tn_ru, tn_lat = def_mnn_mis(mis_position)
    # doze_unit, doze_unit_groups, vol_unparsed = def_dosages_vol_unparsed(mis_position, mnn_mis )
    # if debug: print(f"doze_unit: '{doze_unit}', doze_unit_groups: '{doze_unit_groups}', vol_unparsed: '{vol_unparsed}'")
    # dosage, measurement_unit, pseudo_vol, vol  = def_doze_measurement_unit(doze_unit, doze_unit_groups, vol_unparsed)
    #dosage_per_farm_form_unit = calc_dosage_per_farm_form_unit(dosage, measurement_unit, pseudo_vol, vol)
    #group_unify = dict_MISposition_group.get(mis_position)
    
    mis_position_w = mis_position
    # update 01/10/2022
    mnn_mis, tn_ru, tn_lat = def_mnn_mis(mis_position)
    if mnn_mis is not None: 
        mnn_unparsed = re.sub(mnn_mis, "", mis_position)
    
    # update 01/10/2022 ###########################
    tn_ru, tn_lat, tn_ext, pharm_form_type, pharm_form = extract_TN_ext(mis_position, debug=False)  
    #if mnn_unparsed is not None:
    #    tn_ru, tn_lat, tn_ext, pharm_form_type, pharm_form = extract_TN_ext(mnn_unparsed, debug=False)  
    #else: tn_ru, tn_lat, tn_ext, pharm_form_type, pharm_form = extract_TN_ext(mis_position, debug=False)  
    if debug: print(f"parse_mis_position: pharm_form_type: '{pharm_form_type}', '{pharm_form}'")
    
    if tn_ru is not None:
        tn_ru_clean, mnn_from_tn_ru, pharm_form_from_tn_ru, pharm_form_type_from_tn_ru = correct_tn_ru_ext(tn_ru)
    else: tn_ru_clean, mnn_from_tn_ru, pharm_form_from_tn_ru, pharm_form_type_from_tn_ru = None, None, '#Н/Д', '#Н/Д'
    
    #pharm_form_type = pharm_form_type
    tn_ru_ext, tn_lat_ext = update__tn_ru_ext__tn_lat_ext(tn_ext, debug=False)

    if tn_ru_ext is  None: 
        tn_ru_ext = get_tn_ru_ext_from_dict(tn_lat_ext, tn_lat)
    
    if tn_ru_ext is not None:
        tn_ru_ext_clean, mnn_from_tn_ru_ext, pharm_form_from_tn_ru_ext, pharm_form_type_from_tn_ru_ext = \
        correct_tn_ru_ext(tn_ru_ext)
    else: tn_ru_ext_clean, mnn_from_tn_ru_ext, pharm_form_from_tn_ru_ext, pharm_form_type_from_tn_ru_ext = None, None, '#Н/Д', '#Н/Д'

    if pharm_form_type is None or pharm_form_type=='#Н/Д':
        pharm_form = pharm_form_from_tn_ru or pharm_form_from_tn_ru_ext
        pharm_form_type = pharm_form_type_from_tn_ru or pharm_form_type_from_tn_ru_ext
    
    doze_group, doze_proc, doze, doze_unit, doze_str, complex_doze_list, complex_doze_str, pseudo_vol, pseudo_vol_unit, vol, vol_unit, vol_str = \
        None,None,None,None,None,None,None,None,None, None, None, None
    dosage_parsing_value,	dosage_parsing_unit, dosage_parsing_value_str = None, None, None        
    if parse_dozes:
        # !!!  pharm_form_type vs pharm_form_unify
        doze_group, doze_proc, doze, doze_unit, doze_str, pseudo_vol, pseudo_vol_unit, complex_doze_list, complex_doze_str, vol, vol_unit, vol_str = \
                 extract_doze_vol_02(mis_position, tn_ru_ext, tn_lat_ext, pharm_form_type, pharm_form, debug=debug)
                 #### НЕ ЗАБУДЬ # !!!  pharm_form_type - правильно vs pharm_form_unify - неправильно
                #  extract_doze_vol_02(mis_position, tn_ru_ext, tn_lat_ext, pharm_form_unify, pharm_form, debug=debug)
        
        
        # dosage_parsing_value,	dosage_parsing_unit = \
        #            calc_parsing_doze(doze_proc, doze, doze_unit, pseudo_vol, pseudo_vol_unit, vol_unit, debug=debug)
        if complex_doze_list is None: # не сложная - простая - дозировка
            # doze_parts_list = doze_pseudo_to_doze_parts_list(doze_str, doze, doze_unit, pseudo_vol, pseudo_vol_unit, debug = debug)
            dosage_parsing_value, dosage_parsing_unit = \
                calc_parsing_doze_02(doze_proc, doze, doze_unit, pseudo_vol, pseudo_vol_unit, vol_unit, debug=debug)
                # calc_parsing_doze(doze_proc, doze, doze_unit, pseudo_vol, pseudo_vol_unit, vol_unit, debug=debug)
            
            # if dosage_parsing_value is not None:
                # dosage_parsing_value = str(dosage_parsing_value)
            # doze_parts_list = doze_pseudo_to_doze_parts_list(doze_str, dosage_parsing_value, doze_unit, pseudo_vol, pseudo_vol_unit, debug = debug)
            # if doze is None and dosage_parsing_unit is not None: 
            if dosage_parsing_unit is not None: 
                # может быть просто число без ЕИ дозировки
                pos_doze_unit = dosage_parsing_unit.rfind('/')
                if pos_doze_unit >- 1:
                    doze_unit_01 = dosage_parsing_unit[:pos_doze_unit]
                    pseudo_vol_unit_01 = dosage_parsing_unit[pos_doze_unit+1:]
                else: 
                    doze_unit_01 = dosage_parsing_unit
                    pseudo_vol_unit_01 = None
                pseudo_vol_01 = None
            else:
                doze_unit_01 = doze_unit
                pseudo_vol_unit_01 = pseudo_vol_unit
                pseudo_vol_01 = pseudo_vol

            # doze_parts_list = doze_pseudo_to_doze_parts_list_02(doze_str, dosage_parsing_value, doze_unit_01, pseudo_vol, pseudo_vol_unit, debug = debug)
            doze_parts_list = doze_pseudo_to_doze_parts_list_02(doze_str, dosage_parsing_value, doze_unit_01, pseudo_vol_01, pseudo_vol_unit_01, debug = debug)
            # dosage_parsing_value_str = make_doze_str_frmt_02(doze_parts_list, debug = debug )
            dosage_parsing_value_str, _, _ = make_doze_str_frmt_03(doze_parts_list, debug = debug )
        else:
            # dosage_parsing_value, dosage_parsing_unit = doze, doze_unit
            # dosage_parsing_value, dosage_parsing_unit = \
            #     calc_parsing_doze_02(doze_proc, doze, doze_unit, pseudo_vol, pseudo_vol_unit, vol_unit, debug=debug)
            # if pseudo_vol_unit is not None and dosage_parsing_unit is not None: 
            #     dosage_parsing_unit += pseudo_vol_unit
            # dosage_parsing_value_str = make_doze_str_frmt_02(complex_doze_list, debug = debug )
            dosage_parsing_value_str, dosage_parsing_value, dosage_parsing_unit = make_doze_str_frmt_03(complex_doze_list, debug = debug )

        # dosage_parsing_value_str = form_dosage_parsing_value_str(dosage_parsing_value, dosage_parsing_unit, debug = debug)

        doze = to_float(doze)
        vol = to_float(vol)
        pseudo_vol = to_float(pseudo_vol)

        # doze_group, doze_proc, doze, doze_unit, doze_str, pseudo_vol, pseudo_vol_unit, vol, vol_unit, vol_str =\
        #  extract_doze_vol_02(mis_position, tn_ru_ext, tn_lat_ext, pharm_form_type, pharm_form, debug=debug)
         # Berotec N 100mkg/dosa 200 доз N1 аэрозоль
        # if debug: print("dozes:", doze_group, doze, doze_unit, doze_str, pseudo_vol, pseudo_vol_unit, vol, vol_unit, vol_str)
    # else: 
    #   doze_group, doze_proc, doze, doze_unit, doze_str, pseudo_vol, pseudo_vol_unit, vol, vol_unit, vol_str = \
    #     None,None,None,None,None,None,None,None,None, None
    pack_1_form_unify, pack_1_form,  pack_1_num, pack_2_form_unify, pack_2_form, pack_2_num, n_packs_str =\
        extract_packs(mis_position, debug=False)
    pack_1_num = to_float(pack_1_num)
    pack_2_num = to_float(pack_2_num)
    consumer_total_parsing = calc_consumer_total(pack_1_num, pack_2_num, debug = debug)

    tn_ru_orig, mnn_local_dict = def_tn_ru_orig(tn_lat_ext, tn_lat, debug=False)
    if debug: print(f"parse_mis_position: inner: tn_lat: '{tn_lat}', tn_lat_ext: '{tn_lat_ext}', tn_ru_orig: '{tn_ru_orig}, tn_ru_ext: '{tn_ru_ext}', 'tn_ru: '{tn_ru}'")
    
    tn_by_tn, mnn_by_tn = None, None
    if select_by_tn:
        # for i_tn, tn in enumerate([tn_ru_orig, tn_ru_ext_clean, tn_ru_clean]):
        #     # tn_by_tn, mnn_by_tn = select_klp_mnn_tn_by_tn(tn, debug=debug)
        #     mnn_by_tn, tn_by_tn = select_klp_mnn_tn_by_tn(tn, debug=debug)
        #     if tn_by_tn is not None: break
        mnn_by_tn, tn_by_tn = [], []
        for i_tn, tn in enumerate([tn_ru_orig, tn_ru_ext_clean, tn_ru_clean]):
            # tn_by_tn, mnn_by_tn = select_klp_mnn_tn_by_tn(tn, debug=debug)
            # print(f"parse_mis_position_07_update: tn: {i_tn}, {tn}")
            mnn_by_tn_pre, tn_by_tn_pre = select_klp_mnn_tn_by_tn(tn, debug=debug)
            if tn_by_tn_pre is not None:  #break
                if (type(tn_by_tn_pre)==str) or (type(tn_by_tn_pre)==np.str_):
                    tn_by_tn.append(tn_by_tn_pre)
                elif (type(tn_by_tn_pre)==list):
                    tn_by_tn.extend(tn_by_tn_pre)
                    
                elif (type(tn_by_tn_pre)==np.ndarray):
                    tn_by_tn.extend(list(tn_by_tn_pre))
            if mnn_by_tn_pre is not None:
                # mnn_by_tn.append(mnn_by_tn)
                if (type(mnn_by_tn_pre)==str) or (type(mnn_by_tn_pre)==np.str_):
                    mnn_by_tn.append(mnn_by_tn_pre)
                elif (type(mnn_by_tn_pre)==list):
                    mnn_by_tn.extend(mnn_by_tn_pre)
                elif (type(mnn_by_tn_pre)==np.ndarray):
                    mnn_by_tn.extend(list(mnn_by_tn_pre))
        
        if tn_by_tn is not None and not((type(tn_by_tn)==str) or (type(tn_by_tn)==np.str_)):
            if type(tn_by_tn)==np.ndarray: 
                tn_by_tn = list(tn_by_tn) # pass # 
            try:
                tn_by_tn = list(set(tn_by_tn))
                # tn_by_tn = np_unique_nan(tn_by_tn)
            except Exception as err:
                print("parse_mis_position_07:", err)
                print("--> tn_by_tn:", type(tn_by_tn), tn_by_tn)

            if len(tn_by_tn) == 0: tn_by_tn = None
            elif len(tn_by_tn) == 1: tn_by_tn = tn_by_tn[0]
        if mnn_by_tn is not None and not((type(mnn_by_tn)==str) or (type(mnn_by_tn)==np.str_)):
            if type(mnn_by_tn)==np.ndarray: mnn_by_tn = list(mnn_by_tn)
            try: 
                mnn_by_tn = list(set(mnn_by_tn))
            except Exception as err:
                print("parse_mis_position_07:", err)
                print("--> mnn_by_tn:", type(mnn_by_tn), mnn_by_tn)
            if len(mnn_by_tn) == 0: mnn_by_tn = None
            elif len(mnn_by_tn) == 1: mnn_by_tn = mnn_by_tn[0]     

    num_records, tn_true, mnn_true, mnn_lst, code_smnn_lst = 0, [], [], None, []
    last_num_records, last_mnn_lst, last_code_smnn_lst = 0, None, None
    if not(pharm_form_type is None or pharm_form_type=='#Н/Д'):
        
        
        #for i_tn, tn in enumerate([tn_ru_orig, tn_ru_ext, tn_ru]):
        for i_tn, tn in enumerate([tn_ru_orig, tn_ru_ext_clean, tn_ru_clean]):
            if debug: print("parse_mis_position: tn --->", i_tn, tn)
            if tn is not None:
                mnn_lst, code_smnn_lst_00, num_records = \
                select_klp_mnn_by_tn__pharm_form_type(tn.capitalize(), pharm_form_type, strict_select = False, debug=debug )
                if debug: print("parse_mis_position: tn, mnn_lst, code_smnn_lst_00, num_records --->", 
                    i_tn, tn, mnn_lst, code_smnn_lst_00, num_records)
                
                if num_records > 0: 
                    tn_true.append(tn)
                    tn_true = list(set(tn_true))
                    if mnn_lst is not None: 
                        if (type(mnn_lst)==list):
                            mnn_true.extend (mnn_lst) #list(set())
                            # if debug: print("parse_mis_position: type(mnn_lst), mnn_true")
                        # mnn_true = list(set(mnn_true))
                        # print(i_tn, 'mnn_true ->', mnn_true)
                        elif (type(mnn_lst)==np.ndarray):
                            mnn_true.extend (list(mnn_lst))
                            # if debug: print("parse_mis_position: type(mnn_lst), mnn_true")
                        else:
                            mnn_true.append (mnn_lst)
                            # if debug: print("parse_mis_position: type(mnn_lst), mnn_true")
                    if code_smnn_lst_00 is not None: 
                        if (type(code_smnn_lst_00)==list):
                            code_smnn_lst.extend (code_smnn_lst_00)
                        elif (type(code_smnn_lst_00)==np.ndarray):
                            code_smnn_lst.extend (list(code_smnn_lst_00))
                            # print("type(code_smnn_lst_00), code_smnn_lst", type(code_smnn_lst_00), code_smnn_lst)
                        else: # str or np.str_
                            code_smnn_lst.append(code_smnn_lst_00)
                            # print("type(code_smnn_lst_00), code_smnn_lst", type(code_smnn_lst_00), code_smnn_lst)
                        code_smnn_lst = list(set(code_smnn_lst))

        if len(tn_true)==0: tn_true = None
        elif len(tn_true)==1: tn_true = tn_true[0]
        if len(mnn_true)==0: mnn_true = None
        elif len(mnn_true)==1: mnn_true = mnn_true[0]
        else:
            mnn_true = list(set(mnn_true))
            if len(mnn_true)==1: mnn_true = mnn_true[0]
        if len(code_smnn_lst)==0: code_smnn_lst = None
        # elif len(code_smnn_lst)==1: code_smnn_lst = code_smnn_lst[0]
        # df_sel_63000_be[df_sel_63000_be['mnn_true'].notnull() & (df_sel_63000_be['mnn_true'].str.len()==0)]=None
        # df_sel_63000_be[df_sel_63000_be['tn_true'].notnull() & (df_sel_63000_be['tn_true'].str.len()==0)]=None
    
    if tn_true is not None and not (type(tn_true)==str or type(tn_true)==np.str_)\
        and (type(tn_true)==list or type(tn_true)==np.ndarray) and len(tn_true)==0:
        tn_true = None
    if mnn_true is not None and not (type(mnn_true)==str or type(mnn_true)==np.str_)\
        and (type(mnn_true)==list or type(mnn_true)==np.ndarray) and len(mnn_true)==0:
        mnn_true = None  
    if debug: print(f"parse_mis_position: last_mnn_lst: {last_mnn_lst}, last_code_smnn_lst: {last_code_smnn_lst}, last_num_records: {last_num_records}")        
    
    tn_selected = tn_true
    tn_true = choice_tn(tn_selected)
    
    ath_name, ath_code, is_znvlp, is_narcotic, form_standard  = None, None, None, None, None
    # dosage, 
    dosage_standard_value, dosage_standard_unit, dosage_standard_value_str = None, None, None
    dosage_standard_value_str_refrmt = None
    # dosage_parsing_value,	dosage_parsing_unit, dosage_parsing_value_str = None, None, None
    lp_pack_1_num, lp_pack_1_name, lp_pack_2_num, lp_pack_2_name, lp_unit_okei_name, lp_unit_name, lp_consumer_total, lp_consumer_total_calc,\
                        is_dosed, mass_volume_num, mass_volume_name =\
        None, None, None, None, None, None, None, None, None, None, None
    c_doze = None
    c_vol, c_vol_unit, name_ei_lp = None, None, None
    c_pack, c_mnn, c_form = None, None, None
    vol_calc, vol_unit_calc = None, None
    vol_klp, vol_unit_klp = None, None
    ls_doze, ls_doze_unit, ls_vol, ls_vol_unit, ls_doze_vol, ls_doze_vol_unit = None, None, None, None, None, None
    #if mnn_true is not None:
    #if num_records > 0:
    if debug: print(f"parse_mis_position: code_smnn_lst: {code_smnn_lst}")
    if code_smnn_lst is not None and len(code_smnn_lst)>0:
    #if mnn_lst is not None and len(mnn_lst)>0:
        #print("mnn_true is not None:")
        cols_return_lst = ['ath_name','ath_code', 'is_znvlp', 'is_narcotic', 'form_standard', 'dosage_grls_value'] # 'dosage_standard_value'
        cols_check_duplicates = ['ath_name','ath_code', 'is_znvlp', 'is_narcotic', 'form_standard']
        # индиффмрентно cols_check_duplicates попадаются словари и псики по к-ым drop_duplocatse не работают
        try:
            cols_srch  = {
                #'code': { 'ptn': [r"^(?:" , r")$"], 's_srch': "|".join(['(?:'+ re.escape(c) +')' for c in code_smnn_lst]),
                #'flags': re.I, 'regex': True},
                #'code': { 'ptn': ['' , ''], 's_srch': "|".join(['(?:'+ re.escape(c) +')' for c in code_smnn_lst]),
                # 'code': { 'ptn': ['' , ''], 's_srch': "|".join(['(?:'+ c +')' for c in code_smnn_lst]),
                'code_smnn': { 'ptn': ['' , ''], 's_srch': "|".join(['(?:'+ c +')' for c in code_smnn_lst]),
                        'flags': re.I, 'regex': True}, #True
                #  'mnn_standard': { 'ptn': [r"^(?:" , r")$"], 's_srch': "|".join(['(?:'+ re.escape(c) +')' for c in mnn_lst]),
                                
                #'form_standard': { 'ptn': [r"^(?:" , r").*$"], 's_srch': form_standard, 'flags': re.I},
            }
            # if debug: print("parse_mis_position: cols_srch:");pprint(cols_srch)

            return_values, num_records = \
                select_cols_values_from_smnn( cols_srch, cols_return_lst, cols_check_duplicates, check_col_names=False, debug=debug)
            if debug: print(f"parse_mis_position: num_records: {num_records}, return_values: {return_values}")
            if num_records > 0:  
                ath_name, ath_code, is_znvlp, is_narcotic, form_standard, dosage_standard_value_str = return_values
                if type(is_znvlp) ==  list and True in is_znvlp: is_znvlp = True
            else: ath_name, ath_code, is_znvlp, is_narcotic, form_standard, dosage_standard_value_str  = None, None, None, None, None
                # if num_records > 1:  form_standard, is_znvlp = list(return_values[0,:]), list(return_values[1,:])
                # elif num_records == 1: form_standard, is_znvlp = return_values
                # form_standard, is_znvlp = pd.Series({"form_standard":form_standard, "is_znvlp": is_znvlp})
        except Exception as err:
            print("parse_mis_position: Error create cols_srch", err, code_smnn_lst)
            # Error create cols_srch name 'select_cols_values_from_smnn' is not defined
            
        if dosage_standard_value_str is not None:
            dosage_standard_value, dosage_standard_unit = extract_dosage_standard(dosage_standard_value_str, debug=debug)
            # dosage_parsing_value,	dosage_parsing_unit = \
            #       calc_parsing_doze(doze_proc, doze, doze_unit, pseudo_vol, pseudo_vol_unit, vol_unit, debug=debug)

            # c_doze, dosage_parsing_value_str = compare_standard_parsing_doze(dosage_standard_value_str, dosage_parsing_value, dosage_parsing_unit, debug=debug)
            c_doze, i_doze = compare_standard_parsing_doze_02(dosage_standard_value_str, dosage_parsing_value_str, debug=debug)
            
            if not c_doze: # пробуем привести к правильной базе еи
                dosage_standard_value_str_refrmt = reformat_dosage_standard_value_str(dosage_standard_value_str, debug=debug)
                c_doze_unit, i_doze_02 = compare_standard_parsing_doze_02(dosage_standard_value_str_refrmt, dosage_parsing_value_str, debug=debug)
            
            if c_doze:
                # lp_pack_1_num, lp_pack_2_num, lp_unit_okei, lp_unit, lp_consumer_total, lp_consumer_total_calc = \
                #     select_klp_packs_norm(tn_true,  form_standard, dosage_parsing_value_str, debug=debug)
                if i_doze is None: 
                    # такого здесь быть не может: если c_doze is None то и i_doze is None
                    dosage_str = ''
                elif i_doze == -1: # dosage_standard_value_str - строка не список строк
                    dosage_str = dosage_standard_value_str
                elif i_doze > -1: # индекс в спсике dosage_standard_value_str
                    dosage_str = dosage_standard_value_str[i_doze]
                else: 
                    dosage_str = '' # страхуемся закрываем ветки
                lp_pack_1_num, lp_pack_1_name, lp_pack_2_num, lp_pack_2_name, lp_unit_okei_name, lp_unit_name, lp_consumer_total, lp_consumer_total_calc,\
                        is_dosed, mass_volume_num, mass_volume_name = \
                    select_klp_packs_norm_02(tn_true,  form_standard, dosage_str, debug=debug)    
                # select_klp_packs_norm_02(tn_true,  form_standard, dosage_standard_value_str, debug=debug)
                lp_pack_1_num = to_float(lp_pack_1_num)
                lp_pack_2_num = to_float(lp_pack_2_num)
                lp_consumer_total = to_float(lp_consumer_total)
                mass_volume_num = to_float(mass_volume_num)

                
                
                
                
                # vol_calc, vol_unit_calc = calc_volume(doze_group, lp_unit_name, pack_1_num, 
                # form_standard, consumer_total, consumer_total_kis, dosage_standard_unit, mass_volume_name, 
                # mass_volume_num,
                # debug=debug)
                # vol_calc, vol_unit_calc = calc_volume_02(doze_group, lp_unit_name, lp_pack_1_num, pack_1_num, 
                vol_klp, vol_unit_klp = calc_volume_02(doze_group, lp_unit_name, lp_pack_1_num, pack_1_num, 
                    form_standard, lp_consumer_total, consumer_total_parsing, dosage_parsing_unit, mass_volume_name, 
                    mass_volume_num, debug=debug)
                # vol_calc, vol_unit_calc = calc_volume(doze_group, lp_unit_name, pack_1_num, 
                #     form_standard, lp_consumer_total, consumer_total_parsing, dosage_parsing_unit, mass_volume_name, 
                #     mass_volume_num, debug=debug)
                # vol_calc = to_float(vol_calc)
                vol_klp = to_float(vol_klp)
                
                # c_vol, name_ei_lp = compare_vol_norm_parsing(doze_group, lp_pack_1_num, lp_pack_2_num, lp_unit_okei_name, lp_unit_name, 
                #               lp_consumer_total, lp_consumer_total_calc, consumer_total_parsing, vol, debug=debug)
                vol_calc, vol_unit_calc, c_vol, c_vol_unit = control_vol(doze_group, vol, vol_unit, vol_klp, vol_unit_klp, debug=debug)
                
                # dosage_standard_unit
    if consumer_total_parsing is not None: c_pack = 1
    else: c_pack = None

    if mnn_true is None: c_mnn = 0
    elif (type(mnn_true) == str) or (type(mnn_true) == np.str_): c_mnn = 1 # строка
    elif ((type(mnn_true) == list) or (type(mnn_true) == np.ndarray)) and (len(mnn_true)>1) : c_mnn = 2 # список
    else: c_mnn = None
    
    if form_standard is None: c_form = 0
    elif (type(form_standard) == str) or (type(form_standard) == np.str_): c_form = 1 # строка
    elif ((type(form_standard) == list) or (type(form_standard) == np.ndarray)) and (len(form_standard)>1) : c_form = 2 # список
    else: c_form = None
    
    if dosage_parsing_value_str is not None:
        if '+' in dosage_parsing_value_str:
            dosage_parsing_value_w, dosage_parsing_unit_w = extract_complex_dosage(dosage_parsing_value_str, debug=debug)
        else:
            dosage_parsing_value_w, dosage_parsing_unit_w = extract_simple_dosage(dosage_parsing_value_str, debug=debug)
    else:
        dosage_parsing_value_w, dosage_parsing_unit_w = None, None
    ls_doze, ls_doze_unit, ls_vol, ls_vol_unit, ls_doze_vol, ls_doze_vol_unit = \
        calc_ls_totals(dosage_parsing_value_w, dosage_parsing_unit_w,vol_calc, vol_unit_calc, debug=False)
        # calc_ls_totals(dosage_parsing_value, dosage_parsing_unit,vol_calc, vol_unit_calc, debug=False)
    
    dosage_correct_value, dosage_correct_unit = None, None

    # else: ath_name, ath_code, is_znvlp, is_narcotic, form_standard  = None, None, None, None, None
    if debug_print: 
        print_debug(  mis_position, tn_ru, tn_lat, tn_ru_ext, tn_lat_ext, tn_ru_orig, tn_ru_ext_clean, 
        tn_selected, tn_true,
        tn_by_tn, mnn_by_tn,
        tn_ru_clean, 
        pharm_form_type, pharm_form, 
        mnn_from_tn_ru_ext,  mnn_local_dict, mnn_true, 
        ath_name, ath_code, is_znvlp, is_narcotic, form_standard,
        doze_group, doze_proc, doze, doze_unit, pseudo_vol, pseudo_vol_unit, complex_doze_list, complex_doze_str, vol, vol_unit,
        pack_1_form_unify, pack_1_form,  pack_1_num, pack_2_form_unify, pack_2_form, pack_2_num, n_packs_str, consumer_total_parsing,
        dosage_standard_value_str, dosage_standard_value, dosage_standard_unit, 
        dosage_standard_value_str_refrmt,
        dosage_parsing_value_str, dosage_parsing_value, dosage_parsing_unit,
        dosage_correct_value, dosage_correct_unit,
        c_doze,
        lp_pack_1_num, lp_pack_1_name, lp_pack_2_num, lp_pack_2_name, lp_unit_okei_name, lp_unit_name, lp_consumer_total, lp_consumer_total_calc,
        is_dosed, mass_volume_num, mass_volume_name,
        vol_klp, vol_unit_klp,
        vol_calc, vol_unit_calc,
        c_vol, c_vol_unit, name_ei_lp,
        c_pack, c_mnn, c_form,
        ls_doze, ls_doze_unit, ls_vol, ls_vol_unit, ls_doze_vol, ls_doze_vol_unit 
                   
                   )
    
    return  tn_ru, tn_lat, tn_ru_ext, tn_lat_ext, tn_ru_orig, tn_ru_ext_clean, tn_selected, tn_true,\
    tn_by_tn, mnn_by_tn,\
    tn_ru_clean, \
    pharm_form_type, pharm_form, \
    mnn_from_tn_ru_ext,  mnn_local_dict, mnn_true, \
    ath_name, ath_code, is_znvlp, is_narcotic, form_standard,\
    doze_group, doze_proc, doze, doze_unit, pseudo_vol, pseudo_vol_unit, complex_doze_list, complex_doze_str, vol, vol_unit,\
    pack_1_form_unify, pack_1_form,  pack_1_num, pack_2_form_unify, pack_2_form, pack_2_num, consumer_total_parsing,\
    dosage_standard_value_str, dosage_standard_value, dosage_standard_unit, \
    dosage_standard_value_str_refrmt, \
    dosage_parsing_value_str, dosage_parsing_value,	dosage_parsing_unit,\
    dosage_correct_value, dosage_correct_unit,\
    c_doze,\
    lp_pack_1_num, lp_pack_1_name, lp_pack_2_num, lp_pack_2_name, lp_unit_okei_name, lp_unit_name, lp_consumer_total, lp_consumer_total_calc,\
    is_dosed, mass_volume_num, mass_volume_name,\
    vol_klp, vol_unit_klp,\
    vol_calc, vol_unit_calc,\
    c_vol, c_vol_unit, name_ei_lp,\
    c_pack, c_mnn, c_form,\
    ls_doze, ls_doze_unit, ls_vol, ls_vol_unit, ls_doze_vol, ls_doze_vol_unit


def parse_mis_position_07_00_01(mis_position, select_by_tn=False, parse_dozes=True, debug=False, debug_print=False):
       
    # mnn_mis, tn_ru, tn_lat = def_mnn_mis(mis_position)
    # doze_unit, doze_unit_groups, vol_unparsed = def_dosages_vol_unparsed(mis_position, mnn_mis )
    # if debug: print(f"doze_unit: '{doze_unit}', doze_unit_groups: '{doze_unit_groups}', vol_unparsed: '{vol_unparsed}'")
    # dosage, measurement_unit, pseudo_vol, vol  = def_doze_measurement_unit(doze_unit, doze_unit_groups, vol_unparsed)
    #dosage_per_farm_form_unit = calc_dosage_per_farm_form_unit(dosage, measurement_unit, pseudo_vol, vol)
    #group_unify = dict_MISposition_group.get(mis_position)
    
    mis_position_w = mis_position
    # update 01/10/2022
    mnn_mis, tn_ru, tn_lat = def_mnn_mis(mis_position)
    if mnn_mis is not None: 
        mnn_unparsed = re.sub(mnn_mis, "", mis_position)
    
    # update 01/10/2022 ###########################
    tn_ru, tn_lat, tn_ext, pharm_form_type, pharm_form = extract_TN_ext(mis_position, debug=False)  
    #if mnn_unparsed is not None:
    #    tn_ru, tn_lat, tn_ext, pharm_form_type, pharm_form = extract_TN_ext(mnn_unparsed, debug=False)  
    #else: tn_ru, tn_lat, tn_ext, pharm_form_type, pharm_form = extract_TN_ext(mis_position, debug=False)  
    if debug: print(f"parse_mis_position: pharm_form_type: '{pharm_form_type}', '{pharm_form}'")
    
    if tn_ru is not None:
        tn_ru_clean, mnn_from_tn_ru, pharm_form_from_tn_ru, pharm_form_type_from_tn_ru = correct_tn_ru_ext(tn_ru)
    else: tn_ru_clean, mnn_from_tn_ru, pharm_form_from_tn_ru, pharm_form_type_from_tn_ru = None, None, '#Н/Д', '#Н/Д'
    
    #pharm_form_type = pharm_form_type
    tn_ru_ext, tn_lat_ext = update__tn_ru_ext__tn_lat_ext(tn_ext, debug=False)

    if tn_ru_ext is  None: 
        tn_ru_ext = get_tn_ru_ext_from_dict(tn_lat_ext, tn_lat)
    
    if tn_ru_ext is not None:
        tn_ru_ext_clean, mnn_from_tn_ru_ext, pharm_form_from_tn_ru_ext, pharm_form_type_from_tn_ru_ext = \
        correct_tn_ru_ext(tn_ru_ext)
    else: tn_ru_ext_clean, mnn_from_tn_ru_ext, pharm_form_from_tn_ru_ext, pharm_form_type_from_tn_ru_ext = None, None, '#Н/Д', '#Н/Д'

    if pharm_form_type is None or pharm_form_type=='#Н/Д':
        pharm_form = pharm_form_from_tn_ru or pharm_form_from_tn_ru_ext
        pharm_form_type = pharm_form_type_from_tn_ru or pharm_form_type_from_tn_ru_ext
    
    doze_group, doze_proc, doze, doze_unit, doze_str, complex_doze_list, complex_doze_str, pseudo_vol, pseudo_vol_unit, vol, vol_unit, vol_str = \
        None,None,None,None,None,None,None,None,None, None, None, None
    dosage_parsing_value,	dosage_parsing_unit, dosage_parsing_value_str = None, None, None        
    if parse_dozes:
        # !!!  pharm_form_type vs pharm_form_unify
        doze_group, doze_proc, doze, doze_unit, doze_str, pseudo_vol, pseudo_vol_unit, complex_doze_list, complex_doze_str, vol, vol_unit, vol_str = \
                 extract_doze_vol_02(mis_position, tn_ru_ext, tn_lat_ext, pharm_form_type, pharm_form, debug=debug)
                 #### НЕ ЗАБУДЬ # !!!  pharm_form_type - правильно vs pharm_form_unify - неправильно
                #  extract_doze_vol_02(mis_position, tn_ru_ext, tn_lat_ext, pharm_form_unify, pharm_form, debug=debug)
        
        
        # dosage_parsing_value,	dosage_parsing_unit = \
        #            calc_parsing_doze(doze_proc, doze, doze_unit, pseudo_vol, pseudo_vol_unit, vol_unit, debug=debug)
        if complex_doze_list is None: # не сложная - простая - дозировка
            # doze_parts_list = doze_pseudo_to_doze_parts_list(doze_str, doze, doze_unit, pseudo_vol, pseudo_vol_unit, debug = debug)
            dosage_parsing_value, dosage_parsing_unit = \
                calc_parsing_doze_02(doze_proc, doze, doze_unit, pseudo_vol, pseudo_vol_unit, vol_unit, debug=debug)
                # calc_parsing_doze(doze_proc, doze, doze_unit, pseudo_vol, pseudo_vol_unit, vol_unit, debug=debug)
            
            # if dosage_parsing_value is not None:
                # dosage_parsing_value = str(dosage_parsing_value)
            # doze_parts_list = doze_pseudo_to_doze_parts_list(doze_str, dosage_parsing_value, doze_unit, pseudo_vol, pseudo_vol_unit, debug = debug)
            # if doze is None and dosage_parsing_unit is not None: 
            if dosage_parsing_unit is not None: 
                # может быть просто число без ЕИ дозировки
                pos_doze_unit = dosage_parsing_unit.rfind('/')
                if pos_doze_unit >- 1:
                    doze_unit_01 = dosage_parsing_unit[:pos_doze_unit]
                    pseudo_vol_unit_01 = dosage_parsing_unit[pos_doze_unit+1:]
                else: 
                    doze_unit_01 = dosage_parsing_unit
                    pseudo_vol_unit_01 = None
                pseudo_vol_01 = None
            else:
                doze_unit_01 = doze_unit
                pseudo_vol_unit_01 = pseudo_vol_unit
                pseudo_vol_01 = pseudo_vol

            # doze_parts_list = doze_pseudo_to_doze_parts_list_02(doze_str, dosage_parsing_value, doze_unit_01, pseudo_vol, pseudo_vol_unit, debug = debug)
            doze_parts_list = doze_pseudo_to_doze_parts_list_02(doze_str, dosage_parsing_value, doze_unit_01, pseudo_vol_01, pseudo_vol_unit_01, debug = debug)
            dosage_parsing_value_str = make_doze_str_frmt_02(doze_parts_list, debug = debug )
        else:
            dosage_parsing_value, dosage_parsing_unit = doze, doze_unit
            dosage_parsing_value_str = make_doze_str_frmt_02(complex_doze_list, debug = debug )

        # dosage_parsing_value_str = form_dosage_parsing_value_str(dosage_parsing_value, dosage_parsing_unit, debug = debug)

        doze = to_float(doze)
        vol = to_float(vol)
        pseudo_vol = to_float(pseudo_vol)

        # doze_group, doze_proc, doze, doze_unit, doze_str, pseudo_vol, pseudo_vol_unit, vol, vol_unit, vol_str =\
        #  extract_doze_vol_02(mis_position, tn_ru_ext, tn_lat_ext, pharm_form_type, pharm_form, debug=debug)
         # Berotec N 100mkg/dosa 200 доз N1 аэрозоль
        # if debug: print("dozes:", doze_group, doze, doze_unit, doze_str, pseudo_vol, pseudo_vol_unit, vol, vol_unit, vol_str)
    # else: 
    #   doze_group, doze_proc, doze, doze_unit, doze_str, pseudo_vol, pseudo_vol_unit, vol, vol_unit, vol_str = \
    #     None,None,None,None,None,None,None,None,None, None
    pack_1_form_unify, pack_1_form,  pack_1_num, pack_2_form_unify, pack_2_form, pack_2_num, n_packs_str =\
        extract_packs(mis_position, debug=False)
    pack_1_num = to_float(pack_1_num)
    pack_2_num = to_float(pack_2_num)
    consumer_total_parsing = calc_consumer_total(pack_1_num, pack_2_num, debug = debug)

    tn_ru_orig, mnn_local_dict = def_tn_ru_orig(tn_lat_ext, tn_lat, debug=False)
    if debug: print(f"parse_mis_position: inner: tn_lat: '{tn_lat}', tn_lat_ext: '{tn_lat_ext}', tn_ru_orig: '{tn_ru_orig}, tn_ru_ext: '{tn_ru_ext}', 'tn_ru: '{tn_ru}'")
    
    tn_by_tn, mnn_by_tn = None, None
    if select_by_tn:
        for i_tn, tn in enumerate([tn_ru_orig, tn_ru_ext_clean, tn_ru_clean]):
            # tn_by_tn, mnn_by_tn = select_klp_mnn_tn_by_tn(tn, debug=debug)
            mnn_by_tn, tn_by_tn = select_klp_mnn_tn_by_tn(tn, debug=debug)
            if tn_by_tn is not None: break

    num_records, tn_true, mnn_true, mnn_lst, code_smnn_lst = 0, [], [], None, []
    last_num_records, last_mnn_lst, last_code_smnn_lst = 0, None, None
    if not(pharm_form_type is None or pharm_form_type=='#Н/Д'):
        
        #for i_tn, tn in enumerate([tn_ru_orig, tn_ru_ext, tn_ru]):
        for i_tn, tn in enumerate([tn_ru_orig, tn_ru_ext_clean, tn_ru_clean]):
            if debug: print("parse_mis_position: tn --->", i_tn, tn)
            if tn is not None:
                mnn_lst, code_smnn_lst_00, num_records = \
                select_klp_mnn_by_tn__pharm_form_type(tn.capitalize(), pharm_form_type, strict_select = False, debug=debug )
                if debug: print("parse_mis_position: tn, mnn_lst, code_smnn_lst_00, num_records --->", 
                    i_tn, tn, mnn_lst, code_smnn_lst_00, num_records)
                
                if num_records > 0: 
                    tn_true.append(tn)
                    tn_true = list(set(tn_true))
                    if mnn_lst is not None: 
                        if (type(mnn_lst)==list):
                            mnn_true.extend (mnn_lst) #list(set())
                            # if debug: print("parse_mis_position: type(mnn_lst), mnn_true")
                        # mnn_true = list(set(mnn_true))
                        # print(i_tn, 'mnn_true ->', mnn_true)
                        elif (type(mnn_lst)==np.ndarray):
                            mnn_true.extend (list(mnn_lst))
                            # if debug: print("parse_mis_position: type(mnn_lst), mnn_true")
                        else:
                            mnn_true.append (mnn_lst)
                            # if debug: print("parse_mis_position: type(mnn_lst), mnn_true")
                    if code_smnn_lst_00 is not None: 
                        if (type(code_smnn_lst_00)==list):
                            code_smnn_lst.extend (code_smnn_lst_00)
                        elif (type(code_smnn_lst_00)==np.ndarray):
                            code_smnn_lst.extend (list(code_smnn_lst_00))
                            # print("type(code_smnn_lst_00), code_smnn_lst", type(code_smnn_lst_00), code_smnn_lst)
                        else: # str or np.str_
                            code_smnn_lst.append(code_smnn_lst_00)
                            # print("type(code_smnn_lst_00), code_smnn_lst", type(code_smnn_lst_00), code_smnn_lst)
                        code_smnn_lst = list(set(code_smnn_lst))

        if len(tn_true)==0: tn_true = None
        elif len(tn_true)==1: tn_true = tn_true[0]
        if len(mnn_true)==0: mnn_true = None
        elif len(mnn_true)==1: mnn_true = mnn_true[0]
        else:
            mnn_true = list(set(mnn_true))
            if len(mnn_true)==1: mnn_true = mnn_true[0]
        if len(code_smnn_lst)==0: code_smnn_lst = None
        # elif len(code_smnn_lst)==1: code_smnn_lst = code_smnn_lst[0]
        # df_sel_63000_be[df_sel_63000_be['mnn_true'].notnull() & (df_sel_63000_be['mnn_true'].str.len()==0)]=None
        # df_sel_63000_be[df_sel_63000_be['tn_true'].notnull() & (df_sel_63000_be['tn_true'].str.len()==0)]=None
    
    if tn_true is not None and not (type(tn_true)==str or type(tn_true)==np.str_)\
        and (type(tn_true)==list or type(tn_true)==np.ndarray) and len(tn_true)==0:
        tn_true = None
    if mnn_true is not None and not (type(mnn_true)==str or type(mnn_true)==np.str_)\
        and (type(mnn_true)==list or type(mnn_true)==np.ndarray) and len(mnn_true)==0:
        mnn_true = None  
    # if debug: print(f"parse_mis_position: last_mnn_lst: {last_mnn_lst}, last_code_smnn_lst: {last_code_smnn_lst}, last_num_records: {last_num_records}")        
    
    tn_selected = tn_true
    tn_true = choice_tn(tn_selected)
    
    ath_name, ath_code, is_znvlp, is_narcotic, form_standard  = None, None, None, None, None
    # dosage, 
    dosage_standard_value, dosage_standard_unit, dosage_standard_value_str = None, None, None
    dosage_standard_value_str_refrmt = None
    # dosage_parsing_value,	dosage_parsing_unit, dosage_parsing_value_str = None, None, None
    lp_pack_1_num, lp_pack_1_name, lp_pack_2_num, lp_pack_2_name, lp_unit_okei_name, lp_unit_name, lp_consumer_total, lp_consumer_total_calc,\
                        is_dosed, mass_volume_num, mass_volume_name =\
        None, None, None, None, None, None, None, None, None, None, None
    c_doze = None
    c_vol, name_ei_lp = None, None
    c_pack, c_mnn, c_form = None, None, None
    vol_calc, vol_unit_calc = None, None
    #if mnn_true is not None:
    #if num_records > 0:
    if debug: print(f"parse_mis_position: code_smnn_lst: {code_smnn_lst}")
    if code_smnn_lst is not None and len(code_smnn_lst)>0:
    #if mnn_lst is not None and len(mnn_lst)>0:
        #print("mnn_true is not None:")
        cols_return_lst = ['ath_name','ath_code', 'is_znvlp', 'is_narcotic', 'form_standard', 'dosage_grls_value'] # 'dosage_standard_value'
        cols_check_duplicates = ['ath_name','ath_code', 'is_znvlp', 'is_narcotic', 'form_standard']
        # индиффмрентно cols_check_duplicates попадаются словари и псики по к-ым drop_duplocatse не работают
        try:
            cols_srch  = {
                #'code': { 'ptn': [r"^(?:" , r")$"], 's_srch': "|".join(['(?:'+ re.escape(c) +')' for c in code_smnn_lst]),
                #'flags': re.I, 'regex': True},
                #'code': { 'ptn': ['' , ''], 's_srch': "|".join(['(?:'+ re.escape(c) +')' for c in code_smnn_lst]),
                # 'code': { 'ptn': ['' , ''], 's_srch': "|".join(['(?:'+ c +')' for c in code_smnn_lst]),
                'code_smnn': { 'ptn': ['' , ''], 's_srch': "|".join(['(?:'+ c +')' for c in code_smnn_lst]),
                        'flags': re.I, 'regex': True}, #True
                #  'mnn_standard': { 'ptn': [r"^(?:" , r")$"], 's_srch': "|".join(['(?:'+ re.escape(c) +')' for c in mnn_lst]),
                                
                #'form_standard': { 'ptn': [r"^(?:" , r").*$"], 's_srch': form_standard, 'flags': re.I},
            }
            # if debug: print("parse_mis_position: cols_srch:");pprint(cols_srch)

            return_values, num_records = \
                select_cols_values_from_smnn( cols_srch, cols_return_lst, cols_check_duplicates, check_col_names=False, debug=debug)
            if debug: print(f"parse_mis_position: num_records: {num_records}, return_values: {return_values}")
            if num_records > 0:  
                ath_name, ath_code, is_znvlp, is_narcotic, form_standard, dosage_standard_value_str = return_values
                if type(is_znvlp) ==  list and True in is_znvlp: is_znvlp = True
            else: ath_name, ath_code, is_znvlp, is_narcotic, form_standard, dosage_standard_value_str  = None, None, None, None, None
                # if num_records > 1:  form_standard, is_znvlp = list(return_values[0,:]), list(return_values[1,:])
                # elif num_records == 1: form_standard, is_znvlp = return_values
                # form_standard, is_znvlp = pd.Series({"form_standard":form_standard, "is_znvlp": is_znvlp})
        except Exception as err:
            print("parse_mis_position: Error create cols_srch", err, code_smnn_lst)
            # Error create cols_srch name 'select_cols_values_from_smnn' is not defined
            
        if dosage_standard_value_str is not None:
            dosage_standard_value, dosage_standard_unit = extract_dosage_standard(dosage_standard_value_str, debug=debug)
            # dosage_parsing_value,	dosage_parsing_unit = \
            #       calc_parsing_doze(doze_proc, doze, doze_unit, pseudo_vol, pseudo_vol_unit, vol_unit, debug=debug)

            # c_doze, dosage_parsing_value_str = compare_standard_parsing_doze(dosage_standard_value_str, dosage_parsing_value, dosage_parsing_unit, debug=debug)
            c_doze, i_doze = compare_standard_parsing_doze_02(dosage_standard_value_str, dosage_parsing_value_str, debug=debug)
            
            if not c_doze: # пробуем привести к правильной базе еи
                dosage_standard_value_str_refrmt = reformat_dosage_standard_value_str(dosage_standard_value_str, debug=debug)
                c_doze, i_doze = compare_standard_parsing_doze_02(dosage_standard_value_str_refrmt, dosage_parsing_value_str, debug=debug)
            
            if c_doze:
                # lp_pack_1_num, lp_pack_2_num, lp_unit_okei, lp_unit, lp_consumer_total, lp_consumer_total_calc = \
                #     select_klp_packs_norm(tn_true,  form_standard, dosage_parsing_value_str, debug=debug)
                if i_doze is None: 
                    # такого здесь быть не может: если c_doze is None то и i_doze is None
                    dosage_str = ''
                elif i_doze == -1: # dosage_standard_value_str - строка не список строк
                    dosage_str = dosage_standard_value_str
                elif i_doze > -1: # индекс в спсике dosage_standard_value_str
                    dosage_str = dosage_standard_value_str[i_doze]
                else: 
                    dosage_str = '' # страхуемся закрываем ветки
                lp_pack_1_num, lp_pack_1_name, lp_pack_2_num, lp_pack_2_name, lp_unit_okei_name, lp_unit_name, lp_consumer_total, lp_consumer_total_calc,\
                        is_dosed, mass_volume_num, mass_volume_name = \
                    select_klp_packs_norm_02(tn_true,  form_standard, dosage_str, debug=debug)    
                # select_klp_packs_norm_02(tn_true,  form_standard, dosage_standard_value_str, debug=debug)
                lp_pack_1_num = to_float(lp_pack_1_num)
                lp_pack_2_num = to_float(lp_pack_2_num)
                lp_consumer_total = to_float(lp_consumer_total)
                mass_volume_num = to_float(mass_volume_num)

                
                c_vol, name_ei_lp = compare_vol_norm_parsing(doze_group, lp_pack_1_num, lp_pack_2_num, lp_unit_okei_name, lp_unit_name, 
                              lp_consumer_total, lp_consumer_total_calc, consumer_total_parsing, vol, debug=debug)
                
                
                # vol_calc, vol_unit_calc = calc_volume(doze_group, lp_unit_name, pack_1_num, 
                # form_standard, consumer_total, consumer_total_kis, dosage_standard_unit, mass_volume_name, 
                # mass_volume_num,
                # debug=debug)
                vol_calc, vol_unit_calc = calc_volume(doze_group, lp_unit_name, pack_1_num, 
                    form_standard, lp_consumer_total, consumer_total_parsing, dosage_parsing_unit, mass_volume_name, 
                    mass_volume_num, debug=debug)
                vol_calc = to_float(vol_calc)
                # dosage_standard_unit
    if consumer_total_parsing is not None: c_pack = 1
    else: c_pack = None

    if mnn_true is None: c_mnn = 0
    elif (type(mnn_true) == str) or (type(mnn_true) == np.str_): c_mnn = 1 # строка
    elif ((type(mnn_true) == list) or (type(mnn_true) == np.ndarray)) and (len(mnn_true)>1) : c_mnn = 2 # список
    else: c_mnn = None
    
    if form_standard is None: c_form = 0
    elif (type(form_standard) == str) or (type(form_standard) == np.str_): c_form = 1 # строка
    elif ((type(form_standard) == list) or (type(form_standard) == np.ndarray)) and (len(form_standard)>1) : c_form = 2 # список
    else: c_form = None

    # else: ath_name, ath_code, is_znvlp, is_narcotic, form_standard  = None, None, None, None, None
    if debug_print: 
        print_debug(  mis_position, tn_ru, tn_lat, tn_ru_ext, tn_lat_ext, tn_ru_orig, tn_ru_ext_clean, 
        tn_selected, tn_true,
        tn_by_tn, mnn_by_tn,
        tn_ru_clean, 
        pharm_form_type, pharm_form, 
        mnn_from_tn_ru_ext,  mnn_local_dict, mnn_true, 
        ath_name, ath_code, is_znvlp, is_narcotic, form_standard,
        doze_group, doze_proc, doze, doze_unit, pseudo_vol, pseudo_vol_unit, complex_doze_list, complex_doze_str, vol, vol_unit,
        pack_1_form_unify, pack_1_form,  pack_1_num, pack_2_form_unify, pack_2_form, pack_2_num, n_packs_str, consumer_total_parsing,
        dosage_standard_value_str, dosage_standard_value, dosage_standard_unit, 
        dosage_standard_value_str_refrmt,
        dosage_parsing_value_str, dosage_parsing_value, dosage_parsing_unit,
        c_doze,
        lp_pack_1_num, lp_pack_1_name, lp_pack_2_num, lp_pack_2_name, lp_unit_okei_name, lp_unit_name, lp_consumer_total, lp_consumer_total_calc,
        is_dosed, mass_volume_num, mass_volume_name,
        vol_calc, vol_unit_calc,
        c_vol, name_ei_lp,
        c_pack, c_mnn, c_form
                   
                   )
    
    return  tn_ru, tn_lat, tn_ru_ext, tn_lat_ext, tn_ru_orig, tn_ru_ext_clean, tn_selected, tn_true,\
    tn_by_tn, mnn_by_tn,\
    tn_ru_clean, \
    pharm_form_type, pharm_form, \
    mnn_from_tn_ru_ext,  mnn_local_dict, mnn_true, \
    ath_name, ath_code, is_znvlp, is_narcotic, form_standard,\
    doze_group, doze_proc, doze, doze_unit, pseudo_vol, pseudo_vol_unit, complex_doze_list, complex_doze_str, vol, vol_unit,\
    pack_1_form_unify, pack_1_form,  pack_1_num, pack_2_form_unify, pack_2_form, pack_2_num, consumer_total_parsing,\
    dosage_standard_value_str, dosage_standard_value, dosage_standard_unit, \
    dosage_standard_value_str_refrmt, \
    dosage_parsing_value_str, dosage_parsing_value,	dosage_parsing_unit,\
    c_doze,\
    lp_pack_1_num, lp_pack_1_name, lp_pack_2_num, lp_pack_2_name, lp_unit_okei_name, lp_unit_name, lp_consumer_total, lp_consumer_total_calc,\
    is_dosed, mass_volume_num, mass_volume_name,\
    vol_calc, vol_unit_calc,\
    c_vol, name_ei_lp,\
    c_pack, c_mnn, c_form


def parse_mis_position_07_00 (mis_position, select_by_tn=False, parse_dozes=True, debug=False, debug_print=False):
       
    # mnn_mis, tn_ru, tn_lat = def_mnn_mis(mis_position)
    # doze_unit, doze_unit_groups, vol_unparsed = def_dosages_vol_unparsed(mis_position, mnn_mis )
    # if debug: print(f"doze_unit: '{doze_unit}', doze_unit_groups: '{doze_unit_groups}', vol_unparsed: '{vol_unparsed}'")
    # dosage, measurement_unit, pseudo_vol, vol  = def_doze_measurement_unit(doze_unit, doze_unit_groups, vol_unparsed)
    #dosage_per_farm_form_unit = calc_dosage_per_farm_form_unit(dosage, measurement_unit, pseudo_vol, vol)
    #group_unify = dict_MISposition_group.get(mis_position)
    
    mis_position_w = mis_position
    # update 01/10/2022
    mnn_mis, tn_ru, tn_lat = def_mnn_mis(mis_position)
    if mnn_mis is not None: 
        mnn_unparsed = re.sub(mnn_mis, "", mis_position)
    
    # update 01/10/2022 ###########################
    tn_ru, tn_lat, tn_ext, pharm_form_type, pharm_form = extract_TN_ext(mis_position, debug=False)  
    #if mnn_unparsed is not None:
    #    tn_ru, tn_lat, tn_ext, pharm_form_type, pharm_form = extract_TN_ext(mnn_unparsed, debug=False)  
    #else: tn_ru, tn_lat, tn_ext, pharm_form_type, pharm_form = extract_TN_ext(mis_position, debug=False)  
    if debug: print(f"parse_mis_position: pharm_form_type: '{pharm_form_type}', '{pharm_form}'")
    
    if tn_ru is not None:
        tn_ru_clean, mnn_from_tn_ru, pharm_form_from_tn_ru, pharm_form_type_from_tn_ru = correct_tn_ru_ext(tn_ru)
    else: tn_ru_clean, mnn_from_tn_ru, pharm_form_from_tn_ru, pharm_form_type_from_tn_ru = None, None, '#Н/Д', '#Н/Д'
    
    #pharm_form_type = pharm_form_type
    tn_ru_ext, tn_lat_ext = update__tn_ru_ext__tn_lat_ext(tn_ext, debug=False)

    if tn_ru_ext is  None: 
        tn_ru_ext = get_tn_ru_ext_from_dict(tn_lat_ext, tn_lat)
    
    if tn_ru_ext is not None:
        tn_ru_ext_clean, mnn_from_tn_ru_ext, pharm_form_from_tn_ru_ext, pharm_form_type_from_tn_ru_ext = \
        correct_tn_ru_ext(tn_ru_ext)
    else: tn_ru_ext_clean, mnn_from_tn_ru_ext, pharm_form_from_tn_ru_ext, pharm_form_type_from_tn_ru_ext = None, None, '#Н/Д', '#Н/Д'

    if pharm_form_type is None or pharm_form_type=='#Н/Д':
        pharm_form = pharm_form_from_tn_ru or pharm_form_from_tn_ru_ext
        pharm_form_type = pharm_form_type_from_tn_ru or pharm_form_type_from_tn_ru_ext
    
    doze_group, doze_proc, doze, doze_unit, doze_str, comlex_doze_list, comlex_doze_str, pseudo_vol, pseudo_vol_unit, vol, vol_unit, vol_str = \
        None,None,None,None,None,None,None,None,None, None, None, None
    dosage_parsing_value,	dosage_parsing_unit, dosage_parsing_value_str = None, None, None        
    if parse_dozes:
        # !!!  pharm_form_type vs pharm_form_unify
        doze_group, doze_proc, doze, doze_unit, doze_str, pseudo_vol, pseudo_vol_unit, comlex_doze_list, comlex_doze_str, vol, vol_unit, vol_str = \
                 extract_doze_vol_02(mis_position, tn_ru_ext, tn_lat_ext, pharm_form_type, pharm_form, debug=debug)
                 #### НЕ ЗАБУДЬ # !!!  pharm_form_type - правильно vs pharm_form_unify - неправильно
                #  extract_doze_vol_02(mis_position, tn_ru_ext, tn_lat_ext, pharm_form_unify, pharm_form, debug=debug)
        
        
        # dosage_parsing_value,	dosage_parsing_unit = \
        #            calc_parsing_doze(doze_proc, doze, doze_unit, pseudo_vol, pseudo_vol_unit, vol_unit, debug=debug)
        if comlex_doze_list is None: # не сложная - простая - дозировка
            # doze_parts_list = doze_pseudo_to_doze_parts_list(doze_str, doze, doze_unit, pseudo_vol, pseudo_vol_unit, debug = debug)
            dosage_parsing_value, dosage_parsing_unit = \
                   calc_parsing_doze(doze_proc, doze, doze_unit, pseudo_vol, pseudo_vol_unit, vol_unit, debug=debug)
            
            # if dosage_parsing_value is not None:
                # dosage_parsing_value = str(dosage_parsing_value)
            # doze_parts_list = doze_pseudo_to_doze_parts_list(doze_str, dosage_parsing_value, doze_unit, pseudo_vol, pseudo_vol_unit, debug = debug)
            # if doze is None and dosage_parsing_unit is not None: 
            if dosage_parsing_unit is not None: 
                # может быть просто число без ЕИ дозировки
                pos_doze_unit = dosage_parsing_unit.rfind('/')
                if pos_doze_unit >- 1:
                    doze_unit_01 = dosage_parsing_unit[:pos_doze_unit]
                    pseudo_vol_unit_01 = dosage_parsing_unit[pos_doze_unit+1:]
                else: 
                    doze_unit_01 = dosage_parsing_unit
                    pseudo_vol_unit_01 = None
                pseudo_vol_01 = None
            else:
                doze_unit_01 = doze_unit
                pseudo_vol_unit_01 = pseudo_vol_unit
                pseudo_vol_01 = pseudo_vol

            # doze_parts_list = doze_pseudo_to_doze_parts_list_02(doze_str, dosage_parsing_value, doze_unit_01, pseudo_vol, pseudo_vol_unit, debug = debug)
            doze_parts_list = doze_pseudo_to_doze_parts_list_02(doze_str, dosage_parsing_value, doze_unit_01, pseudo_vol_01, pseudo_vol_unit_01, debug = debug)
            dosage_parsing_value_str = make_doze_str_frmt_02(doze_parts_list, debug = debug )
        else:
            # dosage_parsing_value, dosage_parsing_unit = doze, doze_unit
            dosage_parsing_value, dosage_parsing_unit = \
                calc_parsing_doze_02(doze_proc, doze, doze_unit, pseudo_vol, pseudo_vol_unit, vol_unit, debug=debug)
            dosage_parsing_value_str = make_doze_str_frmt_02(comlex_doze_list, debug = debug )

        # dosage_parsing_value_str = form_dosage_parsing_value_str(dosage_parsing_value, dosage_parsing_unit, debug = debug)

        doze = to_float(doze)
        vol = to_float(vol)
        pseudo_vol = to_float(pseudo_vol)

        # doze_group, doze_proc, doze, doze_unit, doze_str, pseudo_vol, pseudo_vol_unit, vol, vol_unit, vol_str =\
        #  extract_doze_vol_02(mis_position, tn_ru_ext, tn_lat_ext, pharm_form_type, pharm_form, debug=debug)
         # Berotec N 100mkg/dosa 200 доз N1 аэрозоль
        # if debug: print("dozes:", doze_group, doze, doze_unit, doze_str, pseudo_vol, pseudo_vol_unit, vol, vol_unit, vol_str)
    # else: 
    #   doze_group, doze_proc, doze, doze_unit, doze_str, pseudo_vol, pseudo_vol_unit, vol, vol_unit, vol_str = \
    #     None,None,None,None,None,None,None,None,None, None
    pack_1_form_unify, pack_1_form,  pack_1_num, pack_2_form_unify, pack_2_form, pack_2_num, n_packs_str =\
        extract_packs(mis_position, debug=False)
    pack_1_num = to_float(pack_1_num)
    pack_2_num = to_float(pack_2_num)
    consumer_total_parsing = calc_consumer_total(pack_1_num, pack_2_num, debug = debug)

    tn_ru_orig, mnn_local_dict = def_tn_ru_orig(tn_lat_ext, tn_lat, debug=False)
    if debug: print(f"parse_mis_position: inner: tn_lat: '{tn_lat}', tn_lat_ext: '{tn_lat_ext}', tn_ru_orig: '{tn_ru_orig}, tn_ru_ext: '{tn_ru_ext}', 'tn_ru: '{tn_ru}'")
    
    tn_by_tn, mnn_by_tn = None, None
    if select_by_tn:
        for i_tn, tn in enumerate([tn_ru_orig, tn_ru_ext_clean, tn_ru_clean]):
            # tn_by_tn, mnn_by_tn = select_klp_mnn_tn_by_tn(tn, debug=debug)
            mnn_by_tn, tn_by_tn = select_klp_mnn_tn_by_tn(tn, debug=debug)
            if tn_by_tn is not None: break

    num_records, tn_true, mnn_true, mnn_lst, code_smnn_lst = 0, [], [], None, []
    last_num_records, last_mnn_lst, last_code_smnn_lst = 0, None, None
    if not(pharm_form_type is None or pharm_form_type=='#Н/Д'):
        
        #for i_tn, tn in enumerate([tn_ru_orig, tn_ru_ext, tn_ru]):
        for i_tn, tn in enumerate([tn_ru_orig, tn_ru_ext_clean, tn_ru_clean]):
            if debug: print("parse_mis_position: tn --->", i_tn, tn)
            if tn is not None:
                mnn_lst, code_smnn_lst_00, num_records = \
                select_klp_mnn_by_tn__pharm_form_type(tn.capitalize(), pharm_form_type, strict_select = False, debug=debug )
                if debug: print("parse_mis_position: tn, mnn_lst, code_smnn_lst_00, num_records --->", 
                    i_tn, tn, mnn_lst, code_smnn_lst_00, num_records)
                
                if num_records > 0: 
                    tn_true.append(tn)
                    tn_true = list(set(tn_true))
                    if mnn_lst is not None: 
                        if (type(mnn_lst)==list):
                            mnn_true.extend (mnn_lst) #list(set())
                            # if debug: print("parse_mis_position: type(mnn_lst), mnn_true")
                        # mnn_true = list(set(mnn_true))
                        # print(i_tn, 'mnn_true ->', mnn_true)
                        elif (type(mnn_lst)==np.ndarray):
                            mnn_true.extend (list(mnn_lst))
                            # if debug: print("parse_mis_position: type(mnn_lst), mnn_true")
                        else:
                            mnn_true.append (mnn_lst)
                            # if debug: print("parse_mis_position: type(mnn_lst), mnn_true")
                    if code_smnn_lst_00 is not None: 
                        if (type(code_smnn_lst_00)==list):
                            code_smnn_lst.extend (code_smnn_lst_00)
                        elif (type(code_smnn_lst_00)==np.ndarray):
                            code_smnn_lst.extend (list(code_smnn_lst_00))
                            # print("type(code_smnn_lst_00), code_smnn_lst", type(code_smnn_lst_00), code_smnn_lst)
                        else: # str or np.str_
                            code_smnn_lst.append(code_smnn_lst_00)
                            # print("type(code_smnn_lst_00), code_smnn_lst", type(code_smnn_lst_00), code_smnn_lst)
                        code_smnn_lst = list(set(code_smnn_lst))

        if len(tn_true)==0: tn_true = None
        elif len(tn_true)==1: tn_true = tn_true[0]
        if len(mnn_true)==0: mnn_true = None
        elif len(mnn_true)==1: mnn_true = mnn_true[0]
        else:
            mnn_true = list(set(mnn_true))
            if len(mnn_true)==1: mnn_true = mnn_true[0]
        if len(code_smnn_lst)==0: code_smnn_lst = None
        # elif len(code_smnn_lst)==1: code_smnn_lst = code_smnn_lst[0]
        # df_sel_63000_be[df_sel_63000_be['mnn_true'].notnull() & (df_sel_63000_be['mnn_true'].str.len()==0)]=None
        # df_sel_63000_be[df_sel_63000_be['tn_true'].notnull() & (df_sel_63000_be['tn_true'].str.len()==0)]=None
    
    if tn_true is not None and not (type(tn_true)==str or type(tn_true)==np.str_)\
        and (type(tn_true)==list or type(tn_true)==np.ndarray) and len(tn_true)==0:
        tn_true = None
    if mnn_true is not None and not (type(mnn_true)==str or type(mnn_true)==np.str_)\
        and (type(mnn_true)==list or type(mnn_true)==np.ndarray) and len(mnn_true)==0:
        mnn_true = None  
    # if debug: print(f"parse_mis_position: last_mnn_lst: {last_mnn_lst}, last_code_smnn_lst: {last_code_smnn_lst}, last_num_records: {last_num_records}")        
    
    tn_selected = tn_true
    tn_true = choice_tn(tn_selected)
    
    ath_name, ath_code, is_znvlp, is_narcotic, form_standard  = None, None, None, None, None
    # dosage, 
    dosage_standard_value, dosage_standard_unit, dosage_standard_value_str = None, None, None
    dosage_standard_value_str_refrmt = None
    # dosage_parsing_value,	dosage_parsing_unit, dosage_parsing_value_str = None, None, None
    lp_pack_1_num, lp_pack_2_num, lp_unit_okei, lp_unit, lp_consumer_total, lp_consumer_total_calc = None, None, None, None, None, None
    c_doze = None
    c_vol, name_ei_lp = None, None
    #if mnn_true is not None:
    #if num_records > 0:
    if debug: print(f"parse_mis_position: code_smnn_lst: {code_smnn_lst}")
    if code_smnn_lst is not None and len(code_smnn_lst)>0:
    #if mnn_lst is not None and len(mnn_lst)>0:
        #print("mnn_true is not None:")
        cols_return_lst = ['ath_name','ath_code', 'is_znvlp', 'is_narcotic', 'form_standard', 'dosage_grls_value'] # 'dosage_standard_value'
        cols_check_duplicates = ['ath_name','ath_code', 'is_znvlp', 'is_narcotic', 'form_standard']
        # индиффмрентно cols_check_duplicates попадаются словари и псики по к-ым drop_duplocatse не работают
        try:
            cols_srch  = {
                #'code': { 'ptn': [r"^(?:" , r")$"], 's_srch': "|".join(['(?:'+ re.escape(c) +')' for c in code_smnn_lst]),
                #'flags': re.I, 'regex': True},
                #'code': { 'ptn': ['' , ''], 's_srch': "|".join(['(?:'+ re.escape(c) +')' for c in code_smnn_lst]),
                # 'code': { 'ptn': ['' , ''], 's_srch': "|".join(['(?:'+ c +')' for c in code_smnn_lst]),
                'code_smnn': { 'ptn': ['' , ''], 's_srch': "|".join(['(?:'+ c +')' for c in code_smnn_lst]),
                        'flags': re.I, 'regex': True}, #True
                #  'mnn_standard': { 'ptn': [r"^(?:" , r")$"], 's_srch': "|".join(['(?:'+ re.escape(c) +')' for c in mnn_lst]),
                                
                #'form_standard': { 'ptn': [r"^(?:" , r").*$"], 's_srch': form_standard, 'flags': re.I},
            }
            # if debug: print("parse_mis_position: cols_srch:");pprint(cols_srch)

            return_values, num_records = \
                select_cols_values_from_smnn( cols_srch, cols_return_lst, cols_check_duplicates, check_col_names=False, debug=debug)
            if debug: print(f"parse_mis_position: num_records: {num_records}, return_values: {return_values}")
            if num_records > 0:  
                ath_name, ath_code, is_znvlp, is_narcotic, form_standard, dosage_standard_value_str = return_values
                if type(is_znvlp) ==  list and True in is_znvlp: is_znvlp = True
            else: ath_name, ath_code, is_znvlp, is_narcotic, form_standard, dosage_standard_value_str  = None, None, None, None, None
                # if num_records > 1:  form_standard, is_znvlp = list(return_values[0,:]), list(return_values[1,:])
                # elif num_records == 1: form_standard, is_znvlp = return_values
                # form_standard, is_znvlp = pd.Series({"form_standard":form_standard, "is_znvlp": is_znvlp})
        except Exception as err:
            print("parse_mis_position: Error create cols_srch", err, code_smnn_lst)
            # Error create cols_srch name 'select_cols_values_from_smnn' is not defined
            
        if dosage_standard_value_str is not None:
            dosage_standard_value, dosage_standard_unit = extract_dosage_standard(dosage_standard_value_str, debug=debug)
            # dosage_parsing_value,	dosage_parsing_unit = \
            #       calc_parsing_doze(doze_proc, doze, doze_unit, pseudo_vol, pseudo_vol_unit, vol_unit, debug=debug)

            # c_doze, dosage_parsing_value_str = compare_standard_parsing_doze(dosage_standard_value_str, dosage_parsing_value, dosage_parsing_unit, debug=debug)
            c_doze = compare_standard_parsing_doze_02(dosage_standard_value_str, dosage_parsing_value_str, debug=debug)
            
            if not c_doze: # пробуем привести к правильной базе еи
                dosage_standard_value_str_refrmt = reformat_dosage_standard_value_str(dosage_standard_value_str, debug=debug)
                c_doze = compare_standard_parsing_doze_02(dosage_standard_value_str_refrmt, dosage_parsing_value_str, debug=debug)
            
            if c_doze:
                lp_pack_1_num, lp_pack_2_num, lp_unit_okei, lp_unit, lp_consumer_total, lp_consumer_total_calc = \
                    select_klp_packs_norm(tn_true,  form_standard, dosage_parsing_value_str, debug=debug)
                lp_pack_1_num = to_float(lp_pack_1_num)
                lp_pack_2_num = to_float(lp_pack_2_num)
                lp_consumer_total = to_float(lp_consumer_total)

                c_vol, name_ei_lp = compare_vol_norm_parsing(doze_group, lp_pack_1_num, lp_pack_2_num, lp_unit_okei, lp_unit, 
                              lp_consumer_total, lp_consumer_total_calc, consumer_total_parsing, vol, debug=debug)
                

    # else: ath_name, ath_code, is_znvlp, is_narcotic, form_standard  = None, None, None, None, None
    if debug_print: 
        print_debug(  mis_position, tn_ru, tn_lat, tn_ru_ext, tn_lat_ext, tn_ru_orig, tn_ru_ext_clean, 
            tn_selected, tn_true, 
            tn_by_tn, mnn_by_tn,
            tn_ru_clean, 
            pharm_form_type, pharm_form, 
            mnn_from_tn_ru_ext,  mnn_local_dict, mnn_true, 
            ath_name, ath_code, is_znvlp, is_narcotic, form_standard,
            doze_group, doze_proc, doze, doze_unit, pseudo_vol, pseudo_vol_unit, comlex_doze_list, comlex_doze_str, vol, vol_unit,
            pack_1_form_unify, pack_1_form,  pack_1_num, pack_2_form_unify, pack_2_form, pack_2_num, n_packs_str, consumer_total_parsing,
            dosage_standard_value_str, dosage_standard_value, dosage_standard_unit, 
            dosage_parsing_value_str, dosage_parsing_value,	dosage_parsing_unit,
            dosage_standard_value_str_refrmt,
            c_doze,
            lp_pack_1_num, lp_pack_2_num, lp_unit_okei, lp_unit, lp_consumer_total, lp_consumer_total_calc,
            c_vol, name_ei_lp )
    
    return  tn_ru, tn_lat, tn_ru_ext, tn_lat_ext, tn_ru_orig, tn_ru_ext_clean, \
    tn_selected, tn_true,\
    tn_by_tn, mnn_by_tn,\
    tn_ru_clean, \
    pharm_form_type, pharm_form, \
    mnn_from_tn_ru_ext,  mnn_local_dict, mnn_true, \
    ath_name, ath_code, is_znvlp, is_narcotic, form_standard,\
    doze_group, doze_proc, doze, doze_unit, pseudo_vol, pseudo_vol_unit, comlex_doze_list, comlex_doze_str, vol, vol_unit,\
    pack_1_form_unify, pack_1_form,  pack_1_num, pack_2_form_unify, pack_2_form, pack_2_num, consumer_total_parsing,\
    dosage_standard_value_str, dosage_standard_value, dosage_standard_unit, \
    dosage_standard_value_str_refrmt, \
    dosage_parsing_value_str, dosage_parsing_value,	dosage_parsing_unit,\
    c_doze,\
    lp_pack_1_num, lp_pack_2_num, lp_unit_okei, lp_unit, lp_consumer_total, lp_consumer_total_calc,\
    c_vol, name_ei_lp

def parse_mis_position_07_update(mis_position, 
        correct_cols, 
        correct_values,
        select_by_tn=False, parse_dozes=True, 
        debug=False, debug_print=False):

    # print(f"correct_cols: {correct_cols}, correct_values: {correct_values}")      
    # mnn_mis, tn_ru, tn_lat = def_mnn_mis(mis_position)
    # doze_unit, doze_unit_groups, vol_unparsed = def_dosages_vol_unparsed(mis_position, mnn_mis )
    # if debug: print(f"doze_unit: '{doze_unit}', doze_unit_groups: '{doze_unit_groups}', vol_unparsed: '{vol_unparsed}'")
    # dosage, measurement_unit, pseudo_vol, vol  = def_doze_measurement_unit(doze_unit, doze_unit_groups, vol_unparsed)
    #dosage_per_farm_form_unit = calc_dosage_per_farm_form_unit(dosage, measurement_unit, pseudo_vol, vol)
    #group_unify = dict_MISposition_group.get(mis_position)
    
    mis_position_w = mis_position
    # update 01/10/2022
    mnn_mis, tn_ru, tn_lat = def_mnn_mis(mis_position)
    if mnn_mis is not None: 
        mnn_unparsed = re.sub(mnn_mis, "", mis_position)
    
    # update 01/10/2022 ###########################
    tn_ru, tn_lat, tn_ext, pharm_form_type, pharm_form = extract_TN_ext(mis_position, debug=False)  
    #if mnn_unparsed is not None:
    #    tn_ru, tn_lat, tn_ext, pharm_form_type, pharm_form = extract_TN_ext(mnn_unparsed, debug=False)  
    #else: tn_ru, tn_lat, tn_ext, pharm_form_type, pharm_form = extract_TN_ext(mis_position, debug=False)  
    if debug: print(f"parse_mis_position_07_update: pharm_form_type: '{pharm_form_type}', '{pharm_form}'")
    
    if tn_ru is not None:
        tn_ru_clean, mnn_from_tn_ru, pharm_form_from_tn_ru, pharm_form_type_from_tn_ru = correct_tn_ru_ext(tn_ru)
    else: tn_ru_clean, mnn_from_tn_ru, pharm_form_from_tn_ru, pharm_form_type_from_tn_ru = None, None, '#Н/Д', '#Н/Д'
    
    #pharm_form_type = pharm_form_type
    tn_ru_ext, tn_lat_ext = update__tn_ru_ext__tn_lat_ext(tn_ext, debug=False)

    if tn_ru_ext is  None: 
        tn_ru_ext = get_tn_ru_ext_from_dict(tn_lat_ext, tn_lat)
    
    if tn_ru_ext is not None:
        tn_ru_ext_clean, mnn_from_tn_ru_ext, pharm_form_from_tn_ru_ext, pharm_form_type_from_tn_ru_ext = \
        correct_tn_ru_ext(tn_ru_ext)
    else: tn_ru_ext_clean, mnn_from_tn_ru_ext, pharm_form_from_tn_ru_ext, pharm_form_type_from_tn_ru_ext = None, None, '#Н/Д', '#Н/Д'

    if pharm_form_type is None or pharm_form_type=='#Н/Д':
        pharm_form = pharm_form_from_tn_ru or pharm_form_from_tn_ru_ext
        pharm_form_type = pharm_form_type_from_tn_ru or pharm_form_type_from_tn_ru_ext
    
    if 'pharm_form_type_correct' in correct_cols:
        pharm_form_type_correct = correct_values.get('pharm_form_type_correct')
        if not (pharm_form_type_correct is None or \
            ((type(pharm_form_type_correct) == float) or (type(pharm_form_type_correct) == np.float64)) and math.isnan(pharm_form_type_correct)):
            pharm_form_type = correct_values.get('pharm_form_type_correct')

    doze_group, doze_proc, doze, doze_unit, doze_str, complex_doze_list, complex_doze_str, pseudo_vol, pseudo_vol_unit, vol, vol_unit, vol_str = \
        None,None,None,None,None,None,None,None,None, None, None, None
    dosage_parsing_value,	dosage_parsing_unit, dosage_parsing_value_str = None, None, None        
    if parse_dozes:
        # !!!  pharm_form_type vs pharm_form_unify
        doze_group, doze_proc, doze, doze_unit, doze_str, pseudo_vol, pseudo_vol_unit, complex_doze_list, complex_doze_str, vol, vol_unit, vol_str = \
                 extract_doze_vol_02(mis_position, tn_ru_ext, tn_lat_ext, pharm_form_type, pharm_form, debug=debug)
                 #### НЕ ЗАБУДЬ # !!!  pharm_form_type - правильно vs pharm_form_unify - неправильно
                #  extract_doze_vol_02(mis_position, tn_ru_ext, tn_lat_ext, pharm_form_unify, pharm_form, debug=debug)
        
        
        # dosage_parsing_value,	dosage_parsing_unit = \
        #            calc_parsing_doze(doze_proc, doze, doze_unit, pseudo_vol, pseudo_vol_unit, vol_unit, debug=debug)
        if complex_doze_list is None: # не сложная - простая - дозировка
            # doze_parts_list = doze_pseudo_to_doze_parts_list(doze_str, doze, doze_unit, pseudo_vol, pseudo_vol_unit, debug = debug)
            dosage_parsing_value, dosage_parsing_unit = \
                   calc_parsing_doze(doze_proc, doze, doze_unit, pseudo_vol, pseudo_vol_unit, vol_unit, debug=debug)
            
            # if dosage_parsing_value is not None:
                # dosage_parsing_value = str(dosage_parsing_value)
            # doze_parts_list = doze_pseudo_to_doze_parts_list(doze_str, dosage_parsing_value, doze_unit, pseudo_vol, pseudo_vol_unit, debug = debug)
            # if doze is None and dosage_parsing_unit is not None: 
            if dosage_parsing_unit is not None: 
                # может быть просто число без ЕИ дозировки
                pos_doze_unit = dosage_parsing_unit.rfind('/')
                if pos_doze_unit >- 1:
                    doze_unit_01 = dosage_parsing_unit[:pos_doze_unit]
                    pseudo_vol_unit_01 = dosage_parsing_unit[pos_doze_unit+1:]
                else: 
                    doze_unit_01 = dosage_parsing_unit
                    pseudo_vol_unit_01 = None
                pseudo_vol_01 = None
            else:
                doze_unit_01 = doze_unit
                pseudo_vol_unit_01 = pseudo_vol_unit
                pseudo_vol_01 = pseudo_vol

            # doze_parts_list = doze_pseudo_to_doze_parts_list_02(doze_str, dosage_parsing_value, doze_unit_01, pseudo_vol, pseudo_vol_unit, debug = debug)
            doze_parts_list = doze_pseudo_to_doze_parts_list_02(doze_str, dosage_parsing_value, doze_unit_01, pseudo_vol_01, pseudo_vol_unit_01, debug = debug)
            # dosage_parsing_value_str = make_doze_str_frmt_02(doze_parts_list, debug = debug )
            dosage_parsing_value_str, _, _ = make_doze_str_frmt_03(doze_parts_list, debug = debug )
        else:
            # dosage_parsing_value, dosage_parsing_unit = doze, doze_unit
            # dosage_parsing_value, dosage_parsing_unit = \
            #     calc_parsing_doze_02(doze_proc, doze, doze_unit, pseudo_vol, pseudo_vol_unit, vol_unit, debug=debug)
            # if pseudo_vol_unit is not None and dosage_parsing_unit is not None: 
            #     dosage_parsing_unit += pseudo_vol_unit
            # dosage_parsing_value_str = make_doze_str_frmt_02(complex_doze_list, debug = debug )
            dosage_parsing_value_str, dosage_parsing_value, dosage_parsing_unit = make_doze_str_frmt_03(complex_doze_list, debug = debug )

        # dosage_parsing_value_str = form_dosage_parsing_value_str(dosage_parsing_value, dosage_parsing_unit, debug = debug)

        doze = to_float(doze)
        vol = to_float(vol)
        pseudo_vol = to_float(pseudo_vol)

        # doze_group, doze_proc, doze, doze_unit, doze_str, pseudo_vol, pseudo_vol_unit, vol, vol_unit, vol_str =\
        #  extract_doze_vol_02(mis_position, tn_ru_ext, tn_lat_ext, pharm_form_type, pharm_form, debug=debug)
         # Berotec N 100mkg/dosa 200 доз N1 аэрозоль
        # if debug: print("dozes:", doze_group, doze, doze_unit, doze_str, pseudo_vol, pseudo_vol_unit, vol, vol_unit, vol_str)
    # else: 
    #   doze_group, doze_proc, doze, doze_unit, doze_str, pseudo_vol, pseudo_vol_unit, vol, vol_unit, vol_str = \
    #     None,None,None,None,None,None,None,None,None, None
    pack_1_form_unify, pack_1_form,  pack_1_num, pack_2_form_unify, pack_2_form, pack_2_num, n_packs_str =\
        extract_packs(mis_position, debug=False)
    pack_1_num = to_float(pack_1_num)
    pack_2_num = to_float(pack_2_num)
    consumer_total_parsing = calc_consumer_total(pack_1_num, pack_2_num, debug = debug)

    tn_ru_orig, mnn_local_dict = def_tn_ru_orig(tn_lat_ext, tn_lat, debug=False)
    if debug: print(f"parse_mis_position_07_update: inner: tn_lat: '{tn_lat}', tn_lat_ext: '{tn_lat_ext}', tn_ru_orig: '{tn_ru_orig}, tn_ru_ext: '{tn_ru_ext}', 'tn_ru: '{tn_ru}'")
    # if 'tn_correct' in correct_cols: print(f"correct_values.get('tn_correct'): {correct_values.get('tn_correct')}")
    tn_by_tn, mnn_by_tn = None, None
    if select_by_tn:
        # if flags.get('correct_tn'): #==True,
        tn_correct = None
        if 'tn_correct' in correct_cols:
            tn_correct = correct_values.get('tn_correct')
        if not (tn_correct is None or \
            ((type(tn_correct) == float) or (type(tn_correct) == np.float64)) and math.isnan(tn_correct)):
            # tn = correct_values.get('tn_correct')
            tn = tn_correct
            mnn_by_tn, tn_by_tn = select_klp_mnn_tn_by_tn(tn, debug=debug)
            if type(mnn_by_tn)==np.ndarray: mnn_by_tn = list(mnn_by_tn)
            if type(tn_by_tn)==np.ndarray: tn_by_tn = list(tn_by_tn)
        else:
            mnn_by_tn, tn_by_tn = [], []
            for i_tn, tn in enumerate([tn_ru_orig, tn_ru_ext_clean, tn_ru_clean]):
                # tn_by_tn, mnn_by_tn = select_klp_mnn_tn_by_tn(tn, debug=debug)
                # print(f"parse_mis_position_07_update: tn: {i_tn}, {tn}")
                mnn_by_tn_pre, tn_by_tn_pre = select_klp_mnn_tn_by_tn(tn, debug=debug)
                if tn_by_tn_pre is not None:  #break
                    if (type(tn_by_tn_pre)==str) or (type(tn_by_tn_pre)==np.str_):
                        tn_by_tn.append(tn_by_tn_pre)
                    elif (type(tn_by_tn_pre)==list):
                        # print(f"parse_mis_position_07_update: list tn_by_tn before: {tn_by_tn}")
                        # print(f"parse_mis_position_07_update: tn_by_tn_pre {tn_by_tn_pre}")
                        tn_by_tn.extend(tn_by_tn_pre)
                        # print(f"parse_mis_position_07_update: list  tn_by_tn after: {tn_by_tn}")
                    elif (type(tn_by_tn_pre)==np.ndarray):
                        # print(f"parse_mis_position_07_update: np.ndarray tn_by_tn before: {tn_by_tn}")
                        # print(f"parse_mis_position_07_update: tn_by_tn_pre {tn_by_tn_pre}")
                        tn_by_tn.extend(list(tn_by_tn_pre))
                        # print(f"parse_mis_position_07_update: np.ndarray tn_by_tn after: {tn_by_tn}")
                        
                        # tn_by_tn.extend(tn_by_tn_pre)
                    # if i_tn ==0:
                    #     tn_by_tn = [tn_by_tn_pre]
                if mnn_by_tn_pre is not None:
                    # mnn_by_tn.append(mnn_by_tn)
                    if (type(mnn_by_tn_pre)==str) or (type(mnn_by_tn_pre)==np.str_):
                        mnn_by_tn.append(mnn_by_tn_pre)
                    elif (type(mnn_by_tn_pre)==list):
                        mnn_by_tn.extend(mnn_by_tn_pre)
                    elif (type(mnn_by_tn_pre)==np.ndarray):
                        mnn_by_tn.extend(list(mnn_by_tn_pre))
        if tn_by_tn is not None and not((type(tn_by_tn)==str) or (type(tn_by_tn)==np.str_)):
            if type(tn_by_tn)==np.ndarray: 
                tn_by_tn = list(tn_by_tn) # pass # 
            try:
                tn_by_tn = list(set(tn_by_tn))
                # tn_by_tn = np_unique_nan(tn_by_tn)
            except Exception as err:
                print("parse_mis_position_07_update:", err)
                print("--> tn_by_tn:", type(tn_by_tn), tn_by_tn)

            if len(tn_by_tn) == 0: tn_by_tn = None
            elif len(tn_by_tn) == 1: tn_by_tn = tn_by_tn[0]
        if mnn_by_tn is not None and not((type(mnn_by_tn)==str) or (type(mnn_by_tn)==np.str_)):
            if type(mnn_by_tn)==np.ndarray: mnn_by_tn = list(mnn_by_tn)
            try: 
                mnn_by_tn = list(set(mnn_by_tn))
            except Exception as err:
                print("parse_mis_position_07_update:", err)
                print("--> mnn_by_tn:", type(mnn_by_tn), mnn_by_tn)
            if len(mnn_by_tn) == 0: mnn_by_tn = None
            elif len(mnn_by_tn) == 1: mnn_by_tn = mnn_by_tn[0]

    num_records, tn_true, mnn_true, mnn_lst, code_smnn_lst = 0, [], [], None, []
    last_num_records, last_mnn_lst, last_code_smnn_lst = 0, None, None
    if not(pharm_form_type is None or pharm_form_type=='#Н/Д'):
        
        # if flags.get('correct_tn'): #==True,
        # if 'tn_correct' in correct_cols and correct_values.get('tn_correct') is not None:
        # # if 'tn_correct' in correct_cols:
        #     tn = correct_values.get('tn_correct')
        tn_correct = None
        if 'tn_correct' in correct_cols:
            tn_correct = correct_values.get('tn_correct')
        if not (tn_correct is None or \
            ((type(tn_correct) == float) or (type(tn_correct) == np.float64)) and math.isnan(tn_correct)):
            # tn = correct_values.get('tn_correct')
            tn = tn_correct

            if debug: print("parse_mis_position: tn --->", tn)
            # if tn is not None: 
            if tn is not None and not (((type(tn)==float) or (type(tn)==np.float64)) and math.isnan(tn)):
                # после восставноления из Excel проверка доп условий
                mnn_lst, code_smnn_lst_00, num_records = \
                select_klp_mnn_by_tn__pharm_form_type(tn.capitalize(), pharm_form_type, strict_select = False, debug=debug )
                if debug: print("parse_mis_position: tn, mnn_lst, code_smnn_lst_00, num_records --->", 
                    tn, mnn_lst, code_smnn_lst_00, num_records)

                if num_records > 0: 
                    tn_true.append(tn)
                    tn_true = list(set(tn_true))
                    if mnn_lst is not None: 
                        if (type(mnn_lst)==list):
                            mnn_true.extend (mnn_lst) #list(set())
                            # if debug: print("parse_mis_position: type(mnn_lst), mnn_true")
                        # mnn_true = list(set(mnn_true))
                        # print(i_tn, 'mnn_true ->', mnn_true)
                        elif (type(mnn_lst)==np.ndarray):
                            mnn_true.extend (list(mnn_lst))
                            # if debug: print("parse_mis_position: type(mnn_lst), mnn_true")
                        else:
                            mnn_true.append (mnn_lst)
                            # if debug: print("parse_mis_position: type(mnn_lst), mnn_true")
                    if code_smnn_lst_00 is not None: 
                        if (type(code_smnn_lst_00)==list):
                            code_smnn_lst.extend (code_smnn_lst_00)
                        elif (type(code_smnn_lst_00)==np.ndarray):
                            code_smnn_lst.extend (list(code_smnn_lst_00))
                            # print("type(code_smnn_lst_00), code_smnn_lst", type(code_smnn_lst_00), code_smnn_lst)
                        else: # str or np.str_
                            code_smnn_lst.append(code_smnn_lst_00)
                            # print("type(code_smnn_lst_00), code_smnn_lst", type(code_smnn_lst_00), code_smnn_lst)
                        code_smnn_lst = list(set(code_smnn_lst))

            # if len(tn_true)==0: tn_true = None
            # elif len(tn_true)==1: tn_true = tn_true[0]

            if len(mnn_true)==0: mnn_true = None
            elif len(mnn_true)==1: mnn_true = mnn_true[0]
            else:
                # if type(mnn_true)==list:
                mnn_true = list(set(mnn_true))
                if len(mnn_true)==1: mnn_true = mnn_true[0]
            if len(code_smnn_lst)==0: code_smnn_lst = None
        else:
            #for i_tn, tn in enumerate([tn_ru_orig, tn_ru_ext, tn_ru]):
            for i_tn, tn in enumerate([tn_ru_orig, tn_ru_ext_clean, tn_ru_clean]):
                if debug: print("parse_mis_position: tn --->", i_tn, tn)
                if tn is not None:
                    mnn_lst, code_smnn_lst_00, num_records = \
                    select_klp_mnn_by_tn__pharm_form_type(tn.capitalize(), pharm_form_type, strict_select = False, debug=debug )
                    if debug: print("parse_mis_position: tn, mnn_lst, code_smnn_lst_00, num_records --->", 
                        i_tn, tn, mnn_lst, code_smnn_lst_00, num_records)

                    if num_records > 0: 
                        tn_true.append(tn)
                        tn_true = list(set(tn_true))
                        if mnn_lst is not None: 
                            if (type(mnn_lst)==list):
                                mnn_true.extend (mnn_lst) #list(set())
                                # if debug: print("parse_mis_position: type(mnn_lst), mnn_true")
                            # mnn_true = list(set(mnn_true))
                            # print(i_tn, 'mnn_true ->', mnn_true)
                            elif (type(mnn_lst)==np.ndarray):
                                mnn_true.extend (list(mnn_lst))
                                # if debug: print("parse_mis_position: type(mnn_lst), mnn_true")
                            else:
                                mnn_true.append (mnn_lst)
                                # if debug: print("parse_mis_position: type(mnn_lst), mnn_true")
                        if code_smnn_lst_00 is not None: 
                            if (type(code_smnn_lst_00)==list):
                                code_smnn_lst.extend (code_smnn_lst_00)
                            elif (type(code_smnn_lst_00)==np.ndarray):
                                code_smnn_lst.extend (list(code_smnn_lst_00))
                                # print("type(code_smnn_lst_00), code_smnn_lst", type(code_smnn_lst_00), code_smnn_lst)
                            else: # str or np.str_
                                code_smnn_lst.append(code_smnn_lst_00)
                                # print("type(code_smnn_lst_00), code_smnn_lst", type(code_smnn_lst_00), code_smnn_lst)
                            code_smnn_lst = list(set(code_smnn_lst))

            if len(tn_true)==0: tn_true = None
            elif len(tn_true)==1: tn_true = tn_true[0]

            if len(mnn_true)==0: mnn_true = None
            elif len(mnn_true)==1: mnn_true = mnn_true[0]
            else:
                # if type(mnn_true)==list:
                mnn_true = list(set(mnn_true))
                if len(mnn_true)==1: mnn_true = mnn_true[0]
            if len(code_smnn_lst)==0: code_smnn_lst = None
            # elif len(code_smnn_lst)==1: code_smnn_lst = code_smnn_lst[0]
            # df_sel_63000_be[df_sel_63000_be['mnn_true'].notnull() & (df_sel_63000_be['mnn_true'].str.len()==0)]=None
            # df_sel_63000_be[df_sel_63000_be['tn_true'].notnull() & (df_sel_63000_be['tn_true'].str.len()==0)]=None
    
    if tn_true is not None and not (type(tn_true)==str or type(tn_true)==np.str_)\
        and (type(tn_true)==list or type(tn_true)==np.ndarray) and len(tn_true)==0:
        tn_true = None
    if mnn_true is not None and not (type(mnn_true)==str or type(mnn_true)==np.str_)\
        and (type(mnn_true)==list or type(mnn_true)==np.ndarray) and len(mnn_true)==0:
        mnn_true = None  
    # if debug: print(f"parse_mis_position: last_mnn_lst: {last_mnn_lst}, last_code_smnn_lst: {last_code_smnn_lst}, last_num_records: {last_num_records}")        
    
    tn_selected = tn_true
    tn_true = choice_tn(tn_selected)
    
    ath_name, ath_code, is_znvlp, is_narcotic, form_standard  = None, None, None, None, None
    # dosage, 
    dosage_standard_value, dosage_standard_unit, dosage_standard_value_str = None, None, None
    dosage_standard_value_str_refrmt = None
    # dosage_parsing_value,	dosage_parsing_unit, dosage_parsing_value_str = None, None, None
    lp_pack_1_num, lp_pack_1_name, lp_pack_2_num, lp_pack_2_name, lp_unit_okei_name, lp_unit_name, lp_consumer_total, lp_consumer_total_calc,\
                        is_dosed, mass_volume_num, mass_volume_name =\
        None, None, None, None, None, None, None, None, None, None, None
    c_doze = None
    c_vol, c_vol_unit, name_ei_lp = None, None, None
    c_pack, c_mnn, c_form = None, None, None
    vol_calc, vol_unit_calc = None, None
    vol_klp, vol_unit_klp = None, None
    #if mnn_true is not None:
    #if num_records > 0:
    if debug: print(f"parse_mis_position: code_smnn_lst: {code_smnn_lst}")
    if code_smnn_lst is not None and len(code_smnn_lst)>0:
    #if mnn_lst is not None and len(mnn_lst)>0:
        #print("mnn_true is not None:")
        cols_return_lst = ['ath_name','ath_code', 'is_znvlp', 'is_narcotic', 'form_standard', 'dosage_grls_value'] # 'dosage_standard_value'
        cols_check_duplicates = ['ath_name','ath_code', 'is_znvlp', 'is_narcotic', 'form_standard']
        # индиффмрентно cols_check_duplicates попадаются словари и псики по к-ым drop_duplocatse не работают
        try:
            cols_srch  = {
                #'code': { 'ptn': [r"^(?:" , r")$"], 's_srch': "|".join(['(?:'+ re.escape(c) +')' for c in code_smnn_lst]),
                #'flags': re.I, 'regex': True},
                #'code': { 'ptn': ['' , ''], 's_srch': "|".join(['(?:'+ re.escape(c) +')' for c in code_smnn_lst]),
                # 'code': { 'ptn': ['' , ''], 's_srch': "|".join(['(?:'+ c +')' for c in code_smnn_lst]),
                'code_smnn': { 'ptn': ['' , ''], 's_srch': "|".join(['(?:'+ c +')' for c in code_smnn_lst]),
                        'flags': re.I, 'regex': True}, #True
                #  'mnn_standard': { 'ptn': [r"^(?:" , r")$"], 's_srch': "|".join(['(?:'+ re.escape(c) +')' for c in mnn_lst]),
                                
                #'form_standard': { 'ptn': [r"^(?:" , r").*$"], 's_srch': form_standard, 'flags': re.I},
            }
            # if debug: print("parse_mis_position: cols_srch:");pprint(cols_srch)

            return_values, num_records = \
                select_cols_values_from_smnn( cols_srch, cols_return_lst, cols_check_duplicates, check_col_names=False, debug=debug)
            if debug: print(f"parse_mis_position: num_records: {num_records}, return_values: {return_values}")
            if num_records > 0:  
                ath_name, ath_code, is_znvlp, is_narcotic, form_standard, dosage_standard_value_str = return_values
                if type(is_znvlp) ==  list and True in is_znvlp: is_znvlp = True
            else: ath_name, ath_code, is_znvlp, is_narcotic, form_standard, dosage_standard_value_str  = None, None, None, None, None
                # if num_records > 1:  form_standard, is_znvlp = list(return_values[0,:]), list(return_values[1,:])
                # elif num_records == 1: form_standard, is_znvlp = return_values
                # form_standard, is_znvlp = pd.Series({"form_standard":form_standard, "is_znvlp": is_znvlp})
        except Exception as err:
            print("parse_mis_position: Error create cols_srch", err, code_smnn_lst)
            # Error create cols_srch name 'select_cols_values_from_smnn' is not defined
            
        if dosage_standard_value_str is not None:
            dosage_standard_value, dosage_standard_unit = extract_dosage_standard(dosage_standard_value_str, debug=debug)
            # dosage_parsing_value,	dosage_parsing_unit = \
            #       calc_parsing_doze(doze_proc, doze, doze_unit, pseudo_vol, pseudo_vol_unit, vol_unit, debug=debug)

            # c_doze, dosage_parsing_value_str = compare_standard_parsing_doze(dosage_standard_value_str, dosage_parsing_value, dosage_parsing_unit, debug=debug)
            dosage_parsing_value_str_correct = None
            if 'dosage_parsing_value_str_correct' in correct_cols:
                dosage_parsing_value_str_correct = correct_values.get('dosage_parsing_value_str_correct')
            if not (dosage_parsing_value_str_correct is None or \
                ((type(dosage_parsing_value_str_correct) == float) or (type(dosage_parsing_value_str_correct) == np.float64)) \
                    and math.isnan(dosage_parsing_value_str_correct)):
                dosage_parsing_value_str_work = dosage_parsing_value_str_correct
            # if 'dosage_parsing_value_str_correct' in correct_cols and correct_values.get('dosage_parsing_value_str_correct') is not None:
            #     dosage_parsing_value_str_work = correct_values.get('dosage_parsing_value_str_correct')
            else:
                dosage_parsing_value_str_work = dosage_parsing_value_str
            
            if ((type(dosage_parsing_value_str_work)==str) or (type(dosage_parsing_value_str_work)==np.str_)) \
                and ((type(dosage_standard_value_str)==str) or (type(dosage_standard_value_str)==np.str_)) \
                and (dosage_parsing_value_str_work == '~') and (dosage_standard_value_str == '~'):
                c_doze = True
                i_doze = -1
            else:
                # c_doze, i_doze = compare_standard_parsing_doze_02(dosage_standard_value_str, dosage_parsing_value_str, debug=debug)
                c_doze, i_doze = compare_standard_parsing_doze_02(dosage_standard_value_str, dosage_parsing_value_str_work, debug=debug)

                if not c_doze: # пробуем привести к правильной базе еи
                    dosage_standard_value_str_refrmt = reformat_dosage_standard_value_str(dosage_standard_value_str, debug=debug)
                    c_doze_unit, i_doze_02 = compare_standard_parsing_doze_02(dosage_standard_value_str_refrmt, dosage_parsing_value_str_work, debug=debug)
            
            if c_doze:
                # lp_pack_1_num, lp_pack_2_num, lp_unit_okei, lp_unit, lp_consumer_total, lp_consumer_total_calc = \
                #     select_klp_packs_norm(tn_true,  form_standard, dosage_parsing_value_str, debug=debug)
                if i_doze is None: 
                    # такого здесь быть не может: если c_doze is None то и i_doze is None
                    dosage_str = ''
                elif i_doze == -1: # dosage_standard_value_str - строка не список строк
                    dosage_str = dosage_standard_value_str
                elif i_doze > -1: # индекс в спсике dosage_standard_value_str
                    dosage_str = dosage_standard_value_str[i_doze]
                else: 
                    dosage_str = '' # страхуемся закрываем ветки
                if debug: print(f"parse_mis_position_07_update: tn_true: '{tn_true}', dosage_str: '{dosage_str}', form_standard: '{form_standard}'")
                lp_pack_1_num, lp_pack_1_name, lp_pack_2_num, lp_pack_2_name, lp_unit_okei_name, lp_unit_name, lp_consumer_total, lp_consumer_total_calc,\
                        is_dosed, mass_volume_num, mass_volume_name = \
                    select_klp_packs_norm_02(tn_true,  form_standard, dosage_str, debug=debug)    
                # select_klp_packs_norm_02(tn_true,  form_standard, dosage_standard_value_str, debug=debug)
                lp_pack_1_num = to_float(lp_pack_1_num)
                lp_pack_2_num = to_float(lp_pack_2_num)
                lp_consumer_total = to_float(lp_consumer_total)
                mass_volume_num = to_float(mass_volume_num)

                
                # c_vol, name_ei_lp = compare_vol_norm_parsing(doze_group, lp_pack_1_num, lp_pack_2_num, lp_unit_okei_name, lp_unit_name, 
                #               lp_consumer_total, lp_consumer_total_calc, consumer_total_parsing, vol, debug=debug)
                
                
                # vol_calc, vol_unit_calc = calc_volume(doze_group, lp_unit_name, pack_1_num, 
                # form_standard, consumer_total, consumer_total_kis, dosage_standard_unit, mass_volume_name, 
                # mass_volume_num,
                # debug=debug)
                # vol_calc, vol_unit_calc = calc_volume(doze_group, lp_unit_name, pack_1_num, 
                # vol_calc, vol_unit_calc = calc_volume_02(doze_group, lp_unit_name, lp_pack_1_num, pack_1_num, 
                vol_klp, vol_unit_klp = calc_volume_02(doze_group, lp_unit_name, lp_pack_1_num, pack_1_num, 
                    form_standard, lp_consumer_total, consumer_total_parsing, dosage_parsing_unit, mass_volume_name, 
                    mass_volume_num, debug=debug)
                # vol_calc, vol_unit_calc = calc_volume(doze_group, lp_unit_name, pack_1_num, 
                #     form_standard, lp_consumer_total, consumer_total_parsing, dosage_parsing_unit, mass_volume_name, 
                #     mass_volume_num, debug=debug)
                # vol_calc = to_float(vol_calc)
                vol_klp = to_float(vol_klp)
                
                vol_correct, vol_unit_correct = None, None
                if 'vol_correct' in correct_cols:
                    vol_correct = correct_values.get('vol_correct')
                    vol_unit_correct = correct_values.get('vol_unit_correct')
    
                if not (vol_correct is None or \
                    ((type(vol_correct) == float) or (type(vol_correct) == np.float64)) \
                        and math.isnan(vol_correct)):
                    vol_w, vol_unit_w = vol_correct, vol_unit_correct
                else: 
                    vol_w, vol_unit_w = vol, vol_unit
                # c_vol, name_ei_lp = compare_vol_norm_parsing(doze_group, lp_pack_1_num, lp_pack_2_num, lp_unit_okei_name, lp_unit_name, 
                #               lp_consumer_total, lp_consumer_total_calc, consumer_total_parsing, vol, debug=debug)
                # vol_calc, vol_unit_calc, c_vol, c_vol_unit = control_vol(doze_group, vol, vol_unit, vol_klp, vol_unit_klp, debug=debug)
                vol_calc, vol_unit_calc, c_vol, c_vol_unit = control_vol(doze_group, vol_w, vol_unit_w, vol_klp, vol_unit_klp, debug=debug)

                
                # dosage_standard_unit
    if consumer_total_parsing is not None: c_pack = 1
    else: c_pack = None

    if mnn_true is None: c_mnn = 0
    elif (type(mnn_true) == str) or (type(mnn_true) == np.str_): c_mnn = 1 # строка
    elif ((type(mnn_true) == list) or (type(mnn_true) == np.ndarray)) and (len(mnn_true)>1) : c_mnn = 2 # список
    else: c_mnn = None
    
    if form_standard is None: c_form = 0
    elif (type(form_standard) == str) or (type(form_standard) == np.str_): c_form = 1 # строка
    elif ((type(form_standard) == list) or (type(form_standard) == np.ndarray)) and (len(form_standard)>1) : c_form = 2 # список
    else: c_form = None
    
    dosage_correct_value, dosage_correct_unit = None, None
    dosage_parsing_value_str_correct = None
    if 'dosage_parsing_value_str_correct' in correct_cols:
        dosage_parsing_value_str_correct = correct_values.get('dosage_parsing_value_str_correct')
    
    if (dosage_parsing_value_str_correct is None or \
            ((type(dosage_parsing_value_str_correct) == float) or (type(dosage_parsing_value_str_correct) == np.float64)) \
            and math.isnan(dosage_parsing_value_str_correct)):
        # dosage_parsing_value_w, dosage_parsing_unit_w = dosage_parsing_value, dosage_parsing_unit
        if dosage_parsing_value_str is not None:
            if '+' in dosage_parsing_value_str:
                dosage_parsing_value_w, dosage_parsing_unit_w = extract_complex_dosage(dosage_parsing_value_str, debug=debug)
            else:
                dosage_parsing_value_w, dosage_parsing_unit_w = extract_simple_dosage(dosage_parsing_value_str, debug=debug)
        else:
            dosage_parsing_value_w, dosage_parsing_unit_w = None, None
        #     ls_doze, ls_doze_unit, ls_vol, ls_vol_unit, ls_doze_vol, ls_doze_vol_unit = \
        #         calc_ls_totals(dosage_parsing_value_w, dosage_parsing_unit_w,vol_calc, vol_unit_calc, debug=False)
        # # calc_ls_totals(dosage_parsing_value, dosage_parsing_unit,vol_calc, vol_unit_calc, debug=False)
    
    else:
        if '+' in dosage_parsing_value_str_correct:
            dosage_parsing_value_w, dosage_parsing_unit_w = extract_complex_dosage(dosage_parsing_value_str_correct, debug=debug)
        else:
            dosage_parsing_value_w, dosage_parsing_unit_w = extract_simple_dosage(dosage_parsing_value_str_correct, debug=debug)
        dosage_correct_value, dosage_correct_unit = dosage_parsing_value_w, dosage_parsing_unit_w
    
    vol_correct, vol_unit_correct = None, None
    if 'vol_correct' in correct_cols:
        vol_correct = correct_values.get('vol_correct')
        vol_unit_correct = correct_values.get('vol_unit_correct')

    if not (vol_correct is None or \
        ((type(vol_correct) == float) or (type(vol_correct) == np.float64)) \
            and math.isnan(vol_correct)):
        vol_calc_w, vol_unit_calc_w = vol_correct, vol_unit_correct
    else: 
        vol_calc_w, vol_unit_calc_w = vol_calc, vol_unit_calc

    ls_doze, ls_doze_unit, ls_vol, ls_vol_unit, ls_doze_vol, ls_doze_vol_unit = \
        calc_ls_totals(dosage_parsing_value_w, dosage_parsing_unit_w, vol_calc_w, vol_unit_calc_w, debug=False)
        # calc_ls_totals(dosage_parsing_value, dosage_parsing_unit,vol_calc, vol_unit_calc, debug=False)
    
    # else: ath_name, ath_code, is_znvlp, is_narcotic, form_standard  = None, None, None, None, None
    if debug_print: 
        print_debug(  mis_position, tn_ru, tn_lat, tn_ru_ext, tn_lat_ext, tn_ru_orig, tn_ru_ext_clean, 
        tn_selected, tn_true,
        tn_by_tn, mnn_by_tn,
        tn_ru_clean, 
        pharm_form_type, pharm_form, 
        mnn_from_tn_ru_ext,  mnn_local_dict, mnn_true, 
        ath_name, ath_code, is_znvlp, is_narcotic, form_standard,
        doze_group, doze_proc, doze, doze_unit, pseudo_vol, pseudo_vol_unit, complex_doze_list, complex_doze_str, vol, vol_unit,
        pack_1_form_unify, pack_1_form,  pack_1_num, pack_2_form_unify, pack_2_form, pack_2_num, n_packs_str, consumer_total_parsing,
        dosage_standard_value_str, dosage_standard_value, dosage_standard_unit, 
        dosage_standard_value_str_refrmt,
        dosage_parsing_value_str, dosage_parsing_value, dosage_parsing_unit,
        dosage_correct_value, dosage_correct_unit,
        c_doze,
        lp_pack_1_num, lp_pack_1_name, lp_pack_2_num, lp_pack_2_name, lp_unit_okei_name, lp_unit_name, lp_consumer_total, lp_consumer_total_calc,
        is_dosed, mass_volume_num, mass_volume_name,
        vol_klp, vol_unit_klp,
        vol_calc, vol_unit_calc,
        c_vol, c_vol_unit, name_ei_lp,
        c_pack, c_mnn, c_form,
        ls_doze, ls_doze_unit, ls_vol, ls_vol_unit, ls_doze_vol, ls_doze_vol_unit 
                   
                   )
    
    return  tn_ru, tn_lat, tn_ru_ext, tn_lat_ext, tn_ru_orig, tn_ru_ext_clean, tn_selected, tn_true,\
    tn_by_tn, mnn_by_tn,\
    tn_ru_clean, \
    pharm_form_type, pharm_form, \
    mnn_from_tn_ru_ext,  mnn_local_dict, mnn_true, \
    ath_name, ath_code, is_znvlp, is_narcotic, form_standard,\
    doze_group, doze_proc, doze, doze_unit, pseudo_vol, pseudo_vol_unit, complex_doze_list, complex_doze_str, vol, vol_unit,\
    pack_1_form_unify, pack_1_form,  pack_1_num, pack_2_form_unify, pack_2_form, pack_2_num, consumer_total_parsing,\
    dosage_standard_value_str, dosage_standard_value, dosage_standard_unit, \
    dosage_standard_value_str_refrmt, \
    dosage_parsing_value_str, dosage_parsing_value,	dosage_parsing_unit,\
    dosage_correct_value, dosage_correct_unit,\
    c_doze,\
    lp_pack_1_num, lp_pack_1_name, lp_pack_2_num, lp_pack_2_name, lp_unit_okei_name, lp_unit_name, lp_consumer_total, lp_consumer_total_calc,\
    is_dosed, mass_volume_num, mass_volume_name,\
    vol_klp, vol_unit_klp,\
    vol_calc, vol_unit_calc,\
    c_vol, c_vol_unit, name_ei_lp,\
    c_pack, c_mnn, c_form,\
    ls_doze, ls_doze_unit, ls_vol, ls_vol_unit, ls_doze_vol, ls_doze_vol_unit



def parse_mis_position_07_update_00(mis_position, 
        correct_cols, 
        correct_values,
        select_by_tn=False, parse_dozes=True, 
        debug=False, debug_print=False):

    print(f"correct_cols: {correct_cols}, correct_values: {correct_values}")   
    # mnn_mis, tn_ru, tn_lat = def_mnn_mis(mis_position)
    # doze_unit, doze_unit_groups, vol_unparsed = def_dosages_vol_unparsed(mis_position, mnn_mis )
    # if debug: print(f"doze_unit: '{doze_unit}', doze_unit_groups: '{doze_unit_groups}', vol_unparsed: '{vol_unparsed}'")
    # dosage, measurement_unit, pseudo_vol, vol  = def_doze_measurement_unit(doze_unit, doze_unit_groups, vol_unparsed)
    #dosage_per_farm_form_unit = calc_dosage_per_farm_form_unit(dosage, measurement_unit, pseudo_vol, vol)
    #group_unify = dict_MISposition_group.get(mis_position)
    
    mis_position_w = mis_position
    # update 01/10/2022
    mnn_mis, tn_ru, tn_lat = def_mnn_mis(mis_position)
    if mnn_mis is not None: 
        mnn_unparsed = re.sub(mnn_mis, "", mis_position)
    
    # update 01/10/2022 ###########################
    tn_ru, tn_lat, tn_ext, pharm_form_type, pharm_form = extract_TN_ext(mis_position, debug=False)  
    #if mnn_unparsed is not None:
    #    tn_ru, tn_lat, tn_ext, pharm_form_type, pharm_form = extract_TN_ext(mnn_unparsed, debug=False)  
    #else: tn_ru, tn_lat, tn_ext, pharm_form_type, pharm_form = extract_TN_ext(mis_position, debug=False)  
    if debug: print(f"parse_mis_position: pharm_form_type: '{pharm_form_type}', '{pharm_form}'")
    
    if tn_ru is not None:
        tn_ru_clean, mnn_from_tn_ru, pharm_form_from_tn_ru, pharm_form_type_from_tn_ru = correct_tn_ru_ext(tn_ru)
    else: tn_ru_clean, mnn_from_tn_ru, pharm_form_from_tn_ru, pharm_form_type_from_tn_ru = None, None, '#Н/Д', '#Н/Д'
    
    #pharm_form_type = pharm_form_type
    tn_ru_ext, tn_lat_ext = update__tn_ru_ext__tn_lat_ext(tn_ext, debug=False)

    if tn_ru_ext is  None: 
        tn_ru_ext = get_tn_ru_ext_from_dict(tn_lat_ext, tn_lat)
    
    if tn_ru_ext is not None:
        tn_ru_ext_clean, mnn_from_tn_ru_ext, pharm_form_from_tn_ru_ext, pharm_form_type_from_tn_ru_ext = \
        correct_tn_ru_ext(tn_ru_ext)
    else: tn_ru_ext_clean, mnn_from_tn_ru_ext, pharm_form_from_tn_ru_ext, pharm_form_type_from_tn_ru_ext = None, None, '#Н/Д', '#Н/Д'

    if pharm_form_type is None or pharm_form_type=='#Н/Д':
        pharm_form = pharm_form_from_tn_ru or pharm_form_from_tn_ru_ext
        pharm_form_type = pharm_form_type_from_tn_ru or pharm_form_type_from_tn_ru_ext
    
    if 'pharm_form_type_correct' in correct_cols and correct_values.get('pharm_form_type_correct') is not None:
        pharm_form_type = correct_values.get('pharm_form_type_correct')

    doze_group, doze_proc, doze, doze_unit, doze_str, complex_doze_list, complex_doze_str, pseudo_vol, pseudo_vol_unit, vol, vol_unit, vol_str = \
        None,None,None,None,None,None,None,None,None, None, None, None
    dosage_parsing_value,	dosage_parsing_unit, dosage_parsing_value_str = None, None, None        
    if parse_dozes:
        # !!!  pharm_form_type vs pharm_form_unify
        doze_group, doze_proc, doze, doze_unit, doze_str, pseudo_vol, pseudo_vol_unit, complex_doze_list, complex_doze_str, vol, vol_unit, vol_str = \
                 extract_doze_vol_02(mis_position, tn_ru_ext, tn_lat_ext, pharm_form_type, pharm_form, debug=debug)
                 #### НЕ ЗАБУДЬ # !!!  pharm_form_type - правильно vs pharm_form_unify - неправильно
                #  extract_doze_vol_02(mis_position, tn_ru_ext, tn_lat_ext, pharm_form_unify, pharm_form, debug=debug)
        
        
        # dosage_parsing_value,	dosage_parsing_unit = \
        #            calc_parsing_doze(doze_proc, doze, doze_unit, pseudo_vol, pseudo_vol_unit, vol_unit, debug=debug)
        if complex_doze_list is None: # не сложная - простая - дозировка
            # doze_parts_list = doze_pseudo_to_doze_parts_list(doze_str, doze, doze_unit, pseudo_vol, pseudo_vol_unit, debug = debug)
            dosage_parsing_value, dosage_parsing_unit = \
                   calc_parsing_doze(doze_proc, doze, doze_unit, pseudo_vol, pseudo_vol_unit, vol_unit, debug=debug)
            
            # if dosage_parsing_value is not None:
                # dosage_parsing_value = str(dosage_parsing_value)
            # doze_parts_list = doze_pseudo_to_doze_parts_list(doze_str, dosage_parsing_value, doze_unit, pseudo_vol, pseudo_vol_unit, debug = debug)
            # if doze is None and dosage_parsing_unit is not None: 
            if dosage_parsing_unit is not None: 
                # может быть просто число без ЕИ дозировки
                pos_doze_unit = dosage_parsing_unit.rfind('/')
                if pos_doze_unit >- 1:
                    doze_unit_01 = dosage_parsing_unit[:pos_doze_unit]
                    pseudo_vol_unit_01 = dosage_parsing_unit[pos_doze_unit+1:]
                else: 
                    doze_unit_01 = dosage_parsing_unit
                    pseudo_vol_unit_01 = None
                pseudo_vol_01 = None
            else:
                doze_unit_01 = doze_unit
                pseudo_vol_unit_01 = pseudo_vol_unit
                pseudo_vol_01 = pseudo_vol

            # doze_parts_list = doze_pseudo_to_doze_parts_list_02(doze_str, dosage_parsing_value, doze_unit_01, pseudo_vol, pseudo_vol_unit, debug = debug)
            doze_parts_list = doze_pseudo_to_doze_parts_list_02(doze_str, dosage_parsing_value, doze_unit_01, pseudo_vol_01, pseudo_vol_unit_01, debug = debug)
            # dosage_parsing_value_str = make_doze_str_frmt_02(doze_parts_list, debug = debug )
            dosage_parsing_value_str, _, _ = make_doze_str_frmt_03(doze_parts_list, debug = debug )
        else:
            # dosage_parsing_value, dosage_parsing_unit = doze, doze_unit
            # dosage_parsing_value, dosage_parsing_unit = \
            #     calc_parsing_doze_02(doze_proc, doze, doze_unit, pseudo_vol, pseudo_vol_unit, vol_unit, debug=debug)
            # if pseudo_vol_unit is not None and dosage_parsing_unit is not None: 
            #     dosage_parsing_unit += pseudo_vol_unit
            # dosage_parsing_value_str = make_doze_str_frmt_02(complex_doze_list, debug = debug )
            dosage_parsing_value_str, dosage_parsing_value, dosage_parsing_unit = make_doze_str_frmt_03(complex_doze_list, debug = debug )

        # dosage_parsing_value_str = form_dosage_parsing_value_str(dosage_parsing_value, dosage_parsing_unit, debug = debug)

        doze = to_float(doze)
        vol = to_float(vol)
        pseudo_vol = to_float(pseudo_vol)

        # doze_group, doze_proc, doze, doze_unit, doze_str, pseudo_vol, pseudo_vol_unit, vol, vol_unit, vol_str =\
        #  extract_doze_vol_02(mis_position, tn_ru_ext, tn_lat_ext, pharm_form_type, pharm_form, debug=debug)
         # Berotec N 100mkg/dosa 200 доз N1 аэрозоль
        # if debug: print("dozes:", doze_group, doze, doze_unit, doze_str, pseudo_vol, pseudo_vol_unit, vol, vol_unit, vol_str)
    # else: 
    #   doze_group, doze_proc, doze, doze_unit, doze_str, pseudo_vol, pseudo_vol_unit, vol, vol_unit, vol_str = \
    #     None,None,None,None,None,None,None,None,None, None
    pack_1_form_unify, pack_1_form,  pack_1_num, pack_2_form_unify, pack_2_form, pack_2_num, n_packs_str =\
        extract_packs(mis_position, debug=False)
    pack_1_num = to_float(pack_1_num)
    pack_2_num = to_float(pack_2_num)
    consumer_total_parsing = calc_consumer_total(pack_1_num, pack_2_num, debug = debug)

    tn_ru_orig, mnn_local_dict = def_tn_ru_orig(tn_lat_ext, tn_lat, debug=False)
    if debug: print(f"parse_mis_position: inner: tn_lat: '{tn_lat}', tn_lat_ext: '{tn_lat_ext}', tn_ru_orig: '{tn_ru_orig}, tn_ru_ext: '{tn_ru_ext}', 'tn_ru: '{tn_ru}'")
    if 'tn_correct' in correct_cols: print(f"correct_values.get('tn_correct'): {correct_values.get('tn_correct')}")
    tn_by_tn, mnn_by_tn = None, None
    if select_by_tn:
        # if flags.get('correct_tn'): #==True,
        if 'tn_correct' in correct_cols and correct_values.get('tn_correct') is not None:
            tn = correct_values.get('tn_correct')
            mnn_by_tn, tn_by_tn = select_klp_mnn_tn_by_tn(tn, debug=debug)
            if type(mnn_by_tn)==np.ndarray: mnn_by_tn = list(mnn_by_tn)
            if type(tn_by_tn)==np.ndarray: tn_by_tn = list(tn_by_tn)
        else:
            mnn_by_tn, tn_by_tn = [], []
            for i_tn, tn in enumerate([tn_ru_orig, tn_ru_ext_clean, tn_ru_clean]):
                # tn_by_tn, mnn_by_tn = select_klp_mnn_tn_by_tn(tn, debug=debug)
                mnn_by_tn_pre, tn_by_tn_pre = select_klp_mnn_tn_by_tn(tn, debug=debug)
                if tn_by_tn_pre is not None:  #break
                    if (type(tn_by_tn_pre)==str) or (type(tn_by_tn_pre)==np.str_):
                        tn_by_tn.append(tn_by_tn_pre)
                    elif (type(tn_by_tn_pre)==list):
                        tn_by_tn.extend(tn_by_tn_pre)
                    elif (type(tn_by_tn_pre)==np.ndarray):
                        tn_by_tn.extend(list(tn_by_tn_pre))
                    # if i_tn ==0:
                    #     tn_by_tn = [tn_by_tn_pre]
                if mnn_by_tn_pre is not None:
                    # mnn_by_tn.append(mnn_by_tn)
                    if (type(mnn_by_tn_pre)==str) or (type(mnn_by_tn_pre)==np.str_):
                        tn_by_tn.append(tn_by_tn_pre)
                    elif (type(mnn_by_tn_pre)==list):
                        tn_by_tn.extend(mnn_by_tn_pre)
                    elif (type(mnn_by_tn_pre)==np.ndarray):
                        mnn_by_tn.extend(list(mnn_by_tn_pre))
        if tn_by_tn is not None and not((type(tn_by_tn)==str) or (type(tn_by_tn)==np.str_)):
            if type(tn_by_tn)==np.ndarray: tn_by_tn = list(tn_by_tn)
            try:
                tn_by_tn = list(set(tn_by_tn))
            except Exception as err:
                print(err)
                print(type(tn_by_tn), tn_by_tn)

            if len(tn_by_tn) == 0: tn_by_tn = None
            elif len(tn_by_tn) == 1: tn_by_tn = tn_by_tn[0]
        if mnn_by_tn is not None and not((type(mnn_by_tn)==str) or (type(mnn_by_tn)==np.str_)):
            if type(mnn_by_tn)==np.ndarray: tn_by_tn = list(mnn_by_tn)
            try: 
                mnn_by_tn = list(set(mnn_by_tn))
            except Exception as err:
                print(err)
                print(type(mnn_by_tn), mnn_by_tn)
            if len(mnn_by_tn) == 0: mnn_by_tn = None
            elif len(mnn_by_tn) == 1: mnn_by_tn = mnn_by_tn[0]

    num_records, tn_true, mnn_true, mnn_lst, code_smnn_lst = 0, [], [], None, []
    last_num_records, last_mnn_lst, last_code_smnn_lst = 0, None, None
    if not(pharm_form_type is None or pharm_form_type=='#Н/Д'):
        
        # if flags.get('correct_tn'): #==True,
        if 'tn_correct' in correct_cols and correct_values.get('tn_correct') is not None:
        # if 'tn_correct' in correct_cols:
            tn = correct_values.get('tn_correct')
            
            if debug: print("parse_mis_position: tn --->", tn)
            # if tn is not None: 
            if tn is not None and not (((type(tn)==float) or (type(tn)==np.float64)) and math.isnan(tn)):
                # после восставноления из Excel проверка доп условий
                mnn_lst, code_smnn_lst_00, num_records = \
                select_klp_mnn_by_tn__pharm_form_type(tn.capitalize(), pharm_form_type, strict_select = False, debug=debug )
                if debug: print("parse_mis_position: tn, mnn_lst, code_smnn_lst_00, num_records --->", 
                    tn, mnn_lst, code_smnn_lst_00, num_records)

                if num_records > 0: 
                    tn_true.append(tn)
                    tn_true = list(set(tn_true))
                    if mnn_lst is not None: 
                        if (type(mnn_lst)==list):
                            mnn_true.extend (mnn_lst) #list(set())
                            # if debug: print("parse_mis_position: type(mnn_lst), mnn_true")
                        # mnn_true = list(set(mnn_true))
                        # print(i_tn, 'mnn_true ->', mnn_true)
                        elif (type(mnn_lst)==np.ndarray):
                            mnn_true.extend (list(mnn_lst))
                            # if debug: print("parse_mis_position: type(mnn_lst), mnn_true")
                        else:
                            mnn_true.append (mnn_lst)
                            # if debug: print("parse_mis_position: type(mnn_lst), mnn_true")
                    if code_smnn_lst_00 is not None: 
                        if (type(code_smnn_lst_00)==list):
                            code_smnn_lst.extend (code_smnn_lst_00)
                        elif (type(code_smnn_lst_00)==np.ndarray):
                            code_smnn_lst.extend (list(code_smnn_lst_00))
                            # print("type(code_smnn_lst_00), code_smnn_lst", type(code_smnn_lst_00), code_smnn_lst)
                        else: # str or np.str_
                            code_smnn_lst.append(code_smnn_lst_00)
                            # print("type(code_smnn_lst_00), code_smnn_lst", type(code_smnn_lst_00), code_smnn_lst)
                        code_smnn_lst = list(set(code_smnn_lst))

            # if len(tn_true)==0: tn_true = None
            # elif len(tn_true)==1: tn_true = tn_true[0]

            if len(mnn_true)==0: mnn_true = None
            elif len(mnn_true)==1: mnn_true = mnn_true[0]
            else:
                # if type(mnn_true)==list:
                mnn_true = list(set(mnn_true))
                if len(mnn_true)==1: mnn_true = mnn_true[0]
            if len(code_smnn_lst)==0: code_smnn_lst = None
        else:
            #for i_tn, tn in enumerate([tn_ru_orig, tn_ru_ext, tn_ru]):
            for i_tn, tn in enumerate([tn_ru_orig, tn_ru_ext_clean, tn_ru_clean]):
                if debug: print("parse_mis_position: tn --->", i_tn, tn)
                if tn is not None:
                    mnn_lst, code_smnn_lst_00, num_records = \
                    select_klp_mnn_by_tn__pharm_form_type(tn.capitalize(), pharm_form_type, strict_select = False, debug=debug )
                    if debug: print("parse_mis_position: tn, mnn_lst, code_smnn_lst_00, num_records --->", 
                        i_tn, tn, mnn_lst, code_smnn_lst_00, num_records)

                    if num_records > 0: 
                        tn_true.append(tn)
                        tn_true = list(set(tn_true))
                        if mnn_lst is not None: 
                            if (type(mnn_lst)==list):
                                mnn_true.extend (mnn_lst) #list(set())
                                # if debug: print("parse_mis_position: type(mnn_lst), mnn_true")
                            # mnn_true = list(set(mnn_true))
                            # print(i_tn, 'mnn_true ->', mnn_true)
                            elif (type(mnn_lst)==np.ndarray):
                                mnn_true.extend (list(mnn_lst))
                                # if debug: print("parse_mis_position: type(mnn_lst), mnn_true")
                            else:
                                mnn_true.append (mnn_lst)
                                # if debug: print("parse_mis_position: type(mnn_lst), mnn_true")
                        if code_smnn_lst_00 is not None: 
                            if (type(code_smnn_lst_00)==list):
                                code_smnn_lst.extend (code_smnn_lst_00)
                            elif (type(code_smnn_lst_00)==np.ndarray):
                                code_smnn_lst.extend (list(code_smnn_lst_00))
                                # print("type(code_smnn_lst_00), code_smnn_lst", type(code_smnn_lst_00), code_smnn_lst)
                            else: # str or np.str_
                                code_smnn_lst.append(code_smnn_lst_00)
                                # print("type(code_smnn_lst_00), code_smnn_lst", type(code_smnn_lst_00), code_smnn_lst)
                            code_smnn_lst = list(set(code_smnn_lst))

            if len(tn_true)==0: tn_true = None
            elif len(tn_true)==1: tn_true = tn_true[0]

            if len(mnn_true)==0: mnn_true = None
            elif len(mnn_true)==1: mnn_true = mnn_true[0]
            else:
                # if type(mnn_true)==list:
                mnn_true = list(set(mnn_true))
                if len(mnn_true)==1: mnn_true = mnn_true[0]
            if len(code_smnn_lst)==0: code_smnn_lst = None
            # elif len(code_smnn_lst)==1: code_smnn_lst = code_smnn_lst[0]
            # df_sel_63000_be[df_sel_63000_be['mnn_true'].notnull() & (df_sel_63000_be['mnn_true'].str.len()==0)]=None
            # df_sel_63000_be[df_sel_63000_be['tn_true'].notnull() & (df_sel_63000_be['tn_true'].str.len()==0)]=None
    
    if tn_true is not None and not (type(tn_true)==str or type(tn_true)==np.str_)\
        and (type(tn_true)==list or type(tn_true)==np.ndarray) and len(tn_true)==0:
        tn_true = None
    if mnn_true is not None and not (type(mnn_true)==str or type(mnn_true)==np.str_)\
        and (type(mnn_true)==list or type(mnn_true)==np.ndarray) and len(mnn_true)==0:
        mnn_true = None  
    # if debug: print(f"parse_mis_position: last_mnn_lst: {last_mnn_lst}, last_code_smnn_lst: {last_code_smnn_lst}, last_num_records: {last_num_records}")        
    
    tn_selected = tn_true
    tn_true = choice_tn(tn_selected)
    
    ath_name, ath_code, is_znvlp, is_narcotic, form_standard  = None, None, None, None, None
    # dosage, 
    dosage_standard_value, dosage_standard_unit, dosage_standard_value_str = None, None, None
    dosage_standard_value_str_refrmt = None
    # dosage_parsing_value,	dosage_parsing_unit, dosage_parsing_value_str = None, None, None
    lp_pack_1_num, lp_pack_1_name, lp_pack_2_num, lp_pack_2_name, lp_unit_okei_name, lp_unit_name, lp_consumer_total, lp_consumer_total_calc,\
                        is_dosed, mass_volume_num, mass_volume_name =\
        None, None, None, None, None, None, None, None, None, None, None
    c_doze = None
    c_vol, c_vol_unit, name_ei_lp = None, None, None
    c_pack, c_mnn, c_form = None, None, None
    vol_calc, vol_unit_calc = None, None
    vol_klp, vol_unit_klp = None, None
    #if mnn_true is not None:
    #if num_records > 0:
    if debug: print(f"parse_mis_position: code_smnn_lst: {code_smnn_lst}")
    if code_smnn_lst is not None and len(code_smnn_lst)>0:
    #if mnn_lst is not None and len(mnn_lst)>0:
        #print("mnn_true is not None:")
        cols_return_lst = ['ath_name','ath_code', 'is_znvlp', 'is_narcotic', 'form_standard', 'dosage_grls_value'] # 'dosage_standard_value'
        cols_check_duplicates = ['ath_name','ath_code', 'is_znvlp', 'is_narcotic', 'form_standard']
        # индиффмрентно cols_check_duplicates попадаются словари и псики по к-ым drop_duplocatse не работают
        try:
            cols_srch  = {
                #'code': { 'ptn': [r"^(?:" , r")$"], 's_srch': "|".join(['(?:'+ re.escape(c) +')' for c in code_smnn_lst]),
                #'flags': re.I, 'regex': True},
                #'code': { 'ptn': ['' , ''], 's_srch': "|".join(['(?:'+ re.escape(c) +')' for c in code_smnn_lst]),
                # 'code': { 'ptn': ['' , ''], 's_srch': "|".join(['(?:'+ c +')' for c in code_smnn_lst]),
                'code_smnn': { 'ptn': ['' , ''], 's_srch': "|".join(['(?:'+ c +')' for c in code_smnn_lst]),
                        'flags': re.I, 'regex': True}, #True
                #  'mnn_standard': { 'ptn': [r"^(?:" , r")$"], 's_srch': "|".join(['(?:'+ re.escape(c) +')' for c in mnn_lst]),
                                
                #'form_standard': { 'ptn': [r"^(?:" , r").*$"], 's_srch': form_standard, 'flags': re.I},
            }
            # if debug: print("parse_mis_position: cols_srch:");pprint(cols_srch)

            return_values, num_records = \
                select_cols_values_from_smnn( cols_srch, cols_return_lst, cols_check_duplicates, check_col_names=False, debug=debug)
            if debug: print(f"parse_mis_position: num_records: {num_records}, return_values: {return_values}")
            if num_records > 0:  
                ath_name, ath_code, is_znvlp, is_narcotic, form_standard, dosage_standard_value_str = return_values
                if type(is_znvlp) ==  list and True in is_znvlp: is_znvlp = True
            else: ath_name, ath_code, is_znvlp, is_narcotic, form_standard, dosage_standard_value_str  = None, None, None, None, None
                # if num_records > 1:  form_standard, is_znvlp = list(return_values[0,:]), list(return_values[1,:])
                # elif num_records == 1: form_standard, is_znvlp = return_values
                # form_standard, is_znvlp = pd.Series({"form_standard":form_standard, "is_znvlp": is_znvlp})
        except Exception as err:
            print("parse_mis_position: Error create cols_srch", err, code_smnn_lst)
            # Error create cols_srch name 'select_cols_values_from_smnn' is not defined
            
        if dosage_standard_value_str is not None:
            dosage_standard_value, dosage_standard_unit = extract_dosage_standard(dosage_standard_value_str, debug=debug)
            # dosage_parsing_value,	dosage_parsing_unit = \
            #       calc_parsing_doze(doze_proc, doze, doze_unit, pseudo_vol, pseudo_vol_unit, vol_unit, debug=debug)

            # c_doze, dosage_parsing_value_str = compare_standard_parsing_doze(dosage_standard_value_str, dosage_parsing_value, dosage_parsing_unit, debug=debug)
            if 'dosage_parsing_value_str_correct' in correct_cols and correct_values.get('dosage_parsing_value_str_correct') is not None:
                dosage_parsing_value_str_work = correct_values.get('dosage_parsing_value_str_correct')
            else:
                dosage_parsing_value_str_work = dosage_parsing_value_str
            
            # c_doze, i_doze = compare_standard_parsing_doze_02(dosage_standard_value_str, dosage_parsing_value_str, debug=debug)
            c_doze, i_doze = compare_standard_parsing_doze_02(dosage_standard_value_str, dosage_parsing_value_str_work, debug=debug)
            
            if not c_doze: # пробуем привести к правильной базе еи
                dosage_standard_value_str_refrmt = reformat_dosage_standard_value_str(dosage_standard_value_str, debug=debug)
                c_doze_unit, i_doze_02 = compare_standard_parsing_doze_02(dosage_standard_value_str_refrmt, dosage_parsing_value_str_work, debug=debug)
            
            if c_doze:
                # lp_pack_1_num, lp_pack_2_num, lp_unit_okei, lp_unit, lp_consumer_total, lp_consumer_total_calc = \
                #     select_klp_packs_norm(tn_true,  form_standard, dosage_parsing_value_str, debug=debug)
                if i_doze is None: 
                    # такого здесь быть не может: если c_doze is None то и i_doze is None
                    dosage_str = ''
                elif i_doze == -1: # dosage_standard_value_str - строка не список строк
                    dosage_str = dosage_standard_value_str
                elif i_doze > -1: # индекс в спсике dosage_standard_value_str
                    dosage_str = dosage_standard_value_str[i_doze]
                else: 
                    dosage_str = '' # страхуемся закрываем ветки
                lp_pack_1_num, lp_pack_1_name, lp_pack_2_num, lp_pack_2_name, lp_unit_okei_name, lp_unit_name, lp_consumer_total, lp_consumer_total_calc,\
                        is_dosed, mass_volume_num, mass_volume_name = \
                    select_klp_packs_norm_02(tn_true,  form_standard, dosage_str, debug=debug)    
                # select_klp_packs_norm_02(tn_true,  form_standard, dosage_standard_value_str, debug=debug)
                lp_pack_1_num = to_float(lp_pack_1_num)
                lp_pack_2_num = to_float(lp_pack_2_num)
                lp_consumer_total = to_float(lp_consumer_total)
                mass_volume_num = to_float(mass_volume_num)

                
                # c_vol, name_ei_lp = compare_vol_norm_parsing(doze_group, lp_pack_1_num, lp_pack_2_num, lp_unit_okei_name, lp_unit_name, 
                #               lp_consumer_total, lp_consumer_total_calc, consumer_total_parsing, vol, debug=debug)
                
                
                # vol_calc, vol_unit_calc = calc_volume(doze_group, lp_unit_name, pack_1_num, 
                # form_standard, consumer_total, consumer_total_kis, dosage_standard_unit, mass_volume_name, 
                # mass_volume_num,
                # debug=debug)
                # vol_calc, vol_unit_calc = calc_volume(doze_group, lp_unit_name, pack_1_num, 
                # vol_calc, vol_unit_calc = calc_volume_02(doze_group, lp_unit_name, lp_pack_1_num, pack_1_num, 
                vol_klp, vol_unit_klp = calc_volume_02(doze_group, lp_unit_name, lp_pack_1_num, pack_1_num, 
                    form_standard, lp_consumer_total, consumer_total_parsing, dosage_parsing_unit, mass_volume_name, 
                    mass_volume_num, debug=debug)
                # vol_calc, vol_unit_calc = calc_volume(doze_group, lp_unit_name, pack_1_num, 
                #     form_standard, lp_consumer_total, consumer_total_parsing, dosage_parsing_unit, mass_volume_name, 
                #     mass_volume_num, debug=debug)
                # vol_calc = to_float(vol_calc)
                vol_klp = to_float(vol_klp)
                
                # c_vol, name_ei_lp = compare_vol_norm_parsing(doze_group, lp_pack_1_num, lp_pack_2_num, lp_unit_okei_name, lp_unit_name, 
                #               lp_consumer_total, lp_consumer_total_calc, consumer_total_parsing, vol, debug=debug)
                
                vol_correct = None
                if 'vol_correct' in correct_cols:
                    vol_correct = correct_values.get('vol_correct')
                # else:
                #     dosage_parsing_value_str_work = dosage_parsing_value_str
                
                vol_calc, vol_unit_calc, c_vol, c_vol_unit = control_vol(doze_group, vol, vol_unit, vol_klp, vol_unit_klp, debug=debug)
                
                # dosage_standard_unit
    if consumer_total_parsing is not None: c_pack = 1
    else: c_pack = None

    if mnn_true is None: c_mnn = 0
    elif (type(mnn_true) == str) or (type(mnn_true) == np.str_): c_mnn = 1 # строка
    elif ((type(mnn_true) == list) or (type(mnn_true) == np.ndarray)) and (len(mnn_true)>1) : c_mnn = 2 # список
    else: c_mnn = None
    
    if form_standard is None: c_form = 0
    elif (type(form_standard) == str) or (type(form_standard) == np.str_): c_form = 1 # строка
    elif ((type(form_standard) == list) or (type(form_standard) == np.ndarray)) and (len(form_standard)>1) : c_form = 2 # список
    else: c_form = None

    # else: ath_name, ath_code, is_znvlp, is_narcotic, form_standard  = None, None, None, None, None
    if debug_print: 
        print_debug(  mis_position, tn_ru, tn_lat, tn_ru_ext, tn_lat_ext, tn_ru_orig, tn_ru_ext_clean, 
        tn_selected, tn_true,
        tn_by_tn, mnn_by_tn,
        tn_ru_clean, 
        pharm_form_type, pharm_form, 
        mnn_from_tn_ru_ext,  mnn_local_dict, mnn_true, 
        ath_name, ath_code, is_znvlp, is_narcotic, form_standard,
        doze_group, doze_proc, doze, doze_unit, pseudo_vol, pseudo_vol_unit, complex_doze_list, complex_doze_str, vol, vol_unit,
        pack_1_form_unify, pack_1_form,  pack_1_num, pack_2_form_unify, pack_2_form, pack_2_num, n_packs_str, consumer_total_parsing,
        dosage_standard_value_str, dosage_standard_value, dosage_standard_unit, 
        dosage_standard_value_str_refrmt,
        dosage_parsing_value_str, dosage_parsing_value, dosage_parsing_unit,
        c_doze,
        lp_pack_1_num, lp_pack_1_name, lp_pack_2_num, lp_pack_2_name, lp_unit_okei_name, lp_unit_name, lp_consumer_total, lp_consumer_total_calc,
        is_dosed, mass_volume_num, mass_volume_name,
        vol_klp, vol_unit_klp,
        vol_calc, vol_unit_calc,
        c_vol, c_vol_unit, name_ei_lp,
        c_pack, c_mnn, c_form
                   
                   )
    
    return  tn_ru, tn_lat, tn_ru_ext, tn_lat_ext, tn_ru_orig, tn_ru_ext_clean, tn_selected, tn_true,\
    tn_by_tn, mnn_by_tn,\
    tn_ru_clean, \
    pharm_form_type, pharm_form, \
    mnn_from_tn_ru_ext,  mnn_local_dict, mnn_true, \
    ath_name, ath_code, is_znvlp, is_narcotic, form_standard,\
    doze_group, doze_proc, doze, doze_unit, pseudo_vol, pseudo_vol_unit, complex_doze_list, complex_doze_str, vol, vol_unit,\
    pack_1_form_unify, pack_1_form,  pack_1_num, pack_2_form_unify, pack_2_form, pack_2_num, consumer_total_parsing,\
    dosage_standard_value_str, dosage_standard_value, dosage_standard_unit, \
    dosage_standard_value_str_refrmt, \
    dosage_parsing_value_str, dosage_parsing_value,	dosage_parsing_unit,\
    c_doze,\
    lp_pack_1_num, lp_pack_1_name, lp_pack_2_num, lp_pack_2_name, lp_unit_okei_name, lp_unit_name, lp_consumer_total, lp_consumer_total_calc,\
    is_dosed, mass_volume_num, mass_volume_name,\
    vol_klp, vol_unit_klp,\
    vol_calc, vol_unit_calc,\
    c_vol, c_vol_unit, name_ei_lp,\
    c_pack, c_mnn, c_form

# def init_parse_kis(klp_list_dict_df_in, smnn_list_df_in):
def init_parse_kis(klp_list_dict_df_in, smnn_list_df_in, path_supp_dicts):  
    global dict__tn_lat_ext__tn_ru_ext, dict__tn_lat_ext__tn_ru_orig, dict__tn_lat__tn_ru_orig
    global klp_srch_list_columns, klp_srch_list
    global smnn_list_df, klp_list_dict_df
    global code_klp_id, mnn_standard_id, code_smnn_id, trade_name_id, trade_name_capitalize_id, \
        form_standard_unify_id, lim_price_barcode_str_id, num_reg_id, lf_norm_name_id, dosage_norm_name_id

    klp_srch_list_columns = [ 'code_klp', 'mnn_standard', 'code_smnn', 'trade_name', 'trade_name','form_standard_unify', 
                         'lim_price_barcode_str', 'num_reg',
                          'lf_norm_name', 'dosage_norm_name']
    if klp_list_dict_df_in is None:
        print("klp_list_dict_df is None")
        sys.exit(2)
    else: klp_list_dict_df = klp_list_dict_df_in
    if smnn_list_df_in is None:
        print("smnn_list_df is None")
        sys.exit(2)        
    else: smnn_list_df  = smnn_list_df_in
    klp_srch_list = klp_list_dict_df[klp_srch_list_columns].values
    code_klp_id, mnn_standard_id, code_smnn_id, trade_name_id, trade_name_capitalize_id, \
    form_standard_unify_id, lim_price_barcode_str_id, num_reg_id, lf_norm_name_id, dosage_norm_name_id = 0,1,2,3,4,5,6,7,8,9
    # print(code_klp_id, mnn_standard_id, code_smnn_id, trade_name_id, trade_name_capitalize_id, 
    # form_standard_unify_id, lim_price_barcode_str_id, num_reg_id, lf_norm_name_id, dosage_norm_name_id)
    for r in klp_srch_list:
        r[trade_name_capitalize_id] = r[trade_name_id].capitalize()

    # print(len(klp_srch_list))    

    
    fn_dict = "dict_tn_lat_ext__tn_ru_ext.json"
    if not os.path.exists(os.path.join(path_supp_dicts, fn_dict)):
        logger.error(f"Не найден справочник '{fn_dict}' в лиректории '{path_supp_dicts}'")
        sys.exit(2)
    # !cp "/content/drive/MyDrive/Colab Notebooks/__work/_A_Pav_Helth/Parsing/data/new_dict/""$fn_dict" "$fn_dict"
    with open(os.path.join(path_supp_dicts, fn_dict), "r") as f:
        dict__tn_lat_ext__tn_ru_ext = json.load(f) 
    
    
    fn_dict = "dict__tn_lat_ext__tn_ru_orig.json"
    if not os.path.exists(os.path.join(path_supp_dicts, fn_dict)):
        logger.error(f"Не найден справочник '{fn_dict}' в лиректории '{path_supp_dicts}'")
        sys.exit(2)
    # !cp "/content/drive/MyDrive/Colab Notebooks/__work/_A_Pav_Helth/Parsing/data/new_dict/""$fn_dict"  "$fn_dict" 
    with open(os.path.join(path_supp_dicts, fn_dict), "r") as f:
        dict__tn_lat_ext__tn_ru_orig = json.load(f ) 
        

    
    fn_dict = "dict__tn_lat__tn_ru_orig.json"
    if not os.path.exists(os.path.join(path_supp_dicts, fn_dict)):
        logger.error(f"Не найден справочник '{fn_dict}' в лиректории '{path_supp_dicts}'")
        sys.exit(2)
    # !cp "/content/drive/MyDrive/Colab Notebooks/__work/_A_Pav_Helth/Parsing/data/new_dict/""$fn_dict"  "$fn_dict" 
    with open(os.path.join(path_supp_dicts, fn_dict), "r") as f:
        dict__tn_lat__tn_ru_orig = json.load(f )         

    # path_f_pharm_form_tn_lat_tn_ru = 'ФОРМЫ ВЫПУСКА+ПЕРВИЧ УПАК_ТОРГОВЫЕ_для парсинга.xlsx'
    # df_dict_01_tn_lat_tn_ru = pd.read_excel(os.path.join(path_supp_dicts, path_f_pharm_form_tn_lat_tn_ru), 
    #     sheet_name='Привязка_ТН_лат')        

    # df_pharm_form_parsing__pharm_form_norm = pd.read_excel(path_f_pharm_form_tn_lat_tn_ru, sheet_name='привязка ФВ', header=1)

def read_selection_25000(path_selections,  xls_file_name, sheet_name ='Total', b=0, e=np.inf):
    logger.info(f"Data selection '{xls_file_name}' read - start ...")
    selections_63000_df = pd.read_excel(os.path.join(path_selections, xls_file_name),  sheet_name = sheet_name, #'Total', 
            # skiprows = b, nrows = None if e==np.inf else e-b,
        names =['NAME', 'grouping', 'MNN', 'PTN', 'MEAS_NAME', 'NAME_сжп','NAME_сжп_левсим', 'Длстр', 'Группа', 'МНН_из_справочника'])
    df_sel_63000 = selections_63000_df[selections_63000_df['Группа']=='ЛС'].copy()[b: None if e==np.inf else e]
    df_sel_63000 = df_sel_63000[['NAME','Группа', 'grouping', 'MNN', 'MEAS_NAME', 'МНН_из_справочника']]
    # print(df_sel_63000.shape)
    # print(df_sel_63000.columns) 
    df_sel_63000.name = 'selections_25400'
    # display(df_sel_63000.head())
    logger.info(f"Data selection '{xls_file_name}' read - done!")
    logger.info("Shape: " + str(df_sel_63000.shape))
    mis_position_col_name = 'NAME'
    return df_sel_63000, mis_position_col_name
    
def read_selection(path_selections,  xls_file_name, col_name, sheet_name = None, b=0, e=np.inf):
    logger.info(f"Data selection '{xls_file_name}' read - start ...")
    if sheet_name is not None:
        selections_df = pd.read_excel(os.path.join(path_selections, xls_file_name),  sheet_name = sheet_name)
            # skiprows = b, nrows = None if e==np.inf else e-b,
        # names =['NAME', 'grouping', 'MNN', 'PTN', 'MEAS_NAME', 'NAME_сжп','NAME_сжп_левсим', 'Длстр', 'Группа', 'МНН_из_справочника'])
    else: 
        selections_df = pd.read_excel(os.path.join(path_selections, xls_file_name))
    selections_df = selections_df[b: None if e==np.inf else e]
    # df_sel_63000 = selections_df[selections_63000_df['Группа']=='ЛС'].copy()[b: None if e==np.inf else e]
    # df_sel_63000 = df_sel_63000[['NAME','Группа', 'grouping', 'MNN', 'MEAS_NAME', 'МНН_из_справочника']]
    # print(df_sel_63000.shape)
    # print(df_sel_63000.columns) 
    selections_df.name = 'selection'
    # display(df_sel_63000.head())
    logger.info(f"Data selection '{xls_file_name}' read - done!")
    logger.info("Shape: " + str(selections_df.shape))
    mis_position_col_name = col_name
    return selections_df, mis_position_col_name    

def apply_parse_kis(df_sel_63000, mis_position_col_name, debug=False, debug_print=False, b=0, e=None):
    # mis_position_col_name = 'NAME'
    new_cols = ['tn_ru', 'tn_lat', 'tn_ru_ext', 'tn_lat_ext', 'tn_ru_orig', 'tn_ru_ext_clean', 
                'tn_selected', 'tn_true',
                'tn_by_tn', 'mnn_by_tn',
                'tn_ru_clean', 
                'pharm_form_type', 'pharm_form',
                'mnn_from_tn_ru_ext', 'mnn_local_dict', 'mnn_true',  # 'mnn_tn_ru_orig', 'mnn_tn_ru_ext', 'mnn_tn_ru', 
                'ath_name', 'ath_code', 'is_znvlp', 'is_narcotic', 'form_standard',
                #'dosage', 'measurement_unit', 'pseudo_vol', 'vol',
                'doze_group', 'doze_proc', 'doze', 'doze_unit', 'pseudo_vol', 'pseudo_vol_unit', 
                'comlex_doze_list', 'comlex_doze_str',
                'vol', 'vol_unit',
                'pack_1_form_unify', 'pack_1_form', 'pack_1_num', 'pack_2_form_unify', 'pack_2_form', 'pack_2_num', 'consumer_total_parsing',
                'dosage_standard_value_str', 'dosage_standard_value', 'dosage_standard_unit', 
                'dosage_standard_value_str_refrmt',
                'dosage_parsing_value_str', 'dosage_parsing_value',	'dosage_parsing_unit',
                'dosage_correct_value', 'dosage_correct_unit',
                'c_doze',
                'lp_pack_1_num', 'lp_pack_1_name', 'lp_pack_2_num', 'lp_pack_2_name', 'lp_unit_okei_name', 'lp_unit_name', 'lp_consumer_total', 'lp_consumer_total_calc',
                'is_dosed', 'mass_volume_num', 'mass_volume_name',
                'vol_klp', 'vol_unit_klp',
                'vol_calc', 'vol_unit_calc',
                'c_vol', 'c_vol_unit', 'name_ei_lp',
                'c_pack', 'c_mnn', 'c_form',
                'расчет ЛС (по дозировке)',  'ЕИ ЛС (по дозировке)',
                'расчет ЛС (по объему)', 'ЕИ ЛС (по объему)', 
                'расчет ЛС (по дозировке/объему)', 'ЕИ ЛС (по дозировке/объему)',
                ]

    
    df_sel_63000_be = df_sel_63000[b:e].copy()
    offset = datetime.timezone(datetime.timedelta(hours=3))
    # debug, debug_print = False, False
    logger.info("Parsing selection - start ...")
    begin_time = datetime.datetime.now(offset)
    df_sel_63000_be[new_cols] = None

    df_sel_63000_be[new_cols] = df_sel_63000_be[mis_position_col_name].progress_apply( \
    lambda x: pd.Series(parse_mis_position_07(x, select_by_tn=True, parse_dozes=True, debug=debug, debug_print=debug_print), index=new_cols)) #, axis=1)) #,  result_type='expand')) 
    end_time = datetime.datetime.now(offset)

    print("done", datetime.datetime.now(offset).strftime("%Y_%m_%d %H:%M:%S"))
    logger.info("Parsing selection - done!")
    logger.info("shape: " + str(df_sel_63000_be.shape))

    calc_time = end_time - begin_time
    calc_time_lst = str(calc_time).split(':')
    calc_time_str = ':'.join([f"{int(float(c)):02d}" for c in calc_time_lst])
    df_sel_63000_be.attrs['name'] =  'selection_25400'
    df_sel_63000_be.attrs['esklp'] = '2022_09_23_active'
    df_sel_63000_be.attrs['datetime_stamp'] = end_time.strftime("%Y_%m_%d_%H%M")
    # df_sel_63000_be.attrs['datetime_stamp'] = '2022_10_26_1728'
    df_sel_63000_be.attrs['calc_time'] = calc_time_str
    return df_sel_63000_be

def apply_upd_parse_kis(df_sel_63000, mis_position_col_name, 
        correct_cols,
        debug=False, debug_print=False, b=0, e=None):
    # mis_position_col_name = 'NAME'
    new_cols = ['tn_ru', 'tn_lat', 'tn_ru_ext', 'tn_lat_ext', 'tn_ru_orig', 'tn_ru_ext_clean', 
                'tn_selected', 'tn_true',
                'tn_by_tn', 'mnn_by_tn',
                'tn_ru_clean', 
                'pharm_form_type', 'pharm_form',
                'mnn_from_tn_ru_ext', 'mnn_local_dict', 'mnn_true',  # 'mnn_tn_ru_orig', 'mnn_tn_ru_ext', 'mnn_tn_ru', 
                'ath_name', 'ath_code', 'is_znvlp', 'is_narcotic', 'form_standard',
                #'dosage', 'measurement_unit', 'pseudo_vol', 'vol',
                'doze_group', 'doze_proc', 'doze', 'doze_unit', 'pseudo_vol', 'pseudo_vol_unit', 
                'comlex_doze_list', 'comlex_doze_str',
                'vol', 'vol_unit',
                'pack_1_form_unify', 'pack_1_form', 'pack_1_num', 'pack_2_form_unify', 'pack_2_form', 'pack_2_num', 'consumer_total_parsing',
                'dosage_standard_value_str', 'dosage_standard_value', 'dosage_standard_unit', 
                'dosage_standard_value_str_refrmt',
                'dosage_parsing_value_str', 'dosage_parsing_value',	'dosage_parsing_unit',
                'dosage_correct_value', 'dosage_correct_unit',
                'c_doze',
                'lp_pack_1_num', 'lp_pack_1_name', 'lp_pack_2_num', 'lp_pack_2_name', 'lp_unit_okei_name', 'lp_unit_name', 'lp_consumer_total', 'lp_consumer_total_calc',
                'is_dosed', 'mass_volume_num', 'mass_volume_name',
                'vol_klp', 'vol_unit_klp',
                'vol_calc', 'vol_unit_calc',
                'c_vol', 'c_vol_unit', 'name_ei_lp',
                'c_pack', 'c_mnn', 'c_form',
                'расчет ЛС (по дозировке)',  'ЕИ ЛС (по дозировке)',
                'расчет ЛС (по объему)', 'ЕИ ЛС (по объему)', 
                'расчет ЛС (по дозировке/объему)', 'ЕИ ЛС (по дозировке/объему)',
                ]
       
    for ic, col in enumerate(correct_cols):
        if ic == 0: mask = df_sel_63000[col].notnull()
        else: mask = mask | df_sel_63000[col].notnull()

    # df_sel_63000 = df_sel_63000[mask]
    df_sel_63000_be = df_sel_63000[b:e].copy()
    
    offset = datetime.timezone(datetime.timedelta(hours=3))
    # debug, debug_print = False, False
    logger.info("Update parsing selection - start ...")
    begin_time = datetime.datetime.now(offset)
    # df_sel_63000_be[new_cols] = None

    df_sel_63000_be.loc[mask, new_cols] = df_sel_63000_be.loc[mask, [mis_position_col_name] + correct_cols].progress_apply( 
    # df_sel_63000_be.loc[:, new_cols] = df_sel_63000_be.loc[:, [mis_position_col_name] + correct_cols].progress_apply( 
    lambda x: pd.Series(parse_mis_position_07_update(x[0], correct_cols, \
        correct_values= dict(zip(correct_cols, x[correct_cols])),\
        select_by_tn=True, parse_dozes=True, debug=debug, debug_print=debug_print), index=new_cols), axis=1) #,  result_type='expand')) 
    
    end_time = datetime.datetime.now(offset)

    print("done", datetime.datetime.now(offset).strftime("%Y_%m_%d %H:%M:%S"))
    logger.info("Update parsing selection - done!")
    logger.info("shape: " + str(df_sel_63000_be.shape))

    calc_time = end_time - begin_time
    calc_time_lst = str(calc_time).split(':')
    calc_time_str = ':'.join([f"{int(float(c)):02d}" for c in calc_time_lst])
    df_sel_63000_be.attrs['name'] =  'selection_25400'
    df_sel_63000_be.attrs['esklp'] = '2022_09_23_active'
    df_sel_63000_be.attrs['datetime_stamp'] = end_time.strftime("%Y_%m_%d_%H%M")
    # df_sel_63000_be.attrs['datetime_stamp'] = '2022_10_26_1728'
    df_sel_63000_be.attrs['calc_time'] = calc_time_str
    return df_sel_63000_be  
