from haversine import haversine, Unit
from .models import OrderPickupLocations
SHOP_LOCATION = (-1.6629332253698739, 29.887313910965002)  # your shop coordinates

def calculate_distance_and_time(order_lat, order_long, pickup_location=None, avg_speed_kmh=40):
    if pickup_location is not None:
        try:
            pickup_location_obj = OrderPickupLocations.objects.get(id=pickup_location)
            pickup_location = (pickup_location_obj.latitude, pickup_location_obj.longitude)
        except OrderPickupLocations.DoesNotExist:
            pickup_location = None

        user_location = (order_lat, order_long)
        
        distance_km = haversine(pickup_location, user_location, unit=Unit.KILOMETERS)
        time_min = (distance_km / avg_speed_kmh) * 60  # convert to minutes
        return distance_km, round(time_min)

    else:
        user_location = (order_lat, order_long)
        distance_km = haversine(SHOP_LOCATION, user_location, unit=Unit.KILOMETERS)
        time_min = (distance_km / avg_speed_kmh) * 60  # convert to minutes
        return distance_km, round(time_min)
