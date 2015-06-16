import math

def calculate_approach_angle(segment, intersection, influence_distance, azumith_zero_direction):
    intersection_point = intersection.firstPoint
    if intersection.distanceTo(segment.firstPoint) < intersection.distanceTo(segment.lastPoint):
        next_point = segment.positionAlongLine(influence_distance).firstPoint
    else:
        next_point = segment.positionAlongLine(segment.length - influence_distance).firstPoint

    if azumith_zero_direction == "N":
        return angle_between_two_vectors((0, 1), (intersection_point.X - next_point.X, intersection_point.Y - next_point.Y))
    else:
        return angle_between_two_vectors((1, 0), (intersection_point.X - next_point.X, intersection_point.Y - next_point.Y))


def angle_between_two_vectors(vector1, vector2):
    vector11_sum = 0
    vector12_sum = 0
    vector22_sum = 0
    for i in range(len(vector1)):
        vector11_sum += vector1[i] ** 2
        vector12_sum += vector1[i] * vector2[i]
        vector22_sum += vector2[i] ** 2

    try:
        angle = math.acos(vector12_sum / math.sqrt(vector11_sum*vector22_sum)) * 180 / math.pi
    except ZeroDivisionError:
        return -1
    if angle_larger_than_pi(vector1, vector2):
        angle = 360 - angle
    return angle


def angle_larger_than_pi(vector1, vector2):
    # clockwise angle from vector1 to vector2
    return vector1[0] * vector2[1] - vector1[1] * vector2[0] > 0


# Convert angle to direction descriptor
def angle_to_direction(angle, azumith_zero_direction):
    if azumith_zero_direction == "E":
        angle = angle + 90 if angle <= 270 else angle + 90 - 360
    if angle >= 337.5 or angle < 22.5:
        return "North"
    elif 22.5 <= angle < 67.5:
        return "NorthEast"
    elif 67.5 <= angle < 112.5:
        return "East"
    elif 112.5 <= angle < 157.5:
        return "SouthEast"
    elif 157.5 <= angle < 202.5:
        return "South"
    elif 202.5 <= angle < 247.5:
        return "SouthWest"
    elif 247.5 <= angle < 292.5:
        return "West"
    else:
        return "NorthWest"

def geodesic_angle_to_circular_angle(angle):
    return angle if angle > 0 else angle + 360

def geodesic_angle_to_direction(angle):
    if -22.5 < angle <=22.5:
        return "North"
    elif 22.5 < angle <= 67.5:
        return "NorthEast"
    elif 67.5 < angle <= 112.5:
        return "East"
    elif 112.5 < angle <= 157.5:
        return "SouthEast"
    elif angle > 157.5 or angle <= -157.5:
        return "South"
    elif -157.5 < angle <= -112.5:
        return "SouthWest"
    elif -112.5 < angle <= -67.5:
        return "West"
    else:
        return "NorthWest"