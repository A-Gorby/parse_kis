import re
pattern_s_digits = r'(((\d+,\d+|\d+\.\d+|\d+)\s*((тыс)(.)*)*)\s*)'
pattern_s_digits = r'((([\d,\.]+)\s*((тыс)(.)*)*)\s*)'
pattern_s_proc = r"((\d+,\d+|\d+\.\d+|\d+)\s*(\%\s*))"
pattern_s_proc = r"(\%\s*)"
pattern_s_pack_N = r"(((N|№)(\d+,\d+|\d+\.\d+|\d+)\s*))"
pattern_s_pack_N = r"((N|№)*\s)*"
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

pattern_s_unit_01 = '('  \
    + pattern_s_proc  + '|'\
    + pattern_s_anti_ha_me_mil +'|'+ pattern_s_anti_ha_le_mil +'|'+ pattern_s_anti_ha_mil \
    +'|'+ pattern_s_anti_ha_me +'|'+ pattern_s_anti_ha_le +'|'+ pattern_s_me_anti_ha_mil +'|'+ pattern_s_le_anti_ha_mil +'|'\
    + pattern_s_me_anti_ha + '|' + pattern_s_le_anti_ha + '|' + pattern_s_anti_ha + ')'
# 
#+ r"(" + pattern_s_proc + r".+" + pattern_s_pack_N + r")|" + pattern_s_pack_N + '|'\
#pattern_s_anti_ha_me_ml +'|'+ pattern_s_anti_ha_ml +'|'+ pattern_s_anti_ha_me + '|'+ pattern_s_me_anti_ha_ml +'|'+ pattern_s_me_anti_ha_ml +'|'+ \
# есть конфликт паттернов - разносим    
pattern_s_unit_02 = '('  +\
     pattern_s_me_mil +'|'+ pattern_s_le_mil  +'|'+ pattern_s_le  +'|'+ pattern_s_me  +'|'+ pattern_s_mg_mil +'|'\
     + pattern_s_mg +'|'\
     + ')' #+ '|'+ pattern_s_mil
     
     #pattern_s_me_mil +'|'+ pattern_s_le_mil  \
#pattern_s_unit_03 = '('  +\
     #pattern_s_le  +'|'+ pattern_s_me  +'|'+ pattern_s_mg_ml +'|'+ pattern_s_mg     + ')'
pattern_s_01 = pattern_s_digits + pattern_s_unit_01 #+ pattern_s_pack_N + pattern_s_digits + r"*"
pattern_s_02 = pattern_s_digits + pattern_s_unit_02 #+ pattern_s_pack_N + pattern_s_digits + r"*"

pttn_pill_list = [
    r"(?:\b((таблетк[иа]*)|(табл)|(таб)|(тб)|(tab)|(tb))\.*\s*ваг\.)",
    r"(?:\b((таблетк[иа]*)|(табл)|(таб)|(тб)|(tab)|(tb))\.*\s*ваг[инальные]*\.*)",
    r"(?:\b((таблетк[иа]*)|(табл)|(таб)|(тб)|(tab)|(tb))\.* *ретард\.*)",  
    r"(?:\b((таблетк[иа]*)|(табл)|(таб)|(тб)|(tab)|(tb))\.*\s*кишечнораст\.* *об\.*)",
    r"(?:\b((таблетк[иа]*)|(табл)|(таб)|(тб)|(tab)|(tb))\.* *пл*/о кш/раств\.*)",
    r"(?:\b((таблетк[иа]*)|(табл)|(таб)|(тб)|(tab)|(tb))\.* *модиф\.* *высв\.* *пл*/о)",
    r"(?:\b((таблетк[иа]*)|(табл)|(таб)|(тб)|(tab)|(tb))\.* *контр\.* *высв\.* *пл*/о)",
    r"(?:\b((таблетк[иа]*)|(табл)|(таб)|(тб)|(tab)|(tb))\.* *контр\.* *высв\.* *п/плен\.* *об*\.*)",
    r"(?:\b((таблетк[иа]*)|(табл)|(таб)|(тб)|(tab)|(tb))\.* *пл*/о зам\.* высв\.*)",
    r"(?:таблетки,* покрытые пленочной оболочкой)",
    r"(?:таблетки,* покрытые оболочкой)",
    r"(?:\b((таблетк[иа]*)|(табл)|(таб)|(тб)|(tab)|(tb))\.*,* *покрытые пленочной оболочкой)",
    r"(?:\b((таблетк[иа]*)|(табл)|(таб)|(тб)|(tab)|(tb))\.*,* *покр[ытые]*\.*\s*пл[еночной]*\.*\s*об[олочкой]*\.*)",
    r"(?:\b((таблетк[иа]*)|(табл)|(таб)|(тб)|(tab)|(tb)|(та[бд]))\.*,*\s*п*/*пл[ен]*\.*\s*/*о[болоч]*\.*)",
    r"(?:\b((таблетк[иа]*)|(табл)|(таб)|(тб)|(tab)|(tb))\.* *пл[еночной]*\.*\s*об[олочкой]*\.*)",
    r"(?:\b((таблетк[иа]*)|(табл)|(таб)|(тб)|(tab)|(tb))\.*\s*плен/об)",
    r"(?:\b((таблетк[иа]*)|(табл)|(таб)|(тб)|(tab)|(tb))\.*\s*дисперг\b\.*)",
    r"(?:\b((таблетк[иа]*)|(табл)|(таб)|(тб)|(tab)|(tb))\.*\s*пролонг\.* действ\b\.*)",
    r"(?:\b((таблетк[иа]*)|(табл)|(таб)|(тб)|(tab)|(tb))\.*\s*\bшип\b\.*)",
    r"(?:\b((таблетк[иа]*)|(табл)|(таб)|(тб)|(tab)|(tb))\.*.*\bшип\b\.*)",
    r"(?:\b((таблетк[иа]*)|(табл)|(таб)|(тб)|(tab)|(tb))\.*\s*\bжев\b\.*)",
    r"(?:\b((таблетк[иа]*)|(табл)|(таб)|(тб)|(tab)|(tb))\.*.*\bжев\b\.*)",
    r"(?:\b((таблетк[иа]*)|(табл)|(таб)|(тб)|(tab)|(tb))\b(\s*|\.*|$))",
]
pattern_pills = "". join([ s + "|" for s in pttn_pill_list[::1]])[:-1]
# # print(pattern_pills)

pttn_form_solution_list = [r"(?:\bамп\.*\w*\b)",
                      r"(?:\bфл\.*\w*\b)",
                      r"(?:\bбут\.*\w*\b)",
                      r"(?:\bкартр\.*\w*\b)",
                      r"(?:\bшпр\.*\w*\b)",
                      r"(?:\bкапс\.*\w*\b)", #  под вопросом часто не раствор
                      
                  ]
pattern_form_solution = "". join([ s + "|" for s in pttn_form_solution_list[::1]])[:-1]
## # print(pattern_form_solution)
pttn_solution_list = [r"(?:раствор для внутривенного и внутриартериального введения)",
                      r"(?:раствор для внутриполостного введения, местного и наружного применения)",
                      r"(?:раствор для внутривенного введения)",
                      r"(?:((раствор)|(p-p)|(р/р)|(р\.р))\.* *д[ля]* в/в вв[едения]*\.*)", 
                      r"(?:раствор для внутривенного и подкожного введения)",
                      r"(?:раствор для внутривенного и внутримышечного введения)", 
                      r"(?:((раствор)|(p-p*)|(р/р)|(р\.р))\.* *(д[ля/]*)* (в/в)* *и* *(в/м)* *вв[едения]*\.*)", 
                      r"(?:((р-р)|(раствор)|(р/р)(р.р))\.* *(д[ля/]*)* *в/в и в/м)",
                      r"(?:((р-р)|(раствор)|(р/р)(р.р))\.* *(д[ля/]*)* *в/м *и* *п/к)",
                      r"(?:((р-р)|(раствор)|(р/р)(р.р))\.* *(д[ля/]*)* *в/м *и* *п/к)",
                      r"(?:((р-р)|(раствор)|(р/р)(р.р))\.* *(д[ля/]*)* *в/в *и* *подкож\.* введ\.*)", 
                      r"(?:((раствор)|(p-p*)|(р/р)|(р\.р))\.* *(д[ля/]*)* в/в *и* *(в/м)* *вв[едения]*\.*)",
                      r"(?:((р-р)|(раствор)|(р/р)(р.р))\.* *(д[ля/]*)* *в/в введ\.*)",
                      r"(?:раствор для инфузий)",
                      r"(?:раствор для ингаляций)",
                      r"(?:раствор для инъекций и ингаляций)",
                      r"(?:раствор для подкожного введения)",
                      r"(?:раствор.*.* для внутрисосудистого введения)",
                      r"(?:раствор для внутриполостного (введения)* *и* наружного применения)",
                      r"(?:\b((р-р)|(раствор)|(р/р)(р\.р))\.* *д[ля]*/*\.*\s*внутрипол[остного]*\.* вв[едения]*\.* и нар[ужного]*\.* прим[енения]*\.*)",
                      r"(?:\b((р-р)|(раствор)|(р/р)(р\.р))\.* *д[ля]*/*\.*\s*внутрипол[остного]*\.* и нар[ужного]*\.* прим[енения]*\.*)",
                      r"(?:\b((р-р)|(раствор)|(р/р)(р\.р))\.* *д[ля]*/*\.*\s*нар[ужного]*\.* прим[енения]*\.* и инг[аляций]*\.*)",
                      r"(?:\b((р-р)|(раствор)|(р/р)(р\.р))\.* *(д[ля]*)*/*\.*\s*((инф[узий\.]*)|(инг[аляций]*)|(ин[ъекций]*))\.* п/к)",
                      r"(?:\b((р-р)|(раствор)|(р/р)(р\.р))\.* *(д[ля]*)*/*\.*\s*((инф[узий\.]*)|(инг[аляций]*)|(ин[ъекций]*))\.*)",
                      r"(?:(?<![a-zA-Z])sol\.*)(?![a-zA-Z]*[^\d]*)",
                      r"(?:\b((р-р*)|(раствор)|(р/р)(р\.р))\.* *(д[ля]*)*/*\.*\s*в/в в/м введ\b\.*)",
                      r"(?:\b((р-р*)|(раствор)|(р/р)(р\.р))\.* *(д[ля]*)*/*\.*\s* в/в в/м введ\b\.*)",
                      r"(?:\b((р-р*)|(раствор)|(р/р)(р\.р))\.* *(д[ля]*)*/*\.*\s*в/м вв)",
                      r"(?:\b((р-р*)|(раствор)|(р/р)(р\.р))\.* *(д[ля]*)*/*\.*\s*п/к)",
                      r"(?:\b((р-р)|(раствор)|(р/р)(р\.р))\.* *в/в\b)", 
                      r"(?:\bраствор для\s*([\w/][^\d])*\b\.*)",
                      r"(?:\b((р-р)|(раствор)|(р/р)(р\.р))\.* *в[\w/]+\b)",
                      r"(?:\bраствор\b)", 
                      r"(?:\bр-р )",
                      r"(?:\bр-р)",
                  ]
pattern_solution = "". join([ s + "|" for s in pttn_solution_list[::1]])[:-1]
# print(pattern_solution)

pttn_solutions_set_list = [r"(?:р-ров набор д/приг[-я\.]* хирург\.* *клея)",
                      r"(?:р-ров набор для приготовления хирургич\.* *клея)",
]
pattern_solutions_set = "". join([ s + "|" for s in pttn_solutions_set_list[::1]])[:-1]
# print(pattern_solutions_set)

pttn_powder_list = [# r"(?:\b(пор\.*|порошок)\b\s*(д|для)*(\s|/)*(приготовления/п)*(\s|/)*(раствора|р\-ра)*\s*(д|для)*(\s|/)*([\w/\-\s]*[^\dN№(флакон|ампула|шприц|капсула)])*\b[\.\,]*)",
    #r"(?:\b(пор|порошок)\b\.*\s*д/\s*[\w\-]*\b)",
    r"(?:пор[ошок]*\.*\s*д/конц\.* *д/дисп[ерсии]*\.* *д/инф[узий]*\.* *р[-аствора]*)",
    r"(?:порошок для приготовления +раствора +для +ингаляций)",
    r"(?:порошок для приготовления +раствора +для +приема внутрь)",
    r"(?:порошок для приготовления +раствора +для +внутривенного *(введения)*)",
    r"(?:порошок для приготовления +раствора +для +внутримышечного +и +внутривенного +введения)",
    r"(?:порошок для приготовления +раствора +для +внутривенного +и +внутримышечного +введения)",
    r"(?:порошок для приготовления +раствора +для +в/м и +в/в +введения)",
    r"(?:порошок\** для приготовления раствора для инфузий)",
    r"(?:\bпор[ошок]*\.* */*д[ля]*\.* */*сусп\.*)",
    r"(?:\bпор[ошок]*\.* */*д[ля]*\.*/* *приема внутрь и местн\.* *прим\.*)",
    r"(?:пор[ошок]*\.*\s*/*д[ля]*\.*\s*/*внут\.* *сусп\.*)",
    r"(?:пор[ошок]*\.*\s*/*д[ля]*\.*\s*/*орал\.* *сусп\.*)",
    r"(?:пор[ошок]*\.*\s*/*д[ля]*\.*\s*/*ин.в/в и в/м)",
    r"(?:пор[ошок]*\.*\s*/*д[ля]*\.*\s*/*приг[отовления]*\.* *р[-аствора]* *д[ля]*/*\.*\s*инф[узий]*\.*)",
    r"(?:пор[ошок]*\.*\s*/*д[ля]*\.*\s*/*приг[отовления]*\.* *р[-аствора]* *д[ля]*/*\.*\s*инг[аляций]*\.*)",
    r"(?:пор[ошок]*\.*\s*/*д[ля]*\.*\s*/*р[-аствора]* (для)* *в/в и в/м *(введ[ения]*)*\.*)",
    r"(?:пор[ошок]*\.*\s*/*д[ля]*\.*\s*/*в/в и в/м *(введ[ения]*)*\.*)",
    r"(?:пор[ошок]*\.*\s*/*д/р[-аствора]*/*\.*\s*в/в)",
    # пор. д/р-ра в/в и в/м введ.
    r"(?:пор[ошок]*\.*\s*/*д[ля]*\.*\s*/*cусп. *д[ля]*/*\.*\s*приема внутрь)",
    ##r"(?:пор для приг р-ра для инф)",
    r"(?:пор[ошок]*\.*\s*/* *для приг р-ра для инф)",
    r"(?:пор[ошок]*\.*\s*/*д[ля]*\.*/*\s*р[-аствора]* *д[ля]*/*\.*\s*((инф[узий]*)|(инъек[ций]*))\.*)",
    #пор. д/р-ра д/инъек.
    #пор. д/р-ра д/инф.
    r"(?:пор[ошок]*\.*\s*/*д[ля]*\.*/*\s*ин[фузий]*\.*)",
    r"(?:пор[ошок]*\.*\s*/*д[ля]*\.*/*\s*ин[галяций]*\.*)",
    r"(?:пор[ошок]*\.*\s*/*д[ля]*\.*/*\s*нар[ужного]*\.*\s*прим[енения]*\.*)",
    r"(?:пор[ошок]*\.*\s*/*д[ля]*\.*/*\s*приг[отовления]*\.* *р[-аствора]* *в/в и в/м)",
    r"(?:пор[ошок]*\.*\s*/*(д[ля]*)*\s*/*приг[отовления]*\.* *р[-аствора]* *д[ля]*/*\s*приема внутрь)",
    # #r"(?:пор[ошок]*\.*\s*(д[ля]*)*)",
    r"(?:\bпор\.)",
    r"(?:\bпор\s)",
    r"(?:порошок\s)",
    r"(?:порошок$)",
    #r"(?:\bпор[ошок]*\.*\s*(д[ля]*)*(\s|/)*([\w/\-][^\dN№])*\b)",
    r"(?:\bпор[ошок]*\.*\s*(д[ля]*)(\s|/)*([\w/\-][^\dN№])*\b)",
    r"(?:\bпор[ошок]*\.*\s*(д[ля]*)(\s|/)*([\w/\-\.][^\dN№])*(\s|/)*(в/в)*(\s|/)*(р-р(а)*)*(\s|/)*(д/((в/*н)|(в/*в))*(\.|\s|/)*)*(\.|\s|/)*(и)*(\.|\s|/)()*(в/м)*(\.|\s|/)*(прим|введ)*\b[\.\,]*)",
    #r"(?:\b(пор\.*|пор[ошок]*)\s(д|для)*(\s|/)*([\w/\-][^\dN№])*\b)",
    #r"(?:\b(пор\.*|порошок)\s(д|для)*(\s|/)*([\w/\-\.][^\dN№])*(\s|/)*(в/в)*(\s|/)*(р-р(а)*)*(\s|/)*(д/((в/*н)|(в/*в))*(\.|\s|/)*)*(\.|\s|/)*(и)*(\.|\s|/)()*(в/м)*(\.|\s|/)*(прим|введ)*\b[\.\,]*)",
                    #r"(?:\b(пор|порошок)\b\.*\s*для\b)",
                    #r"(?:\b(пор|порошок)\b\.\s*\b)",
                  ]
pattern_powder = "". join([ s + "|" for s in pttn_powder_list[::1]])[:-1]                  
# print(pattern_powder)

pttn_lyophilizate_list = [ r"(?:\b(лиоф(илизат)*|лф)\b\.*\s*(д|для)*(\s|/)*(приготовления/п)*(\s|/)*(раствора|р\-ра)*\s*(д|для)*(\s|/)*([\w/\-\s]*[^\dN№(флакон|ампула|шприц|капсула)])*\b[\.\,]*)",
                          r"(?:\bлиоф(илизат)*\b\.*\s*(д|для)*\s*([\w/\-\s][^\dN№]*(?!(фл|амп|капс*|флакон|ампула|шприц|капсула)*[\s\.]*)*)\b[\.\,]*)",
                          r"(?:\bлиоф(илизат)*\b\.*\s*(д|для)*\s*([\w/\-\s][^\dN№])*\b[\.\,]*)",
                  ]
pttn_lyophilizate_list = [ 
    r"(?:\bлиоф[илизат]*\.* *д[ля]*/*\s*сусп\.* и мест\.* *прим\.*)",
    r"(?:\bлиоф[илизат]*\.* *д[ля]*/*\s*сусп\.* *(п/к))",
    r"(?:\bлиоф[илизат]*\.* *д[ля]*/*\s*сусп\.*)",
    r"(?:лиофилизат для приготовления раствора для внутримышечного введения)",
    r"(?:лиофилизат для приготовления раствора для инфузий)",
    r"(?:лиофилизат для приготовления раствора для внутривенного введения)",
    r"(?:лиофилизат для приготовления раствора для внутрисосудистого и внутрипузырного введения)",
    r"(?:лиофилизат для приготовления раствора для инъекций)",
    r"(?:лиофилизат для приготовления суспензии для внутримышечного введения пролонгированного действия)",
    r"(?:\bлиоф[илизат]*\b\.*\s*д[ля]*\s*/*р[-аствора]* */*п/к)",
    r"(?:лиоф[илизат]*\.* *д[ля]*/*\s*конц.* *д[ля]*/*\s*р[-аствора]* *д[ля]*/*\s*ин[фузий]*\.*)",
    #r"(?:\bлиоф[илизат]*\b\.*\s*(д|для)*\s*([\w/\-\s][^\dN№]*(?!(фл|амп|капс*|флакон|ампула|шприц|капсула)*[\s\.]*)*)\b[\.\,]*)",
    
    r"(?:лиоф[илизат]*\.* *д[ля]*\s*/*р[-аствора]* *в/в( в/м)*)",
    r"(?:\bлиоф[илизат]*\b\.*\s*д[ля]*\s*/*(в/в)*\.*/* *введ[ения]*)",
    r"(?:лиоф[илизат]*\.* *д[ля]*\s*/*р[-аствора]* */*д/[инфузий]*\.*)",
    r"(?:\bлиоф[илизат]*\b\.*\s*д[ля]*\s*/*(в/в)*)",
    #лиоф. д/р-ра д/инф.
    
    r"(?:\bлиоф[илизат]*\b\.*\s*(д|для)*\s*([\w/\-\s][^\dN№])*\b[\.\,]*)",
    #r"(?:\b(лиоф(илизат)*|лф)\b\.*\s*(д|для)*(\s|/)*(приготовления/п)*(\s|/)*(раствора|р\-ра)*\s*(д|для)*(\s|/)*([\w/\-\s]*[^\dN№(флакон|ампула|шприц|капсула)])*\b[\.\,]*)",
    r"(?:\bлиоф[илизат]*\b\.*\s*(д|для)*\s*([\w/\-\s][^\dN№]*(?!(фл|амп|капс*|флакон|ампула|шприц|капсула)*[\s\.]*)*)\b[\.\,]*)",
    r"(?:\bлиоф[илизат]*\b\.*\s*(д|для)*\s*([\w/\-\s][^\dN№])*\b[\.\,]*)",
    r"(?:\b(лиоф[илизат]*|лф)\b\.*\s*(д|для)*\s*/*(п[риготовления]*\.*)*(\s|/)*(р[-аствора]*)*\s*(д|для)*(\s|/)*[инфузий]*\.*)",
                  ]
pattern_lyophilizate = "". join([ s + "|" for s in pttn_lyophilizate_list[::1]])[:-1]
# print(pattern_lyophilizate)

pttn_concentrate_list = [ #r"(?<!д[/\.])(?<!для\s)(?:\b(конц(ентрат)*)\b\.*\s*(д|для)*\s*([\w/\-\s][^\dN№])*\b[\.\,]*)",
                         #r"(?<!д[/\.])(?<!для\s)(?:\b(конц[ентрат]*)\.*\s*д[ля]*\s*([\w/\-\s][^\dN№])*[\.\,]*)",
                         r"(?<!д[/\.])(?<!для\s)(?:\b(конц[ентрат]*)\.*\s*д[ля/]*\s*р[-аствора]*\s*д[ля/\.]*\s*(ин[фуз])*\.*)",
                         r"(?<!д[/\.])(?<!для\s)(?:\b(конц[ентрат]*)\.*\s*д[ля/]*\s*[инфуз]*\s*(д[ля/\.]*)*\s*р[-аствора]*)",
                         #r"(?<!д[/\.])(?<!для\s)(?:\b(конц[ентрат]*)\.*\s*д[ля/]*\s*(д[ля/\.]*)*\s*р[-аствора]*\s*(д[ля/\.]*)*\s*[инфузг]*(\s*(д[ля/\.]*)*\s*[инфузг]*)*)",
                         r"(?:конц[ентрат]*\.* для приготовления раствора для инфузий)",
                         r"(?:конц\.* пригот\.* р-ра д/инф\.*)",
                         
                         r"(?:конц\.* *д[ля/]*р-ра *(д[ля/\.]*)* *инф\.*)",
                         r"(?:конц\.* *д[ля/]*эмульс\.* *(д[ля/\.]*)* *инф\.*)",
                         r"(?:конц\.* *д[ля/]*эмульс\.* *(д[ля/\.]*)* *наруж\.*\s*прим\.*)",
                         r"(?:конц[ентрат]*\.* *(д[ля/\.]*)* *приг[отовления]*\.* *р[-аствора]*\s*(д[ля/\.]*)* *инф[узий]*\.*)",
                         r"(?:конц[ентрат]*\.* *(д[ля/\.]*)* *приг[отовления]*\.* *р[-аствора]*\s*(д[ля/\.]*)* *наружн\.* прим\.*)",
                         r"(?:конц[ентрат]*\.* *(д[ля/\.]*)* *приг[отовления]*\.* *р[-аствора]*\s*(д[ля/\.]*)* *в/в\.* введ\.*)",
                         #конц. д/приг. р-ра д/в/в введ
                         r"(?:конц[ентрат]*\.* *д/*р[-аствора]* *(в/в)*)",
                         r"(?:(конц\b)|(концентр[ат]*\b)\.*(\s|$))",
                         #r"(?:конц[ентрат]*\.* для приг[отовления]*)",
                  ]
pattern_concentrate = "". join([ s + "|" for s in pttn_concentrate_list[::1]])[:-1]
# print(pattern_concentrate)

pttn_capsules_list = [r"(?:капсулы )", r"(?:капсулы$)",
                      r"(?:\bкапс\.*)", r"(?:капс[улы]* ((для)|(д/*)) *приема внутрь)",
                      r"(?:\bkaps\.*)", r"(?:\bkap\.*)",r"(?:\bcaps\.*)", r"(?:\bcap\.*)",
                  ]
pattern_capsules = "". join([ s + "|" for s in pttn_capsules_list[::1]])[:-1]

pttn_emulsion_list = [r"(?:\bэмульсия )", r"(?:\bэмульсия$)",
                      r"(?:\bэмульс\.*)", r"(?:\bэмул\.*)",
                      r"(?:\bэм\.)", r"(?:\bэм\s)",
                      #r"(?:\bэмул[ьсия]*\.*$)",
                      #r"(?:\bэмул[ьсия]*\.*\s*)", 
                         #r"(?<!д[/\.])(?<!для\s)(?:\b(конц(ентрат)*)\b\.*\s*(д|для)*\s*([\w/\-\s][^\dN№])*\b[\.\,]*)",
                  ]
pattern_emulsion = "". join([ s + "|" for s in pttn_emulsion_list[::1]])[:-1]
# print(pattern_emulsion)

pttn_ampoule_list = [r"(?:\bампула )", r"(?:\bампула$)",
                      #r"(?:\bэмульс\.*)", r"(?:\bэмул\.*)",
                      #r"(?:\bэм\.)",
                         #r"(?<!д[/\.])(?<!для\s)(?:\b(конц(ентрат)*)\b\.*\s*(д|для)*\s*([\w/\-\s][^\dN№])*\b[\.\,]*)",
                  ]
pattern_ampoule = "". join([ s + "|" for s in pttn_ampoule_list[::1]])[:-1]
# print(pattern_ampoule)

pttn_drops_list = [r"(?:\bкапли$)",
      r"(?:\bгл[азные]*\.*\s*кап[ли]*\.*)",
      r"(?:\bкапли* глазн*\.*/*(ушные)*)", r"(?:\bкапл*и*[\s\.]+\(*глазн*\.\))", 
      r"(?:\bкапли ушные)", r"(?:\bкапл*и*\.*\s*\(*ушн\.*\)*)",
      r"(?:\bкап\.*л*\.*и* \(*наз\.*\)*)",
      r"(?:\bкап\.*л*\.*и* \(*наз\.*\)*)",
      r"(?:\bкапл\.*\s*д/внут)", r"(?:\bкапли*\.*\s*д/приема внутрь)", 
      r"(?:капли глаз[ные]*\.*)",
      r"(?:капл[\.]* орал\.*)",
      r"(?:\bкапли )", 
      r"(?:р-р/капл)",
      r"(?:\bка[пл]*\.\s*(?=фл\.*))", r"(?:\bкап[пл]*\.\s*(?=шт\.*))", r"(?:\bкап[пл]*\.\s*(?=[\d\.,]+\s*\%\.*))",
      r"(?:\bкапл )", 
      
]
pattern_drops = "". join([ s + "|" for s in pttn_drops_list[::1]])[:-1]
# print(pattern_drops)

ss ="""сусп в/м в/с введ[ения]*
сусп.* *в/суст ок/суст введ[ения]*
сусп.* *внутрь
сусп.* *д/внут
сусп.* *д/и п/к
сусп.* *д/ин
сусп.* *д/ин в/м
сусп.* *д/ин п/к
сусп.* *д/инг
сусп.* *п/к
сусп.* *д/ингал
сусп.* *д/ингал.* дозир
сусп.* *д/инъек
сусп.* *д/наруж.* прим
сусп.* *д/приема внутрь
сусп.* *д/эндотр.* введ
сусп.* *для в/м
сусп.* *для в/м и п/к
сусп.* *для п/к вв[едения]*
суспензия
суспензия д/инъекц
сусп. д/приема внутрь
сусп\s
сусп
сусп$
susp"""

pttn_suspension_list = [r"(?:\b" + p.replace('.','\.').replace('(','\(').replace(')','\)') + r"\.*)"  for p in ss.split('\n') ]
#pttn_suspension_list = [r"(?:" + p.replace('.','\.').replace('(','\(').replace(')','\)') + r"\.*)"  for p in ss.split('\n') ]
pattern_suspension = "". join([ s + "|" for s in pttn_suspension_list[::1]])[:-1]
# print(pattern_suspension)

ss = """глазная мазь
мазь (*глазн.*)*
мазь глазн
мазь глаз
мазь д/мест
мазь д/наруж.* прим
мазь д/наруж
мазь для наруж прим
мазь для наружн примен
мазь
ung.
ung\s
ung$"""
pttn_ointment_list = [r"(?:\b" + p.replace('.','\.').replace('(','\(').replace(')','\)') + r"\.*)"  for p in ss.split('\n') ]

pattern_ointment = "". join([ s + "|" for s in pttn_ointment_list[::1]])[:-1]
# print(pattern_ointment)

ss = """аэрозоль для ингаляций дозированный
аэр. */*д/инг *доз
аэр.* /*д/инг доз
аэр. */*д/инг
аэр.* /*д/инг
аэр/динг.*
аэр. */*д/мест
аэр.* /*д/мест
аэр. */*доз
аэр.* /*доз
аэр. */*д/ингал.* *доз
аэр.* /*д/ингал.* *доз
аэр. */*д/наруж.* *прим
аэр.* /*д/наруж.* *прим
аэр. */*д/наруж
аэр.* /*д/наруж
аэроз. */*д/ингал.* *доз[ир]*
аэроз.* */*д/ингал.* *доз[ир]*
аэрозоль
аэроз.*\s*
аэроз.*$
аэр.\s*
аэр\s
аэр.*$
aer[osol]*(?![a-zA-Z]*)"""

#pttn_aerosol_list = [r"(?:\b" + p.replace('.','\.').replace('(','\(').replace(')','\)') + r"\.*)"  for p in ss.split('\n') ]
pttn_aerosol_list = [r"(?:\b" + p.replace('.','\.') + r"\.*)"  for p in ss.split('\n') ]
pattern_aerosol = "". join([ s + "|" for s in pttn_aerosol_list[::1]])[:-1]
# print(pattern_aerosol)

ss = """гель (*глазн.*)*
гель глаз
гель */*д/мест.* прим
гель */*д/мест
гель */*д/наруж.* *прим
гель */*д/наруж
гель */*д/приема внутрь
гель */*д/сусп д/внут
гель для наружн примен
гель стомат
гель
gel\s
gel.
gel$"""
pttn_gel_list = [r"(?:\b" + p.replace('.','\.').replace('(','\(').replace(')','\)') + r"\.*)"  for p in ss.split('\n') ]
pattern_gel = "". join([ s + "|" for s in pttn_gel_list[::1]])[:-1]
# print(pattern_gel)

#ss = """гр.
pttn_granules_list=[
                    r"(?:гранулы*\.* *к/раств\.)",
                    r"(?:гранулы*\.* */*д/р-ра д/внут[рь]*)",
                    r"(?:гранулы*\.* */*д/р-ра д/приема внут[рь]*)",
                    r"(?:гранулы*\.* *с пролонг.* высвоб\.*)",
                    r"(?:гран[улы\.]* */*д/внут\.* пролон\.*)",
                    r"(?:гран[улы\.]* */*д/сусп.* д/приема внут[рь]*)",
                    r"(?:гран[улы.]* */*д/сусп.* д/внут[рь]*)",
                    r"(?:\bгранулы)",
                    r"(?:\bгранулы$)",
                    #r"(?:((?<!\d)&(?<!\d\d)&(?<!\d\d\d)&(?<!\d\d\d\d)|((?<=\w)+))(?:\sгр\.*))",
                    r"(?:((?<!\d)&(?<!\d\d)&(?<!\d\d\d)&(?<!\d\d\d\d))(?:\sгр\.*))",
                    # r"(?:((?<!\d)(?<!\d\d)(?<!\d\d\d)(?<!\d\d\d\d))(?:\sгр\.*))",
                    r"(?:((?<=N\d)|(?<=N\d\d)|(?<=N\d\d\d)|(?<=N\d\d\d\d))(?:\sгр\.*))",
                    # r"(?:((?<=\w+))(?:\sгр\.*))",
                    # r"(?:(?<=\w)*\w*)(?:\s*гр\.)",
                    #r"(?:((?<=N\d)|(?<=N\d\d)|(?<=N\d\d\d)|(?<=N\d\d\d\d))(?:\sгр\.*)$)",
                    
]


# pattern_granules = "". join([ s + "|" for s in pttn_granules_list[::1]])[:-1]
pattern_granules = "|".join(pttn_granules_list[::1])
# print(pattern_granules) 

pttn_dragees_list = [r"(?:\bдр\.(?!\sГерхард)(?!\sФранц)(?!\sРедди)(?!\sФальк))",
    r"(?:драже\s)", r"(?:драже$)", r"(?:др\.*$)", 
    r"(?:dr\.(?!\sGerhard)(?!\sFalk))", r"(?:dr\.*$)",
]
#pattern_dragees = "". join([ s + "|" for s in pttn_dragees_list[::1]])[:-1]
pattern_dragees = "". join([ s + "|" for s in pttn_dragees_list])[:-1]
# print(pattern_dragees)

ss = """жидк.* д/ингал
жидкость для ингаляций
жидк. */*д/ингал.*[наркоза]*
жидк.* д/инг[аляций]*
жидк. */*для инг[аляций]*
жидк.* для инг[аляций]*
жидк. */для инг[аляций]*
жидкость\s*д/инг[ал]*.* *[наркоза]*
жидкость
ж-сть"""
#pttn_liquid_list = [r"(?:\b" + p.replace('.','\.').replace('(','\(').replace(')','\)') + r"\.*)"  for p in ss.split('\n') ]
pttn_liquid_list = [r"(?:" + p.replace('.','\.').replace('(','\(').replace(')','\)') + r"\.*)"  for p in ss.split('\n') ]
pattern_liquid = "". join([ s + "|" for s in pttn_liquid_list[::1]])[:-1]
# print(pattern_liquid)

ss = """крем д[/ля.]* *наруж.* прим.*
крем д[/ля.]* *местн.* и наруж.* прим
крем д/нар.*
крем\s
крем$
cream
krem"""
# pttn_cream_list = [r"(?:\b" + p.replace('.','\.').replace('(','\(').replace(')','\)') + r"\.*)"  for p in ss.split('\n') ]
pttn_cream_list = [r"(?:" + p.replace('.','\.').replace('(','\(').replace(')','\)') + r"\.*)"  for p in ss.split('\n') ]
pattern_cream = "". join([ s + "|" for s in pttn_cream_list[::1]])[:-1]
# print(pattern_cream)

ss = """спрей д/мест.* *и* *наруж.* *прим.* *доз
спрей д/мест.* */*прим.* *доз
спрей д/мест.* */*прим
спрей д/мест.*
спрей д/наруж.* */*прим.* *спирт
спрей дозиров
спрей назал
спр. до[зир]
спрей п/яз.* */*доз
спрей"""
pttn_spray_list = [r"(?:\b" + p.replace('.','\.').replace('(','\(').replace(')','\)') + r"\.*)"  for p in ss.split('\n') ]
pattern_spray = "". join([ s + "|" for s in pttn_spray_list[::1]])[:-1]
# print(pattern_spray)

ss = """суппозитории вагинальные
супп.* *(*ваг.*)*
супп.* *(*вагин.*)*
суппозитории ректальные
супп.* *(*рект.*)*
суппозитории (*рект.*)*
суппозитори[ий]*
супп.
супп\s
супп$
свечи ректальные
(*свечи*)
свечи
cвечи
св\s
св.\s
св$
suppos 
suppos.
sup 
sup.
sup$"""
# супп.* рект
# супп.рект.
#\bсв.*\b\s
pttn_suppositories_list = [r"(?:\b" + p.replace('.','\.').replace('(','\(').replace(')','\)') + r"\.*)"  for p in ss.split('\n') ]
#pttn_suppositories_list = [r"(?:" + p.replace('.','\.').replace('(','\(').replace(')','\)') + r"\.*)"  for p in ss.split('\n') ]
pattern_suppositories = "". join([ s + "|" for s in pttn_suppositories_list[::1]])[:-1]
# print(pattern_suppositories)

ss = """масло д/приема внутрь и д/наружн.* прим
масло д/приема внутрь
масло\s
масло
масло$"""
pttn_oil_list = [r"(?:\b" + p.replace('.','\.').replace('(','\(').replace(')','\)') + r"\.*)"  for p in ss.split('\n') ]
pattern_oil = "". join([ s + "|" for s in pttn_oil_list[::1]])[:-1]
# print(pattern_oil)

ss = """сироп 
сироп$"""
pttn_syrup_list = [r"(?:\b" + p.replace('.','\.').replace('(','\(').replace(')','\)') + r"\.*)"  for p in ss.split('\n') ]
pattern_syrup = "". join([ s + "|" for s in pttn_syrup_list[::1]])[:-1]
# print(pattern_syrup)

pttn_tincture_list = [r"(?<=настойка\s).*(?:настойка)",  r"(?<=настойка\s).*(?:\bнаст\.*)", 
                      r"(?<=настойка\s).*(?:\bн-ка)", r"(?:\bн-ка)",
                      r"(?:настойка)",
                      r"(?:\bнаст\.)", r"(?:\bнаст\.*\s)"] #, r"(?<=\bнастойка.)(?:\bнастойка)|(?:\bнастойка)"

pattern_tincture = "". join([ s + "|" for s in pttn_tincture_list[::1]])[:-1]
# print(pattern_tincture)

####################################################### 25/09/2022
ss = """газ мед.* сжатый
газ мед. *сжатый
газ сжатый"""
pttn_gaz_list = [r"(?:\b" + p.replace('.','\.').replace('(','\(').replace(')','\)') + r"\.*)"  for p in ss.split('\n') ]
pattern_gaz = "". join([ s + "|" for s in pttn_gaz_list[::1]])[:-1]
# print(pattern_gaz)

ss = """губка
губ.
губ.*$
трансдермальная терапевтическая система"""
pttn_sponge_list = [r"(?:\b" + p.replace('.','\.').replace('(','\(').replace(')','\)') + r"\.*)"  for p in ss.split('\n') ]
pattern_sponge = "". join([ s + "|" for s in pttn_sponge_list[::1]])[:-1]
# print(pattern_sponge)

ss = """импл[антант]*\s
импл[антант]*$
импл[антант]*.* д/интравитр.* *введ[ения]*
импл[антант]* *д/интравитр.* *введ[ения]*
импл
импл\s
импл$
implant"""
pttn_implant_list = [r"(?:\b" + p.replace('.','\.').replace('(','\(').replace(')','\)') + r"\.*)"  for p in ss.split('\n') ]
pattern_implant = "". join([ s + "|" for s in pttn_implant_list[::1]])[:-1]
# print(pattern_implant)

ss = """линим[ент]*"""
pttn_liniment_list = [r"(?:\b" + p.replace('.','\.').replace('(','\(').replace(')','\)') + r"\.*)"  for p in ss.split('\n') ]
pattern_liniment = "". join([ s + "|" for s in pttn_liniment_list[::1]])[:-1]
# print(pattern_liniment)

ss = """микросферы для приготовления суспензии для внутримышечного введения пролонгированного действия
мкс.* д[ля/.]*сусп.* в/м пролонг
микросферы"""
pttn_microspheres_list = [r"(?:\b" + p.replace('.','\.').replace('(','\(').replace(')','\)') + r"\.*)"  for p in ss.split('\n') ]
pattern_microspheres = "". join([ s + "|" for s in pttn_microspheres_list[::1]])[:-1]
# print(pattern_microspheres)

ss = """клей
glue"""
pttn_glue_list = [r"(?:\b" + p.replace('.','\.').replace('(','\(').replace(')','\)') + r"\.*)"  for p in ss.split('\n') ]
pattern_glue = "". join([ s + "|" for s in pttn_glue_list[::1]])[:-1]
# print(pattern_glue)

ss = """напиток
drink"""
pttn_drink_list = [r"(?:\b" + p.replace('.','\.').replace('(','\(').replace(')','\)') + r"\.*)"  for p in ss.split('\n') ]
pattern_drink = "". join([ s + "|" for s in pttn_drink_list[::1]])[:-1]
# print(pattern_drink)

pttn_tincture_list = [r"(?<=настойка\s).*(?:настойка)",  r"(?<=настойка\s).*(?:\bнаст\.*)", 
          r"(?<=настойка\s).*(?:\bн-ка)", r"(?:\bн-ка)",
          r"(настойка)",
          r"(?:\bнаст\.)", r"(?:\bнаст\.*\s)"] #, r"(?<=\bнастойка.)(?:\bнастойка)|(?:\bнастойка)"

pattern_tincture = "". join([ s + "|" for s in pttn_tincture_list[::1]])[:-1]
# print(pattern_tincture)

ss = """паста д/приема внутрь
паста
pasta"""
pttn_pasta_list = [r"(?:\b" + p.replace('.','\.').replace('(','\(').replace(')','\)') + r"\.*)"  for p in ss.split('\n') ]
pattern_pasta = "". join([ s + "|" for s in pttn_pasta_list[::1]])[:-1]
# print(pattern_pasta)

ss = """пастилки
pastille"""
pttn_pastille_list = [r"(?:\b" + p.replace('.','\.').replace('(','\(').replace(')','\)') + r"\.*)"  for p in ss.split('\n') ]
pattern_pastille = "". join([ s + "|" for s in pttn_pastille_list[::1]])[:-1]
# print(pattern_pastille)

ss = """питание
nutrition"""
pttn_nutrition_list = [r"(?:\b" + p.replace('.','\.').replace('(','\(').replace(')','\)') + r"\.*)"  for p in ss.split('\n') ]
pattern_nutrition = "". join([ s + "|" for s in pttn_nutrition_list[::1]])[:-1]
# print(pattern_nutrition)

ss = """пластырь
ттс\s
тдтс\s
тдтс$
bandage"""
pttn_bandage_list = [r"(?:\b" + p.replace('.','\.').replace('(','\(').replace(')','\)') + r"\.*)"  for p in ss.split('\n') ]
pattern_bandage = "". join([ s + "|" for s in pttn_bandage_list[::1]])[:-1]
# print(pattern_bandage)

ss = """р-ль д/приг.* лек.* форм д/инъек[ъекций]*
растворитель для приготовления лекарственных форм для инъекций
раств.* д/лек.* форм д/ин[ъекций]*
р-ль для приг.* *лек.* форм для инъек
р-ль п/приг.* *лк.*форм д/ин
р-ль д/вакцин
раств д/лек форм д/ин
р-ль д/ин[галяций]*"""
#pttn_solvent_list = [r"(?:\b" + p.replace('.','\.').replace('(','\(').replace(')','\)') + r"\.*)"  for p in ss.split('\n') ]
pttn_solvent_list = [r"(?:" + p.replace('.','\.').replace('(','\(').replace(')','\)') + r"\.*)"  for p in ss.split('\n') ]
pattern_solvent = "". join([ s + "|" for s in pttn_solvent_list[::1]])[:-1]
# print(pattern_solvent)

ss = """смесь
mixture"""
pttn_mixture_list = [r"(?:\b" + p.replace('.','\.').replace('(','\(').replace(')','\)') + r"\.*)"  for p in ss.split('\n') ]
pattern_mixture = "". join([ s + "|" for s in pttn_mixture_list[::1]])[:-1]
# print(pattern_mixture)

ss = """сист.в/маточ.
система"""
pttn_system_list = [r"(?:\b" + p.replace('.','\.').replace('(','\(').replace(')','\)') + r"\.*)"  for p in ss.split('\n') ]
pattern_system = "". join([ s + "|" for s in pttn_system_list[::1]])[:-1]
# print(pattern_system)

ss = """пена рект.* доз
пена
foam"""

pttn_foam_list = [r"(?:\b" + p.replace('.','\.').replace('(','\(').replace(')','\)') + r"\.*)"  for p in ss.split('\n') ]
pattern_foam = "". join([ s + "|" for s in pttn_foam_list[::1]])[:-1]
# print(pattern_foam)


# важен порядок чтобы отсечь пересекающиеся формы 'лиоф д пор."
pharm_form_types_list = ['Микросферы',
                         'Таблетки', 'Лиофилизат', 'Порошок', 
                         'Капсулы',  'Капли',
                          'Гель', 'Гранулы', 'Жидкость', 'Крем',
                         'Суспензия', 'Мазь', 
                          'Концентрат', 'Эмульсия',
                          'Спрей', 'Суппозитории',
                          'Масло', 'Сироп',
                          'Настойка', 
                          'Газ', #'Газ медицинский', 
                          'Губка', 'Имплантат',
                          'Линимент', 
                          'Клей', #'Набор растворов для приготовления хирургического клея', 
                          'Напиток','Паста',
                          'Пастилки','Питание','Пластырь',
                         'Растворитель', 'Смесь', 'Система',
                         'Набор', # Набор растворов
                         'Раствор',
                         'Пена',
                         'Драже', 'Аэрозоль', 
                         ]
pharm_form_pttn_list = [pattern_microspheres, 
                        pattern_pills, pattern_lyophilizate,  pattern_powder, 
#pharm_form_pttn_list = [pattern_pills, pattern_solution, pattern_powder, pattern_lyophilizate,  
                        pattern_capsules,  pattern_drops,
                        pattern_gel, pattern_granules, pattern_liquid, pattern_cream,
                        pattern_suspension, pattern_ointment, 
                        pattern_concentrate, pattern_emulsion,
                        pattern_spray, pattern_suppositories,
                        pattern_oil, pattern_syrup,
                        pattern_tincture, 
                        pattern_gaz, pattern_sponge, pattern_implant, 
                        pattern_liniment, 
                        pattern_glue, 
                        pattern_drink,  pattern_pasta,
                        pattern_pastille, pattern_nutrition, pattern_bandage,
                        pattern_solvent, pattern_mixture, pattern_system,
                        pattern_solutions_set,
                        pattern_solution,  
                        pattern_foam,
                        pattern_dragees, pattern_aerosol, 
                        ]

pttn_ampoule_list = [r"(?:\bампул[аы]*\b *)", r"(?:\bампул[аы]*$)",
                      r"(?:\амп\b(\.|\s|$))",r"(?:\амп\.*$)",
                  ]
pattern_ampoule = "". join([ s + "|" for s in pttn_ampoule_list[::1]])[:-1]
# print(pattern_ampoule)

pttn_pack_list = [r"(?:\bупаковка\b *)", r"(?:\bупаковка)$",
                  r"(?:\bуп(\.|\s|$)*конт яч)",
                  r"(?:\bуп(\.|\s|$))",
                  ]
pattern_pack_01 = "". join([ s + "|" for s in pttn_pack_list[::1]])[:-1]
# print(pattern_pack_01)

pttn_pack_list = [r"(?:пач[ка\.]* карт[онная\.]*)", r"(?:пач[ки\.]* картон[ные\.]*)", 
                  r"(?:картон[ная\.]* пач[ка\.]*)", r"(?:картон[ные\.]* пач[ки\.]*)", 
                  ]
pattern_pack_02 = "". join([ s + "|" for s in pttn_pack_list[::1]])[:-1]
# print(pattern_pack_02)

pttn_blister_list = [r"(?:\bблистер\b *)", r"(?:\bблистер)$",
                      r"(?:\bбл[истер]*(\.*|\s|\b|$))",
                  ]
pattern_blister = "". join([ s + "|" for s in pttn_blister_list[::1]])[:-1]
# print(pattern_blister)
pttn_flacon_list = [r"(?:\bфлаконы*\b *)", r"(?:\bфлаконы*)$",
                      r"(?:\bфл(\.|\s|$))",
                  ]
pattern_flacon = "". join([ s + "|" for s in pttn_flacon_list[::1]])[:-1]
# print(pattern_flacon)

# Флакон-капельница
pttn_list = [ r"(?:\bфл-кап[ел]*\.* полиэтил(\.*|\s|\b|$))",
              r"(?:\bфл-кап[ел]*\.* полимер(\.*|\s|\b|$))",
              r"(?:\bфл-кап[ел]*\.* с мерн\.* *ст(\.*|\s|\b|$))",
              r"(?:\bфл-кап[ел]*\.* *темн\.* *ст(\.*|\s|\b|$))",
              r"(?:\bфл-кап[ел]*(\.*|\s|\b|$))",
                  ]
pattern_flacon_dropper = "". join([ s + "|" for s in pttn_list[::1]])[:-1]
# print(pattern_flacon_dropper)

pttn_list = [r"(?:\bбутыл[ьи]*\b(\s*|$))", r"(?:\bбутыл[киа]*\b(\s*|$))",
             r"(?:\bпластиковая бутылочка(\.*|\s*|$))",
             r"(?:\bбут(\.|\s|$))",
                  ]
pattern_bottle = "". join([ s + "|" for s in pttn_list[::1]])[:-1]
# print(pattern_bottle)

pttn_list = [ r"(?:\bшпр[иц]*\.* *с уст\.* защ\.* иг[л]*(\s*|$))", 
              r"(?:\bшпр[иц]*\.* *разов\.*(\s*|$))",
              r"(?:\bшпр[иц]*\.* *-руч[ка]*(\.*|\s*|$))",
              r"(?:\bшпр[иц]*\.* *комп\.* *иг[л]*(\.*|\s*|$))",
              r"(?:\bшпр[иц]*\.* *с игл[ами]*(\.*|\s*|$))",
              r"(?:\bшпр[иц]*\.* *с салф\.* спирт(\.*|\s*|$))",
              r"(?:\bшпр[иц]*\.* *одн\.* *с игл(\.*|\s*|$))",
             r"(?:\bшпр[иц]*(\.*|\s*|\b|$))",
                  ]
pattern_injector = "". join([ s + "|" for s in pttn_list[::1]])[:-1]
# print(pattern_injector)

pttn_list = [ r"(?:\bкарт[ридж]*(\.*|\s*)ш/р*\b(\s*|$))", 
              r"(?:\bкарт[ридж]*(\.*|\s*|\b|$))",
                  ]
pattern_cartridge = "". join([ s + "|" for s in pttn_list[::1]])[:-1]
# print(pattern_cartridge)
s = 'Инсулин гларгин р-р для п/к 100 ЕД/мл 3 мл картр ш/р БиоматикПен 2 N 5x1'
# print(re.search(pattern_cartridge, s, flags=re.I))

pttn_list = [r"(?:\bтуб[аы]*(\.*|\s*|\b|$))",
                  ]
pattern_tube = "". join([ s + "|" for s in pttn_list[::1]])[:-1]
# print(pattern_tube)

pttn_list = [r"(?:\bтюб[ик]*(\.*|\s*)-*кап[ельница]*(\.*|\s*|\b|$))",
                  ]
pattern_tube_02 = "". join([ s + "|" for s in pttn_list[::1]])[:-1]
# print(pattern_tube_02)

pttn_list = [r"(?:\bтюб[ик]*(\.*|\s*|\b|$))",
                  ]
pattern_tube_03 = "". join([ s + "|" for s in pttn_list[::1]])[:-1]
# print(pattern_tube_03)

pttn_list = [r"(?:\bконт[ейнер\.]* *полим[ерный]*(\.*|\s*|\b|$))",
             r"(?:\bконт[ейнер\.]* п/проп(\.*|\s*|\b|$))",
             r"(?:\bконт[ейнер\.]* *с 2 портами(\.*|\s*|\b|$))",
             r"(?:\bконт[ейнеры]*(\.*|\s*|\b|$))",
                  ]
pattern_container = "". join([ s + "|" for s in pttn_list[::1]])[:-1]
# print(pattern_container)

pttn_list = [r"(?:\bпак[еты]*(\.*|\s*)двухк\.*( *Biofine)*(\.*|\s*|\b|$))",
             r"(?:\bпак[еты]*(\.*|\s*|\b|$))",
                  ]
pattern_packet = "". join([ s + "|" for s in pttn_list[::1]])[:-1]
# print(pattern_packet)

pttn_list = [r"(?:\bмеш[кио]*(\.*|\s*) пласт\.* *двухкам(\.*|\s*|\b|$))",
             r"(?:\bмеш[кио]*(\.*|\s*|\b|$))",
                  ]
pattern_bag = "". join([ s + "|" for s in pttn_list[::1]])[:-1]
# print(pattern_bag)

pttn_list = [r"(?:\bстрип[сы]*(\.*|\s*|\b|$))",
                  ]
pattern_strips = "". join([ s + "|" for s in pttn_list[::1]])[:-1]
# print(pattern_strips)

pttn_list = [r"(?:\bбан[очкаи]*(\.*|\s*|\b|$))",
                  ]
pattern_jar = "". join([ s + "|" for s in pttn_list[::1]])[:-1]
# print(pattern_jar)

# Баллоны/Баллончики
pttn_list = [r"(?:\bбал[лоны]*(\.*|\s*|\b|$))",
                  ]
pattern_ballon = "". join([ s + "|" for s in pttn_list[::1]])[:-1]
# print(pattern_ballon)

pttn_list = [r"(?:\bканист[раы]*(\.*|\s*|\b|$))",
                  ]
pattern_canister = "". join([ s + "|" for s in pttn_list[::1]])[:-1]
# print(pattern_canister)

pttn_list = [r"(?:\bсаше(\.*|\s*|\b|$))",
                  ]
pattern_sasha = "". join([ s + "|" for s in pttn_list[::1]])[:-1]
# print(pattern_sasha)

pttn_list = [r"(?:\bпроб[ирка]*(\.*|\s*|\b|$))",
                  ]
pattern_test_tube = "". join([ s + "|" for s in pttn_list[::1]])[:-1]
# # print(pattern_test_tube)

pack_form_types_list = ['Ампул', # -а, -ы
                        'Упаковка',   # 'Упаковки'
                        'Пачк', # Пачки(-а) картонные(-ая) / Картонные(-ая) пачки(-а)
                        'Блистер', # 'Блистеры'
                        'Флакон', 'Флакон-капельниц', # -а, -ы
                        'Бутыл', # -ка, -ки, -ь, -и
                        'Шприц', 'Картридж', 'Туб', 'Тюбик-капельница', 'Тюбик', 
                        'Контейнер', 'Пакет', 'Меш', #-ок, ки
                        'Стрипс', # -ы
                        'Банк', #-и, -а
                        'Баллон', # Баллоны/Баллончики
                        'Канистр', # _а, -ы
                        'Саше', # пакетик
                        'Пробирк', # -а, -и


                         ]
pack_form_pttn_list = [pattern_ampoule, pattern_pack_01, 
                       pattern_pack_02,
                       pattern_blister,
                       pattern_flacon, pattern_flacon_dropper,
                       pattern_bottle,
                       pattern_injector, pattern_cartridge, pattern_tube, pattern_tube_02, pattern_tube_02,
                       pattern_container, pattern_packet, pattern_bag,
                       pattern_strips,
                       pattern_jar,
                       pattern_ballon,
                       pattern_canister,
                       pattern_sasha,
                       pattern_test_tube,

                        ]                         