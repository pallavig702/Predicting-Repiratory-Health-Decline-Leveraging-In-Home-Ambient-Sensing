from scipy.signal import butter, lfilter, filtfilt


def butter_lowpass_filter(data):
    # fs is 1Hz which is 100 samples/sec after hardware filtering
    # When using 4th order filtfilt, give filterorder = 2 because filtfilt applies a digital filter forward and backward to a signal. So give value 2 to 4th order.
    filterorder = 6  # software filtering 6 order filtering.
    fc_down = 0.2

    normal_cutoff = 0.014 / 0.2
    cutoff = 0.014  # fc_down/(fs/2) [fs is frequency of samples which is 100 samples/sec. This comes from previous signal processing steps]

    # Get the filter coefficients
    # b, a = butter(filterorder, Wn=normal_cutoff, btype="lowpass")
    b = [
        0.000234487894504741,
        0,
        -0.00140692736702845,
        0,
        0.00351731841757112,
        0,
        -0.00468975789009482,
        0,
        0.00351731841757112,
        0,
        -0.00140692736702845,
        0,
        0.000234487894504741,
    ]
    a = [
        1,
        -9.60972210409256,
        42.5044725167320,
        -114.495656304045,
        209.312140612173,
        -273.691848572724,
        262.545133243944,
        -186.198726793693,
        96.9036651938758,
        -36.0926373232641,
        9.13215305571148,
        -1.40928057198485,
        0.100307047533755,
    ]

    y = lfilter(b, a, data)

    return y


# To Get rid of the DC component if you want to try that
def bandpass(vector):
    [b, a] = butter(3, [0.002, 0.014], btype="band")
    # 0.7-10Hz
    f_filtered = lfilter(b, a, vector)
    return f_filtered
