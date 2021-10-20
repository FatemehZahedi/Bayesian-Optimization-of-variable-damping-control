% contour plot

clear
clc
close all
subnum = 4;
load(['C:\Users\Fatem\OneDrive - Arizona State University\Projects\Adaptive\Bayesian Optimization\AP_BO_newsetup\DATA\4D\DATA\Subject',num2str(subnum),'\plots\Obfunc.mat']);

load(['C:\Users\Fatem\OneDrive - Arizona State University\Projects\Adaptive\Bayesian Optimization\AP_BO_newsetup\DATA\4D\DATA\Subject',num2str(subnum),'\plots\bigmu.mat']);
load(['C:\Users\Fatem\OneDrive - Arizona State University\Projects\Adaptive\Bayesian Optimization\AP_BO_newsetup\DATA\4D\DATA\Subject',num2str(subnum),'\plots\gx.mat']);
load(['C:\Users\Fatem\OneDrive - Arizona State University\Projects\Adaptive\Bayesian Optimization\AP_BO_newsetup\DATA\4D\DATA\Subject',num2str(subnum),'\plots\gy.mat']);

load(['C:\Users\Fatem\OneDrive - Arizona State University\Projects\Adaptive\Bayesian Optimization\AP_BO_newsetup\DATA\4D\DATA\Subject',num2str(subnum),'\plots\bigmuml.mat']);
load(['C:\Users\Fatem\OneDrive - Arizona State University\Projects\Adaptive\Bayesian Optimization\AP_BO_newsetup\DATA\4D\DATA\Subject',num2str(subnum),'\plots\gxml.mat']);
load(['C:\Users\Fatem\OneDrive - Arizona State University\Projects\Adaptive\Bayesian Optimization\AP_BO_newsetup\DATA\4D\DATA\Subject',num2str(subnum),'\plots\gyml.mat']);

count = 40;
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

init = 13;
for i=init:size(bigmu,1)
%i=11;
    
    clear MU
    MU(:,:) = bigmu(i,:,:);
    figure
    %contourf(gx,gy,MU);
    %hold on
    surf(gx,gy,MU);
    colormap('jet')
    view(2);
    axis([-55 -2 5 104])
    shading interp
    hold on
    plot(Blbcum(i),Bubcum(i),'y*','MarkerSize',10)
    plot(Data(2,1:i),Data(3,1:i),'k.','MarkerSize',9)
    if i < size(bigmu,1)
        plot(Data(2,i+1),Data(3,i+1),'k+','MarkerSize',15)
    end
    ylabel('b_{ub}')
    xlabel('b_{lb}')
    title(['Iteration ', num2str(i)]);
    
    F(i-init+1) = getframe(gcf) ;
    drawnow
    
end

writerObj = VideoWriter(['C:\Users\Fatem\OneDrive - Arizona State University\Projects\Adaptive\Bayesian Optimization\AP_BO_newsetup\DATA\4D\DATA\Subject',num2str(subnum),'\Subject',num2str(subnum),'ap']);
writerObj.FrameRate = 1;
writerObj.Quality = 100;

open(writerObj);
% write the frames to the video
for i=1:length(F)
    % convert the image to a frame
    frame = F(i) ;    
    writeVideo(writerObj, frame);
end
% close the writer object
close(writerObj);

% ML---------------------------------------------------------------
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

clear F
for i=init:size(bigmuml,1)
%i=11;
    
    clear MU
    MU(:,:) = bigmuml(i,:,:);
    figure
    %contourf(gx,gy,MU);
    %hold on
    surf(gxml,gyml,MU);
    colormap('jet')
    view(2);
    axis([-33 -2 5 104])
    shading interp
    hold on
    plot(Blbcumml(i),Bubcumml(i),'y*','MarkerSize',10)
    plot(Data(4,1:i),Data(5,1:i),'k.','MarkerSize',9)
    if i < size(bigmuml,1)
        plot(Data(4,i+1),Data(5,i+1),'k+','MarkerSize',15)
    end
    ylabel('b_{ub}')
    xlabel('b_{lb}')
    title(['Iteration ', num2str(i)]);
    
    F(i-init+1) = getframe(gcf) ;
    drawnow
    
end

writerObj = VideoWriter(['C:\Users\Fatem\OneDrive - Arizona State University\Projects\Adaptive\Bayesian Optimization\AP_BO_newsetup\DATA\4D\DATA\Subject',num2str(subnum),'\Subject',num2str(subnum),'ml']);
writerObj.FrameRate = 2;
writerObj.Quality = 100;

open(writerObj);
% write the frames to the video
for i=1:length(F)
    % convert the image to a frame
    frame = F(i) ;    
    writeVideo(writerObj, frame);
end
% close the writer object
close(writerObj);

