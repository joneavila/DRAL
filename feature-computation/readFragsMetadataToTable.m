function fragsTable = readFragsMetadataToTable(metadataCSVpath)
% READFRAGSMETADATATOTABLE Read DRAL short fragments metadata into a table.
%
% Input arguments:
%   - metadataCSVpath (char) - Path to metadata CSV
%
% Output arguments:
%   - fragsTable (table) - A table containing the read metadata with the
%       columns:
%
%   - id (string) - fragment ID
%   - conv_id (string) - source conversation ID
%   - lang_code (string) - ISO 639-1 two-letter language code of source
%       conversation
%   - original_or_reenacted (string) - two-letter code indicating whether
%       the source conversation was the original or re-enactment
%   - time_start_rel (duration) - time into concatenated conversation
%       fragments audio when the fragment begins
%   - time_end_rel (duration) - time into concatenated conversation
%       fragments audio when the fragment ends
%   - duration (duration) - duration of fragment
%   - concat_audio_path (string) - path to concantenated conversation
%       fragments audio featuring the fragment
%   - trans_id (string) - translation fragment ID
%   - trans_lang_code (string) - ISO 639-1 two-letter language code of
%       source conversation's translation
%   - participant_id_unique (string) - unique ID of participant speaking

    opts = detectImportOptions(metadataCSVpath);

    opts.RowNamesColumn = 1;
    
    % Most of the CSV import options are detected properly, but the
    % variable types and format of duration columns must be set manually.
    opts.VariableTypes = {'string', 'string', 'string', 'string', ...
        'duration', 'duration', 'duration', ...
        'char', 'string', 'string', 'string'};
    opts = setvaropts(opts, 'time_start_rel', 'InputFormat', 'mm:ss.SSS');
    opts = setvaropts(opts, 'time_end_rel', 'InputFormat', 'mm:ss.SSS');
    opts = setvaropts(opts, 'duration', 'InputFormat', 'mm:ss.SSS');
    
    fragsTable = readtable(metadataCSVpath, opts);

end