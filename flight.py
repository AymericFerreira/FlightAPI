import requests
import sys
import json
import ast

def create_session():
    country = 'FR'
    currency = 'CAD'
    locale = 'fr-FR'
    originPlace = 'YQB-sky'
    destinationPlace = 'CDG-sky'
    departureDate = '2019-12-20'
    returnDate = '2020-01-03'
    cabinClass = 'economy'
    adults = 1

    return requests.post(
        "https://skyscanner-skyscanner-flight-search-v1.p.rapidapi.com/apiservices/pricing/v1.0",
        headers={
            "X-RapidAPI-Host": "skyscanner-skyscanner-flight-search-v1.p.rapidapi.com",
            "X-RapidAPI-Key": YOURAPIKEY,
            "Content-Type": "application/x-www-form-urlencoded",
        },
        data={
            "inboundDate": returnDate,
            "cabinClass": cabinClass,
            "children": 0,
            "infants": 0,
            "country": country,
            "currency": currency,
            "locale": locale,
            "originPlace": originPlace,
            "destinationPlace": destinationPlace,
            "outboundDate": departureDate,
            "adults": adults,
        },
    )

response = create_session()
if response.status_code != 201:
    print(f"error {response.status_code}, the program can't continue, see HTML error codes on Google for more info)")
    sys.exit()
else:
    print(f"Session created with success")
# print(response.headers["Location"])
key = response.headers["Location"].split('/')[-1]
# print(key)

def get_session(key):
    request_string = f'https://skyscanner-skyscanner-flight-search-v1.p.rapidapi.com/apiservices/pricing/uk2/v1.0/{key}?sortType=price&sortOrder=asc&pageIndex=0&pageSize=10'
    return requests.get(
        request_string,
        headers={
            "X-RapidAPI-Host": "skyscanner-skyscanner-flight-search-v1.p.rapidapi.com",
            "X-RapidAPI-Key": "ea607b75f4msh7fad7ab7fad19d8p10d9c5jsn9db67cde0a57",
        },
    )

final_response = get_session(key)

if final_response.status_code == 200:
    print('Connection done, retrieving data')

def compute_results(response):
    content = final_response.content.decode('utf-8') # Decode using the utf-8 encoding
    json_content = json.dumps(content)

    text_dic = ast.literal_eval(json_content)
    return json.loads(text_dic)
    
result_dic = compute_results(final_response)

class flightInformation:
    def __init__(self, originPlace, destinationPlace, departureDate, returnDate, cabinClass, numberOfPersons, currency,
             price, company, transfert, url, accessDate, accessHour):
        self.originPlace = originPlace
        self.destinationPlace = destinationPlace
        self.departureDate = departureDate
        self.returnDate = returnDate
        self.cabinClass = cabinClass
        self.numberOfPersons = numberOfPersons
        self.price = price
        self.company = company
        self.transfert = transfert
        self.url = url
        self.currency = currency
        self.accessDate = accessDate
        self.accesHour = accessHour
        
class Agent:
    def __init__(self, Id, name):
        self.Id = Id
        self.name = name

class Legs:
    def __init__(self, Id, segmentId, originStation, destinationStation, departureDateTime, arrivalDateTime, duration,
        numberOfStops, carriers):
        self.Id = Id
        self.segmentId = segmentId
        self.originStation = originStation
        self.destinationStation = destinationStation
        self.departureDateAndHour = departureDateTime
        self.arrivalDateAndHour = arrivalDateTime
        self.duration = duration
        self.numberOfStops = numberOfStops
        self.carriers = carriers
        
    
class Segment:
    def __init__(self, Id, originStation, destinationStation, departureDateTime, arrivalDateTime, carrier, duration):
        self.Id = Id 
        self.originStation = originStation
        self.destinationStation = destinationStation
        self.departureDateTime = departureDateTime
        self.arrivalDateTime = arrivalDateTime
        self.carrier = carrier
        self.duration = duration
        

class Places:
    def __init__(self, Id, code, name, parentId=None):
        self.Id = Id
        self.parentId = parentId
        self.code = code
        self.name = name
    
    def convert_id_to_code(self):
        return self.code
    
    def convert_id_to_name(self):
        return self.name
        
# class flightStatistics:
#     def create_flight_info(self, destinationPlace, departureDate, returnDate, cabinClass, numberOfPersons, currency,
#              price, company, transfert, url)
        
def generate_itineraries(result_dic):
    return [
        flightInformation(
            result_dic["Query"]["OriginPlace"],
            result_dic["Query"]["DestinationPlace"],
            result_dic["Query"]["OutboundDate"],
            result_dic["Query"]["InboundDate"],
            result_dic["Query"]["CabinClass"],
            result_dic["Query"]["Adults"]
            + result_dic["Query"]["Children"]
            + result_dic["Query"]["Infants"],
            result_dic["Query"]["Currency"],
            item["PricingOptions"][0]["Price"],
            'random-company',
            'random_number_of_transfert',
            item["PricingOptions"][0]["DeeplinkUrl"],
            'random_access_date',
            'random_acces_hour',
        )
        for item in result_dic["Itineraries"]
    ]
    
def generate_segment(result_dic):
    return [
        Segment(
            item["Id"],
            item["OriginStation"],
            item["DestinationStation"],
            item["DepartureDateTime"],
            item["ArrivalDateTime"],
            item["Carrier"],
            item["Duration"],
        )
        for item in result_dic["Segments"]
    ]
    
def generate_legs(result_dic):
    return [
        Legs(
            item["Id"],
            item["SegmentIds"],
            item["OriginStation"],
            item["DestinationStation"],
            item["Departure"],
            item["Arrival"],
            item["Duration"],
            item["Stops"],
            item["Carriers"],
        )
        for item in result_dic["Legs"]
    ]
    
def generate_agent(result_dic):
    return [Agent(item["Id"], item["Name"]) for item in result_dic["Agents"]]
    
def generate_places(result_dic):
    placesList = []
    for item in result_dic["Places"]:
        if len(item) == 4:
            placesList.append(Places(item["Id"], item["Code"], item["Name"]))
        else:
            placesList.append(
                Places(
                    item["Id"], item["Code"], item["Name"], item["ParentId"]
                )
            )

    return placesList
    
    
flightList = generate_itineraries(result_dic)
segmentList = generate_segment(result_dic)
agentList = generate_agent(result_dic)
placesList = generate_places(result_dic)
legsList = generate_legs(result_dic)
