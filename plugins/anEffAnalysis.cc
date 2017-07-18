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
        std::map<std::string, TH2F*> map_h_ClusterStoN_vs_bx_custom1;
        std::map<std::string, TH2F*> map_h_ClusterStoN_vs_bx_custom2;
        std::map<std::string, TH2F*> map_h_ClusterStoN_vs_bx_custom3;
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
    for (auto it = map_h_ClusterStoN_vs_bx_custom1.begin() ; it != map_h_ClusterStoN_vs_bx_custom1.end() ; it++)
        delete (*it).second;
    for (auto it = map_h_ClusterStoN_vs_bx_custom2.begin() ; it != map_h_ClusterStoN_vs_bx_custom2.end() ; it++)
        delete (*it).second;
    for (auto it = map_h_ClusterStoN_vs_bx_custom3.begin() ; it != map_h_ClusterStoN_vs_bx_custom3.end() ; it++)
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
                map_h_ClusterStoN_vs_bx_custom1[h_name]->Fill(bunchx, ClusterStoN);
                map_h_ClusterStoN_vs_bx_custom2[h_name]->Fill(bunchx, ClusterStoN);
                map_h_ClusterStoN_vs_bx_custom3[h_name]->Fill(bunchx, ClusterStoN);
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
                const int nbins1 = 30;
                Double_t edges1[nbins1 + 1] = {0, 1, 2, 41, 53, 183, 231, 266, 314, 349, 397, 1077, 1125, 1160, 1208, 1243, 1291, 1971, 2019, 2054, 2102, 2137, 2185, 2865, 2913, 2948, 2996, 3031, 3079, 3563, 3600};
                map_h_ClusterStoN_vs_bx_custom1[h_name] = new TH2F(("h_ClusterStoN_vs_bx_custom1_" + h_name).c_str(), ("h_ClusterStoN_vs_bx_custom1_" + h_name).c_str(), nbins1, edges1, 2000, 0, 2000);
                const int nbins2 = 108;
                Double_t edges2[nbins2 + 1] = {0, 56, 104, 111, 159, 190, 238, 245, 293, 300, 348, 379, 427, 434, 482, 489, 537, 568, 616, 623, 671, 678, 726, 761, 809, 816, 864, 895, 943, 950, 998, 1005, 1053, 1084, 1132, 1139, 1187, 1194, 1242, 1273, 1321, 1328, 1376, 1383, 1431, 1462, 1510, 1517, 1565, 1572, 1620, 1655, 1703, 1710, 1758, 1789, 1837, 1844, 1892, 1899, 1947, 1978, 2026, 2033, 2081, 2088, 2136, 2167, 2215, 2222, 2270, 2277, 2325, 2356, 2404, 2411, 2459, 2466, 2514, 2549, 2597, 2604, 2652, 2683, 2731, 2738, 2786, 2793, 2841, 2872, 2920, 2927, 2975, 2982, 3030, 3061, 3109, 3116, 3164, 3171, 3219, 3250, 3298, 3305, 3353, 3360, 3408, 3563, 3600};
                map_h_ClusterStoN_vs_bx_custom2[h_name] = new TH2F(("h_ClusterStoN_vs_bx_custom2_" + h_name).c_str(), ("h_ClusterStoN_vs_bx_custom2_" + h_name).c_str(), nbins2, edges2, 2000, 0, 2000);
                const int nbins3 = 94;
                Double_t edges3[nbins3 + 1] = {0, 65, 113, 120, 168, 175, 223, 254, 302, 309, 357, 364, 412, 443, 491, 498, 546, 553, 601, 770, 818, 825, 873, 880, 928, 959, 1007, 1014, 1062, 1069, 1117, 1148, 1196, 1203, 1251, 1258, 1306, 1337, 1385, 1392, 1440, 1447, 1495, 1579, 1580, 1664, 1712, 1719, 1767, 1774, 1822, 1853, 1901, 1908, 1956, 1963, 2011, 2042, 2090, 2097, 2145, 2152, 2200, 2231, 2279, 2286, 2334, 2341, 2389, 2558, 2606, 2613, 2661, 2668, 2716, 2747, 2795, 2802, 2850, 2857, 2905, 2936, 2984, 2991, 3039, 3046, 3094, 3125, 3173, 3180, 3228, 3235, 3283, 3563, 3600};
                map_h_ClusterStoN_vs_bx_custom3[h_name] = new TH2F(("h_ClusterStoN_vs_bx_custom3_" + h_name).c_str(), ("h_ClusterStoN_vs_bx_custom3_" + h_name).c_str(), nbins3, edges3, 2000, 0, 2000);
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
    for (auto it = map_h_ClusterStoN_vs_bx_custom1.begin() ; it != map_h_ClusterStoN_vs_bx_custom1.end() ; it++)
        it->second->Write();
    for (auto it = map_h_ClusterStoN_vs_bx_custom2.begin() ; it != map_h_ClusterStoN_vs_bx_custom2.end() ; it++)
        it->second->Write();
    for (auto it = map_h_ClusterStoN_vs_bx_custom3.begin() ; it != map_h_ClusterStoN_vs_bx_custom3.end() ; it++)
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
