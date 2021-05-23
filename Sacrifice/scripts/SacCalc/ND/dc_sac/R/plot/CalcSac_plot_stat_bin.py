import ROOT
import sys
import os
import numpy as np
import time

start_time = time.time()

nbins = 21
first_bin = 0.0
last_bin = 1.0
#name = str(input("stat file name: "))
name = str("fit_stats.txt")
f = ROOT.TFile.Open("sum.root")
f2 = open(name, 'a')
f3 = open("bin-by-bin.txt", 'a')

add1 = ROOT.TH1F('add1', 'all', nbins, first_bin, last_bin)
for i in range(nbins):
	add1.SetBinContent(i,1.0)

Total = f.Total

DC_acc = ROOT.TH1F('DC_acc', 'acc', nbins, first_bin, last_bin)
for i in  range(nbins):
	copy = f.DCsac.GetBinContent(i)
	DC_acc.SetBinContent(i, copy)

CC_acc = ROOT.TH1F('CC_acc', 'acc', nbins, first_bin, last_bin)
for i in  range(nbins):
	copy = f.CCsac.GetBinContent(i)
	CC_acc.SetBinContent(i, copy)

DC = f.DCsac
DC.Divide(Total)
DC.Scale(-1.0)
DC.Add(add1)

CC = f.CCsac
CC.Divide(Total)
CC.Scale(-1.0)
CC.Add(add1)

f3.write("number of bins: {}".format(nbins))
f3.write("\n")
f3.write("binlow: {}  binhigh: {}".format(first_bin, last_bin))
f3.write("\n")
f3.write("bin width: {}".format(float((float(last_bin)  - float(first_bin))/float(nbins - 1.0))))
f3.write("\n")
f3.write("bin	fractional sacrifice	uncertainty")
for j in range(nbins):
	#error_cc = CC.GetBinError(j)
	#error_cc = np.sqrt(f.CCsac.GetBinContent(j))
	#error_dc = DC.GetBinError(j)
#	print(f.DCsac.GetBinContent(j))
	#error_dc = np.sqrt(f.DCsac.GetBinContent(j))
	error_dc = np.sqrt(Total.GetBinContent(j) - DC_acc.GetBinContent(j))
	error_cc = np.sqrt(Total.GetBinContent(j) - CC_acc.GetBinContent(j))
#	print("{} , {}".format(Total.GetBinContent(j), DC_acc.GetBinContent(j)))
	n = Total.GetBinContent(j)
	if n == 0.0:
		continue
#	norm = np.sqrt(n)
	norm = n
	CCerr = error_cc/norm
	DCerr = error_dc/norm
	f3.write("\n")
	f3.write("{}	{}	{}".format(j, DC.GetBinContent(j), DCerr))
	DC.SetBinError(j,DCerr)
	CC.SetBinError(j,CCerr)

DCfit = ROOT.TF1("DCfit", "pol1(0)", 0.0, 0.78)
DCfit.SetParameter(0,0.02)
DCfit.SetParameter(1,0.00000001)
DCfit.FixParameter(1,0.0)

CCfit = ROOT.TF1("CCfit", "pol1(0)", 0.0, 0.78)
CCfit.SetParameter(0,0.02)
CCfit.SetParameter(1,0.00000001)
CCfit.FixParameter(1,0.0)

	




testing = ROOT.TFile('Plots.root', 'RECREATE')

#aeshtetics and uncertainty 

#c1 = ROOT.TCanvas()
#DC.SetTitle("Data Cleaning Cuts")
#DCfit.SetLineColor(46)
DC.Fit(DCfit, "RB")
ndf_dc = DCfit.GetNDF()
chi_dc = DCfit.GetChisquare()
chindf_dc = chi_dc/ndf_dc
sbar_dc = DCfit.GetParameter(0)
fit_err_dc = DCfit.GetParError(0)
num_tot_dc = 0.0
den_tot_dc = 0.0
for i in range(nbins):
	s_bin = DC.GetBinContent(i)
#	s_binerr = f.DCsac.GetBinError(i)
	s_binerr = DC.GetBinError(i)
	normtot = f.Total.GetBinContent(i)
	if normtot == 0.0:
		continue
#	s_binerr = s_binerr/normtot
	s_binerr_sq = s_binerr**2.0
	if s_binerr_sq == 0.0:
		continue
	w_i = 1.0/s_binerr_sq
	num_i = nbins*w_i*(s_bin - sbar_dc)**2.0
	den_i = (nbins - 1.0)*w_i
	
	num_tot_dc = num_tot_dc + num_i
	den_tot_dc = den_tot_dc + den_i
DC_uncert = np.sqrt(num_tot_dc/den_tot_dc)
#DC.GetXaxis().SetRangeUser(5.8,8.8)
#DC.SetLineColor(46)
#DC.GetXaxis().SetTitle("Energy [MeV]")
#DC.GetYaxis().SetTitle("Fractional Sacrifice")
#DC.SetLineWidth(2)
#DC.Draw("SAME HISTE1")

#c2 = ROOT.TCanvas()


#CC.SetTitle("Classifier Cuts")
#CCfit.SetLineColor(9)
CC.Fit(CCfit, "RB")
ndf_cc = CCfit.GetNDF()
chi_cc = CCfit.GetChisquare()
chindf_cc = chi_cc/ndf_cc
sbar_cc = CCfit.GetParameter(0)
fit_err_cc = CCfit.GetParError(0)
num_tot_cc = 0.0
den_tot_cc = 0.0
for i in range(nbins):
	s_bin = CC.GetBinContent(i)
	s_binerr = CC.GetBinError(i)
	normie = f.Total.GetBinContent(i)
	if normie == 0.0:
		continue
	s_binerr = s_binerr/normie
	s_binerr_sq = s_binerr**2.0
	if s_binerr_sq == 0.0:
		continue
	w_i = 1.0/s_binerr_sq
	num_i = nbins*w_i*(s_bin - sbar_cc)**2.0
	den_i = (nbins - 1.0)*w_i
	
	num_tot_cc = num_tot_cc + num_i
	den_tot_cc = den_tot_cc + den_i
CC_uncert = np.sqrt(num_tot_cc/den_tot_cc)

#CC.GetXaxis().SetRangeUser(5.8,8.8)
#CC.SetLineColor(9)
#CC.GetXaxis().SetTitle("Energy [MeV]")
#CC.GetYaxis().SetTitle("Fractional Sacrifice")
#CC.SetLineWidth(2)
f2.write("cc sacrifice is {}".format(sbar_cc))
f2.write("\n")
f2.write("cc stat uncert is {}".format(CC_uncert))
f2.write("\n")
f2.write("cc fit uncert is {}".format(fit_err_cc))
f2.write("\n")
f2.write("cc chi2/ndf is {}".format(chindf_cc))
f2.write("\n")
f2.write("\n")
f2.write("dc sacrifice is {}".format(sbar_dc))
f2.write("\n")
f2.write("dc stat uncert is {}".format(DC_uncert))
f2.write("\n")
f2.write("dc fit uncert is {}".format(fit_err_dc))
f2.write("\n")
f2.write("dc chi2/ndf is {}".format(chindf_dc))
f2.write("\n")
f2.close()
#CC.Draw("HISTE1 SAME")
#ROOT.TGaxis.SetMaxDigits(2)

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

testing = ROOT.TFile('Plots.root', 'RECREATE')

#aeshtetics

c1 = ROOT.TCanvas()
DC.SetTitle("Data Cleaning Cuts")
DCfit.SetLineColor(46)
DC.Fit(DCfit, "RB")
DC.GetXaxis().SetRangeUser(0.0,0.78)
DC.SetLineColor(46)
DC.GetXaxis().SetTitle("(R/R_{AV})^3")
DC.GetYaxis().SetTitle("Fractional Sacrifice")
DC.SetLineWidth(2)
DC.Draw("SAME HISTE1")

c2 = ROOT.TCanvas()
CC.SetTitle("Classifier Cuts")
CCfit.SetLineColor(9)
CC.Fit(CCfit, "RB")
CC.GetXaxis().SetRangeUser(0.0,0.78)
CC.SetLineColor(9)
CC.GetXaxis().SetTitle("(R/R_{AV})^3")
CC.GetYaxis().SetTitle("Fractional Sacrifice")
CC.SetLineWidth(2)
CC.Draw("HISTE1 SAME")
ROOT.TGaxis.SetMaxDigits(2)

ROOT.gStyle.SetErrorX(0.)
ROOT.gStyle.SetOptStat(0)
ROOT.gStyle.SetOptFit(0)
c1.Draw()
c1.Write()
c2.Draw()
c2.Write()
CC.Write()
DC.Write()
testing.Close()
waiting = input("press any key to close")

Outname = "AvgSac.dat"
outfile = open(Outname, 'a')
outfile.write('CC DC')
outfile.write(' ')
outfile.write(str(CCfit.GetParameter(0)))
outfile.write(' ')
outfile.write(str(DCfit.GetParameter(0)))
outfile.close()
#waiting = input("press any key to close")

print("--- %s seconds ---" % (time.time() - start_time))
