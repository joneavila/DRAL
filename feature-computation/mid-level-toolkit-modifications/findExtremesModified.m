function findExtremesModified(monsterRotated, dirOutput, provenance, ...
    pathTrackListFile)
% FINDEXTREMESMODIFIED For each dimension, find and write places with very
% high or very low value.
%
% Input arguments:
%   monsterRotated (double) - features after applying rotation
%   dirOutput (char) - directory to write outputs to
%   provenance (char) - provenance string
%   pathTrackListFile (char) - path to Mid-level Toolkit track list file
%       (.tl)
%
% This is a modified Mid-level Toolkit FINDEXTREMES, with modifications:
%   - Remove input argument for specifying track side, since all tracks
%       (fragments) are mono.
%   - Remove input argument for specifying track. Replace with input
%       argument for specifying path to track list file.
%   - Remove appending to output extremes file. Force overwrite.
%   - Remove code related to timepoints.

    trackList = gettracklist(pathTrackListFile);
    if ~exist(dirOutput, 'dir')
        warning('Output directory %s not found. Skipping write.', ...
            dirOutput);
        return
    end
    
    [~, nDimensions] = size(monsterRotated);
    
    nDimensionsToWriteMax = 25;
    nDimensionsToWrite = min(nDimensionsToWriteMax, nDimensions);
    
    stddevs = std(monsterRotated(:, 1:nDimensionsToWrite));
    
    for dimensionNum = 1:nDimensionsToWrite
        outputFilename = sprintf('dim%.2d.txt', dimensionNum);
        outputPath = strcat(dirOutput, outputFilename);   
        outputFile = fopen(outputPath, 'w');

        dimensionSlice = monsterRotated(:,dimensionNum);
        % The original code called INDICESOFSEPARATEDMAXIMA, but here each
        % track is a fragment, so it's okay if the maxima are close.
        [~, maxIndices] = sort(dimensionSlice, 'descend');
        [~, minIndices] = sort(dimensionSlice, 'ascend');
        % maxIndices = indicesOfSeparatedMaxima(dimensionSlice);
        % minIndices = indicesOfSeparatedMaxima(-1 * dimensionSlice);
        
        fprintf(outputFile, '%s\n', provenance);
        fprintf(outputFile, 'Low\n');
        writeExtrema(outputFile, minIndices, dimensionNum, ...
            monsterRotated, stddevs, trackList);
        fprintf(outputFile, 'High\n');
        writeExtrema(outputFile, maxIndices, dimensionNum, ...
            monsterRotated, stddevs, trackList);
        fclose(outputFile);
    end  
end

function  writeExtrema(outputFile, indices, dimNum, monsterRotated, ...
    stddevs, tracklist)

    numOfExtremesPerTrack = 20;
    for i = 1:numOfExtremesPerTrack
        index = indices(i);
        actualValue = monsterRotated(index, dimNum);
        track = tracklist{index};
        lineToWrite = sprintf('  %2d %.1f in %s', dimNum, actualValue, ...
            track.filename);
        fprintf(outputFile, lineToWrite);
        writeSalientDims(outputFile, monsterRotated(index,:), stddevs);
        fprintf(outputFile, '\n');
    end
end

function writeSalientDims(outputFile, values, stddevs)
% WRITESALIENTDIMS (Original documentation.) If the current dimension value
% is not on this list, but other dimensions are then this timepoint is a
% better example of something else, than it is of this dimension.
    displayThreshold = 2.5;
    ndims = min(15, size(stddevs, 2));
    values = values(1:ndims);
    stddevs = stddevs(1:ndims);
    infoString = ' bigdims: ';
    salientIndices = abs(values) > displayThreshold * stddevs;
    
    for dim = 1:ndims
        if salientIndices(dim) 
            infoString = strcat(infoString, ' ', ...
                sprintf(' dim%2d %.1f ', dim, values(dim)));
        end
    end
    fprintf(outputFile, infoString);
end