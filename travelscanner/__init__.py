import logging

from travelscanner.data.database import Database

from travelscanner.models.price import Price
from travelscanner.models.travel import Travel

# Setup logging
from travelscanner.models.tripadvisor_rating import TripAdvisorRating

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Connect to database
Database.connect()

# Create model tables
#Database.get_driver().drop_tables([TripAdvisorRating, Travel, Price])
#Database.get_driver().create_tables([TripAdvisorRating, Travel, Price])
