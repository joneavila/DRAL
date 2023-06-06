function writeVarExplainedModified(pcVariances, dirOutput)
% WRITEVAREXPLAINEDMODIFIED
%
% Input arguments:
%   pcVariances (double) - principal component variances returned by MATLAB
%       PCA
%   dirOutput (char) - directory to write output to
%
% This is a modified Mid-level Toolkit WRITEVAREXPLAINED, with
% modifications:
%   - Add input argument for specifying output directory. Write output
%       files to this directory.
%   - Remove dead code.
  
    variancePerDim = pcVariances ./ sum(pcVariances);
    cummulativeVarExplained = cumsum(pcVariances) ./ sum(pcVariances);
    
    pathOutputFile = strcat(dirOutput, 'variance.txt');
    fileOutput = fopen(pathOutputFile, 'w');
    fileHeader = 'dim  variance cumulative variance\n';
    fprintf(fileOutput, fileHeader);
    for dimNum = 1:min(length(pcVariances), 20)
        lineToWrite = sprintf('%2d    %5.2f   %5.2f\n', dimNum, ...
            variancePerDim(dimNum), cummulativeVarExplained(dimNum));
        fprintf(fileOutput, lineToWrite);
    end
    fclose(fileOutput);

end