from typing import Union
import requests 
from fastapi import FastAPI
import xml.etree.ElementTree as ET  # for parsing XML
import numpy as np  # for using pandas
import pandas as pd  # for using dataframes
from datetime import datetime


def modifyApi():
    response = requests.get("https://api.entur.io/realtime/v1/rest/et?datasetId=ATB")
    if response.status_code == 200:
        print("Yess")
        xml_data = response.content
        
        # Parsing the XML data with namespace
        namespaces = {'siri': 'http://www.siri.org.uk/siri'}
        root = ET.fromstring(xml_data)
        
        journey_data = []
        
        for estimated_journey in root.findall(".//siri:EstimatedVehicleJourney", namespaces):
            journey_pattern_name = estimated_journey.find("siri:JourneyPatternName", namespaces)
            lineref = estimated_journey.find("siri:LineRef", namespaces)
            
            if lineref is not None and lineref.text == "ATB:Line:2_22":
                direction = estimated_journey.find("siri:DirectionRef", namespaces)
                
                if direction is not None and direction.text == "Inbound":
                    # Variable to store the previous stop information
                    previous_stop_name = None
                    previous_aimed_arrival_time = None
                    previous_expected_arrival_time = None
                    
                    for call in estimated_journey.findall(".//siri:EstimatedCall", namespaces):
                        stop_name = call.find("siri:StopPointName", namespaces)
                        
                        if stop_name is not None:
                            aimedArrivalTime = call.find("siri:AimedArrivalTime", namespaces)
                            expectedArrivalTime = call.find("siri:ExpectedArrivalTime", namespaces)
                            
                            # Check if the current stop is "Solsiden"
                            if stop_name.text == "Solsiden":
                                arrivalStatus = call.find("siri:ArrivalStatus", namespaces)
                                
                                aimed_arrival_time_formatted = datetime.fromisoformat(aimedArrivalTime.text).strftime('%H:%M:%S')
                                expected_arrival_time_formatted = datetime.fromisoformat(expectedArrivalTime.text).strftime('%H:%M:%S')
                                vehicleref = estimated_journey.find("siri:VehicleRef", namespaces)
                                
                                journey_data.append({
                                    'stop_name': stop_name.text,
                                    'arrival_status': arrivalStatus.text,
                                    'aimed_arrival_time': aimed_arrival_time_formatted,
                                    'expected_arrival_time': expected_arrival_time_formatted,
                                    'previous_stop_name': previous_stop_name,
                                    'previous_aimed_arrival_time': previous_aimed_arrival_time,
                                    'previous_expected_arrival_time': previous_expected_arrival_time,
                                    'expected_arrival_timestamp': expectedArrivalTime.text,
                                    'vehicleref'    : vehicleref.text
                                })
                                    
                            # Update previous stop information
                            previous_stop_name = stop_name.text
                            previous_aimed_arrival_time = aimedArrivalTime.text if aimedArrivalTime is not None else None
                            previous_expected_arrival_time = expectedArrivalTime.text if expectedArrivalTime is not None else None
        
        # Sort journey data by the `expected_arrival_timestamp` in descending order
        journey_data.sort(key=lambda x: x['expected_arrival_timestamp'], reverse=False)
        
        # Print the sorted results
        for data in journey_data:
            print(f"Inbound Mot skolen!")
            print(f"  Stop: {data['stop_name']}")
            print(f"    ArrivalStatus: {data['arrival_status']}")
            print(f"    AimedArrivalTime: {data['aimed_arrival_time']}")
            print(f"    ExpectedArrivalTime: {data['expected_arrival_time']}")
            
            if data['previous_stop_name'] is not None:
                prev_aimed_time_formatted = datetime.fromisoformat(data['previous_aimed_arrival_time']).strftime('%H:%M:%S')
                prev_expected_time_formatted = datetime.fromisoformat(data['previous_expected_arrival_time']).strftime('%H:%M:%S')
                print(f"  Previous Stop: {data['previous_stop_name']}")
                print(f"    AimedArrivalTime: {prev_aimed_time_formatted}")
                print(f"    ExpectedArrivalTime: {prev_expected_time_formatted}")
    
    else:
        print(f"Failed to retrieve data: {response.status_code}")
                        

modifyApi()