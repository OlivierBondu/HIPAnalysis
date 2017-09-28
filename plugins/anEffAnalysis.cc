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
#include "TF1.h"
#include "TGraphAsymmErrors.h"

// RooFit includes
#include "RooPlot.h"
#include "RooRealVar.h"
#include "RooDataHist.h"
#include "RooAddPdf.h"
#include "RooGaussian.h"
#include "RooLandau.h"
#include "RooFFTConvPdf.h"
#include "RooFitResult.h"

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

TF1 * f2 = NULL;
TF1 * f3 = NULL;

class anEffAnalysis : public edm::EDAnalyzer {
    public:
        explicit anEffAnalysis(const edm::ParameterSet&);
        ~anEffAnalysis();

        static void fillDescriptions(edm::ConfigurationDescriptions& descriptions);


    private:
        virtual void beginJob() override;
        virtual void analyze(const edm::Event&, const edm::EventSetup&) override;
        virtual void endJob() override;
        std::string histname(int run, std::string layer, std::string bx);
        unsigned int checkLayer( unsigned int iidd, const TrackerTopology* tTopo);
        static Double_t function_sum(Double_t *x, Double_t *par);
        void fitAll();
        std::pair<unsigned int, unsigned int> getBx(std::string bx);

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
        std::vector<std::string> m_Vbxs_th1;
        std::vector<std::string> m_Vbxs_th2;
        std::string m_filter_exp;
        bool m_perform_fit;
        bool m_verbose_fit;
        // Internal things
        std::unordered_set<int> m_Sruns;
        std::unordered_set<std::string> m_Slayers;
        std::unordered_set<std::string> m_Sbxs_th1;
        std::unordered_set<std::string> m_Sbxs_th2;
        // Utilities
        typedef std::chrono::system_clock clock;
        typedef std::chrono::milliseconds ms;
        typedef std::chrono::seconds seconds;
        clock::time_point m_start_time;
        // Histograms
        std::map<std::string, TH1F*> map_h_ClusterStoN;
        std::map<std::string, TH2F*> map_h_ClusterStoN_vs_bx;
        std::map<std::string, TGraphAsymmErrors*> map_h_ClusterStoN_vs_bx_fit_lxg;
        std::map<std::string, TGraphAsymmErrors*> map_h_ClusterStoN_vs_bx_fit_lpg;
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
m_Vbxs_th1(iConfig.getUntrackedParameter<std::vector<std::string>>("bxs_th1")),
m_Vbxs_th2(iConfig.getUntrackedParameter<std::vector<std::string>>("bxs_th2")),
m_filter_exp(iConfig.getParameter<std::string>("filter_exp")),
m_perform_fit(iConfig.getParameter<bool>("perform_fit")),
m_verbose_fit(iConfig.getParameter<bool>("verbose_fit"))
{
   //now do what ever initialization is needed
    m_output.reset(TFile::Open(m_output_filename.c_str(), "recreate"));
    std::copy(m_Vruns.begin(), m_Vruns.end(), std::inserter(m_Sruns, m_Sruns.end()));
    std::copy(m_Vlayers.begin(), m_Vlayers.end(), std::inserter(m_Slayers, m_Slayers.end()));
    std::copy(m_Vbxs_th1.begin(), m_Vbxs_th1.end(), std::inserter(m_Sbxs_th1, m_Sbxs_th1.end()));
    std::copy(m_Vbxs_th2.begin(), m_Vbxs_th2.end(), std::inserter(m_Sbxs_th2, m_Sbxs_th2.end()));
}


anEffAnalysis::~anEffAnalysis()
{
   // do anything here that needs to be done at desctruction time
   // (e.g. close files, deallocate resources etc.)
    for (auto it = map_h_ClusterStoN.begin() ; it != map_h_ClusterStoN.end() ; it++)
        delete (*it).second;
    for (auto it = map_h_ClusterStoN_vs_bx.begin() ; it != map_h_ClusterStoN_vs_bx.end() ; it++)
        delete (*it).second;
    for (auto it = map_h_ClusterStoN_vs_bx_fit_lxg.begin() ; it != map_h_ClusterStoN_vs_bx_fit_lxg.end() ; it++)
        delete (*it).second;
    for (auto it = map_h_ClusterStoN_vs_bx_fit_lpg.begin() ; it != map_h_ClusterStoN_vs_bx_fit_lpg.end() ; it++)
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

std::string anEffAnalysis::histname(int run, std::string layer, std::string bx) {
    return std::to_string(run) + '_' + (layer) + "_bxs_" + (bx);
}

std::pair<unsigned int, unsigned int> anEffAnalysis::getBx(std::string bx) {
    std::vector<std::string> tmp = anEffAnalysisTool::split(bx, '-');
    unsigned int bxlow = std::stoi(tmp[0]);
    unsigned int bxhigh = std::stoi(tmp[1]);
    return std::pair<unsigned int, unsigned int>(bxlow, bxhigh);
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
                std::cout << "## TH1 histogram filling ##" << std::endl;
                for (auto it_bxs = m_Sbxs_th1.begin() ; it_bxs != m_Sbxs_th1.end() ; it_bxs++)
                {
                    TCanvas *c1 = new TCanvas();
                    std::string h_name = histname(*it_runs, *it_layers, *it_bxs); 
                    unsigned int bxlow = getBx(*it_bxs).first;
                    unsigned int bxhig = getBx(*it_bxs).second;
                    std::cout << "Filling histograms for " << h_name << std::endl;
                    // ClusterStoN is the S / N NOT corrected for the track angle
                    // we need to correct it by cosRZ = pz / p
                    // (see 
                    // unfortunately the local pz is not stored
                    // fortunately, we have and px = pz * locDxDz and TrajLocAngleX = atan(locDxDz)
                    // so we have cosRZ = 1 / sqrt(1 + pow(tan(TrajLocAngleX), 2) + pow(tan(TrajLocAngleY), 2))
                    intree->Draw(("(ClusterStoN / sqrt(1 + pow(tan(TrajLocAngleX), 2) + pow(tan(TrajLocAngleY), 2)))>>h_ClusterStoN_" + h_name + "(2000, 0, 2000)").c_str(), (m_filter_exp + "&& (" + std::to_string(bxlow) + " <= bunchx && bunchx <= " + std::to_string(bxhig) + ")").c_str(), "");
                    TH1F *h = (TH1F*)c1->GetPrimitive(("h_ClusterStoN_" + h_name).c_str());
                    map_h_ClusterStoN[h_name]->Add(h);
                    delete h;
                    delete c1;
                } // end of loop over th1 bx list
                std::cout << "## TH2 histogram filling ##" << std::endl;
                for (auto it_bxs = m_Sbxs_th2.begin() ; it_bxs != m_Sbxs_th2.end() ; it_bxs++)
                {
                    TCanvas *c1 = new TCanvas();
                    std::string h_name = histname(*it_runs, *it_layers, *it_bxs); 
                    unsigned int bxlow = getBx(*it_bxs).first;
                    unsigned int bxhig = getBx(*it_bxs).second;
                    std::cout << "Filling histograms for " << h_name << std::endl;
                    intree->Draw("(ClusterStoN / sqrt(1 + pow(tan(TrajLocAngleX), 2) + pow(tan(TrajLocAngleY), 2))):bunchx>>h3(3600, 0, 3600, 2000, 0, 2000)", (m_filter_exp + "&& (" + std::to_string(bxlow) + " <= bunchx && bunchx <= " + std::to_string(bxhig) + ")").c_str(), "colz");
                    map_h_ClusterStoN_vs_bx[h_name]->Add((TH2F*)(c1->GetPrimitive("h3")));
                    // necessary because of the weird way the graph is translated into a TH2F automatically by root
                    map_h_ClusterStoN_vs_bx[h_name]->SetName(("h_ClusterStoN_vs_bx_" + h_name).c_str());
                    map_h_ClusterStoN_vs_bx[h_name]->SetTitle(("h_ClusterStoN_vs_bx_" + h_name).c_str());
                    delete c1;
                } // end of loop over th2 bx list
            } // end of loop over layers
        } // end of loop over runs
        infile = 0;
        intree = 0;
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
            std::cout << "## Creating TH1 histograms ##" << std::endl;
            for (auto it_bxs = m_Sbxs_th1.begin() ; it_bxs != m_Sbxs_th1.end() ; it_bxs++)
            {
                std::string h_name = histname(*it_runs, *it_layers, *it_bxs);
                std::cout << "Will create histograms corresponding to " << h_name << std::endl;
                map_h_ClusterStoN[h_name] = new TH1F(("h_ClusterStoN_" + h_name).c_str(), ("h_ClusterStoN_" + h_name).c_str(), 2000, 0, 2000);
            } // end of loop over th1 bx intervals
            std::cout << "## Creating TH2 histograms ##" << std::endl;
            for (auto it_bxs = m_Sbxs_th2.begin() ; it_bxs != m_Sbxs_th2.end() ; it_bxs++)
            {
                std::string h_name = histname(*it_runs, *it_layers, *it_bxs);
                std::cout << "Will create histograms corresponding to " << h_name << std::endl;
                map_h_ClusterStoN_vs_bx[h_name] = new TH2F(("h_ClusterStoN_vs_bx_" + h_name).c_str(), ("h_ClusterStoN_vs_bx_" + h_name).c_str(), 3600, 0, 3600, 2000, 0, 2000);
                map_h_ClusterStoN_vs_bx_fit_lxg[h_name] = new TGraphAsymmErrors();
                map_h_ClusterStoN_vs_bx_fit_lxg[h_name]->SetName(("h_ClusterStoN_vs_bx_fit_lxg_" + h_name).c_str());
                map_h_ClusterStoN_vs_bx_fit_lxg[h_name]->SetTitle(("h_ClusterStoN_vs_bx_fit_lxg_" + h_name).c_str());
                map_h_ClusterStoN_vs_bx_fit_lpg[h_name] = new TGraphAsymmErrors();
                map_h_ClusterStoN_vs_bx_fit_lpg[h_name]->SetName(("h_ClusterStoN_vs_bx_fit_lpg_" + h_name).c_str());
                map_h_ClusterStoN_vs_bx_fit_lpg[h_name]->SetTitle(("h_ClusterStoN_vs_bx_fit_lpg_" + h_name).c_str());
            } // end of loop over th2 bx intervals
        } // end of loop over layers
    } // end of loop over runs

}

Double_t anEffAnalysis::function_sum(Double_t *x, Double_t *par) {
    const Double_t xx =x[0];
    return (1 - par[0]) * f2->Eval(xx) / par[1] + (par[0]) * f3->Eval(xx) / par[2];
    //return (par[0]) * f2->Eval(xx) + (1 - par[0]) * f3->Eval(xx);
}

void anEffAnalysis::fitAll()
{
    std::cout << "## Fitting TH1 histograms ##" << std::endl;
    if (!m_verbose_fit) {
        RooMsgService::instance().setGlobalKillBelow(RooFit::FATAL);
    }
    TCanvas *c1 = new TCanvas();
    for (auto it_runs = m_Sruns.begin() ; it_runs != m_Sruns.end() ; it_runs++)
    {
        for (auto it_layers = m_Slayers.begin() ; it_layers != m_Slayers.end() ; it_layers++)
        {
            for (auto it_bxs = m_Sbxs_th1.begin() ; it_bxs != m_Sbxs_th1.end() ; it_bxs++)
            {
                // Define common things for the different fits
                std::string h_name = histname(*it_runs, *it_layers, *it_bxs);
                c1->Clear();
                Double_t xmin = 0;
                Double_t xmax = 100;
                RooRealVar StoN("StoN", "S / N", xmin, xmax);
                RooPlot* frame = StoN.frame();
                RooDataHist datahist("datahist", "datahist", StoN, RooFit::Import(*map_h_ClusterStoN[h_name]));
                datahist.plotOn(frame);

                // Try Landau convolved with a gaussian
//                RooRealVar meanG("meanG", "meanG", 0);
                RooRealVar sigmaG("sigmaG", "sigmaG", 1, 0.1, 20);
                RooRealVar meanL("meanL", "meanL", 30, 10, 50);
                RooRealVar sigmaL("sigmaL", "sigmaL", 0.1, 100);
                RooGaussian gaussian("gaussian", "gaussian", StoN, meanL, sigmaG);
                RooLandau landau("landau", "landau", StoN, meanL, sigmaL);
                // Set #bins to be used for FFT sampling to 10000
                StoN.setBins(10000, "cache");
                RooFFTConvPdf model("model", "landau (X) gauss", StoN, landau, gaussian) ;
                RooFitResult* r = 0;
                if (m_verbose_fit) {
                    r = model.fitTo(datahist, RooFit::Save());
                } else {
                    r = model.fitTo(datahist, RooFit::PrintLevel(-1), RooFit::Save());
                }
                model.plotOn(frame, RooFit::LineColor(kBlue));
                // Get the maxima
                // lxg == landau (X) gauss
                TF1 *lxg = model.asTF(RooArgList(StoN));
                Double_t xmax_lxg = lxg->GetMaximumX();
                Double_t ymax_lxg = lxg->GetMaximum();
                Double_t x1_lxg = lxg->GetX(ymax_lxg / 2., xmin, xmax_lxg);
                Double_t x2_lxg = lxg->GetX(ymax_lxg / 2., xmax_lxg, xmax);
                if (HIPDEBUG) {
                    std::cout << "From TF1, maximum at (x, y) = (" << xmax_lxg << " , " << ymax_lxg << ")" << std::endl;
                    std::cout << "From TF1, FWHM at (x1, x2) = (" << x1_lxg << " , " << x2_lxg << ")" << std::endl;
                }
                // Now let's get some uncertainty on xmax
                TH1F h_xmax("h_xmax", "h_xmax", 5000, 0, 50);
                int ntoys = 500;
                RooArgSet* model_params = model.getParameters(RooArgList(StoN));
                model_params->writeToStream(std::cout, true);
                for (int i = 0 ; i < ntoys ; i++) {
                    // get a randomized set of parameters for the model from the fit results
                    RooArgList randomizedParams = r->randomizePars();
                    *model_params = randomizedParams;
                    TF1 *lxg_toy = model.asTF(RooArgList(StoN));
                    h_xmax.Fill(lxg_toy->GetMaximumX());
                    lxg_toy = 0;
                }
                r = 0;
                

                // Try landau + a gaussian
                RooRealVar meanG2("meanG2", "meanG2", 30, 10, 50);
                RooRealVar sigmaG2("sigmaG2", "sigmaG2", 1, 1, 50);
                RooRealVar meanL2("meanL2", "meanL2", 30, 10, 50);
                RooRealVar sigmaL2("sigmaL2", "sigmaL2", 0.1, 100);
                RooGaussian gaussian2("gaussian2", "gaussian2", StoN, meanG2, sigmaG2);
                RooLandau landau2("landau2", "landau2", StoN, meanL2, sigmaL2);
                RooRealVar x("x", "x", 0.1, 0, 0.4);
                RooAddPdf model2("model2", "model2", gaussian2, landau2, x);
                if (m_verbose_fit) {
                    r = model2.fitTo(datahist, RooFit::Save());
                } else {
                    r = model2.fitTo(datahist, RooFit::PrintLevel(-1), RooFit::Save());
                }
                model2.plotOn(frame, RooFit::LineColor(kRed));
                // Get the maxima
                // lpg == landau + gauss
                f2 = landau2.asTF(RooArgList(StoN));
                f3 = gaussian2.asTF(RooArgList(StoN));
                TF1 *lpg = new TF1("Sum", function_sum, 0, 100, 3);
                lpg->SetParameter(0, x.getVal());
                lpg->SetParameter(1, f2->Integral(0, 100));
                lpg->SetParameter(2, f3->Integral(0, 100));
                Double_t xmax_lpg = lpg->GetMaximumX();
                Double_t ymax_lpg = lpg->GetMaximum();
                Double_t x1_lpg = lpg->GetX(ymax_lpg / 2., xmin, xmax_lpg);
                Double_t x2_lpg = lpg->GetX(ymax_lpg / 2., xmax_lpg, xmax);
                if (HIPDEBUG) {
                    std::cout << "From TF1, maximum at (x, y) = (" << xmax_lpg << " , " << ymax_lpg << ")" << std::endl;
                    std::cout << "From TF1, FWHM at (x1, x2) = (" << x1_lpg << " , " << x2_lpg << ")" << std::endl;
                }
                // Now let's get some uncertainty on xmax
                TH1F h_xmax2("h_xmax2", "h_xmax2", 5000, 0, 50);
                RooArgSet* model2_params = model2.getParameters(RooArgList(StoN));
                model2_params->writeToStream(std::cout, true);
                for (int i = 0 ; i < ntoys ; i++) {
                    // get a randomized set of parameters for the model from the fit results
                    RooArgList randomizedParams2 = r->randomizePars();
                    *model2_params = randomizedParams2;
                    TF1 *lpg_toy = model2.asTF(RooArgList(StoN));
                    h_xmax2.Fill(lpg_toy->GetMaximumX());
                    lpg_toy = 0;
                }
                r = 0;

                // Redraw data on top and print / store everything
                datahist.plotOn(frame);
                unsigned int bxlow = getBx(*it_bxs).first;
                unsigned int bxhig = getBx(*it_bxs).second;
                for (auto it_bxs_th2 = m_Sbxs_th2.begin() ; it_bxs_th2 != m_Sbxs_th2.end() ; it_bxs_th2++)
                {
                    unsigned int bxlow_th2 = getBx(*it_bxs_th2).first;
                    unsigned int bxhig_th2 = getBx(*it_bxs_th2).second;
                    if ((bxlow < bxlow_th2) || (bxhig > bxhig_th2))
                        continue;
                    std::string h_name_th2 = histname(*it_runs, *it_layers, *it_bxs_th2);
                    float bxmean = (bxhig - bxlow) / 2. + bxlow;
                    unsigned int n = map_h_ClusterStoN_vs_bx_fit_lxg[h_name_th2]->GetN();
//  y: maximum of the fitted function
// dy: FWHM
//                    map_h_ClusterStoN_vs_bx_fit_lxg[h_name_th2]->SetPoint(n, bxmean, xmax_lxg);
//                    map_h_ClusterStoN_vs_bx_fit_lxg[h_name_th2]->SetPointError(n, bxmean - bxlow, bxhig - bxmean, xmax_lxg - x1_lxg, x2_lxg - xmax_lxg);
//                    map_h_ClusterStoN_vs_bx_fit_lpg[h_name_th2]->SetPoint(n, bxmean, xmax_lpg);
//                    map_h_ClusterStoN_vs_bx_fit_lpg[h_name_th2]->SetPointError(n, bxmean - bxlow, bxhig - bxmean, xmax_lpg - x1_lpg, x2_lpg - xmax_lpg);
//  y: maximum of the fitted function
// dy: uncertainty on y from toy TF1 from random function parameters taken from the fit results
                    map_h_ClusterStoN_vs_bx_fit_lxg[h_name_th2]->SetPoint(n, bxmean, xmax_lxg);
                    map_h_ClusterStoN_vs_bx_fit_lxg[h_name_th2]->SetPointError(n, bxmean - bxlow, bxhig - bxmean, h_xmax.GetRMS() / 2., h_xmax.GetRMS() / 2.);
                    map_h_ClusterStoN_vs_bx_fit_lpg[h_name_th2]->SetPoint(n, bxmean, xmax_lpg);
                    map_h_ClusterStoN_vs_bx_fit_lpg[h_name_th2]->SetPointError(n, bxmean - bxlow, bxhig - bxmean, h_xmax2.GetRMS() / 2., h_xmax2.GetRMS() / 2.);
                    frame->SetName(("frame_" + h_name).c_str());
                    frame->SetTitle(("frame_" + h_name).c_str());
                    frame->Draw();
                    m_output->cd();
                    frame->Write();
                    if (HIPDEBUG) {
                        c1->Print("anEff_fit_debug.pdf");
                    }
//                    c1->SetName(("canvas_" + h_name).c_str());
//                    c1->SetTitle(("canvas_" + h_name).c_str());
//                    c1->Write();
                } // end of loop over th2 bx intervals
                delete lxg;
                delete lpg;
            } // end of loop over th1 bx intervals
        } // end of loop over layers
    } // end of loop over runs
    delete c1;
}

// ------------ method called once each job just after ending the event loop  ------------
void 
anEffAnalysis::endJob() 
{
    auto histo_time = clock::now();
    std::cout << std::endl << "Histos done in " << std::chrono::duration_cast<ms>(histo_time - m_start_time).count() / 1000. << "s" << std::endl;
    if (m_perform_fit) {
        fitAll();
        auto fit_time = clock::now();
        std::cout << std::endl << "Fits done in " << std::chrono::duration_cast<ms>(fit_time - histo_time).count() / 1000. << "s" << std::endl;
    }

    auto end_time = clock::now();
    std::cout << std::endl << "Job done in " << std::chrono::duration_cast<ms>(end_time - m_start_time).count() / 1000. << "s" << std::endl;
    m_output->cd();
    for (auto it = map_h_ClusterStoN.begin() ; it != map_h_ClusterStoN.end() ; it++) {
        std::cout << "#entries in " << it->second->GetName() << "= " << it->second->GetEntries() << std::endl;
        it->second->Write();
    }
    for (auto it = map_h_ClusterStoN_vs_bx.begin() ; it != map_h_ClusterStoN_vs_bx.end() ; it++) {
        std::cout << "#entries in " << it->second->GetName() << "= " << it->second->GetEntries() << std::endl;
        it->second->Write();
    }
    for (auto it = map_h_ClusterStoN_vs_bx_fit_lxg.begin() ; it != map_h_ClusterStoN_vs_bx_fit_lxg.end() ; it++) {
        std::cout << "#entries in " << it->second->GetName() << "= " << it->second->GetN() << std::endl;
        if (HIPDEBUG) {
            for (int i = 0 ; i < it->second->GetN() ; i++) {
                std::cout  
                    << "\t" << it->second->GetErrorXlow(i)
                    << "\t" << it->second->GetErrorXhigh(i)
                    << "\t" << it->second->GetErrorYlow(i)
                    << "\t" << it->second->GetErrorYhigh(i)
                    << std::endl;
            }
        }
        it->second->Write();
    }
    for (auto it = map_h_ClusterStoN_vs_bx_fit_lpg.begin() ; it != map_h_ClusterStoN_vs_bx_fit_lpg.end() ; it++) {
        std::cout << "#entries in " << it->second->GetName() << "= " << it->second->GetN() << std::endl;
        it->second->Write();
    }
    m_output->Write();
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
