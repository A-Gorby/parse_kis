import ipywidgets as widgets
from ipywidgets import Layout, Box, Label
import os
import pandas as pd

# global fn_kis_file_drop_douwn, sheet_name_drop_down, col_name_drop_douwn, data_kis_source_dir

# def form_param_kis(fn_list, data_kis_source_dir):
def form_param_kis(fn_list):
    fn_kis_file_drop_douwn = widgets.Dropdown( options=fn_list, value=None) #fn_list[0] if len(fn_list) > 0 else None, disabled=False)
    sheet_name_drop_down = widgets.Dropdown( options= [None], value= None, disabled=False)
    col_name_drop_down = widgets.Dropdown( options= [None], value= None, disabled=False)
    # fn_dict_file_drop_douwn = widgets.Dropdown( options= [None] + fn_list, value= None, disabled=False, )
    # radio_btn_big_dict = widgets.RadioButtons(options=['Р”Р°', 'РќРµС‚'], value= 'Р”Р°', disabled=False) # description='Check me',    , indent=False
    # radio_btn_prod_options = widgets.RadioButtons(options=['Р”Р°', 'РќРµС‚'], value= 'РќРµС‚', disabled=False if radio_btn_big_dict.value=='Р”Р°' else True )
    # similarity_threshold_slider = widgets.IntSlider(min=1,max=100, value=90)
    # max_entries_slider = widgets.IntSlider(min=1,max=5, value=4)
    # max_out_values_slider = widgets.IntSlider(min=1,max=10, value=4)

    form_item_layout = Layout(display='flex', flex_flow='row', justify_content='space-between')
    fn_select_box = Box([Label(value="Выберите Excel-файл с данными КИС:"), fn_kis_file_drop_douwn], layout=form_item_layout) 
    sheet_select_box = Box([Label(value='Выберите лист Excel-файла:'), sheet_name_drop_down], layout=form_item_layout) 
    column_select_box = Box([Label(value='Выберите колонку с наименование ЛП из КИС:'), col_name_drop_down], layout=form_item_layout) 
    # big_dict_box = Box([Label(value='РСЃРїРѕР»СЊР·РѕРІР°С‚СЊ Р±РѕР»СЊС€РёРµ СЃРїСЂР°РІРѕС‡РЅРёРєРё:'), radio_btn_big_dict], layout=form_item_layout) 
    # prod_options_box = Box([Label(value='РСЃРєР°С‚СЊ РІ Р’Р°СЂРёР°РЅС‚Р°С… РёСЃРїРѕР»РЅРµРЅРёСЏ (+10 РјРёРЅ):'), radio_btn_prod_options], layout=form_item_layout) 
    # similarity_threshold_box = Box([Label(value='РњРёРЅРёРјР°Р»СЊРЅС‹Р№ % СЃС…РѕРґСЃС‚РІР° РїРѕР·РёС†РёР№:'), similarity_threshold_slider], layout=form_item_layout) 
    # max_entries_box = Box([Label(value='РњР°РєСЃРёРјР°Р»СЊРЅРѕРµ РєРѕР»-РІРѕ РЅР°Р№РґРµРЅРЅС‹С… РїРѕР·РёС†РёР№:'), max_entries_slider], layout=form_item_layout) 
    # max_out_values_box = Box([Label(value='РњР°РєСЃРёРјР°Р»СЊРЅРѕРµ РєРѕР»-РІРѕ РІС‹РІРѕРґРёРјС‹С… РїРѕР·РёС†РёР№:'), max_out_values_slider], layout=form_item_layout) 
    
    # form_items = [check_box, dict_box, big_dict_box, prod_options_box, similarity_threshold_box, max_entries_box]
    form_items = [fn_select_box, sheet_select_box, column_select_box] #, column_box, similarity_threshold_box, max_entries_box, max_out_values_box]
    
    form_kis = Box(form_items, layout=Layout(display='flex', flex_flow= 'column', border='solid 2px', align_items='stretch', width='50%')) #width='auto'))
    
    # data_kis_source_dir1 = data_kis_source_dir
    # return form_kis, fn_kis_file_drop_douwn, sheet_name_drop_duwn, col_name_drop_down, data_kis_source_dir1
    return form_kis, fn_kis_file_drop_douwn, sheet_name_drop_down, col_name_drop_down

def on_fn_kis_file_drop_down_change(change):
    global sheet_name_drop_down, data_kis_source_dir
    xl = pd.ExcelFile(os.path.join(data_kis_source_dir, change.new))
    sheet_lst = list(xl.sheet_names)
    sheet_name_drop_down.options = sheet_lst 
def on_sheet_name_drop_down_change(change):
    global fn_kis_file_drop_down, sheet_name_drop_down, col_name_drop_down, data_kis_source_dir
    df = pd.read_excel(os.path.join(data_kis_source_dir, fn_kis_file_drop_down.value), sheet_name=change.new) #cols_lst
    cols_lst = list(df.columns)
    # print(cols_lst)
    col_name_drop_down.options = cols_lst      
