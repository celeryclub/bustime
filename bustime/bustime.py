import json
import requests
import os
import sys
from os.path import join, dirname
from dotenv import load_dotenv

load_dotenv(join(dirname(__file__), '.env'))

BUSTIME_API_KEY = os.environ.get('BUSTIME_API_KEY')

if not BUSTIME_API_KEY:
  sys.exit('BUSTIME_API_KEY enviroment variable must be present')

"""
Query the MTA BusTime stop monitoring endpoint for bus information.

Example calls:
# b70_near_me_as_json = StopMonitor(MY_API_KEY, '308100', 'B70', 2).json()
# b35_near_me_as_string = StopMonitor(MY_API_KEY, '302684', 'B35', 2)
"""

STOP_MONITORING_ENDPOINT = "http://bustime.mta.info/api/siri/stop-monitoring.json"
FEET_PER_METER = 3.28084
FEET_PER_MILE = 5280

class StopMonitor(object):
  def __init__(self, stop_id, route=None, max_visits=3):
    self.api_key = BUSTIME_API_KEY
    self.stop_id = stop_id
    self.route = route
    self.max_visits = max_visits
    self.visits = []
    self.error = None

    if not self.stop_id:
      sys.exit('You must provide a stop ID')

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

if __name__ == '__main__':
  import argparse

  parser = argparse.ArgumentParser()
  parser.add_argument('-s', '--stop', type=int)
  parser.add_argument('-r', '--route')
  parser.add_argument('-m', '--max_visits', type=int, default=3)
  args = parser.parse_args()

  monitor = StopMonitor(args.stop, args.route, args.max_visits)

  print(monitor)
