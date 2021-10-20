clear
clc
close all

subnum = 2;
load(['C:\Users\fzahedi1\OneDrive - Arizona State University\Projects\Adaptive\Bayesian Optimization\AP_BO_newsetup\DATA\2D+Ks\Subject',num2str(subnum),'\UsedKs.mat']);


figure
yyaxis left
plot(UsedKs(1,:),'LineWidth',1.25)
hold on
plot(UsedKs(1,:),'.','MarkerSize',10)
ylabel('k_{p}')
yyaxis right
plot(UsedKs(2,:),'LineWidth',1.25)
hold on
plot(UsedKs(2,:),'.','MarkerSize',10)
xlabel('iteration')
ylabel('k_{n}')