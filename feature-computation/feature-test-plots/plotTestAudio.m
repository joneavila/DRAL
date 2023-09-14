function plotTestAudio()
% PLOTTESTAUDIO Plot test audio mid-level features for analysis.
% 
% The test audio contains fragments that should measure low or high for
% different base features in one or more regions. The fragments are marked
% up in ELAN in a tier "fragment" with empty values. The regions of low or
% high extremes for a base feature are marked up in a tier "extreme" with
% values following the format "<base-feature-code>-(low,high)", e.g.
% "wp-high". Regions with more than one low or high extreme are marked up
% with values containing commas, e.g. "wp-high,np-low".
%
% This function reads the test audio and computes its low-level features
% with lookUpOrGetLowLevel and for each of its fragments computes its
% mid-level features with getSummaryMidLevelForFrag. For each region of low
% or high extreme, this function plots the fragment mid-level features and
% highlights the region of the extreme.

audioPath = './feature-validation/test-audio-mono-downsampled.wav';
markupPath = './feature-validation/test-audio-mono-downsampled.txt';

outputDir = './figures';
makeDirIfNotExists(outputDir);

markupTable = readELANtoTable(markupPath);

% Markups in the tier "fragment". 
fragmentRows = markupTable(strcmp(markupTable.tier, 'fragment'), :);

% Markups in the tier "extreme".
extremesRows = markupTable(strcmp(markupTable.tier, 'extreme'), :);

midLevelFrameWidth_ms = 10;

nFragmentRows = height(fragmentRows);

% For each fragment (row in fragmentRows).
for fragRowNum = 1:nFragmentRows

    fragment = fragmentRows(fragRowNum, :);

    % Print progress.
    fprintf('%d/%d\n', fragRowNum, nFragmentRows);

    % Find the regions of extremes (row in extremesRows) within this
    % fragment.
    extremesRowsInFrag = extremesRows( ...
        all([extremesRows.startTime >= fragment.startTime, ...
        extremesRows.endTime <= fragment.endTime], 2), :);

    % The fragment start time will appear in output paths. Replace colons
    % (invalid character) with dashes.
    fragStartTimeFormatted = replace(string(fragment.startTime), ':', '-');

    % For each region of extremes within this fragment.
    for extremesRowInFragRowNum = 1:height(extremesRowsInFrag)

        extremesInFrag = extremesRowsInFrag(extremesRowInFragRowNum, :);

        % Split on commas, when one region measures multiple extremes.
        extremesInExtreme = split(extremesInFrag.value, ',');
        
        % For each extreme in the region.
        for extremeInExtremesNum = 1:length(extremesInExtreme)

            extreme = extremesInExtreme{extremeInExtremesNum};

            % Split on dash to get the feature base code and type of
            % extreme (low or high).
            markupValueSplit = split(extreme, '-');
            featBaseCode = markupValueSplit{1};
            extremeType = markupValueSplit{2};
    
            featureName = baseFeatCodeToName(featBaseCode);
            
            % Get a feature set with just this base feature.
            fragFeatureSet = getFeatureSetForFrag(fragment.duration, ...
                string(featBaseCode));
    
            % Get the summary features (one value per feature) for the
            % fragment.
            fragSummaryMidLevelFeats = getSummaryMidLevelForFrag( ...
                audioPath, fragment.startTime, fragment.endTime, ...
                fragFeatureSet);
            
            % Get the extended summary features (one value per 10 ms) for
            % the fragment.
            fragExtendedMidLevelFeats = extendSummaryMidLevelFeats( ...
                fragFeatureSet, fragSummaryMidLevelFeats);
    
            % The x-axis starts at the time into the audio the fragment
            % begins and ends at the time into the audio the fragment ends,
            % with 10 ms increments.
            X =  milliseconds(1:length(fragExtendedMidLevelFeats)) * ...
                midLevelFrameWidth_ms + fragment.startTime;
    
            % Plot the extended summary features.
            plot(X, fragExtendedMidLevelFeats, 'black');
    
            hold on;
    
            % Fill the region of extreme with yellow, a bit transparent,
            % for highlight.
            minX = extremesInFrag.startTime;
            maxX = extremesInFrag.endTime;
            ax = gca;
            minY = ax.YLim(1);
            maxY = ax.YLim(end);
            X = [minX minX maxX maxX];
            Y = [minY maxY maxY minY];
            patch(X, Y, 'yellow', 'FaceAlpha', 0.2, 'EdgeColor', 'none');
    
            % Add a title with the base feature name and the extreme type.
            title(sprintf('%s %s region', featureName, extremeType));
            
            % Add a subtitle with the audio path.
            subtitle(audioPath);
    
            % Add axes labels.
            xlabel('time');
            ylabel(featureName);

            % Write figure as .fig to output directory.
            outputPathFig = sprintf('%s/%s-%s.fig', outputDir, ...
                fragStartTimeFormatted, extreme);
            savefig(outputPathFig)
            
            % Write figure as .png to output directory.
            outputPathPng = sprintf('%s/%s-%s.png', outputDir, ...
                fragStartTimeFormatted, extreme);
            saveas(gcf, outputPathPng)
            
            hold off;

        end

    end

end