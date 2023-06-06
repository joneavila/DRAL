function findDimensionsModified(pathTrackListFile, pathFssFile, ...
    monster, dirOutput)
% FINDDIMENSIONSMODIFIED A modified Mid-level Toolkit FINDDIMENSIONS
% specific to DRAL's feature computation.
%
% Input arguments:
%   - pathTrackListFile (char) - Path to Mid-level Toolkit track list file    
%       (.tl)
%   - pathFssFile (char) - Path to Mid-level Toolkit feature set
%       specification file (.fss)
%   - monster (double) - Pre-computed features, returned by COMPUTEFEATURES
%   - dirOutput (char) - Directory to write outputs to

    featureSetSpec = getfeaturespec(pathFssFile);
    
    % Standardize (z-normalize) pre-computed features. `monsterNormalized`
    % has shape (n, p), where n is the number of observations (fragments)
    % and p is the number of variables (features).
    monsterMeans = mean(monster);
    monsterStds = std(monster);
    monsterNormalized = (monster - monsterMeans(:)') ./ monsterStds;
    
    % The call to WRITECORRELATIONS was removed since this is handled by
    % the Python code.
    % corrCoeffs = corrcoef(monster);
    % writeCorrelations(corrCoeffs, struct2cell(featureSetSpec), ...
    %     dirOutput, 'correlations.txt');
    
    % `pcCoeffs` (loadings) has shape (p, p). Each column contains the
    % coefficients for one principal component and are in descending order
    % of variance.
    [pcCoeffs, ~, pcVariances] = pca(monsterNormalized);
    
    % A string to include in various output files.
    rotationProvenance = sprintf(['Rotation generated from ''%s'', ' ...
        'using features ''%s'', at %s '], pathTrackListFile, ...
        pathFssFile, datetime('now'));
    
    % Save variables to load later.
    pathOutputRotationSpec = strcat(dirOutput, "rotationSpec.mat");
    save(pathOutputRotationSpec, "monsterMeans", "monsterStds", ...
        "pcCoeffs", "pcVariances", "rotationProvenance", ...
        "featureSetSpec", "pathFssFile")
    
    writeVarExplainedModified(pcVariances, dirOutput);

end