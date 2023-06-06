function rotated = applyNormRotModified(pathTracklistFile, ...
    pathFssFile, dirOutput, monster, pathRotationSpec)
% APPLYNORMROTMODIFIED Apply pre-saved normalization and rotation to the
% specified files.
%
% Input arguments:
%   pathTrackListFile (char) - path to Mid-level Toolkit track list file
%       (.tl)
%   pathFssFile (char) - path to Mid-level Toolkit feature set
%       specification file (.fss)
%   dirOutput (char) - directory to write outputs to
%   monster (double) - pre-computed features
%
% This is a modified Mid-level Toolkit APPLYNORMROT, with modifications:
%   - Add input argument for specifying output directory. Write outputs to
%       this directory.
%   - Replace NORMROTONEABLATIONS with NORMROTONEABLATIONSMODIFIED. Remove
%       code for processing one track at a time, since here a "track" is
%       really a DRAL fragment or utterance.
%   - Replace discouraged DATESTR with DATETIME.
%   - Replace discouraged CSVWRITE with WRITEMATRIX.
%   - Replace IF and MKDIR with MAKEDIRIFNOTEXISTS.
%   - Add variable names in LOAD.
%   - Replace output argument `allRotated` with `rotated`. Why?

    % Load the variables saved by FINDDIMENSIONSMODIFIED (saved to the same
    % output directory).
    % pathRotationSpec = strcat(dirOutput, "rotationSpec.mat");
    load(pathRotationSpec, "pcCoeffs", "monsterMeans", "monsterStds", ...
        "rotationProvenance")

    featureSetSpec = getfeaturespec(pathFssFile);

    dirOutputExtremes = strcat(dirOutput, 'extremes/');
    makeDirIfNotExists(dirOutputExtremes);

    dirOutputPcFiles = strcat(dirOutput, 'pcfiles/');
    makeDirIfNotExists(dirOutputPcFiles);
    
    provenance = sprintf(['Generated from track list:\n\t%s\nUsing ' ...
        'features:\n\t%s\nAnd rotation:\n\t%s\nAt:\n\t%s'], ...
        pathTracklistFile, pathFssFile, rotationProvenance, ...
        datetime('now'));
    
    rotated = normRotOneAblationsModified(pathTracklistFile, ...
        featureSetSpec, monsterMeans, monsterStds, pcCoeffs, provenance, ...
        dirOutputExtremes, monster);
    
    sigmas = std(rotated);
    pathOutputSigmas = strcat(dirOutput, 'sigmas.csv');
    writematrix(sigmas, pathOutputSigmas);

end