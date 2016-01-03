if __name__ == '__main__':
  import argparse
  from os import getenv
  from .monitor import StopMonitor

  BUSTIME_API_KEY = getenv('BUSTIME_API_KEY')

  parser = argparse.ArgumentParser()
  parser.add_argument('-s', '--stop', type=int)
  parser.add_argument('-r', '--route')
  parser.add_argument('-m', '--max_visits', type=int, default=3)
  args = parser.parse_args()

  monitor = StopMonitor(BUSTIME_API_KEY, args.stop, args.route, args.max_visits)

  print(monitor)
