"""
Small library for all classes relevant to modelling the London Underground, for Assignment 13
These are used in place of tuples
"""

__author__ = 'Drullkus'


class RailLine:
  """
  Represents an entire line in which contains multiple stations

  Follows CSV format "name","colour","stripe"
  """
  def __init__(self, name, color, stripe):
    self.name = name
    self.color = color
    self.stripe = stripe

  def __repr__(self) -> str:
    return f'RailLine({self.name}, {self.color}, {self.stripe})'

  def __str__(self) -> str:
    return self.name

class Station:
  """
  Represents a station and some additional relevant info

  Follows CSV format "latitude","longitude","name","display_name","zone","total_lines","rail"
  """
  def __init__(self, latitude, longitude, name, display_name, zone, total_lines, rail):
    self.geo_coords = float(longitude), float(latitude)  # Swizzle coordinate components to better match x,y usage
    self.name = name
    self.display_name = name if display_name == 'NULL' else '\n'.join(display_name.split('<br />'))
    self.zone = zone
    self.total_lines = total_lines
    self.rail = rail

  def __repr__(self) -> str:
    return f'''Station({self.geo_coords[0]}, {self.geo_coords[1]}, {self.name}, {self.display_name},
    {self.zone}, {self.total_lines}, {self.rail})'''
  
  def coords(self) -> tuple[float, float]:
    return self.geo_coords
