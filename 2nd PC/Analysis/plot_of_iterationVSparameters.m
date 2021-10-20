clc
clear
close all

subnum = 9;

load(['/home/fzahedi/Fatemeh/Adaptive/AP_BO_newsetup/DATA/Subject',num2str(subnum),'/Obfunc.mat']);
count = 25;%size(Objectivefunc,2);
Data = Objectivefunc(:,1:count);
load(['/home/fzahedi/Fatemeh/Adaptive/AP_BO_newsetup/DATA/Subject',num2str(subnum),'/UsedKs.mat']);

UsedKsn = UsedKs(:,1:count);


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

% yyaxis left
% plot(Blbcum,'LineWidth',1.25)
% hold on
% plot(Blbcum,'.','MarkerSize',10)
% ylabel('max b_{lb}')
% hold on
% yyaxis right
% plot(Bubcum,'LineWidth',1.25)
% hold on
% plot(Bubcum,'.','MarkerSize',10)
% ylabel('max b_{ub}')
% xlabel('iteration')
% 
% figure
% plot(cumulative,'LineWidth',1.25,'Color',[0 0.50 1])
% hold on
% plot(cumulative,'.','MarkerSize',10,'Color',[0 0.50 1])
% xlabel('iteration')
% ylabel('f(b_{lb}, b_{ub})')



% ML----------------------------------------------------------------

cumulative2 = cummax(Data(end,:));
index2 = find(Data(end,:)==cumulative2);

n = 1;
for i=1:length(Data(end,:))
    
    if i~=index2(n)
        if i < index2(length(index2))
            indexcum2(i) = index2(n-1);
        else
            indexcum2(i) = index2(n);
        end
    else
        indexcum2(i) = index2(n);
        if n < length(index2)
            n = n+1;
        end
    end
end

Blbcumml = Data(4,indexcum2);
Bubcumml = Data(5,indexcum2);


%% Plotting

figure
subplot(3,2,1)
plot(cumulative,'LineWidth',1.25,'Color',[0, 0.4470, 0.7410])
hold on
plot(cumulative,'.','MarkerSize',10,'Color',[0, 0.4470, 0.7410])
%xlabel('iteration')
subtitle('AP','FontWeight', 'bold');
xticks([]);
ylabel('f(b_{lb}, b_{ub})')

subplot(3,2,3)
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
%ylabel('max b_{ub}')
%xlabel('iteration')
xticks([]);

subplot(3,2,5)
yyaxis left
plot(UsedKsn(1,:),'LineWidth',1.25)
hold on
plot(UsedKsn(1,:),'.','MarkerSize',10)
ylabel('k_{p}')
yyaxis right
plot(UsedKsn(2,:),'LineWidth',1.25)
hold on
plot(UsedKsn(2,:),'.','MarkerSize',10)
xlabel('Iteration')
%ylabel('k_{n}')

%---------------
subplot(3,2,2)
plot(cumulative2,'LineWidth',1.25,'Color',[0, 0.4470, 0.7410])
hold on
plot(cumulative2,'.','MarkerSize',10,'Color',[0, 0.4470, 0.7410])
%xlabel('iteration')
subtitle('ML','FontWeight', 'bold');
xticks([]);
%ylabel('f(b_{lb}, b_{ub})')

subplot(3,2,4)
yyaxis left
plot(Blbcumml,'LineWidth',1.25)
hold on
plot(Blbcumml,'.','MarkerSize',10)
%ylabel('max b_{lb}')
hold on
yyaxis right
plot(Bubcumml,'LineWidth',1.25)
hold on
plot(Bubcumml,'.','MarkerSize',10)
ylabel('max b_{ub}')
%xlabel('iteration')
xticks([]);

subplot(3,2,6)
yyaxis left
plot(UsedKsn(3,:),'LineWidth',1.25)
hold on
plot(UsedKsn(3,:),'.','MarkerSize',10)
%ylabel('k_{p}')
yyaxis right
plot(UsedKsn(4,:),'LineWidth',1.25)
hold on
plot(UsedKsn(4,:),'.','MarkerSize',10)
xlabel('Iteration')
ylabel('k_{n}')

%%
parameters(1,1) = Blbcum(end);
parameters(2,1) = Bubcum(end);
parameters(3,1) = Blbcumml(end);
parameters(4,1) = Bubcumml(end);
parameters(5,1) = UsedKsn(1,end);
parameters(6,1) = UsedKsn(2,end);
parameters(7,1) = UsedKsn(3,end);
parameters(8,1) = UsedKsn(4,end);

save(['/home/fzahedi/Fatemeh/Adaptive/AP_BO_newsetup/DATA/Subject',num2str(subnum),'/plots/parameters.mat'],'parameters');

