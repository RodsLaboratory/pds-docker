# Models

In this project we trained 36 different models covering multiple years from 2012-2020 that
include influenza, respiratory syncytial virus, adenovirus, parainfluenza, human metapneumovirus, enterovirus and
Covid-19. These are Naive Bayes models built using the Weka Java API. The input for these models are up to 696 discrete
valued variables derived from medical records and the output
of each model is a single binary variable i.e., the presence or absence of disease.

The pre-trained models are in one of
three formats: Weka .model files, comma-delimited files (.csv) and text files (.txt). In order to utilize the .model
files directly,
one can use the Weka desktop software or Weka Java API. The .txt file is for convenient reading and we provide the .csv
file for use in other inference engines. The conventions we used in the
abbreviations are the following:

* M - missing or not present
* T - true or present
* P - positive
* N - negative
* H - high
* N - normal
* L - low