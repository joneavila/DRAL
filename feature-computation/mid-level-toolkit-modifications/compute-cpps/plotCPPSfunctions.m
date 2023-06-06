%% 
% Test 1. Plot CPPS functions for concatenated fragments, original and
% re-enacted, split tracks (mono), 16 kHz.
plotCPPS('./release/fragments-concatenated-downsampled', ...
    './CPPS-plots-concatenated')

%%
% Test 2. Plot CPPS functions for original conversations, split tracks
% (mono), 16 kHz.
% Note: The audios in this directory were hand-picked. process_markups.py
% does not currently create this directory automatically.
plotCPPS('./release/recordings-og-split', './CPPS-plots-og')

function plotCPPS(inputDir, outputDir)
% PLOTCPPS Compute CPPS for audios in an input directory, with both
% computeCPPSmodified and Midlevel Toolkit computeCPPS, and display and
% save plots as .fig and .jpg to an output directory.
%   
%   Input arguments:
%       inputDir (char) - The directory to read audios (.wav) from.
%       outputDir (char) - The directory to write plots (.fig, .jpg) to.

makeDirIfNotExists(outputDir);

audioFiles = dir(strcat(inputDir,'/*.wav'));
numAudioFiles = length(audioFiles);

cppsCorrCoefficients = zeros(numAudioFiles, 1);
signalDurations_s = zeros(numAudioFiles, 1);

% For all .wav files in the input directory.
for audioNum = 1:numAudioFiles

    audioFile = audioFiles(audioNum);
    
    % Print progress.
    fprintf('%d/%d %s\n', audioNum, numAudioFiles, audioFile.name);

    audioPath = strcat(audioFile.folder,'/',audioFile.name);
    [signal, sampleRate] = audioread(audioPath);

    signalDuration_s = length(signal) / sampleRate;
    signalDurations_s(audioNum) = signalDuration_s;

    [~,audioID,~] = fileparts(audioFile.name);

    cppsOriginal = computeCPPS(signal, sampleRate);
    cppsModified = computeCPPSmodified(signal, sampleRate);

    % Trim cppsModified to match the length of cppsOriginal.
    % computeCPPSmodified adds more padding than Midlevel Toolkit
    % computeCPPS so cppsModified is always longer.
    cppsModified = cppsModified(1:length(cppsOriginal));

    % Compute the correlation between cppsOriginal and cppsModified.
    cpssCorr = corrcoef(cppsModified, cppsOriginal);
    cppsCorrCoefficient = cpssCorr(1,2);
    cppsCorrCoefficients(audioNum) = cppsCorrCoefficient;

    % Plot cppsOriginal and cppsModified on the same x-axis.
    plot(cppsOriginal, 'Color', '#0072BD', 'DisplayName', 'original')
    hold on
    plot(cppsModified, 'Color', '#D95319', 'DisplayName', 'modified')
    hold off

    % Add a title with the audio ID.
    titleStr = sprintf('%s', audioID);
    title(titleStr)

    % Add a subtitle with the sample rate and correlation coefficient
    % between cppsOriginal and cppsModified.
    subTitleStr = sprintf('sampleRate=%d, corrCoefficient=%f',...
        sampleRate, cppsCorrCoefficient);
    subtitle(subTitleStr)

    % Add a legend.
    legend

    % Write the figure as a .fig to the output directory.
    outputFigPath = strcat(outputDir, '/', audioID, '.fig');
    savefig(outputFigPath)

    % Write the figure as a .jpg to the output directory.
    outputImagePath = strcat(outputDir, '/', audioID, '.jpg');
    exportgraphics(gca, outputImagePath)
end

% Print the mininum, maximum, and mean CPPS correlation coefficients.
minCppsCorrCoeff = min(cppsCorrCoefficients);
maxCppsCorrCoeff = max(cppsCorrCoefficients);
meanCppsCorrCoeff = mean(cppsCorrCoefficients);
fprintf(['minCppsCorrCoeff=%d, maxCppsCorrCoeff=%d, ...' ...
    'meanCppsCorrCoeff=%d\n'], minCppsCorrCoeff, maxCppsCorrCoeff,...
    meanCppsCorrCoeff);

% Compute the correlation between signal durations and the correlations
% between cppsOriginal and cppsModified.
cpssDurationCorr = corrcoef(cppsCorrCoefficients, signalDurations_s);
cppsDurationCorrCoefficient = cpssDurationCorr(1,2);
fprintf('cppsDurationCorrCoefficient=%f\n', cppsDurationCorrCoefficient);

end