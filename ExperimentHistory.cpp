/*
    Plots for experiment history
    In the file the lines should be: name, year, sensitivity(or something else)
    Then you choose marker style and colors
    Everything else should be automatic
*/

#include <stdlib.h>
#include "TFile.h"
#include "TTree.h"
#include "TNtuple.h"
#include "TChain.h"
#include "TStyle.h"
#include "THStack.h"
#include "TH1.h"
#include "TH2.h"
#include <TMath.h>
#include "TString.h"
#include <TStyle.h>

/*
    Choose name of the txt
*/
string File_name = "exp_history.txt";

/*
    Choose marker styles and colors, these are applied in the order of the file.
    Plus the marker size
*/
int my_styles[] = {20, 21, 22, 23, 20, 21, 22, 23, 20, 21, 22, 23, 20, 21, 22, 23, 20, 21, 22, 23};
int my_colors[] = {30, 40, 31, 41, 32, 42, 33, 43, 34, 44, 35, 45, 36, 46, 37, 47, 38, 48, 39, 49};
double MarkerSize = 1.5;

/*
--------------------------------------------------------------------------------------
------------------ From here on everything should be automatic -----------------------
--------------------------------------------------------------------------------------
*/

std::vector<string> txt_v;              // names
std::vector<string> txt_v_NoDoppioni;   // names but removing doubles
std::vector<int> date_v;                // year
std::vector<float> num_v;               // your variable


// funcion to create the legend for a vector of TGraph
void fai_legenda(TLegend *legendina, std::vector<TGraph *> g_v){
    for(int i=0; i<g_v.size();i++){
        legendina->AddEntry(g_v[i],txt_v_NoDoppioni[i].c_str(),"p");    
    }
}

int main()
{
    // opens the file
    ifstream indata;
    indata.open(File_name);

    // error if the file doesnt exist
    if(!indata) {
       cerr << "Error: file could not be opened" << std::endl;
       exit(1);
    }

    int i = 0;
    string read;
    
    // read each line in the file and separate the info
    while (getline(indata, read))
    {
        string txt_tmp;
        int date_tmp;
        float num_tmp;

        switch(i%3+1){
            case 1:
                txt_tmp=read;
                txt_v.push_back(txt_tmp);
                break;
            case 2:
                date_tmp =std::stoi(read);
                date_v.push_back(date_tmp);
                break;
            case 3:
                num_tmp =std::stof(read);
                num_v.push_back(num_tmp);
                break;
        }
        i++;
    }

    for(int i=0; i< txt_v.size(); i++){
        std::cout<<txt_v[i]<<" "<<num_v[i]<<" "<<date_v[i]<<std::endl;
    }
    
    std::vector<TGraph*> g_v;
    
    for(int j =0; j<txt_v.size() ;j++){
        int k = -1;
        for(int i=0; i<j; i++){
            std::cout<<i<<" "<<j<<std::endl;
            if(txt_v[i]==txt_v[j]) {k=i; break;}
        }
        std::cout<<k<<std::endl;
        
        if(k==-1) {
            TGraph * g_tmp= new TGraph;
            g_tmp->SetPoint(0, date_v[j], num_v[j]);
            g_v.push_back(g_tmp);
            txt_v_NoDoppioni.push_back(txt_v[j]);
        }
        else{
            g_v[k]->SetPoint(g_v[k]->GetN(), date_v[j], num_v[j]);
        }
        
    }


    int style_i = 0;

    TLegend * leg = new TLegend(0.83,0.3,0.98,0.7);

    auto mg = new TMultiGraph;
    mg->SetTitle("title;xaxis title; yaxis title");
    for(int i=0; i< g_v.size(); i++){
        g_v[i]->SetMarkerStyle(my_styles[style_i]);
        g_v[i]->SetMarkerColor(my_colors[style_i]);
        g_v[i]->SetMarkerSize(MarkerSize);
        style_i ++;

        mg->Add(g_v[i]);
    }

    fai_legenda(leg,g_v);

    new TCanvas;
    mg->Draw("AP");
    leg->DrawClone("Same");

    indata.close();
    std::cout << "End-of-file reached.." << std::endl;
    return 0;
}
