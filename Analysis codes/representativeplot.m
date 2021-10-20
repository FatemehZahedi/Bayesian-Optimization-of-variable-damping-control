% representative plots

clear
clc
close all
subnum = 6;
load(['C:\Users\Fatem\OneDrive - Arizona State University\Projects\Adaptive\Bayesian Optimization\AP_BO_newsetup\DATA\4D\DATA\Subject',num2str(subnum),'\plots\Obfunc.mat']);
load(['C:\Users\Fatem\OneDrive - Arizona State University\Projects\Adaptive\Bayesian Optimization\AP_BO_newsetup\DATA\4D\DATA\Subject',num2str(subnum),'\plots\bigmu.mat']);
load(['C:\Users\Fatem\OneDrive - Arizona State University\Projects\Adaptive\Bayesian Optimization\AP_BO_newsetup\DATA\4D\DATA\Subject',num2str(subnum),'\plots\gx.mat']);
load(['C:\Users\Fatem\OneDrive - Arizona State University\Projects\Adaptive\Bayesian Optimization\AP_BO_newsetup\DATA\4D\DATA\Subject',num2str(subnum),'\plots\gy.mat']);
load(['C:\Users\Fatem\OneDrive - Arizona State University\Projects\Adaptive\Bayesian Optimization\AP_BO_newsetup\DATA\4D\DATA\Subject',num2str(subnum),'\plots\bigquants.mat']);
load(['C:\Users\Fatem\OneDrive - Arizona State University\Projects\Adaptive\Bayesian Optimization\AP_BO_newsetup\DATA\4D\DATA\Subject',num2str(subnum),'\plots\bigei.mat']);

%ML
load(['C:\Users\Fatem\OneDrive - Arizona State University\Projects\Adaptive\Bayesian Optimization\AP_BO_newsetup\DATA\4D\DATA\Subject',num2str(subnum),'\plots\bigmuml.mat']);
load(['C:\Users\Fatem\OneDrive - Arizona State University\Projects\Adaptive\Bayesian Optimization\AP_BO_newsetup\DATA\4D\DATA\Subject',num2str(subnum),'\plots\gxml.mat']);
load(['C:\Users\Fatem\OneDrive - Arizona State University\Projects\Adaptive\Bayesian Optimization\AP_BO_newsetup\DATA\4D\DATA\Subject',num2str(subnum),'\plots\gyml.mat']);
load(['C:\Users\Fatem\OneDrive - Arizona State University\Projects\Adaptive\Bayesian Optimization\AP_BO_newsetup\DATA\4D\DATA\Subject',num2str(subnum),'\plots\bigquantsml.mat']);
load(['C:\Users\Fatem\OneDrive - Arizona State University\Projects\Adaptive\Bayesian Optimization\AP_BO_newsetup\DATA\4D\DATA\Subject',num2str(subnum),'\plots\bigeiml.mat']);

count = size(Objectivefunc,2);%25;
Data = Objectivefunc(:,1:count);

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



%i=size(bigmu,1);
%i=14;
iteration = [14 size(bigmu,1)];
init = 15;
figure
for j=1:2
    clear MU EI ST
    i = iteration(j);
    MU(:,:) = bigmu(i,:,:);
    EI(:,:) = bigei(i,:,:);
    ST(:,:) = bigquants(i,:,:);
    %contourf(gx,gy,MU);
    %hold on
    subplot(2,3,3*(j-1)+1)
    surf(gx,gy,MU);
    colormap('jet')
    view(2);
    colorbar
    axis([-55 -2 5 104])
    shading interp
    hold on
    plot(Blbcum(i),Bubcum(i),'y*','MarkerSize',10)
    plot(Data(2,init:i),Data(3,init:i),'k.','MarkerSize',9)
    ylabel('b_{ub}')
    if(j == 2)
        xlabel('b_{lb}')
    end
    if(j == 1)
        title('posterior mean')
        xticks([]);
    end

    subplot(2,3,3*(j-1)+2)
    surf(gx,gy,ST);
    colormap('jet')
    view(2);
    colorbar
    axis([-55 -2 5 104])
    shading interp
    hold on
    plot(Blbcum(i),Bubcum(i),'y*','MarkerSize',10)
    plot(Data(2,init:i),Data(3,init:i),'k.','MarkerSize',9)
    ylabel('b_{ub}')
    if(j == 2)
        xlabel('b_{lb}')
    end
    if(j == 1)
        title('posterior std.')
        xticks([]);
    end

    subplot(2,3,3*(j-1)+3)
    surf(gx,gy,EI);
    colormap('jet')
    view(2);
    colorbar
    axis([-55 -2 5 104])
    shading interp
    hold on
    if i < size(bigmu,1)
        plot3(Data(2,i+1),Data(3,i+1),0.2,'k+','MarkerSize',15)
    end
    ylabel('b_{ub}')
    if(j == 2)
        xlabel('b_{lb}')
    end
    if(j == 1)
        title('Acquisition function')
        xticks([]);
    end
    
end

% ML

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

iteration = [13 size(bigmuml,1)];
init = 14;
figure
for j=1:2
    clear MU EI ST
    i = iteration(j);
    MU(:,:) = bigmuml(i,:,:);
    EI(:,:) = bigeiml(i,:,:);
    ST(:,:) = bigquantsml(i,:,:);
    %contourf(gx,gy,MU);
    %hold on
    subplot(2,3,3*(j-1)+1)
    surf(gxml,gyml,MU);
    colormap('jet')
    view(2);
    colorbar
    axis([-33 -2 5 104])
    shading interp
    hold on
    plot(Blbcumml(i),Bubcumml(i),'y*','MarkerSize',10)
    plot(Data(4,init:i),Data(5,init:i),'k.','MarkerSize',9)
    ylabel('b_{ub}')
    if(j == 2)
        xlabel('b_{lb}')
    end
    if(j == 1)
        title('posterior mean')
        xticks([]);
    end

    subplot(2,3,3*(j-1)+2)
    surf(gxml,gyml,ST);
    colormap('jet')
    view(2);
    colorbar
    axis([-33 -2 5 104])
    shading interp
    hold on
    plot(Blbcumml(i),Bubcumml(i),'y*','MarkerSize',10)
    plot(Data(4,init:i),Data(5,init:i),'k.','MarkerSize',9)
    ylabel('b_{ub}')
    if(j == 2)
        xlabel('b_{lb}')
    end
    if(j == 1)
        title('posterior std.')
        xticks([]);
    end

    subplot(2,3,3*(j-1)+3)
    surf(gxml,gyml,EI);
    colormap('jet')
    view(2);
    colorbar
    axis([-33 -2 5 104])
    shading interp
    hold on
    if i < size(bigmuml,1)
        plot3(Data(4,i+1),Data(5,i+1),0.2,'k+','MarkerSize',15)
    end
    ylabel('b_{ub}')
    if(j == 2)
        xlabel('b_{lb}')
    end
    if(j == 1)
        title('Acquisition function')
        xticks([]);
    end
    
end


%%
iteration2 = [13 size(bigmuml,1)];
init2 = 14;
iteration = [14 size(bigmuml,1)];
init = 15;
figure
for j=1:2
    clear MU EI ST
    i = iteration(j);
    MU(:,:) = bigmu(i,:,:);
    EI(:,:) = bigei(i,:,:);
    ST(:,:) = bigquants(i,:,:);
    %contourf(gx,gy,MU);
    %hold on
    subplot(4,2,2*(j-1)+1)
    surf(gx,gy,MU);
    colormap('jet')
    view(2);
    colorbar
    axis([-55 -2 5 104])
    shading interp
    hold on
    plot(Blbcum(i),Bubcum(i),'y*','MarkerSize',10)
    plot(Data(2,init:i),Data(3,init:i),'k.','MarkerSize',9)
    ylabel('b_{ub}')
    if(j == 2)
        xlabel('b_{lb}')
    end
    if(j == 1)
        title('posterior mean')
        xticks([]);
    end

    subplot(4,2,2*(j-1)+2)
    surf(gx,gy,EI);
    colormap('jet')
    view(2);
    colorbar
    axis([-55 -2 5 104])
    shading interp
    hold on
    if i < size(bigmu,1)
        plot3(Data(2,i+1),Data(3,i+1),0.2,'k+','MarkerSize',15)
    end
    ylabel('b_{ub}')
    if(j == 2)
        xlabel('b_{lb}')
    end
    if(j == 1)
        title('Acquisition function')
        xticks([]);
    end
    
    clear MU EI ST
    i = iteration2(j);
    MU(:,:) = bigmuml(i,:,:);
    EI(:,:) = bigeiml(i,:,:);
    ST(:,:) = bigquantsml(i,:,:);
    %contourf(gx,gy,MU);
    %hold on
    subplot(4,2,2*(j-1)+5)
    surf(gxml,gyml,MU);
    colormap('jet')
    view(2);
    colorbar
    axis([-33 -2 5 104])
    shading interp
    hold on
    plot(Blbcumml(i),Bubcumml(i),'y*','MarkerSize',10)
    plot(Data(4,init2:i),Data(5,init2:i),'k.','MarkerSize',9)
    ylabel('b_{ub}')
    if(j == 2)
        xlabel('b_{lb}')
    end
    if(j == 1)
        title('posterior mean')
        xticks([]);
    end

    subplot(4,2,2*(j-1)+6)
    surf(gxml,gyml,EI);
    colormap('jet')
    view(2);
    colorbar
    axis([-33 -2 5 104])
    shading interp
    hold on
    if i < size(bigmuml,1)
        plot3(Data(4,i+1),Data(5,i+1),0.2,'k+','MarkerSize',15)
    end
    ylabel('b_{ub}')
    if(j == 2)
        xlabel('b_{lb}')
    end
    if(j == 1)
        title('Acquisition function')
        xticks([]);
    end
    
end

%%

%%
iteration2 = [13 14 size(bigmuml,1)];
init2 = 14;
iteration = [14 15 size(bigmuml,1)];
init = 15;
figure
for j=1:3
    clear MU EI ST
    i = iteration(j);
    MU(:,:) = bigmu(i,:,:);
    EI(:,:) = bigei(i,:,:);
    ST(:,:) = bigquants(i,:,:);
    %contourf(gx,gy,MU);
    %hold on
    subplot(3,4,4*(j-1)+1)
    surf(gx,gy,MU);
    colormap('jet')
    view(2);
    colorbar
    caxis([-3.5 0])
    axis([-55 -2 5 104])
    shading interp
    hold on
    plot(Blbcum(i),Bubcum(i),'y*','MarkerSize',10)
    plot(Data(2,init:i),Data(3,init:i),'k.','MarkerSize',9)
    ylabel('b_{ub}')
    xlabel('b_{lb}')
    if(j == 2)
        xlabel('b_{lb}')
    end
    if(j == 1)
        title('Posterior mean')
        %xticks([]);
    end
    xticks([-50 -30 -10]);
    yticks([20 60 100]);

    subplot(3,4,4*(j-1)+2)
    surf(gx,gy,EI);
    colormap('jet')
    view(2);
    cbh=colorbar
    cbh.Ticks = [0 0.1 0.2];
    caxis([0 0.2])
    axis([-55 -2 5 104])
    shading interp
    hold on
    if i < size(bigmu,1)
        plot3(Data(2,i+1),Data(3,i+1),0.2,'k+','MarkerSize',15)
    end
    ylabel('b_{ub}')
    xlabel('b_{lb}')
    if(j == 2)
        xlabel('b_{lb}')
    end
    if(j == 1)
        title('Acquisition function')
        %xticks([]);
    end
    xticks([-50 -30 -10]);
    yticks([20 60 100]);
    
    clear MU EI ST
    i = iteration2(j);
    MU(:,:) = bigmuml(i,:,:);
    EI(:,:) = bigeiml(i,:,:);
    ST(:,:) = bigquantsml(i,:,:);
    %contourf(gx,gy,MU);
    %hold on
    subplot(3,4,4*(j-1)+3)
    surf(gxml,gyml,MU);
    colormap('jet')
    view(2);
    cbh=colorbar;
    cbh.Ticks = [-1.2 -0.6 0];
    caxis([-1.2 0])
    axis([-33 -2 5 104])
    shading interp
    hold on
    plot(Blbcumml(i-1),Bubcumml(i-1),'y*','MarkerSize',10)
    plot(Data(4,init2:i),Data(5,init2:i),'k.','MarkerSize',9)
    ylabel('b_{ub}')
    xlabel('b_{lb}')
    if(j == 2)
        xlabel('b_{lb}')
    end
    if(j == 1)
        title('Posterior mean')
        %xticks([]);
    end
    xticks([-30 -15 -5]);
    yticks([20 60 100]);

    subplot(3,4,4*(j-1)+4)
    surf(gxml,gyml,EI);
    colormap('jet')
    view(2);
    colorbar
    caxis([0 0.015])
    axis([-33 -2 5 104])
    shading interp
    hold on
    if i < size(bigmuml,1)
        plot3(Data(4,i+1),Data(5,i+1),0.2,'k+','MarkerSize',15)
    end
    ylabel('b_{ub}')
    xlabel('b_{lb}')
    if(j == 2)
        xlabel('b_{lb}')
    end
    if(j == 1)
        title('Acquisition function')
        %xticks([]);
    end
    xticks([-30 -15 -5]);
    yticks([20 60 100]);
    
end
