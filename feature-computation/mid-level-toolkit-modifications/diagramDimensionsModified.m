function diagramDimensionsModified(pathRotationSpecFile, dirOutput)
% DIAGRAMDIMENSIONSMODIFIED Make loadings plots for each dimension and save
% them to files in the the specified output directory.
% While the code is short, it is terribly hard-coded.
% 
% Adapted from Mid-level Toolkit DIAGRAMDIMENSIONS, PATVIS2, and
% RESHAPEANDDECORATE
    
    % Load variables written by FINDDIMENSIONSMODIFIED.
    load(pathRotationSpecFile, 'pcCoeffs');  

    nDimsToPlotMax = 12;
    nDimsToPlot = min(nDimsToPlotMax, length(pcCoeffs));
    
    % Create a feature set for a dummy fragment, just to read the feature
    % codes and spans.
    featureSet = getFragFeatureSet(seconds(0), seconds(0));
    uniqueFeatureCodes = unique([featureSet(:).featname]);
    uniqueFeatureNames = arrayfun(@(x) baseFeatCodeToName(x), ...
        uniqueFeatureCodes, 'UniformOutput', false);
    
    dirOutputPlots = strcat(dirOutput, 'loadingplots');
    makeDirIfNotExists(dirOutputPlots);

    % TODO The number of subplots is hard-coded.

    % For each dimension.
    for dimNum = 1:nDimsToPlot
        
        % TODO This value is hard-coded and assumes the spans can neatly
        % align from 1 to 100.
        nValuesToExpandTo = 100;

        % For each dimension pole.
        dimPoles = struct('direction', {-1, 1}, 'name', {'low', 'high'});
        for dimPole = dimPoles

            fprintf('\tPlotting dimension %d %s\n', dimNum, dimPole.name);

            pathOutputPlot = sprintf('%s/dim%02d%s', dirOutputPlots, ...
                dimNum, dimPole.name(1:2));
            dimValues = dimPole.direction * pcCoeffs(:, dimNum);
            
            baseFeatPlotPos = [1 6 2 7 3 8 4 9 5 10];
            baseFeatCodes = ["vo" "pd" "sr" "le" "th" "tl" "np" "wp" "cp" "cr"];
            baseFeatCodeToPlotPos = dictionary(baseFeatCodes,baseFeatPlotPos);

            % For each base feature.
            for featureCodeNum = 1:length(uniqueFeatureCodes)

                featureCode = uniqueFeatureCodes(featureCodeNum);
                featureName = uniqueFeatureNames(featureCodeNum);

                % Capitalize first character and convert back to cell
                % array.
                featureNameChar = char(featureName);
                featureName = {strcat(upper(featureNameChar(1)), featureNameChar(2:end))};
                
                hasFeatureCode = arrayfun(@(x) strcmp(x, featureCode), ...
                    [featureSet.featname]);
                featureSubset = featureSet(hasFeatureCode, :);
                dimValuesWithFeatureCode = dimValues(hasFeatureCode);
    
                % Extend the values so that they appear proportional to
                % their span.
                dimValuesExpanded = zeros(1, nValuesToExpandTo);
                for featureNum = 1:length(featureSubset)
                    feature = featureSubset(featureNum);
                    [spanStart, spanEnd] = spansFromFeatureNameFull(feature.featnamefull);
                    dimValuesExpanded(spanStart:spanEnd) = dimValuesWithFeatureCode(featureNum);
                end
                
                colorGray = "#8C8C8C";
                colorBlack = "#000000";
                lineWidth = 1.75;

                x = linspace(1, nValuesToExpandTo);
                
                nPlotRows = 2;
                nPlotCols = 5;

                plotPos = baseFeatCodeToPlotPos(featureCode);
                subplot(nPlotRows, nPlotCols, plotPos);
                hold on

                % Draw line at zero.
                plot(x, zeros(1, nValuesToExpandTo), 'Color', ...
                    colorGray, 'LineWidth', lineWidth);

                % Plot loadings.
                plot(x, dimValuesExpanded, 'Color', colorBlack, ...
                    'LineWidth', lineWidth);
                
                % Add axes labels.
                % xlabel('Percentage into utterance');

                title(featureName)
                
                % Add Y padding.
                ylim('tight')
                maxY = max(abs(dimValuesWithFeatureCode));
                yLimitPaddingPercentage = 0.1;
                ylim([ ...
                    -maxY - maxY * yLimitPaddingPercentage, ...
                    maxY + maxY * yLimitPaddingPercentage ...
                    ])

                hold off
                
                % Hide Y ticks.
                set(gca,'yticklabel',[])
            end
        
        
        % Adjust figure size.
        figureHeight = 250;
        figureWidth = 850;
        set(gcf, 'position', [64, 64, figureWidth, figureHeight])
        
        % Add title.
        % plotTitle = sprintf('Dimension %d %s', dimNum, dimPole.name);
        % sgtitle(plotTitle)

        saveas(gcf, pathOutputPlot, 'png');
        clf;
        
        end
    end
end

function [spanStart, spanEnd] = spansFromFeatureNameFull(featureNameFull)
% Input arguments:
%   featureSet - Mid-level Toolkit feature set, spefically returned by
%   GETFRAGFEATURESET
    
    % The field `featnamefull` is a string containing the base feature
    % code, start span percentage, and end span percented, delimited by
    % hyphen.
    splitResult = split(featureNameFull, "-");
    spanStart = str2double(splitResult(2));
    spanEnd = str2double(splitResult(3));

    % A span can start at 0, e.g., intensity 0% through 5% of the duration,
    % but MATLAB does not like zero indices.
    if spanStart == 0
        spanStart = 1;
    end
    

end


    
