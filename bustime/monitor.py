import json
import requests
import sys

STOP_MONITORING_ENDPOINT = 'http://bustime.mta.info/api/siri/stop-monitoring.json'
FEET_PER_METER = 3.28084
FEET_PER_MILE = 5280

class StopMonitor(object):
  def __init__(self, api_key, stop_id, route=None, max_visits=3):
    self.api_key = api_key
    self.stop_id = stop_id
    self.route = route
    self.max_visits = max_visits
    self.visits = []
    self.error = None

    if not api_key:
      sys.exit('API key must be present')

    if not self.stop_id:
      sys.exit('You must provide a stop ID')

    params = {
      'key': self.api_key,
      'OperatorRef': 'MTA',
      'MonitoringRef': self.stop_id,
      'MaximumStopVisits': self.max_visits,
    }

    if self.route:
      params['LineRef'] = 'MTA NYCT_%s' % self.route.upper()

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
    if self.error:
      return self.error
    else:
      output = []
      stop_name = self.visits[0].monitored_stop if len(self.visits) > 0 else None
      if stop_name:
        output.append(stop_name)

      if len(self.visits) == 0:
        output.append('No buses en route')

      for visit in self.visits:
        output.append(str(visit))

      return '\n'.join(output)

class Visit(object):
  def __init__(self, raw_visit):
    self.route = raw_visit['MonitoredVehicleJourney']['PublishedLineName']
    call = raw_visit['MonitoredVehicleJourney']['MonitoredCall']
    distances = call['Extensions']['Distances']
    self.monitored_stop = call['StopPointName']
    self.stops_away = distances['StopsFromCall']
    self.distance = round(distances['DistanceFromCall'] * FEET_PER_METER / FEET_PER_MILE, 2)

  def __str__(self):
    return ('{} {} stops/{}mi').format(self.route, self.stops_away, self.distance)
