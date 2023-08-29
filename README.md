# Code for Dialogs Re-enacted Across Languages (DRAL) corpus

This repository contains the code used in creating the Dialogs Re-enacted Across Languages (DRAL) corpus, computing prosodic features of utterances, and modeling the mappings of English and Spanish prosody.

## Download the DRAL corpus

Download the DRAL corpus releases from the [releases page](https://www.cs.utep.edu/nigel/dral/).

Note: Releases are incremental. To get the latest release, download each release in sequence, merging the files of each release into the previous.

## Collect similar data following the DRAL protocol

The DRAL protocol is described in our [technical report](https://www.cs.utep.edu/nigel/papers/dral-techreport.pdf). For post-processing, see the `DRAL-corpus` subdirectory.

## Compute prosodic features of DRAL utterances, model prosody the mappings of English and Spanish prosody

The code is separated into the following subdirectories. Each subdirectory contains a README.

- [**`DRAL-corpus`**](DRAL-corpus/) - Code for DRAL post-processing and preparing the data for feature computation. See the included workflow diagram.
- [**`feature-computation`**](feature-computation/) - Code for computing DRAL conversation fragments prosodic features and prosody representations, and for plotting and validating features.
- [**`modeling`**](modeling/) - Code for DRAL English and Spanish prosody mapping models, baselines, metrics, and feature correlations.

### Setup

#### MATLAB

1. Install [MATLAB](https://www.mathworks.com/products/matlab.html) R2023a.
2. Install the MATLAB add-ons [Signal Processing Toolbox](https://www.mathworks.com/products/signal.html) and [Statistics and Machine Learning Toolbox](https://www.mathworks.com/products/statistics.html). To install add-ons from MATLAB, select *Home* > *Add-Ons* > *Get Add-Ons*.
3. Clone the [Mid-level Prosodic Features Toolkit (February 9, 2023)](https://github.com/nigelgward/midlevel) repository.
4. Before running any of the project MATLAB functions, add the Mid-level Prosodic Features Toolkit to MATLAB's search path. To add a directory from MATLAB, use the built-in `addpath` function. Alternatively, right-click the directory in the *Current Folder* view, then select *Add to Path* > *Selected Folders and Subfolders*.

#### Python

1. Create a [Python](https://www.python.org) 3.10.4 virtual environment, e.g., with [conda](https://docs.conda.io/en/latest/).
2. Activate the virtual environment, navigate to the project root directory, then install the required Python modules with pip: `pip install -r requirements.txt`.
3. Clone the [REAPER](https://github.com/google/REAPER) repository and compile it following its instructions, then add it to your PATH environment variable.
4. Install [SoX](https://sox.sourceforge.net). Depending on your operating system and install method, you may need to add it your PATH environment variable.

## Citing


### Interspeech 2023 paper

Cite as: Avila, J.E., Ward, N.G. (2023) Towards Cross-Language Prosody Transfer for Dialog. Proc. INTERSPEECH 2023, 2143-2147, doi: 10.21437/Interspeech.2023-1152

```tex
@inproceedings{avila23_interspeech,
  author={Jonathan E. Avila and Nigel G. Ward},
  title={{Towards Cross-Language Prosody Transfer for Dialog}},
  year=2023,
  booktitle={Proc. INTERSPEECH 2023},
  pages={2143--2147},
  doi={10.21437/Interspeech.2023-1152}
}
```

Online: [ISCA Archive](https://www.isca-speech.org/archive/interspeech_2023/index.html)

### DRAL technical report

```tex
@techreport{ward2023a,
  title = {Dialogs {{Re-enacted Across Languages}}, {{Version}} 2},
  author = {Ward, Nigel G. and Avila, Jonathan E. and Rivas, Emilia and Marco, Divette},
  year = {2023},
  number = {UTEP-CS-23-27},
  institution = {{University of Texas at El Paso}}
}
```

Online: [UTEP, Nigel Ward](https://www.cs.utep.edu/nigel/abstracts/dral-techreport2.html)

## Contributing

Included is a [Flake8](https://flake8.pycqa.org/en/latest/) Python linter settings file ([`.flake8`](.flake8)). If [VS Code](https://code.visualstudio.com) is your preferred editor, included is a VS Code workspace settings file ([`.vscode`](.vscode/)) with debug configurations. I suggest installing the [markdownlint extension](https://marketplace.visualstudio.com/items?itemName=DavidAnson.vscode-markdownlint) for linting Markdown, and formatting Python code on save with [Black](https://black.readthedocs.io/en/stable/).
