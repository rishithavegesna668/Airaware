
def get_category(aqi):

    if aqi <= 50:
        return "Good"

    elif aqi <= 100:
        return "Moderate"

    elif aqi <= 150:
        return "Unhealthy for Sensitive Groups"

    elif aqi <= 200:
        return "Unhealthy"

    elif aqi <= 300:
        return "Very Unhealthy"

    else:
        return "Hazardous"


def get_alert(aqi):

    if aqi <= 50:
        return "Air quality is safe. Enjoy outdoor activities."

    elif aqi <= 100:
        return "Air quality is acceptable. Sensitive people should take care."

    elif aqi <= 150:
        return "Wear a mask if going outside."

    elif aqi <= 200:
        return "Limit outdoor activities. Stay indoors if possible."

    elif aqi <= 300:
        return "Avoid outdoor activities. Keep windows closed."

    else:
        return "Hazardous air quality! Stay indoors."


if __name__ == "__main__":

    test_values = [35, 85, 130, 175, 250, 350]

    for val in test_values:

        category = get_category(val)
        alert = get_alert(val)

        print(f"AQI {val} → {category}")
        print(f"Alert: {alert}")
        print()