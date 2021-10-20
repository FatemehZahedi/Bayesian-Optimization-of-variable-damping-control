clc
clear
close all

subnum = 2;
load(['C:\Users\fzahedi1\OneDrive - Arizona State University\Projects\Adaptive\Bayesian Optimization\AP_BO_newsetup\DATA\2D+Ks\Subject',num2str(subnum),'\Obfunc.mat']);
Data = Objectivefunc;
load(['C:\Users\fzahedi1\OneDrive - Arizona State University\Projects\Adaptive\Bayesian Optimization\AP_BO_newsetup\DATA\2D+Ks\Subject',num2str(subnum),'\UsedKs.mat']);


cumulative = cummax(Data(1,:));
index = find(Data(1,:)==cumulative);

n = 1;
for i=1:length(Data(1,:))
    
    if i~=index(n)
        if i < index(length(index))
            indexcum(i) = index(n-1);
        else
            indexcum(i) = index(n);
        end
    else
        indexcum(i) = index(n);
        if n < length(index)
            n = n+1;
        end
    end
end

Blbcum = Data(2,indexcum);
Bubcum = Data(3,indexcum);

yyaxis left
plot(Blbcum,'LineWidth',1.25)
hold on
plot(Blbcum,'.','MarkerSize',10)
ylabel('max b_{lb}')
hold on
yyaxis right
plot(Bubcum,'LineWidth',1.25)
hold on
plot(Bubcum,'.','MarkerSize',10)
ylabel('max b_{ub}')
xlabel('iteration')

figure
plot(cumulative,'LineWidth',1.25,'Color',[0 0.50 1])
hold on
plot(cumulative,'.','MarkerSize',10,'Color',[0 0.50 1])
xlabel('iteration')
ylabel('f(b_{lb}, b_{ub})')

figure
subplot(3,1,1)
plot(cumulative,'LineWidth',1.25,'Color',[0, 0.4470, 0.7410])
hold on
plot(cumulative,'.','MarkerSize',10,'Color',[0, 0.4470, 0.7410])
%xlabel('iteration')
xticks([]);
ylabel('f(b_{lb}, b_{ub})')

subplot(3,1,2)
yyaxis left
plot(Blbcum,'LineWidth',1.25)
hold on
plot(Blbcum,'.','MarkerSize',10)
ylabel('max b_{lb}')
hold on
yyaxis right
plot(Bubcum,'LineWidth',1.25)
hold on
plot(Bubcum,'.','MarkerSize',10)
ylabel('max b_{ub}')
%xlabel('iteration')
xticks([]);

subplot(3,1,3)
yyaxis left
plot(UsedKs(1,:),'LineWidth',1.25)
hold on
plot(UsedKs(1,:),'.','MarkerSize',10)
ylabel('k_{p}')
yyaxis right
plot(UsedKs(2,:),'LineWidth',1.25)
hold on
plot(UsedKs(2,:),'.','MarkerSize',10)
xlabel('Iteration')
ylabel('k_{n}')

