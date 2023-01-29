::此为注释This is comments
::using upx to possible reduce the size of outputs from pyinstaller. 

@echo on
pyinstaller.exe -F "Math_Calculation_Tester_V1.9.py" -w --upx-exclude=vcruntime140.dll 

pause