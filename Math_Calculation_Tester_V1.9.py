from asyncio.windows_events import NULL
from multiprocessing.connection import wait
from tkinter.constants import TRUE
import PySimpleGUI as sg
import time
from datetime import datetime
import random
import itertools
from PySimpleGUI.PySimpleGUI import Text
from pandas.core.frame import DataFrame
import re,math

declare_info="\
*******************************Info**********************************\n\
Name: Math_Calculation_Tester\n\
Writer: Kaka&Bell's Family\n\
Typical Taeget user: the fist&second grade student in primary school\n\
Version；V1.9 2022-Dec-4\n\
License: Free to use&modify following MIT license\n\
Contact: hwzx216@126.com\n\
Please reserve the above infomation in case of any code or software transfer to anybody anywhere.\n\
*********************************************************************\n\
Welcome to use!\n\
***************************Changelog*****************************\n\
V1.3：one loop one excel file created + null input is thought as no avaliable inputs.\n\
V1.4：Self definition of \"scopeofca\", it means children can set a number to decide the scope of answer,like plus or minus but answer is under 20.\n\
V1.5: identify user inputs in correct format, extract only number from user inputs, eliminate or ignore possible letters in user inputs, bug fixed. \n\
V1.6: auto calculation of max expected time comsumption of each loop.\n\
V1.7: zoom out the summary font, it means make the word bigger to display. Fixed an issue about no fixed width of first column in Summary window.\n\
V1.8：modify all name from 'SimpleCaluculationTester' to 'Math_Calculation_Tester' \n\
V1.9：supports multiplication and division\n\
*********************************************************************\n"

####变量声明
set_time_initial = False #设置界面计时器在start按钮按下后才开始计时
i = 0 #计数器，基本是点start或者next按钮的次数，也意味着操作者在本轮的所处阶段，是start，还是答题中，还是答题结束阶段。
excel_list = []#作为一个loop的主缓存用，存放[等式，正确答案，实际输入答案，实际输入对错]
excel_list_accumulation = []#用作多个loop的主缓存，列表形式，格式为：[等式，正确答案，实际输入答案，实际输入对错]
progress_history = '' #把孩子的答案做出判断，答对就是(P)Pass,答错就是(F)Fail
equation_amount = 20 #设定总共有多少道题，可外部指定，默认20.(mandatory)
scopeofcal = 20 #20以内的加减法(mandatory)
multiplication_mode = 0 #默认非乘法或除法模式，只有加减法。
question_mode = 0#指定一个题库的模式(mandatory)
QT_ENTER_KEY1 = 'special 16777220'#键盘enter符
QT_ENTER_KEY2 = 'special 16777221'#键盘enter符
loop_times = 0#初始化计数，loop为答题从一遍开始到结束（比如1至40道题一遍），若不关闭窗口，第二个loop时该loop_times计数为2.


####函数定义
def main_window_format():  
    sg.theme('Tan')
    #sg.ChangeLookAndFeel('DarkGreen')#设置窗口风格
    menu_def = [['Setting',['ScopeOfCal','TotalAmountofItems','X/','HardMode']],['About',['Readme']]]
    # Define the main window's layout and contents
    layout = [[sg.Menu(menu_def)],[sg.Text(text='Timer',size=(10,1), key='-timer-', font=('Courier',20),justification='l'),
            sg.Text(text='Info',size=(100,1), key='-Indocator-', font=('Courier',10),justification='r',text_color='lightblue')],
            [sg.Text(text='Ready?',size=(20,1), key='-item_disp-', font=('Courier',40), auto_size_text=True,text_color='black',justification='c')],
            [sg.Input(default_text='^_^',text_color='black',disabled=True,size=(15,1), font=('Courier',40),key='-item_in-',justification='c',background_color='grey')],
            [sg.ProgressBar(equation_amount,size=(90,15), orientation='h',key='-progress-',bar_color=('yellow','yellow'))],
            [sg.Text("Result: ",visible= False)],[sg.Text(size=(50,1),key='-result-',visible= False,font=('Courier',15),justification='c')],
            [sg.Button('Start',disabled=False, font=('Courier',30)),sg.Button('Next',disabled=True, font=('Courier',30)),sg.Button('Summary',disabled=True, font=('Courier',30))],
            [sg.Multiline(visible= False, key='-multiline-',write_only=True,size=(80,30),font=80)]]
    #时间输出显示
    #题目输出显示区域
    #答案输入区域
    #进度条(答对的就变为绿色，答错的变为红色.)
    #结果显示区域，‘本轮共答题几道，错误几道，正确几道’
    #按键区域（开始测试，下一题，结束测试，生成图表）
    
    # Create the main window, format the window
    window = sg.Window('Math_Calculation_Tester', 
                        layout = layout,
                    auto_size_buttons=False,
                    keep_on_top=TRUE,
                    grab_anywhere=True,
                    element_padding=(0, 0),
                    finalize=True,
                    element_justification='c',
                    right_click_menu=sg.MENU_RIGHT_CLICK_EDITME_EXIT,
                    return_keyboard_events=True) #main window definition or format
    return window

#定义定时器用，获取当前时间
def time_as_int():
    return int(round(time.time() * 100))

#Define a random elements of equations for plus and minus:
def get_combination(max, m):
    #'max' is the number in which scope you want to calcaluate, like inside 20 then here put 20 in.
    #'m' is the amount of equations you want to ask students to answer in one loop.like 40.
    list_combination =  random.sample(list(itertools.combinations(range(1, max), 2)), m) #从1到max里按顺序挑2个数做全部枚举成一个list,再在这个list里挑出m个组数字，返回的是list,元素是元组。
    return list_combination


#Define a random elements of equations for multiplication or divition:
def multiplication_divition(max,m):
    i = 0
    list_combination = []
    max_factor = math.sqrt(max)
    #max_factor是乘法的积的最大值，比如100是期望最大的积，那max_factor就是10，也就是factor是0到10的随机整数
    while i<m: #找出m个两个数的组合，做两个因子
        factor1 = random.randint(1,max_factor)
        factor2 = random.randint(1,max_factor)
        list_combination.append((factor1,factor2))
        i=i+1
    return list_combination

#Define the equations//题库生成
def equation_creation(equation_amount,question_mode,scopeofcal,multiplication_mode):#输入参数为几道题这个数目，返回一个list，第一和第二元素分别为题目算式，正确答案。
    excel_list=[]
    if multiplication_mode == 0:
        if question_mode == 0:#简易模式，只求等式右边的答案,类似1+1=几（非1+几=2）
            for onenumber, result in get_combination(scopeofcal, equation_amount):#20以内的加减法，一共equation_amount道题
                if random.random() < 0.5:#随机分配加减法
                    excel_list.append([('%-12s' %(str(onenumber)+' + '+str(result-onenumber)+' =')),'%-7s' %(str(result))])#拼凑加法算式和正确答案
                else:#减法
                    excel_list.append([('%-12s' %(str(result) + ' - ' + str(onenumber)+' =')),'%-7s' %(str(result-onenumber))])#拼凑剑法算式和正确答案
            #print('excel_list is:',excel_list)
            return excel_list#这里的题库是一个list形式，每个元素均又为一个2个元素的list，第一个元素为题目本身的str，第一个元素为题目正确答案的str
        elif question_mode > 0:#等式左边也有填空的题目
            for onenumber, result in get_combination(scopeofcal, equation_amount):#20以内的加减法，一共equation_amount道题
                if random.random() < 0.5:#随机分配加减法
                    if random.random() < 0.5:#某数加某数等于几的形式
                        excel_list.append(['%-12s' % ((str(onenumber)+' + '+str(result-onenumber)+' = [ ]')),'%-7s' % str(result)])#拼凑加法算式和正确答案
                    else:#某数加几等于指定数字的形式
                        excel_list.append(['%-12s' % (str(onenumber)+' + '+str('[ ]') + ' = '+ str(result)),'%-7s' % str(result-onenumber)])
                else:
                    if random.random() < 0.5:
                        excel_list.append(['%-12s' % ((str(result) + ' - ' + str(onenumber)+' = [ ]')),'%-7s' % str(result-onenumber)])#拼凑剑法算式和正确答案
                    else:
                        excel_list.append(['%-12s' % ((str(result) + ' - ' + str('[ ]')+' = ' + str(result - onenumber))),'%-7s' % str(onenumber)])#拼凑剑法算式和正确答案
            #print('excel_list is:',excel_list)
            return excel_list#这里的题库是一个list形式，每个元素均又为一个2个元素的list，第一个元素为题目本身的str，第一个元素为题目正确答案的str
        else:
            print('***Please give the correct question_mode.')
    elif multiplication_mode > 0: #乘除法模式
        if question_mode == 0:#简易模式，只求等式右边的答案,类似1X1=几（非1X几=1）
            for factor1, factor2 in multiplication_divition(scopeofcal, equation_amount):#100以内的乘法除法，一共equation_amount道题
                if random.random() < 0.5:#随机分配乘除法
                    excel_list.append([('%-12s' %(str(factor1)+' X '+str(factor2)+' =')),'%-7s' %(str(factor1*factor2))])#拼凑加法算式和正确答案
                else:#除法
                    excel_list.append([('%-12s' %(str(factor1*factor2) + ' / ' + str(factor1)+' =')),'%-7s' %(str(factor2))])#拼凑剑法算式和正确答案
            #print('excel_list is:',excel_list)
            return excel_list#这里的题库是一个list形式，每个元素均又为一个2个元素的list，第一个元素为题目本身的str，第一个元素为题目正确答案的str
        elif question_mode > 0:#等式左边也有填空的题目
            for factor1, factor2 in multiplication_divition(scopeofcal, equation_amount):#100以内的乘法除法，一共equation_amount道题
                if random.random() < 0.5:#随机分配乘除法，若为乘法
                    if random.random() < 0.5:
                        excel_list.append(['%-12s' % ((str('[ ]')+' X '+str(factor2)+' = '+ str(factor1*factor2))),'%-7s' % str(factor1)])#拼凑加法算式和正确答案
                    else:
                        excel_list.append(['%-12s' % (str(factor1)+' X '+str('[ ]') + ' = '+ str(factor1*factor2)),'%-7s' % str(factor2)])
                else:#若为除法
                    if random.random() < 0.5:
                        excel_list.append(['%-12s' % ((str(factor1*factor2) + ' / ' + str('[ ]')+' = ' + str(factor1))),'%-7s' % str(factor2)])#拼凑剑法算式和正确答案
                    else:
                        excel_list.append(['%-12s' % ((str(factor1*factor2) + ' / ' + str('[ ]')+' = ' + str(factor2))),'%-7s' % str(factor1)])#拼凑剑法算式和正确答案
            #print('excel_list is:',excel_list)
            return excel_list#这里的题库是一个list形式，每个元素均又为一个2个元素的list，第一个元素为题目本身的str，第一个元素为题目正确答案的str
        else:
            print('***Please give the correct question_mode.')
    else:
        print('***Please give the correct multiplication_mode.')

#统计正确率
def resultdisp(list):#finish答题后计数答对答错的数目，并攒好字符串以供直接显示
    i = 0
    rightamount = 0
    wrongamount = 0
    for i in range(len(list)):
        if list[i][3].strip() == 'Pass':#.strip()为去掉首尾的空格
            rightamount = rightamount + 1#用户答对的计数
        elif list[i][3].strip() == 'Fail':
            wrongamount = wrongamount + 1
        else:
            pass
    return '共答题'+str(rightamount+wrongamount)+'道.\
        正确:错误为'+ str(rightamount) + ':' + str(wrongamount) + ',\
        正确率为' + str(int(rightamount/(rightamount+wrongamount)*100))+'%.'

#期望一轮答题所需的最长时间
def expect_duration_cal(equation_amount,scopeofcal,question_mode,multiplication_mode):
    if str(question_mode).strip() == '0': #hardmode == 1为easy模式，
        additional = 0 ##如果是easy模式的题目，每道题允许多加0秒钟
    else: 
        additional = 5 #如果非easy模式的题目，每道题允许多加5秒钟做出来
    if scopeofcal <= 20: #如果20以内的加减法
        max_time_consumption_per_item_sec = 5
    elif 20 < scopeofcal <= 100: #如果100以内的加减法
        max_time_consumption_per_item_sec = 13
    else:
        max_time_consumption_per_item_sec = 25 
    expect_duration = round((equation_amount * (max_time_consumption_per_item_sec + additional)+ multiplication_mode*10)  /60,2) #设定计算一个loop所期望的最长耗时expect_duration(单位为分钟，可以为小数)的公式,并用round()来保留2位小数,如10.25min
    expect_duration_min,expect_duration_sec = str(expect_duration).split('.') #分离整数和小数部分
    expect_duration_min_sec = expect_duration_min + '\'' + str(round(int(expect_duration_sec) * 60/100)) +'\"'#打包成便于显示的分和秒的形式。
    return expect_duration,expect_duration_min_sec


#显示（累计）本轮详细的统计结果：每道题的结果显示。
def summary(excel_list):
    df_summary=DataFrame(excel_list[:])#excellist是题库，在这转为DataFrame
    df_summary.rename(columns={0:'%-12s' % 'Equations',1: '%-7s' % 'Ans',2:'%-4s' % 'Kid',3:'%-6s' % 'Result',4:'%-10s' % 'Duration/s'},inplace=True)#列名设置
    #print(df_summary)
    return df_summary

####主函数开始
#初始化
window = main_window_format()#调用函数定义一个窗口及其所有元素
excel_list = equation_creation(equation_amount,question_mode,scopeofcal,multiplication_mode)#将当前出题组合导出至该变量内存储，excel_list是个列表
#print('Initial excel_list:',excel_list)

# Display and interact with the Window using an Event Loop
while True:
    event, values = window.read(timeout=1000)
    expect_duration, expect_duration_min_sec = expect_duration_cal(equation_amount,scopeofcal,question_mode,multiplication_mode) #计算本次loop所期望的最长用时，短于此值的会有界面的解锁。鼓励孩子做题时间短于此值。
    #print('event is:',event, ';values is:',values)
    # See if user wants to quit or window was closed
    window['-Indocator-'].update(str('Scopeofcal='+str(scopeofcal)+';Equation_amount='+ str(equation_amount)+';HardMode='+str(question_mode)+'; Expect_consumption='+str(expect_duration_min_sec)+'; multiplication_mode='+str(multiplication_mode)))#实时显示设置的数值
    if event == sg.WINDOW_CLOSED:#窗口关闭的事件
        break
    elif (event == 'Start') or (event in ('\r', QT_ENTER_KEY1, QT_ENTER_KEY2) and (i == 0)):#相当于初始化
        i = 0 #题目计数器，0为第一道题
        loop_times = loop_times + 1 #标识第一个(或下一个)loop的开始（未关闭窗口可以累计作答多个loop）
        #print('excel_list[i] is:',excel_list[i])
        window['-item_disp-'].update(excel_list[i][0].strip(),font=('Courier',40))#题目显示
        window['-item_in-'].update('',disabled=False,background_color='white')#输入框启用
        start_time = time_as_int()#获取当前时间
        set_time_initial = True#计时开始
        window['Start'].update(disabled=True)
        window['Next'].update(disabled=False)
        window['Summary'].update(disabled=True)
        window['-result-'].update(visible=False)
        window['-progress-'].update(i,bar_color=('yellow','yellow'))
        window['-multiline-'].update(visible = False)
        progress_history = ''#清空上一轮每个题目的答案
        i = 1
    elif (event == 'Next') or (event in ('\r', QT_ENTER_KEY1, QT_ENTER_KEY2) and (0<i<=equation_amount)):#使键盘enter操作仅在Next按钮可按下的情况下执行
        window['-item_in-'].update('',background_color='white')#清空输入框内原有的输入数字
        #print('excel_list[i-1]:',excel_list[i-1])
        #print('excel_list[i-1][0]:',excel_list[i-1][0])
        #print('i:',i)
        user_inputs_answer = re.sub(u"([^\u0030-\u0039])","",values['-item_in-'])#只保留用户输入答案里的数字部分
        if user_inputs_answer == '':
            pass
        else:
            if i == 1:#孩子答了第一道题
                duration_one_item = current_time // 100  #第一道题的用时就是当前计时器的时间，无需减去前一道题的时间（实际前一道题的时间为0）
                duration_one_item_previous = duration_one_item
            else:#孩子答了第二道题及后面的题
                duration_one_item = (current_time // 100) - duration_one_item_previous#得到孩子做一道题所用的时间：当前计时器时间与上道题计时器时间的差值
                duration_one_item_previous = duration_one_item + duration_one_item_previous#将当前秒数写入buffer，等待被下个题目时再被减
            if user_inputs_answer == excel_list[i-1][1].strip():#孩子答题正确的情形
                excel_list[i-1].extend(['%-4s' % values['-item_in-'],'%-6s' % 'Pass','%-10s' % str(duration_one_item)])#把题库这个list增加对应的孩子实际的答案和结果这两个元素
                progress_history = progress_history + 'P'#本轮全部题目的孩子答案的正确错误记录
                window['-progress-'].update(i,bar_color=('green','yellow'))#当题目答错时，进度条会变绿
            else:#孩子答题错误的情形
                excel_list[i-1].extend(['%-4s' % values['-item_in-'],'%-6s' % 'Fail','%-10s' % str(duration_one_item)])
                progress_history = progress_history + 'F'
                window['-progress-'].update(i,bar_color=('red','yellow'))#当题目答错时，进度条会变红
            #print('excel_list is:',excel_list)
            if i == equation_amount :#当题目都答完时
                window['Next'].update(disabled=True)#使Next按钮不可见
                #print('Appended excel_list:',excel_list)
                window['-item_in-'].update('',disabled=True,background_color='grey')#不再让用户输入
                window['-item_disp-'].update('Result of this loop.' ,font=('Courier',20))#信息告示栏
                window['Start'].update(disabled=False)
                window['Summary'].update(disabled=False)
                set_time_initial = False#停止本轮计时
                if progress_history.count('P') == len(progress_history) and current_time <= expect_duration*60*100: #在规定时间内答对所有题目
                    window['-result-'].update(resultdisp(excel_list),visible=True,text_color='green',background_color='white')#在规定时间内且答题全对，解锁绿色字符提示
                else:
                    window['-result-'].update(resultdisp(excel_list),visible=True,text_color='black',background_color='orange')#显示本轮答题统计结果
                excel_list_old = excel_list #暂存本轮答题结果，_old用于后面可能的summary显示,不带old的用于写入excel
                for q in range(len(excel_list)):
                    excel_list_accumulation.append(excel_list[q])#把一个loop里的每一个答案都推进一个累积loop的list里，用于excel显示
                window['-multiline-'].print(resultdisp(excel_list_old))#攒好Summary要显示的内容，只待按钮按下
                window['-multiline-'].print('本轮答题用时：'+str((current_time // 100) // 60) +'分' + str((current_time // 100) % 60)+'秒。')
                window['-multiline-'].print(summary(excel_list_old))
                window['-multiline-'].print('----------------------------------------------------')
                excel_list = equation_creation(equation_amount,question_mode,scopeofcal,multiplication_mode)#题库更新，预备下个loop
                i = 0 #主要让i不在0到题目数量范围之间，让键盘enter在本轮中不起作用
                #每次答完题一个loop后，就自动生成Excel
                if len(excel_list_accumulation) < 1:
                    pass
                else:
                    df_summary=DataFrame(excel_list_accumulation[(-1*equation_amount):])#从累计的list中只抓出当loop的题目
                    df_summary.rename(columns={0:'Equations',1:'CorrectAns',2:'KidAns',3:'Result',4:'Duration/s'},inplace=True)
                    df_summary.to_excel(str('.\Math_Calculation_Tester_Out_'+time.strftime("%Y_%m_%d_%H_%M_%S", time.localtime())+'.xlsx'),sheet_name='Loops',startcol=0)#在py脚本所在的路径下生成report.excel.
            else:#没答完全部习题的情况
                window['-item_disp-'].update(excel_list[i][0].strip())#继续显示下道题
                i = i + 1 #当i为出题目数量+1时，代表Next阶段结束，Next按钮不激活，键盘也不起作用。
    elif event == 'Summary':#按下Summary按钮（可选）
        #print("excel_list_old is:",excel_list_old)
        window['-item_disp-'].update('Here is the Summary.', font=('Courier',20))
        window['-item_in-'].update('',disabled=True,background_color='grey')
        window['-multiline-'].update(visible=True)#使多行显示，此时会显示出之前攒好的-multiline-的内容
        window['Summary'].update(disabled=True)#按钮会变灰色，不可用
    else:
        pass
    #分支功能，参数自定义，及计时器计时
    if set_time_initial == True: #意味着点了开始按钮，计时器开始计时
        current_time = time_as_int() - start_time #求得相对时间，是ms为单位的整数
        window['-timer-'].update(str((current_time // 100) // 60) +'\'' + str((current_time // 100) % 60) + '\"')
    elif event == 'Readme':#点击菜单栏readme时弹出对话框,仅在计时器不计时即不答题时才会弹出。
        window.disappear()#主窗口不显示
        sg.popup(declare_info, grab_anywhere=True, title='Readme',line_width=69)#弹出小窗
        window.reappear()#主窗口恢复显示
    elif event == 'ScopeOfCal':#点击菜单栏ScopeOfCal时弹出对话框,仅在计时器不计时即不答题时才会弹出。#设置多少数值以内的加减法。
        window.disappear()#主窗口不显示
        scopeofcal_inputs_buffer = sg.popup_get_text(message='Please input your expected number:',title='Scope of Calculation', default_text='100')
        try: 
            if scopeofcal_inputs_buffer != None and re.findall("\d+",scopeofcal_inputs_buffer)[0] != None: #没有按窗口的Cancel按钮 即 按的是确认按钮 且 输入至少有一个数字（可能是数字和字母的组合）
                scopeofcal = int(re.findall("\d+",scopeofcal_inputs_buffer)[0]) #利用正则表达式，只提取输入字符串里的数字部分
                excel_list = equation_creation(equation_amount,question_mode,scopeofcal,multiplication_mode)#将当前出题组合导出至该变量内存储，excel_list是个列表
            else: #按的是Cancel按钮
                pass
        except: #如果出现输入毫无数字（比如输入为空或是输入全为非数字）等特殊场景
            print('No valid  inputs of Scope of Calculation, keep last used value.')
            pass
        window.reappear()#主窗口恢复显示
    elif event == 'TotalAmountofItems':#点击菜单栏TotalAmountofItems时弹出对话框,仅在计时器不计时即不答题时才会弹出。#设置一轮总共出多少道题。
        window.disappear()#主窗口不显示
        equation_amount_inputs_buffer = sg.popup_get_text(message='Please input your expected number:',title='Total amount of items per round', default_text='20')
        try:
            if  equation_amount_inputs_buffer != None and re.findall("\d+",equation_amount_inputs_buffer)[0] != None: #没有按Cancel按钮，按的是确认按钮 且 输入的数值不为空
                equation_amount = int(re.findall("\d+",equation_amount_inputs_buffer)[0])
                excel_list = equation_creation(equation_amount,question_mode,scopeofcal,multiplication_mode)#将当前出题组合导出至该变量内存储，excel_list是个列表
                window = main_window_format() #更新进度条的总长度;因没找到更好方法，就相当于重置了一次主窗口设置。
            else:
                pass
        except:
            print('No valid  inputs of Total amount of items per round, keep last used value.')
            pass
        window.reappear()#主窗口恢复显示
    elif event == 'X/':
        window.disappear()#主窗口不显示
        multiplication_mode_inputs_buffer = sg.popup_get_text(message='1 for multiplication and division, 0 for only plus and minus:',title='Desert multiplication&Division?', default_text='1')
        try:
            if  multiplication_mode_inputs_buffer != None and re.findall("\d+",multiplication_mode_inputs_buffer)[0] != None: #没有按Cancel按钮，按的是确认按钮 且 输入的数值不为空
                multiplication_mode = int(re.findall("\d+",multiplication_mode_inputs_buffer)[0])
                excel_list = equation_creation(equation_amount,question_mode,scopeofcal,multiplication_mode)#将当前出题组合导出至该变量内存储，excel_list是个列表
                window = main_window_format() #更新进度条的总长度;因没找到更好方法，就相当于重置了一次主窗口设置。
            else:
                pass
        except:
            print('No valid  inputs of calculation mode(+-X/), keep last used value.')
            pass
        window.reappear()#主窗口恢复显示
    elif event == 'HardMode':#点击菜单栏HardModel时弹出对话框,仅在计时器不计时即不答题时才会弹出。#Hard模式是相当于填空，比如1+[]=2，easy模式是答案都是在等号一边，如1+1=[]。
        window.disappear()#主窗口不显示
        question_mode_inputs_buffer = sg.popup_get_text(message='Please input your expected mode:[1:HardMode/0:EasyMode]',title='Hard Mode?', default_text='1') 
        try:
            if question_mode_inputs_buffer != None and re.findall("\d+",question_mode_inputs_buffer)[0] != None: #没有按Cancel按钮，按的是确认按钮 且 输入的数值不为空
                question_mode = int(re.findall("\d+",question_mode_inputs_buffer)[0])
                excel_list = equation_creation(equation_amount,question_mode,scopeofcal,multiplication_mode)#将当前出题组合导出至该变量内存储，excel_list是个列表
            else:
                pass
        except: #见equation_creation函数的定义，2022-5-4设定的是等于0为easy模式，其他值为hard模式。
            print('No valid  inputs of [1:HardMode/0:EasyMode], keep last used value.')
            pass
        window.reappear()#主窗口恢复显示
    else:
        pass
# Finish up by removing from the screen
window.Close()#主窗口关闭
