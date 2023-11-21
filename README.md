# About

This repository holds all the code I developed for my masters' thesis

# Neural networks in hydrology: A comparative study of different algorithms

## Abstract

This study presents a comparative analysis of different neural network models, including Convolutional Neural Net-
works (CNN), Long Short-Term Memory (LSTM) and Gated Recurrent Unit (GRU) in predicting discharge within ungauged
basins in Hesse, Germany. All models were trained on 54 catchments with 28 years of daily meteorological data, either includ-
ing or excluding 12 static catchment attributes. The training process of each model scenario combination was repeated 100
times, using a Latin Hyper Cube Sampler for the purpose of hyperparameter optimisation with batch sizes of 256 and 2048.5
Evaluation was carried out using data from 35 additional catchments (6 years), to ensure predictions in basins that were not part
of the training data. Sensitivity analysis showed a generally consistent and authentic reflection of input feature influence in both
CNN and LSTM models. The integration of static features was found to improve performance across all models, highlighting
the importance of feature selection. Interestingly, models utilising larger batch sizes displayed reduced performance, while the
relationship between batch size and runtime revealed variations across different models, highlighting the complex interplay10
between model architecture and configuration. This study contributes to a comprehensive framework for evaluating different
algorithms and confirms that the challenge of predicting streamflow in ungauged basins appears to be finally within reach with
the aid of neural networks.

## Introduction

## Materials and Methods
### Study Area
![fig01.png](https://github.com/MaxWeissenborn/Neural-networks-in-hydrology-A-comparative-study-of-different-algorithms/fig01.png)
Geographic Distribution of the Catchments in Hesse and Hesse’s Location Within Germany. Darker Shades Represent Nested
Catchments, While Intersections Indicate Catchments Partially Incorporated in Both Training and Testing Phases.

## Results
### Model Performance
[fig05.pdf](https://github.com/MaxWeissenborn/Neural-networks-in-hydrology-A-comparative-study-of-different-algorithms/files/13430242/fig05.pdf)

### Runtime
[fig06.pdf](https://github.com/MaxWeissenborn/Neural-networks-in-hydrology-A-comparative-study-of-different-algorithms/files/13430248/fig06.pdf)


### Model Sensitivity
#### CNN
[fig07.pdf](https://github.com/MaxWeissenborn/Neural-networks-in-hydrology-A-comparative-study-of-different-algorithms/files/13430209/fig07.pdf)

#### LSTM 
[fig08.pdf](https://github.com/MaxWeissenborn/Neural-networks-in-hydrology-A-comparative-study-of-different-algorithms/files/13430256/fig08.pdf)


#### GRU
[fig09.pdf](https://github.com/MaxWeissenborn/Neural-networks-in-hydrology-A-comparative-study-of-different-algorithms/files/13430254/fig09.pdf)
