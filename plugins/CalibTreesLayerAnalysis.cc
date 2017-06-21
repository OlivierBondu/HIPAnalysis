// -*- C++ -*-
//
// Package:    CalibTracker/CalibTreesLayerAnalysis
// Class:      CalibTreesLayerAnalysis
// 
/**\class CalibTreesLayerAnalysis CalibTreesLayerAnalysis.cc CalibTracker/CalibTreesLayerAnalysis/plugins/CalibTreesLayerAnalysis.cc

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



std::vector<std::string> split(std::string str, char delimiter) {
    std::vector<std::string> internal;
    std::stringstream ss(str); // Turn the string into a stream.
    std::string tok; 
    while(getline(ss, tok, delimiter)) {
        internal.push_back(tok);
    }
    return internal;
}

//
// class declaration
//

class CalibTreesLayerAnalysis : public edm::EDAnalyzer {
    public:
        explicit CalibTreesLayerAnalysis(const edm::ParameterSet&);
        ~CalibTreesLayerAnalysis();

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
        std::map<std::string, TH1F*> map_h_chargeoverpath;
        std::map<std::string, TH2F*> map_h_chargeoverpath_vs_bx;
        std::map<std::string, TH1F*> map_h_PU;
        std::map<std::string, TH2F*> map_h_PU_vs_bx;
        std::map<std::string, TH1F*> map_h_instLumi;
        std::map<std::string, TH2F*> map_h_instLumi_vs_bx;
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
CalibTreesLayerAnalysis::CalibTreesLayerAnalysis(const edm::ParameterSet& iConfig):
HIPDEBUG(iConfig.getParameter<bool>("debug")),
VInputFiles(iConfig.getUntrackedParameter<std::vector<std::string>>("InputFiles")),
m_max_events_per_file(iConfig.getUntrackedParameter<Long64_t>("maxEventsPerFile")),
m_input_treename(iConfig.getParameter<std::string>("inputTreeName")),
m_output_filename(iConfig.getParameter<std::string>("output")),
m_Vruns(iConfig.getUntrackedParameter<std::vector<int>>("runs")),
m_Vlumisections(iConfig.getUntrackedParameter<std::vector<edm::LuminosityBlockRange>>("lumisections")),
m_Vlayers(iConfig.getUntrackedParameter<std::vector<std::string>>("layers")),
m_Vbxs(iConfig.getUntrackedParameter<std::vector<std::string>>("bxs"))
{
   //now do what ever initialization is needed
    m_output.reset(TFile::Open(m_output_filename.c_str(), "recreate"));
    std::copy(m_Vruns.begin(), m_Vruns.end(), std::inserter(m_Sruns, m_Sruns.end()));
    std::copy(m_Vlayers.begin(), m_Vlayers.end(), std::inserter(m_Slayers, m_Slayers.end()));
    std::copy(m_Vbxs.begin(), m_Vbxs.end(), std::inserter(m_Sbxs, m_Sbxs.end()));
}


CalibTreesLayerAnalysis::~CalibTreesLayerAnalysis()
{
   // do anything here that needs to be done at desctruction time
   // (e.g. close files, deallocate resources etc.)
    for (auto it = map_h_chargeoverpath.begin() ; it != map_h_chargeoverpath.end() ; it++)
        delete (*it).second;
    for (auto it = map_h_chargeoverpath_vs_bx.begin() ; it != map_h_chargeoverpath_vs_bx.end() ; it++)
        delete (*it).second;
    for (auto it = map_h_PU.begin() ; it != map_h_PU.end() ; it++)
        delete (*it).second;
    for (auto it = map_h_PU_vs_bx.begin() ; it != map_h_PU_vs_bx.end() ; it++)
        delete (*it).second;
    for (auto it = map_h_instLumi.begin() ; it != map_h_instLumi.end() ; it++)
        delete (*it).second;
    for (auto it = map_h_instLumi_vs_bx.begin() ; it != map_h_instLumi_vs_bx.end() ; it++)
        delete (*it).second;
    m_output->Close();
}


//
// member functions
//

// ------------ method called for each event  ------------
void
CalibTreesLayerAnalysis::analyze(const edm::Event& iEvent, const edm::EventSetup& iSetup)
{
    unsigned long long ievent = iEvent.id().event();
    unsigned long long ifile = ievent - 1;
    if (ifile < VInputFiles.size())
    {
        std::cout << std::endl << "-----" << std::endl;
        printf("Opening file %3llu/%3i --> %s\n", ifile + 1, (int)VInputFiles.size(), (char*)(VInputFiles[ifile].c_str())); fflush(stdout);
        TChain* intree = new TChain(m_input_treename.c_str());
        intree->Add(VInputFiles[ifile].c_str());
        TString EventPrefix("");
        TString EventSuffix("");

        TString TrackPrefix("track");
        TString TrackSuffix("");

        TString CalibPrefix("GainCalibration");
        TString CalibSuffix("");

        unsigned int                 eventnumber    = 0;    intree->SetBranchAddress(EventPrefix + "event"          + EventSuffix, &eventnumber   , NULL);
        unsigned int                 runnumber      = 0;    intree->SetBranchAddress(EventPrefix + "run"            + EventSuffix, &runnumber     , NULL);
        unsigned int                 luminumber     = 0;    intree->SetBranchAddress(EventPrefix + "lumi"           + EventSuffix, &luminumber    , NULL);
        unsigned int                 bxnumber       = 0;    intree->SetBranchAddress(EventPrefix + "bx"             + EventSuffix, &bxnumber      , NULL);
        std::vector<bool>*           TrigTech       = 0;    intree->SetBranchAddress(EventPrefix + "TrigTech"       + EventSuffix, &TrigTech      , NULL);
        std::vector<bool>*           TrigPh         = 0;    intree->SetBranchAddress(EventPrefix + "TrigPh"         + EventSuffix, &TrigPh        , NULL);
        float                        PU             = 0;    intree->SetBranchAddress(EventPrefix + "PU"             + EventSuffix, &PU            , NULL);
        float                        instLumi       = 0;    intree->SetBranchAddress(EventPrefix + "instLumi"       + EventSuffix, &instLumi      , NULL);

        std::vector<double>*         trackchi2ndof  = 0;    intree->SetBranchAddress(TrackPrefix + "chi2ndof"       + TrackSuffix, &trackchi2ndof , NULL);
        std::vector<float>*          trackp         = 0;    intree->SetBranchAddress(TrackPrefix + "momentum"       + TrackSuffix, &trackp        , NULL);
        std::vector<float>*          trackpt        = 0;    intree->SetBranchAddress(TrackPrefix + "pt"             + TrackSuffix, &trackpt       , NULL);
        std::vector<double>*         tracketa       = 0;    intree->SetBranchAddress(TrackPrefix + "eta"            + TrackSuffix, &tracketa      , NULL);
        std::vector<double>*         trackphi       = 0;    intree->SetBranchAddress(TrackPrefix + "phi"            + TrackSuffix, &trackphi      , NULL);
        std::vector<unsigned int>*   trackhitsvalid = 0;    intree->SetBranchAddress(TrackPrefix + "hitsvalid"      + TrackSuffix, &trackhitsvalid, NULL);
        std::vector<int>*            trackalgo      = 0;    intree->SetBranchAddress(TrackPrefix + "algo"           + TrackSuffix, &trackalgo     , NULL);

        std::vector<int>*            trackindex     = 0;    intree->SetBranchAddress(CalibPrefix + "trackindex"     + CalibSuffix, &trackindex    , NULL);
        std::vector<unsigned int>*   rawid          = 0;    intree->SetBranchAddress(CalibPrefix + "rawid"          + CalibSuffix, &rawid         , NULL);
        std::vector<float>*          localdirx      = 0;    intree->SetBranchAddress(CalibPrefix + "localdirx"      + CalibSuffix, &localdirx     , NULL);
        std::vector<float>*          localdiry      = 0;    intree->SetBranchAddress(CalibPrefix + "localdiry"      + CalibSuffix, &localdiry     , NULL);
        std::vector<float>*          localdirz      = 0;    intree->SetBranchAddress(CalibPrefix + "localdirz"      + CalibSuffix, &localdirz     , NULL);
        std::vector<unsigned short>* firststrip     = 0;    intree->SetBranchAddress(CalibPrefix + "firststrip"     + CalibSuffix, &firststrip    , NULL);
        std::vector<unsigned short>* nstrips        = 0;    intree->SetBranchAddress(CalibPrefix + "nstrips"        + CalibSuffix, &nstrips       , NULL);
        std::vector<bool>*           saturation     = 0;    intree->SetBranchAddress(CalibPrefix + "saturation"     + CalibSuffix, &saturation    , NULL);
        std::vector<bool>*           overlapping    = 0;    intree->SetBranchAddress(CalibPrefix + "overlapping"    + CalibSuffix, &overlapping   , NULL);
        std::vector<bool>*           farfromedge    = 0;    intree->SetBranchAddress(CalibPrefix + "farfromedge"    + CalibSuffix, &farfromedge   , NULL);
        std::vector<unsigned int>*   charge         = 0;    intree->SetBranchAddress(CalibPrefix + "charge"         + CalibSuffix, &charge        , NULL);
        std::vector<double>*         path           = 0;    intree->SetBranchAddress(CalibPrefix + "path"           + CalibSuffix, &path          , NULL);
        std::vector<double>*         chargeoverpath = 0;    intree->SetBranchAddress(CalibPrefix + "chargeoverpath" + CalibSuffix, &chargeoverpath, NULL);
        std::vector<unsigned char>*  amplitude      = 0;    intree->SetBranchAddress(CalibPrefix + "amplitude"      + CalibSuffix, &amplitude     , NULL);
        std::vector<double>*         gainused       = 0;    intree->SetBranchAddress(CalibPrefix + "gainused"       + CalibSuffix, &gainused      , NULL);
        std::vector<double>*         gainusedTick       = 0;    intree->SetBranchAddress(CalibPrefix + "gainusedTick"       + CalibSuffix, &gainusedTick      , NULL);

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
                std::cout << "Event: Run " << runnumber << ", Lumisection " << luminumber << ", Event " << eventnumber << ", BX " << bxnumber << std::endl;

            // Skip event if it is not in the short list of requested events
            if (m_Sruns.find(runnumber) == m_Sruns.end())
            {
                if (HIPDEBUG) {std::cout << "run #" << runnumber << " not in the list of required runs, skipping the event" << std::endl;}
                continue;
            }
            bool isInLSList = false;
            for (auto it_ls = m_Vlumisections.begin() ; it_ls != m_Vlumisections.end() ; it_ls++)
            {
                if ((it_ls->startLumi() < luminumber) && (luminumber < it_ls->endLumi()))
                    isInLSList = true;
            }
            if (!isInLSList)
            {
                if (HIPDEBUG) {std::cout << "LS #" << luminumber << " not in the list of required lumisections, skipping the event" << std::endl;}
                continue;
            }

            // 
            for (unsigned int icluster = 0; icluster < (*chargeoverpath).size(); icluster++)
            { // Loop over clusters
                int layerid =  tkLayerMap_->layerSearch((*rawid)[icluster]);
                std::string layer = tkDetMap_->getLayerName(layerid);
                auto it_layers = m_Slayers.find(layer);
                if (it_layers == m_Slayers.end())
                {
                    continue;
                }
                if (HIPDEBUG) {std::cout << "Cluster #" << icluster << " belongs to layer " << layer << std::endl;}
                for (auto it_ls = m_Vlumisections.begin() ; it_ls != m_Vlumisections.end() ; it_ls++)
                { // Loop over lumi sections
                    if ((it_ls->startLumi() > luminumber) || (luminumber > it_ls->endLumi()))
                        continue;
                    for (auto it_bxs = m_Sbxs.begin() ; it_bxs != m_Sbxs.end() ; it_bxs++)
                    { // Loop over bx intervals
                        std::vector<std::string> tmp = split(*it_bxs, '-');
                        unsigned int bxlow = std::stoi(tmp[0]);
                        unsigned int bxhigh = std::stoi(tmp[1]);
                        if ((bxlow > bxnumber) || (bxnumber > bxhigh))
                            continue;
                        std::string h_name =
                            std::to_string(runnumber) + '_'
                            + std::to_string(it_ls->startLumi()) + '-' + std::to_string(it_ls->endLumi()) + '_'
                            + (*it_layers)
                            + "_bxs_" + (*it_bxs);
                        if (HIPDEBUG) {std::cout << "\tAdding cluster to histo " << h_name << std::endl;}
                        map_h_chargeoverpath[h_name]->Fill((*chargeoverpath)[icluster]);
                        map_h_chargeoverpath_vs_bx[h_name]->Fill(bxnumber, (*chargeoverpath)[icluster]);
                    } // end of loop over bx intervals
                } // end of loop over lumi sections
            } // end of loop over clusters
// FIXME
//            map_h_PU[h_name]->Fill(PU);
//            map_h_PU_vs_bx[h_name]->Fill(bxnumber, PU);
//            map_h_instLumi[h_name]->Fill(instLumi);
//            map_h_instLumi_vs_bx[h_name]->Fill(bxnumber, instLumi);
        } // end of loop over entries in the calibTree
    } // end of loop over input files



/*
   using namespace edm;



#ifdef THIS_IS_AN_EVENT_EXAMPLE
   Handle<ExampleData> pIn;
   iEvent.getByLabel("example",pIn);
#endif
   
#ifdef THIS_IS_AN_EVENTSETUP_EXAMPLE
   ESHandle<SetupData> pSetup;
   iSetup.get<SetupRecord>().get(pSetup);
#endif
*/
}


// ------------ method called once each job just before starting event loop  ------------
void 
CalibTreesLayerAnalysis::beginJob()
{
    m_start_time = clock::now();

    for (auto it_runs = m_Sruns.begin() ; it_runs != m_Sruns.end() ; it_runs++)
    {
        for (auto it_ls = m_Vlumisections.begin() ; it_ls != m_Vlumisections.end() ; it_ls++)
        {
            for (auto it_layers = m_Slayers.begin() ; it_layers != m_Slayers.end() ; it_layers++)
            {
                for (auto it_bxs = m_Sbxs.begin() ; it_bxs != m_Sbxs.end() ; it_bxs++)
                {
                    std::string h_name = 
                        std::to_string(*it_runs) + '_'
                        + std::to_string(it_ls->startLumi()) + '-' + std::to_string(it_ls->endLumi()) + '_'
                        + (*it_layers)
                        + "_bxs_" + (*it_bxs);
                    std::cout << "Will create histograms corresponding to " << h_name << std::endl;
                    map_h_chargeoverpath[h_name] = new TH1F(("h_chargeoverpath_" + h_name).c_str(), ("h_chargeoverpath_" + h_name).c_str(), 2000, 0, 2000);
                    map_h_chargeoverpath_vs_bx[h_name] = new TH2F(("h_chargeoverpath_vs_bx_" + h_name).c_str(), ("h_chargeoverpath_vs_bx_" + h_name).c_str(), 3600, 0, 3600, 2000, 0, 2000);
                    map_h_PU[h_name] = new TH1F(("h_PU_" + h_name).c_str(), ("h_PU_" + h_name).c_str(), 2000, 0, 2000);
                    map_h_PU_vs_bx[h_name] = new TH2F(("h_PU_vs_bx_" + h_name).c_str(), ("h_PU_vs_bx_" + h_name).c_str(), 3600, 0, 3600, 2000, 0, 2000);
                    map_h_instLumi[h_name] = new TH1F(("h_instLumi_" + h_name).c_str(), ("h_instLumi_" + h_name).c_str(), 2000, 0, 2000);
                    map_h_instLumi_vs_bx[h_name] = new TH2F(("h_instLumi_vs_bx_" + h_name).c_str(), ("h_instLumi_vs_bx_" + h_name).c_str(), 3600, 0, 3600, 2000, 0, 2000);
                } // end of loop over bx intervals
            } // end of loop over layers
        } // end of loop over lumisection blocks
    } // end of loop over runs

}

// ------------ method called once each job just after ending the event loop  ------------
void 
CalibTreesLayerAnalysis::endJob() 
{
    for (auto it = map_h_chargeoverpath.begin() ; it != map_h_chargeoverpath.end() ; it++)
        it->second->Write();
    for (auto it = map_h_chargeoverpath_vs_bx.begin() ; it != map_h_chargeoverpath_vs_bx.end() ; it++)
        it->second->Write();
    for (auto it = map_h_PU.begin() ; it != map_h_PU.end() ; it++)
        it->second->Write();
    for (auto it = map_h_PU_vs_bx.begin() ; it != map_h_PU_vs_bx.end() ; it++)
        it->second->Write();
    for (auto it = map_h_instLumi.begin() ; it != map_h_instLumi.end() ; it++)
        it->second->Write();
    for (auto it = map_h_instLumi_vs_bx.begin() ; it != map_h_instLumi_vs_bx.end() ; it++)
        it->second->Write();
    m_output->Write();

    auto end_time = clock::now();
    std::cout << std::endl << "Job done in " << std::chrono::duration_cast<ms>(end_time - m_start_time).count() / 1000. << "s" << std::endl;
}

// ------------ method called when starting to processes a run  ------------
/*
void 
CalibTreesLayerAnalysis::beginRun(edm::Run const&, edm::EventSetup const&)
{
}
*/

// ------------ method called when ending the processing of a run  ------------
/*
void 
CalibTreesLayerAnalysis::endRun(edm::Run const&, edm::EventSetup const&)
{
}
*/

// ------------ method called when starting to processes a luminosity block  ------------
/*
void 
CalibTreesLayerAnalysis::beginLuminosityBlock(edm::LuminosityBlock const&, edm::EventSetup const&)
{
}
*/

// ------------ method called when ending the processing of a luminosity block  ------------
/*
void 
CalibTreesLayerAnalysis::endLuminosityBlock(edm::LuminosityBlock const&, edm::EventSetup const&)
{
}
*/

// ------------ method fills 'descriptions' with the allowed parameters for the module  ------------
void
CalibTreesLayerAnalysis::fillDescriptions(edm::ConfigurationDescriptions& descriptions) {
  //The following says we do not know what parameters are allowed so do no validation
  // Please change this to state exactly what you do use, even if it is no parameters
    edm::ParameterSetDescription desc;
    desc.setUnknown();
    descriptions.addDefault(desc);
}

//define this as a plug-in
DEFINE_FWK_MODULE(CalibTreesLayerAnalysis);
