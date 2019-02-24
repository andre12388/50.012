import random
import datetime
import xlwt
from xlwt import Workbook
import matplotlib.pyplot as pyplot
import matplotlib.animation as animation
from matplotlib import style
import socket

# Generate a random output data
def sampleOutputGen():
    dirt = random.randint(1,90)
    bacteria = random.randint(1,90)
    ph = random.randint(1,90)
    vitamins = random.randint(1,90)
    water = random.randint(1,800)
    output = [dirt,bacteria,ph,vitamins,water]
    return output

def unpack(packet):
	input_str, output_str = str.split(packet.decode("utf-8"),'|')
	input_str_batch = input_str.split(',')
	output_str_batch = output_str.split(',')
	input_batch = []
	output_batch = []
	for i in range(len(input_str_batch)):
		input_batch.append(float(input_str_batch[i]))
		output_batch.append(float(output_str_batch[i]))
	return input_batch, output_batch

# Return a string status of the data
def statusChecker (output):
    dirt = output[0]
    bacteria = output[1]
    ph = output[2]
    vitamins = output[3]
    water = output[4]
    currentStatus = ["nil","nil","nil","nil"]
    if(dirt>5):
        currentStatus[0] = "WARNING!, water is dirty!"
    else:
        currentStatus[0] = "dirt level okay!"

    if(bacteria>5):
        currentStatus[1] = "WARNING!, bacteria level is too high!"
    else:
        currentStatus[1] = "bacteria level okay!"

    if (round(ph / water, 4)*100 > 5):
        currentStatus[2] = "WARNING!, ph is not stable!"
    else:
        currentStatus[2] = "ph level okay!"

    if (round(vitamins / water, 4)*100 > 5):
        currentStatus[3] = "WARNING!, vitamins is not stable!"
    else:
        currentStatus[3] = "vitamins level okay!"
    return currentStatus

# Select font style depending on the status of the data
def fontStyleSelector(status):
    if ("WARNING" in status):
        style = xlwt.easyxf('font: bold 1, color red;')
    else:
        style = xlwt.easyxf('font: color green;')
    return style

# Workbook is created
wb = Workbook()

# Add_sheet is used to create sheet.
sheet1 = wb.add_sheet('Sheet 1')

# Labeling
sheet1.write(0, 0, 'Time Stamp')
sheet1.write(0, 1, 'Dirt Level')
sheet1.write(0, 2, 'Dirt Status')

sheet1.write(0, 3, 'Bacteria Level')
sheet1.write(0, 4, 'Bacteria Status')

sheet1.write(0, 5, 'Ph Level')
sheet1.write(0, 6, 'Ph Status')

sheet1.write(0, 7, 'Vitamin Level')
sheet1.write(0, 8, 'Vitamin Status')

sheet1.write(0, 9, 'Water Level')

open("dataSet_dirt.txt", 'w+')
open("dataSet_bacteria.txt", 'w+')
open("dataSet_ph.txt", 'w+')
open("dataSet_vitamin.txt", 'w+')

# # A) Simulation of writing data to excel sheet
# for i in range(200):
#     output = sampleOutputGen()
#
#     # Writing raw data to dataSet.txt for live graph
#     with open("dataSet.txt", 'a') as out:
#         data = str(i)+","+str(output[0])
#         out.write(str(data) + '\n')
#
#     # Writing to excel sheet
#     allStatus = statusChecker(output)
#     print(i)
#
#     sheet1.write(i+1,0,str(datetime.datetime.now()))
#     sheet1.write(i+1,1,output[0])
#     sheet1.write(i+1,2,allStatus[0])
#
#     sheet1.write(i+1,3,output[1])
#     sheet1.write(i+1,4,allStatus[1])
#
#     sheet1.write(i+1,5,output[2])
#     sheet1.write(i+1,6,allStatus[2])
#
#     sheet1.write(i+1,7,output[3])
#     sheet1.write(i+1,8,allStatus[3])
#
#     sheet1.write(i+1,9,output[4])
#
# fileName = str(datetime.datetime.now())
# fileName = fileName.replace('-','_')
# fileName = fileName.replace('.',' ')
# fileName = fileName.replace(':','#')
# wb.save(str(fileName)+".xls")

# B) Receiving data from the plantation
socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
plant_address = "10.0.0.92"
port = 1024
try:
    socket.connect((plant_address, port))
    print("Connection Successful")
except:
    print("Connection Failed")

numberOfData = 0
numberOfSheet = 0
while True:
    data = socket.recv(1024)
    if not data:
        break
    output = unpack(data)[1]
    print (output)
    allStatus = statusChecker(output)

    # Writing raw data to dataSet.txt for live graph
    with open("dataSet_dirt.txt", 'a') as out:
        data = str(numberOfData)+","+str(output[0])
        out.write(str(data) + '\n')

    with open("dataSet_bacteria.txt", 'a') as out:
        data = str(numberOfData)+","+str(output[1])
        out.write(str(data) + '\n')

    with open("dataSet_ph.txt", 'a') as out:
        data = str(numberOfData)+","+str(output[2])
        out.write(str(data) + '\n')

    with open("dataSet_vitamin.txt", 'a') as out:
        data = str(numberOfData)+","+str(output[3])
        out.write(str(data) + '\n')

    sheet1.write(numberOfData + 1, 0, str(datetime.datetime.now()))
    sheet1.write(numberOfData + 1, 1, output[0])
    sheet1.write(numberOfData + 1, 2, allStatus[0],fontStyleSelector(allStatus[0]))

    sheet1.write(numberOfData + 1, 3, output[1])
    sheet1.write(numberOfData + 1, 4, allStatus[1],fontStyleSelector(allStatus[1]))

    sheet1.write(numberOfData + 1, 5, output[2])
    sheet1.write(numberOfData + 1, 6, allStatus[2],fontStyleSelector(allStatus[2]))

    sheet1.write(numberOfData + 1, 7, output[3])
    sheet1.write(numberOfData + 1, 8, allStatus[3],fontStyleSelector(allStatus[3]))

    sheet1.write(numberOfData + 1, 9, output[4])

    if numberOfData == 100:
        print ("END")
        numberOfData=0
        numberOfSheet+=1
        open("dataSet_dirt.txt", 'w+')
        open("dataSet_bacteria.txt", 'w+')
        open("dataSet_ph.txt", 'w+')
        open("dataSet_vitamin.txt", 'w+')
        fileName = str(datetime.datetime.now())
        fileName = fileName.replace('-', '_')
        fileName = fileName.replace('.', ' ')
        fileName = fileName.replace(':', '#')
        wb.save(str(fileName) + ".xls")
        wb = Workbook()
        sheetName = "Sheet" + str(numberOfSheet)
        sheet1 = wb.add_sheet(sheetName)
        # Labeling
        sheet1.write(0, 0, 'Time Stamp')
        sheet1.write(0, 1, 'Dirt Level')
        sheet1.write(0, 2, 'Dirt Status')

        sheet1.write(0, 3, 'Bacteria Level')
        sheet1.write(0, 4, 'Bacteria Status')

        sheet1.write(0, 5, 'Ph Level')
        sheet1.write(0, 6, 'Ph Status')

        sheet1.write(0, 7, 'Vitamin Level')
        sheet1.write(0, 8, 'Vitamin Status')

        sheet1.write(0, 9, 'Water Level')
    else:
        print ("CONTINUE")
        numberOfData+=1
socket.close()
