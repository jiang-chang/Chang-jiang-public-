import xlrd
import os
from configparser import ConfigParser


wb = xlrd.open_workbook('Directory.xlsx')
ws = wb.sheet_by_name('Class 14')
row = ws.nrows
col = ws.ncols
Start_row = 1
Start_col = 0
index = 0
Tel = []
Name = []


#Search the name in Class 14 sheet
def NameList(ws):
    cols = Start_col
    rows = Start_row
    Name = []
    while rows < row:
        if ws.cell_value(rows,cols) != "":
            Name.append(ws.cell_value(rows,cols))
            rows += 1
    return Name

#Search the name in Class 14 sheet
def TelList(ws):
    cols = Start_col
    rows = Start_row
    Tel = []
    while rows < row:
        if ws.cell_value(rows,cols) != "":
            Tel.append(ws.cell_value(rows,cols+1))
            rows += 1
    return Tel

Name = NameList(ws)
Tel = TelList(ws)

filename = "Directory.txt"

with open(filename,"w", encoding="utf-8") as f:
    for index in range(len(Name)):
        name = str(Name[index]).replace("'", '').replace("'", '')
        name_N = "N;CHARSET=UTF-8:" + name + "\n"
        name_FN = "FN;CHARSET=UTF-8:" + name + "\n"
        tel_temp = str(Tel[index]).replace("'", '').replace("'", '')
        tel = "TEL;CELL;VOICE:" + tel_temp + "\n"
        f.write("BEGIN:VCARD\n")
        f.write("VERSION:2.1\n")
        #N;CHARSET = UTF - 8
        f.write(name_N)
        #FN;CHARSET=UTF-8
        f.write(name_FN)
        f.write(tel)
        f.write("END:VCARD\n")

















