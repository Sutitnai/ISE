import serial as sr
from matplotlib import pyplot as plt
import time as tm
import timeit as tmt
import statistics
import numpy as np

def convrertStrToListOfFloat(string: str) -> list[float]:
    """
    Convert a semicolon-separated string of numbers into a list of floats.
    
    Args:
    - string (str): Input string with semicolon-separated numbers.
    
    Returns:
    - list[float]: List of floats parsed from the input string. Non-convertible
      entries are replaced with 0.0.
    """

    bitsToMs = 40181.76
    floatMesuremnts = []  # Initialize an empty list to store float measurements
    strMesurements = string.split(";")  # Split the input string by semicolons
    for mesurement in strMesurements:
        try:
            x = float(mesurement)  # Convert each measurement to float
        except ValueError:
            x = 0.0  # If conversion fails, set the value to 0.0
        floatMesuremnts += [x/bitsToMs]  # Add the float value to the list
    return floatMesuremnts

def trackSerial(comPort: str, mesureTm: int) -> tuple[bool, dict[str, list]]:
    """
    Track and read sensor data from a serial port for a specified duration.
    
    Args:
    - comPort (str): The COM port to connect to.
    - mesureTm (int): Duration in seconds for which to read data.
    
    Returns:
    - tuple[bool, dict[str, list]]: A tuple containing a success flag and a dictionary
      with lists of sensor data for each axis ('X', 'Y', 'Z').
    """
    results = {"X": [], "Y": [], "Z": []}  # Initialize a dictionary to store results
    print("trying to connect to serial port")
    try:
        # Attempt to connect to the specified serial port
        serialPort = sr.Serial(port=comPort, baudrate=115200)
        print("connected")
        tm.sleep(0.07)  # Wait briefly to ensure the connection is established
    except sr.serialutil.SerialException:
        print("Connection failed")
        return False, results  # Return false if the connection fails

    print("monitoring Sensor...")    
    startTime = tmt.default_timer()  # Record the start time
    while (tmt.default_timer() - startTime) < float(mesureTm):
        remTime = round((mesureTm -(tmt.default_timer() - startTime)) / 60, 2) #calculates the remaining time for the mesurement
        print("\r>> Time remaining: {}min.".format(remTime), end='')  #updates the remaining time for the user
        if serialPort.in_waiting > 1:  # Check if there is data waiting in the serial buffer
            serialInput = serialPort.readline()  # Read a line of input from the serial port
            try:
                serialStr = serialInput.decode("Ascii")  # Decode the input as an ASCII string
            except UnicodeDecodeError:
                return False, results  # Return false if decoding fails
            currentResults = convrertStrToListOfFloat(serialStr)  # Convert the string to a list of floats

            j = 0
            for key in results.keys():
                results[key] += [currentResults[j]]  # Add the float values to the respective axis lists
                j += 1

    serialPort.close()  # Close the serial port
    print("finished.")

    return True, results  # Return the success flag and results

def calculateDeviation(results: dict[str, list]) -> dict[str, list]:
    """
    Calculate the deviation of each sensor reading from its mean.
    
    Args:
    - results (dict[str, list]): Dictionary with lists of sensor data for each axis ('X', 'Y', 'Z').
    
    Returns:
    - dict[str, list]: Dictionary with lists of deviations for each axis.
    """
    devDict = {"X": [], "Y": [], "Z": []}  # Initialize a dictionary to store deviations
    for key in results.keys():
        devList = []
        values = results[key]
        mean = statistics.mean(values)  # Calculate the mean of the values
        for value in values:
            value = value - mean  # Calculate the deviation from the mean
            devList += [value]  # Add the deviation to the list
        devDict[key] += devList  # Store the deviations in the dictionary
    return devDict

def plotDeviation(deviationDict: dict[str, list], numBars: int, time: int):
    """
    Plot the deviation of sensor data as a bar plot for each axis.
    
    Args:
    - deviationDict (dict[str, list]): Dictionary with lists of deviations for each axis.
    - numBars (int): Number of bars for the plot.
    - time (int): Duration in seconds over which the data was collected.
    """
    for key in deviationDict.keys():
        deviations = deviationDict[key]
        max_dev = max(deviations)  # Find the maximum deviation
        min_dev = min(deviations)  # Find the minimum deviation
        bin_width = (max_dev - min_dev) / numBars  # Calculate the width of each bin
        bins = np.arange(min_dev, max_dev + bin_width, bin_width)  # Create the bins
        hist, bin_edges = np.histogram(deviations, bins=bins)  # Calculate the histogram
        bin_centers = (bin_edges[:-1] + bin_edges[1:]) / 2  # Calculate the bin centers
        fig, ax = plt.subplots()  # Create a new figure and axes
        ax.bar(bin_centers, hist, width=bin_width)  # Create the bar plot
        ax.set_xlabel('Deviation Range')  # Set the x-axis label
        ax.set_ylabel('Frequency')  # Set the y-axis label
        ax.set_title(f'Bar Plot of Deviations (m/s^2) for {key} axis. Over {time} seconds.')  # Set the title
        plt.show()  # Display the plot

def mangeMesurement(comPort: str, mesuringTime: int, numBars: int):
    """
    Manage the process of measuring sensor data, calculating deviation, and plotting results.
    
    Args:
    - comPort (str): The COM port to connect to.
    - mesuringTime (int): Duration in seconds for which to read data.
    - numBars (int): Number of bars for the plot.
    """
    success, sensorData = trackSerial(comPort=comPort, mesureTm=mesuringTime)  # Track sensor data
    if success:
        deviation = calculateDeviation(sensorData)  # Calculate deviations
        plotDeviation(deviationDict=deviation, numBars=numBars, time=mesuringTime)  # Plot deviations
    else:
        print("measuring failed")  # Print error message if tracking fails

# Main execution
print("Welcome")
comPort = input("Enter the com port: ")
print("you've selected: " + comPort)
mesuringTime = input("Enter the time you want to measure in s: ")
print("your measuring time is: " + mesuringTime)
numbBars = input("Enter the number of bars for the plot: ")
print("You've selected " + numbBars + " bars.")
mangeMesurement(comPort=comPort, mesuringTime=int(mesuringTime), numBars=int(numbBars))
