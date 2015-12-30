import requests
import json
import jsonpickle

"""
Query the MTA BusTime stop monitoring endpoint for bus information.

Example calls:
# b70_near_me_as_json = StopMonitor(MY_API_KEY, '308100', 'B70', 2).json()
# b35_near_me_as_string = StopMonitor(MY_API_KEY, '302684', 'B35', 2)
"""

STOP_MONITORING_ENDPOINT = "http://bustime.mta.info/api/siri/stop-monitoring.json"
VEHICLE_MONITORING_ENDPOINT = "http://bustime.mta.info/api/siri/vehicle-monitoring.json"

FEET_PER_METER = 3.28084
FEET_PER_MILE = 5280

class StopMonitor(object):

  def __init__(self, api_key, stop_id, route, max_visits=3):
    self.api_key = api_key
    self.stop_id = stop_id
    self.route = route
    self.max_visits = max_visits
    self.visits = []
    self.error = None
    self.name = self.visits[0].monitored_stop if len(self.visits) > 0 else None

    # TODO define num_visits globally (or per instance of this class)
    params = {
      'key': self.api_key,
      'OperatorRef': 'MTA',
      'MonitoringRef': self.stop_id,
      'MaximumStopVisits': self.max_visits,
    }

    if self.route:
      params['LineRef'] = "MTA NYCT_%s" % self.route.upper()

    response = requests.get(STOP_MONITORING_ENDPOINT, params=params)
    rsp = response.json()

    try:
      delivery = rsp['Siri']['ServiceDelivery']['StopMonitoringDelivery'][0]

      if 'ErrorCondition' in delivery:
        self.error = delivery['ErrorCondition']['Description']
      else:
        raw_visits = delivery['MonitoredStopVisit']
        visits = []

        for raw_visit in raw_visits:
          visits.append(Visit(raw_visit))

        self.visits = visits

    except KeyError:
      self.error = 'The BusTime API response was invalid'

  def __str__(self):
    output = []
    if self.name:
      output.append("{}:".format(self.name))
    for visit in self.visits:
      output.append("{}. {}".format(self.visits.index(visit)+1, visit))
    if len(self.visits) == 0:
      output.append("no buses are on the way. sad :(")
    return '\n'.join(output)

  def json(self):
    response = { 'bustime': {} }

    if self.error:
      response['bustime']['error'] = json.dumps(self.error)
    else:
      response['bustime']['visits'] = jsonpickle.encode(self.visits)

    return response

# class Visit(JSONEncoder):
class Visit(object):

  def __init__(self, raw_visit):
    self.route = raw_visit['MonitoredVehicleJourney']['PublishedLineName']
    call = raw_visit['MonitoredVehicleJourney']['MonitoredCall']
    distances = call['Extensions']['Distances']
    self.monitored_stop = call['StopPointName']
    self.stops_away = distances['StopsFromCall']
    self.distance = round(distances['DistanceFromCall'] * FEET_PER_METER / FEET_PER_MILE, 2)

  def __str__(self):
    return ("{} bus {} stops away ({} miles)").format(
          self.route, self.stops_away, self.distance)

  # def default(self, o):
  #   return o.__dict__

  def __getstate__(self):
    return json.dumps({
      'route': self.route,
      'stops_away': self.stops_away,
      'distance': self.distance,
    })
