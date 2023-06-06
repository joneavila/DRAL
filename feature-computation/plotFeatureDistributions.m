function plotFeatureDistributions()
% PLOTFEATUREDISTRIBUTIONS Plot an overlayed histogram (EN vs. ES) for
% each feature (computed with COMPUTEFEATURES), with outlier percentages
% in the legent, and save as an image to an output directory.

    pathFeaturesEN = '/Users/jon/Documents/dissertation/DRAL-corpus/release/features/EN-features.csv';
    pathFeaturesES = '/Users/jon/Documents/dissertation/DRAL-corpus/release/features/ES-features.csv';
    
    opts = detectImportOptions(pathFeaturesEN);
    
    % Set some import options that are not detected properly.
    opts.RowNamesColumn = 1;
    opts.SelectedVariableNames = 2:101;
    
    featuresEN = readtable(pathFeaturesEN, opts);
    featuresES = readtable(pathFeaturesES, opts);
    
    % Standardize.
    % featuresEN = normalize(featuresEN);
    % featuresES = normalize(featuresES);
    
    dirOutput = 'feature-distribution-plots-new';
    makeDirIfNotExists(dirOutput);
    
    % For each feature.
    varNames = featuresEN.Properties.VariableNames;
    for varNum = 1:length(varNames)
    
        varName = varNames(varNum); % e.g. 'cr-0-50'
    
        % Get the base feature name from the variable name.
        varNameSplit = split(varName, '_');
        baseFeatCode = varNameSplit{1}; % e.g. 'cr'
        baseFeatName = baseFeatCodeToName(baseFeatCode); % e.g. 'creakiness'
    
        varEN = featuresEN{:, varName};
        varES = featuresES{:, varName};
    
        % "MAD is defined as c*median(abs(A-median(A))), where
        % c=-1/(sqrt(2)*erfcinv(3/2))."
        % https://www.mathworks.com/help/matlab/ref/isoutlier.html
        outliersPercentageMedianEN = getOutliersPercentage(varEN, 'median');
        outliersPercentageMedianES = getOutliersPercentage(varES, 'median');
        
        % "elements more than three standard deviations from the mean. This
        % method is faster but less robust than 'median'."
        % https://www.mathworks.com/help/matlab/ref/isoutlier.html
        outliersPercentMeanEN = getOutliersPercentage(varEN, 'mean');
        outliersPercentMeanES = getOutliersPercentage(varES, 'mean');
    
        displayNameEN = sprintf(['EN (%.1f%% median outliers, %.1f%% mean '...
            'outliers)'], outliersPercentageMedianEN, outliersPercentMeanEN);
        displayNameES = sprintf(['ES (%.1f%% median outliers, %.1f%% mean '...
            'outliers)'], outliersPercentageMedianES, outliersPercentMeanES);
    
        histogram(varEN, 'DisplayName', displayNameEN);
        hold on; % Hold on to overlay the next histogram.
        histogram(varES, 'DisplayName', displayNameES);
    
        legend;
        % Escape hyphens in the variable name to display it properly.
        varNameEscaped = strrep(varName, '_', '\_');
        title(varNameEscaped);
        xlabel(baseFeatName);
        ylabel('count');
    
        % Write the figure as a .fig to the output directory.
        outputFigPath = strcat(dirOutput, '/', varName, '.fig');
        savefig(gcf, char(outputFigPath))
    
        % Write the figure as a .jpg to the output directory.
        outputImagePath = strcat(dirOutput, '/', varName, '.jpg');
        saveas(gcf, char(outputImagePath))
    
        hold off; % Hold off to clear for next histogram.
    
    end

end

function percentOutliers = getOutliersPercentage(featureArr, method)
    isOutlier = isoutlier(featureArr, method);
    numOutliers = sum(isOutlier);
    percentOutliers = numOutliers / length(featureArr) * 100;
end