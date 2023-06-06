
% Load the loadings written by FINDDIMENSIONSMODIFIED.
pathRotationSpecEN = "/Users/jon/Documents/dissertation/DRAL-corpus/release/features/PCA-outputs-EN/rotationSpec.mat";
pathRotationSpecES = "/Users/jon/Documents/dissertation/DRAL-corpus/release/features/PCA-outputs-ES/rotationSpec.mat";
rotationSpecEN = load(pathRotationSpecEN, "pcCoeffs");
rotationSpecES = load(pathRotationSpecES, "pcCoeffs");
loadingsEN = rotationSpecEN.pcCoeffs;
loadingsES = rotationSpecES.pcCoeffs;

% Each column of the loadings contains coefficients for one principal
% component. Get the loadings of the first N principal components.
nComponents = 5;
loadingsENtruncated = loadingsEN(:, 1:nComponents);
loadingsEStruncated = loadingsES(:, 1:nComponents);


% Compute the pairwise cosine difference between the sets of loadings.
%
% The return argument is "an mx-by-my matrix, where mx and my are the
% number of observations in X and Y, respectively. D(i,j) is the distance
% between observation i in X and observation j in Y."
%
% https://www.mathworks.com/help/stats/pdist2.html#description
%
% The cosine distance metric is "One minus the cosine of the included angle
% between points (treated as vectors)"
% 
% https://www.mathworks.com/help/stats/pdist2.html#d124e753566
%
% So subtract the distances from 1 to get the cosine.
pairwiseDistances = pdist2(loadingsENtruncated', loadingsEStruncated', "cosine");
pairwiseDistances = 1 - pairwiseDistances;

disp(pairwiseDistances)