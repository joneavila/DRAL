# feature-computation

This directory contains the code for computing prosodic (Midlevel Toolkit) features of DRAL short fragments and plotting prosodic features in an interactive figure.

## Computing prosodic features of DRAL short fragments

1. Add this directory to MATLAB path.
2. Add the Midlevel Toolkit directory to MATLAB path.
3. Prepare the DRAL data for feature computation. Follow the workflow diagram in
   [../DRAL/README.md](../DRAL/README.md).
4. Run `computeFeatures.m`. For more information, see documentation in script.

## Plotting prosodic features in an interactive figure

To plot the prosodic features of a DRAL fragment, run `plotFragFeatures.m`.

- [ ] Update documentation in `plotFeatures.m`.
- [ ] Update documentation in `featuresToTimeTables.m`.

![plotFeatures.m example](./images/plot-features-example.png)

## Test audio

See [./test-audio/README.md](./test-audio/README.md).

## Modifications, contributions to Midlevel Toolkit

### Modified pitch computation

The script `lookUpOrComputePitchModified.m` is modified from Midlevel Toolkit `lookupOrComputePitch.m`. The function `lookUpOrComputePitchModified` removes the fallback to VOICEBOX `fxrapt` enforcing REAPER for pitch tracking.

For more information, see documentation in `lookUpOrComputePitchModified.m`.

- [ ] Update documentation in `lookUpOrComputePitchModified.m`.

### Modified CPPS computation

The script `computeCPPSmodified.m` is modified from Midlevel Toolkit `computeCPPS.m`. The function `computeCPPS` runs about 5 times faster by reducing the number of spectrogram windows computations (as tested by `timeCPPSfunctions.m`) and pads the return CPPS feature vector so that each 10 milliseconds of the input signal is assigned a CPPS value.

This modified function is unused; it did not have a strong correlation with the original function, as tested by `plotCPPSfunctions.m`.

### Interactive feature plot

The function `plotFeatures.m`, called by `plotFragFeatures.m` is generalized and can be used with other features computed outside of DRAL.

## Notes

I wanted to write all code in Python and use the MATLAB engine to call the Midlevel Toolkit functions I
needed, but not all Midlevel Toolkit functions can be called from Python because they return [unsupported
types](https://www.mathworks.com/help/matlab/matlab_external/passing-data-to-python.html#buialof-51).
