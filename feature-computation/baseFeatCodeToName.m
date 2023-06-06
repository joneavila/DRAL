function baseFeatName = baseFeatCodeToName(baseFeatCode)
% BASEFEATCODETONAME Returns the full name of a Midlevel Toolkit base
% feature code.
%
% Input arguments:
%     * baseFeatCode (char) - A Midlevel Toolkit base feature code, e.g.
%           'cr'.
%
% Output arguments:
%     * baseFeatName (char) - The full name of the base feature with code 
%           `baseFeatCode`.

baseFeatCodeToNameMap = containers.Map( ...
    {'cr', 'sr', 'tl', 'th', 'wp', 'np', 'vo', 'le', 'cp', 'pd'}, ...
    {'creakiness', 'speaking rate', 'pitch lowness', 'pitch highness', ...
     'wide pitch range', 'narrow pitch range', 'intensity', ...
     'lengthening', 'CPPS', 'peak disalignment'} ...
     );
baseFeatName = baseFeatCodeToNameMap(baseFeatCode);

end