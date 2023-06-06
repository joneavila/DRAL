function computeFeatures()
% COMPUTEFEATURES Compute prosody representations of DRAL English and
% Spanish short fragments pairs, and write table as CSV with features as
% columns and fragment IDs as rows.
%
% [!] This function is part of a workflow described in
%     ../DRAL-corpus/README.md.
%
% [!] This function calls many functions defined in scripts in its parent
%     directory, including functions from the Mid-level Toolkit. Add
%     these directories to MATLAB's search path before running it.
%
% [!] Some paths are relative. Run this function with the project root
%     directory as the working directory.
%
% Fragments are processed in the order they appear in the metadata.
% Low-level features of source conversations are redundantly re-computed. I
% tried separating low-level and mid-level code before, but the two are
% strongly tied.

    warning(['The Mid-level Toolkit creates cache directories ' ...
        '(''cppsCache'') in the same directories containing the audio ' ...
        'data. If the audio data has changed, delete these directories.'])

    warning(['The function LOOKUPORCOMPUTEPITCHMODIFIED creates cache ' ...
        'directories (''f0reaper'') in the same directories ' ...
        'containing the audio data. If the audio data has changed, ' ...
        'delete these directories.'])
    
    dirRelease = '/Users/jon/Documents/dissertation/DRAL-corpus/release/';

    pathInputMetadata = strcat(dirRelease, 'fragments-short-matlab.csv');

    dirOutput = strcat(dirRelease, 'features/');
    makeDirIfNotExists(dirOutput);
    
    % Read the metadata CSV into a table.
    fragsTable = readFragsMetadataToTable(pathInputMetadata);

    % Preallocate a table for the computed features. The rows (fragments)
    % are known but the columns (features) are not. Create a feature set
    % for a dummy fragment to read its feature names.
    dummyFeatureSet = getFragFeatureSet(seconds(0), seconds(0));
    tableRowNames = fragsTable.Properties.RowNames;
    tableVarNames = [dummyFeatureSet.featnamefull];    
    tableVarTypes = repmat("double", 1, length(tableVarNames));
    tableSize = [length(tableRowNames), length(tableVarNames)];
    tableArgs = {'Size', tableSize, 'VariableTypes', tableVarTypes, ...
        'RowNames', tableRowNames, 'VariableNames', tableVarNames};
    featuresTable = table(tableArgs{:});

    % Create a progress bar figure to display during the main loop.
    fprintf('Computing features. See progress figure.\n');
    progressFig = waitbar(0, '', 'Name', 'Computing features...');
    
    % For each row (fragment).
    nFrags = height(fragsTable);
    for fragNum = 1:nFrags

        fragID = string(fragsTable(fragNum, :).Properties.RowNames); % This feels hacky. 
    
        % Update the progress bar figure with the fragment ID, e.g.,
        % "EN_016_39 (26 of 2092)". Escape underscores in the ID to display
        % it properly.
        displayFragID = strrep(fragID, '_', '\_');
        displayString = sprintf('%s (%d of %d)', displayFragID, fragNum, nFrags);
        waitbar(fragNum/nFrags, progressFig, displayString);
        
        % Compute the features and insert into table.
        fragFeatures = computeFragFeatures( ...
            fragsTable{fragID, 'concat_audio_path'}, ...
            fragsTable{fragID, 'duration'}, ...
            fragsTable{fragID, 'time_start_rel'} ...
        );
        featuresTable(fragID, :) = num2cell(fragFeatures);

    end
    
    % Close the progress bar figure.
    delete(progressFig);
    
    % Write the table as CSV.
    writetable(featuresTable, strcat(dirOutput, 'features.csv'), ...
        'WriteRowNames', true);

    fprintf('Done. Output written to: %s\n', dirOutput);


end

function fragFeatures = computeFragFeatures(pathConvAudio, ...
    fragDuration, fragStartTime)
    
    fragFeatureSet = getFragFeatureSet(fragDuration, fragStartTime);
    trackSpec = makeMonoTrackSpec(pathConvAudio);

    [~, monster] = makeTrackMonsterModified(trackSpec, fragFeatureSet);

    % The first row of `monster` contains the relevant fragment 
    % features. For more information, see GETFRAGFEATURESET.
    fragFeatures = monster(1,:);
end