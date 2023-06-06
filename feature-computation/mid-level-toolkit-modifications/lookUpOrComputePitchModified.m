function paddedPitch = ...
    lookUpOrComputePitchModified(trackDirectory, trackFilename, signal, sampleRate)
% LOOKUPORCOMPUTEPITCHMODIFIED Return a vector of pitch points and a vector
% of where they are, in ms.

% This function is modified from Mid-level Toolkit LOOKUPORCOMPUTEPITCH
% with the following changes:
%   * Remove fallback to fxrapt. Instead read REAPER F0 files else raise an
%     error.
%   * Remove FILE1ISOLDER function since they were only used when falling
%     back to fxrapt.
%   * Remove code relate to separate channels and assume input file is mono
%   * Assume no "trimmable" files.
%   * Remove PADDEDCENTERS output argument since it is not used by
%     GETLOWLEVEL.
%   * Add padding so that PADDEDPITCH matches expected length.

% REAPER F0 files are expected in a subdirectory named "f0reaper", in the
% same directory containing the audio. The audio's REAPER F0 file is
% expected to have the same basename.
[~,audioFileBase,~] = fileparts(trackFilename);
reaperF0Dir = [trackDirectory 'f0reaper'];
reaperFile =  sprintf('%s.txt', audioFileBase);
reaperPath =  [reaperF0Dir '/' reaperFile];
if ~exist(reaperPath, 'file')
    error('REAPER F0 file not found. Try running reaper_on_dir.sh. For more information, see its documentation.');
end

% Read the REAPER file into a matrix. Ignore the first 7 lines containing 
% the header:
% ```
% EST_File Track
% DataType ascii
% NumFrames ...
% NumChannels ...
% FrameShift ...
% VoicingEnabled ...
% EST_Header_End
% ```
reaperMatrix = readmatrix(reaperPath, 'NumHeaderLines', 7);

% The first row is the reported pitch at 0ms. The first row should be the
% reported pitch frame at 10ms, so discard the first row.
reaperMatrix(1,:) = [];

% Convert time column (first column) from seconds to milliseconds.
reaperMatrix(:, 1) = reaperMatrix(:, 1) .* 100;
reaperMatrix(:, 1) = round(reaperMatrix(:, 1));

% Get the time of the last reported pitch and check whether it matches the
% total number of reported frames.
timeOfLastF0frameMs = reaperMatrix(end, 1);
nF0frames = height(reaperMatrix);
if timeOfLastF0frameMs < nF0frames
    error('REAPER F0 file has less reported pitch values than reported frames.')
end
if timeOfLastF0frameMs > nF0frames
    error('REAPER F0 file has more reported pitch values than reported frames.')
end

% Get the reported pitch values from the third column.
pitch = reaperMatrix(:, 3);

% Reported pitch values are -1 if no pitch. Replace these values with NaN.
pitch(pitch == -1) = NaN;

pitchLength = length(pitch);
expectedPitchLength = getExpectedFeatureVecLen(signal, sampleRate);

paddedPitch = pitch;

% If the length of the pitch vector is less than the expected length, then
% REAPER did not report a pitch value for some frames.
if pitchLength < expectedPitchLength

    % If the missing reported pitch values belong to the last frames, it's
    % likely because the audio ends with silence. Pad the end of the pitch
    % vector with NaN.
    if timeOfLastF0frameMs == nF0frames
        paddingNeeded = expectedPitchLength - pitchLength;
        paddedPitch = [pitch; NaN(paddingNeeded, 1)];

    % If the missing reported pitch values belong to some other frames,
    % there's a problem to diagnose.
    else
        error('pitch length is less than expected length.')
    end
    
end

% If the length of the pitch vector is greater than the expected length,
% there's a problem to diagnose.
if pitchLength > expectedPitchLength
    error('pitch length is grater than expected length.')
end

return