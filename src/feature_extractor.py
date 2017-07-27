#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jul 21 15:05:22 2017

@author: fmeyerzudiehausen, iibs, vamo, dvalenti


"""

import pywt
import pandas as pd
import numpy as np
import scipy.ndimage
import scipy.signal
import os
mode = pywt.Modes.smooth

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
    features = []
    targets = pd.DataFrame()

    subject_ids = ['a', 'b','c','d','e','f']
    for s in subject_ids:
        print(s)
        data = pd.read_csv('../data/by_subject/'+s+'_data.csv')
        data['subject_id'] = s
        labels = pd.read_csv('../data/by_subject/'+s+'_labels.csv')

        # for snippt_length sec snipped grouping
        snippet_length = 30
        data['TimestampGrouping'] = (data['Timestamp'] / snippet_length).astype(int)
        labels['TimestampGrouping'] = (labels['Timestamp'] / snippet_length).astype(int)

        labels_grouped = labels.groupby('TimestampGrouping')
        labels_grouped_count = labels_grouped.count()
        data_grouped = data.groupby('TimestampGrouping')

        # delete all rows for which there too few data
        labels_grouped_count = labels_grouped_count[labels_grouped_count.Event == snippet_length]
        labels_full_snippets = labels_grouped_count.index

        for l in range(len(labels_full_snippets)):
            try:
                slice = data_grouped.get_group(labels_full_snippets[l])
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

                power_all_channels.append(power)

            # also save info about the subject
            subject = [subject_ids.index(slice['subject_id'].values[0])]
            power_all_channels.append(subject)
            # collect power for all channels into one vector
            power_vec = reduce(lambda x,y: x+y,power_all_channels)

            # currently mean power of the frequency bands over all channels are the only features
            power_vec = np.asarray(power_vec)
            features.append(power_vec)
        subj_targets = pd.DataFrame(index=labels_full_snippets)
        events = []
        for t in range(len(labels_full_snippets)):
            a = labels_grouped.get_group(labels_full_snippets[t])['Event']
            events.append(a.values[0])
        subj_targets['Event'] = events
        subj_targets['subject_id'] = subject[0]

        targets = pd.concat([targets, subj_targets])

    features = np.asarray(features)
    features_df = pd.DataFrame(features,index=targets.index)

    if not os.path.exists("../data/precomputed_features/"):
        os.makedirs("../data/precomputed_features/")
    features_df.to_csv("../data/precomputed_features/features.csv")
    targets.to_csv("../data/precomputed_features/targets.csv")
if __name__ == "__main__":
    main()
