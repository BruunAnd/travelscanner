from random import shuffle

import numpy as np
import sklearn.model_selection

from travelscanner.models.price import Price, JOIN
from travelscanner.models.travel import Travel
from travelscanner.models.tripadvisor_rating import TripAdvisorRating
from travelscanner.options.travel_options import RoomTypes, MealTypes


def load_unscraped_hotels():
    ret_hotels = []

    # Select distinct hotel names and areas without rating
    travels = Travel.select(Travel.hotel, Travel.country, Travel.area).distinct(). \
        join(TripAdvisorRating, join_type=JOIN.LEFT_OUTER, on=((Travel.hotel == TripAdvisorRating.hotel) &
                                                               (Travel.area == TripAdvisorRating.area) &
                                                               (Travel.country == TripAdvisorRating.country))) \
        .where(TripAdvisorRating.rating.is_null(True))

    for travel in travels:
        ret_hotels.append((travel.hotel, travel.area, travel.country))

    shuffle(ret_hotels)

    return ret_hotels


def load_prices(include_objects=False, unpredicted_only=False):
    price_objects = []

    # Get data from database with join query
    joined_prices = Travel.select(Travel, Price, TripAdvisorRating).join(TripAdvisorRating, on=(
                (Travel.country == TripAdvisorRating.country) & (Travel.hotel == TripAdvisorRating.hotel) &
                (Travel.area == TripAdvisorRating.area))).switch(Travel).join(Price)

    if unpredicted_only:
        joined_prices = joined_prices.where(Price.predicted_price.is_null())

    def is_summer_vacation(travel):
        return travel.departure_date.isocalendar()[1] in [28, 29, 30, 31]

    # Initialize arrays
    n_samples = joined_prices.count()
    features = ["Area",
                "All Inclusive", "Meal type", "Duration (days)", "Country", "Guests", "Hotel stars",
                "Days until departure", "Month", "Week", "Departure airport", "Has pool", "Has childpool",
                "Room type", "Weekday", "Day", "Vendor", "TripAdvisor rating", "Review count", "Excellent dist.",
                "Good dist.", "Average dist.", "Poor dist.", "Terrible dist.", "Official class", "Is summer vacation",
                "Sea view"]

    data = np.empty((n_samples, len(features)))
    target = np.empty((n_samples,))

    # Create area vocabulary
    area_dict = dict()
    areas = 0

    # Fill arrays with data
    for i, d in enumerate(joined_prices):
        price_objects.append(d.price)

        # Set features
        meal = MealTypes.ALL_INCLUSIVE if d.price.all_inclusive else MealTypes.parse_da(d.price.meal)
        if meal in [MealTypes.UNKNOWN, MealTypes.NOT_SPECIFIED]:
            # Sometimes the meal is in the room
            room_meal = MealTypes.parse_da(d.price.room)
            meal = room_meal if room_meal != MealTypes.UNKNOWN else meal
        room = RoomTypes.parse_da(d.price.room)

        if d.area.lower() not in area_dict:
            area_dict[d.area.lower()] = areas
            areas += 1

        data[i] = [area_dict[d.area.lower()], d.price.all_inclusive, meal, d.duration_days, d.country, d.guests, d.hotel_stars,
                   (d.departure_date - d.price.created_at.date()).days, d.departure_date.month,
                   d.departure_date.isocalendar()[1], d.departure_airport, d.has_pool, d.has_childpool, room,
                   d.departure_date.weekday(), d.departure_date.day, d.vendor, d.tripadvisorrating.rating,
                   d.tripadvisorrating.review_count, d.tripadvisorrating.excellent, d.tripadvisorrating.good,
                   d.tripadvisorrating.average, d.tripadvisorrating.poor, d.tripadvisorrating.terrible,
                   d.tripadvisorrating.official_class, is_summer_vacation(d), 'havudsigt' in d.price.room]

        # Set target value
        target[i] = d.price.price

    if include_objects:
        return data, target, features, price_objects
    else:
        return data, target, features


def split_set(x, y, train_ratio=0.8):
    return sklearn.model_selection.train_test_split(x, y, train_size=int(len(x) * train_ratio), random_state=42)
