
# v24/11/2022
# v23/11/2022
# v22/11/2022
import itertools
import re

def unit_slash_combination(units):
    # units = [('AntiXa MЕ','MЕ', 'ЛЕ'),('мл','ml')]
    # print(units)
    list_units = list(itertools.product(*units))
    list_units_slash = [i[0]+'/'+ i[1]  for i in list_units]
    # print(list_units_slash)
    return list_units_slash

def make_doze_ptn_str(lst):
    ptn_digits = r'(?P<digits>((\d+,\d+)|(\d+\.\d+)|(\d+))\s*((тыс)(\.|,)*)*\s*)'
    ptn_digits = r'(?P<digits>((\d+,\d+)|(\d+\.\d+)|(\d+)))'
    p_dozes = [re.sub(r"(?<=/)\s*(\w+)", '', p).replace('/','') for p in lst]
    p_pseudos = [re.sub(r".+/", '', p) if '/' in p else None for p in lst ]
    # подумать через rfind('/') и зуздфсу для варианта анти/ХА ME/0,6ml 
    # fr"(?P<doze_digits_{ip:03d}>((\d+,\d+)|(\d+\.\d+)|([\d\s]+\d+)|(\d+)))\s*"  +\
    # doze_ptn_str = \
    #     "|".join(([r'(?:' + # ( [::-1]\
    #   fr"(?P<doze_digits_{ip:03d}>((\d+,\d+)|(\d+\.\d+)|([\d\s]+\d+)|(\d+)))\s*"  +\
    #   (fr"(?P<doze_unit_{ip:03d}>{p_doze})\.*,*" if p_pseudos[ip] is not None else fr"(?P<doze_unit_{ip:03d}>{p_doze})(\.|,|\s|\+|$)")  +\
    #   (fr"(?:(/|\||\\)(?P<digits_pseudo_{ip:03d}>\s*((\d+,\d+)|(\d+\.\d+)|(\d+)))*\s*(?P<unit_pseudo_{ip:03d}>({p_pseudos[ip]})))(\.|,|\s|$)*" \
    #       if p_pseudos[ip] is not None else '') \
    #     + r")"
    # update 26/11/2022 добавление пробела перед слэшем
    doze_ptn_str = \
        "|".join(([r'(?:' + # ( [::-1]\
      fr"(?P<doze_digits_{ip:03d}>((\d+,\d+)|(\d+\.\d+)|([\d\s]+\d+)|(\d+)))\s*"  +\
      (fr"(?P<doze_unit_{ip:03d}>{p_doze})\.*,*\s*" if p_pseudos[ip] is not None else fr"(?P<doze_unit_{ip:03d}>{p_doze})(\.|,|\s|\+|$)")  +\
      (fr"(?:(/|\||\\)(?P<digits_pseudo_{ip:03d}>\s*((\d+,\d+)|(\d+\.\d+)|(\d+)))*\s*(?P<unit_pseudo_{ip:03d}>({p_pseudos[ip]})))(\.|,|\s|$)*" \
          if p_pseudos[ip] is not None else '') \
        + r")"
      for ip, p_doze in enumerate(p_dozes)]) [::1])   
      # 14/10/2022  (fr"(?P<doze_unit_{ip:03d}>{p_doze})\.*,*/*(\s*|$)" if p_pseudos[ip] is not None else fr"(?P<doze_unit_{ip:03d}>{p_doze})(\.|,|\s|\+|/|$)")  +\  
      # (fr"(?P<doze_unit_{ip:03d}>{p_doze})\.*,*(\s*|$)" if p_pseudos[ip] is not None else fr"(?P<doze_unit_{ip:03d}>{p_doze})(\.|,|\s|\+|$)")  +\
    return doze_ptn_str

def make_vol_ptn_str(lst):
    #ptn_digits = r'(?P<digits>(\d+,\d+)|(\d+\.\d+)|(\d+))'
    ptn_digits = r'(?P<digits>(\d+,\d+)|(\d+\.\d+)|([\d\s]+\d+)|(\d+))'
    vol_ptn_str = None
    try:
        vol_ptn_str = r"(?:" + ptn_digits + r")\s*" +\
                  r"(?P<unit>" +  "|".join(['(?:' + p + r")" for p in lst]) + r")\.*,*(\s*|$)" 
    except Exception as err:
        print(err, "lst is not list of str")
    return vol_ptn_str

def make_complex_doze_ptn_str(lst):
    ptn_digits = r'(?P<digits>((\d+,\d+)|(\d+\.\d+)|(\d+))\s*((тыс)(\.|,)*)*\s*)'
    ptn_digits = r'(?P<digits>((\d+,\d+)|(\d+\.\d+)|(\d+)))'
    ptn_digits_0 = r"((\d+,\d+)|(\d+\.\d+)|(\d+\s*\d+)|(\d+))"
    # r"(?:(\+\s*\d+\s*)+\s*мг\s*)+
    # ptn_first_doze_unit = r"(?P<first_doze_unit>" + '|'.join([r"(?:" + ptn + r"\.*,*(\s*|\b|$))" for ptn in lst] ) + r")*"
    ptn_first_doze_unit = r"(?P<first_doze_unit>" + '|'.join([r"(?:" + ptn + r"\.*,*(\s*|$))" for ptn in lst] ) + r")*(\s*|$)"
    ptn_plus_doze_unit = r"(?P<plus_doze_unit>" + '|'.join([r"(?:" + ptn + r"\.*,*(\s*|$))" for ptn in lst] ) + r")*"
    complex_doze_ptn_str = r"(?:" + \
        r"(?P<first_doze>" + ptn_digits_0 + r"\s*" + ptn_first_doze_unit + r"\s*)" +\
        r"(?P<plus_dozes>\s*(\+|/)*\s*" + ptn_digits_0 + r"*\s*" + ptn_plus_doze_unit + r"\s*)*" +\
        r")"
        #r"(?P<doze_digits>\+\s*((\d+,\d+)|(\d+\.\d+)|([\d\s]+\d+)|(\d+))\s*)+"  +\
    return complex_doze_ptn_str    

def make_complex_doze_ptn_str_02(lst, max_bloks_plus=5):
    ptn_digits = r'(?P<digits>((\d+,\d+)|(\d+\.\d+)|(\d+)))' #   спробелами межуд цифрами
    ptn_digits = r"((\d+,\d+)|(\d+\.\d+)|(\d+))"
    ptn_doze_group_only_units = r"(?:" + '|'.join([r"(?:" + p[:p.rfind('/')] + r"\s*/\s*" + ptn_digits + r"*\s*" + p[p.rfind('/')+1:] + r")" 
                                                   if '/' in p else r"(?:" + p + r")"  
                                                   for p in lst ]) + r")"
    
    complex_doze_ptn_str = r"(?:" + ptn_digits + r"\s*(?:" +  ptn_doze_group_only_units + r")*)"  \
        + max_bloks_plus*(r"(\s*\+\s*" + ptn_digits + r"*\s*(?:" +  ptn_doze_group_only_units  + r")*)*") 
    return complex_doze_ptn_str   

# def make_complex_doze_ptn_str_02(lst, max_bloks_plus=5):
#     ptn_digits = r'(?P<digits>((\d+,\d+)|(\d+\.\d+)|(\d+)))' #   спробелами межуд цифрами
#     ptn_digits = r"((\d+,\d+)|(\d+\.\d+)|(\d+))"
#     ptn_doze_group_only_units = r"(?:" + '|'.join([r"(?:" + p[:p.rfind('/')] + r"\s*/\s*" + ptn_digits + r"\s*" + p[p.rfind('/')+1:] + r")" 
#                                                    if '/' in p else r"(?:" + p + r")"  
#                                                    for p in lst ]) + r")"
    
#     complex_doze_ptn_str = r"(?:" + ptn_digits + r"\s*(?:" +  ptn_doze_group_only_units + r")*)"  \
#         + max_bloks_plus*(r"(\s*\+\s*" + ptn_digits + r"\s*(?:" +  ptn_doze_group_only_units  + r")*)*") 
#     return complex_doze_ptn_str  

# handler_numder, is_dosed, is_pseudo_vol, is_vol, is_proc_dozed
# doze_vol_handler_types = [ [0, True, False, False, False],
#                           [1, True, True, True, True],
#                           [2, True, False, True, False],
#                           [3, False, False, True, False],
#                           [4, False, False, True, False],
#                           [5, True, True, True, True],
#                           [6, True, False, False, False],
#                           [7, True, True, True, True],
#                           [8, True, True, True, False], 
#                           [9, True, True, False, False],
#                           [10, True, True, False, False], #соеденить с группой №9
#                           [11, False, False, True, False],
#                           [-1, True, True, True, False],
# ]
# is_proc_dozed = is_dosed
doze_vol_handler_types = [ [0, True, False, False, True],
                          [1, True, True, True, True],
                          [2, True, False, True, True],
                          [3, False, False, True, False],
                          [4, False, False, True, False],
                          [5, True, True, True, True],
                          # [6, True, False, False, True],
                          [6, True, True, True, True], # 22.11.2022 
                          [7, True, True, True, True],
                          [8, True, True, True, True], 
                          [9, True, True, False, True],
                          [10, True, True, False, True], #соеденить с группой №9
                          [11, False, False, True, False],
                          [-1, True, True, True, True],
]
#doze_units_groups, vol_units_groups, doze_vol_handler_types
doze_vol_pharm_form_handlers = {
  'Таблетки':         doze_vol_handler_types[0],
  'Капсулы':          doze_vol_handler_types[0],
  'Драже':            doze_vol_handler_types[0],
  'Суппозитории':     doze_vol_handler_types[0],
  'Пастилки':         doze_vol_handler_types[0],
  'Имплантат':        doze_vol_handler_types[0],
  'Крем':             doze_vol_handler_types[1],
  'Мазь':             doze_vol_handler_types[1],
  'Гель':             doze_vol_handler_types[1],
  'Линимент':         doze_vol_handler_types[1],
  'Паста':            doze_vol_handler_types[1],
  # 'Газ медицинский':  doze_vol_handler_types[2],
  'Газ':              doze_vol_handler_types[2],
  'Клей':             doze_vol_handler_types[3],
  'Масло':            doze_vol_handler_types[4],
  'Настойка':         doze_vol_handler_types[4],
  'Жидкость':         doze_vol_handler_types[4],
  'Капли':            doze_vol_handler_types[5],
  'Концентрат':       doze_vol_handler_types[5],
  'Раствор':          doze_vol_handler_types[5],
  'Растворитель':     doze_vol_handler_types[5],
  'Сироп':            doze_vol_handler_types[5],
  'Суспензия':        doze_vol_handler_types[5],
  'Эмульсия':         doze_vol_handler_types[5],
  'Лиофилизат':       doze_vol_handler_types[6],
  'Порошок':          doze_vol_handler_types[6],
  'Аэрозоль':         doze_vol_handler_types[7],
  'Спрей':            doze_vol_handler_types[7],
  'Гранулы':          doze_vol_handler_types[8],
  'Микросферы':       doze_vol_handler_types[8],
  'Губка':            doze_vol_handler_types[9],
  'Пластырь':         doze_vol_handler_types[9],
  'Система':          doze_vol_handler_types[10],
  'Напиток':          doze_vol_handler_types[11],
  'Питание':          doze_vol_handler_types[11],
  'Смесь':            doze_vol_handler_types[11],
  'ph_f_undefined':   doze_vol_handler_types[-1]
}

vol_units_groups = {
    0: {'ptn':        None,
        'ru_name' :   None},
    1: {'ptn':        ['г', 'g', 'gr', 'мл','ml', 'гр\.*', 'л' ],},
    2: {'ptn':        ['л', 'дм3',
                      'кг']}, # 13.12.2022
    3: {'ptn':        ['мл'],},
    4: {'ptn':        ['мл', 'г', 'ml', 'гр', 'млфл'],},
    5: {'ptn':        ['мл', 'ml',
                       'литров', 'кг', 'г', 'kg', 'gr\.*','g',  'л\.*,*', 'l', 'Л\**', 'Л\.*', 'Л',
                       'dose', # ниже добавление из группы 7
                       'доза', 'дозы', 'доз', 'дз', 'dosa', 'doza', 'dos', 'doz', 'd', 'д\.*'],
         
        # 1) если стоит одно число (без ед. измер дозировки и объема) - то это объем 2) если есть дозировка + ед. измер дозировки, потом число - то это объем
        },
    6: {'ptn':        ['dose', # # 22.11.2022 эти ЕИ объема: доза, дозы, доз
                       'доза', 'дозы', 'доз', 'дз', 'dosa', 'doza', 'dos', 'doz', 'd', 'д\.*'], 
        #None,
        'ru_name' :   None},
    7: {'ptn':        ['доз', 'доза', 'дз', 'dos', 'doz', 'dosa', 'doza', 'd', # 21.11.2022 доза в приоритете потом мл
                        'мл', 'ml', 'г', #'g',
                        'гр', 'g\.*', #05/10/2022
                       ],
        },
    8: {'ptn':        ['г','g'],
        'ru_name' :   None},
    9: {'ptn':        None,
        'ru_name' :   None},
    10: {'ptn':       None,
        'ru_name' :   None},
    11: {'ptn':        ['г', 'мл', 'л', 'ml'],
        'ru_name' :   ['г', 'мл', 'л']},
    -1: {'ptn':       ['г', 'g', 'gr', 'мл']+['л', 'дм3']+['мл']+['мл', 'г', 'ml', 'гр', 'млфл']+['мл', 'ml']+\
         ['мл', 'ml', 'доз', 'доза', 'dos', 'doz', 'dosa', 'doza', 'd', 'г', 'g']+ ['г', 'мл', 'л'],
        },
}
doze_units_groups = {
    0: {'ptn' :       ['mkg/dosa', 'mkg/d',  # 21.11.2022
                        'мг', 'г', 'mg', 'мкг', 'mkg', 'g', 'ЕД', 'ED', 'gr', 'МЕ', 'тыс\.* МЕ', 'тыс\.* *МЕ', 'тыс МЕ', 'гр\.*', 'доз',
                       'ЛЕ', 'тыс\.* *ед\.*', 'ЕD', 'LE', 'тыс\.* *ЕД', 'тыс\.* *ЕД', 'ME', # 04/10/2022
                       
                       ],
        
        },
    1: {'ptn':        ['мг/г', 'mg/g', 'mg/gr', 'Ед/г', 'мг', 'mg', 'Ед',
                       'МЕ/г ', 'g/ml ', 'МЕ/Г', 'g/gr', 'мг/мл', # 04/10/2022
                       'g/ml', # 21.11.2022
                      ],
        },
    2: {'ptn':        ['м3'],
        'ru_name' :   ['м3'] },
    3: {'ptn':        None,
        'ru_name' :   None},
    4: {'ptn':        None,
        'ru_name' :   None},
    5: {'ptn':        unit_slash_combination([['тыс\.* *анти-*Ха *МЕ', 'тыс.анти-Xa МЕ', 'тыс.анти-Xa МЕ',
                    'тыс.анти-Ха МЕ',  #'тыс.анти-Xa МЕ', 'тыс.анти-XaМЕ', 'тыс.анти-Ха МЕ', 
           'anti-Hа ME', # 23/11.2022
            'тыс.анти-XaМЕ', 'анти-XА МЕ',  # 24.11.2022
            'Anti-*Xa MЕ',  'anti-*XA *ME', 'ANTI-*HA *МЕ', 'анти-*ХА *МЕ',
         'ТЫС\.* *МЕ АНТИ-*ХА', 'МЕ *\(анти-*Ха\)', 'МЕ *анти-*Ха',   # 'anti-XA ME', 'anti-Ха ME', 'МЕ(анти-Ха)',
         'анти/ХА *ME', 'анти-*Xa *МЕ', 'анти-*ХА *МЕ', 'АНТИ-*ХА', # 'анти-XА МЕ',
          'mln *ME', 'mln\.*Ed', 'PNU', 
           'ED',  #'ED/ml' 23.11.2022
           'ЕD', 'ЕД', 'ЕД', 'КИЕ', 'Е',
            'E', # 23.11.2022
            'EД', # 24.11.2022
            'KИЕ', # 23.11.2022
            'MЕ', # 23.11.2022
            'anti-Ха ME', # 23.11.2022 МЕ русскими
            'anti-Ха ME', # 23.11.2022 МЕ русскими
            'анти\/ХА ME', # 24.11.2022
            #анти/ХА ME
          'млн\.* *МЕ', 'млн\.* *ЕД', 'тыс\.* *МЕ',  # 'млн. МЕ',  'млн ЕД',
          'МЕ', 'ME', 'ME', 'ЛЕ', 'LE'], [ 'мл', 'ml',  #'мл','мл', 'ml', # пропустил через set
                                   'л', 'l', # 22.11.2022
                                   ]])+\
        unit_slash_combination([[ 'мкмоль', 'ммоль', 'ммоль', 'mmol', 'ккал',  'мг', 'mg', 'мкг', 'Г','mkg', 'мгк','mgk', 
                                              'mg-*iodi', 'mg iodi', 'mg ioda', 'мг йода'],  
                                ['мл','ml',
                                'л', 'l', # 22.11.2022
                                ]])+\
        unit_slash_combination([['мг', 'мкг', 'mg', 'mkg', 'ml',
                                 'мл',
                                # ммоль/л  мл/доза 22.11.2022
                                ], ['доза', 'доз', 'doza', 'doz', 'dosa', 'dose', 'dos', 'd\.*', 'д\.*']])+\
        ['мл/мл', 'ml/ml', 'ml/мл', # исключения переводим потом в мг/мл,
         'мл/ml'] +\
        [ # восстанавливаем 22.11.2022
        'мг/г',]+\
        ['тыс\.* *анти-*Ха *МЕ',
         'Anti-*Xa MЕ',  'ANTI-*HA *МЕ', 'анти-*ХА *МЕ',
         'ТЫС\.* *МЕ АНТИ-*ХА', 'МЕ *\(анти-*Ха\)', 'МЕ *анти-*Ха',   # 'anti-XA ME', 'anti-Ха ME', 'МЕ(анти-Ха)',
         'анти/ХА *ME', 'анти-*Xa *МЕ', 'анти-*ХА *МЕ', 'АНТИ-*ХА', # 'анти-XА МЕ',
          'mln *ME', 'mln\.*Ed', 'PNU', 
           'ЕD', 'ЕД', 'КИЕ', 'Е',
         'E', # 23.11.2022
         'ED', # 24.11.2022
          'KИЕ', # 23.11.2022
         'anti-Ха ME', # 23.11.2022 МЕ русскими
          'млн\.* *МЕ', 'млн\.* *ЕД', 'тыс\.* *МЕ',  # 'млн. МЕ',  'млн ЕД',
          'МЕ', 'ME', 'ЛЕ', 'LE',
         'MЕ', # 24.11.2022
        'мг', 'mg', 'мкг', 'mkg', 'МЕ', 'ME', 'анти-*ХА *МЕ', 'тыс.анти-*Ха *МЕ', # восстанволение doze_unit 21.11.2022
         'g\.*',# 23.11.2022
         'PNU', 'ЕD', 'ЕД', 'КИЕ', 'Е',
         'доз', 'anti-*Ha *ME',  'mg-iodi', 'mg iodi', 'мг йода'],
        # # 150 anti-XA ME/ml, 151 ME/ml, ME/0.2ml  160 7 тыс.анти-Ха МЕ/0,7 мл, 66 ЕД/мл 67 млн.МЕ/мл
            # 190 ME/мл, 194 ED/ml
        # ЕД/мл
        },

    6: {'ptn':        ['мг/доза', 'мг/доз', 'мг/doza', 'мг/doz', 'мг/dosa', 'мг/dos', 'мг/d\.*', 'мг/d', 
                       'мкг/доза', 'мкг/доз', 
                       'мкг/doza', 'мкг/doz', 'мкг/dosa', 'мкг/dos', 'мкг/d\.*', 'мкг/d', 
                       'mg/доза', 'mg/доз', 'mg/doza', 'mg/doz', 'mg/dosa', 'mg/dos', 'mg/d\.*', 'mg/d', 'mkg/доза', 'mkg/доз', 'mkg/doza', 'mkg/doz', 
                       'mkg/dosa', 'mkg/dos', 'mkg/d\.*', 'mkg/d', 
                       'мл/доза',
                       'мг/мл', 'mg/ml', # 21.11.2022
                       'МЕ/доза', 'МЕ/доз', 'МЕ/doza', 'МЕ/doz', 'МЕ/dosa', 'МЕ/dos', 'МЕ/d\.*', 'МЕ/d', 
                       'ME/доза', 'ME/доз', 'ME/doza', 'ME/doz', 'ME/dosa', 'ME/dos', 'ME/d\.*', 'ME/d',
                         # МЕ/доза мг/доза мл/доза мкг/доза mkg/dosa # эти ЕИ дозировки: 22.11.2022
                       'ME/г', # 02.12.2022 ME латинскими
                       'МЕ/г',  # 02.12.2022
                       'тыс\.* *АТрЕ', 'тыс\.* *ЕД', 'тыс\.* *МЕ',
                       'мкл/мл', 'млн *ЕД', 'млн\.* *ЕД', 'млн\.* *КОЕ', 'млн\.* *МЕ','млнМЕ',  
                       'mln *ED', 'mln *KOE', 'MlnME', 'млн.КОЕ',
                       'УЕ',
                       'мг', 'mg', 'ЕД', 'ED', 'г', 'g', 'МЕ', 'ME', 'гр', 'gr\.*', 'gr', 'мкг', 'mkg',
                       'ATpE',  'KOE',  'АТрЕ',  


          # ('мг', 'мкг', 'mg', 'mkg', 'МЕ', 'ME'), ('доза', 'доз', 'doza', 'doz', 'dosa', 'dos', 'd.', 'd')
                       ],
        'ru_name' :   ['мг', 'мг', 'ЕД', 'ЕД', 'г', 'г', 'МЕ', 'МЕ', 'г', 'г', 'мкг', 'мкг']},
    7: {'ptn':        ['мг/мл', 'mg/ml', 'мкг/мл', 'mkg/ml',
                       'мг/доза', 'мкг/доза', 'mg/doza', 'mg/dosa', 'mg/доза',  'mkg/doza', 'mkg/doz','mkg/dosa*',  'mkg/доза', 'mkg/d\.*',
                       'мкг/доза', # 02.12.2022
                       'mg/dos\.*', 'mg/dos\.*', 'мг/д\.*',   #'mkg\\dosa', 'mg\\dos.',
                       'g/g',   #05/10/2022
                       'МЕ/доза',
                       'мг', 'mg', 'mkg',
                       'мкг', # 21.11.2022
                       ],
        #'%',
        'ru_name' :   ['мг/доза', 'мг/доза', 'мг/доза', 'мг/доза', 'мкг/доза', 'мкг/доза', 'мкг/доза', 'мкг/доза', 
                       'мг/мл', 'мг/мл', 'мкг/мл', 'мкг/мл', 'мг', 'мг', 'мкг/доза', 'мг/доза']},
    8: {'ptn':        ['мг', 'ЕД', 'мг/мл', 'г\.*', 'g', 'mg', 'тыс\.* *ЕД'],
        'ru_name' :   None},
    9: {'ptn':        ['мкг/час', 'мкг/часа', 'мкг/ч'], # 'МКГ/ЧАС', 
        'ru_name' :   None},
    10: {'ptn':       ['мкг/час', 'мкг/часа'], # 'МКГ/ЧАС', 
        'ru_name' :   None},
    11: {'ptn':       None,
        'ru_name' :   None},
    -1: {'ptn':       ['мг', 'г', 'mg', 'мкг', 'mkg', 'g', 'ЕД', 'ED', 'gr', 'МЕ', 'тыс\. МЕ', 'тыс\.МЕ', 'тыс МЕ', 'гр\.*', 'доз']+\
                      ['%', 'мг/г', 'mg/g', 'mg/gr', 'Ед/г', 'мг', 'mg', 'Ед']+ ['м3']+ \
                      ['мг/мл', 'mg/ml', 'мг', 'mg', 'мкг', 'mkg', 'мкг/мл', 'mkg/ml', 'МЕ/мл', 'ME/ml', 'ЕД/мл', 'ED/ml', 
                       'МЕ', 'ME', '%', 'анти-*ХА *МЕ/мл', 'анти-*ХА *МЕ', 'Анти-*Ха/мл', 'тыс.анти-*Ха *МЕ', 'Анти-*Ха МЕ/ml', r'МЕ \(анти-*Ха\)/ml', 
                       'доз', 'мг/г', 'мл/доза', 'МЕ/мл',
                       'anti-*Ha *ME', 'anti-*Hа *ME/мл']+\
                      ['мг', 'mg', 'ЕД', 'ED', 'г', 'g', 'МЕ', 'ME', 'гр', 'gr', 'мкг', 'mkg']+\
                      ['мг/доза', 'mg/doza', 'mg/dosa', 'mg/доза', 'мкг/доза', 'mkg/doza', 'mkg/dosa', 'mkg/d', 
                       'мг/мл', 'mg/ml', 'мкг/мл', 'mkg/ml', 'мг', 'mg', '%', 'mkg/dosa', 'mg/dos\.*'],
        'ru_name' :   None}
}

units_total_lst = []
for i, (k, v) in enumerate(doze_units_groups.items()):
    #ptn_digits = r'(((\d+,\d+|\d+\.\d+|\d+)\s*((тыс)(.)*)*)\s*)'
    #ptn_digits = r'(?P<digits>\.*,*(\d+,\d+|\d+\.\d+|\d+))'
    ptn_digits = r'(?P<digits>((\d+,\d+)|(\d+\.\d+)|(\d+))\s*((тыс)(\.|,)*)*\s*)'
    ptn_digits = r'(?P<digits>((\d+,\d+)|(\d+\.\d+)|(\d+)))'
    #print(k,v)
    if doze_vol_handler_types[k][1]: # есть is_dosed
        if v['ptn'] is not None:
            doze_units_groups[k]['ptn_str'] = make_doze_ptn_str(v['ptn'])
            # doze_units_groups[k]['cmplx_ptn_str'] = make_complex_doze_ptn_str(v['ptn'])
            doze_units_groups[k]['cmplx_ptn_str'] = make_complex_doze_ptn_str_02(v['ptn'])
            units_total_lst.extend(v['ptn'])
        else: 
            doze_units_groups[k]['ptn_str'] = None
            doze_units_groups[k]['cmplx_ptn_str'] = None
    #if i >2: break
for i, (k, v) in enumerate(vol_units_groups.items()):
    ptn_digits = r'(?P<digits>(\d+,\d+)|(\d+\.\d+)|([\d\s]+\d+)|(\d+))'
    if doze_vol_handler_types[k][3]: # есть is_vol 
        if v['ptn'] is not None:
            vol_units_groups[k]['ptn_str'] = make_vol_ptn_str(v['ptn'])
            units_total_lst.extend(v['ptn'])
        else: 
            vol_units_groups[k]['ptn_str'] = None

def make_combinations_by_punct_01(lst, delimiter):
    if delimiter is None or '*' not in delimiter: return lst
    u1_split = []
    for u0 in lst:
        s_lst = u0.split(delimiter)
        u1_split.extend([''.join(s_lst), re.sub(r"\*",'', delimiter).join(s_lst)])
    return u1_split
make_combinations_by_punct_01([r'anti-*ha\.* *ме/мл'], r'-*')    
def make_combinations_by_punct(lst):
    lst_01 = make_combinations_by_punct_01(lst, r'-*')
    # print(lst_01)
    lst_02 = make_combinations_by_punct_01(lst_01, r'\.*')
    # print(lst_02)
    lst_03 = make_combinations_by_punct_01(lst_02, r' *')
    lst_04 = make_combinations_by_punct_01(lst_03, r',*')
    lst_04 = make_combinations_by_punct_01(lst_04, r'a*')
    return lst_04






# v 21/11/2022
# import itertools 
# import re

# def unit_slash_combination(units):
#     # units = [('AntiXa MЕ','MЕ', 'ЛЕ'),('мл','ml')]
#     # print(units)
#     list_units = list(itertools.product(*units))
#     list_units_slash = [i[0]+'/'+ i[1]  for i in list_units]
#     # print(list_units_slash)
#     return list_units_slash

# def make_doze_ptn_str(lst):
#     ptn_digits = r'(?P<digits>((\d+,\d+)|(\d+\.\d+)|(\d+))\s*((тыс)(\.|,)*)*\s*)'
#     ptn_digits = r'(?P<digits>((\d+,\d+)|(\d+\.\d+)|(\d+)))'
#     p_dozes = [re.sub(r"(?<=/)\s*(\w+)", '', p).replace('/','') for p in lst]
#     p_pseudos = [re.sub(r".+/", '', p) if '/' in p else None for p in lst ]
#     # fr"(?P<doze_digits_{ip:03d}>((\d+,\d+)|(\d+\.\d+)|([\d\s]+\d+)|(\d+)))\s*"  +\
#     doze_ptn_str = \
#         "|".join(([r'(?:' + # ( [::-1]\
#       fr"(?P<doze_digits_{ip:03d}>((\d+,\d+)|(\d+\.\d+)|([\d\s]+\d+)|(\d+)))\s*"  +\
#       (fr"(?P<doze_unit_{ip:03d}>{p_doze})\.*,*" if p_pseudos[ip] is not None else fr"(?P<doze_unit_{ip:03d}>{p_doze})(\.|,|\s|\+|$)")  +\
#       (fr"(?:(/|\||\\)(?P<digits_pseudo_{ip:03d}>\s*((\d+,\d+)|(\d+\.\d+)|(\d+)))*\s*(?P<unit_pseudo_{ip:03d}>({p_pseudos[ip]})))(\.|,|\s|$)*" \
#           if p_pseudos[ip] is not None else '') \
#         + r")"
#       for ip, p_doze in enumerate(p_dozes)]) [::1])   
#       # 14/10/2022  (fr"(?P<doze_unit_{ip:03d}>{p_doze})\.*,*/*(\s*|$)" if p_pseudos[ip] is not None else fr"(?P<doze_unit_{ip:03d}>{p_doze})(\.|,|\s|\+|/|$)")  +\  
#       # (fr"(?P<doze_unit_{ip:03d}>{p_doze})\.*,*(\s*|$)" if p_pseudos[ip] is not None else fr"(?P<doze_unit_{ip:03d}>{p_doze})(\.|,|\s|\+|$)")  +\
#     return doze_ptn_str

# def make_vol_ptn_str(lst):
#     #ptn_digits = r'(?P<digits>(\d+,\d+)|(\d+\.\d+)|(\d+))'
#     ptn_digits = r'(?P<digits>(\d+,\d+)|(\d+\.\d+)|([\d\s]+\d+)|(\d+))'
#     vol_ptn_str = None
#     try:
#         vol_ptn_str = r"(?:" + ptn_digits + r")\s*" +\
#                   r"(?P<unit>" +  "|".join(['(?:' + p + r")" for p in lst]) + r")\.*,*(\s*|$)" 
#     except Exception as err:
#         print(err, "lst is not list of str")
#     return vol_ptn_str

# def make_complex_doze_ptn_str(lst):
#     ptn_digits = r'(?P<digits>((\d+,\d+)|(\d+\.\d+)|(\d+))\s*((тыс)(\.|,)*)*\s*)'
#     ptn_digits = r'(?P<digits>((\d+,\d+)|(\d+\.\d+)|(\d+)))'
#     ptn_digits_0 = r"((\d+,\d+)|(\d+\.\d+)|(\d+\s*\d+)|(\d+))"
#     # r"(?:(\+\s*\d+\s*)+\s*мг\s*)+
#     # ptn_first_doze_unit = r"(?P<first_doze_unit>" + '|'.join([r"(?:" + ptn + r"\.*,*(\s*|\b|$))" for ptn in lst] ) + r")*"
#     ptn_first_doze_unit = r"(?P<first_doze_unit>" + '|'.join([r"(?:" + ptn + r"\.*,*(\s*|$))" for ptn in lst] ) + r")*(\s*|$)"
#     ptn_plus_doze_unit = r"(?P<plus_doze_unit>" + '|'.join([r"(?:" + ptn + r"\.*,*(\s*|$))" for ptn in lst] ) + r")*"
#     complex_doze_ptn_str = r"(?:" + \
#         r"(?P<first_doze>" + ptn_digits_0 + r"\s*" + ptn_first_doze_unit + r"\s*)" +\
#         r"(?P<plus_dozes>\s*(\+|/)*\s*" + ptn_digits_0 + r"*\s*" + ptn_plus_doze_unit + r"\s*)*" +\
#         r")"
#         #r"(?P<doze_digits>\+\s*((\d+,\d+)|(\d+\.\d+)|([\d\s]+\d+)|(\d+))\s*)+"  +\
#     return complex_doze_ptn_str    
# # handler_numder, is_dosed, is_pseudo_vol, is_vol, is_proc_dozed
# # doze_vol_handler_types = [ [0, True, False, False, False],
# #                           [1, True, True, True, True],
# #                           [2, True, False, True, False],
# #                           [3, False, False, True, False],
# #                           [4, False, False, True, False],
# #                           [5, True, True, True, True],
# #                           [6, True, False, False, False],
# #                           [7, True, True, True, True],
# #                           [8, True, True, True, False], 
# #                           [9, True, True, False, False],
# #                           [10, True, True, False, False], #соеденить с группой №9
# #                           [11, False, False, True, False],
# #                           [-1, True, True, True, False],
# # ]
# # is_proc_dozed = is_dosed
# doze_vol_handler_types = [ [0, True, False, False, False],
#                           [1, True, True, True, True],
#                           [2, True, False, True, True],
#                           [3, False, False, True, False],
#                           [4, False, False, True, False],
#                           [5, True, True, True, True],
#                           [6, True, False, False, True],
#                           [7, True, True, True, True],
#                           [8, True, True, True, True], 
#                           [9, True, True, False, True],
#                           [10, True, True, False, True], #соеденить с группой №9
#                           [11, False, False, True, False],
#                           [-1, True, True, True, True],
# ]
# #doze_units_groups, vol_units_groups, doze_vol_handler_types
# doze_vol_pharm_form_handlers = {
#   'Таблетки':         doze_vol_handler_types[0],
#   'Капсулы':          doze_vol_handler_types[0],
#   'Драже':            doze_vol_handler_types[0],
#   'Суппозитории':     doze_vol_handler_types[0],
#   'Пастилки':         doze_vol_handler_types[0],
#   'Имплантат':        doze_vol_handler_types[0],
#   'Крем':             doze_vol_handler_types[1],
#   'Мазь':             doze_vol_handler_types[1],
#   'Гель':             doze_vol_handler_types[1],
#   'Линимент':         doze_vol_handler_types[1],
#   'Паста':            doze_vol_handler_types[1],
#   # 'Газ медицинский':  doze_vol_handler_types[2],
#   'Газ':              doze_vol_handler_types[2],
#   'Клей':             doze_vol_handler_types[3],
#   'Масло':            doze_vol_handler_types[4],
#   'Настойка':         doze_vol_handler_types[4],
#   'Жидкость':         doze_vol_handler_types[4],
#   'Капли':            doze_vol_handler_types[5],
#   'Концентрат':       doze_vol_handler_types[5],
#   'Раствор':          doze_vol_handler_types[5],
#   'Растворитель':     doze_vol_handler_types[5],
#   'Сироп':            doze_vol_handler_types[5],
#   'Суспензия':        doze_vol_handler_types[5],
#   'Эмульсия':         doze_vol_handler_types[5],
#   'Лиофилизат':       doze_vol_handler_types[6],
#   'Порошок':          doze_vol_handler_types[6],
#   'Аэрозоль':         doze_vol_handler_types[7],
#   'Спрей':            doze_vol_handler_types[7],
#   'Гранулы':          doze_vol_handler_types[8],
#   'Микросферы':       doze_vol_handler_types[8],
#   'Губка':            doze_vol_handler_types[9],
#   'Пластырь':         doze_vol_handler_types[9],
#   'Система':          doze_vol_handler_types[10],
#   'Напиток':          doze_vol_handler_types[11],
#   'Питание':          doze_vol_handler_types[11],
#   'Смесь':            doze_vol_handler_types[11],
#   'ph_f_undefined':   doze_vol_handler_types[-1]
# }

# vol_units_groups = {
#     0: {'ptn':        None,
#         'ru_name' :   None},
#     1: {'ptn':        ['г', 'g', 'gr', 'мл','ml', 'гр\.*', 'л' ],},
#     2: {'ptn':        ['л', 'дм3']},
#     3: {'ptn':        ['мл'],},
#     4: {'ptn':        ['мл', 'г', 'ml', 'гр', 'млфл'],},
#     5: {'ptn':        ['мл', 'ml',
#                        'литров', 'кг', 'г', 'kg', 'gr\.*','g',  'л\.*,*', 'l', 'Л\**', 'Л\.*', 'Л',
#                        'dose', # ниже добавление из группы 7
#                        'доза', 'доз', 'дз', 'dosa', 'doza', 'dos', 'doz', 'd', 'д\.*'],
         
#         # 1) если стоит одно число (без ед. измер дозировки и объема) - то это объем 2) если есть дозировка + ед. измер дозировки, потом число - то это объем
#         },
#     6: {'ptn':        None,
#         'ru_name' :   None},
#     7: {'ptn':        ['доз', 'доза', 'дз', 'dos', 'doz', 'dosa', 'doza', 'd', # 21.11.2022 доза в приоритете потом мл
#                         'мл', 'ml', 'г', #'g',
#                         'гр', 'g\.*', #05/10/2022
#                        ],
#         },
#     8: {'ptn':        ['г','g'],
#         'ru_name' :   None},
#     9: {'ptn':        None,
#         'ru_name' :   None},
#     10: {'ptn':       None,
#         'ru_name' :   None},
#     11: {'ptn':        ['г', 'мл', 'л', 'ml'],
#         'ru_name' :   ['г', 'мл', 'л']},
#     -1: {'ptn':       ['г', 'g', 'gr', 'мл']+['л', 'дм3']+['мл']+['мл', 'г', 'ml', 'гр', 'млфл']+['мл', 'ml']+\
#          ['мл', 'ml', 'доз', 'доза', 'dos', 'doz', 'dosa', 'doza', 'd', 'г', 'g']+ ['г', 'мл', 'л'],
#         },
# }
# doze_units_groups = {
#     0: {'ptn' :       ['mkg/dosa', 'mkg/d',  # 21.11.2022
#                         'мг', 'г', 'mg', 'мкг', 'mkg', 'g', 'ЕД', 'ED', 'gr', 'МЕ', 'тыс\.* МЕ', 'тыс\.*МЕ', 'тыс МЕ', 'гр\.*', 'доз',
#                        'ЛЕ', 'тыс\.* *ед\.*', 'ЕD', 'LE', 'тыс\.* *ЕД', 'тыс\.* *ЕД', 'ME', # 04/10/2022
                       
                       
#                        ],
        
#         },
#     1: {'ptn':        ['мг/г', 'mg/g', 'mg/gr', 'Ед/г', 'мг', 'mg', 'Ед',
#                        'МЕ/г ', 'g/ml ', 'МЕ/Г', 'g/gr', 'мг/мл', # 04/10/2022
#                        'g/ml', # 21.11.2022
#                       ],
#         },
#     2: {'ptn':        ['м3'],
#         'ru_name' :   ['м3'] },
#     3: {'ptn':        None,
#         'ru_name' :   None},
#     4: {'ptn':        None,
#         'ru_name' :   None},
#     5: {'ptn':        unit_slash_combination([['тыс\.* *анти-*Ха *МЕ', #'тыс.анти-Xa МЕ', 'тыс.анти-XaМЕ', 'тыс.анти-Ха МЕ', 
#             'Anti-*Xa MЕ',  'ANTI-*HA *МЕ', 'анти-*ХА *МЕ',
#          'ТЫС\.* *МЕ АНТИ-*ХА', 'МЕ *\(анти-*Ха\)', 'МЕ *анти-*Ха',   # 'anti-XA ME', 'anti-Ха ME', 'МЕ(анти-Ха)',
#          'анти/ХА *ME', 'анти-*Xa *МЕ', 'анти-*ХА *МЕ', 'АНТИ-*ХА', # 'анти-XА МЕ',
#           'mln *ME', 'mln\.*Ed', 'PNU', 
#            'ЕD', 'ЕД', 'КИЕ', 'Е',
#           'млн\.* *МЕ', 'млн\.* *ЕД', 'тыс\.* *МЕ',  # 'млн. МЕ',  'млн ЕД',
#           'МЕ', 'ME', 'ЛЕ', 'LE'], ['мл','ml']])+\
#         unit_slash_combination([[ 'мкмоль', 'ммоль', 'mmol', 'ккал',  'мг', 'mg', 'мкг', 'Г','mkg', 'мгк','mgk', 
#                                               'mg-*iodi', 'mg iodi', 'mg ioda', 'мг йода'],  
#                                 ['мл','ml']])+\
#         unit_slash_combination([['мг', 'мкг', 'mg', 'mkg', 'ml'], ['доза', 'доз', 'doza', 'doz', 'dosa', 'dose', 'dos', 'd\.*', 'д\.*']])+\
#         ['мл/мл', 'ml/ml', 'ml/мл', # исключения переводим потом в мг/мл,
#          'мл/ml'] +\
#         ['тыс\.* *анти-*Ха *МЕ',
#          'Anti-*Xa MЕ',  'ANTI-*HA *МЕ', 'анти-*ХА *МЕ',
#          'ТЫС\.* *МЕ АНТИ-*ХА', 'МЕ *\(анти-*Ха\)', 'МЕ *анти-*Ха',   # 'anti-XA ME', 'anti-Ха ME', 'МЕ(анти-Ха)',
#          'анти/ХА *ME', 'анти-*Xa *МЕ', 'анти-*ХА *МЕ', 'АНТИ-*ХА', # 'анти-XА МЕ',
#           'mln *ME', 'mln\.*Ed', 'PNU', 
#            'ЕD', 'ЕД', 'КИЕ', 'Е',
#           'млн\.* *МЕ', 'млн\.* *ЕД', 'тыс\.* *МЕ',  # 'млн. МЕ',  'млн ЕД',
#           'МЕ', 'ME', 'ЛЕ', 'LE',
#         'мг', 'mg', 'мкг', 'mkg', 'МЕ', 'ME', 'анти-*ХА *МЕ', 'тыс.анти-*Ха *МЕ', # восстанволение doze_unit 21.11.2022
#          'PNU', 'ЕD', 'ЕД', 'КИЕ', 'Е',
#          'доз', 'anti-*Ha *ME',  'mg-iodi', 'mg iodi', 'мг йода'],
        
#         },

#     6: {'ptn':        ['мг/доза', 'мг/доз', 'мг/doza', 'мг/doz', 'мг/dosa', 'мг/dos', 'мг/d\.*', 'мг/d', 'мкг/доза', 'мкг/доз', 
#                        'мкг/doza', 'мкг/doz', 'мкг/dosa', 'мкг/dos', 'мкг/d\.*', 'мкг/d', 
#                        'mg/доза', 'mg/доз', 'mg/doza', 'mg/doz', 'mg/dosa', 'mg/dos', 'mg/d\.*', 'mg/d', 'mkg/доза', 'mkg/доз', 'mkg/doza', 'mkg/doz', 
#                        'mkg/dosa', 'mkg/dos', 'mkg/d\.*', 'mkg/d', 
#                        'мг/мл', 'mg/ml', # 21.11.2022
#                        'МЕ/доза', 'МЕ/доз', 'МЕ/doza', 'МЕ/doz', 'МЕ/dosa', 'МЕ/dos', 'МЕ/d\.*', 'МЕ/d', 
#                        'ME/доза', 'ME/доз', 'ME/doza', 'ME/doz', 'ME/dosa', 'ME/dos', 'ME/d\.*', 'ME/d',
#                        'тыс\.* *АТрЕ', 'тыс\.* *ЕД', 'тыс\.* *МЕ',
#                        'мкл/мл', 'млн *ЕД', 'млн\.* *ЕД', 'млн\.* *КОЕ', 'млн\.* *МЕ','млнМЕ',  
#                        'mln *ED', 'mln *KOE', 'MlnME', 'млн.КОЕ',
#                        'УЕ',
#                        'мг', 'mg', 'ЕД', 'ED', 'г', 'g', 'МЕ', 'ME', 'гр', 'gr\.*', 'gr', 'мкг', 'mkg',
#                        'ATpE',  'KOE',  'АТрЕ',  
                       

#           # ('мг', 'мкг', 'mg', 'mkg', 'МЕ', 'ME'), ('доза', 'доз', 'doza', 'doz', 'dosa', 'dos', 'd.', 'd')
#                        ],
#         'ru_name' :   ['мг', 'мг', 'ЕД', 'ЕД', 'г', 'г', 'МЕ', 'МЕ', 'г', 'г', 'мкг', 'мкг']},
#     7: {'ptn':        ['мг', 'mg', 'mkg',
#                        'мкг', # 21.11.2022
#                        'мг/мл', 'mg/ml', 'мкг/мл', 'mkg/ml',
#                        'мг/доза', 'мкг/доза', 'mg/doza', 'mg/dosa', 'mg/доза',  'mkg/doza', 'mkg/doz','mkg/dosa*',  'mkg/доза', 'mkg/d\.*',
#                        'mg/dos\.*', 'mg/dos\.*', 'мг/д\.*',   #'mkg\\dosa', 'mg\\dos.',
#                        'g/g',   #05/10/2022
#                        'МЕ/доза',
#                        ],
#         #'%',
#         'ru_name' :   ['мг/доза', 'мг/доза', 'мг/доза', 'мг/доза', 'мкг/доза', 'мкг/доза', 'мкг/доза', 'мкг/доза', 
#                        'мг/мл', 'мг/мл', 'мкг/мл', 'мкг/мл', 'мг', 'мг', 'мкг/доза', 'мг/доза']},
#     8: {'ptn':        ['мг', 'ЕД', 'мг/мл', 'г\.*', 'g', 'mg', 'тыс\.* *ЕД'],
#         'ru_name' :   None},
#     9: {'ptn':        ['мкг/час', 'мкг/часа'], # 'МКГ/ЧАС', 
#         'ru_name' :   None},
#     10: {'ptn':       ['мкг/час', 'мкг/часа'], # 'МКГ/ЧАС', 
#         'ru_name' :   None},
#     11: {'ptn':       None,
#         'ru_name' :   None},
#     -1: {'ptn':       ['мг', 'г', 'mg', 'мкг', 'mkg', 'g', 'ЕД', 'ED', 'gr', 'МЕ', 'тыс\. МЕ', 'тыс\.МЕ', 'тыс МЕ', 'гр\.*', 'доз']+\
#                       ['%', 'мг/г', 'mg/g', 'mg/gr', 'Ед/г', 'мг', 'mg', 'Ед']+ ['м3']+ \
#                       ['мг/мл', 'mg/ml', 'мг', 'mg', 'мкг', 'mkg', 'мкг/мл', 'mkg/ml', 'МЕ/мл', 'ME/ml', 'ЕД/мл', 'ED/ml', 
#                        'МЕ', 'ME', '%', 'анти-*ХА *МЕ/мл', 'анти-*ХА *МЕ', 'Анти-*Ха/мл', 'тыс.анти-*Ха *МЕ', 'Анти-*Ха МЕ/ml', r'МЕ \(анти-*Ха\)/ml', 
#                        'доз', 'мг/г', 'мл/доза', 'МЕ/мл',
#                        'anti-*Ha *ME', 'anti-*Hа *ME/мл']+\
#                       ['мг', 'mg', 'ЕД', 'ED', 'г', 'g', 'МЕ', 'ME', 'гр', 'gr', 'мкг', 'mkg']+\
#                       ['мг/доза', 'mg/doza', 'mg/dosa', 'mg/доза', 'мкг/доза', 'mkg/doza', 'mkg/dosa', 'mkg/d', 
#                        'мг/мл', 'mg/ml', 'мкг/мл', 'mkg/ml', 'мг', 'mg', '%', 'mkg/dosa', 'mg/dos\.*'],
#         'ru_name' :   None}
# }

# units_total_lst = []
# for i, (k, v) in enumerate(doze_units_groups.items()):
#     #ptn_digits = r'(((\d+,\d+|\d+\.\d+|\d+)\s*((тыс)(.)*)*)\s*)'
#     #ptn_digits = r'(?P<digits>\.*,*(\d+,\d+|\d+\.\d+|\d+))'
#     ptn_digits = r'(?P<digits>((\d+,\d+)|(\d+\.\d+)|(\d+))\s*((тыс)(\.|,)*)*\s*)'
#     ptn_digits = r'(?P<digits>((\d+,\d+)|(\d+\.\d+)|(\d+)))'
#     #print(k,v)
#     if doze_vol_handler_types[k][1]: # есть is_dosed
#         if v['ptn'] is not None:
#             doze_units_groups[k]['ptn_str'] = make_doze_ptn_str(v['ptn'])
#             doze_units_groups[k]['cmplx_ptn_str'] = make_complex_doze_ptn_str(v['ptn'])
#             units_total_lst.extend(v['ptn'])
#         else: 
#             doze_units_groups[k]['ptn_str'] = None
#             doze_units_groups[k]['cmplx_ptn_str'] = None
#     #if i >2: break
# for i, (k, v) in enumerate(vol_units_groups.items()):
#     ptn_digits = r'(?P<digits>(\d+,\d+)|(\d+\.\d+)|([\d\s]+\d+)|(\d+))'
#     if doze_vol_handler_types[k][3]: # есть is_vol 
#         if v['ptn'] is not None:
#             vol_units_groups[k]['ptn_str'] = make_vol_ptn_str(v['ptn'])
#             units_total_lst.extend(v['ptn'])
#         else: 
#             vol_units_groups[k]['ptn_str'] = None

# def make_combinations_by_punct_01(lst, delimiter):
#     if delimiter is None or '*' not in delimiter: return lst
#     u1_split = []
#     for u0 in lst:
#         s_lst = u0.split(delimiter)
#         u1_split.extend([''.join(s_lst), re.sub(r"\*",'', delimiter).join(s_lst)])
#     return u1_split
# # make_combinations_by_punct_01([r'anti-*ha\.* *ме/мл'], r'-*')    
# def make_combinations_by_punct(lst):
#     lst_01 = make_combinations_by_punct_01(lst, r'-*')
#     # print(lst_01)
#     lst_02 = make_combinations_by_punct_01(lst_01, r'\.*')
#     # print(lst_02)
#     lst_03 = make_combinations_by_punct_01(lst_02, r' *')
#     lst_04 = make_combinations_by_punct_01(lst_03, r',*')
#     lst_04 = make_combinations_by_punct_01(lst_04, r'a*')
#     return lst_04


# import itertools
# import re

# def unit_slash_combination(units):
#     # units = [('AntiXa MЕ','MЕ', 'ЛЕ'),('мл','ml')]
#     # print(units)
#     list_units = list(itertools.product(*units))
#     list_units_slash = [i[0]+'/'+ i[1]  for i in list_units]
#     # print(list_units_slash)
#     return list_units_slash

# def make_doze_ptn_str(lst):
#     ptn_digits = r'(?P<digits>((\d+,\d+)|(\d+\.\d+)|(\d+))\s*((тыс)(\.|,)*)*\s*)'
#     ptn_digits = r'(?P<digits>((\d+,\d+)|(\d+\.\d+)|(\d+)))'
#     p_dozes = [re.sub(r"(?<=/)\s*(\w+)", '', p).replace('/','') for p in lst]
#     p_pseudos = [re.sub(r".+/", '', p) if '/' in p else None for p in lst ]
#     # fr"(?P<doze_digits_{ip:03d}>((\d+,\d+)|(\d+\.\d+)|([\d\s]+\d+)|(\d+)))\s*"  +\
#     doze_ptn_str = \
#         "|".join(([r'(?:' + # ( [::-1]\
#       fr"(?P<doze_digits_{ip:03d}>((\d+,\d+)|(\d+\.\d+)|([\d\s]+\d+)|(\d+)))\s*"  +\
#       (fr"(?P<doze_unit_{ip:03d}>{p_doze})\.*,*" if p_pseudos[ip] is not None else fr"(?P<doze_unit_{ip:03d}>{p_doze})(\.|,|\s|\+|$)")  +\
#       (fr"(?:(/|\||\\)(?P<digits_pseudo_{ip:03d}>\s*((\d+,\d+)|(\d+\.\d+)|(\d+)))*\s*(?P<unit_pseudo_{ip:03d}>({p_pseudos[ip]})))(\.|,|\s|$)*" \
#           if p_pseudos[ip] is not None else '') \
#         + r")"
#       for ip, p_doze in enumerate(p_dozes)]) [::1])   
#       # 14/10/2022  (fr"(?P<doze_unit_{ip:03d}>{p_doze})\.*,*/*(\s*|$)" if p_pseudos[ip] is not None else fr"(?P<doze_unit_{ip:03d}>{p_doze})(\.|,|\s|\+|/|$)")  +\  
#       # (fr"(?P<doze_unit_{ip:03d}>{p_doze})\.*,*(\s*|$)" if p_pseudos[ip] is not None else fr"(?P<doze_unit_{ip:03d}>{p_doze})(\.|,|\s|\+|$)")  +\
#     return doze_ptn_str

# def make_vol_ptn_str(lst):
#     #ptn_digits = r'(?P<digits>(\d+,\d+)|(\d+\.\d+)|(\d+))'
#     ptn_digits = r'(?P<digits>(\d+,\d+)|(\d+\.\d+)|([\d\s]+\d+)|(\d+))'
#     vol_ptn_str = None
#     try:
#         vol_ptn_str = r"(?:" + ptn_digits + r")\s*" +\
#                   r"(?P<unit>" +  "|".join(['(?:' + p + r")" for p in lst]) + r")\.*,*(\s*|$)" 
#     except Exception as err:
#         print(err, "lst is not list of str")
#     return vol_ptn_str

# def make_complex_doze_ptn_str(lst):
#     ptn_digits = r'(?P<digits>((\d+,\d+)|(\d+\.\d+)|(\d+))\s*((тыс)(\.|,)*)*\s*)'
#     ptn_digits = r'(?P<digits>((\d+,\d+)|(\d+\.\d+)|(\d+)))'
#     ptn_digits_0 = r"((\d+,\d+)|(\d+\.\d+)|(\d+\s*\d+)|(\d+))"
#     # r"(?:(\+\s*\d+\s*)+\s*мг\s*)+
#     # ptn_first_doze_unit = r"(?P<first_doze_unit>" + '|'.join([r"(?:" + ptn + r"\.*,*(\s*|\b|$))" for ptn in lst] ) + r")*"
#     ptn_first_doze_unit = r"(?P<first_doze_unit>" + '|'.join([r"(?:" + ptn + r"\.*,*(\s*|$))" for ptn in lst] ) + r")*(\s*|$)"
#     ptn_plus_doze_unit = r"(?P<plus_doze_unit>" + '|'.join([r"(?:" + ptn + r"\.*,*(\s*|$))" for ptn in lst] ) + r")*"
#     complex_doze_ptn_str = r"(?:" + \
#         r"(?P<first_doze>" + ptn_digits_0 + r"\s*" + ptn_first_doze_unit + r"\s*)" +\
#         r"(?P<plus_dozes>\s*(\+|/)*\s*" + ptn_digits_0 + r"*\s*" + ptn_plus_doze_unit + r"\s*)*" +\
#         r")"
#         #r"(?P<doze_digits>\+\s*((\d+,\d+)|(\d+\.\d+)|([\d\s]+\d+)|(\d+))\s*)+"  +\
#     return complex_doze_ptn_str    
# # handler_numder, is_dosed, is_pseudo_vol, is_vol, is_proc_dozed
# doze_vol_handler_types = [ [0, True, False, False, False],
#                           [1, True, True, True, True],
#                           [2, True, False, True, False],
#                           [3, False, False, True, False],
#                           [4, False, False, True, False],
#                           [5, True, True, True, True],
#                           [6, True, False, False, False],
#                           [7, True, True, True, True],
#                           [8, True, True, True, False], 
#                           [9, True, True, False, False],
#                           [10, True, True, False, False], #соеденить с группой №9
#                           [11, False, False, True, False],
#                           [-1, True, True, True, False],
# ]
# #doze_units_groups, vol_units_groups, doze_vol_handler_types
# doze_vol_pharm_form_handlers = {
#   'Таблетки':         doze_vol_handler_types[0],
#   'Капсулы':          doze_vol_handler_types[0],
#   'Драже':            doze_vol_handler_types[0],
#   'Суппозитории':     doze_vol_handler_types[0],
#   'Пастилки':         doze_vol_handler_types[0],
#   'Имплантат':        doze_vol_handler_types[0],
#   'Крем':             doze_vol_handler_types[1],
#   'Мазь':             doze_vol_handler_types[1],
#   'Гель':             doze_vol_handler_types[1],
#   'Линимент':         doze_vol_handler_types[1],
#   'Паста':            doze_vol_handler_types[1],
#   # 'Газ медицинский':  doze_vol_handler_types[2],
#   'Газ':              doze_vol_handler_types[2],
#   'Клей':             doze_vol_handler_types[3],
#   'Масло':            doze_vol_handler_types[4],
#   'Настойка':         doze_vol_handler_types[4],
#   'Жидкость':         doze_vol_handler_types[4],
#   'Капли':            doze_vol_handler_types[5],
#   'Концентрат':       doze_vol_handler_types[5],
#   'Раствор':          doze_vol_handler_types[5],
#   'Растворитель':     doze_vol_handler_types[5],
#   'Сироп':            doze_vol_handler_types[5],
#   'Суспензия':        doze_vol_handler_types[5],
#   'Эмульсия':         doze_vol_handler_types[5],
#   'Лиофилизат':       doze_vol_handler_types[6],
#   'Порошок':          doze_vol_handler_types[6],
#   'Аэрозоль':         doze_vol_handler_types[7],
#   'Спрей':            doze_vol_handler_types[7],
#   'Гранулы':          doze_vol_handler_types[8],
#   'Микросферы':       doze_vol_handler_types[8],
#   'Губка':            doze_vol_handler_types[9],
#   'Пластырь':         doze_vol_handler_types[9],
#   'Система':          doze_vol_handler_types[10],
#   'Напиток':          doze_vol_handler_types[11],
#   'Питание':          doze_vol_handler_types[11],
#   'Смесь':            doze_vol_handler_types[11],
#   'ph_f_undefined':   doze_vol_handler_types[-1]
# }

# vol_units_groups = {
#     0: {'ptn':        None,
#         'ru_name' :   None},
#     1: {'ptn':        ['г', 'g', 'gr', 'мл','ml', 'гр\.*', 'л' ],},
#     2: {'ptn':        ['л', 'дм3']},
#     3: {'ptn':        ['мл'],},
#     4: {'ptn':        ['мл', 'г', 'ml', 'гр', 'млфл'],},
#     5: {'ptn':        ['мл', 'ml',
#                        'кг', 'г', 'kg', 'gr\.*','g',  'л\.*,*', 'Л', 'l',  'Л\.*', 'литров', 'dose', 'д\.*'],
#         # 1) если стоит одно число (без ед. измер дозировки и объема) - то это объем 2) если есть дозировка + ед. измер дозировки, потом число - то это объем
#         },
#     6: {'ptn':        None,
#         'ru_name' :   None},
#     7: {'ptn':        ['мл', 'ml', 'доз', 'доза', 'dos', 'doz', 'dosa', 'doza', 'd', 'г', #'g',
#                        'дз', 'гр', 'g\.*', #05/10/2022
#                        ],
#         },
#     8: {'ptn':        ['г','g'],
#         'ru_name' :   None},
#     9: {'ptn':        None,
#         'ru_name' :   None},
#     10: {'ptn':        None,
#         'ru_name' :   None},
#     11: {'ptn':        ['г', 'мл', 'л', 'ml'],
#         'ru_name' :   ['г', 'мл', 'л']},
#     -1: {'ptn':       ['г', 'g', 'gr', 'мл']+['л', 'дм3']+['мл']+['мл', 'г', 'ml', 'гр', 'млфл']+['мл', 'ml']+\
#          ['мл', 'ml', 'доз', 'доза', 'dos', 'doz', 'dosa', 'doza', 'd', 'г', 'g']+ ['г', 'мл', 'л'],
#         },
# }
# doze_units_groups = {
#     0: {'ptn' :       ['мг', 'г', 'mg', 'мкг', 'mkg', 'g', 'ЕД', 'ED', 'gr', 'МЕ', 'тыс\.* МЕ', 'тыс\.*МЕ', 'тыс МЕ', 'гр\.*', 'доз',
#                        'ЛЕ', 'тыс\.* *ед\.*', 'ЕD', 'LE', 'тыс\.* *ЕД', 'тыс\.* *ЕД', 'ME', # 04/10/2022
#                        ],
#         },
#     1: {'ptn':        ['мг/г', 'mg/g', 'mg/gr', 'Ед/г', 'мг', 'mg', 'Ед',
#                        'МЕ/г ', 'g/ml ', 'МЕ/Г', 'g/gr', 'мг/мл', # 04/10/2022
#                       ],
#         },
#     2: {'ptn':        ['м3'],
#         'ru_name' :   ['м3'] },
#     3: {'ptn':        None,
#         'ru_name' :   None},
#     4: {'ptn':        None,
#         'ru_name' :   None},
#     5: {'ptn':        unit_slash_combination([['тыс\.* *анти-*Ха *МЕ', #'тыс.анти-Xa МЕ', 'тыс.анти-XaМЕ', 'тыс.анти-Ха МЕ', 
#             'Anti-*Xa MЕ',  'ANTI-*HA *МЕ', 
#          'ТЫС\.* *МЕ АНТИ-*ХА', 'МЕ *\(анти-*Ха\)', 'МЕ *анти-*Ха',   # 'anti-XA ME', 'anti-Ха ME', 'МЕ(анти-Ха)',
#          'анти/ХА *ME', 'анти-*Xa *МЕ', 'анти-*ХА *МЕ', 'АНТИ-*ХА', # 'анти-XА МЕ',
#           'mln *ME', 'mln\.*Ed', 'PNU', 
#            'ЕD', 'ЕД', 'КИЕ', 'Е',
#           'млн\.* *МЕ', 'млн\.* *ЕД', 'тыс\.* *МЕ',  # 'млн. МЕ',  'млн ЕД',
#           'МЕ', 'ME', 'ЛЕ', 'LE'], ['мл','ml']])+\
#         unit_slash_combination([[ 'мкмоль', 'ммоль', 'mmol', 'ккал',  'мг', 'mg', 'мкг', 'Г','mkg', 'мгк','mgk', 
#                                               'mg-*iodi', 'mg iodi', 'mg ioda', 'мг йода'],  
#                                 ['мл','ml']])+\
#         unit_slash_combination([['мг', 'мкг', 'mg', 'mkg', 'ml'], ['доза', 'доз', 'doza', 'doz', 'dosa', 'dose', 'dos', 'd\.*', 'д\.*']])+\
#         ['мл/мл', 'ml/ml', 'ml/мл', 'мл/ml'], # исключения переводим потом в мг/мл,
#         # [],
#         #'%',
#         },

#     6: {'ptn':        ['мг/доза', 'мг/доз', 'мг/doza', 'мг/doz', 'мг/dosa', 'мг/dos', 'мг/d\.*', 'мг/d', 'мкг/доза', 'мкг/доз', 
#                        'мкг/doza', 'мкг/doz', 'мкг/dosa', 'мкг/dos', 'мкг/d\.*', 'мкг/d', 
#                        'mg/доза', 'mg/доз', 'mg/doza', 'mg/doz', 'mg/dosa', 'mg/dos', 'mg/d\.*', 'mg/d', 'mkg/доза', 'mkg/доз', 'mkg/doza', 'mkg/doz', 
#                        'mkg/dosa', 'mkg/dos', 'mkg/d\.*', 'mkg/d', 
#                        'МЕ/доза', 'МЕ/доз', 'МЕ/doza', 'МЕ/doz', 'МЕ/dosa', 'МЕ/dos', 'МЕ/d\.*', 'МЕ/d', 
#                        'ME/доза', 'ME/доз', 'ME/doza', 'ME/doz', 'ME/dosa', 'ME/dos', 'ME/d\.*', 'ME/d',
#                        'тыс\.* *АТрЕ', 'тыс\.* *ЕД', 'тыс\.* *МЕ',
#                        'мкл/мл', 'млн *ЕД', 'млн\.* *ЕД', 'млн\.* *КОЕ', 'млн\.* *МЕ','млнМЕ',  
#                        'mln *ED', 'mln *KOE', 'MlnME', 'млн.КОЕ',
#                        'УЕ',
#                        'мг', 'mg', 'ЕД', 'ED', 'г', 'g', 'МЕ', 'ME', 'гр', 'gr\.*', 'gr', 'мкг', 'mkg',
#                        'ATpE',  'KOE',  'АТрЕ',  
                       

#           # ('мг', 'мкг', 'mg', 'mkg', 'МЕ', 'ME'), ('доза', 'доз', 'doza', 'doz', 'dosa', 'dos', 'd.', 'd')
#                        ],
#         'ru_name' :   ['мг', 'мг', 'ЕД', 'ЕД', 'г', 'г', 'МЕ', 'МЕ', 'г', 'г', 'мкг', 'мкг']},
#     7: {'ptn':        ['мг', 'mg', 'mkg',
#                        'мг/мл', 'mg/ml', 'мкг/мл', 'mkg/ml',
#                        'мг/доза', 'мкг/доза', 'mg/doza', 'mg/dosa', 'mg/доза',  'mkg/doza', 'mkg/doz','mkg/dosa*',  'mkg/доза', 'mkg/d\.*',
#                        'mg/dos\.*', 'mg/dos\.*', 'мг/д\.*',   #'mkg\\dosa', 'mg\\dos.',
#                        'g/g',   #05/10/2022
#                        'МЕ/доза',
#                        ],
#         #'%',
#         'ru_name' :   ['мг/доза', 'мг/доза', 'мг/доза', 'мг/доза', 'мкг/доза', 'мкг/доза', 'мкг/доза', 'мкг/доза', 
#                        'мг/мл', 'мг/мл', 'мкг/мл', 'мкг/мл', 'мг', 'мг', 'мкг/доза', 'мг/доза']},
#     8: {'ptn':        ['мг', 'ЕД', 'мг/мл', 'г\.*', 'g', 'mg', 'тыс\.* *ЕД'],
#         'ru_name' :   None},
#     9: {'ptn':        ['мкг/час', 'мкг/часа'], # 'МКГ/ЧАС', 
#         'ru_name' :   None},
#     10: {'ptn':       ['мкг/час', 'мкг/часа'], # 'МКГ/ЧАС', 
#         'ru_name' :   None},
#     11: {'ptn':       None,
#         'ru_name' :   None},
#     -1: {'ptn':       ['мг', 'г', 'mg', 'мкг', 'mkg', 'g', 'ЕД', 'ED', 'gr', 'МЕ', 'тыс\. МЕ', 'тыс\.МЕ', 'тыс МЕ', 'гр\.*', 'доз']+\
#                       ['%', 'мг/г', 'mg/g', 'mg/gr', 'Ед/г', 'мг', 'mg', 'Ед']+ ['м3']+ \
#                       ['мг/мл', 'mg/ml', 'мг', 'mg', 'мкг', 'mkg', 'мкг/мл', 'mkg/ml', 'МЕ/мл', 'ME/ml', 'ЕД/мл', 'ED/ml', 
#                        'МЕ', 'ME', '%', 'анти-*ХА *МЕ/мл', 'анти-*ХА *МЕ', 'Анти-*Ха/мл', 'тыс.анти-*Ха *МЕ', 'Анти-*Ха МЕ/ml', r'МЕ \(анти-*Ха\)/ml', 
#                        'доз', 'мг/г', 'мл/доза', 'МЕ/мл',
#                        'anti-*Ha *ME', 'anti-*Hа *ME/мл']+\
#                       ['мг', 'mg', 'ЕД', 'ED', 'г', 'g', 'МЕ', 'ME', 'гр', 'gr', 'мкг', 'mkg']+\
#                       ['мг/доза', 'mg/doza', 'mg/dosa', 'mg/доза', 'мкг/доза', 'mkg/doza', 'mkg/dosa', 'mkg/d', 
#                        'мг/мл', 'mg/ml', 'мкг/мл', 'mkg/ml', 'мг', 'mg', '%', 'mkg/dosa', 'mg/dos\.*'],
#         'ru_name' :   None}
# }

# units_total_lst = []
# for i, (k, v) in enumerate(doze_units_groups.items()):
#     #ptn_digits = r'(((\d+,\d+|\d+\.\d+|\d+)\s*((тыс)(.)*)*)\s*)'
#     #ptn_digits = r'(?P<digits>\.*,*(\d+,\d+|\d+\.\d+|\d+))'
#     ptn_digits = r'(?P<digits>((\d+,\d+)|(\d+\.\d+)|(\d+))\s*((тыс)(\.|,)*)*\s*)'
#     ptn_digits = r'(?P<digits>((\d+,\d+)|(\d+\.\d+)|(\d+)))'
#     #print(k,v)
#     if doze_vol_handler_types[k][1]: # есть is_dosed
#         if v['ptn'] is not None:
#             doze_units_groups[k]['ptn_str'] = make_doze_ptn_str(v['ptn'])
#             doze_units_groups[k]['cmplx_ptn_str'] = make_complex_doze_ptn_str(v['ptn'])
#             units_total_lst.extend(v['ptn'])
#         else: 
#             doze_units_groups[k]['ptn_str'] = None
#             doze_units_groups[k]['cmplx_ptn_str'] = None
#     #if i >2: break
# for i, (k, v) in enumerate(vol_units_groups.items()):
#     ptn_digits = r'(?P<digits>(\d+,\d+)|(\d+\.\d+)|([\d\s]+\d+)|(\d+))'
#     if doze_vol_handler_types[k][3]: # есть is_vol 
#         if v['ptn'] is not None:
#             vol_units_groups[k]['ptn_str'] = make_vol_ptn_str(v['ptn'])
#             units_total_lst.extend(v['ptn'])
#         else: 
#             vol_units_groups[k]['ptn_str'] = None

# def make_combinations_by_punct_01(lst, delimiter):
#     if delimiter is None or '*' not in delimiter: return lst
#     u1_split = []
#     for u0 in lst:
#         s_lst = u0.split(delimiter)
#         u1_split.extend([''.join(s_lst), re.sub(r"\*",'', delimiter).join(s_lst)])
#     return u1_split
# make_combinations_by_punct_01([r'anti-*ha\.* *ме/мл'], r'-*')    
# def make_combinations_by_punct(lst):
#     lst_01 = make_combinations_by_punct_01(lst, r'-*')
#     # print(lst_01)
#     lst_02 = make_combinations_by_punct_01(lst_01, r'\.*')
#     # print(lst_02)
#     lst_03 = make_combinations_by_punct_01(lst_02, r' *')
#     lst_04 = make_combinations_by_punct_01(lst_03, r',*')
#     lst_04 = make_combinations_by_punct_01(lst_04, r'a*')
#     return lst_04

# v 24/11/2022
# v 23/11/2022
# v 22/11/2022
units_total_dict = {'%': '%',
 'anti-ha me': 'анти-Ха МЕ',
 'anti-ha ме': 'анти-Ха МЕ',
 'anti-xa me': 'анти-Ха МЕ',
 # 'anti-xA me': 'анти-Ха МЕ',
 'anti-hame': 'анти-Ха МЕ',
 'anti-haме': 'анти-Ха МЕ',
 'anti-hа me': 'анти-Ха МЕ',
 'anti-hаme': 'анти-Ха МЕ',
 'anti-xa mе': 'анти-Ха МЕ',
 'anti-ха me': 'анти-Ха МЕ',
 'antiha me': 'анти-Ха МЕ',
 'antiha ме': 'анти-Ха МЕ',
 'анти-xа ме': 'анти-Ха МЕ',
 'antihame': 'анти-Ха МЕ',
 'antihaме': 'анти-Ха МЕ',
 'antihа me': 'анти-Ха МЕ',
 'antihаme': 'анти-Ха МЕ',
 'antixa mе': 'анти-Ха МЕ',
 'ме  анти-ха': 'анти-Ха МЕ',       
 'анти': 'анти-Ха МЕ',
 'анти-xa ме': 'анти-Ха МЕ',
 'анти-xaме': 'анти-Ха МЕ',
 'анти-ха': 'анти-Ха МЕ',
 'анти-ха ме': 'анти-Ха МЕ',
 'анти-хаме': 'анти-Ха МЕ',
 'антиxa ме': 'анти-Ха МЕ',
 'антиxaме': 'анти-Ха МЕ',
 'антиха': 'анти-Ха МЕ',
 'антиха ме': 'анти-Ха МЕ',
 'антихаме': 'анти-Ха МЕ',
 'ме': 'МЕ',
 'mе': 'МЕ',
 'ме (анти-ха)': 'анти-Ха МЕ',
 'ме (антиха)': 'анти-Ха МЕ',
 'ме анти-ха': 'анти-Ха МЕ',
 'ме антиха': 'анти-Ха МЕ',
 'ме(анти-ха)': 'анти-Ха МЕ',
 'ме(антиха)': 'анти-Ха МЕ',
 'меанти-ха': 'анти-Ха МЕ',
 'меантиха': 'анти-Ха МЕ',
 'тысме анти-ха': 'тыс. анти-Xa МЕ',
 'тысме антиха': 'тыс. анти-Xa МЕ',
 
 'ха me': 'анти-Ха МЕ',
 'хаme': 'анти-Ха МЕ',
 'тыс анти-ха ме': 'тыс. анти-Ха МЕ',
 'тыс антиха ме': 'тыс. анти-Ха МЕ',
 'тыс.анти-ха ме': 'тыс. анти-Ха МЕ', 
 'тыс.анти-xaме': 'тыс. анти-Ха МЕ', 
 'тыс.ме анти-ха': 'тыс. анти-Ха МЕ', 
 'тыс ме': 'тыс. МЕ',
 'тыс.ме': 'тыс. МЕ',
 'тыс. ме': 'тыс. МЕ',
 'тыс ме анти-ха': 'тыс. анти-Ха МЕ',
 'тыс ме антиха': 'тыс. анти-Ха МЕ',
 'тысанти-ха ме': 'тыс. анти-Ха МЕ',
 'тысанти-хаме': 'тыс. анти-Ха МЕ',
 'тысантиха ме': 'тыс. анти-Ха МЕ',
 'тысантихаме': 'тыс. анти-Ха МЕ',
 'тыс. анти-ха ме': 'тыс. анти-Ха МЕ',
 'тыс.анти-xa ме': 'тыс. анти-Ха МЕ',
                    
 'atpe': 'АТрЕ',
 'd': 'доз(а)',
 'd': 'доз(а)',
 'dos': 'доз(а)',
 'dosa': 'доз(а)',
 'dose': 'доз(а)',
 'doz': 'доз(а)',
 'doza': 'доз(а)',
 'ed': 'ЕД',
 'e': 'ЕД',
 'е': 'ЕД',
 'еd': 'ЕД',
 'ед': 'ЕД',
 'eд': 'ЕД',
                    
 'тысед': 'тыс. ЕД',
 'тыс.ед': 'тыс. ЕД',
 'mln ed': 'млн. ЕД',
 'mlned': 'млн. ЕД',
 'mln.ed': 'млн. ЕД',
 # 'млн.ЕД': 'млн. ЕД',
 'млн ед': 'млн. ЕД', 
 'млн.ед': 'млн. ЕД',
 'млн. ед': 'млн. ЕД',
 'млн. ЕД': 'млн. ЕД',
 'тыс ед': 'тыс. ЕД',
 'тыс.ед': 'тыс. ЕД',
 'тыс. ед': 'тыс. ЕД',
 'тыс.ед.': 'тыс. ЕД',        
 'тыс. ед.': 'тыс. ЕД',        
 'млнед': 'млн. ЕД',
 # 'уе': 'УЕ',
 'уе': 'ЕД',
 'тысуе': 'тыс. ЕД',
 'тыс уе': 'тыс. ЕД',
 'тыс.уе': 'тыс. ЕД',
 'тыс. уе': 'тыс. ЕД',
 'млнуе': 'млн. ЕД',
 'млн.уе': 'млн. ЕД',
 'млн. уе': 'млн. ЕД',
 'млн уе': 'млн. ЕД',

 'g': 'г',
 'gr': 'г',
 'gr.': 'г',
 'г': 'г',
 'гр': 'г',
 'гр.': 'г',
 'kg': 'кг',
 'koe': 'КОЕ',

 'le': 'ЛЕ',
 'ле': 'ЛЕ',                    
 'me': 'МЕ',
 'тысме': 'тыс. МЕ',
 'тыс.ме': 'тыс. МЕ',
 'mlnme': 'млн. МЕ',
 'mln me': 'млн. МЕ',
 'mln. me': 'млн. МЕ',                    
 'млн.МЕ': 'млн. МЕ',
 'млн.ме': 'млн. МЕ',
 'млн.ме': 'млн. МЕ',
 'млн.ме': 'млн. МЕ',
 'млн. ме': 'млн. МЕ',
                    
                    
 'mg': 'мг',
 'мг': 'мг',
 # 'mg ioda': 'мг йода',
 # 'mg iodi': 'мг йода',
 # 'mg-iodi': 'мг йода',
 # 'mgiodi': 'мг йода',
 # 'мг йода': 'мг йода',                        
 'mg ioda': 'мг',
 'mg iodi': 'мг',
 'mg-iodi': 'мг',
 'mgiodi': 'мг',
 'мг йода': 'мг',                        
                    
 'mgk': 'мкг',
 'mkg': 'мкг',
 'l': 'л',
 'ml': 'мл',
 'мл' : 'мл',
 'mln koe': 'млн. КОЕ',
 'млн. кое': 'млн. КОЕ',
 'млн.кое': 'млн. КОЕ',
 'млн кое': 'млн. КОЕ',
 'mlnkoe': 'млн. КОЕ',
 'mmol': 'ммоль',
 'pnu': 'PNU',
                    
 'атре': 'АТрЕ',
 'д': 'доз(а)',
 'дз': 'доз(а)',
 'дм3': 'дм3',
 'доз': 'доз(а)',
 'доза': 'доз(а)',
 'доз(а)': 'доз(а)',

 'кг': 'кг',
 'кие': 'КИЕ',
 'kие': 'КИЕ',
 'ккал': 'ккал',
 'л': 'л',
 'л,': 'л',

 'литров': 'л',
 'м3': 'м3',
 'мг': 'мг',
 'мг йода': 'мг',
 'мгк': 'мкг',
                   
 'мкг': 'мкг',
 'мкл': 'мкл',
 'мкмоль': 'мкмоль',
 'мл': 'мл',

 'млн кое': 'млн. КОЕ',
 'млн ме': 'млн. МЕ',

 'млнкое': 'млн. КОЕ',
 'млн.кое': 'млн. КОЕ',
 'млнме': 'млн. МЕ',
 'млфл': 'мл',
 'ммоль': 'ммоль',
 
 'тыс атре': 'тыс. АТрЕ',
 'тысатре': 'тыс. АТрЕ',
 'тыс.атре': 'тыс. АТрЕ',

 
 'ч': 'час',
 'ч.': 'час',
 'час': 'час',
 'часа': 'часа'
 }
# v 21/11/2022
# units_total_dict = {'%': '%',
#  'anti-ha me': 'анти-Ха МЕ',
#  'anti-ha ме': 'анти-Ха МЕ',
#  'anti-hame': 'анти-Ха МЕ',
#  'anti-haме': 'анти-Ха МЕ',
#  'anti-hа me': 'анти-Ха МЕ',
#  'anti-hаme': 'анти-Ха МЕ',
#  'anti-xa mе': 'анти-Ха МЕ',
#  'antiha me': 'анти-Ха МЕ',
#  'antiha ме': 'анти-Ха МЕ',
#  'antihame': 'анти-Ха МЕ',
#  'antihaме': 'анти-Ха МЕ',
#  'antihа me': 'анти-Ха МЕ',
#  'antihаme': 'анти-Ха МЕ',
#  'antixa mе': 'анти-Ха МЕ',
#  'atpe': 'АТрЕ',
#  'd': 'доз(а)',
#  'dos': 'доз(а)',
#  'dosa': 'доз(а)',
#  'dose': 'доз(а)',
#  'doz': 'доз(а)',
#  'doza': 'доз(а)',
#  'ed': 'ЕД',
#  'g': 'г',
#  'gr': 'г',
#  'kg': 'кг',
#  'koe': 'КОЕ',
#  'l': 'л',
#  'le': 'ЛЕ',
#  'me': 'ЛЕ',
#  'mg': 'мг',
#  'мг': 'мг',
#  'mg ioda': 'мг йода',
#  'mg iodi': 'мг йода',
#  'mg-iodi': 'мг йода',
#  'mgiodi': 'мг йода',
#  'mgk': 'мкг',
#  'mkg': 'мкг',
#  'ml': 'мл',
#  'мл' : 'мл',
#  'mln ed': 'млн. ЕД',
#  'mln koe': 'млн. КОЕ',
#  'mln me': 'млн. МЕ',
#  'mlned': 'млн. ЕД',
#  'mlnkoe': 'млн. КОЕ',
#  'mlnme': 'млн. МЕ',
#  'mmol': 'ммоль',
#  'pnu': 'PNU',
#  'анти': 'анти-Ха МЕ',
#  'анти-xa ме': 'анти-Ха МЕ',
#  'анти-xaме': 'анти-Ха МЕ',
#  'анти-ха': 'анти-Ха МЕ',
#  'анти-ха ме': 'анти-Ха МЕ',
#  'анти-хаме': 'анти-Ха МЕ',
#  'антиxa ме': 'анти-Ха МЕ',
#  'антиxaме': 'анти-Ха МЕ',
#  'антиха': 'анти-Ха МЕ',
#  'антиха ме': 'анти-Ха МЕ',
#  'антихаме': 'анти-Ха МЕ',
#  'атре': 'АТрЕ',
#  'г': 'г',
#  'гр': 'г',
#  'д': 'доз(а)',
#  'дз': 'доз(а)',
#  'дм3': 'дм3',
#  'доз': 'доз(а)',
#  'доза': 'доз(а)',
#  'доз(а)': 'доз(а)',
#  'e': 'ЕД',
#  'е': 'ЕД',
#  'еd': 'ЕД',
#  'ед': 'ЕД',
#  'кг': 'кг',
#  'кие': 'КИЕ',
#  'ккал': 'ккал',
#  'л': 'л',
#  'л,': 'л',
#  'ле': 'ЛЕ',
#  'литров': 'л',
#  'м3': 'м3',
#  'мг': 'мг',
#  'мг йода': 'мг',
#  'мгк': 'мкг',
#  'ме': 'МЕ',
#  'ме (анти-ха)': 'анти-Ха МЕ',
#  'ме (антиха)': 'анти-Ха МЕ',
#  'ме анти-ха': 'анти-Ха МЕ',
#  'ме антиха': 'анти-Ха МЕ',
#  'ме(анти-ха)': 'анти-Ха МЕ',
#  'ме(антиха)': 'анти-Ха МЕ',
#  'меанти-ха': 'анти-Ха МЕ',
#  'меантиха': 'анти-Ха МЕ',
#  'мкг': 'мкг',
#  'мкл': 'мкл',
#  'мкмоль': 'мкмоль',
#  'мл': 'мл',
#  'млн ед': 'млн. ЕД',
#  'млн кое': 'млн. КОЕ',
#  'млн ме': 'млн. МЕ',
#  'млнед': 'млн. ЕД',
#  'млнкое': 'млн. КОЕ',
#  'млн.кое': 'млн. КОЕ',
#  'млнме': 'млн. МЕ',
#  'млфл': 'мл',
#  'ммоль': 'ммоль',
#  'тыс анти-ха ме': 'тыс. анти-Ха МЕ',
#  'тыс антиха ме': 'тыс. анти-Ха МЕ',
#  'тыс атре': 'тыс. АТрЕ',
#  'тыс ед': 'тыс. ЕД',
#  'тыс ме': 'тыс. МЕ',
#  'тыс ме анти-ха': 'тыс. анти-Ха МЕ',
#  'тыс ме антиха': 'тыс. анти-Ха МЕ',
#  'тысанти-ха ме': 'тыс. анти-Ха МЕ',
#  'тысанти-хаме': 'тыс. анти-Ха МЕ',
#  'тысантиха ме': 'тыс. анти-Ха МЕ',
#  'тысантихаме': 'тыс. анти-Ха МЕ',
#  'тысатре': 'тыс. АТрЕ',
#  'тысед': 'тыс. ЕД',
#  'тысме': 'тыс. МЕ',
#  'тысме анти-ха': 'тыс. анти-Xa МЕ',
#  'тысме антиха': 'тыс. анти-Xa МЕ',
#  'уе': 'УЕ',
#  'ха me': 'анти-Ха МЕ',
#  'хаme': 'анти-Ха МЕ',
#  'час': 'час',
#  'часа': 'часа'
#  }

s = '''КИЕ,КИЕ,1
анти-Ха МЕ,анти-Ха ЕД,1
кг,г,1000
тыс. анти-Xa МЕ,анти-Ха ЕД,1000
мкмоль,мкмоль,1
м3,м3,1
АТрЕ,АТрЕ,1
ммоль,ммоль,1
тыс. АТрЕ,АТрЕ,1000
ккал,ккал,1
дм3,м3,0.1
мл,мл,1
тыс. ЕД,ЕД,1000
млн. МЕ,МЕ,1000000
мг йода,мг,1
КОЕ,КОЕ,1
МЕ,МЕ,1
часа,ч,1
тыс. анти-Ха МЕ,анти-Ха ЕД,1000
PNU,ЕД,1
мкг,мг,0.001
л,л,1
мг,мг,1
млн. КОЕ,КОЕ,1000000
доз(а),доза,1
г,мг,1000
ЛЕ,ЕД,1
млн. ЕД,ЕД,1000000
час,ч,1
тыс. МЕ,МЕ,1000
мкл,мкл,1
ЕД,ЕД,1'''
ss = s.split('\n')
ss = [s.split(',') for s in ss]
recalc_doze_units_dict = {s[0] : {'base_unit': s[1], 'k': float(s[2])} for s in ss}
# print(recalc_doze_units_dict.get ('тыс. анти-Xa МЕ'))
# recalc_doze_units_dict 
# ss = s.split('\n')
# ss = [s.split(',') for s in ss]
# recalc_doze_units_dict = {s[0] : {'base_unit': s[1], 'k': float(s[2])} for s in ss}
# recalc_doze_units_dict 
# recalc_doze_units_dict.get ('тыс. анти-Xa МЕ')

# base_doze_unit_esklp = [v['base_unit'] for v in recalc_doze_units_dict.values()]
# base_doze_unit_esklp = {v: v for v in base_doze_unit_esklp}
# base_doze_unit_esklp
base_doze_unit_esklp = [v['base_unit'] for v in recalc_doze_units_dict.values()]
base_doze_unit_esklp = {v: v for v in base_doze_unit_esklp}
base_doze_unit_esklp
base_doze_unit_esklp = {'КИЕ': {'base_unit': 'КИЕ', 'k': 1.0},
 'анти-Ха ЕД': {'base_unit': 'анти-Ха ЕД', 'k': 1.0},
 'анти-Ха МЕ': {'base_unit': 'анти-Ха ЕД', 'k': 1.0},
 'г': {'base_unit': 'мг', 'k': 1000.0},
 'мг': {'base_unit': 'мг', 'k': 1.0},
 'мг йода': {'base_unit': 'мг', 'k': 1.0},
 'мкг': {'base_unit': 'мг', 'k': 0.001},
 'мкмоль': {'base_unit': 'мкмоль', 'k': 1.0},
 'м3': {'base_unit': 'м3', 'k': 1.0},
 'дм3': {'base_unit': 'м3', 'k': 0.1},
 'АТрЕ': {'base_unit': 'АТрЕ', 'k': 1.0},
 'ммоль': {'base_unit': 'ммоль', 'k': 1.0},
 'ккал': {'base_unit': 'ккал', 'k': 1.0},
 'мл': {'base_unit': 'мл', 'k': 1.0},
 'ЕД': {'base_unit': 'ЕД', 'k': 1.0},
 'МЕ': {'base_unit': 'ЕД', 'k': 1.0},
 'ЛЕ': {'base_unit': 'ЕД', 'k': 1.0},
 'мг': {'base_unit': 'мг', 'k': 1.0},
 'КОЕ': {'base_unit': 'КОЕ', 'k': 1.0},
 'PNU': {'base_unit': 'ЕД', 'k': 1.0},
 'ч': {'base_unit': 'ч', 'k': 1.0},
 'час': {'base_unit': 'ч', 'k': 1.0},
 'л': {'base_unit': 'мл', 'k': 1000.0},
 'доза': {'base_unit': 'доза', 'k': 1.0},
 'доз(а)': {'base_unit': 'доза', 'k': 1.0},
 'мкл': {'base_unit': 'мкл', 'k': 1.0},
 
    }

base_vol_unit_esklp = {'КИЕ': {'base_unit': 'КИЕ', 'k': 1.0},
 'анти-Ха ЕД': {'base_unit': 'анти-Ха ЕД', 'k': 1.0},
 'анти-Ха МЕ': {'base_unit': 'анти-Ха ЕД', 'k': 1.0},
 # 'г': {'base_unit': 'мг', 'k': 1000.0},
 'г': {'base_unit': 'г', 'k': 1.0},
 'мг': {'base_unit': 'мг', 'k': 1.0},
 'мг йода': {'base_unit': 'мг', 'k': 1.0},
 'мкг': {'base_unit': 'мг', 'k': 0.001},
 'мкмоль': {'base_unit': 'мкмоль', 'k': 1.0},
 'м3': {'base_unit': 'м3', 'k': 1.0},
 'дм3': {'base_unit': 'м3', 'k': 0.1},
 'АТрЕ': {'base_unit': 'АТрЕ', 'k': 1.0},
 'ммоль': {'base_unit': 'ммоль', 'k': 1.0},
 'ккал': {'base_unit': 'ккал', 'k': 1.0},
 'мл': {'base_unit': 'мл', 'k': 1.0},
 'ЕД': {'base_unit': 'ЕД', 'k': 1.0},
 'МЕ': {'base_unit': 'ЕД', 'k': 1.0},
 'ЛЕ': {'base_unit': 'ЕД', 'k': 1.0},
 'мг': {'base_unit': 'мг', 'k': 1.0},
 'КОЕ': {'base_unit': 'КОЕ', 'k': 1.0},
 'PNU': {'base_unit': 'ЕД', 'k': 1.0},
 'ч': {'base_unit': 'ч', 'k': 1.0},
 'час': {'base_unit': 'ч', 'k': 1.0},
 'л': {'base_unit': 'мл', 'k': 1000.0},
 'доза': {'base_unit': 'доз(а)', 'k': 1.0},
 'доз(а)': {'base_unit': 'доз(а)', 'k': 1.0},
 'мкл': {'base_unit': 'мкл', 'k': 1.0},
     }

base_pseudo_vol_unit_esklp = {'КИЕ': {'base_unit': 'КИЕ', 'k': 1.0},
 'анти-Ха ЕД': {'base_unit': 'анти-Ха ЕД', 'k': 1.0},
 'анти-Ха МЕ': {'base_unit': 'анти-Ха ЕД', 'k': 1.0},
 # 'г': {'base_unit': 'мг', 'k': 1000.0},
 'г': {'base_unit': 'г', 'k': 1.0},
 'мг': {'base_unit': 'мг', 'k': 1.0},
 'мг йода': {'base_unit': 'мг', 'k': 1.0},
 'мкг': {'base_unit': 'мг', 'k': 0.001},
 'мкмоль': {'base_unit': 'мкмоль', 'k': 1.0},
 'м3': {'base_unit': 'м3', 'k': 1.0},
 'дм3': {'base_unit': 'м3', 'k': 0.1},
 'АТрЕ': {'base_unit': 'АТрЕ', 'k': 1.0},
 'ммоль': {'base_unit': 'ммоль', 'k': 1.0},
 'ккал': {'base_unit': 'ккал', 'k': 1.0},
 'мл': {'base_unit': 'мл', 'k': 1.0},
 'ЕД': {'base_unit': 'ЕД', 'k': 1.0},
 'МЕ': {'base_unit': 'ЕД', 'k': 1.0},
 'ЛЕ': {'base_unit': 'ЕД', 'k': 1.0},
 'мг': {'base_unit': 'мг', 'k': 1.0},
 'КОЕ': {'base_unit': 'КОЕ', 'k': 1.0},
 'PNU': {'base_unit': 'ЕД', 'k': 1.0},
 'ч': {'base_unit': 'ч', 'k': 1.0},
 'час': {'base_unit': 'ч', 'k': 1.0},
 'л': {'base_unit': 'мл', 'k': 1000.0},
 'доза': {'base_unit': 'доза', 'k': 1.0},
 'доз(а)': {'base_unit': 'доза', 'k': 1.0},
 'мкл': {'base_unit': 'мкл', 'k': 1.0},
     }
