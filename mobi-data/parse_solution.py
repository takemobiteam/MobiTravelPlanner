import json
from params import *

def parse_travel_plan(input_json, problem_data):
    # Load the json file
    with open(input_json, 'r') as f:
        data = json.load(f)

    poi_type_map = get_poi_type(problem_data)

    plan = []
    days = 1
    id2location = dict()
    prev_city = None

    for route in data['routes']:
        day_plan = {
            "days": days,
            "current_city": "-",
            "transportation": "-",
            "breakfast": "-",
            "attraction": "-",
            "lunch": "-",
            "dinner": "-",
            "accommodation": "-"
        }
        days += 1
        # Obtain the current city, transportation, accommodation, breakfast, lunch, dinner, and attractions for the day
        for i in range(len(route)):
            segment = route[i]
            name = segment['name'] if 'name' in segment else "-"
            if name in poi_type_map:
                if poi_type_map[name] == POIType.RESTAURANT:
                    # check the start time of the segment to determine if it is breakfast, lunch, or dinner
                    start_time = segment['startTimeRange'][0]
                    if start_time >= BREAKFAST_START_TIME and start_time < BREAKFAST_END_TIME:
                        day_plan["breakfast"] = name
                    elif start_time >= LUNCH_START_TIME and start_time < LUNCH_END_TIME:
                        day_plan["lunch"] = name
                    elif start_time >= DINNER_START_TIME and start_time < DINNER_END_TIME:
                        day_plan["dinner"] = name
                elif poi_type_map[name] == POIType.ATTRACTION:
                    if day_plan["attraction"] == "-":
                        day_plan["attraction"] = name
                    else:
                        day_plan["attraction"] += "; " + name
                elif poi_type_map[name] == POIType.ACCOMMODATION:
                    # Only hotel if last segment of the day
                    if i == len(route) - 1:
                        day_plan["accommodation"] = name
                elif poi_type_map[name] == POIType.FLIGHT:
                    day_plan["transportation"] = name
                elif poi_type_map[name] == POIType.SELF_DRIVING:
                    day_plan["transportation"] = "Self-driving"
                    start_loc = get_location(segment['startLocation'], id2location)
                    end_loc = get_location(segment['endLocation'], id2location)
                    start_city = start_loc['name']
                    end_city = end_loc['name']
                    prev_city = end_city
                    day_plan["current_city"] = "from " + start_city + " to " + end_city
                elif poi_type_map[name] == POIType.TAXI:
                    day_plan["transportation"] = "Taxi"
                    start_loc = get_location(segment['startLocation'], id2location)
                    end_loc = get_location(segment['endLocation'], id2location)
                    start_city = start_loc['name']
                    end_city = end_loc['name']
                    prev_city = end_city
                    day_plan["current_city"] = "from " + start_city + " to " + end_city
            else:
                get_location(segment['startLocation'], id2location)
                get_location(segment['endLocation'], id2location)
        if day_plan["current_city"] == "-" and prev_city is not None:
            day_plan["current_city"] = prev_city
        plan.append(day_plan)
    return plan

def get_location(segment_loc, id2location):
    if isinstance(segment_loc, dict):
        locationId = segment_loc["@id"]
        id2location[locationId] = segment_loc
        return segment_loc
    else:
        assert(segment_loc in id2location)
        segment_loc = id2location[segment_loc]
        return segment_loc

def get_poi_type(data):
    # From input json data, obtain the name of POI -> Type: restaurant, attraction, accommodation, flight, self-driving, taxi
    poi_type_map = {}
    info = data['structured_ref_info']
    for i in range(len(info)):
        if info[i]['Info Type'] == 'Attractions':
            if info[i]['Number'] > 0:
                for name in info[i]['Structured Content']['Name'].values():
                    poi_type_map[name] = POIType.ATTRACTION
        elif info[i]['Info Type'] == 'Restaurants':
            if info[i]['Number'] > 0:
                for name in info[i]['Structured Content']['Name'].values():
                    poi_type_map[name] = POIType.RESTAURANT
        elif info[i]['Info Type'] == 'Accommodations':
            if info[i]['Number'] > 0:
                for name in info[i]['Structured Content']['NAME'].values():
                    poi_type_map[name] = POIType.ACCOMMODATION
        elif info[i]['Info Type'] == 'Flight':
            if info[i]['Number'] > 0:
                for name in info[i]['Structured Content']['Flight Number'].values():
                    poi_type_map[name] = POIType.FLIGHT
    poi_type_map['self-driving'] = POIType.SELF_DRIVING
    poi_type_map['taxi'] = POIType.TAXI
    return poi_type_map

