import uproot
import ROOT
#import matplotlib.dates as dates
import datetime
import os
#import matplotlib.pyplot as plot
import sys
import argparse
#from matplotlib.backends.backend_pdf import PdfPages
import numpy as np
import rootreader as rr
import time
start_time = time.time()

def get_parser():
	parser = argparse.ArgumentParser(description='nutple input, txt file output of all data cleaning cuts and number of passes for each')
	parser.add_argument('input_path', help='nutuple from Aobo')
	parser.add_argument('root_name', help='output root name')
	
	return parser

def get_args(parser):
	args = parser.parse_args()
	return args

args = get_args(get_parser())

#Get data from directory wide
input_path = args.input_path
input_file_list = [file for file in os.listdir(input_path)]


#initiate progress printed to terminal
length = len(input_file_list)
m = 0

nbins = 41
first_bin = -1.0
last_bin = 1.0
DCsac = ROOT.TH1F('DCsac', 'DC', nbins, first_bin, last_bin)
CCsac = ROOT.TH1F('CCsac', 'CC', nbins, first_bin, last_bin)
Total = ROOT.TH1F('Total', 'all', nbins, first_bin, last_bin)

for ntuple in input_file_list: #loop over files in a directory
	PassClassIndices = []
	#############################
	#syntax I still don't understand - don't delete!! 
	#neckcut = (data.dcFlagged & 32)
	#neckpassed = neckcut[neckcut == 32] 
	#############################
	
	full_path = str(input_path + ntuple) #get the full path name to the file
	data = rr.rootreader(full_path) #root reader magic on this file
	
	m +=1 #counter to show progress through files
	
	#PrelimMask = 0b11110110000000000000000000000000100000011100010
	PrelimMask = int(239693534871552)
	#DCMask = 0b10001111000011100
	DCMask = int(36283883798270)
	TrigMask_path = int(5216)
	TrigMask_DC = int(512)
	#TrigMask_path = 0b00010
	#TrigMask_DC = 0b11101
	
	PrelimpassIndices = np.where((data.dcFlagged & PrelimMask) == PrelimMask)[0]
	
	TotalDCMask = PrelimMask + DCMask
	
	PassIndices = np.where((data.dcFlagged & TotalDCMask) == TotalDCMask)[0]
	
	TotalTrigDC = TrigMask_path + TrigMask_DC
	DCTrigPass = np.where((data.triggerWord & TotalTrigDC) == 0)[0]	
	CCTrigPass = np.where((data.triggerWord & TrigMask_path) ==0)[0]
	PathTrigPass = np.where((data.triggerWord & TrigMask_path) ==0)[0]


	E_HIGH = 5.0 #mev
	E_LOW = 2.5 #mev
	POSR_CUT_LOW = 5700.0 #mm
	POSR_CUT_HIGH = 6300.0 #mm
	Z_LOW = -1500.0 #mm
	Z_HIGH = 3500.0 #mm
	nhitsCleaned_LOW = 15
	nhitsCleaned_HIGH = 39
	udotr_LOW = 0.0
	
	for i in PassIndices: #This one is okay
		if i not in DCTrigPass:
			continue
		if data.fitValid[i] == False:
			continue
		if data.isCal[i] == False:
			continue
		if data.energy[i] >= E_HIGH:
			continue
		if data.energy[i] <= E_LOW:
			continue
		if data.posr[i] >= POSR_CUT_HIGH:
			continue
		if data.posr[i] <= POSR_CUT_LOW:
			continue
		if data.posz[i] <= Z_LOW:
			continue
		if data.posz[i] >= Z_HIGH:
			continue
		if data.nhitsCleaned[i] >= nhitsCleaned_HIGH:
			continue
		if data.nhitsCleaned[i] <= nhitsCleaned_LOW:
			continue
		u = data.dirx[i]*data.posx[i] + data.diry[i]*data.posy[i] + data.dirz[i]*data.posz[i]
		n = np.sqrt(data.posx[i]**2 + data.posy[i]**2 + data.posz[i]**2)
		udotr = u/n
		if udotr <= udotr_LOW:
			continue
		DCsac.Fill(data.udotr[i])
	
	for j in PrelimpassIndices: #This needs to be histogram of everythign that passed prelim ****put iscal here****
		if j not in PathTrigPass:
			continue
		if data.fitValid[j] == False:
			continue
		if data.isCal[j] == False:
			continue
		if data.energy[j] >= E_HIGH:
			continue
		if data.energy[j] <= E_LOW:
			continue
		if data.posr[j] >= POSR_CUT_HIGH:
			continue
		if data.posr[j] <= POSR_CUT_LOW:
			continue
		if data.posz[j] <= Z_LOW:
			continue
		if data.posz[j] >= Z_HIGH:
			continue
		if data.nhitsCleaned[j] >= nhitsCleaned_HIGH:
			continue
		if data.nhitsCleaned[j] <= nhitsCleaned_LOW:
			continue
		u = data.dirx[j]*data.posx[j] + data.diry[j]*data.posy[j] + data.dirz[j]*data.posz[j]
		n = np.sqrt(data.posx[j]**2 + data.posy[j]**2 + data.posz[j]**2)
		udotr = u/n
		if udotr <= udotr_LOW:
			continue
		Total.Fill(data.udotr[j])
	
	for p, event in enumerate(data.dcFlagged):
		if p not in PrelimpassIndices:
			continue
		if p not in CCTrigPass:
			continue
		if -0.12 < data.beta14[p] < 0.95 and data.itr[p] > 0.55 and data.isCal[p] == True:
			PassClassIndices.append(p)    
	for index in PassClassIndices:
		if data.fitValid[index] == False:
			continue
		if data.isCal[index] == False:
			continue
		if data.energy[index] >= E_HIGH:
			continue
		if data.energy[index] <= E_LOW:
			continue
		if data.posr[index] >= POSR_CUT_HIGH:
			continue
		if data.posr[index] <= POSR_CUT_LOW:
			continue
		if data.posz[index] <= Z_LOW:
			continue
		if data.posz[index] >= Z_HIGH:
			continue
		if data.nhitsCleaned[index] >= nhitsCleaned_HIGH:
			continue
		if data.nhitsCleaned[index] <= nhitsCleaned_LOW:
			continue
		u = data.dirx[index]*data.posx[index] + data.diry[index]*data.posy[index] + data.dirz[index]*data.posz[index]
		n = np.sqrt(data.posx[index]**2 + data.posy[index]**2 + data.posz[index]**2)
		udotr = u/n
		if udotr <= udotr_LOW:
			continue
		CCsac.Fill(data.udotr[index]) 

output = args.root_name
file1 = ROOT.TFile(output, 'RECREATE')
CCsac.Write()
DCsac.Write()
Total.Write()
file1.Close()

#add1 = ROOT.TH1F('add1', 'all', nbins, first_bin, last_bin)
#for i in range(nbins):
#	add1.SetBinContent(i,1.0)
#
#DCsac.Divide(Total)#divide by pass prelim
#DCsac.Scale(-1.0)
#DCsac.Add(add1)

#DCfit = ROOT.TF1("DCfit", "pol1(0)", 30, 45)
#DCfit.SetParameter(0,0.02)
#DCfit.SetParameter(1,0.00000001)
#
#CCfit = ROOT.TF1("CCfit", "pol1(0)", 30, 45)
#CCfit.SetParameter(0,0.02)
#CCfit.SetParameter(1,0.00000001)
#
#CCsac.Divide(Total)
#CCsac.Scale(-1.0)
#CCsac.Add(add1)
#
#DCsac.Fit(DCfit, "RN0")
#CCsac.Fit(CCfit, "R")
#
#Outname = "AvgSac.dat"
#outfile = open(Outname, 'a')
#outfile.write('CC DC')
#outfile.write(' ')
#outfile.write(str(CCfit.GetParameter(0)))
#outfile.write(' ')
#outfile.write(str(DCfit.GetParameter(0)))


print("--- %s seconds ---" % (time.time() - start_time))

