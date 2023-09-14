function markupTable = readELANtoTable(markupPath)
% READELANTOTABLE Read an ELAN export tab-delimited .txt file and return
% its contents as a table.
%   
%   Input arguments:
%       markupPath (string) - The path to an ELAN export tab-delimited .txt
%       file. To export with the expected format from ELAN: click "File" >
%       "Export As" > "Tab-delimited Text..." > click "Select All" under
%       "Select tiers" and uncheck "ss.msec" under "Include time format:" >
%       click "OK" > click "Save".
%
%   Output arguments:
%       markupTable (table) - A table with the columns: tier (char),
%       startTime (duration), endTime (duration), duration (duration),
%       value (char).

% The auto-detected import options work well for most columns.
importOpts = detectImportOptions(markupPath);

importOpts.VariableNames = {'tier', 'startTime', 'endTime', 'duration', ...
    'value'};
importOpts.VariableTypes = {'char', 'duration', 'duration', 'duration', ...
    'char'};
importOpts.ConsecutiveDelimitersRule = 'join';

markupTable = readtable(markupPath, importOpts);

end