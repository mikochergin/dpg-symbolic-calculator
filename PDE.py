import dearpygui.dearpygui as dpg
import webbrowser
import pyperclip as pc
# from sympy import *
from sympy import simplify, diff, latex
import matplotlib
matplotlib.use('agg')
import matplotlib.pyplot as plt
from matplotlib.backends.backend_agg import FigureCanvasAgg
import numpy as np


dpg.create_context()

count_of_PDEs = 0
is_formula_shown = False
default_formula = 'a*x^y+b*x+c'

#--start of functions

def str_py_to_cpp(str_py:str):
    '''
    Заменяет ** на ^ в строке
    '''
    str_cpp = str_py.replace('**', '^')
    return str_cpp

def str_cpp_to_py(str_cpp:str):
    '''
    Заменяет ^ на ** в строке
    '''
    str_py = str_cpp.replace('^', '**')
    return str_py

def help_callback(sender, app_data):
    message = '''Данная программа предназначена для аналитической обработки выражений.
    Для начала работы введите формулу и имя переменной для дифференцирования.
    (* - умножение, ^ или ** - возведение в степень, / - деление, + - сложение, - - вычитание, написание
    функций типа sqrt, cos, sin и пр. см. в документации Sympy по кнопке "Список функций".)
    Результат будет выведен в поле для вывода результата.
    При нажатии кнопки "Копировать" результат будет скопирован в буфер обмена.
    При нажатии кнопки "Очистить" поля для ввода и вывода результата будут очищены.
    При нажатии кнопки "Список функций" в браузере будет открыта веб-страница Sympy \nсо списком функций.
    При нажатии кнопки "Пример" в поле для ввода будет введена функция \nдля определения частной производной.
    При нажатии кнопки "Справка" будет открыта справка.\n
    Вопросы, предложения, пожелания, информацию об ошибках можно направить 
    на maksim.i.kochergin@tusur.ru или
    в https://github.com/mikochergin/dpg-symbolic-calculator
    '''
    show_info("Справка: Модуль взятия производных 1.0", message, on_selection)
def show_info(title, message, selection_callback):

    # guarantee these commands happen in the same frame
    with dpg.mutex():

        viewport_width = dpg.get_viewport_client_width()
        viewport_height = dpg.get_viewport_client_height()

        with dpg.window(label=title, modal=True, no_close=True) as modal_id:
            dpg.add_text(message)
            with dpg.group(horizontal=True):
                dpg.add_button(label="Ok", width=75, user_data=(modal_id, True), callback=selection_callback)
                dpg.add_spacer(width=5)
                dpg.add_button(label='Сообщить об ошибке\nна GitHub', width=175, 
                    callback=lambda: open('https://github.com/mikochergin/dpg-symbolic-calculator/issues'))
                dpg.add_spacer(width=5)
                dpg.add_button(label='Сообщить об ошибке\nна e-mail', width=175, 
                    callback=lambda: open('mailto:maksim.i.kochergin@tusur.ru'))

    # guarantee these commands happen in another frame
    dpg.split_frame()
    width = dpg.get_item_width(modal_id)
    height = dpg.get_item_height(modal_id)
    dpg.set_item_pos(modal_id, [viewport_width // 2 - width // 2, viewport_height // 2 - height // 2])
def on_selection(sender, unused, user_data):
    pass
    # delete window
    dpg.delete_item(user_data[0])



def Flist_callback(sender, app_data):
    webbrowser.open('https://docs.sympy.org/latest/modules/functions/elementary.html')


def copy_callback(sender, app_data):
    pc.copy(dpg.get_value('result_output'))

def clear_output(sender, app_data):
    global is_formula_shown
    global count_of_PDEs
    dpg.set_value('result_output', '')
    if is_formula_shown == True:
        dpg.delete_item(item='result_group', children_only=True)
        is_formula_shown = False

def clear_input(sender, app_data):
    dpg.set_value('formula_input', '')
    dpg.set_value('var_input', '')

def example_callback(sender, app_data):
    dpg.set_value('formula_input', default_formula)
    dpg.set_value('var_input', 'x')

def simplify_callback(sender, app_data):
    try:
        result = simplify(dpg.get_value('result_output'))
        dpg.set_value('result_output', result)
        create_PDE(result)
    except:
        dpg.set_value('result_output', 'Неверная формула для упрощения')

def calc_callback(sender, app_data):
    global count_of_PDEs
    global is_formula_shown
    try:
        formula = dpg.get_value('formula_input')
        var = dpg.get_value('var_input')

        result = diff(formula, var)
        dpg.set_value('result_output', str(result))
        create_PDE(result)
        # dpg.add_image("texture_id_"+str(count_of_PDEs-1), parent='result_group')
    except:
        dpg.set_value('result_output', 'Неверная формула или переменная')
        if is_formula_shown == True:
            dpg.delete_item(item='result_group', children_only=True)     
            is_formula_shown = False

def create_PDE(formula):
    global count_of_PDEs
    global is_formula_shown
    formula_latex = latex(formula)

    fig = plt.figure(figsize=(4, 1), dpi=100)

    ax = plt.axes([0,0,0.3,0.3]) #left,bottom,width,height
    ax.set_xticks([])
    ax.set_yticks([])
    ax.axis('off')
    plt.text(0.0,2.0,'$%s$' %formula_latex,size=14,color="black")
    canvas = FigureCanvasAgg(fig)
    ax = fig.gca()
    canvas.draw()
    buf = canvas.buffer_rgba()
    image = np.asarray(buf)
    image = image.astype(np.float32) / 255

    with dpg.texture_registry():
        dpg.add_raw_texture(
            400, 70, image, format=dpg.mvFormat_Float_rgba, tag="fig_"+str(count_of_PDEs)
        )
    if is_formula_shown == True:
        dpg.delete_item(item='result_group', children_only=True)     
        is_formula_shown = False
    dpg.add_image('fig_'+str(count_of_PDEs), parent='result_group')
    is_formula_shown = True
    count_of_PDEs += 1
#--end of functions

# Allow Cyrillic in window
big_let_start = 0x00C0  # Capital "A" in cyrillic alphabet
big_let_end = 0x00DF  # Capital "Я" in cyrillic alphabet
small_let_end = 0x00FF  # small "я" in cyrillic alphabet
remap_big_let = 0x0410  # Starting number for remapped cyrillic alphabet
alph_len = big_let_end - big_let_start + 1  # adds the shift from big letters to small
alph_shift = remap_big_let - big_let_start  # adds the shift from remapped to non-remapped

with dpg.font_registry():
    with dpg.font("C:/Windows/Fonts/times.ttf", 20) as default_font:
        dpg.add_font_range_hint(dpg.mvFontRangeHint_Default)
        dpg.add_font_range_hint(dpg.mvFontRangeHint_Cyrillic)
        biglet = remap_big_let  # Starting number for remapped cyrillic alphabet
        for i1 in range(big_let_start, big_let_end + 1):  # Cycle through big letters in cyrillic alphabet
            dpg.add_char_remap(i1, biglet)  # Remap the big cyrillic letter
            dpg.add_char_remap(i1 + alph_len, biglet + alph_len)  # Remap the small cyrillic letter
            biglet += 1  # choose next letter
dpg.bind_font(default_font)

with dpg.window(label="Приложение для взятия частных производных аналитически", width=800, height=500, no_move=True, no_title_bar=True) as MainWindow:
    with dpg.group(horizontal=False):#, tag='result_group'):
        with dpg.group(horizontal=True):
            dpg.add_spacer(width=100)
            dpg.add_button(label = 'Справка', tag = 'help_btn', callback = help_callback)
            dpg.add_spacer(width=50)
            dpg.add_button(label = 'Список функций', tag = 'listF_btn', callback=Flist_callback)
            dpg.add_spacer(width=20)
            # dpg.add_checkbox(label='Обозначение степени как в C++ (^)', tag='degree_btn', default_value=True)
        with dpg.group(horizontal=True):
            dpg.add_spacer(width=100)
            dpg.add_text('Поле для ввода формулы |')
            dpg.add_text('Имя переменной для дифференцирования')
        with dpg.group(horizontal=True):
            dpg.add_input_text(hint=default_formula, width=300, height=50, tag = 'formula_input')
            dpg.add_input_text(hint='x', width=100, height=50, tag = 'var_input')
            dpg.add_button(label = 'Частная\nпроизводная', tag = 'calc_btn', callback = calc_callback)
            dpg.add_button(label = 'Очистить', tag = 'clearInput_btn', callback = clear_input)
            dpg.add_button(label = 'Пример', tag = 'example_btn', callback = example_callback)
        with dpg.group(horizontal=True):
            dpg.add_text('        ')
            dpg.add_text('Поле для вывода результата')
        with dpg.group(horizontal=True):
            dpg.add_input_text(hint='Результат', width=300, height=50, tag = 'result_output')
            dpg.add_spacer(width=5)
            dpg.add_button(label = 'Копировать', tag = 'copy_btn', callback = copy_callback)
            dpg.add_spacer(width=5)
            dpg.add_button(label = 'Очистить', tag = 'clearOutput_btn', callback = clear_output)
            dpg.add_spacer(width=5)
            dpg.add_button(label='Упростить', tag='simplify_btn', callback=simplify_callback)
        with dpg.group(horizontal=False, tag = 'result_group'):
            pass

with dpg.theme() as container_theme:
    with dpg.theme_component(dpg.mvAll):
        dpg.add_theme_color(dpg.mvThemeCol_Text, (0,0,0))
        dpg.add_theme_color(dpg.mvThemeCol_TextDisabled, (80,80,80))
        dpg.add_theme_color(dpg.mvThemeCol_WindowBg, (240,240,240))
        dpg.add_theme_color(dpg.mvThemeCol_ChildBg, (200,200,200))
        dpg.add_theme_color(dpg.mvThemeCol_FrameBg, (180,180,180))
        dpg.add_theme_color(dpg.mvThemeCol_TitleBgActive, (33,131,198))
        dpg.add_theme_color(dpg.mvThemeCol_TitleBg, (180,180,180))
        dpg.add_theme_color(dpg.mvThemeCol_MenuBarBg, (180,180,180))
        dpg.add_theme_color(dpg.mvThemeCol_ScrollbarBg, (180,180,180))
        dpg.add_theme_color(dpg.mvThemeCol_Button, (180,180,180))
        dpg.add_theme_color(dpg.mvThemeCol_ResizeGrip, (180,180,180))
        dpg.add_theme_color(dpg.mvPlotCol_LegendBg, (200,200,200), category=dpg.mvThemeCat_Plots)
        dpg.add_theme_color(dpg.mvNodeCol_NodeBackground, (220,220,220), category=dpg.mvThemeCat_Nodes)
        dpg.add_theme_color(dpg.mvNodeCol_TitleBar, (93,179,255), category=dpg.mvThemeCat_Nodes)
        dpg.add_theme_color(dpg.mvNodeCol_GridBackground, (93,179,255), category=dpg.mvThemeCat_Nodes)
        dpg.add_theme_color(dpg.mvNodeCol_GridLine, (93,179,255), category=dpg.mvThemeCat_Nodes)

        dpg.add_theme_color(dpg.mvThemeCol_PopupBg, (180,180,180))

        dpg.add_theme_style(dpg.mvNodeStyleVar_NodePadding,0, category=dpg.mvThemeCat_Nodes)#horizontal and vertical?


dpg.bind_item_theme(MainWindow, container_theme)

# dpg.show_style_editor()

dpg.create_viewport(title='Symbolic Calculator', width=800, height=500)
dpg.setup_dearpygui()
dpg.show_viewport()
dpg.start_dearpygui()
dpg.destroy_context()
