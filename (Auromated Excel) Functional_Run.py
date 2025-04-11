from csv import reader
from datetime import date, datetime
import xlsxwriter
import serial
import os.path

file_path = "F:\Thesis\Testing\(Auromated Excel) Functional_Run"
d1 = datetime.now()
file_name1 = 'Functional_run'+d1.strftime("(%Y%m%d%H%M%S)")
fileName1=file_path + file_name1+".csv"

d2 = datetime.now()
file_name2 = 'Functional_run_Calc'+d1.strftime("(%Y%m%d%H%M%S)")
fileName2=file_path + file_name2+".xlsm"

today = date.today()
d3 = today.strftime("%d-%m-%Y")
book = xlsxwriter.Workbook(fileName2)
worksheet = book.add_worksheet('Sheet2')

#uncomment the code below to take input from arduino
#Change current COM port on your laptop in place of COM5 when needed
ser = serial.Serial('COM14', 115200, timeout=1)
file = open(fileName1, "a")
print("Created file")
os.path.exists(fileName1)
def get_reading(ser):
  if ser.isOpen():
    samples = 90
    line = 0
    while line <=samples: 
      result1 = ser.readline().decode('utf-8').replace("\t",",")
      ser.write(b'2')
      print(result1)
      #add the data to the file
      file = open(fileName1, "a", newline='')#append the data to the file
      file.write(result1) #write data with a newline
      result2 = ser.readline().decode('utf-8').replace("\t",",")
      ser.write(b'2')
      print(result2)
      #add the data to the file
      file = open(fileName1, "a", newline='') #append the data to the file
      file.write(result2) #write data with a newline
      line = line + 1
get_reading(ser)
#close out the file
file.close()

merge_format1 = book.add_format({'align': 'center', 'valign': 'vcenter', 'border': 2, 'border_color':'black','bg_color':'#BDD7EE'})
merge_format2 = book.add_format({'align': 'center', 'valign': 'vcenter','bg_color':'#E2EFDA', 'text_wrap': True})
merge_format3 = book.add_format({'align': 'center', 'valign': 'vcenter','bg_color':'#FF9FF1','bottom':2, 'text_wrap': True})
format1 = book.add_format({'bg_color':'#BDD7EE'})
format2 = book.add_format({'bg_color':'#D9D9D9'})
format5 = book.add_format({'bg_color':'#FFF2CC'})
format3 = book.add_format({'bg_color':'#FFF2CC','top':2}) # green
format4 = book.add_format({'bg_color':'#FFF2CC','bottom':2})
format6 = book.add_format({'bg_color':'#FF9FF1','top':2}) # pink
format7 = book.add_format({'bg_color':'#FF9FF1'})
format8 = book.add_format({'bg_color':'#FF9FF1','bottom':2})
merge_format2.set_font_size(10)

with open("F:/Thesis/Testing/Functional/Functional drive 25.csv", 'r') as read_obj:
#with open(fileName1, 'r') as read_obj:
    # pass the file object to reader() to get the reader object
    csv_reader = reader(read_obj)
    for r, row in enumerate(csv_reader):
            for c, col in enumerate(row):
                worksheet.write(r, c, col)

worksheet.set_column(0, 0, 3.71)
worksheet.set_column(1, 1, 6)
worksheet.set_column(6, 7, 3.57, format2)
worksheet.set_column(2, 5, 10.71)
worksheet.set_column(8, 9, 10.71)
worksheet.set_column(10, 10, 3.57, format2)
worksheet.set_column(11, 14, 10.71)
worksheet.set_column(15, 15, 3.57, format2)
worksheet.set_column(16, 17, 10.71)
worksheet.set_column(18, 18, 3.57, format2)
worksheet.set_column(19, 20, 10.71)
worksheet.set_column(21, 21, 3.57, format2)
worksheet.set_column(22, 23, 10.71)
worksheet.set_column(24, 24, 3.57, format2)
worksheet.set_column(25, 26, 10.71)
worksheet.set_column(27, 27, 3.57, format2)
worksheet.set_column(28, 29, 10.71)
worksheet.set_column(30, 30, 3.57, format2)

worksheet.merge_range('I17:J17','Differential Output', merge_format1)
worksheet.write('I18', "Y_Sin_Diff",format1)
worksheet.write('J18', "X_Cos_Diff",format1)
worksheet.merge_range('L17:O17','Curve Fitting', merge_format1)
worksheet.write('L18', "Sin_Fit",format1)
worksheet.write('M18', "Residual^2",format1)
worksheet.write('N18', "",format1)
worksheet.write('O18', "",format1)
worksheet.merge_range('Q17:R17','Offset Compensation', merge_format1)
worksheet.write('Q18', "Y1_Sin",format1)
worksheet.write('R18', "X1_Cos",format1)
worksheet.merge_range('T17:U17','Gain Compensation', merge_format1)
worksheet.write('T18', "Y2_Sin",format1)
worksheet.write('U18', "X2_Cos",format1)
worksheet.merge_range('W17:X17','Orthogonality & Angle', merge_format1)
worksheet.write('W18', "Y3_Sin",format1)
worksheet.write('X18', "alpha[deg]",format1)
worksheet.write('X19', "=IF(MOD(ATAN2(U19,W19)*180/PI()-$J$9+360,360)>5,MOD(ATAN2(U19,W19)*180/PI()-$J$9+360,360)-360,MOD(ATAN2(U19,W19)*180/PI()-$J$9+360,360))",format1)
worksheet.merge_range('Z17:AA17','Encoder', merge_format1)
worksheet.write('Z18', "θ[deg]",format1)
worksheet.write('AA18', "θ[rad]",format1)
worksheet.write('Z19', "=360/40000*B19",format1)
worksheet.merge_range('AC17:AD17','Angle Error & Hysteresis', merge_format1)
worksheet.write('AC18', "Angle_Error",format1)
worksheet.write('AD18', "Hysteresis",format1)
for i in range(18, 148):
    worksheet.write(i, 8, f'=C{i+1}-E{i+1}',format1)
    worksheet.write(i, 9, f'=D{i+1}-F{i+1}',format1)
    worksheet.write(i, 12, f'=(W{i+1}-L{i+1})^2',format1)
    worksheet.write(i, 13, '',format1)
    worksheet.write(i, 14, '',format1)
    worksheet.write(i, 16, f'=I{i+1}-$J$4',format1)
    worksheet.write(i, 17, f'=J{i+1}-$J$3',format1)
    worksheet.write(i, 19, f'=Q{i+1}/$J$7',format1)
    worksheet.write(i, 20, f'=R{i+1}/$J$6',format1)
    worksheet.write(i, 22, f'=(T{i+1}-U{i+1}*SIN(-$J$11*PI()/180))/(COS(-$J$11*PI()/180))',format1)
    worksheet.write(i, 26, f'=Z{i+1}*PI()/180',format1)
    worksheet.write(i, 28, f'=X{i+1}/1000-Z{i+1}/1000',format1)
    worksheet.write(i, 29, f'=@INDIRECT("AC"&AE{i+1})-AC{i+1}',format1)
    if i >= 19:
        worksheet.write(i, 23, f'=MOD(ATAN2(U{i+1},W{i+1})*180/PI()-$J$9+360,360)',format1)
        worksheet.write(i, 25, f'=360/40000*B{i+1}+Z{i}',format1)
v = 148
for i in range(18, 85):
    worksheet.write(i, 11, f'=$M$3*SIN(2*PI()/$M$4*($Z{i+1}+$M$5))+$M$6',format1)
    worksheet.write(i, 30, f'{v}')
    v = v - 1
for i in range(85, 148):
    worksheet.write(i, 11, f'=$O$3*SIN(2*PI()/$O$4*($Z{i+1}+$O$5))+$O$6',format1)

worksheet.merge_range('I1:J2','Curve parameters from three calibration runs ↓', merge_format2)
worksheet.merge_range('I12:J13','Worksheet names of the three calibration runs ↓', merge_format2)
worksheet.merge_range('L1:O2','Curve parameters of corrected "Y3_Sin" curve by fitting method', merge_format2)
worksheet.merge_range('L9:O10','Average curve parameters (FF) from cw/ccw ↓', merge_format2)
worksheet.merge_range('Q2:R2','Max angle error', merge_format2)
worksheet.merge_range('Q6:R6','Max Hysterese', merge_format2)
worksheet.merge_range('Q10:R10','Max Non-Ortho', merge_format2)

dict1 = {'I3': format3, 'I4': format4, 'I6': format3, 'I7': format4, 'I9':format3, 'I10':format5, 'I11':format4}
L2 = ['O_X_M','O_Y_M','A_X_M','A_Y_M','ϕ_X_M', 'ϕ_Y_M', 'ϕ_M']
L1 = []
for k, v in dict1.items():
    L1.append(k)
for num in range(len(L2)):  
    worksheet.write(L1[num], L2[num], dict1[L1[num]])
    
worksheet.write('J3', "=AVERAGE(INDIRECT(\"'\"&I14&\"'!\"&\"J3\",TRUE))", format3)
worksheet.write('J4', "=AVERAGE(INDIRECT(\"'\"&I14&\"'!\"&\"J4\",TRUE))", format4)
worksheet.write('J6', "=AVERAGE(INDIRECT(\"'\"&I14&\"'!\"&\"J6\",TRUE))", format3)
worksheet.write('J7', "=AVERAGE(INDIRECT(\"'\"&I14&\"'!\"&\"J7\",TRUE))", format4)
worksheet.write('J9', "=AVERAGE(INDIRECT(\"'\"&I14&\"'!\"&\"J9\",TRUE))", format3)
worksheet.write('J10',"=AVERAGE(INDIRECT(\"'\"&I14&\"'!\"&\"J10\",TRUE))", format5)
worksheet.write('J11',"=AVERAGE(INDIRECT(\"'\"&I14&\"'!\"&\"J11\",TRUE))", format4)

f1 = book.add_format({'top': 2})
f2 = book.add_format({'top': 2, 'right':2})
f3 = book.add_format({'right':2})
f4 = book.add_format({'bottom': 2, 'right':2})
f5 = book.add_format({'bottom': 2})
dic = {'L3': ["A_Y_cw", f1], 'M3': ["=8000", f2 ],'M4':["=360", f3],'M5':["=-180", f3],  
        'M6':["=0", f3], 'L7':["SSD",f5],'M7':["=SUM(M19:M83)",f4], 'N3':["A_Y_ccw",f1],
        'O3':["=-8000", f1], 'N7':["SSD", f5], 'O7':["=SUM(M84:M148)", f5]}
dic1={'L4':"f_Y_cw",'L5':"ϕ_Y_cw",'L6':"O_Y_cw", 'N4':"f_Y_ccw", 'O4':"=-360", 
    'N5':"ϕ_Y_ccw", 'O5':"=-180", 'N6':"O_Y_ccw", 'O6':"=0"}
dic2= {'L11': ["O_Y3_M",format3], 'L12':["f_Y3_M", format5], 'L13':["ϕ_Y3_M", format4],
        'M11':["=(M6+O6)/2",format3], 'M12':["=(M3+O3)/2", format5], 'M13':["=(M5+O5)/2", format4],
        'T3':["Datum",format6], 'U3':[d3 ,format6], 'T4':["Sensor", format7], 'U4':["Infineon", format7],
        'T5':["Sensor_ID", format7], 'U5':[" ", format7], 'T6':["Abstand",format7], 'U6':["4,4 mm",format7]
        }
for k, v in dic.items():
    worksheet.write(k, v[0], v[1])
for k, v in dic1.items():
    worksheet.write(k, v)
for k, v in dic2.items():
    worksheet.write(k, v[0], v[1])

book.add_vba_project('./vbaProject.bin')
worksheet.insert_button(
   'L15:O16',
   {'macro': 'Makro2',
      'caption': 'Click here to fit "Y3_Sin"',
      'width': 318, 'height': 30, 'color': '#FFDD9C'
   })

worksheet.merge_range('N11:O11', "", format3)
worksheet.merge_range('N12:O12', "", format5)
worksheet.merge_range('N13:O13', "", format4)

def output_block(n1,n2, i, j):
    worksheet.write(f'Q{n1}', "positiv", format3)
    worksheet.write(f'Q{n2}', "negativ", format4)
    worksheet.write(f'R{n1}', f"=MAX({i}:{j})",format3)
    worksheet.write(f'R{n2}', f"=MIN({i}:{j})", format4)
output_block(3,4, 'AC20', 'AC148')
output_block(7,8, ' AD20', 'AD83')
output_block(11,12, 'W19', 'W148')

worksheet.merge_range('T7:T8', "delay zw. Microsteps", merge_format3)
worksheet.merge_range('U7:U8', "250 us", merge_format3)

chart = book.add_chart({'type': 'scatter', 'subtype': 'smooth'})
chart.set_title({'name': 'Angular error & hysteresis of the function measurement from the differential output','name_font': {'name':'Calibri', 'size':14, 'align': 'center', 'bold':False} })
worksheet.insert_chart('W1', chart, {'x_scale': 1.6, 'y_scale': 1.1})
chart.set_legend({'position': 'bottom', 'name_font': {'name':'Calibri', 'size': 9, 'align': 'center', 'bold':False}})
chart.set_y_axis({'min': '-0.5','max': '0.5'})

series_dict = {'cw':['=Sheet2!$Z$19:$Z$83', '=Sheet2!$AC$19:$AC$83', {'color': 'blue'}],
'ccw':['=Sheet2!$Z$84:$Z$148', '=Sheet2!$AC$84:$AC$148', {'color': 'orange'}],
'hysteresis':['=Sheet2!$Z$19:$Z$83', '=Sheet2!$AD$19:$AD$83', {'color': '#A5A5A5'}]}
for k, v in series_dict.items():
    chart.add_series({
        'name':k,
        'categories':v[0],
        'values':v[1],
        'line': v[2]})
book.close()