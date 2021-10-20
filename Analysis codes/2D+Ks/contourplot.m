% contour plot

clear
clc
close all
subnum = 2;
load(['C:\Users\fzahedi1\OneDrive - Arizona State University\Projects\Adaptive\Bayesian Optimization\AP_BO_newsetup\DATA\2D+Ks\Subject',num2str(subnum),'\Obfunc.mat']);
load(['C:\Users\fzahedi1\OneDrive - Arizona State University\Projects\Adaptive\Bayesian Optimization\AP_BO_newsetup\DATA\2D+Ks\Subject',num2str(subnum),'\bigmu.mat']);
load(['C:\Users\fzahedi1\OneDrive - Arizona State University\Projects\Adaptive\Bayesian Optimization\AP_BO_newsetup\DATA\2D+Ks\Subject',num2str(subnum),'\gx.mat']);
load(['C:\Users\fzahedi1\OneDrive - Arizona State University\Projects\Adaptive\Bayesian Optimization\AP_BO_newsetup\DATA\2D+Ks\Subject',num2str(subnum),'\gy.mat']);

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


for i=11:size(bigmu,1)
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
    
    F(i-10) = getframe(gcf) ;
    drawnow
    
end

writerObj = VideoWriter(['C:\Users\fzahedi1\OneDrive - Arizona State University\Projects\Adaptive\Bayesian Optimization\AP_BO_newsetup\DATA\2D+Ks\Subject',num2str(subnum),'\Subject',num2str(subnum),'.mp4']);
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