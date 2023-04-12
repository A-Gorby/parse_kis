import pandas as pd
import numpy as np
import os, sys, glob
import logging
import zipfile
import datetime
import humanize
import re
# import g
from utils_io_kis import logger
if len(logger.handlers) > 1:
    for handler in logger.handlers:
        logger.removeHandler(handler)
# global smnn_list_df, klp_list_dict_df, zvnlp_df


def unzip_file(path_source, fn_zip, work_path):
    logger.info('Unzip ' + fn_zip + ' start...')

    try:
        with zipfile.ZipFile(path_source + fn_zip, 'r') as zip_ref:
            fn_list = zip_ref.namelist()
            zip_ref.extractall(work_path)
        logger.info('Unzip ' + fn_zip + ' done!')
        return fn_list[0]
    except Exception as err:
        logger.error('Unzip error: ' + str(err))
        sys.exit(2)

def find_last_fn_pickle(prefix, path_files):
    fn_pickle = None
    if prefix is None: prefix =''
    fn_list = sorted(glob.glob(os.path.join(path_files, prefix) + '*.pickle'))
    # fn_list = sorted(glob.glob(path_files + prefix + '*.pickle'))
    # print(fn_list)
    if len(fn_list)>0:  fn_pickle = fn_list[-1]
    return fn_pickle

def find_last_file (path_files, prefix, suffix = '.pickle'):
    fn = None
    if prefix is None: prefix =''
    fn_list = sorted(glob.glob(path_files + prefix + '*' + suffix))
    if len(fn_list)>0:  fn = fn_list[-1]
    return fn

def restore_df_from_pickle(prefix, path_files, fn_pickle):
    # global logger
    # print(f"restore_df_from_pickleЖ prefix: '{prefix}', path_files: '{path_files}', fn_pickle: '{fn_pickle}'")
    if fn_pickle == 'last':
        # fn_pickle = 'smnn_list_v2022_09_23.pickle'
        #smnn_list_df_esklp
        fn_pickle_с = find_last_fn_pickle(prefix, path_files = path_files)
    elif fn_pickle is not None:
        fn_pickle_с = fn_pickle
    else:
        fn_pickle_с = find_last_fn_pickle(prefix = prefix, path_files = path_files)
    # print(f"restore_df_from_pickle: fn_pickle: {fn_pickle}")
    if fn_pickle is None:
        logger.error('Restore pickle from ' + path_files + ' failed!')
        sys.exit(2)
    if os.path.exists(os.path.join(path_files, fn_pickle_с)):
        df = pd.read_pickle(os.path.join(path_files, fn_pickle_с))
        # logger.info('Restore ' + re.sub(path_files, '', fn_pickle_с) + ' done!')
        logger.info('Restore ' + fn_pickle_с.split('\\')[-1] + ' done!')
        logger.info('Shape: ' + str(df.shape))
    else:
        # logger.error('Restore ' + re.sub(path_files, '', fn_pickle_с) + ' from ' + path_files + ' failed!')
        logger.error('Restore ' + fn_pickle_с.split('\\')[-1] + ' from ' + path_files + ' failed!')
    return df

def get_humanize_filesize(path, fn):
    human_file_size = None
    try:
        fn_full = os.path.join(path, fn)
    except Exception as err:
        print(err)
        return human_file_size
    if os.path.exists(fn_full):
        file_size = os.path.os.path.getsize(fn_full)
        human_file_size = humanize.naturalsize(file_size)
    return human_file_size

def exract_esklp_date(fn):
    if fn is None: return None
    m = re.search(r"(?<=esklp_)\d+", fn)
    if m is not None:
        esklp_date = m.group()
        # print(f"esklp_date: {esklp_date}")
    else: esklp_date = None
    return esklp_date

def save_df_to_pickle(df, path_to_save, fn_main):
    offset = datetime.timezone(datetime.timedelta(hours=3))
    dt = datetime.datetime.now(offset)
    str_date = dt.strftime("%Y_%m_%d_%H%M")
    fn = fn_main + '_' + str_date + '.pickle'
    df.to_pickle(path_to_save + fn)
    logger.info(fn + ' saved to ' + path_to_save)
    hfs = get_humanize_filesize(path_to_save, fn)
    logger.info("Size: " + str(hfs))
    return fn

def save_df_to_excel(df, path_to_save, fn_main, columns = None, b=0, e=None):
    offset = datetime.timezone(datetime.timedelta(hours=3))
    dt = datetime.datetime.now(offset)
    str_date = dt.strftime("%Y_%m_%d_%H%M")
    fn = fn_main + '_' + str_date + '.xlsx'
    logger.info(fn + ' save - start ...')
    if e is None or (e <0):
        e = df.shape[0]
    if columns is None:
        df[b:e].to_excel(os.path.join(path_to_save, fn), index = False)
    else:
        df[b:e].to_excel(os.path.join(path_to_save, fn), index = False, columns = columns)
    logger.info(fn + ' saved to ' + path_to_save)
    hfs = get_humanize_filesize(path_to_save, fn)
    logger.info("Size: " + str(hfs))
    return fn
