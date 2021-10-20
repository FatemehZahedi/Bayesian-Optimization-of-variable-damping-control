clear
clc
close all
subnum = 4;
section = 4;
ntrial = section;
errorbound = 0.005;

load(['C:\Users\Fatem\OneDrive - Arizona State University\Projects\Adaptive\Bayesian Optimization\AP_BO_newsetup\DATA\4D\DATA\Subject',num2str(subnum),'\plots\Obfunc.mat']);

blockvec = [5 30 30 30];
iterationvec = [1 1 2 3];
for i = 1:4
        block = blockvec(i);
        Iteration = iterationvec(i);
        for trial = 1:ntrial
            str = ['C:\Users\Fatem\OneDrive - Arizona State University\Projects\Adaptive\Bayesian Optimization\AP_BO_newsetup\DATA\4D\DATA\Subject',num2str(subnum),'\Block',num2str(block),'\Iteration',num2str(Iteration),'\Trial',num2str((Iteration-1)*section+trial),'\KukaData.txt'];
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
            DATA.kpAP = data(:,39);
            DATA.knAP = data(:,40);
            DATA.bLBml = data(:,41);
            DATA.bUBml = data(:,42);
            DATA.kpML = data(:,43);
            DATA.knML = data(:,44);

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
            tangentialovershoot_0 = abs((max(abs(xrotated))-abs(xtargetrotated))) - errorbound;
            if tangentialovershoot_0 <= 0
                tangentialovershoot = 0;
            else
                tangentialovershoot = tangentialovershoot_0;
            end
            normalovershoot_0 = abs((max(abs(yrotated))-abs(ytargetrotated))) - errorbound;
            if normalovershoot_0 <= 0
                normalovershoot = 0;
            else
                normalovershoot = normalovershoot_0;
            end


            Tableofmeasures(trial,1) = tangentialovershoot;
            Tableofmeasures(trial,2) = normalovershoot;

            % finding enclosing ellipses

            clear xrotated yrotated

            ellipseTollerance = 0.1;
            anglerotated = [pi/4; pi - pi/4; pi + pi/4; 2*pi - pi];

            xcheck = DATA.xtarget(10)-DATA.xinit(10);
            ycheck = DATA.ytarget(10)-DATA.yinit(10);

            if xcheck >= 0 && ycheck >= 0
                angle = -anglerotated(1);
            elseif xcheck < 0 && ycheck >=0
                angle = -anglerotated(2);
            elseif xcheck < 0 && ycheck < 0
                angle = -anglerotated(3);
            elseif xcheck >=0 && ycheck < 0
                angle = -anglerotated(4);
            end

            xrotated = (DATA.x(firsthit:end))*cos(angle)-(DATA.y(firsthit:end))*sin(angle);
            yrotated = (DATA.y(firsthit:end))*cos(angle)+(DATA.x(firsthit:end))*sin(angle);

            % Calculate and plot the enclousing ellipse
            [A, C] = MinVolEllipse([xrotated'; yrotated'], ellipseTollerance);
            area = Ellipse_plot(A, C);


            Tableofmeasures(trial,3) = area;

            % Variability time

            variabilitytime = (tstability - (firsthit-1))*0.001;
            Tableofmeasures(trial,4) = variabilitytime;

            % mean speed
            velocityboth = sqrt(DATA.Vx.^2 + DATA.Vy.^2);
            meanspeed = mean(velocityboth(firstmove:firsthit));

            Tableofmeasures(trial,5) = meanspeed;

            % maximum speed

            maxspeed = max(velocityboth);
            Tableofmeasures(trial,6) = maxspeed;

            % User Effort

            ForceRMS = sqrt(0.5*(DATA.Forcex.^2 + DATA.Forcey.^2));

            meanRMS = mean(ForceRMS);
            maxRMS = max(ForceRMS);

            Tableofmeasures(trial,7) = meanRMS;
            Tableofmeasures(trial,8) = maxRMS;

            EnergyAP = (DATA.Forcey(firstmove:tstability)).*(DATA.Vy(firstmove:tstability))*(tstability-firstmove+1)*0.001;
            Tableofmeasures(trial,9) = mean(abs(EnergyAP));
            EnergyML = (DATA.Forcex(firstmove:tstability)).*(DATA.Vx(firstmove:tstability))*(tstability-firstmove+1)*0.001;
            Tableofmeasures(trial,10) = mean(abs(EnergyML));

        end
    Avemeasures(i,:,1) = mean(Tableofmeasures,1);
    Avemeasures(i,:,2) = std(Tableofmeasures);
end
%%
Avemeasures(:,11,1) = sqrt(Avemeasures(:,9,1).^2 + Avemeasures(:,10,1).^2);

Newmeasures(1,:,:) = Avemeasures(1,:,:);
[~,index] = min(Avemeasures(2:end,11,1));
Newmeasures(2,:,:) = Avemeasures(index+1,:,:);
Newmeasures(3,:,:) = mean(Avemeasures(2:end,:,:));

percentageImprove = (-(Newmeasures(2,:,1)- Newmeasures(1,:,1))./mean(Newmeasures(1:2,:,1)))*100;

percentageImprove(5)= -percentageImprove(5);
percentageImprove(6) = -percentageImprove(6);

save(['C:\Users\Fatem\OneDrive - Arizona State University\Projects\Adaptive\Bayesian Optimization\AP_BO_newsetup\DATA\4D\DATA\Subject',num2str(subnum),'\Subject',num2str(subnum),'.mat'],'percentageImprove','Newmeasures','Avemeasures');

            
    