function fragFeatureSet = getFragFeatureSet(fragDuration, ...
    fragStartTime, featureCodes, windowSpanPercentages)
% GETFRAGFEATURESET Create a Midlevel Toolkit feature set for a fragment of
% a single track audio. The feature set will contain one feature
% specification for each combination of base feature and non-overlapping
% window span specified. If the feature set is supplied to Midlevel Toolkit
% MAKETRACKMONSTER, the first row of the output 2D array `monster` contains
% the relevant fragment features. See the example below.
%
% Example:
%     Create a feature set for a fragment 5 seconds (5000 milliseconds) in
%     duration beginning 30 seconds (30000 milliseconds) into its source
%     audio.
%
%     fragFeatureSet = getFragFeatureSet(seconds(5), seconds(30), ...
%         ["vo", "le"], [20 60 20])
%     
%     `fragFeatureSet` is a 6x1 struct with 7 fields:
%
%     | featname | startms | endms | duration | side   | plotcolor | featnamefull |
%     | -------- | ------- | ----- | -------- | ------ | --------- | ------------ |
%     | 'vo'     | 30000   | 31000 | 1000     | 'self' | 0         | 'vo-0-20'    |
%     | 'vo'     | 31000   | 34000 | 3000     | 'self' | 0         | 'vo-20-80'   |
%     | 'vo'     | 34000   | 35000 | 1000     | 'self' | 0         | 'vo-80-100'  |
%     | 'le'     | 30000   | 31000 | 1000     | 'self' | 0         | 'le-0-20'    |
%     | 'le'     | 31000   | 34000 | 3000     | 'self' | 0         | 'le-20-80'   |
%     | 'le'     | 34000   | 35000 | 1000     | 'self' | 0         | 'le-80-100'  |
%     
%     The feature specifications in `fragFeatureSet`, in order, are:
%         - Volume from 0% to 20% into the fragment, or volume over the
%            first 1000 milliseconds of the fragment.
%         - Volume from 20% to 80% into the fragment, or volume over the
%            next 3000 milliseconds of the fragment.
%         - Volume from 80% to 100% into the fragment, or volume over the
%            last 1000 milliseconds of the fragment.
%         - Lengthening from 0% to 20% into the fragment, or lengthening
%            over the first 1000 milliseconds of the fragment.
%         - Lengthening from 20% to 80% into the fragment, or lengthening
%            over the next 3000 milliseconds of the fragment.
%         - Lengthening from 80% to 100% into the fragment, or lengthening
%            over the last 1000 milliseconds of the fragment.
%
%     Midlevel Toolkit MAKETRACKMONSTER computes each feature for windows
%     centered every 10 millisecond throughout the audio. The size of its
%     output 2D array `monster` is (number of frames)x(number of features).
%
%     All feature specification start times and end times in
%     `fragFeatureSet` are offset (shifted into the future) by the time
%     into the source audio the fragment begins. Thus, the first column of
%     `monster` will contain the relevant fragment features since the start
%     times and end times are relative to the first 10 millisecond frame.
%
%     The custom field `featnamefull` describes the base feature and window
%     span of each feature. COMPUTEFEATURES reads this field to combine
%     multiple fragments' features into a single view. While this field is
%     not added by Midlevel Toolkit MAKEFEATURESPEC or GETFEATURESPEC, it
%     has not interfered with other Midlevel Toolkit code in my testing.
%
%     The field `side` is always 'self' because the audio is assumed to be
%     single track. The field `plotcolor` is always 0 because I do not use
%     Midlevel Toolkit plotting.
%
% Input arguments:
%     * fragDuration (duration) - The duration of the fragment.
%     * fragStartTime (duration) - The time into the source audio the
%           fragment begins.
%     * featureCodes (string) - An array of Midlevel Toolkit base feature
%           codes. This argument is optional; its default value is
%           specified in the argument block.
%     * windowSpanPercentages (double) - An array of window span
%           percentages. Its sum must equal 100. This argument is optional;
%           its default value is specified in the argument block.
%
% Output arguments:
%     * fragFeatureSet (struct) - A structure array of feature 
%           specifications to supply to Midlevel Toolkit MAKETRACKMONSTER.
%
% TODO Specifying the input argument windowSpanPercentages does not work as
%     expected.

arguments
    fragDuration (1,1) duration
    fragStartTime (1,1) duration
    featureCodes (1,:) string = ["cr", "sr", "tl", "th", "wp", "np", "vo", "le", "cp", "pd"]
    windowSpanPercentages (1,:) double = [5 5 10 10 20 20 10 10 5 5]
end

assert(sum(windowSpanPercentages) == 100,...
    'Window span percentages sum must equal 100.');

startPercentages = cumsum([0, windowSpanPercentages(1:end-1)]);
endPercentages = cumsum(windowSpanPercentages);

% Get the feature start times and end times in milliseconds. Offset the
% start times and end times by the time into the source audio the fragment
% begins.
fragDuration_ms = milliseconds(fragDuration);
fragStartTime_ms = milliseconds(fragStartTime);
baseFeatStartTimes = fragDuration_ms * startPercentages * 0.01 + ...
    fragStartTime_ms;
baseFeatEndTimes = fragDuration_ms * endPercentages * 0.01 + ...
    fragStartTime_ms;

% Round the start times and end times to be a multiple of the milliseconds
% in a Midlevel Toolkit frame (10) to avoid errors downstream.
baseFeatStartTimes = round(baseFeatStartTimes, -1);
baseFeatEndTimes = round(baseFeatEndTimes, -1);

baseFeatDurations = baseFeatEndTimes - baseFeatStartTimes;

% The source audio is single track, so the side of focus is always 'self'.
side = 'self';

% No plotting is done, so the plot color is always 0.
plotColor = 0;

% Create the feature set struct by copying (repeating) the feature names,
% start times, end times, durations, side, and plot color. Create the field
% `featnamefull` by appending a feature's code, window start percentage,
% and window end percentage into a string with the format: <base
% code>-<start percentage>-<end percentage>.
nWindows = length(windowSpanPercentages);
nFeatures = length(featureCodes);
featNames = repelem(featureCodes, 1, nWindows);
featStartTimes = repmat(baseFeatStartTimes, 1, nFeatures);
featEndTimes = repmat(baseFeatEndTimes, 1, nFeatures);
featDurations = repmat(baseFeatDurations, 1, nFeatures);
featSides = repmat({side}, 1, nWindows * nFeatures);
featPlotColors = repmat(plotColor, 1, nWindows * nFeatures); %#ok<REPMAT> 
featFullNames = append(featureCodes, "-", string(startPercentages)', ...
    "-", string(endPercentages)');
fragFeatureSet = struct( ...
    'featname', num2cell(featNames), ...
    'startms', num2cell(featStartTimes), ...
    'endms', num2cell(featEndTimes), ...
    'duration', num2cell(featDurations), ...
    'side', featSides, ...
    'plotcolor', num2cell(featPlotColors), ...
    'featnamefull', num2cell(featFullNames(:)') ...
    )';
end
