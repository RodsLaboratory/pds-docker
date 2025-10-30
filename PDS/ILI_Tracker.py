from math import log, exp, e
from numpy import logaddexp

MIN_POSTERIOR = 0.0001

def _normalize(probabilities,min_probability):
    probabilites = [x+min_probability for x in probabilities]
    total = sum(probabilities)
    return [p/total for p in probabilities]

def _logsum(logs):
    result = logs[0]
    for i in range(1,len(logs)): result = logaddexp(result,logs[i])
    return result

def ili_tracker(diseases, original_priors, log_likelihood_fields, eqs, base, data):
    original_priors[len(original_priors)-1] = 1.0-sum(original_priors[0:len(original_priors)-1])
    priors = original_priors
    result = dict()
    for dx in diseases: result[dx]=[]
    daily_log_probability = []
    daily_log_unusual_cutoff = []
    for day in range(data.number_of_days()):
        log_priors = [log(prior) for prior in priors]
        expected = [0.0 for dx in diseases]
        number_of_patients_day = 0
        log_probability_day = 0.0
        for patient in data.patients(day):
            log_likelihoods = [(float(patient.get_value(field))/log(e,base)) for field in log_likelihood_fields]
            log_posteriors = [ll+p for (ll,p) in zip(log_likelihoods,log_priors)]
            log_denominator = _logsum(log_posteriors)
            log_probabilities = [log_posterior-log_denominator for log_posterior in log_posteriors]
            probabilities = [exp(lp) for lp in log_probabilities]
            expected = [e+p for (e,p) in zip(expected,probabilities)]
            number_of_patients_day += 1
            log_probability_day += log_denominator
        for i in range(len(diseases)): result[diseases[i]].append(expected[i])
        total = sum(expected)
        posteriors = [(e+(eqs*prior))/(total+eqs) for (e,prior) in zip(expected,original_priors)]
        posteriors = _normalize(posteriors,MIN_POSTERIOR)
        priors = posteriors
        log_probability_day = log_probability_day / len(data.patients(day))
        daily_log_probability.append(log_probability_day)
    result['daily_log_probability'] = daily_log_probability
    return result

