clc
clear
close all

% fileID = fopen('/home/fzahedi/Fatemeh/Adaptive/AP_BO_newsetup/Subjectnum.txt','r');
% formatSpec = '%f';
% subnum = fscanf(fileID,formatSpec);
subnum = 7;
ntrial = 1;
priornum = 10;

errorbound = 0.005;
% pathobj = ['/home/fzahedi/Fatemeh/Adaptive/AP_BO_newsetup/DATA/Subject',num2str(subnum),'/Obfunc.mat'];
% load(pathobj);
%blocknew = 1;
for blocknew = 1:2
    if blocknew > 1
        pathobj = ['/home/fzahedi/Fatemeh/Adaptive/AP_BO_newsetup/DATA/Subject',num2str(subnum),'/Obfunc.mat'];
        load(pathobj);
        ftrialbased = Objectivefunc';
    end
    for block = 1 : 10 % This should be changed based on iteration that we are in
        clear measures

    %     if block > 10
    %         pathobj = ['D:\Adaptive\Experiment_AP_lowerbound\Data\Subject',num2str(subnum),'\obj.mat'];
    %         load(pathobj);
    %     end
        %ftrialbased = Objectivefunc';
        for trial = 1 : ntrial
            clear data DATA move hit ind_stability tstability
            str = ['/home/fzahedi/Fatemeh/Adaptive/AP_BO_newsetup/DATA/Subject',num2str(subnum),'/Block',num2str(blocknew),'/Trial',num2str(block),'/KukaData.txt'];
            data = load(str);

            DATA.x = data(:,27);
            DATA.y = data(:,28);
            DATA.xinit = data(:,25);
            DATA.yinit = data(:,26);
            DATA.xtarget = data(:,23);
            DATA.ytarget = data(:,24);
            DATA.Vx = data(:,20);
            DATA.Vy = -data(:,19);
            DATA.ax = data(:,22);
            DATA.ay = -data(:,21);
            DATA.uintentx = DATA.Vx.*DATA.ax;
            DATA.uintenty = DATA.Vy.*DATA.ay;
            DATA.Bx = data(:,18);
            DATA.By = data(:,17);
            DATA.Forcex = data(:,10);
            DATA.Forcey = -data(:,9);
            DATA.bLBap = data(:,37);
            DATA.bUBap = data(:,38);
    %         DATA.x = data(:,1);
    %         DATA.y = data(:,2);
    %         DATA.xinit = data(:,3);
    %         DATA.yinit = data(:,4);
    %         DATA.xtarget = data(:,5);
    %         DATA.ytarget = data(:,6);
    %         DATA.Vx = data(:,7);
    %         DATA.Vy = -data(:,8);
    %         DATA.ax = data(:,9);
    %         DATA.ay = -data(:,10);
    %         DATA.uintentx = DATA.Vx.*DATA.ax;
    %         DATA.uintenty = DATA.Vy.*DATA.ay;
    %         DATA.Bx = data(:,11);
    %         DATA.By = data(:,12);
    %         DATA.Forcex = data(:,13);
    %         DATA.Forcey = -data(:,14);
    %         DATA.bLBap = data(:,15);
    %         DATA.bLBml = data(:,16);
    %         DATA.kpap = data(:,17);
    %         DATA.knap = data(:,18);
    %         DATA.kpml = data(:,19);
    %         DATA.knml = data(:,20);
    %         DATA.bUPap = data(:,21);
    %         DATA.bUPml = data(:,22);

            move = find(((DATA.x-DATA.xinit(10)).^2+(DATA.y-DATA.yinit(10)).^2)>= (errorbound)^2);
            flag = 0;
            q = 1;
            for f=1:length(move)
                    if f < length(move) && flag == 0

                        if move(f+1)-move(f) > 1
                            e_length = f - q;
                            if e_length >= 500
                                firstmove = move(q);
                                flag = 1;
                            else
                                q = f+1;
                            end
                        end
                    end
                    if f == length(move) && flag == 0
                        firstmove = move(q);
                    end
            end

            hit = find(((DATA.x-DATA.xtarget(10)).^2+(DATA.y-DATA.ytarget(10)).^2)<= (errorbound)^2);
            firsthit = hit(1);
            if firstmove == 1
                testtrial = trial;
            end
            ind_stability = find(((DATA.x-DATA.xtarget(10)).^2+(DATA.y-DATA.ytarget(10)).^2)<= (errorbound)^2);
            flag = 0;
            q = 1;
            for f=1:length(ind_stability)
                    if f < length(ind_stability) && flag == 0

                        if ind_stability(f+1)-ind_stability(f) > 1
                            e_length = f - q;
                            if e_length >= 500
                                tstability = ind_stability(q);
                                flag = 1;
                            else
                                q = f+1;
                            end
                        end
                    end
                    if f == length(ind_stability) && flag == 0
                        e_length = f - q;
                        if e_length >= 500
                            tstability = ind_stability(q);
                        else
                            tstability = 2000 + firsthit - 1;
                        end
                    end
            end

            % finding overshoot

            clear xrotated yrotated

            angleofrotation = atan2(DATA.ytarget(10)-DATA.yinit(10),DATA.xtarget(10)-DATA.xinit(10));
            angle = -angleofrotation;
            xrotated = (DATA.x-DATA.xinit(10))*cos(angle)-(DATA.y-DATA.yinit(10))*sin(angle);
            yrotated = (DATA.y-DATA.yinit(10))*cos(angle)+(DATA.x-DATA.xinit(10))*sin(angle);
            xtargetrotated = (DATA.xtarget(10)-DATA.xinit(10))*cos(angle)-(DATA.ytarget(10)-DATA.yinit(10))*sin(angle);
            ytargetrotated = (DATA.ytarget(10)-DATA.yinit(10))*cos(angle)+(DATA.xtarget(10)-DATA.xinit(10))*sin(angle);

            tangentialovershootpercentage = abs((max(abs(xrotated))-xtargetrotated)/xtargetrotated)*100;
            %%%tangentialovershoot = abs((max(abs(xrotated))-abs(xtargetrotated)));
            %normalovershootpercentage = abs((max(abs(yrotated))-ytargetrotated)/ytargetrotated)*100;
            %%%normalovershoot = abs((max(abs(yrotated))-abs(ytargetrotated)));
            tangentialovershoot_0 = abs((max(abs(xrotated))-abs(xtargetrotated)));% - errorbound;
    %         if tangentialovershoot_0 <= 0
    %             tangentialovershoot = 0;
    %         else
    %             tangentialovershoot = tangentialovershoot_0;
    %         end
            normalovershoot_0 = abs((max(abs(yrotated))-abs(ytargetrotated)));% - errorbound;
    %         if normalovershoot_0 <= 0
    %             normalovershoot = 0;
    %         else
    %             normalovershoot = normalovershoot_0;
    %         end

            tangentialovershoot = tangentialovershoot_0;
            normalovershoot = normalovershoot_0;

            measures(trial,1) = tangentialovershoot;
            measures(trial,2) = normalovershoot; % not useful at this moment

            clear xrotated yrotated

            ellipseTollerance = 0.1;
            %anglerotated = [pi/4; pi - pi/4; pi + pi/4; 2*pi - pi];
            anglerotated = [0; pi ; pi + pi/2; pi/2];

            xcheck = DATA.xtarget(10)-DATA.xinit(10);
            ycheck = DATA.ytarget(10)-DATA.yinit(10);

    %             if xcheck >= 0 && ycheck >= 0
    %                 angle = -anglerotated(1);
    %             elseif xcheck < 0 && ycheck >=0
    %                 angle = -anglerotated(2);
    %             elseif xcheck < 0 && ycheck < 0
    %                 angle = -anglerotated(3);
    %             elseif xcheck >=0 && ycheck < 0
    %                 angle = -anglerotated(4);
    %             end

            if xcheck > 0 && ycheck == 0
                angle = -anglerotated(1);
            elseif xcheck < 0 && ycheck ==0
                angle = -anglerotated(2);
            elseif xcheck == 0 && ycheck < 0
                angle = -anglerotated(3);
            elseif xcheck ==0 && ycheck > 0
                angle = -anglerotated(4);
            end

            xrotated = ((DATA.x(firsthit:end))*cos(angle)-(DATA.y(firsthit:end))*sin(angle))*100;
            yrotated = ((DATA.y(firsthit:end))*cos(angle)+(DATA.x(firsthit:end))*sin(angle))*100;


            % Calculate and plot the enclousing ellipse
            [A, C] = MinVolEllipse([xrotated'; yrotated'], ellipseTollerance);
            %hold on
            area = Ellipse_plot(A, C);

            measures(trial,7) = area;

            % Variability time

            variabilitytime = (tstability - (firsthit-1))*0.001;%(tstability - firstmove)*0.001;
            measures(trial,8) = variabilitytime;

            %mean speed

            velocity = abs(DATA.Vy);
            meanspeed = mean(velocity(firstmove:firsthit));

            measures(trial,3) = meanspeed;

            % maximum speed

            maxspeed = max(velocity);
            measures(trial,5) = maxspeed;

            % User Effort

            ForceRMS = sqrt(0.5*(DATA.Forcex.^2 + DATA.Forcey.^2));

            meanRMS = mean(ForceRMS);
            maxRMS = max(ForceRMS);

            measures(trial,4) = meanRMS;
            measures(trial,6) = maxRMS;

            %-------------------

            measures(trial,9)= meanRMS*meanspeed;
            Energy = (sqrt(0.5*(DATA.Forcex(firstmove:tstability).^2 + DATA.Forcey(firstmove:tstability).^2))).*velocity(firstmove:tstability)*(tstability-firstmove+1)*0.001;
            measures(trial,11) = mean(Energy);
            powercorrection = DATA.Forcey(firstmove:tstability).*DATA.Vy(firstmove:tstability)*(tstability-firstmove+1)*0.001;
            indexpower=find(powercorrection<0);
            powercorrection(indexpower)=powercorrection(indexpower).^2;
            measures(trial,10) = mean(powercorrection);

            %-------------------------------------------------------------------------------
            ftrial(trial) = -0.5*(measures(trial,11))^2;

        end
        b_LB = DATA.bLBap;
        b_UB = DATA.bUBap;

        ftrialbased(block+(blocknew-1)*priornum,2) = b_LB(10);
        ftrialbased(block+(blocknew-1)*priornum,3) = b_UB(10);
        %---------------------------------------------------------------------------------------------
        ftrialbasedblock(block+(blocknew-1)*priornum,:) = ftrial;
        sortf = sort(ftrial,'descend');
        ftrialbasedblocksort(block+(blocknew-1)*priornum,:) = sortf;
        ftrialbased(block+(blocknew-1)*priornum,1) = mean(sortf(1:ntrial));

    end
    Objectivefunc = ftrialbased';
    save(['/home/fzahedi/Fatemeh/Adaptive/AP_BO_newsetup/DATA/Subject',num2str(subnum),'/Obfunc.mat'],'Objectivefunc');
end

[~,order2]=sortrows(ftrialbased(:,2));
ftrialbased2 = ftrialbased(order2,:);

[~,order3]=sortrows(ftrialbased(:,3));
ftrialbased3 = ftrialbased(order3,:);

figure
plot(ftrialbased2(:,2),ftrialbased2(:,1));
xlabel('damping values')
ylabel('objective function Energy based')

figure
plot(ftrialbased3(:,3),ftrialbased3(:,1));
xlabel('damping values UB')
ylabel('objective function Energy based')

% Objectivefunc(1,end+1) = ftrialbased(end,1)';
% Objectivefunc(2,end+1) = ftrialbased(end,2)';
%Objectivefunc = ftrialbased';

save(['/home/fzahedi/Fatemeh/Adaptive/AP_BO_newsetup/Prior/Obfunc',num2str(subnum),'.mat'],'Objectivefunc');


