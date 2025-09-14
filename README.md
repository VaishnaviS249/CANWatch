CANWatch – Real-Time CAN Bus Logger and Analyzer
Overview
CANWatch is a Python tool to log and analyze CAN bus messages from vehicles. It generates visualizations to help understand message traffic and detect anomalies.
Tech stack: Python, pandas, Matplotlib, Git/GitHub

Features
Logs CAN messages to CSV (can_log.csv)
Detects anomalous payloads (non-8-byte messages)

Visualizes:
Top 10 CAN IDs (bar graph)
Traffic rate over time (line graph)

Installation / Requirements:
Python 3.x
Install required packages:
pip install pandas matplotlib
Usage
python3 analyze_can.py
Reads ../data/can_log.csv
Cleans data and timestamps
Detects anomalies (non-8-byte payloads)

Generates visualizations:
can_id_frequency.png → Bar graph of top CAN IDs

traffic_rate.png → Line graph of messages per interval

Detecting Anomalies
Each CAN payload should be 8 bytes.
Messages not equal to 8 bytes are flagged as anomalies and displayed in the console.
