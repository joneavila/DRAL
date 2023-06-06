function expectedLen = getExpectedFeatureVecLen(signal, sampleRate)
% GETEXPECTEDFEATUREVECLEN Returns the expected length of a Midlevel
% Toolkit feature vector, assuming there should be one value per 10 ms
% frame in `signal`.

midlevelFrameWidth_ms = 10;
signalDuration_s = length(signal) / sampleRate;
signalDuration_ms = signalDuration_s * 1000;

% Use floor, i.e. do not expect a value for the last frame if it is less
% than midlevelFrameWidth_ms in duration.
expectedLen = floor(signalDuration_ms / midlevelFrameWidth_ms);

end