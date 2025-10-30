#
# Contents: ILI Tracker
# Author:   John Aronis (jma18@pitt.edu)
# Date:     January 12, 2025
#

This file contains instructions to run the ILI Tracker system.  For a
full description of the system see:

    Aronis JM, Ye Y, Espino J, Hochheiser H, Michaels MG, Cooper GF. A
    Bayesian System to Detect and Track Outbreaks of Influenza-Like
    Illnesses Including Novel Diseases: Algorithm Development and
    Validation. JMIR Public Health Surveill. 2024 Aug 13;10:e57349. doi:
    10.2196/57349. PMID: 38805611; PMCID: PMC11350309.

The main classes are Data and ILI_Tracker.

The Data class reads data from a csv file with one line per patient
and fields for admission date and the log-likelihoods of each modeled
disease. A small sample data file is in Sample_Data.csv to test if the 
program runs.

The file is in CSV format with the following columns:
* ID - Record ID
* SEASON - Season of the data
* ICD_<DISEASE> - ICD Status of the disease [M - missing, T - true, F - false]
* LAB_<DISEASE> - Lab Status of the disease [M,T,F]
* LABEL_<DISEASE> - ICD/Lab Status of the disease [M,T,F] - using rule ***
* Admit_date_time - Time of ED visit in YYYY-MM-DD HH24:MM:SS
* <DISEASE>_loglikelihood_M - Log likelihood of the disease missing given the Label value
* <DISEASE>_loglikelihood_T - Log likelihood of the disease true  given the Label value
* <DISEASE>_Prob_M - Probability of the disease missing given the Label value
* <DISEASE>_Prob_T - Probability of the disease true given the Label value

Please see https://www.rods.pitt.edu/research/pds/ for more information on how to 
obtain additional data used in our research paper.

The file ILI_Tracker.py contains the method ili_tracker() that
computes the daily expected number of patients with each of the
modeled diseases.  It expects a Data object with patient data, along
with several other parameters.

The file Run_ILI_Tracker.py contains an example of how to run the ILI
Tracker program.  ```Run_ILI_Tracker.py -h``` will show the command line arguments.

You can change the following variables in Run_ILI_Tracker.py:

    data_directory is the directory containing the data files.
    
    data_file is the particular data file to use.
    
    diseases is a list of diseases that are to be tracked.
    
    ll_fields is a list of the fields with the log-likelihoods.
    
    priors is a list of initial prior probabilities of the
      tracked diseases.
    
    admission_date_field is the name of the field containing the patient's
      admission date.
    
    delimiter is the data file delimiter (usually a comma).
    
    file_missing_value is the token that designates a missing value
      in the data file (usually "M" or empty).
    
    data_missing_value is the token that methods in the Data and Patient
      class use to designate a missing value (usually "M").
    
    base is the logarithmic base of the log-likelihood fields in the
      data file (usually 10.0 or e).
    
    equivalent_sample_size is the equivalent sample size to use to
      avoid over-reliance on small samples
    
    moving_average_window is the window size to use when computing
      moving averages for graphing results.

The ili_tracker method expects several months or a year of data.  It
returns a dictionary of daily expected numbers of patients with each
modeled disease.  It also returns the daily log-probability of the
data according to its predictions.  See the variable
ili_tracker_results[] in Run_ILI_Tracker.py.

Run_ILI_Tracker.py also illustrates how results can be plotted.

