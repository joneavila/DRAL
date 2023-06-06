function [firstCompleteFrame, monster] = makeTrackMonsterModified(trackspec, featurelist)

% inputs:
%   trackspec: includes au pathname plus track (left or right)
%   fsspec: feature set specification
% output:
%   monster is a large 2-dimensional array, 
%     where every row is a timepoint, 10ms apart, starting at 10ms (?)
%     and every column a feature
%   firstCompleteFrame, is the first frame for which all data tracks
%     are present.   This considers only the fact that the gaze
%     track may not have values up until frame x
%     It does not consider the fact that some of the wide past-value
%     features may not have meaningful values until some time into the data
%     The reason for this is that, in case the gaze data starts late,
%     we pad it with zeros, rather than truncating the audio.  This is because
%     we compute times using not timestamps, but implicitly, e.g. frame 0 
%     is anchored at time zero (in the audio track)
% efficiency issues: 
%   lots of redundant computation
%   compute everything every 10ms, then in the last step downsample to 20ms
% testing:
%   the simplest test harness is validateFeature.m

% Nigel Ward, UTEP, 2014-2015


% Below are my main modifications. The documentation above has not been
% modified.
% - Remove code related to gaze features.
% - Remove code related to keystroke features.
% - Remove code related to plotting.
% - Add error to DECIDEIFSTEREO if audio is stereo. The rest of the code
%   assumes the audio is mono.
% - Replace LOOKUPORCOMPUTEPITCH with LOOKUPORCOMPUTEPITCHMODIFIED.

firstCompleteFrame = 1;
lastCompleteFrame = 9999999999999;

msPerFrame = 10; 

% ------ First, compute frame-level features ------
stereop = decideIfStereo(trackspec, featurelist);  % error-prone

[sampleRate, signal] = readtracks(trackspec.path);

if size(signal,2) < 2 && stereop
    fprintf('%s is not a stereo file, though the feature list ', trackspec.path);
    fprintf('and/or \n the channel in the trackspec suggested it was.  Exiting...\n');
    error('Not Stereo.');
end

samplesPerFrame = msPerFrame * (sampleRate / 1000);

% TODO Check whether the audio is truly mono.

signal = signal(:,1);

pitchRaw = lookUpOrComputePitchModified(trackspec.directory,...
    trackspec.filename, signal, sampleRate);

energy = computeLogEnergy(signal', samplesPerFrame);

pitch = pitchRaw;  
cepFlux = cepstralFlux(signal, sampleRate, energy);

if isnan(sum(cepFlux))
    bfp = fopen('badfiles.txt', 'a');
    nanFraction = sum(isnan(cepFlux))/length(cepFlux);
    fprintf('                      fraction of NaNs in cepstral Flux l  is %.4f\n',  nanFraction);
    fprintf(bfp, '                      fraction of NaNs in cepstral Flux l  is %.4f\n',  nanFraction);
    fprintf(bfp, 'NaN in cepstralFlux l for %s\n', trackspec.filename);
    fclose(bfp);
end

nframes = floor(length(signal(:,1)) / samplesPerFrame);
lastCompleteFrame = min([nframes, lastCompleteFrame]);

maxPitch = 500;
pitchPer = percentilizePitch(pitch, maxPitch);

% ------ Second, compute derived features, and add to monster ------
for featureNum = 1 : length(featurelist)

    thisfeature = featurelist(featureNum);
    duration = thisfeature.duration;
    startms = thisfeature.startms;
    endms = thisfeature.endms;
    feattype = thisfeature.featname;

    relevantPitch = pitch;
    relevantPitchPer = pitchPer;
    relevantEnergy = energy;
    relevantFlux = cepFlux;
    relevantSig = signal;

    switch feattype
        case 'vo'    % volume/energy/intensity/amplitude
            featurevec = windowEnergy(relevantEnergy, duration)';  
        case 'vf'    % voicing fraction
            featurevec = windowize(~isnan([0 relevantPitch' 0]), duration)';
        case 'sf'    % speaking fraction
            featurevec = speakingFraction(relevantEnergy, duration)';
        case 'en'    % cepstral distinctiveness
            featurevec = cepstralDistinctness(relevantSig, sampleRate, relevantPitch, duration, 'enunciation')';
        case 're'    % cepstral blandness
            featurevec = cepstralDistinctness(relevantSig, sampleRate, relevantPitch, duration, 'reduction')';
        case 'th'    % pitch truly high-ness
            featurevec = computePitchInBand(relevantPitchPer, 'th', duration);
        case 'tl'    % pitch truly low-ness
            featurevec = computePitchInBand(relevantPitchPer, 'tl', duration);
        case 'lp'    % pitch lowness 
            featurevec = computePitchInBand(relevantPitchPer, 'l', duration);
        case 'hp'    % pitch highness
            featurevec = computePitchInBand(relevantPitchPer, 'h', duration);
        case 'fp'    % flat pitch range 
            featurevec  = computePitchRange(relevantPitch, duration,'f')';
        case 'np'    % narrow pitch range 
            featurevec  = computePitchRange(relevantPitch, duration,'n')';
        case 'wp'    % wide pitch range 
            featurevec  = computePitchRange(relevantPitch, duration,'w')'; 
        case 'sr'    % speaking rate 
            featurevec = computeRate(relevantEnergy, duration)';
        case 'cr'    % creakiness
            featurevec = computeCreakiness(relevantPitch, duration); 
        case 'pd'    % peakDisalignment
            featurevec = computeWindowedSlips(relevantEnergy, relevantPitchPer, duration,trackspec)';
        case 'le'    % lengthening
            featurevec = computeLengthening(relevantEnergy, relevantFlux, duration);
        case 'vr'    % voiced-unvoiced energy ratio
            featurevec = voicedUnvoicedIR(relevantEnergy, relevantPitch, duration)';
        case 'cp'    % CPPS
            cpvec = lookupOrComputeCpps(...
                trackspec.directory, [trackspec.filename trackspec.side], ...
                relevantSig, sampleRate);
            featurevec = windowize(cpvec',duration)';
        case 'ts'  % time from start
            featurevec =  windowize(1:length(relevantPitch), duration)';
        case 'te'  % time until end
            featurevec =  windowize((length(relevantPitch) - (1:length(relevantPitch))), duration)';

        case 'ns' % near to start
            featurevec = distanceToNearness(windowize(1:length(relevantPitch), duration)');

        case 'ne' % near to end
            featurevec = distanceToNearness(windowize((length(relevantPitch) - (1:length(relevantPitch))), duration)');
        otherwise
            warning([feattype ' :  unknown feature type']);
    end 
  
    % time-shift values as appropriate, either up or down (backward or forward in time)
    % the first value of each featurevec represents the situation at 10ms or 15ms
    centerOffsetMs = (startms + endms) / 2;     % offset of the window center
    shift = round(centerOffsetMs / msPerFrame);
    if (shift == 0)
        shifted = featurevec;
    elseif (shift < 0)
        % then we want data from the past, so move it forward in time, 
        % by stuffing zeros in the front 
        shifted = [zeros(-shift,1); featurevec(1:end+shift)];  
    else 
        % shift > 0: want data from the future, so move it backward in time,
        % padding with zeros at the end
        shifted = [featurevec(shift+1:end); zeros(shift,1)];  
    end

    %Some features on some tracks end up with a shifted that is less than
    %lastCompleteFrame - 1.  Pads it with zeros to make it equal to
    %lastCompleteFrame - 1, so the next line of code does not error out.
    if size(shifted,1) < lastCompleteFrame-1
        shifted = [shifted; zeros(lastCompleteFrame-1-size(shifted,1), 1)];
    end
    % might convert from every 10ms to every 20ms to same time and space,
    % here, instead of doing it at the very end in writePcFilesBis
    %  downsampled = shifted(2:2:end);   
    shifted = shifted(1:lastCompleteFrame-1);

    features_array{featureNum} = shifted;  % append shifted values to monster
end   % loop back to do the next feature

monster = cell2mat(features_array);  % flatten it to be ready for princomp

end

% true if trackspec is a right channel or any feature is inte
function stereop = decideIfStereo(trackspec, featurelist)
  stereop = false;
  if strcmp(trackspec.side, 'r')
    stereop = true;
  end
  for featureNum = 1 : length(featurelist)
    thisfeature = featurelist(featureNum);
    if strcmp(thisfeature.side, 'inte')
      stereop = true;
    end
  end
  if stereop
    error('MAKETRACKMONSTERMODIFIED is not designed for stereo audio.')
  end
end


