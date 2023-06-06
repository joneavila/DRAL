# models

## Create feature correlation figures

To create these, run `make_feature_corrs_fig.py`. Below is the feature-by-feature correlation figure for English versus Spanish DRAL 4.0 short fragments.

![DRAL EN-ES correlation figure](./images/corr-matrix-EN-ES.jpeg)

## Create feature-duration correlation figures

## Prosody dissimilarity metric

## Prosody dissimilarity GUI application

To help in analysis of the similarity measure, I built a "similarity" application. The application consists of three main views: the "To fragment" view, the "To mean" view, and the "Overall" view. The "To fragment" view lets you search for and select a fragment by ID, and then displays the fragments that are most similar and dissimilar according to the similarity measure. Next to a fragment is a button to play its audio and a field to enter notes on observations. This view displays fragments only in the same language, as the models are designed to compare fragments within the same language.

![Similarity GUI - similarity to fragment view](./images/similarity-gui-to-fragment.png)

Run `gui_main.py`.

## Test models

1. linear regression model --> `model_linear_regression.py`
2. k-nearest neighbors regression --> `model_knn.py`
3. shallow feed forward neural network
4. naive baseline
5. synthesis baseline

To run the experiments:

1. Prepare the data for feature computation and compute the prosodic features. See the workflow diagram in [DRAL/README.md](../DRAL/README.md).
2. Run `experiments.py`.

<!--

## Parse MATLAB PCA outputs

(Description.)

-->