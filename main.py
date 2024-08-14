from typing import Union
import requests
from fastapi import FastAPI
import xml.etree.ElementTree as ET  # for parsing XML
import numpy as np  # for using pandas
import pandas as pd  # for using dataframes
from datetime import datetime

app = FastAPI()


@app.get("/")
def read_root():
    res = modifyApi()
    busID = res[0]["vehicle_ref"]
    if busID != "N/A":
        geo = getLocation(busID)
        print(geo)
    # print(res)
    return {
        "inbound": res[:2],
        "geo": geo
        }


@app.get("/items/{item_id}")
def read_item(item_id: int, q: Union[str, None] = None):
    return {"item_id": item_id, "q": q}


def modifyApi():
    response = requests.get("https://api.entur.io/realtime/v1/rest/et?datasetId=ATB")
    if response.status_code == 200:
        print("Yess")
        xml_data = response.content

        # Parsing the XML data with namespace
        namespaces = {"siri": "http://www.siri.org.uk/siri"}
        root = ET.fromstring(xml_data)

        journey_data = []

        for estimated_journey in root.findall(
            ".//siri:EstimatedVehicleJourney", namespaces
        ):
            journey_pattern_name = estimated_journey.find(
                "siri:JourneyPatternName", namespaces
            )
            lineref = estimated_journey.find("siri:LineRef", namespaces)
            vehicle_ref = estimated_journey.find("siri:VehicleRef", namespaces)

            if vehicle_ref is not None:
                print(f"VehicleRef found: {vehicle_ref.text}")
            else:
                print("VehicleRef not found")

            if lineref is not None and lineref.text == "ATB:Line:2_22":
                direction = estimated_journey.find("siri:DirectionRef", namespaces)

                if direction is not None and direction.text == "Inbound":
                    # Variable to store the previous stop information
                    previous_stop_name = None
                    previous_aimed_arrival_time = None
                    previous_expected_arrival_time = None

                    for call in estimated_journey.findall(
                        ".//siri:EstimatedCall", namespaces
                    ):
                        stop_name = call.find("siri:StopPointName", namespaces)

                        if stop_name is not None:
                            aimedArrivalTime = call.find(
                                "siri:AimedArrivalTime", namespaces
                            )
                            expectedArrivalTime = call.find(
                                "siri:ExpectedArrivalTime", namespaces
                            )

                            # Check if the current stop is "Solsiden"
                            if stop_name.text == "Solsiden":
                                arrivalStatus = call.find(
                                    "siri:ArrivalStatus", namespaces
                                )

                                aimed_arrival_time_formatted = datetime.fromisoformat(
                                    aimedArrivalTime.text
                                ).strftime("%H:%M:%S")
                                expected_arrival_time_formatted = (
                                    datetime.fromisoformat(
                                        expectedArrivalTime.text
                                    ).strftime("%H:%M:%S")
                                )

                                journey_data.append(
                                    {
                                        "stop_name": stop_name.text,
                                        "arrival_status": arrivalStatus.text,
                                        "aimed_arrival_time": aimed_arrival_time_formatted,
                                        "expected_arrival_time": expected_arrival_time_formatted,
                                        # "previous_stop_name": previous_stop_name,
                                        # "previous_aimed_arrival_time": (
                                        #     datetime.fromisoformat(
                                        #         previous_aimed_arrival_time
                                        #     ).strftime("%H:%M:%S")
                                        #     if previous_aimed_arrival_time
                                        #     else None
                                        # ),
                                        # "previous_expected_arrival_time": (
                                        #     datetime.fromisoformat(
                                        #         previous_expected_arrival_time
                                        #     ).strftime("%H:%M:%S")
                                        #     if previous_expected_arrival_time
                                        #     else None
                                        # ),
                                        # "expected_arrival_timestamp": expectedArrivalTime.text,
                                        "vehicle_ref": (
                                            vehicle_ref.text
                                            if vehicle_ref is not None
                                            else "N/A"
                                        ),
                                    }
                                )

                            # # Update previous stop information
                            # previous_stop_name = stop_name.text
                            # previous_aimed_arrival_time = (
                            #     aimedArrivalTime.text
                            #     if aimedArrivalTime is not None
                            #     else None
                            # )
                            # previous_expected_arrival_time = (
                            #     expectedArrivalTime.text
                            #     if expectedArrivalTime is not None
                            #     else None
                            # )

        # Sort journey data by the `expected_arrival_timestamp` in ascending order
        journey_data.sort(key=lambda x: x["expected_arrival_time"])

        return journey_data

    else:
        print(f"Failed to retrieve data: {response.status_code}")
        return []


def getLocation(busID: str):
    print(f"Looking for bus with ID: {busID}")
    
    # Fetch the vehicle monitoring data
    response = requests.get("https://api.entur.io/realtime/v1/rest/vm?datasetId=ATB")
    
    if response.status_code == 200:
        xml_data = response.content
        namespaces = {'siri': 'http://www.siri.org.uk/siri'}
        root = ET.fromstring(xml_data)
        
        # Loop through all VehicleActivities
        for vehicle_activity in root.findall(".//siri:VehicleActivity", namespaces):
            vehicle_ref = vehicle_activity.find(".//siri:VehicleMonitoringRef", namespaces)
            
            if vehicle_ref is not None and vehicle_ref.text == busID:
                vehicle_location = vehicle_activity.find(".//siri:VehicleLocation", namespaces)
                if vehicle_location is not None:
                    latitude = vehicle_location.find("siri:Latitude", namespaces).text
                    longitude = vehicle_location.find("siri:Longitude", namespaces).text
                    return {"latitude": latitude, "longitude": longitude}
    
    # If the busID is not found, return None
    return {"latitude": None, "longitude": None}