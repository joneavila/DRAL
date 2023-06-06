function monsterRotated = normRotOneAblationsModified(pathTracklistFile, ...
    featureSetSpec, monsterMeans, monsterStds, pcCoeffs, provenance, ...
    dirExtremes, monster)
% NORMROTONEABLATIONSMODIFIED
%
% Input arguments:
%   pathTrackListFile (char) - path to Mid-level Toolkit track list file
%       (.tl)
%   featureSetSpec (struct) - Mid-level Toolkit feature set specification
%   monsterMeans (double) - feature means
%   monsterStds (double) - feature STDs
%   pcCoeffs (double) - principal component coefficients, returned by
%       MATLAB PCA
%   provenance (char) - provenance string
%   dirExtremes (char) - path to directory containing extremes
%   monster (double) - pre-computed features
%
% This is a modified Mid-level Toolkit NORMROTONEABLATIONS, with
% modifications:
%   - Add input argument for pre-computed features. Remove feature
%       computation code.
%   - Remove input argument for specifying track feature specification.
%       Replace with input argument for specifying path to track list file.
%   - Remove unused input argument for specifying PC files directory.
%   - Remove dead code. Replace unused variables with ~.
%   - Replace for-loop with vector operations.
%   - Replace FPRINTF with WARNING when printing warnings.
%   - Remove check if extremes directory contains files. Force overwrite.
    
    fprintf('Applying norm+rot+ablations to %s... \n', pathTracklistFile);
    
    nFeatures = size(featureSetSpec, 2);
    nMonsterMeans = size(monsterMeans, 2);
    if nFeatures ~= nMonsterMeans
        fprintf('featureSetSpec has size %d %d\n', size(featureSetSpec));
        fprintf('monster has size %d %d\n', size(monster));
        fprintf('monsterMeans has size %d %d\n', size(monsterMeans));
        fprintf('monsterStds has size %d %d\n', size(monsterStds));
        fprintf(['Probably a mismatch between rotationSpec.m and the ' ...
            'feature list file\n']);
    end
    
    % Normalize with pre-saved means and STDs.
    monsterNormalized = (monster - monsterMeans(:)') ./ monsterStds;
    
    % Do the rotation.
    [~, nFeaturesInMonsterNormalized] = size(monsterNormalized);
    [nFeaturesInCoeffs, ~] = size(pcCoeffs);
    if (nFeaturesInMonsterNormalized ~= nFeaturesInCoeffs)
        % TODO Replace with error, since the code should probably not
        % continue.
        warning(['nFeaturesInMonsterNormalized ~= nFeaturesInCoeffs: '
            '%d ~= %d'], nFeaturesInMonsterNormalized, nFeaturesInCoeffs);
    end
    
    monsterRotated = monsterNormalized * pcCoeffs;

    findExtremesModified(monsterRotated, dirExtremes, provenance, ...
        pathTracklistFile);   

end