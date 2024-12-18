"""
This sctipt is for verifying the installation of essential packages on the Pi
"""
import cv2
import tflite_runtime.interpreter as tflite
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import MFRC522
from gpiozero import OutputDevice


print("OpenCV version:", cv2.__version__)
print("tflite_runtime version:", tflite.__version__)
print("NumPy version:", np.__version__)
print("Matplotlib version:", matplotlib.__version__)
