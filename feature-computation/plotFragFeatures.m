function plotFragFeatures()
% PLOTFRAGFEATURES Plot a DRAL short fragment's features using PLOTFEATURES.

% TODO Paths to audios have changed after renaming the parent directory.

    % The fragment to plot.
    fragID = 'EN_033_11';

    % Path to the input metadata CSV, created by concatenate_fragments.py.
    DRALreleaseDir = '/Users/jon/Documents/dissertation/DRAL-corpus/release/';
    inputMetadataCSVpath = strcat(DRALreleaseDir, ...
        'fragments-short-matlab.csv');
    
    % Read the metadata CSV into a table.
    fragsTable = readFragsMetadataToTable(inputMetadataCSVpath);

    frag = fragsTable(fragID, :);

    fragSourceAudioPathStr = string(frag.concat_audio_path);

    % Compute the fragment's features.
    % TODO This code is duplicated in GETFRAGFEATURES.
    fragFeatureSet = getFragFeatureSet(frag.duration, frag.time_start_rel);
    trackSpec = makeMonoTrackSpec(fragSourceAudioPathStr);
    [~, monster] = makeTrackMonsterModified(trackSpec, fragFeatureSet);

    [sourceSignal, sampleRate] = audioread(fragSourceAudioPathStr);

    % For DRAL fragments, the frame of focus is always the first. For more
    % information, see GETFRAGFEATURESET.
    frameOfFocus = 1;

    plotFeatures(sourceSignal, sampleRate, fragFeatureSet, monster, ...
        frameOfFocus, fragID);

end
