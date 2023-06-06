# models

## Estimate the prosodic dissimilarity of utterances

To start the application, run the Python script `gui_main.py`.

The GUI application consists of three main views: the "To fragment" view, the "To mean" view, and the "Overall" view.

The "To fragment" view lets you search for and select a fragment by ID, and then displays the fragments that are most similar and dissimilar according to the similarity measure. Next to a fragment is a button to play its audio and a field to enter notes on observations. This view displays fragments only in the same language, as the models are designed to compare fragments within the same language.

![Similarity GUI - similarity to fragment view](./images/similarity-gui-to-fragment.png)


## Create feature correlation figures

To create feature correlation figures, run `make_feature_corrs_fig.py`. Below is the feature-by-feature correlation figure for English versus Spanish DRAL 4.0 short fragments.

![DRAL EN-ES correlation figure](./images/corr-matrix-EN-ES.jpeg)

<!--
## Create feature-duration correlation figures
-->

## Model prosody mappings

1. linear regression model (`model_linear_regression.py`)
2. k-nearest neighbors regression (`model_knn.py`)
3. shallow feed forward neural network (`neural_network.py`)
4. naive baseline (`model_naive_baseline.py`)
5. synthesis baseline (`model_synthesis_baseline.py`)

<!--

## Parse MATLAB PCA outputs

(Description.)

