function [featuresTimeTables, relevantSignal] = featuresToTimeTables(...
    featureSet, monster, signal, sampleRate, frameOfFocus)
% FEATURESTOTIMETABLES Get the features computed with MAKETRACKMONSTER as
% an array of MATLAB time tables, to plot with STACKEDPLOT.
% 
% [!] This function assumes signal is mono.

    monsterSlice = monster(frameOfFocus, :);

    nFeatures = length(featureSet);
    
    % Allocate empty cell array to hold feature time tables.
    featuresTimeTables = cell(1, nFeatures);

    % For each feature in the feature set.
    for featureNum = 1:nFeatures
    
        feature = featureSet(featureNum);

        featureName = baseFeatCodeToName(feature.featname);
    
        startTime = milliseconds(feature.startms);
        endTime = milliseconds(feature.endms);
        value = monsterSlice(featureNum);

        % Create the timetable.
        featureTimeTable = timetable([startTime; endTime], ...
            [value; value], 'VariableNames', {featureName});

        featuresTimeTables(featureNum) = {featureTimeTable};
    
    end

    % TODO Apply some downsampling?

    % Get the portion of the signal with these features.
    featureStartTimes = cellfun(@(x) min(x.Time), featuresTimeTables);
    featureEndTimes = cellfun(@(x) max(x.Time), featuresTimeTables);
    minStartTime = min(featureStartTimes);
    maxEndTime = max(featureEndTimes);
    minTimeSeconds = seconds(minStartTime);
    maxTimeSeconds = seconds(maxEndTime);
    startSample = minTimeSeconds * sampleRate;
    endSample = maxTimeSeconds * sampleRate;
    relevantSignal = signal(startSample+1:endSample);

end