% representative plots

clear
clc
close all
subnum = 2;
load(['C:\Users\fzahedi1\OneDrive - Arizona State University\Projects\Adaptive\Bayesian Optimization\AP_BO_newsetup\DATA\2D+Ks\Subject',num2str(subnum),'\Obfunc.mat']);
load(['C:\Users\fzahedi1\OneDrive - Arizona State University\Projects\Adaptive\Bayesian Optimization\AP_BO_newsetup\DATA\2D+Ks\Subject',num2str(subnum),'\bigmu.mat']);
load(['C:\Users\fzahedi1\OneDrive - Arizona State University\Projects\Adaptive\Bayesian Optimization\AP_BO_newsetup\DATA\2D+Ks\Subject',num2str(subnum),'\gx.mat']);
load(['C:\Users\fzahedi1\OneDrive - Arizona State University\Projects\Adaptive\Bayesian Optimization\AP_BO_newsetup\DATA\2D+Ks\Subject',num2str(subnum),'\gy.mat']);
load(['C:\Users\fzahedi1\OneDrive - Arizona State University\Projects\Adaptive\Bayesian Optimization\AP_BO_newsetup\DATA\2D+Ks\Subject',num2str(subnum),'\bigquants.mat']);
load(['C:\Users\fzahedi1\OneDrive - Arizona State University\Projects\Adaptive\Bayesian Optimization\AP_BO_newsetup\DATA\2D+Ks\Subject',num2str(subnum),'\bigei.mat']);

Data = Objectivefunc;

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
iteration = [15 size(bigmu,1)];
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
    plot(Data(2,12:i),Data(3,12:i),'k.','MarkerSize',9)
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
    plot(Data(2,12:i),Data(3,12:i),'k.','MarkerSize',9)
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
