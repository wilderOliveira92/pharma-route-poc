"""
Distance calculation utilities.

Functions:
  - distancia_euclidiana: Haversine formula (returns km)
  - distancia_osrm: Real driving distance via OSRM demo server
  - melhor_distancia: Tries OSRM first, falls back to Haversine
"""
import math
import httpx


_EARTH_RADIUS_KM = 6371.0


def distancia_euclidiana(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Returns the great-circle distance between two points using the Haversine formula.

    Parameters
    ----------
    lat1, lon1 : coordinates of point 1 (degrees)
    lat2, lon2 : coordinates of point 2 (degrees)

    Returns
    -------
    float : distance in kilometres
    """
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    d_phi = math.radians(lat2 - lat1)
    d_lambda = math.radians(lon2 - lon1)

    a = math.sin(d_phi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(d_lambda / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    return _EARTH_RADIUS_KM * c


def distancia_osrm(lat1: float, lon1: float, lat2: float, lon2: float) -> float | None:
    """
    Returns driving distance in kilometres via OSRM demo server.
    Falls back to None on any error or timeout.

    OSRM expects coordinates in (longitude, latitude) order.
    """
    url = (
        f"http://router.project-osrm.org/route/v1/driving/"
        f"{lon1},{lat1};{lon2},{lat2}?overview=false"
    )
    try:
        response = httpx.get(url, timeout=3.0)
        response.raise_for_status()
        data = response.json()
        routes = data.get("routes")
        if routes:
            distance_m = routes[0]["distance"]
            return distance_m / 1000.0
        return None
    except Exception:
        return None


def melhor_distancia(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Returns the best available distance estimate in km.
    Tries OSRM first; if it fails, falls back to Haversine.
    """
    osrm = distancia_osrm(lat1, lon1, lat2, lon2)
    if osrm is not None:
        return osrm
    return distancia_euclidiana(lat1, lon1, lat2, lon2)
