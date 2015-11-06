// -*- C++ -*-
//
// Package:    CalibTracker/HIPAnalysis
// Class:      HIPAnalysis
// 
/**\class HIPAnalysis HIPAnalysis.cc CalibTracker/HIPAnalysis/plugins/HIPAnalysis.cc

 Description: [one line class summary]

 Implementation:
     [Notes on implementation]
*/
//
// Original Author:  Olivier Bondu
//         Created:  Fri, 30 Oct 2015 10:45:37 GMT
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
#include "FWCore/Utilities/interface/InputTag.h"
#include "DataFormats/TrackReco/interface/Track.h"
#include "DataFormats/TrackReco/interface/TrackFwd.h"
#include "FWCore/ServiceRegistry/interface/Service.h"

#include "TTree.h"
#include "TChain.h"
#include "TFile.h"

#include <CalibTracker/TreeWrapper/interface/TreeWrapper.h>
#include <string>
#include <algorithm>

#define BRANCH(NAME, ...) __VA_ARGS__& NAME = tree[#NAME].write<__VA_ARGS__>()

//
// class declaration
//

class HIPAnalysis : public edm::EDAnalyzer {
    public:
        HIPAnalysis(const edm::ParameterSet& iConfig):
            VInputFiles(iConfig.getUntrackedParameter<std::vector<std::string>>("InputFiles")),
            m_max_events_per_file(iConfig.getUntrackedParameter<Long64_t>("maxEventsPerFile")),
            m_output_filename(iConfig.getParameter<std::string>("output")),
            tree(tree_)
        {
            m_output.reset(TFile::Open(m_output_filename.c_str(), "recreate"));
        }

        ~HIPAnalysis();

        static void fillDescriptions(edm::ConfigurationDescriptions& descriptions);

    private:
        virtual void beginJob() override;
        virtual void analyze(const edm::Event&, const edm::EventSetup&) override;
        virtual void endJob() override;

        // ----------member data ---------------------------
        std::vector<std::string> VInputFiles;
        Long64_t m_max_events_per_file;
        std::string m_output_filename;
        std::unique_ptr<TFile> m_output;
        TTree* tree_ = new TTree("t", "t");
        ROOT::TreeWrapper tree;

        BRANCH(run, unsigned int);
        BRANCH(event, unsigned int);
        BRANCH(nTotEvents, unsigned int);
        BRANCH(nEvents, unsigned int);
        BRANCH(nTotTracks, unsigned int);
        BRANCH(nTracks, unsigned int);
        BRANCH(nTotClusters, unsigned int);
        BRANCH(nClusters, unsigned int);
        BRANCH(nSaturatedStrips, std::vector<int>);
        class isEqual{
            public:
		        template <class T> bool operator () (const T& PseudoDetId1, const T& PseudoDetId2) { return PseudoDetId1==PseudoDetId2; }
        };
};

HIPAnalysis::~HIPAnalysis()
{
    m_output->Close();
}


//
// member functions
//

// ------------ method called for each event  ------------
void
HIPAnalysis::analyze(const edm::Event& iEvent, const edm::EventSetup& iSetup)
{
    for(unsigned int i=0;i<VInputFiles.size();i++)
    {
        std::cout << std::endl << "-----" << std::endl;
        printf("Opening file %3i/%3i --> %s\n",i+1, (int)VInputFiles.size(), (char*)(VInputFiles[i].c_str())); fflush(stdout);
        TChain* intree = new TChain("gainCalibrationTree/tree");
        intree->Add(VInputFiles[i].c_str());

        TString EventPrefix("");
        TString EventSuffix("");

        TString TrackPrefix("track");
        TString TrackSuffix("");

        TString CalibPrefix("GainCalibration");
        TString CalibSuffix("");

        unsigned int                 eventnumber    = 0;    intree->SetBranchAddress(EventPrefix + "event"          + EventSuffix, &eventnumber   , NULL);
        unsigned int                 runnumber      = 0;    intree->SetBranchAddress(EventPrefix + "run"            + EventSuffix, &runnumber     , NULL);
        unsigned int                 luminumber     = 0;    intree->SetBranchAddress(EventPrefix + "lumi"           + EventSuffix, &luminumber    , NULL);
        std::vector<bool>*           TrigTech       = 0;    intree->SetBranchAddress(EventPrefix + "TrigTech"       + EventSuffix, &TrigTech      , NULL);

        std::vector<double>*         trackchi2ndof  = 0;    intree->SetBranchAddress(TrackPrefix + "chi2ndof"       + TrackSuffix, &trackchi2ndof , NULL);
        std::vector<float>*          trackp         = 0;    intree->SetBranchAddress(TrackPrefix + "momentum"       + TrackSuffix, &trackp        , NULL);
        std::vector<float>*          trackpt        = 0;    intree->SetBranchAddress(TrackPrefix + "pt"             + TrackSuffix, &trackpt       , NULL);
        std::vector<double>*         tracketa       = 0;    intree->SetBranchAddress(TrackPrefix + "eta"            + TrackSuffix, &tracketa      , NULL);
        std::vector<double>*         trackphi       = 0;    intree->SetBranchAddress(TrackPrefix + "phi"            + TrackSuffix, &trackphi      , NULL);
        std::vector<unsigned int>*   trackhitsvalid = 0;    intree->SetBranchAddress(TrackPrefix + "hitsvalid"      + TrackSuffix, &trackhitsvalid, NULL);

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
        std::vector<float>*          path           = 0;    intree->SetBranchAddress(CalibPrefix + "path"           + CalibSuffix, &path          , NULL);
        std::vector<float>*          chargeoverpath = 0;    intree->SetBranchAddress(CalibPrefix + "chargeoverpath" + CalibSuffix, &chargeoverpath, NULL);
        std::vector<unsigned char>*  amplitude      = 0;    intree->SetBranchAddress(CalibPrefix + "amplitude"      + CalibSuffix, &amplitude     , NULL);
        std::vector<double>*         gainused       = 0;    intree->SetBranchAddress(CalibPrefix + "gainused"       + CalibSuffix, &gainused      , NULL);

        nTotEvents = nEvents = 0;
        nTotTracks = nTracks = 0;
        nTotClusters = nClusters = 0;

        printf("Number of Events = %i + %i = %i\n", nTotEvents, (unsigned int)intree->GetEntries(), (unsigned int)(nEvents + intree->GetEntries()));
        int TreeStep = intree->GetEntries() / 50; if(TreeStep <= 1) TreeStep = 1;
        printf("Progressing Bar              :0%%       20%%       40%%       60%%       80%%       100%%\n");
        printf("Looping on the Tree          :");
        unsigned int maxEntries = m_max_events_per_file > 0 ? std::min(m_max_events_per_file, (Long64_t)intree->GetEntries()) : intree->GetEntries();
        for (unsigned int ientry = 0; ientry < maxEntries; ientry++)
        {
            run = runnumber;
            event = eventnumber;
            if (ientry % TreeStep == 0)
            {
                printf(".");
                fflush(stdout);
            }
            intree->GetEntry(ientry);

            nTotEvents++;
            nTotTracks += (*trackp).size();
            nTotClusters += (*chargeoverpath).size();

        	unsigned int FirstAmplitude = 0;
            nClusters = 0;
            nSaturatedStrips.clear();
            for (unsigned int i = 0; i < (*chargeoverpath).size(); i++)
            { // Loop over clusters
                if (!(*saturation)[i]) continue;
                
                FirstAmplitude += (*nstrips)[i];
                int nSaturatedStrips_ = 0;
                for (unsigned int s = 0; s < (*nstrips)[i]; s++)
                {
                    int StripCharge =  (*amplitude)[FirstAmplitude - (*nstrips)[i] + s];
                    if (StripCharge > 253)
                        nSaturatedStrips_++;
                }
                nSaturatedStrips.push_back(nSaturatedStrips_);
                if (nSaturatedStrips_ >= 3)
                    nClusters++;

            }// End of loop over clusters
            if (nClusters > 0)
                nEvents++;

        }printf("\n");// End of loop over events

    std::cout << "nEvents / nTotEvents= " << nEvents << " / " << nTotEvents << "\tnTracks / nTotTracks= " << nTracks << " / " << nTotTracks << "\tnClusters / nTotClusters= " << nClusters << " / " << nTotClusters << std::endl;   

    tree.fill();

    } // End of loop over files


}


// ------------ method called once each job just before starting event loop  ------------
void 
HIPAnalysis::beginJob()
{
}

// ------------ method called once each job just after ending the event loop  ------------
void 
HIPAnalysis::endJob() 
{
    m_output->cd();
    tree_->Write();
}

// ------------ method called when starting to processes a run  ------------
/*
void 
HIPAnalysis::beginRun(edm::Run const&, edm::EventSetup const&)
{
}
*/

// ------------ method called when ending the processing of a run  ------------
/*
void 
HIPAnalysis::endRun(edm::Run const&, edm::EventSetup const&)
{
}
*/

// ------------ method called when starting to processes a luminosity block  ------------
/*
void 
HIPAnalysis::beginLuminosityBlock(edm::LuminosityBlock const&, edm::EventSetup const&)
{
}
*/

// ------------ method called when ending the processing of a luminosity block  ------------
/*
void 
HIPAnalysis::endLuminosityBlock(edm::LuminosityBlock const&, edm::EventSetup const&)
{
}
*/

// ------------ method fills 'descriptions' with the allowed parameters for the module  ------------
void
HIPAnalysis::fillDescriptions(edm::ConfigurationDescriptions& descriptions) {
  //The following says we do not know what parameters are allowed so do no validation
  // Please change this to state exactly what you do use, even if it is no parameters
  edm::ParameterSetDescription desc;
  desc.setUnknown();
  descriptions.addDefault(desc);

  //Specify that only 'tracks' is allowed
  //To use, remove the default given above and uncomment below
  //ParameterSetDescription desc;
  //desc.addUntracked<edm::InputTag>("tracks","ctfWithMaterialTracks");
  //descriptions.addDefault(desc);
}

//define this as a plug-in
DEFINE_FWK_MODULE(HIPAnalysis);
