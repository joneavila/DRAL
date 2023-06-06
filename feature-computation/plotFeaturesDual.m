% @February 22, 2023 This is a modified version of PLOTFEATURES, with
% changes to display to fragments. Written to create figures in Interspeech
% paper.
%
% [!] The features' Y-axis minimum and maximum are relative to the values
%     being displayed, not relative to the entire `monster` (return value
%     of MAKETRACKMONSTER).


% Config.
fragID1 = 'EN_013_34';
fragID2 = 'ES_013_34';
baseFeatureSelected = 'cp';

% featureName = baseFeatCodeToName(baseFeatureSelected);
% Temporary, use a hardcoded name instead.
featureName = "CPPS";

[x1, y1] = getFeatureData(fragID1, baseFeatureSelected);
[x2, y2] = getFeatureData(fragID2, baseFeatureSelected);

f = figure;
f.Position = [100 100 600 250];

colorBlack = "#000000";
c1 = plot(x1, y1);



c1.Color = colorBlack;

c1.LineWidth = 2;
hold on
c2 = plot(x2, y2);
c2.Color = colorBlack;
c2.LineWidth = 2;
c2.LineStyle = "--";
axesFontSize = 18;
legendFontSize = 14;
% xlabel('Percentage into duration', 'FontSize', axesFontSize)
% ylabel(featureName, 'FontSize', axesFontSize)
xlabel('Percentage into duration')
ylabel(featureName)

fragID1escaped = strrep(fragID1, '_', '\_');
fragID2escaped = strrep(fragID2, '_', '\_');
legend(fragID1escaped, fragID2escaped, 'FontSize', legendFontSize);

ax = gca;
ax.FontSize = 18;

% ymax = max(max(y1), max(y2));
% ymin = min(min(y1), min(y2));
% newYmax = ymax + ymax * 0.05;
% newYmin = ymin + ymin * 0.05;
% ax.YLim = [0 350];

outputFilename = sprintf("%s-%s-%s.png", fragID1, fragID2, featureName);
saveas(f, outputFilename)
fprintf("Figure saved to: %s", outputFilename)

function [x, y] = getFeatureData(fragID, baseFeatureCode)

    % Read the metadata CSV into a table.
    DRALreleaseDir = '/Users/jon/Documents/dissertation/DRAL-corpus/release/';
    inputMetadataCSVpath = strcat(DRALreleaseDir, ...
        'fragments-short-matlab.csv');
    fragsTable = readFragsMetadataToTable(inputMetadataCSVpath);
    
    frag = fragsTable(fragID, :);
    
    fragSourceAudioPath = string(frag.concat_audio_path);
    
    % TODO Temporary fix.
    fragSourceAudioPath = strrep(fragSourceAudioPath, 'prosody_project', 'dissertation');
    fragSourceAudioPath = strrep(fragSourceAudioPath, 'DRAL', 'DRAL-corpus');
    fragSourceAudioPath = convertStringsToChars(fragSourceAudioPath);
    
    % Compute the fragments' features.
    fragFeatureSet = getFragFeatureSet(frag.duration, frag.time_start_rel);
    trackSpec = makeMonoTrackSpec(fragSourceAudioPath);
    [~, monster] = makeTrackMonsterModified(trackSpec, fragFeatureSet);
    
    % For DRAL fragments, the frame of focus is always the first. For more
    % information, see GETFRAGFEATURESET.
    frameOfFocus = 1;
    
    fragFeatures = monster(frameOfFocus,:);
    count = 1;
    extended = zeros(1, 100);
    spans = [5 5 10 10 20 20 10 10 5 5];
    sumSpans = cumsum(spans);
    idxStart = 1;
    for featNum = 1:length(fragFeatureSet)
        feat = fragFeatureSet(featNum);
        if ~strcmp(feat.featname, baseFeatureCode)
            continue
        end
        featureValue = fragFeatures(1, featNum);
        idxEnd = sumSpans(count) + 1;
        extended(idxStart:idxEnd) = featureValue;
        idxStart = idxEnd + 1;
        count = count + 1;
    
    end
    y = extended(1:100);
    x = linspace(1, 100, 100);

end