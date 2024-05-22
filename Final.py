import numpy as np
import sounddevice as sd
import tkinter as tk
from tkinter import ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import scipy.signal as sig

# Variables
samplingFreq = 44100  # Sample rate in Hz
sampleDuration = 2  # Duration of notes in seconds
time = np.linspace(0, sampleDuration, samplingFreq * sampleDuration, False)  # Time vector in seconds
amp = 1  # Amplitude
initPhase = np.pi / 2  # Initial phase in radians

# List of notes
notes = {"C": 261.63, "C#": 277.18, "D": 293.66, "D#": 311.13, "E": 329.63, "F": 349.23,
         "F#": 369.99, "G": 392.00, "G#": 415.30, "A": 440.00, "A#": 466.16, "B": 493.88}


def apply_peak_filter(input_signal, center_freq, Q, sampling_rate):
    # Peak filter coefficients (b and a) which are used to filter the signal using IIR filter.
    b, a = sig.iirpeak(center_freq / (sampling_rate / 2), Q)
    # Application of the filter to the input signal using lfilter function
    filtered_signal = sig.lfilter(b, a, input_signal)
    return filtered_signal, b, a


def plot_frequency_response(canvas, fig, ax, b, a, sampling_rate):
    freq, h = sig.freqz(b, a, fs=sampling_rate)

    # Clear the axes
    ax[0].clear()
    ax[1].clear()

    ax[0].plot(freq, 20 * np.log10(np.maximum(abs(h), 1e-5)), color='blue')
    ax[0].set_title("Frequency Response")
    ax[0].set_ylabel("Amplitude (dB)", color='blue')
    ax[0].set_xlim([0, sampling_rate / 2])  # The x-axis limit is half the sampling rate (Nyquist frequency)
    ax[0].set_ylim([-50, 10])
    ax[0].grid(True)

    ax[1].plot(freq, np.unwrap(np.angle(h)) * 180 / np.pi, color='green')
    ax[1].set_ylabel("Angle (degrees)", color='green')
    ax[1].set_xlabel("Frequency (Hz)")
    ax[1].set_xlim([0, sampling_rate / 2])  # Here, the x-axis limit is also adjusted to half the sampling rate (Nyquist frequency)
    ax[1].set_yticks([-90, -60, -30, 0, 30, 60, 90])
    ax[1].set_ylim([-90, 90])
    ax[1].grid(True)

    # Draw the updated figure
    canvas.draw()


def play_sound():
    # Getting the values from the GUI
    waveform = waveform_var.get()
    note = notes[note_var.get()]
    center_freq = float(center_freq_var.get())
    Q = float(Q_var.get())

    # Generate the waveform
    if waveform == "Sine":
        generated_signal = np.sin(2 * np.pi * note * time)
    elif waveform == "Sawtooth":
        generated_signal = 2 * (time * note % 1) - 1
    elif waveform == "Square":
        generated_signal = np.sign(np.sin(2 * np.pi * note * time))

    # Apply peak filter
    filtered_signal, b, a = apply_peak_filter(generated_signal, center_freq, Q, samplingFreq)

    # Plot frequency response in the canvas
    plot_frequency_response(canvas, fig, ax, b, a, samplingFreq)

    # Play the sound
    sd.play(filtered_signal, samplingFreq)
    sd.wait()  # Wait until sound has finished playing


# Initialize the main window
root = tk.Tk()
root.title("Synthesizer")

# Controls
control_frame = ttk.Frame(root, padding=10)
control_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

# Dropdown for waveform selection
waveform_label = ttk.Label(control_frame, text="Waveform:")
waveform_label.pack(side=tk.LEFT)
waveform_var = tk.StringVar()
waveform_dropdown = ttk.Combobox(control_frame, textvariable=waveform_var, values=["Sine", "Sawtooth", "Square"])
waveform_dropdown.pack(side=tk.LEFT)
waveform_dropdown.set("Sine")  # default value

# Note selection stuff
note_label = ttk.Label(control_frame, text="Note:")
note_label.pack(side=tk.LEFT)
note_var = tk.StringVar()
note_dropdown = ttk.Combobox(control_frame, textvariable=note_var,
                             values=["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B", "C"])
note_dropdown.pack(side=tk.LEFT)
note_dropdown.set("A")  # default value

# Center frequency entry
center_freq_label = ttk.Label(control_frame, text="Center Frequency (Hz):")
center_freq_label.pack(side=tk.LEFT)
center_freq_var = tk.StringVar(value="1000")  # Default value
center_freq_entry = ttk.Entry(control_frame, textvariable=center_freq_var)
center_freq_entry.pack(side=tk.LEFT)

# Q factor entry
Q_label = ttk.Label(control_frame, text="Q Factor:")
Q_label.pack(side=tk.LEFT)
Q_var = tk.StringVar(value="10")  # Default value
Q_entry = ttk.Entry(control_frame, textvariable=Q_var)
Q_entry.pack(side=tk.LEFT)

# Play button
play_button = ttk.Button(control_frame, text="Play Sound")
play_button.config(command=play_sound)
play_button.pack(side=tk.RIGHT)

# plotting
plot_frame = ttk.Frame(root, padding=10)
plot_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
fig, ax = plt.subplots(2, 1, figsize=(8, 6))
canvas = FigureCanvasTkAgg(fig, master=plot_frame)
canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

root.mainloop()
