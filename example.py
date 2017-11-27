import scanners
from agent import Agent
from travel_options import Airports, Countries

agent = Agent()
options = agent.get_travel_options()

# Set options for our desired travel
options.departure_airports = [Airports.AALBORG, Airports.BILLUND, Airports.COPENHAGEN]
options.destination_countries = [Countries.SPAIN, Countries.GREECE]
options.set_earliest_departure_date('27/07/2018')

# Add scanners
agent.add_scanner(scanners.TravelMarketScanner())

# Start the agent
agent.scan_loop()
