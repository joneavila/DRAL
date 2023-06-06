# Code for Dialogs Re-enacted Across Languages (DRAL)

This repository contains the code used in creating the DRAL corpus, prosody feature computation, modeling, and more. The code can be generalized to work for other language pairs. See technical report for more details.

> Nigel G. Ward, Jonathan E. Avila, and Emilia Rivas. 2022. Dialogs Re-enacted Across Languages. University of Texas at El Paso. Retrieved from <https://cs.utep.edu/nigel/papers/dral-techreport.pdf>

## Table of contents

 Most subdirectories contain a README.

- [**DRAL-corpus**](DRAL-corpus/) - code for creating a DRAL release, and transcribing, synthesizing, and concatenating conversation fragments, with workflow diagram
- [**feature-computation**](feature-computation/) - code for computing DRAL conversation fragments prosodic features and prosody representations, and for plotting and validating features
- [**modeling**](modeling/) - code for DRAL English and Spanish prosody mapping models, baselines, metrics, and feature correlations
- [**.flake8**](.flake8) - [Flake8](https://flake8.pycqa.org/en/latest/), Python linter settings
- [**.gitignore**](.gitignore) - [git](https://git-scm.com), untracked files to ignore
- [**.vscode**](.vscode/) - [VS Code](https://code.visualstudio.com) workspace settings: [launch.json](.vscode/launch.json) with debug configurations and [LTeX](https://marketplace.visualstudio.com/items?itemName=valentjn.vscode-ltex) grammar/spell checker dictionaries
- [**README.md**](README.md) - this file
- [**requirements.txt**](requirements.txt) - required Python modules to install with `pip`

## Setup

### MATLAB

1. Install [MATLAB](https://www.mathworks.com/products/matlab.html) R2023a.
2. Install the MATLAB add-ons [Signal Processing Toolbox](https://www.mathworks.com/products/signal.html) and [Statistics and Machine Learning Toolbox](https://www.mathworks.com/products/statistics.html). To install add-ons from MATLAB, select *Home* > *Add-Ons* > *Get Add-Ons*.
3. Clone the [Mid-level Prosodic Features Toolkit (February 9, 2023)](https://github.com/nigelgward/midlevel) repository.
4. Before running any of the project MATLAB functions, add the Mid-level Prosodic Features Toolkit to MATLAB's search path. To add a directory from MATLAB, use the built-in `addpath` function. Alternatively, right-click the directory in the *Current Folder* view, then select *Add to Path* > *Selected Folders and Subfolders*.

### Python

1. Create a [Python](https://www.python.org) 3.10.4 virtual environment, e.g., with [conda](https://docs.conda.io/en/latest/).
2. Activate the virtual environment, navigate to the project root directory, then install the required Python modules with pip: `pip install -r requirements.txt`.
3. Clone the [REAPER](https://github.com/google/REAPER) repository and compile it following its instructions, then add it to your PATH environment variable.
4. Install [SoX](https://sox.sourceforge.net). Depending on your operating system and install method, you may need to add it your PATH environment variable.

## Download DRAL

Download the Dialogs Re-enacted Across Languages (DRAL) corpus releases, up to DRAL 6.1, from the [releases page](https://cs.utep.edu/nigel/dral/).

## Contributing

If [VS Code](https://code.visualstudio.com) is your preferred editor, I suggest installing [LaTeX Workshop](https://marketplace.visualstudio.com/items?itemName=James-Yu.latex-workshop) for LaTeX typesetting and [markdownlint](https://marketplace.visualstudio.com/items?itemName=DavidAnson.vscode-markdownlint) of linting Markdown, and formatting Python code on save with [Black](https://black.readthedocs.io/en/stable/).