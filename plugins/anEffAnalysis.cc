// -*- C++ -*-
//
// Package:    CalibTracker/anEffAnalysis
// Class:      anEffAnalysis
// 
/**\class anEffAnalysis anEffAnalysis.cc CalibTracker/anEffAnalysis/plugins/anEffAnalysis.cc

 Description: [one line class summary]

 Implementation:
     [Notes on implementation]
*/
//
// Original Author:  Olivier Bondu
//         Created:  Mon, 04 Jul 2016 13:16:13 GMT
//
//


// system include files
#include <memory>

// user include files
#include "FWCore/Framework/interface/Frameworkfwd.h"
#include "FWCore/Framework/interface/EDAnalyzer.h"
#include "FWCore/Framework/interface/ESHandle.h"

#include "FWCore/Framework/interface/Event.h"
#include "FWCore/Framework/interface/EventSetup.h"
#include "FWCore/Framework/interface/MakerMacros.h"

#include "FWCore/ParameterSet/interface/ParameterSet.h"

// Tracker geometry
#include "CalibTracker/SiStripCommon/interface/TkDetMap.h"
#include "DataFormats/TrackerCommon/interface/TrackerTopology.h"
#include "DataFormats/SiStripDetId/interface/StripSubdetector.h"
#include "Geometry/Records/interface/TrackerTopologyRcd.h"

// ROOT includes
#include "TCanvas.h"
#include "TFile.h"
#include "TTree.h"
#include "TChain.h"
#include "TH1F.h"
#include "TH2F.h"

// C++ includes
#include <iostream>
#include <string>

namespace anEffAnalysisTool {
    std::vector<std::string> split(std::string str, char delimiter) {
        std::vector<std::string> internal;
        std::stringstream ss(str); // Turn the string into a stream.
        std::string tok; 
        while(getline(ss, tok, delimiter)) {
            internal.push_back(tok);
        }
        return internal;
    }
}
//
// class declaration
//

class anEffAnalysis : public edm::EDAnalyzer {
    public:
        explicit anEffAnalysis(const edm::ParameterSet&);
        ~anEffAnalysis();

        static void fillDescriptions(edm::ConfigurationDescriptions& descriptions);


    private:
        virtual void beginJob() override;
        virtual void analyze(const edm::Event&, const edm::EventSetup&) override;
        virtual void endJob() override;
        unsigned int checkLayer( unsigned int iidd, const TrackerTopology* tTopo);

      //virtual void beginRun(edm::Run const&, edm::EventSetup const&) override;
      //virtual void endRun(edm::Run const&, edm::EventSetup const&) override;
      //virtual void beginLuminosityBlock(edm::LuminosityBlock const&, edm::EventSetup const&) override;
      //virtual void endLuminosityBlock(edm::LuminosityBlock const&, edm::EventSetup const&) override;

      // ----------member data ---------------------------
        // Job setup
        bool HIPDEBUG;
        std::vector<std::string> VInputFiles;
        Long64_t m_max_events_per_file;
        std::string m_input_treename;
        std::string m_output_filename;
        std::unique_ptr<TFile> m_output;
        std::vector<int> m_Vruns;
        std::vector<edm::LuminosityBlockRange> m_Vlumisections;
        std::vector<std::string> m_Vlayers;
        std::vector<std::string> m_Vbxs;
        std::string m_filter_exp;
        // Internal things
        std::unordered_set<int> m_Sruns;
        std::unordered_set<std::string> m_Slayers;
        std::unordered_set<std::string> m_Sbxs;
        // Utilities
        TkDetMap* tkDetMap_;
        TkLayerMap* tkLayerMap_;
        typedef std::chrono::system_clock clock;
        typedef std::chrono::milliseconds ms;
        typedef std::chrono::seconds seconds;
        clock::time_point m_start_time;
        // Histograms
        std::map<std::string, TH1F*> map_h_ClusterStoN;
        std::map<std::string, TH2F*> map_h_ClusterStoN_vs_bx;
};

//
// constants, enums and typedefs
//

//
// static data member definitions
//

//
// constructors and destructor
//
anEffAnalysis::anEffAnalysis(const edm::ParameterSet& iConfig):
HIPDEBUG(iConfig.getParameter<bool>("debug")),
VInputFiles(iConfig.getUntrackedParameter<std::vector<std::string>>("InputFiles")),
m_max_events_per_file(iConfig.getUntrackedParameter<Long64_t>("maxEventsPerFile")),
m_input_treename(iConfig.getParameter<std::string>("inputTreeName")),
m_output_filename(iConfig.getParameter<std::string>("output")),
m_Vruns(iConfig.getUntrackedParameter<std::vector<int>>("runs")),
m_Vlumisections(iConfig.getUntrackedParameter<std::vector<edm::LuminosityBlockRange>>("lumisections")),
m_Vlayers(iConfig.getUntrackedParameter<std::vector<std::string>>("layers")),
m_Vbxs(iConfig.getUntrackedParameter<std::vector<std::string>>("bxs")),
m_filter_exp(iConfig.getParameter<std::string>("filter_exp"))
{
   //now do what ever initialization is needed
    m_output.reset(TFile::Open(m_output_filename.c_str(), "recreate"));
    std::copy(m_Vruns.begin(), m_Vruns.end(), std::inserter(m_Sruns, m_Sruns.end()));
    std::copy(m_Vlayers.begin(), m_Vlayers.end(), std::inserter(m_Slayers, m_Slayers.end()));
    std::copy(m_Vbxs.begin(), m_Vbxs.end(), std::inserter(m_Sbxs, m_Sbxs.end()));
}


anEffAnalysis::~anEffAnalysis()
{
   // do anything here that needs to be done at desctruction time
   // (e.g. close files, deallocate resources etc.)
    for (auto it = map_h_ClusterStoN.begin() ; it != map_h_ClusterStoN.end() ; it++)
        delete (*it).second;
    for (auto it = map_h_ClusterStoN_vs_bx.begin() ; it != map_h_ClusterStoN_vs_bx.end() ; it++)
        delete (*it).second;
    m_output->Close();
}


//
// member functions
//

// Duplicated from
// https://github.com/cms-sw/cmssw/blob/3c369381b186f8aa7f0379883aacf93f712612c8/CalibTracker/SiStripHitEfficiency/src/HitEff.cc#L813-L833
// FIXME Note: since this is also about reading data stored in anEff/traj trees, and that it doesn't access any data from HitEff, probably the method should be made static
unsigned int anEffAnalysis::checkLayer( unsigned int iidd, const TrackerTopology* tTopo) {
    StripSubdetector strip=StripSubdetector(iidd);
    unsigned int subid=strip.subdetId();
    if (subid ==  StripSubdetector::TIB) {
        return tTopo->tibLayer(iidd);
    }
    if (subid ==  StripSubdetector::TOB) {
        return tTopo->tobLayer(iidd) + 4 ;
    }
    if (subid ==  StripSubdetector::TID) {
        return tTopo->tidWheel(iidd) + 10;
    }
    if (subid ==  StripSubdetector::TEC) {
        return tTopo->tecWheel(iidd) + 13 ;
    }
    return 0;
}


// ------------ method called for each event  ------------
void
anEffAnalysis::analyze(const edm::Event& iEvent, const edm::EventSetup& iSetup)
{
    // Get the geometry
//    edm::ESHandle<TrackerTopology> tTopo_handle;
//    iSetup.get<TrackerTopologyRcd>().get(tTopo_handle);
///    const TrackerTopology* tTopo = tTopo_handle.product();
    unsigned long long ievent = iEvent.id().event();
    unsigned long long ifile = ievent - 1;
    if (ifile < VInputFiles.size())
    {
        std::cout << std::endl << "-----" << std::endl;
        printf("Opening file %3llu/%3i --> %s\n", ifile + 1, (int)VInputFiles.size(), (char*)(VInputFiles[ifile].c_str())); fflush(stdout);

        // The tree is flat, so let's filter out events that do not interest us
        // NB: the expression is done in the python config file because it's easier in python than in C++
        TFile *infile = TFile::Open(VInputFiles[ifile].c_str());
        TTree *intree = (TTree*)infile->Get(m_input_treename.c_str());

        // List of variables taken from https://github.com/cms-sw/cmssw/blob/3c369381b186f8aa7f0379883aacf93f712612c8/CalibTracker/SiStripHitEfficiency/interface/HitEff.h#L84-L101
        float TrajGlbX = 0.;                intree->SetBranchAddress("TrajGlbX", &TrajGlbX, NULL);
        float TrajGlbY = 0.;                intree->SetBranchAddress("TrajGlbY", &TrajGlbY, NULL);
        float TrajGlbZ = 0.;                intree->SetBranchAddress("TrajGlbZ", &TrajGlbZ, NULL);
        float TrajLocX = 0.;                intree->SetBranchAddress("TrajLocX", &TrajLocX, NULL);
        float TrajLocY = 0.;                intree->SetBranchAddress("TrajLocY", &TrajLocY, NULL);
        float TrajLocErrX = 0.;             intree->SetBranchAddress("TrajLocErrX", &TrajLocErrX, NULL);
        float TrajLocErrY = 0.;             intree->SetBranchAddress("TrajLocErrY", &TrajLocErrY, NULL);
        float TrajLocAngleX = 0.;           intree->SetBranchAddress("TrajLocAngleX", &TrajLocAngleX, NULL);
        float TrajLocAngleY = 0.;           intree->SetBranchAddress("TrajLocAngleY", &TrajLocAngleY, NULL);
        float ClusterLocX = 0.;             intree->SetBranchAddress("ClusterLocX", &ClusterLocX, NULL);
        float ClusterLocY = 0.;             intree->SetBranchAddress("ClusterLocY", &ClusterLocY, NULL);
        float ClusterLocErrX = 0.;          intree->SetBranchAddress("ClusterLocErrX", &ClusterLocErrX, NULL);
        float ClusterLocErrY = 0.;          intree->SetBranchAddress("ClusterLocErrY", &ClusterLocErrY, NULL);
        float ClusterStoN = 0.;             intree->SetBranchAddress("ClusterStoN", &ClusterStoN, NULL);
        float ResX = 0.;                    intree->SetBranchAddress("ResX", &ResX, NULL);
        float ResXSig = 0.;                 intree->SetBranchAddress("ResXSig", &ResXSig, NULL);
        unsigned int ModIsBad = 0;          intree->SetBranchAddress("ModIsBad", &ModIsBad, NULL);
        unsigned int Id = 0;                intree->SetBranchAddress("Id", &Id, NULL);
        unsigned int SiStripQualBad = 0;    intree->SetBranchAddress("SiStripQualBad", &SiStripQualBad, NULL);
        bool withinAcceptance = false;      intree->SetBranchAddress("withinAcceptance", &withinAcceptance, NULL);
        int nHits = 0;                      intree->SetBranchAddress("nHits", &nHits, NULL);
        int nLostHits = 0;                  intree->SetBranchAddress("nLostHits", &nLostHits, NULL);
        float p = 0.;                       intree->SetBranchAddress("p", &p, NULL);
        float pT = 0.;                      intree->SetBranchAddress("pT", &pT, NULL);
        float chi2 = 0.;                    intree->SetBranchAddress("chi2", &chi2, NULL);
        unsigned int trajHitValid = 0;      intree->SetBranchAddress("trajHitValid", &trajHitValid, NULL);
        unsigned int run = 0;               intree->SetBranchAddress("run", &run, NULL);
        unsigned int event = 0;             intree->SetBranchAddress("event", &event, NULL);
        int bunchx = 0;                     intree->SetBranchAddress("bunchx", &bunchx, NULL);
        float timeDT = 0.;                  intree->SetBranchAddress("timeDT", &timeDT, NULL);
        float timeDTErr = 0.;               intree->SetBranchAddress("timeDTErr", &timeDTErr, NULL);
        int timeDTDOF = 0;                  intree->SetBranchAddress("timeDTDOF", &timeDTDOF, NULL);
        float timeECAL = 0.;                intree->SetBranchAddress("timeECAL", &timeECAL, NULL);
        float dedx = 0.;                    intree->SetBranchAddress("dedx", &dedx, NULL);
        int dedxNOM = 0;                    intree->SetBranchAddress("dedxNOM", &dedxNOM, NULL);
        int tquality = 0;                   intree->SetBranchAddress("tquality", &tquality, NULL);
        int istep = 0;                      intree->SetBranchAddress("istep", &istep, NULL);
//        float instLumi = 0.;                intree->SetBranchAddress("instLumi", &instLumi, NULL);
//        float PU = 0.;                      intree->SetBranchAddress("PU", &PU, NULL);
//        float commonMode = 0.;              intree->SetBranchAddress("commonMode", &commonMode, NULL);
        unsigned int layer = 0;             intree->SetBranchAddress("layer", &layer, NULL);


        for (auto it_runs = m_Sruns.begin() ; it_runs != m_Sruns.end() ; it_runs++)
        {
            for (auto it_layers = m_Slayers.begin() ; it_layers != m_Slayers.end() ; it_layers++)
            {
                for (auto it_bxs = m_Sbxs.begin() ; it_bxs != m_Sbxs.end() ; it_bxs++)
                {
                    TCanvas *c1 = new TCanvas();
                    std::string h_name = 
                        std::to_string(*it_runs) + '_'
                        + (*it_layers)
                        + "_bxs_" + (*it_bxs);
                    intree->Draw(("ClusterStoN>>+h_ClusterStoN_" + h_name + "(2000, 0, 2000)").c_str(), m_filter_exp.c_str(), "");
                    TH1F *h = (TH1F*)c1->GetPrimitive(("h_ClusterStoN_" + h_name).c_str());
                    map_h_ClusterStoN[h_name] = h;

                    intree->Draw("ClusterStoN:bunchx>>h3(3600, 0, 3600, 2000, 0, 2000)", m_filter_exp.c_str(), "colz");
                    map_h_ClusterStoN_vs_bx[h_name] = (TH2F*)(c1->GetPrimitive("h3"));
                }
            }
        }
    } // end of loop over input files
} // end of anEffAnalysis::analyze


// ------------ method called once each job just before starting event loop  ------------
void 
anEffAnalysis::beginJob()
{
    m_start_time = clock::now();

    for (auto it_runs = m_Sruns.begin() ; it_runs != m_Sruns.end() ; it_runs++)
    {
        for (auto it_layers = m_Slayers.begin() ; it_layers != m_Slayers.end() ; it_layers++)
        {
            for (auto it_bxs = m_Sbxs.begin() ; it_bxs != m_Sbxs.end() ; it_bxs++)
            {
                std::string h_name = 
                    std::to_string(*it_runs) + '_'
                    + (*it_layers)
                    + "_bxs_" + (*it_bxs);
                std::cout << "Will create histograms corresponding to " << h_name << std::endl;
                map_h_ClusterStoN[h_name] = new TH1F(("h_ClusterStoN_" + h_name).c_str(), ("h_ClusterStoN_" + h_name).c_str(), 2000, 0, 2000);
                map_h_ClusterStoN_vs_bx[h_name] = new TH2F(("h_ClusterStoN_vs_bx_" + h_name).c_str(), ("h_ClusterStoN_vs_bx_" + h_name).c_str(), 3600, 0, 3600, 2000, 0, 2000);
            } // end of loop over bx intervals
        } // end of loop over layers
    } // end of loop over runs

}

void anEffAnalysis::fitAll()
{
    return
}

// ------------ method called once each job just after ending the event loop  ------------
void 
anEffAnalysis::endJob() 
{
    m_output->cd();
    for (auto it = map_h_ClusterStoN.begin() ; it != map_h_ClusterStoN.end() ; it++) {
        std::cout << "#entries to file= " << it->second->GetEntries() << std::endl;
        it->second->Write();
    }
    for (auto it = map_h_ClusterStoN_vs_bx.begin() ; it != map_h_ClusterStoN_vs_bx.end() ; it++) {
        std::cout << "#entries to file= " << it->second->GetEntries() << std::endl;
        it->second->Write();
    }
    m_output->Write();
    if (m_perform_fit)
        fitAll();

    auto end_time = clock::now();
    std::cout << std::endl << "Job done in " << std::chrono::duration_cast<ms>(end_time - m_start_time).count() / 1000. << "s" << std::endl;
}

// ------------ method called when starting to processes a run  ------------
/*
void 
anEffAnalysis::beginRun(edm::Run const&, edm::EventSetup const&)
{
}
*/

// ------------ method called when ending the processing of a run  ------------
/*
void 
anEffAnalysis::endRun(edm::Run const&, edm::EventSetup const&)
{
}
*/

// ------------ method called when starting to processes a luminosity block  ------------
/*
void 
anEffAnalysis::beginLuminosityBlock(edm::LuminosityBlock const&, edm::EventSetup const&)
{
}
*/

// ------------ method called when ending the processing of a luminosity block  ------------
/*
void 
anEffAnalysis::endLuminosityBlock(edm::LuminosityBlock const&, edm::EventSetup const&)
{
}
*/

// ------------ method fills 'descriptions' with the allowed parameters for the module  ------------
void
anEffAnalysis::fillDescriptions(edm::ConfigurationDescriptions& descriptions) {
  //The following says we do not know what parameters are allowed so do no validation
  // Please change this to state exactly what you do use, even if it is no parameters
    edm::ParameterSetDescription desc;
    desc.setUnknown();
    descriptions.addDefault(desc);
}

//define this as a plug-in
DEFINE_FWK_MODULE(anEffAnalysis);
