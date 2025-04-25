import random
import colorsys

def rgb_distance(color1, color2):
    """
    Calculate the Euclidean distance between two colors in RGB space.
    
    Args:
        color1 (tuple): (R, G, B) values for the first color.
        color2 (tuple): (R, G, B) values for the second color.
    
    Returns:
        float: The Euclidean distance.
    """
    return ((color1[0] - color2[0]) ** 2 +
            (color1[1] - color2[1]) ** 2 +
            (color1[2] - color2[2]) ** 2) ** 0.5

def is_color_distinct(color, colors, threshold=50):
    """
    Check if a color is distinct enough from a list of colors based on a distance threshold.
    
    Args:
        color (tuple): (R, G, B) for the color to check.
        colors (list): List of (R, G, B) colors.
        threshold (float): Minimum distance required between colors.
    
    Returns:
        bool: True if the color is distinct from all colors in the list.
    """
    for c in colors:
        if rgb_distance(color, c) < threshold:
            return False
    return True

def random_color():
    """
    Generate a random RGB color.
    
    Returns:
        tuple: (R, G, B) where each value is between 0 and 255.
    """
    return (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))

def hsv_to_rgb(h, s, v):
    """
    Convert an HSV color to RGB.
    
    Args:
        h (float): Hue value (0 to 360).
        s (float): Saturation (0 to 1).
        v (float): Value (0 to 1).
    
    Returns:
        tuple: (R, G, B) with each value in 0-255.
    """
    rgb = colorsys.hsv_to_rgb(h / 360.0, s, v)
    return (int(rgb[0] * 255), int(rgb[1] * 255), int(rgb[2] * 255))

def generate_distinct_colors(n):
    """
    Generate n distinct colors using evenly spaced hues.
    
    Args:
        n (int): Number of colors.
    
    Returns:
        list: List of (R, G, B) tuples.
    """
    colors = []
    for i in range(n):
        hue = (360.0 * i / n) % 360
        # Use full saturation and value for bright colors.
        color = hsv_to_rgb(hue, 1.0, 1.0)
        colors.append(color)
    return colors
