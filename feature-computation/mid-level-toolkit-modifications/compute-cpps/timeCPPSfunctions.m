% This script prints the total running times of two (or more) compute CPPS
% functions.

% The directory with .wav files to read and compute CPPS from.
inputDir = './release/fragments-concatenated-16000';

funcsToTime = {'computeCPPS', 'computeCPPSmodified'};
numFuncs = length(funcsToTime);

totalRunTimes_s = zeros(numFuncs, 1);

audioFiles = dir(strcat(inputDir,'/*.wav'));
numAudioFiles = length(audioFiles);

totalAudioDuration_s = 0.0;

% The number of times to run the functions on the same set of audios.
numTests = 10;

% For each test.
for testNum = 1:numTests
    fprintf('Running test %d of %d\n', testNum, numTests);

    % For each audio in the input directory.
    for audioFileNum = 1:numAudioFiles
        audioFile = audioFiles(audioFileNum);
        audioPath = strcat(audioFile.folder,'/',audioFile.name);
        [signal, sampleRate] = audioread(audioPath);

        signalDuration_s = length(signal) / sampleRate;
        totalAudioDuration_s = totalAudioDuration_s + signalDuration_s;

        % Randomize the order to execute functions.
        randFuncOrder = randperm(numFuncs);
        funcsToTimeShuffled = funcsToTime(randFuncOrder);

        % For each function to time.
        for funcNum = 1:numFuncs

            % Time the function.
            tic
            funcToTime = funcsToTimeShuffled{funcNum};
            feval(funcToTime, signal, sampleRate);
            elapsedTime_s = toc;

            % Add the elapsed time to its total running time.
            originalOrderIdx = randFuncOrder(funcNum);
            totalRunTimes_s(originalOrderIdx) = ...
                totalRunTimes_s(originalOrderIdx) + elapsedTime_s;
        end

    end
end

% Print the results.
fprintf('Total running times from %d tests on %d audios (%f seconds total audio duration):\n', numTests, numAudioFiles, totalAudioDuration_s)
for funcNum = 1:numFuncs
    fprintf('%s %f seconds\n', funcsToTime{funcNum}, totalRunTimes_s(funcNum));
end
