# import logging
smnn_list_df, klp_list_dict_df, selection_df = None, None, None
esklp_date_format = None
np_lim_price_barcode_str = None
np_lim_price_reg_date_str =  None
klp_srch_list = None
klp_srch_list_columns = None
code_klp_id, mnn_standard_id, code_smnn_id, trade_name_id, trade_name_capitalize_id, \
form_standard_unify_id, lim_price_barcode_str_id, num_reg_id, lf_norm_name_id, dosage_norm_name_id = \
    None, None, None, None, None, None, None, None, None, None
dict__tn_lat__tn_ru_orig = None
dict__tn_lat_ext__tn_ru_orig = None

# # logging.basicConfig(format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')
# logger = logging.getLogger('Parse KIS')
# logger.setLevel(logging.INFO)

# # create console handler and set level to debug
# ch = logging.StreamHandler()
# ch.setLevel(logging.INFO)

# # create formatter
# strfmt = '[%(asctime)s] [%(name)s] [%(levelname)s] > %(message)s'
# strfmt = '%(asctime)s - %(levelname)s > %(message)s'
# # строка формата времени
# datefmt = '%Y-%m-%d %H:%M:%S'
# datefmt = '%H:%M:%S'
# # создаем форматтер
# formatter = logging.Formatter(fmt=strfmt, datefmt=datefmt)

# # add formatter to ch
# ch.setFormatter(formatter)

# # add ch to logger
# logger.addHandler(ch)
