% [!] This function is part of a workflow described in
%     ../DRAL-corpus/README.md.

function runPCAfunctions()
% RUNPCAFUNCTIONS A helper function to call RUNPCAFUNCTIONSFORLANG for
% multiple languages in sequence.

    runPCAfunctionsForLang('EN');
    runPCAfunctionsForLang('ES');
end

function runPCAfunctionsForLang(langCode)
% RUNPCAFUNCTIONSFORLANG Call various Mid-level Toolkit PCA-related
% functions, modified for use with DRAL fragments whose features are
% computed differently than the orginal workflow expects.
%
% Input arguments:
%   langCode (char) - an ISO 639-1 language code, as used in DRAL metadata

    dirWorking = pwd;
    dirFeatures = strcat(dirWorking, '/DRAL-corpus/release/features/');

    % Input paths.
    pathFssFile = strcat(dirFeatures, 'dummy.fss');
    warning(['This function reads a feature set specification file ' ...
        'that should not be used elsewhere. If the feature set ' ...
        'changes, update this file.'])
    pathFeatures = strcat(dirFeatures, 'features.csv');
    pathMetadataTrain = strcat(dirFeatures, langCode, '-train.csv');
    pathMetadataTest = strcat(dirFeatures, langCode, '-test.csv');

    % Output paths.
    dirOutput = strcat(dirFeatures, 'PCA-outputs-', langCode, '/');
    makeDirIfNotExists(dirOutput);
    pathTrackListTrain = strcat(dirOutput, 'track-list-train-', ...
        langCode, '.tl');
    pathTrackListTest = strcat(dirOutput, 'track-list-test-', ...
        langCode, '.tl');

    idxTrain = readIdxFromMetadata(pathMetadataTrain);
    idxTest = readIdxFromMetadata(pathMetadataTest);
    
    % Get train and test partitions.
    features = readtable(pathFeatures, 'RowNamesColumn', 1);

    % TODO Temporary fix: Ignore the rows (fragments) that are not found.
    % These were dropped because update to the code drops short duration
    % fragments.
    %
    % TODO This code still expects ES-test.csv and others (DataFrames, I
    % think) rather than list of indices.
    %
    % TODO This code still expects dummy.fss.
    idxTrain = intersect(features.Properties.RowNames, idxTrain);
    idxTest = intersect(features.Properties.RowNames, idxTest);
   
    featuresTrain = table2array(features(idxTrain, :));
    featuresTest = table2array(features(idxTest, :));

    createTrackListFromFragIds(pathTrackListTrain, idxTrain)
    createTrackListFromFragIds(pathTrackListTest, idxTest)

    % Find the rotation from the training data, then apply it to both the
    % training data and test data.
    findDimensionsModified(pathTrackListTrain, pathFssFile, ...
        featuresTrain, dirOutput);
    pathRotationSpec = strcat(dirOutput, "rotationSpec.mat");

    dirOutputRotationTrain = strcat(dirOutput, 'train/');
    rotatedTrain = applyNormRotModified(pathTrackListTrain, pathFssFile, ...
        dirOutputRotationTrain, featuresTrain, pathRotationSpec);
    
    dirOutputRotationTest = strcat(dirOutput, 'test/');
    rotatedTest = applyNormRotModified(pathTrackListTest, pathFssFile, ...
         dirOutputRotationTest, featuresTest, pathRotationSpec);
    
    % Save rotated features as CSV with PC numbers as columns and fragment
    % IDs as rows.
    pathOutputRotatedTrain = strcat(dirOutput, 'rotated-train-', ...
        langCode, '.csv');
    pathOutputRotatedTest = strcat(dirOutput, 'rotated-test-', ...
        langCode, '.csv');
    varNames = string(linspace(1, 100, 100));
    tableRotatedTrain = array2table(rotatedTrain, 'RowNames', idxTrain, ...
        'VariableNames', varNames);
    writetable(tableRotatedTrain, pathOutputRotatedTrain, ...
        'WriteRowNames', true);
    tableRotatedTest = array2table(rotatedTest, 'RowNames', idxTest, ...
        'VariableNames', varNames);
    writetable(tableRotatedTest, pathOutputRotatedTest, ...
        'WriteRowNames', true);
    
    % Plot the dimensions.
    % TODO Do not display figures while creating them.
    pathRotationSpec = strcat(dirOutput, 'rotationSpec.mat');
    diagramDimensionsModified(pathRotationSpec, dirOutput);

    fprintf('Done. Outputs written to: %s\n', dirOutput);
end

function idx = readIdxFromMetadata(pathMetadataCsv)
% READIDXFROMMETADATA Read DRAL short fragment metadata into a table and
% return its indices (fragment IDs).
%
% Input arguments:
%   pathMetadataCsv (char) - path to metadata CSV

    metadata = readFragsMetadataToTable(pathMetadataCsv);
    idx = metadata.Properties.RowNames;
end

function createTrackListFromFragIds(pathOutput, fragmentIds)
% CREATETRACKLISTFROMFRAGIDS Create a Mid-level Toolkit track list file
% from an array of DRAL fragment IDs and write to the specified output
% path. This track list should only be used in the PCA workflow since audio
% paths are not validated.
%
% Input arguments:
%   pathOutput (char) - path to write track list
%   fragmentIds (cell) - fragment IDs

    fileTrackList = fopen(pathOutput,'w');
    % Mid-level Toolkit GETTRACKLIST expects the file to start with a
    % directory. Any will do.
    fprintf(fileTrackList, './some-dir\n');
    fprintf(fileTrackList, '\n\n');
    side = 'l'; % Short fragment audios are always mono.
    for i = 1:length(fragmentIds)
        fragmentId = fragmentIds{i};
        fprintf(fileTrackList, '%s %s.wav\n', side, fragmentId);
    end
    fprintf(fileTrackList, '\n\n');
    fclose(fileTrackList);
end