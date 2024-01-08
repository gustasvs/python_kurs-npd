from math import sin, cos, pi, atan2, hypot, sqrt
import math
import random
from settings import *
import json


def calculate_centroid(points):
    x_sum, y_sum = 0, 0
    for (x, y) in points:
        x_sum += x
        y_sum += y
    return x_sum / len(points), y_sum / len(points)

def sort_points(points):
    centroid = calculate_centroid(points)

    def sort_key(point):
        return math.atan2(point[1] - centroid[1], point[0] - centroid[0])

    return sorted(points, key=sort_key)

def check_wall_collisions(self):
        for wall in self.game.walls:
            if wall != self and self.rect.colliderect(wall.rect):
                return True
        return False

def get_extended_ray_side(player_pos, corner, wall):
    # Get all corners and find the indices for shared_edge
    corners = [
        wall.rect.topleft,
        wall.rect.topright,
        wall.rect.bottomright,
        wall.rect.bottomleft
    ]
    corner_index = corners.index(corner)
    prev_index = (corner_index - 1) % 4
    next_index = (corner_index + 1) % 4

    # Vectors from the player to the current corner and to the next and previous corners
    player_to_corner = (corner[0] - player_pos[0], corner[1] - player_pos[1])
    player_to_prev_corner = (corners[prev_index][0] - player_pos[0], corners[prev_index][1] - player_pos[1])
    player_to_next_corner = (corners[next_index][0] - player_pos[0], corners[next_index][1] - player_pos[1])

    # Cross products to determine the 'winding' direction around the player
    cp_prev = cross_product(player_to_corner, player_to_prev_corner)
    cp_next = cross_product(player_to_corner, player_to_next_corner)

    # Determine which side to extend the ray based on the winding order
    if cp_prev > 0 > cp_next:
        # The player is 'inside' the winding order, extend to the right
        return 1
    elif cp_next > 0 > cp_prev:
        # The player is 'outside' the winding order, extend to the left
        return -1
    else:
        # If both cross products have the same sign, the player is aligned with the edge
        # Default to extending to the right in this case
        return -1 if cp_next > 0 else 1


def cross_product(v1, v2):
    return v1[0] * v2[1] - v1[1] * v2[0]


def count_intersections_with_wall(player_pos, corner, wall):
    count = 0
    extended_point = (corner[0] + (corner[0] - player_pos[0]) * 10, corner[1] + (corner[1] - player_pos[1]) * 10)

    edges = [
        (wall.rect.topleft, wall.rect.topright),
        (wall.rect.topright, wall.rect.bottomright),
        (wall.rect.bottomright, wall.rect.bottomleft),
        (wall.rect.bottomleft, wall.rect.topleft)
    ]
    for edge_start, edge_end in edges:
        
        if do_intersect(corner, extended_point, edge_start, edge_end):
            count += 1
    return count

def get_edge_containing_corner(corner, edges):
    # Find which edge of the wall contains the corner
    for i, edge in enumerate(edges):
        if corner in edge:
            return edge
    return None


def calculate_max_distance_to_corners(px, py, map_right, map_bottom):
    distances_to_corners = [
        math.hypot(px, py),  # distance to top-left corner (0, 0)
        math.hypot(map_right - px, py),  # distance to top-right corner
        math.hypot(px, map_bottom - py),  # distance to bottom-left corner
        math.hypot(map_right - px, map_bottom - py)  # distance to bottom-right corner
    ]
    return max(distances_to_corners)

def calculate_distance_to_map_boundary(player_pos, angle, walls, current_wall):
    # Map boundaries

    map_left = 0
    map_top = 0
    map_right = ekplat
    map_bottom = ekgar


    # Player position
    px, py = player_pos

    # Ray direction
    dx = math.cos(angle) 
    dy = math.sin(angle) 

    # Initialize distances to be a large number
    distances = []
    hit = True
    
    # # Calculate intersections with walls
    # for wall in walls:
    #     if wall != current_wall:
    #         edges = [
    #             (wall.rect.topleft, wall.rect.topright),
    #             (wall.rect.topright, wall.rect.bottomright),
    #             (wall.rect.bottomright, wall.rect.bottomleft),
    #             (wall.rect.bottomleft, wall.rect.topleft)
    #         ]
            
    #         for edge_start, edge_end in edges:
    #             intersection = get_intersection(player_pos, (px + dx * max_distance, py + dy * max_distance), edge_start, edge_end)
    #             if intersection is not None:
    #                 distances.append(math.hypot(intersection[0] - px, intersection[1] - py))
    #                 # print(f"Hit object at angle: {math.degrees(angle)}")
    #                 hit = False
    #                 # print(math.hypot(wall.rect.right - px, wall.rect.top - py))
    # # Check intersection with each of the four boundaries
    # # Left boundary
    # if hit:
        # print(f"did NOT hit an object at angle: {math.degrees(angle)}")
    if dx < 0:
        distances.append((map_left - px) / dx)
    # Right boundary
    if dx > 0:
        distances.append((map_right - px) / dx)
    # Top boundary
    if dy < 0:
        distances.append((map_top - py) / dy)
    # Bottom boundary
    if dy > 0:
        distances.append((map_bottom - py) / dy)

    # Compute the actual distance to the closest boundary or wall
    min_distance = min(distances)

    # Convert distance to vector length if not already
    distance_to_boundary_or_wall = min_distance
    # print(distances)
    return distance_to_boundary_or_wall




def do_intersect(p1, q1, p2, q2):
    # Utility function to know if two points are on the same side of a line
    def on_same_side(p, q, a, b):
        cp1 = (b[0] - a[0]) * (p[1] - a[1]) - (b[1] - a[1]) * (p[0] - a[0])
        cp2 = (b[0] - a[0]) * (q[1] - a[1]) - (b[1] - a[1]) * (q[0] - a[0])
        return cp1 * cp2 >= 0

    if not on_same_side(p1, q1, p2, q2) and not on_same_side(p2, q2, p1, q1):
        return True

    return False

def get_intersection(p1, q1, p2, q2):
    # Function to calculate the determinant
    def det(a, b, c, d):
        return a * d - b * c

    # Calculate the parts of the line equations
    a1, b1 = q1[1] - p1[1], p1[0] - q1[0]
    c1 = a1 * p1[0] + b1 * p1[1]
    a2, b2 = q2[1] - p2[1], p2[0] - q2[0]
    c2 = a2 * p2[0] + b2 * p2[1]

    # Calculate the determinant
    delta = det(a1, b1, a2, b2)

    # If the determinant is zero, lines are parallel or coincident
    if delta == 0:
        return None

    # Find the intersection point
    x = det(c1, b1, c2, b2) / delta
    y = det(a1, c1, a2, c2) / delta

    # Check if the intersection point lies within both line segments
    if (min(p1[0], q1[0]) <= x <= max(p1[0], q1[0]) and
        min(p1[1], q1[1]) <= y <= max(p1[1], q1[1]) and
        min(p2[0], q2[0]) <= x <= max(p2[0], q2[0]) and
        min(p2[1], q2[1]) <= y <= max(p2[1], q2[1])):
        return (x, y)

    return None


def collide_hit_rect(one, two):
    return one.hit_rect.colliderect(two.rect)

def get_line(start, end):
    """Bresenham's Line Algorithm
    Produces a list of tuples from start and end
    """
    # Setup initial conditions
    x1, y1 = start
    x2, y2 = end
    dx = x2 - x1
    dy = y2 - y1
 
    # Determine how steep the line is
    is_steep = abs(dy) > abs(dx)
 
    # Rotate line
    if is_steep:
        x1, y1 = y1, x1
        x2, y2 = y2, x2
 
    # Swap start and end points if necessary and store swap state
    swapped = False
    if x1 > x2:
        x1, x2 = x2, x1
        y1, y2 = y2, y1
        swapped = True
 
    # Recalculate differentials
    dx = x2 - x1
    dy = y2 - y1
 
    # Calculate error
    error = int(dx / 2.0)
    ystep = 1 if y1 < y2 else -1
 
    # Iterate over bounding box generating points between start and end
    y = y1
    points = []
    for x in range(x1, x2 + 1):
        coord = (y, x) if is_steep else (x, y)
        points.append(coord)
        error -= abs(dy)
        if error < 0:
            y += ystep
            error += dx
 
    # Reverse the list if the coordinates were swapped
    if swapped:
        points.reverse()
    return points


def get_angle(origin, destination):
    x_dist = destination[0] - origin[0]
    y_dist = destination[1] - origin[1]
    return atan2(-y_dist, x_dist) % (2 * pi)

def project(pos, angle, distance):
    """Returns tuple of pos projected distance at angle
    adjusted for pygame's y-axis.
    """
    return (pos[0] + (cos(angle) * distance),
            pos[1] - (sin(angle) * distance))
    

def distance(pos1, pos2):
    return math.sqrt((pos1[0] - pos2[0])**2 + (pos1[1] - pos2[1])**2)

def randomInCircle(pos, radius):
    circle_r = radius
    # center of the circle (x, y)
    circle_x = pos[0]
    circle_y = pos[1]
    # random angle
    alpha = 2 * pi * random.random()
    # random radius
    r = circle_r * sqrt(random.random())
    # calculating coordinates
    x = r * cos(alpha) + circle_x
    y = r * sin(alpha) + circle_y
    return (x, y)


def save_player_stats(player_stats, filename='player_stats.json'):
    with open(filename, 'w') as file:
        json.dump(player_stats, file)

def load_player_stats(filename='player_stats.json'):
    try:
        with open(filename, 'r') as file:
            player_stats = json.load(file)
        return player_stats
    except:
        return None
