// C++ Headers
#include <iostream>
#include <vector>
#include <map>
// ROOT Headers
#include <TChain.h>
#include <TTree.h>
#include <TH1F.h>
#include <TFile.h>
#include <TString.h>
#include <Rtypes.h>
#include <TVector3.h>
#include <TRandom3.h>
#include <TF1.h>
#include <TMath.h>
// RAT Headers
#include <RAT/SunUtil.hh>
//#include <RAT/DU/ReactorNuOsc.hh>
#include <RAT/DU/Utility.hh>
#include <RAT/DU/ReconCorrector.hh> 
#include <RAT/DU/ReconCalibrator.hh> 
// JSON Reader
#include <fstream>
//#include <boost/property_tree/ptree.hpp>
//#include <boost/property_tree/json_parser.hpp>
using namespace std;

double shitZshift = -108;

// Order of operations:
// 1. Prune {fitValid, posr<6m}
// 2. Add to output tree: SunR & uDotR -- sun,dxdydz
// 3. Add header tree with: Accepted, rejected
class Parser
{
  public:
    string oname = "default.root";
    vector<string> flist;
    bool isData = false;

    Parser(int argc, char** argv)
    {
      vector<string> args(argv, argv+argc);
      for(int n=1; n<argc; n++)
      {
        if( args[n] == "--out" )
        {
          this->oname = args[n+1];
          n++;
        }
        else if( args[n] == "--data" )
          this->isData = true;
        else
          flist.push_back(args[n]);
      }
      if (flist.size() == 0)
      {
        cout << "Need at least one file" << endl;
        exit(-1);
      }
    }
};

int main(int argc, char** argv)
{
  Parser args(argc, argv); 
   
  // Check the files in argv
  TChain* chain = new TChain("output");
  cerr<<"loading tchains "<< args.flist.size() - 1 <<endl;
  for(auto& it : args.flist)
    chain->Add(it.c_str());
  // Correction to energy
  if(chain->GetEntries()==0){
      cout << "FILES GIVEN HAVE NO ENTRIES.  fin." << endl;
  }
  else {
    const RAT::DU::ReconCorrector &eCorr = RAT::DU::Utility::Get()->GetReconCorrector();
    const RAT::DU::ReconCalibrator &eCalib= RAT::DU::Utility::Get()->GetReconCalibrator();
    // Header tree
    TTree* header = new TTree("header", "Processor Header Information");
    int accepted=0;
    double efficiency;
    int total;
  
    // Indicates how many events were cut with defined selection 
    header->Branch("efficiency", &efficiency);
    header->Branch("total", &total);
    cerr << "Saving to file " << args.oname << endl;
    TFile* outfile = new TFile(args.oname.c_str(), "recreate");
    TTree* outtree = chain->CloneTree(0);
  
    int evIndex;
    double energy, posr;
    double posx, posy, posz;
    double dirx, diry, dirz;
    int uTDays, uTSecs, uTNSecs;
    double itr, beta14;
    ULong64_t dcFlagged;
    double parentKE;
    int runID;
  
    bool fitValid;
    bool isCal;
 
    //Position FOM inputs
    double posxPosError;
    double posxNegError;
    double posyPosError;
    double posyNegError;
    double poszPosError;
    double poszNegError;
    double posFOM;
    UInt_t posFOM2;
 
    //Energy FOM inputs
    double energyFOMUtest;
    double energyFOMGtest;
    double energyFOMmedProbHit;
    double energyFOMmedProb;
    double energyFOMmedDevHit;
    double energyFOMmedDev;
  
    //TString* parentMeta = new TString(256); // Do i need parentMeta1 and 2?
    chain->SetBranchAddress("evIndex", &evIndex);
    chain->SetBranchAddress("runID", &runID);
    chain->SetBranchAddress("energy", &energy);
    chain->SetBranchAddress("posr", &posr);
    chain->SetBranchAddress("fitValid", &fitValid);
    chain->SetBranchAddress("isCal",&isCal); 
    chain->SetBranchAddress("posx", &posx);
    chain->SetBranchAddress("posy", &posy);
    chain->SetBranchAddress("posz", &posz);
    chain->SetBranchAddress("dirx", &dirx);
    chain->SetBranchAddress("diry", &diry);
    chain->SetBranchAddress("dirz", &dirz);
    chain->SetBranchAddress("uTDays", &uTDays);
    chain->SetBranchAddress("uTSecs", &uTSecs);
    chain->SetBranchAddress("uTNSecs", &uTNSecs);
    chain->SetBranchAddress("itr", &itr);
    chain->SetBranchAddress("beta14", &beta14);
    chain->SetBranchAddress("dcFlagged", &dcFlagged);
    chain->SetBranchAddress("posxPosError", &posxPosError);
    chain->SetBranchAddress("posxNegError", &posxNegError);
    chain->SetBranchAddress("posyPosError", &posyPosError);
    chain->SetBranchAddress("posyNegError", &posyNegError);
    chain->SetBranchAddress("poszPosError", &poszPosError);
    chain->SetBranchAddress("poszNegError", &poszNegError);
    chain->SetBranchAddress("posFOM", &posFOM);
    chain->SetBranchAddress("posFOM2", &posFOM2);
    chain->SetBranchAddress("energyFOMUtest" , &energyFOMUtest);
    chain->SetBranchAddress("energyFOMGtest", &energyFOMGtest);
    chain->SetBranchAddress("energyFOMmedProbHit", &energyFOMmedProbHit);
    chain->SetBranchAddress("energyFOMmedProb", &energyFOMmedProb);
    chain->SetBranchAddress("energyFOMmedDevHit", &energyFOMmedDevHit);
    chain->SetBranchAddress("energyFOMmedDev", &energyFOMmedDev);

   

    // New Branches
    double udotr, sunct, sunx, suny, sunz, posr3;
    int nbc;
    double oscWeight;
    outtree->Branch("posr3", &posr3);
    outtree->Branch("udotr", &udotr);
    outtree->Branch("sunct", &sunct);
    outtree->Branch("sunx", &sunx);
    outtree->Branch("suny", &suny);
    outtree->Branch("sunz", &sunz);
    outtree->Branch("oscillate", &oscWeight);
    outtree->Branch("nbc", &nbc);
    unsigned int entries = chain->GetEntries();
    total = 0;
    cerr<<"Begin processing: "<<entries<<" events"<<endl;
    for(int i=0; i<entries; i++)
    {
      if(i%10000==0)
        cerr<<"Proc: "<<i/double(entries)*100<<"%\r"<<flush;
      chain->GetEvent(i);
      // Oscillate reactors
      total++;
      if( !fitValid )
        continue;
      energy = eCorr.CorrectEnergyRSP(energy,2);
      accepted++;
      double rho = sqrt( posx*posx + posy*posy);
      bool realData = true;
      energy = eCalib.CalibrateEnergyRSP(realData, energy, rho, posz);
      //Now correct z; Logan's calibrator uses PSUP coord, so non-corr Z
      posz = posz + shitZshift;
      posr = sqrt( posx*posx + posy*posy + posz*posz );
      udotr = (posx*dirx+posy*diry+posz*dirz)/sqrt(posx*posx+posy*posy+posz*posz)/sqrt(dirx*dirx+diry*diry+dirz*dirz);
      TVector3 Solar = RAT::SunDirection(uTDays, uTSecs, uTNSecs);
      sunct = (Solar.X()*dirx + Solar.Y()*diry + Solar.Z()*dirz);
      sunx = Solar.X();
      suny = Solar.Y();
      sunz = Solar.Z();
      posr3 = pow((posr/6000.0),3);
      
      //Position figures of merit
      double position_error = sqrt(pow(posxPosError, 2) + pow(posxNegError, 2) + pow(posyPosError, 2) + pow(posyNegError, 2) + pow(poszPosError, 2) + pow(poszNegError, 2));
      double position_fom = posFOM / posFOM2;
      // Nominal Selection
      if( position_error >= 525 ) continue; 
      if( position_fom <= 10.85 ) continue; 
//      if( posFOM > 1300 ) continue; //old cuts as of October 2020; instead using position_fom (ratio)
//      if( posFOM2 < 9.9 ) continue;

      //Energy figures of merit  
      double utest = energyFOMUtest;
      double gtest = energyFOMGtest;
      double zfactor = ( energyFOMmedProbHit != energyFOMmedProb ) ? (1 - 3*( energyFOMmedDevHit + energyFOMmedDev ) /( energyFOMmedProbHit - energyFOMmedProb )) : -99999;
      // Nominal selection
      if( utest <= 0.59 ) continue;
      if( (gtest <= 0.0) || (gtest >= 1.0) ) continue;
      if( (zfactor <= -11.0) || (zfactor >= 1.0) ) continue;


      outtree->Fill();
  
    }
    efficiency = double(accepted)/total;
    header->Fill();
    cerr<<endl<<"fin"<<endl;
    outfile->Write();
  }
}
