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

#include "FWCore/Framework/interface/Event.h"
#include "FWCore/Framework/interface/MakerMacros.h"

#include "FWCore/ParameterSet/interface/ParameterSet.h"

// Tracker geometry
#include "CalibTracker/SiStripCommon/interface/TkDetMap.h"

// ROOT includes
#include "TChain.h"
#include "TFile.h"
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
        std::map<std::string, TH2F*> map_h_ClusterStoN_vs_bx_custom;
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
    for (auto it = map_h_ClusterStoN_vs_bx_custom.begin() ; it != map_h_ClusterStoN_vs_bx_custom.end() ; it++)
        delete (*it).second;
    m_output->Close();
}


//
// member functions
//

// ------------ method called for each event  ------------
void
anEffAnalysis::analyze(const edm::Event& iEvent, const edm::EventSetup& iSetup)
{
    unsigned long long ievent = iEvent.id().event();
    unsigned long long ifile = ievent - 1;
    if (ifile < VInputFiles.size())
    {
        std::cout << std::endl << "-----" << std::endl;
        printf("Opening file %3llu/%3i --> %s\n", ifile + 1, (int)VInputFiles.size(), (char*)(VInputFiles[ifile].c_str())); fflush(stdout);

        // The tree is flat, so let's filter out events that do not interest us
        // NB: the expression is done in the python config file because it's easier in python than in C++
        // FIXME: the full copy adds some overhead, so let's kill this for now
        TChain* intree = new TChain(m_input_treename.c_str());
        intree->Add(VInputFiles[ifile].c_str());
//        TChain* chained_intree = new TChain(m_input_treename.c_str());
//        chained_intree->Add(VInputFiles[ifile].c_str());
//        TTree *intree = chained_intree->CopyTree(m_filter_exp.c_str());

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
// TODO
// layer


//        unsigned int nTotEvents = 0;
//        printf("Number of Events = %i + %i = %i\n", nTotEvents, (unsigned int)intree->GetEntries(), (unsigned int)(nEvents[0] + intree->GetEntries()));
        unsigned int maxEntries = m_max_events_per_file > 0 ? std::min(m_max_events_per_file, (Long64_t)intree->GetEntries()) : intree->GetEntries();
        if (HIPDEBUG) {maxEntries = 2; }

        
        for (unsigned int ientry = 0; ientry < maxEntries; ientry++)
        { // Loop over entries in the calib Trees
            if ((!HIPDEBUG) && ((ientry % 1000 == 0 && ientry < 10000) || (ientry % 10000 == 0)))
                std::cout << "# Processing event " << ientry << " / " << maxEntries << std::endl;
            else if (HIPDEBUG)
                std::cout << "# Processing event " << ientry << " / " << maxEntries << std::endl;
            intree->GetEntry(ientry);
            if (HIPDEBUG)
                std::cout << "Event: Run " << run << ", Lumisection " << "XXXXX" << ", Event " << event << ", BX " << bunchx << std::endl;

            // Skip event if it is not in the short list of requested events
            if (m_Sruns.find(run) == m_Sruns.end())
            {
                if (HIPDEBUG) {std::cout << "run #" << run << " not in the list of required runs, skipping the event" << std::endl;}
                continue;
            }

            int layerid =  tkLayerMap_->layerSearch(Id);
            std::string layer = tkDetMap_->getLayerName(layerid);
            auto it_layers = m_Slayers.find(layer);
            if (it_layers == m_Slayers.end())
            {
                continue;
            }
            if (HIPDEBUG) {std::cout << "Hit #" << ientry << " belongs to layer " << layer << std::endl;}
            for (auto it_bxs = m_Sbxs.begin() ; it_bxs != m_Sbxs.end() ; it_bxs++)
            { // Loop over bx intervals
                std::vector<std::string> tmp = anEffAnalysisTool::split(*it_bxs, '-');
                int bxlow = std::stoi(tmp[0]);
                int bxhigh = std::stoi(tmp[1]);
                if ((bxlow > bunchx) || (bunchx > bxhigh))
                    continue;
                std::string h_name =
                    std::to_string(run) + '_'
                    + (*it_layers)
                    + "_bxs_" + (*it_bxs);
                if (HIPDEBUG) {std::cout << "\tAdding cluster to histo " << h_name << std::endl;}
                map_h_ClusterStoN[h_name]->Fill(ClusterStoN);
                map_h_ClusterStoN_vs_bx[h_name]->Fill(bunchx, ClusterStoN);
                map_h_ClusterStoN_vs_bx_custom[h_name]->Fill(bunchx, ClusterStoN);
            } // end of loop over bx intervals
        } // end of loop over entries in the calibTree
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
                const int nbins = 30;
                Double_t EDGES[nbins + 1] = {0, 1, 2, 41, 53, 183, 231, 266, 314, 349, 397, 1077, 1125, 1160, 1208, 1243, 1291, 1971, 2019, 2054, 2102, 2137, 2185, 2865, 2913, 2948, 2996, 3031, 3079, 3563, 3600};
                map_h_ClusterStoN_vs_bx_custom[h_name] = new TH2F(("h_ClusterStoN_vs_bx_custom_" + h_name).c_str(), ("h_ClusterStoN_vs_bx_custom_" + h_name).c_str(), nbins, EDGES, 2000, 0, 2000);
            } // end of loop over bx intervals
        } // end of loop over layers
    } // end of loop over runs

}

// ------------ method called once each job just after ending the event loop  ------------
void 
anEffAnalysis::endJob() 
{
    for (auto it = map_h_ClusterStoN.begin() ; it != map_h_ClusterStoN.end() ; it++)
        it->second->Write();
    for (auto it = map_h_ClusterStoN_vs_bx.begin() ; it != map_h_ClusterStoN_vs_bx.end() ; it++)
        it->second->Write();
    for (auto it = map_h_ClusterStoN_vs_bx_custom.begin() ; it != map_h_ClusterStoN_vs_bx_custom.end() ; it++)
        it->second->Write();
    m_output->Write();

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
