#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jul 21 15:05:22 2017

@author: fmeyerzudiehausen, iibs, vamo, dvalenti


"""

import pywt
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import scipy.ndimage    
import scipy.signal    
import os
mode = pywt.Modes.smooth




# read the data: with all subjects: takes a long time (~20min)
def load_data():
    
    if not os.path.exists('../data/all_data/all_data.csv'):
       # strings = ['b','c','d','e','f']
        strings = []
        data = pd.read_csv('../data/by_subject/a_data.csv')
        labels = pd.read_csv('../data/by_subject/a_labels.csv')
        for s in strings:
            print(s)
            temp_data = pd.read_csv('../data/by_subject/'+s+'_data.csv')
            data = pd.concat([data,temp_data])
            temp_labels = pd.read_csv('../data/by_subject/'+s+'_labels.csv')
            labels = pd.concat([labels, temp_labels])
            data.to_csv('../data/all_data/all_data.csv')
            labels.to_csv('../data/all_data/all_labels.csv')
        
    else:
        data = pd.read_csv('../data/all_data/all_data.csv')
        labels = pd.read_csv('../data/all_data/all_labels.csv')
    return data, labels
        

def signal_decomp(data):
    """Decompose and plot a signal S.
    S = An + Dn + Dn-1 + ... + D1
    """
    w = pywt.Wavelet('db4')
    a = data
    ca = []
    cd = []
    for i in range(5):
        (a, d) = pywt.dwt(a, w, mode)
        ca.append(a)
        cd.append(d)  
    return ca, cd
        

def Energy(coeffs, k):
    return np.sqrt(np.sum(np.array(coeffs[-k]) ** 2)) / len(coeffs[-k])


# CONSTRUCT FEATURES

# for every label, look up the corresponding data
def main():
    data, labels = load_data()
    
    # group datapoints into bins, corresponding to a seconnd of recording time
    data['TimestampToSec'] = data['Timestamp'].astype(int)
    grouped = data.groupby('TimestampToSec')
    
    features = []
    for l in range(len(labels)):
        try:
            time = labels['Timestamp'][l]
            slice = grouped.get_group(time)
        except KeyError:
            print(time)
            pass
        # for every channel
        power_all_channels = []
        # 1-7 EEG, 8th channel is ECG data
        for ch in range(8):
            single_sec_ch = slice['Ch{}'.format(ch)]
            
            # median filter the data
            pre_processed = scipy.signal.medfilt(single_sec_ch, kernel_size=3)  
            
            _, cd = signal_decomp(pre_processed)
            # for every decomp. level
            power = []
            for l in range(5):
                power.append(Energy(cd, l))
                
            # collect power for all channels into one vector 
            power_all_channels.append(power) 
        
        # currently mean power of the frequency bands over all channels are the only features
        power_vec = np.asarray(power_all_channels).flatten()
        features.append(power_vec)
        
    features =np.asarray(features)
    np.savetxt("../data/precomputed_features/features.csv", features, delimiter = ',')
    np.savetxt("../data/precomputed_features/targets.csv", labels['Event'], delimiter = ',', fmt= '%s')

if __name__ == "__main__":
    main()