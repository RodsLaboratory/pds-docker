from Data import Data
from Patient import Patient
from math import nan

def lab1(patient,dx): return patient.get_value('LAB_'+dx)
def lab2(patient,dx): return patient.get_value('LAB_'+dx+'_ADDITIONAL')

def tested(patient,dx):
    l1, l2 = lab1(patient,dx), lab2(patient,dx)
    return l1=='P' or l1=='N' or l2=='P' or l2=='N'
    
def lab_positive(patient,dx):
    l1, l2 = lab1(patient,dx), lab2(patient,dx)
    return (l1=='P' or l2=='P')
    
def lab_negative(patient,dx):
    return tested(patient,dx) and not(lab_positive(patient,dx))

def daily_lab_positive(disease,data):
    result = []
    for day in range(data.number_of_days()):
        n = 0
        for patient in data.patients(day):
            if (lab_positive(patient,disease)): n+=1
        result.append(n)
    return result

def normalize(L,total): return [(x/sum(L))*total for x in L]

def moving_average(window_size, list_of_numbers):
    result = []
    half = window_size//2
    for i in range(len(list_of_numbers)):
        start = max(0,i-half)
        end = min(len(list_of_numbers), i+half+1)
        window = list_of_numbers[start:end]
        average = sum(window)/len(window)
        result.append(average)
    return result

def empirical_p(window_size, min_window_size, daily_log_probability):
    result = []
    for day in range(len(daily_log_probability)):
        if day<=min_window_size:
            result.append(nan)
            continue
        day_log_p = daily_log_probability[day]
        window = daily_log_probability[max(0,day-window_size):day]
        larger = 0
        for x in window:
            if (x<day_log_p): larger+=1
        result.append(larger/len(window))
    return result

