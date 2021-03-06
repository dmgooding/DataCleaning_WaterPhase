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

nbins = 21
first_bin = -1.0
last_bin = 1.0
DCsac = ROOT.TH1F('DCsac', 'DC', nbins, first_bin, last_bin)
CCsac = ROOT.TH1F('CCsac', 'CC', nbins, first_bin, last_bin)
Total = ROOT.TH1F('Total', 'all', nbins, first_bin, last_bin)

B14_ITR_signal = ROOT.TH2F('signal', "contamination in data set;ITR; Beta_14", nbins, 0.0, 1.0, nbins, -0.5, 2.0)
B14_ITR_bg = ROOT.TH2F('instrumentals', "contamination in data set;ITR; Beta_14", nbins, 0.0, 1.0, nbins, -0.5, 2.0)

for ntuple in input_file_list: #loop over files in a directory
	dcpass = []
	ccpass = []
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
	#PrelimMask = int(275977418670078) incorrect; corrected below
	PrelimMask = int(239693534871552)
	#DCMask = 0b10001111000011100
	#DCMask = int(73244) #incorrect; corrected below
	DCMask = int(36283883798270)
	TrigMask_path = int(5216)
	TrigMask_DC = int(512)
	#TrigMask_path = 0b00010
	#TrigMask_DC = 0b11101
	
	#PrelimpassIndices = np.where((data.dcFlagged & PrelimMask) == PrelimMask)[0]
	bg1 = np.where((data.dcFlagged & int(4)) != int(4))[0]
	bg2 = np.where((data.dcFlagged & int(8)) != int(8))[0]
	bg3 = np.where((data.dcFlagged & int(16)) != int(16))[0]
	bg = np.concatenate([bg1, bg2, bg3])
	
	#TotalDCMask = PrelimMask + DCMask
	PrelimpassIndices = np.where((data.triggerWord & TrigMask_path) == 0)[0]
	TotalDCMask = DCMask
	
	PassIndices = np.where((data.dcFlagged & TotalDCMask) == TotalDCMask)[0]
	
	TotalTrigDC = TrigMask_path + TrigMask_DC
	DCTrigPass = np.where((data.triggerWord & TotalTrigDC) == 0)[0]	
	CCTrigPass = np.where((data.triggerWord & TrigMask_path) ==0)[0]
	PathTrigPass = np.where((data.triggerWord & TrigMask_path) ==0)[0]


	E_HIGH = 10.0 #mev
	E_LOW = 5.0 #mev
	POSR_CUT_LOW = 5550.0 #mm
	#POSR_CUT_HIGH = 5550.0 #mm
	POSR_CUT_HIGH = 5100.0 #mm
	Z_LOW = -6000.0 #mm
	#Z_HIGH = 6000.0 #mm
	Z_HIGH = 1500.0 #mm
	nhitsCleaned_LOW = 15
	nhitsCleaned_HIGH = 39
	udotr_LOW = -1.0
	udotr_HIGH = 1.0
	B14_LOW = -0.12
	B14_HIGH = 0.95
	ITR = 0.55
	IN_TIME_HITS100 = 10
	sunct_HIGH = 1.0
	sunct_LOW = -1.0
	
	
	for i in PassIndices: #This one is okay
		if i not in DCTrigPass:
			continue
		if data.fitValid[i] == False:
			continue
		if data.waterFit[i] == False:
			continue
		if data.isCal[i] == False:
			continue
		#if data.inTimeHits100[i] < IN_TIME_HITS100:
		#	continue
	##	if data.beta14[i] <= B14_LOW:
	#		continue
	#	if data.beta14[i] >= B14_HIGH:
	#		continue
	#	if data.itr[i] <= ITR:
	#		continue
		if data.energy[i] >= E_HIGH:
			continue
		if data.energy[i] <= E_LOW:
			continue
		if data.posr[i] >= POSR_CUT_HIGH:
			continue
		#if data.posr[i] < POSR_CUT_LOW:
		#	continue
		if data.posz[i] <= Z_LOW:
			continue
		if data.posz[i] >= Z_HIGH:
			continue
		#if data.nhitsCleaned[i] > nhitsCleaned_HIGH:
		#	continue
		#if data.nhitsCleaned[i] < nhitsCleaned_LOW:
		#	continue
		u = data.dirx[i]*data.posx[i] + data.diry[i]*data.posy[i] + data.dirz[i]*data.posz[i]
		n = np.sqrt(data.posx[i]**2 + data.posy[i]**2 + data.posz[i]**2)
		udotr = u/n
		if udotr <= udotr_LOW:
			continue
		if udotr >= udotr_HIGH:
			continue
		if data.sunct[i] <= sunct_LOW:
			continue
		if data.sunct[i] >= sunct_HIGH:
			continue
		DCsac.Fill(data.udotr[i])
		dcpass.append(i)
	debugging = []	
	for j in PrelimpassIndices: #This needs to be histogram of everythign that passed prelim ****put iscal here****
		if j not in PathTrigPass:
			continue
		if data.fitValid[j] == False:
			continue
		if data.waterFit[j] == False:
			continue
		if data.isCal[j] == False:
			continue
		#if data.inTimeHits100[j] < IN_TIME_HITS100:
		#	continue
	#	if data.beta14[j] <= B14_LOW:
	#		continue
	#	if data.beta14[j] >= B14_HIGH:
	#		continue
	#	if data.itr[j] <= ITR:
	#		continue
		if data.energy[j] >= E_HIGH:
			continue
		if data.energy[j] <= E_LOW:
			continue
		if data.posr[j] >= POSR_CUT_HIGH:
			continue
		#if data.posr[j] < POSR_CUT_LOW:
		#	continue
		if data.posz[j] <= Z_LOW:
			continue
		if data.posz[j] >= Z_HIGH:
			continue
		#if data.nhitsCleaned[j] > nhitsCleaned_HIGH:
		#	continue
		#if data.nhitsCleaned[j] < nhitsCleaned_LOW:
		#	continue
		u = data.dirx[j]*data.posx[j] + data.diry[j]*data.posy[j] + data.dirz[j]*data.posz[j]
		n = np.sqrt(data.posx[j]**2 + data.posy[j]**2 + data.posz[j]**2)
		udotr = u/n
		if udotr <= udotr_LOW:
			continue
		if udotr >= udotr_HIGH:
			continue
		if data.sunct[j] <= sunct_LOW:
			continue
		if data.sunct[j] >= sunct_HIGH:
			continue
		Total.Fill(data.udotr[j])
		debugging.append(data.eventID[j])
	
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
		if data.waterFit[index] == False:
			continue
		if data.isCal[index] == False:
			continue
		#if data.inTimeHits100[j] < IN_TIME_HITS100:
		#	continue
		if data.beta14[index] <= B14_LOW:
			continue
		if data.beta14[index] >= B14_HIGH:
			continue
		if data.itr[index] <= ITR:
			continue
		if data.energy[index] >= E_HIGH:
			continue
		if data.energy[index] <= E_LOW:
			continue
		if data.posr[index] >= POSR_CUT_HIGH:
			continue
		#if data.posr[j] < POSR_CUT_LOW:
		#	continue
		if data.posz[index] <= Z_LOW:
			continue
		if data.posz[index] >= Z_HIGH:
			continue
		#if data.nhitsCleaned[j] > nhitsCleaned_HIGH:
		#	continue
		#if data.nhitsCleaned[j] < nhitsCleaned_LOW:
		#	continue
		u = data.dirx[index]*data.posx[index] + data.diry[index]*data.posy[index] + data.dirz[index]*data.posz[index]
		n = np.sqrt(data.posx[index]**2 + data.posy[index]**2 + data.posz[index]**2)
		udotr = u/n
		if udotr <= udotr_LOW:
			continue
		if udotr >= udotr_HIGH:
			continue
		if data.sunct[index] <= sunct_LOW:
			continue
		if data.sunct[index] >= sunct_HIGH:
			continue
		ccpass.append(index)
		CCsac.Fill(data.udotr[index]) 
	
	ccpass = np.array(ccpass)
	dcpass = np.array(dcpass)

	signal = np.intersect1d(dcpass,ccpass)
	for x in signal:
		B14_ITR_signal.Fill(data.itr[x], data.beta14[x])
	for y in bg:
		B14_ITR_bg.Fill(data.itr[y], data.beta14[y])

output = args.root_name
#f3 = open(str(output + "_event.txt"), 'a')
#for i in debugging:
#	evid = str(i)
#	f3.write(evid)
#	f3.write('\n')
#f3.close

file1 = ROOT.TFile(output, 'RECREATE')
B14_ITR_signal.Write()
B14_ITR_bg.Write()
CCsac.Write()
DCsac.Write()
Total.Write()
file1.Close()

#B14_ITR_bg.Draw("SAME")
#Total.Write()

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

#waiting = input("press any key to close")
print("--- %s seconds ---" % (time.time() - start_time))

