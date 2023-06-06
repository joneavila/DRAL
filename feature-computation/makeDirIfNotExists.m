function makeDirIfNotExists(dir)
% MAKEDIRIFNOTEXISTS Creates a directory if it does not exist. This avoid
% raising MATLAB's warning when attempting to create a directory that
% already exists.
%
%   Input arguments:
%       dir (char) - The path to the directory to create.

if ~isfolder(dir)
    mkdir(dir);
end

end