import ROOT
import sys
import os
import numpy as np
import time

start_time = time.time()

nbins = 21
first_bin = 0.0
last_bin = 1.0

f1 = ROOT.TFile.Open("sum_data.root")
f2 = ROOT.TFile.Open("sum_mc.root")
f3 = open("bin-by-bin.txt", 'a')

Total_data = f1.Total
Total_mc = f2.Total

CC_data = f1.CCsac

CC_mc = f2.CCsac


CC_acc_data = ROOT.TH1F('CC_acc_data', 'acc', nbins, first_bin, last_bin)
for i in  range(nbins):
        copy = f1.CCsac.GetBinContent(i)
        CC_acc_data.SetBinContent(i, copy)

CC_acc_mc = ROOT.TH1F('CC_acc_mc', 'acc', nbins, first_bin, last_bin)
for i in  range(nbins):
        copy = f2.CCsac.GetBinContent(i)
        CC_acc_mc.SetBinContent(i, copy)



data_err = []
mc_err = []
data_bin = []
mc_bin = []
for j in range(nbins):
	data_bin.append(CC_acc_data.GetBinContent(j))
	#error_data = np.sqrt(Total_data.GetBinContent(j) - CC_acc_data.GetBinContent(j))
	error_data = np.sqrt(CC_acc_data.GetBinContent(j))
	n_data = Total_data.GetBinContent(j)
        if n_data == 0.0:
		data_err.append(0.0)
		continue
	norm_data = n_data
        CCerr_data = error_data/norm_data
	data_err.append(CCerr_data)


for j in range(nbins):
	mc_bin.append(CC_acc_mc.GetBinContent(j))
#	error_mc = np.sqrt(Total_mc.GetBinContent(j) - CC_acc_mc.GetBinContent(j))
	error_mc = np.sqrt(CC_acc_mc.GetBinContent(j))
	n_mc = Total_mc.GetBinContent(j)
        if n_mc == 0.0:
		mc_err.append(0.0)
		continue
	norm_mc = n_mc
        CCerr_mc = error_mc/norm_mc
	mc_err.append(CCerr_mc)

#	pointd = CC_data.GetBinContent(j)
#	data_bin.append(pointd)
#	error_data = CC_data.GetBinError(j)
#	n_data = Total_data.GetBinContent(j)
#	if n_data == 0.0:
#		data_err.append(0.0)
#		continue
#	norm_data = np.sqrt(n_data)
#
#	CCerr_data = error_data/norm_data
#	
#	data_err.append(CCerr_data)

#for q in range(nbins):
#	pointm = CC_mc.GetBinContent(q)
#	mc_bin.append(pointm)
#	error_mc = CC_mc.GetBinError(q)
#	n_mc = Total_mc.GetBinContent(q)
#	if n_mc == 0.0:
#		mc_err.append(0.0)
#		continue
#	norm_mc = np.sqrt(n_mc)
#
#	CCerr_mc = error_mc/norm_data
#	
#	mc_err.append(CCerr_mc)
CC_data.Divide(Total_data)
CC_mc.Divide(Total_mc)
CC_data.Divide(CC_mc)
f3.write("number of bins: {}".format(nbins))
f3.write("\n")
f3.write("binlow: {}  binhigh: {}".format(first_bin, last_bin))
f3.write("\n")
f3.write("bin width: {}".format(float((float(last_bin)  - float(first_bin))/float(nbins - 1.0))))
f3.write("\n")
f3.write("bin   classifier correction    uncertainty")
for m in range(nbins):
	R = CC_data.GetBinContent(m)
	#D = CC_acc_data.GetBinContent(m)
	#M = CC_acc_mc.GetBinContent(m)
	D = data_bin[m]
	M = mc_bin[m]
	erd = data_err[m]
	erm = mc_err[m]
	if D == 0.0:
		continue
	if M == 0.0:
		continue
	#prop_err = float(R*np.sqrt((erd/D)**2+(erm/M)**2))
	prop_err_term1 = float((erd**2)/(M**2))
	prop_err_term2 = float((D**2)*(erm**2)/(M**3))
	prop_term_tot = float(prop_err_term1 + prop_err_term2)
	prop_err = np.sqrt(prop_term_tot)
	print(prop_err)
	CC_data.SetBinError(m,prop_err)
	f3.write("\n")
	f3.write("{}	{}	{}".format(m, R, prop_err))

CC_data_fit = ROOT.TF1("CC_data_fit", "pol1(0)", 0.0,0.78)
CC_data_fit.SetParameter(0,0.02)
CC_data_fit.SetParameter(1,0.00000001)
CC_data_fit.FixParameter(1,0.0)

c1 = ROOT.TCanvas()
CC_data.SetTitle("Classifier Cut Correction")
CC_data_fit.SetLineColor(8)
CC_data.Fit(CC_data_fit, "RB")
CC_data.GetXaxis().SetRangeUser(0.0, 0.78)
CC_data.SetLineColor(8)
CC_data.GetXaxis().SetTitle("(R/R_{AV})^3")
CC_data.GetYaxis().SetTitle("Data Acceptance / MC Acceptance")
CC_data.SetLineWidth(2)
ROOT.gStyle.SetErrorX(0.)
ROOT.gStyle.SetOptStat(0)
ROOT.gStyle.SetOptFit(0)
CC_data.Draw("SAME HISTE1")

f3 = open('cc_stat.dat','a')
sbar_cc = CC_data_fit.GetParameter(0)
fit_err_cc = CC_data_fit.GetParError(0)
num_tot_cc = 0.0
den_tot_cc = 0.0
for i in range(nbins):
        s_bin = CC_data.GetBinContent(i)
        s_binerr = CC_data.GetBinError(i)
        s_binerr_sq = s_binerr**2.0
        if s_binerr_sq == 0.0:
                continue
        w_i = 1.0/s_binerr_sq
        num_i = nbins*w_i*(s_bin - sbar_cc)**2.0
        den_i = (nbins - 1.0)*w_i

        num_tot_cc = num_tot_cc + num_i
        den_tot_cc = den_tot_cc + den_i
CC_uncert = np.sqrt(num_tot_cc/den_tot_cc)

f3.write("cc correction is {}".format(sbar_cc))
f3.write("\n")
f3.write("cc stat uncert is {}".format(CC_uncert))
f3.write("\n")
f3.write("cc fit uncert is {}".format(fit_err_cc))
f3.write("\n")

#c1.Draw()



#correction = cc_d.Divide(cc_mc)

#correction.Draw()

#for j in range(nbins):
#	error_cc = CC_data.GetBinError(j)
#	error_dc = DC.GetBinError(j)
#	n = Total.GetBinContent(j)
#	if n == 0.0:
#		continue
#	norm = np.sqrt(n)
#	CCerr = error_cc/norm
#	DCerr = error_dc/norm
#	DC.SetBinError(j,DCerr)
#	CC.SetBinError(j,CCerr)
#
#DCfit = ROOT.TF1("DCfit", "pol1(0)", 5,10)
#DCfit.SetParameter(0,0.02)
#DCfit.SetParameter(1,0.00000001)
#DCfit.FixParameter(1,0.0)
#
#CCfit = ROOT.TF1("CCfit", "pol1(0)", 5, 10)
#CCfit.SetParameter(0,0.02)
#CCfit.SetParameter(1,0.00000001)
#CCfit.FixParameter(1,0.0)
#
#
#
#Outname = "AvgSac.dat"
#outfile = open(Outname, 'a')
#outfile.write('CC DC')
#outfile.write(' ')
#outfile.write(str(CCfit.GetParameter(0)))
#outfile.write(' ')
#outfile.write(str(DCfit.GetParameter(0)))
#outfile.close()
#
#
#testing = ROOT.TFile('test', 'RECREATE')
#
##aeshtetics 
#
#c1 = ROOT.TCanvas()
#DC.SetTitle("Data Cleaning Cuts")
#DCfit.SetLineColor(46)
#DC.Fit(DCfit, "RB")
#DC.GetXaxis().SetRangeUser(5.8,8.8)
#DC.SetLineColor(46)
#DC.GetXaxis().SetTitle("Energy [MeV]")
#DC.GetYaxis().SetTitle("Fractional Sacrifice")
#DC.SetLineWidth(2)
#DC.Draw("SAME HISTE1")
#
#c2 = ROOT.TCanvas()
#CC.SetTitle("Classifier Cuts")
#CCfit.SetLineColor(9)
#CC.Fit(CCfit, "RB")
#CC.GetXaxis().SetRangeUser(5.8,8.8)
#CC.SetLineColor(9)
#CC.GetXaxis().SetTitle("Energy [MeV]")
#CC.GetYaxis().SetTitle("Fractional Sacrifice")
#CC.SetLineWidth(2)
#CC.Draw("HISTE1 SAME")
#ROOT.TGaxis.SetMaxDigits(2)
#
#ROOT.gStyle.SetErrorX(0.)
#ROOT.gStyle.SetOptStat(0)
#ROOT.gStyle.SetOptFit(0)
#c1.Draw()
#c1.Write()
#c2.Draw()
#c2.Write()
#CC.Write()
#DC.Write()
#testing.Close()
waiting = input("press any key to close")

print("--- %s seconds ---" % (time.time() - start_time))
