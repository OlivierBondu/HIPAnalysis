// -*- C++ -*-
//
// Package:    CalibTracker/HIPAnalysis
// Class:      HIPAnalysis
// 
/**\class HIPAnalysis HIPAnalysis.cc CalibTracker/HIPAnalysis/plugins/HIPAnalysis.cc

 Description: [one line class summary]

 Implementation:
        Inspiration from SiStripGainFromCalibTree.cc:
        https://github.com/cms-sw/cmssw/blob/6b16de370881dd8ef339d34811b3d1e176c02b80/CalibTracker/SiStripChannelGain/plugins/SiStripGainFromCalibTree.cc
*/
//
// Original Author:  Olivier Bondu
//         Created:  Fri, 30 Oct 2015 10:45:37 GMT
//
//



// user include files
#include "FWCore/Framework/interface/Frameworkfwd.h"
#include "FWCore/Framework/interface/EDAnalyzer.h"
#include "FWCore/Framework/interface/ESHandle.h"
#include "FWCore/Framework/interface/Event.h"
#include "FWCore/Framework/interface/MakerMacros.h"

#include "FWCore/ParameterSet/interface/ParameterSet.h"
#include "FWCore/Utilities/interface/InputTag.h"
#include "FWCore/ServiceRegistry/interface/Service.h"

// Tracker geometry
#include "Geometry/TrackerGeometryBuilder/interface/TrackerGeometry.h"
#include "Geometry/TrackerGeometryBuilder/interface/StripGeomDetUnit.h"
#include "Geometry/Records/interface/TrackerDigiGeometryRecord.h"
#include "DataFormats/DetId/interface/DetId.h"
#include "DataFormats/SiStripDetId/interface/StripSubdetector.h"
#include "DataFormats/SiStripDetId/interface/SiStripDetId.h"

// ROOT includes
#include "TTree.h"
#include "TChain.h"
#include "TFile.h"
// Utilities
#include <CalibTracker/TreeWrapper/interface/TreeWrapper.h>
// C++ includes
#include <memory>
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

        unsigned int nSaturationLevels = 10;
        BRANCH(run, unsigned int);
        BRANCH(lumi, unsigned int);
        BRANCH(event, unsigned int);
        BRANCH(bx, unsigned int);
        BRANCH(nTotEvents, unsigned int);
        BRANCH(nEvents, std::vector<unsigned int>);
        BRANCH(nTotTracks, unsigned int);
        BRANCH(nTracks, unsigned int);
        BRANCH(nTotClusters, unsigned int);
        BRANCH(nSaturatedClusters, std::vector<unsigned int>);
        BRANCH(nSaturatedStrips, std::vector<unsigned int>);
        BRANCH(subDetector, std::vector<unsigned int>);
        BRANCH(saturatedCharge, std::vector<std::vector<unsigned int>>);
        BRANCH(saturatedChargeoverpath, std::vector<std::vector<unsigned int>>);
        BRANCH(saturatedAmplitude, std::vector<std::vector<unsigned int>>);
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
    edm::ESHandle<TrackerGeometry> tkGeom;
    iSetup.get<TrackerDigiGeometryRecord>().get( tkGeom );
    std::cout << "StripSubdetector::TIB= " << (StripSubdetector::TIB) << std::endl;
    std::cout << "StripSubdetector::TID= " << (StripSubdetector::TID) << std::endl;
    std::cout << "StripSubdetector::TOB= " << (StripSubdetector::TOB) << std::endl;
    std::cout << "StripSubdetector::TEC= " << (StripSubdetector::TEC) << std::endl;

    unsigned long long ievent = iEvent.id().event();
    std::cout << "ievent= " << ievent << std::endl;
    unsigned long long ifile = ievent - 1;
    if (ifile < VInputFiles.size())
    {
        std::cout << std::endl << "-----" << std::endl;
        printf("Opening file %3llu/%3i --> %s\n", ifile + 1, (int)VInputFiles.size(), (char*)(VInputFiles[ifile].c_str())); fflush(stdout);
        TChain* intree = new TChain("gainCalibrationTree/tree");
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

        nTotEvents = 0;
        nEvents.clear();
        for (unsigned int i = 0; i < nSaturationLevels; i++)
            { nEvents.push_back(0); }
        nTotTracks = nTracks = 0;
        nTotClusters = 0;

        nSaturatedClusters.clear();
        for (unsigned int i = 0; i < nSaturationLevels; i++)
            { nSaturatedClusters.push_back(0); }

        printf("Number of Events = %i + %i = %i\n", nTotEvents, (unsigned int)intree->GetEntries(), (unsigned int)(nEvents[0] + intree->GetEntries()));
        unsigned int maxEntries = m_max_events_per_file > 0 ? std::min(m_max_events_per_file, (Long64_t)intree->GetEntries()) : intree->GetEntries();
        for (unsigned int ientry = 0; ientry < maxEntries; ientry++)
        {
            if ((ientry % 1000 == 0 && ientry < 10000) || (ientry % 10000 == 0))
                std::cout << "Processing event " << ientry << " / " << maxEntries << std::endl;
            run = runnumber;
            lumi = luminumber;
            event = eventnumber;
            bx = bxnumber;
            intree->GetEntry(ientry);

            nTotEvents++;
            nTracks = (*trackp).size();
            nTotTracks += (*trackp).size();
            nTotClusters += (*chargeoverpath).size();

        	unsigned int FirstAmplitude = 0;
            for (unsigned int i = 0; i < nSaturationLevels; i++)
                { nSaturatedClusters[i] = 0; }
            nSaturatedStrips.clear();
            subDetector.clear();
            std::vector<unsigned int> saturatedCharge_;
            saturatedCharge_.clear();
            saturatedCharge.clear();
            std::vector<unsigned int> saturatedChargeoverpath_;
            saturatedChargeoverpath_.clear();
            saturatedChargeoverpath.clear();
            std::vector<unsigned int> saturatedAmplitude_;
            saturatedAmplitude_.clear();
            saturatedAmplitude.clear();
            for (unsigned int i = 0; i < nSaturationLevels; i++)
            {
                saturatedCharge.push_back(saturatedCharge_); 
                saturatedChargeoverpath.push_back(saturatedChargeoverpath_); 
                saturatedAmplitude.push_back(saturatedAmplitude_); 
            }
            for (unsigned int icluster = 0; icluster < (*chargeoverpath).size(); icluster++)
            { // Loop over clusters
// Keep all clusters (for now)
//                if (!(*saturation)[icluster]) continue;
                
                FirstAmplitude += (*nstrips)[icluster];
                const SiStripDetId sistripdetid = SiStripDetId( (*rawid)[icluster] );
                unsigned int subDetector_ = sistripdetid.subDetector(); // returns: TIB:3 TID:4 TOB:5 TEC:6
                unsigned int nSaturatedStrips_ = 0;
// Except if they are not SiStrip clusters
                if (subDetector_ < 3) { continue; }
                for (unsigned int s = 0; s < (*nstrips)[icluster]; s++)
                {
                    int StripCharge =  (*amplitude)[FirstAmplitude - (*nstrips)[icluster] + s];
                    if (StripCharge > 1023)
                    { // Should be useless
                        nSaturatedStrips_++;
                        saturatedCharge_.push_back((*charge)[FirstAmplitude - (*nstrips)[icluster] + s]);
                        saturatedChargeoverpath_.push_back((*chargeoverpath)[FirstAmplitude - (*nstrips)[icluster] + s]);
                        saturatedAmplitude_.push_back((*amplitude)[FirstAmplitude - (*nstrips)[icluster] + s]);
                    }
                    else if (StripCharge > 253)
                    {
                        nSaturatedStrips_++;
                        saturatedCharge_.push_back((*charge)[FirstAmplitude - (*nstrips)[icluster] + s]);
                        saturatedChargeoverpath_.push_back((*chargeoverpath)[FirstAmplitude - (*nstrips)[icluster] + s]);
                        saturatedAmplitude_.push_back((*amplitude)[FirstAmplitude - (*nstrips)[icluster] + s]);
                    }
                }
                nSaturatedStrips.push_back(nSaturatedStrips_);
                subDetector.push_back(subDetector_);
                for (unsigned int i = 0; i < nSaturationLevels; i++)
                {
                    if (nSaturatedStrips_ >= i)
                    {
                        nSaturatedClusters[i]++;
                        saturatedCharge[i] = saturatedCharge_;
                        saturatedChargeoverpath[i] = saturatedChargeoverpath_;
                        saturatedAmplitude[i] = saturatedAmplitude_;
                    }
                }

            }// End of loop over clusters
            for (unsigned int i = 0; i < nSaturationLevels; i++)
            {
                if (nSaturatedClusters[i] > 0)
                    nEvents[i]++;
            }

        }printf("\n");// End of loop over events

    std::cout << "nEvents / nTotEvents= " << nEvents[0] << " / " << nTotEvents << "\tnTracks / nTotTracks= " << nTracks << " / " << nTotTracks << "\tnSaturatedClusters / nTotClusters= " << nSaturatedClusters[3] << " / " << nTotClusters << std::endl;   

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
