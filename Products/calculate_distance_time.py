from haversine import haversine, Unit

SHOP_LOCATION = (-1.6629332253698739, 29.887313910965002)  # your shop coordinates

def calculate_distance_and_time(order_lat, order_long, avg_speed_kmh=40):
    user_location = (order_lat, order_long)
    distance_km = haversine(SHOP_LOCATION, user_location, unit=Unit.KILOMETERS)
    time_min = (distance_km / avg_speed_kmh) * 60  # convert to minutes
    return distance_km, round(time_min)
