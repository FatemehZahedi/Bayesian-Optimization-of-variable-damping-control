clc
clear
close all

n = 1;
for subject=5:9
    
    load(['C:\Users\Fatem\OneDrive - Arizona State University\Projects\Adaptive\Bayesian Optimization\AP_BO_newsetup\DATA\4D\DATA\Subject',num2str(subject),'\plots\Subject',num2str(subject),'.mat']);
    load(['C:\Users\Fatem\OneDrive - Arizona State University\Projects\Adaptive\Bayesian Optimization\AP_BO_newsetup\DATA\4D\DATA\Subject',num2str(subject),'\plots\parameters.mat']);
    
    ALLmeasures(:,:,:,n) = Avemeasures;
    Averagemeasures(:,:,:,n) = Average;
    Minimummeasures(:,:,:,n) = minmeasures;
    
    GPpercentageImprov(n,1:2) = round(percentageImproveave(1:2),2);
    GPpercentageImprov(n,3) = round(percentageImproveave(12),2);
    GPpercentageImprov(n,4) = round(percentageImproveave(4),2);
    GPpercentageImprov(n,5:8) = round(percentageImproveave(5:8),2);
    GPpercentageImprov(n,9) = round(mean(percentageImproveave([12 4 5 6 7 8])),2);
    GPpercentageImprov(n,10) = round(percentageImproveave(11),2);
    GPpercentageImprov(n,11) = round(percentageImproveave(3),2);
    
    GPpercentageImprov2(n,1:2) = round(percentageImprovemin(1:2),2);
    GPpercentageImprov2(n,3) = round(percentageImprovemin(12),2);
    GPpercentageImprov2(n,4) = round(percentageImprovemin(4),2);
    GPpercentageImprov2(n,5:8) = round(percentageImprovemin(5:8),2);
    GPpercentageImprov2(n,9) = round(mean(percentageImprovemin([12 4 5 6 7 8])),2);
    GPpercentageImprov2(n,10) = round(percentageImprovemin(11),2);
    GPpercentageImprov2(n,11) = round(percentageImprovemin(3),2);
    
    Measures(n,1:2,1) = Average(1,1:2,1);
    Measures(n,1:2,2) = Average(2,1:2,1);
    Measures(n,3,1) = Average(1,12,1);
    Measures(n,3,2) = Average(2,12,1);
    Measures(n,4:8,1) = Average(1,4:8,1);
    Measures(n,4:8,2) = Average(2,4:8,1);
    Measures(n,9,1) = Average(1,11,1);
    Measures(n,9,2) = Average(2,11,1);
    Measures(n,10,1) = Average(1,3,1);
    Measures(n,10,2) = Average(2,3,1);
    
    Optimizedparameter(n,:) = parameters';
    
    n=n+1;
    
    
end

GPpercentageImprov(6,:) = mean(GPpercentageImprov);
GPpercentageImprov(7,:) = std(GPpercentageImprov);
Optimizedparameter(6,:) = mean(Optimizedparameter);
Optimizedparameter(7,:) = std(Optimizedparameter);

Optimizedparameterr = round(Optimizedparameter,1);

%%
% Statistical Analysis

Selectedmeasures = Measures(:,3:9,:);



for i=1:size(Selectedmeasures,2)
    
    p(i) = signrank(Selectedmeasures(:,i,1),Selectedmeasures(:,i,2));
    
    [~,pt(i)] = ttest(Selectedmeasures(:,i,1),Selectedmeasures(:,i,2));
end
