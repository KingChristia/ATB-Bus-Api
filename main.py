from typing import Union, List
import requests
from fastapi import FastAPI
import xml.etree.ElementTree as ET  # for parsing XML
from datetime import datetime, date

app = FastAPI()


@app.get("/")
def read_root(
    line_ref: Union[str, None] = None,
    direction: Union[str, None] = None,
    stop_name: Union[str, None] = None,
):
    res = modifyApi(line_ref, direction, stop_name)
    return {"data": res[:2]}


def modifyApi(
    line_ref: Union[str, None] = None,
    direction: Union[str, None] = None,
    stop_name: Union[str, None] = None,
):
    response = requests.get("https://api.entur.io/realtime/v1/rest/et?datasetId=ATB")
    if response.status_code == 200:
        xml_data = response.content

        # Parsing the XML data with namespace
        namespaces = {"siri": "http://www.siri.org.uk/siri"}
        root = ET.fromstring(xml_data)

        journey_data = []

        for estimated_journey in root.findall(
            ".//siri:EstimatedVehicleJourney", namespaces
        ):
            lineref = estimated_journey.find("siri:LineRef", namespaces)
            direction_ref = estimated_journey.find("siri:DirectionRef", namespaces)
            vehicle_ref = estimated_journey.find("siri:VehicleRef", namespaces)

            # Filter by line_ref if provided
            if lineref is not None and (line_ref is None or lineref.text == line_ref):

                # Filter by direction if provided
                if direction_ref is not None and (
                    direction is None or direction_ref.text == direction
                ):

                    for call in estimated_journey.findall(
                        ".//siri:EstimatedCall", namespaces
                    ):
                        stop_point_name = call.find("siri:StopPointName", namespaces)

                        # Filter by stop_name if provided
                        if stop_point_name is not None and (
                            stop_name is None or stop_point_name.text == stop_name
                        ):
                            aimedArrivalTime = call.find(
                                "siri:AimedArrivalTime", namespaces
                            )
                            expectedArrivalTime = call.find(
                                "siri:ExpectedArrivalTime", namespaces
                            )
                            arrivalStatus = call.find(
                                "siri:ArrivalStatus", namespaces
                            )

                            if expectedArrivalTime is not None:
                                expected_arrival_datetime = datetime.fromisoformat(
                                    expectedArrivalTime.text
                                )

                                if expected_arrival_datetime.date() == date.today():
                                    aimed_arrival_time_formatted = (
                                        datetime.fromisoformat(
                                            aimedArrivalTime.text
                                        ).strftime("%H:%M:%S")
                                        if aimedArrivalTime is not None
                                        else "N/A"
                                    )
                                    expected_arrival_time_formatted = (
                                        expected_arrival_datetime.strftime("%H:%M:%S")
                                    )

                                    journey_data.append(
                                        {
                                            "stop_name": stop_point_name.text,
                                            "arrival_status": arrivalStatus.text
                                            if arrivalStatus is not None
                                            else "N/A",
                                            "aimed_arrival_time": aimed_arrival_time_formatted,
                                            "expected_arrival_time": expected_arrival_time_formatted,
                                            "expected_arrival_timestamp": expectedArrivalTime.text,
                                            "vehicle_ref": vehicle_ref.text
                                            if vehicle_ref is not None
                                            else "N/A",
                                            "line_ref": lineref.text,
                                            "direction_ref": direction_ref.text,
                                        }
                                    )

        # Sort journey data by the `expected_arrival_timestamp` in ascending order
        journey_data.sort(key=lambda x: x["expected_arrival_timestamp"])

        return journey_data

    else:
        print(f"Failed to retrieve data: {response.status_code}")
        return []
