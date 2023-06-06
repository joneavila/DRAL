function trackSpec = makeMonoTrackSpec(audioPath)
% MAKEMONOTRACKSPEC Returns a Midlevel Toolkit track specification
% for a mono audio.
%
%   Input arguments:
%       audioPath (char) - The path to the audio.
%
%   Output arguments:
%       trackSpec (struct) - A track specification returned by Midlevel
%       Toolkit MAKETRACKSPEC.
%
%   See also MAKETRACKSPEC.

% Audio is mono, so the side of focus is always 'l'.
side = 'l';

[filepath, name, ext] = fileparts(audioPath);

% For example, `filename` is 'EN_001r.wav'.
filename = append(name, ext);

% For example, `directory` is './release/fragments-concatenated/'.
directory = append(filepath, '/');

trackSpec = makeTrackspec(side, filename, directory);

end