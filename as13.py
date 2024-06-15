#!/usr/bin/env python
"""
Assignment 13: Holistic Route Planning

The main implementation involving the graph.
"""

__author__ = 'https://github.com/Drullkus'

import csv
import itertools
import math
import operator
from graph import Graph
from subway_lib import RailLine, Station

path = './datasets/'

with open(f'{path}lines.csv', newline='') as lines_file:
  next(lines_file)  # Skip table header
  id_lines = {row[0]: RailLine(*row[1:]) for row in csv.reader(lines_file)}

with open(f'{path}stations.csv', newline='') as stations_file:
  next(stations_file)  # Skip table header
  id_stations = {row[0]: Station(*row[1:]) for row in csv.reader(stations_file)}

with open(f'{path}routes.csv', newline='') as routes_file:
  next(routes_file)  # Skip table header
  line_edges: dict[RailLine, list[tuple[Station, Station]]] = {li: [] for li in id_lines.values()}
  for station1_id, station2_id, line_id in csv.reader(routes_file):
    line_edges[id_lines[line_id]].append((id_stations[station1_id], id_stations[station2_id]))

station_coords: list[tuple[float, float]] = list(map(Station.coords, id_stations.values()))
# Find min-max geopositional coordinate boundaries
min_lat = float(min(map(operator.itemgetter(1), station_coords)))
min_lon = float(min(map(operator.itemgetter(0), station_coords)))
max_lat = float(max(map(operator.itemgetter(1), station_coords)))
max_lon = float(max(map(operator.itemgetter(0), station_coords)))

enum_stations = list(id_stations.items())

# Simplified version of line_edges
rail_stations: dict[RailLine, set[Station]] = {rail: set() for rail in line_edges}
# For reverse station -> RailLine lookup
st_routes: dict[Station, set[RailLine]] = {li: set() for li in id_stations.values()}
for rail_line, station_connections in line_edges.items():
  for station in set(itertools.chain.from_iterable(station_connections)):
    st_routes[station].add(rail_line)
    rail_stations[rail_line].add(station)

# Same LUT as above, except only with stations connecting multiple lines
st_multi_routes: dict[Station, set[RailLine]] = dict(filter(lambda t: len(t[1]) > 1,
                                                            st_routes.items()))

# Super-graph where all connections between routes are mapped.
# Each vertex is a rail line, in which its connections are lists of stations intersecting the lines
rail_supergraph = Graph()
for overlapped_station, routes in st_multi_routes.items():
  for rail1, rail2 in itertools.combinations(routes, 2):
    if rail2 not in rail_supergraph[rail1]:
      rail_supergraph[rail1][rail2] = list()
    if rail1 not in rail_supergraph[rail2]:
      rail_supergraph[rail2][rail1] = list()

    rail_supergraph[rail1][rail2].append(overlapped_station)
    rail_supergraph[rail2][rail1].append(overlapped_station)

rail_subgraphs: dict[RailLine, Graph] = {}
for rail_line, station_pairs in line_edges.items():
  for station1, station2 in station_pairs:
    if rail_line not in rail_subgraphs:
      rail_subgraphs[rail_line] = Graph()

    coords1, coords2 = station1.geo_coords, station2.geo_coords

    dist = math.sqrt((coords2[0] - coords1[0])**2 + (coords2[1] - coords1[1])**2)

    rail_graph: Graph = rail_subgraphs[rail_line]
    rail_graph[station1][station2] = dist
    rail_graph[station2][station1] = dist


def route_rail(line: RailLine, st_start: Station, st_goal: Station) -> list[Station]:
  return rail_subgraphs[line].start_search(st_start, st_goal)


def route_closest(line: RailLine, st_start: Station, goals: list[Station]) -> list[Station]:
  return min((route_rail(line, st_start, st_goal) for st_goal in goals), key=len)


def route_between_lines(rl_start: RailLine, rl_goal: RailLine) -> list[RailLine]:
  return rail_supergraph.start_search(rl_start, rl_goal)


def gen_st_instr(line: RailLine, stations: list[Station]) -> tuple[RailLine, str]:
  stations = list(map(operator.attrgetter("name"), stations))
  mid_stations = '\n'.join(map(lambda txt: '\t\t- ' + txt, stations[1:-1]))
  mid_steps = f'\n\n\tWait through:\n{mid_stations}\n\n' if len(stations) > 2 else '\n\n'
  rail_info = f'Use the {line.name}:'
  return line, f'{rail_info}\n\tEmbark at: {stations[0]}{mid_steps}\tDisembark at: {stations[-1]}'


def gen_route_instr(st_start: Station, st_goal: Station) -> (tuple[RailLine, str] |
                                                             list[str | tuple[RailLine, str]]):
  overlaps: set[RailLine] = st_routes[st_start].intersection(st_routes[st_goal])

  if len(overlaps) > 0:
    # Stations are not disjoint by Metro line connections, permute lines & minimize for stops passed
    possibilities = ((overlap, route_rail(overlap, st_start, st_goal)) for overlap in overlaps)
    return gen_st_instr(*min(possibilities, key=len))
  else:  # Reached only if stations are disjoint by rail-lines
    # Start determining complex route by first reducing necessary line transfers
    rails = itertools.product(st_routes[st_start], st_routes[st_goal])
    super_route = list(min(itertools.starmap(route_between_lines, rails), key=len))

    routing_instrs: list[str | tuple[RailLine, str]] = []
    mid_disembark: Station = st_start

    for rail_start, rail_goal in itertools.pairwise(super_route):
      # Seek for closest possible station to exit the first Metro line, with stops minimized
      target_stations = list(rail_stations[rail_start].intersection(rail_stations[rail_goal]))
      closest_for_entry = route_closest(rail_start, mid_disembark, target_stations)
      mid_disembark = closest_for_entry[-1]

      # Actually add data for return
      routing_instrs.append(gen_st_instr(rail_start, closest_for_entry))
      routing_instrs.append(f'Line transfer {rail_start.name} -> {rail_goal.name}')

    last_leg = gen_st_instr(super_route[-1], route_rail(super_route[-1], mid_disembark, st_goal))
    routing_instrs.append(last_leg)

    return routing_instrs


if __name__ == '__main__':
  assert len(id_stations) == 308  # Total stations
  assert len(id_lines) == 13  # Total metro lines

  assert len(id_stations) == len(st_routes)  # Parity check
  assert len(id_lines) == len(line_edges)  # Parity check

  assert len(st_multi_routes) == 78  # Total stations s. t. passengers can switch lines

  assert (min_lon, max_lon) == (-0.611, 0.251)  # Longitude bounds, immutable from source
  assert (min_lat, max_lat) == (51.4022, 51.7052)  # Latitude bounds, immutable from source

  print('All assertions passed!')
