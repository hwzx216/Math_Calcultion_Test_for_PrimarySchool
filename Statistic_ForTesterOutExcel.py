import pandas as pd
import sys
import os
import time


dfs = []
excel_src = r'D:\03_Document\OneDrive\02_HWToolRelease\2021-12-6_Math_Calculation_Tester_ForKakaBell\V1.9\dist'
#print(excel_src)
out_path = r'D:\03_Document\OneDrive\02_HWToolRelease\2021-12-6_Math_Calculation_Tester_ForKakaBell\V1.9\dist'
for root, dirs, filenames in os.walk(str(excel_src)):
    for i in range(len(filenames)):
        if str(filenames[i]).endswith('xlsx') and 'Statistic' not in str(filenames[i]):
            file_name_path = str(root + '\\' + str(filenames[i]))
            print('***Excuting:',file_name_path)
            #print(pd.read_excel('D:\\02_Scripts\\02_Python\\09_KakaSImpleCal\\SimpleCalculatorTester_Out_2021_12_06_21_56_51.xlsx', engine='openpyxl'))
            df = pd.read_excel(file_name_path,sheet_name='Loops',engine='openpyxl')
            excel_name = filenames[i].replace('.xlsx','')#提取文件名
            df['Filename'] = excel_name
            #print('df is:',df)
            dfs.append(df)#dfs needs to be a ‘List’
            #print('dfs is:',dfs)
        else:
            continue
#print('dfs is:',dfs)
df_concated = pd.concat(dfs,ignore_index=True)
df_concated.to_excel(out_path+'\Statistic_'+time.strftime("%Y_%m_%d_%H_%M_%S", time.localtime())+'.xlsx',sheet_name='Statistic',index=False)

