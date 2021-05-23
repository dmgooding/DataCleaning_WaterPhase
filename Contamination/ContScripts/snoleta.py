import numpy as np
import sys
import os
import argparse
import time

start_time = time.time()
def get_parser():
	parser = argparse.ArgumentParser(description='calculate contamination from snoleta approach')
	parser.add_argument('input_path', help='out files')

	return parser

def get_args(parser):
	args = parser.parse_args()
	return args

args = get_args(get_parser())

input_path = args.input_path
input_file_list = [file for file in os.listdir(input_path)]
A = []
B = []
C = []
D = []
for out in input_file_list:
	boxes = []
	file1 = open(str(input_path + '/' + out), 'r')
	for line in file1.readlines():
		data = (line.split(' ')[1]).split('\n')[0]
		boxes.append(data)
	A.append(int(float(boxes[0])))
	B.append(int(float(boxes[1])))
	C.append(int(float(boxes[2])))
	D.append(int(float(boxes[3])))

	file1.close()

A_total = sum(A)
B_total = sum(B)
C_total = sum(C)
D_total = sum(D)
fsac = open('AvgSac.dat', 'r')
for line in fsac.readlines():
	x1 = float(line.split(' ')[3])
	x2 = float(line.split(' ')[2])
#calculate contamination
num1 = float(B_total - ((1.0 - x1)/x1)*A_total)
num2 = float(C_total - ((1.0 - x2)/x2)*A_total)
den1 = float(D_total - (1.0-x2)*(1.0-x1))
den2 = float(A_total/(x1*x2))
NUM = float(num1*num2)
DEN = float(den1*den2)
contamination = float(NUM/DEN)

print("Contamination is: {}".format(contamination))
print("A {}".format(A_total))
print("B {}".format(B_total))
print("C {}".format(C_total))
print("D {}".format(D_total))

print("--- %s seconds ---" % (time.time() - start_time))
