#!/usr/bin/env python
"""
Duplicated from Assignment 12

Upgraded with additional methods for traversal (start_search, _search_graph)
"""

__author__ = 'https://github.com/Drullkus'

import collections
import itertools
from functools import reduce as func_reduce
from operator import add as op_add


class _Node(dict):
  """
  Internal mutable record of edge weights in the direction of another vertex
  """
  def __init__(self, parent):
    self._parent = parent

  def __setitem__(self, key, value) -> None:
    self._parent[key]  # Polite poke to ensure existence of other edge in graph
    return super().__setitem__(key, value)

  def copy(self, new_parent):
    copied = _Node(parent=new_parent)
    copied.update(self)
    return copied

  def __delitem__(self, key) -> None:
    if key in self:  # NOOP any key misses
      return super().__delitem__(key)


class Graph:
  """
  A directed graph with arbitrary data for directional edges
  """
  def __init__(self):
    """
    shall accept no arguments and result in an empty graph containing no vertices or edges
    """
    # Nodes are lists of values. Defaults are empty and disconnected from all other nodes
    self._nodes: dict[str, _Node] = collections.defaultdict(lambda: _Node(parent=self))

  def __getitem__(self, key):
    """
    The following __getitem__() syntax shall add a vertex with value 'new_vertex' to the graph,
    disconnected from all other vertices:

    g['new_vertex']
    """
    return self._nodes.__getitem__(key)

  def __setitem__(self, key, value):
    """
    The following __setitem__() shall add/replace an edge from vertex 'a' to vertex 'b' with
    weight 10, simultaneously adding both of these vertices to the graph, if not already present:

    g['a']['b'] = 10

    Note that an edge weight such as True could serve to represent edges in an unweighted graph,
    and that complementary edges from a to b and from b to a could serve to represent an
    undirected graph.
    """
    self._nodes.__setitem__(key, value)

  def __delitem__(self, key):
    """
    Vertices and edges shall be removed using __delitem__() syntax:
    del g['a']  # Removes vertex 'a' and all associated edges
    del g['b']['c']  # Removes edge from vertex 'b' to vertex 'c', but not the vertices themselves
    """
    for connected in self._nodes.values():
      connected.__delitem__(key)

    del self._nodes[key]

  def __len__(self) -> int:
    """
    Returns the number of vertices in the graph
    """
    return len(self._nodes)

  def __contains__(self, key) -> bool:
    """
    __contains__() shall return whether a vertex or edge exists in the graph:
    'a' in g  # determines whether vertex 'a' exists
    'b' in g['a']  # determines whether there is an edge from vertex 'a' to vertex 'b'
    """
    return self._nodes.__contains__(key)

  # clear(), and copy() shall behave similarly to dict.clear() and dict.copy(), clearing all
  # vertices and edges from a graph, and returning a shallow copy of a graph (i.e., with the same
  # vertices and edges, but adding or removing vertices and
  # edges in the copy will not affect the original):
  #
  # g2 = g.copy()  # g is now a copy of g2
  # g2['c']['b'] = -9  # Modifies g2 but not g
  # g.clear()  # g is now empty
  def clear(self):
    for node in self._nodes.values():
      node.clear()

    self._nodes.clear()

  def copy(self):
    new_graph = Graph()
    for addr, node in self._nodes.items():
      new_graph._nodes[addr] = node.copy(new_graph)

    return new_graph

  def vertices(self):
    """
    vertices() shall return a set of all vertices in the graph.
    """
    return set(self._nodes)

  def _generate_edges(self):
    for key, node in self._nodes.items():
      for addr, val in node.items():
        yield (key, addr, val)

  def edges(self):
    """
    edges() shall return a set of all edges in the graph,
    as 3-tuples in the form (src, dst, weight).
    """
    return set(self._generate_edges())

  def adjacent(self, src, dst) -> bool:
    """
    adjacent(src, dst) shall return whether an edge from src to dst exists.
    """
    return dst in self._nodes[src]

  def neighbors(self, vertex) -> set:
    """
    neighbors(vertex) shall return a set of all vertices adjacent to the given vertex.
    """
    return set(self._nodes[vertex])

  def degree(self, vertex) -> int:
    """
    degree(vertex) shall return the number of edges incident on the given vertex.
    """
    return len(self.neighbors(vertex))

  def path_valid(self, vertices) -> bool:
    """
    path_valid(vertices) shall return whether a sequence of vertices is a valid path
    in the graph. Consider an empty path to be valid.
    """
    # If vertices is not empty, or path is "trivial" having only 1 element existing
    if not vertices:
      return True
    elif len(vertices) == 1:
      return vertices[0] in self._nodes
    # Path is guaranteed to be greater than 1 element, exhaust path with recursive calls
    return vertices[1] in self._nodes[vertices[0]] and self.path_valid(vertices[1:])

  def _get_weight(self, vertex, addr):
    if vertex in self._nodes:
      return self._nodes[vertex][addr]

  def path_length(self, vertices):
    """
    path_length(vertices) shall return the path length of a sequence of vertices, or None if
    the path is invalid or trivial (one vertex). The length shall the be sum of all edge weights
    (you may assume that any_weight + any_other_weight is a valid expression)

    The addition op is essential and sum() will not suffice.
    """
    if len(vertices) > 1 and self.path_valid(vertices):
      return func_reduce(op_add, itertools.starmap(self._get_weight, itertools.pairwise(vertices)))

  def _seek_path(self, src, dst, _acc: set) -> bool:
    if src == dst or src in _acc:
      return False
    _acc.add(src)

    node = self._nodes[src]
    return dst in node or any(self._seek_path(ed, dst, _acc) for ed in node if ed not in _acc)

  def are_connected(self, src, dst) -> bool:
    return self._seek_path(src, dst, set())

  def is_connected(self):
    """
    is_connected() shall return whether the graph is connected.
    """
    return all(itertools.starmap(self.are_connected, itertools.permutations(self._nodes, 2)))

  def __eq__(self, other):
    return isinstance(other, Graph) and self._nodes == other._nodes

  # Naive recursive graph-searching algorithm
  def _search_graph(self, visited: set, start, target, reducer) -> list | None:
    paths = []

    for adjacent in self[start]:
      if adjacent == target:
        return [target, start]

      if adjacent not in visited:
        visited.add(adjacent)
        if ret := self._search_graph(set(visited), adjacent, target, reducer):
          ret.append(start)
          paths.append(ret)

    return reducer(paths) if paths else None

  def start_search(self, start, target, reducer=lambda paths: min(paths, key=len)) -> list:
    ret = self._search_graph({start}, start, target, reducer)
    return list(ret)[::-1] if ret else []


if __name__ == '__main__':
  g = Graph()
  assert len(g) == 0
  assert 'wat' not in g
  assert not g.vertices()
  edges = ('a', 'c', 8), ('a', 'd', 4), ('c', 'b', 6), ('d', 'b', 10), ('d', 'c', 2)
  for (v_from, v_to, weight) in edges:
    g[v_from][v_to] = weight
  assert len(g) == 4
  assert 'a' in g
  assert 'c' in g['a']
  assert g.vertices() == set('abcd')
  assert g.edges() == set(edges)
  assert g.degree('d') == 2 and not g.degree('b')
  assert g.adjacent('a', 'c')
  assert not g.adjacent('c', 'a')
  assert g.path_valid(('a', 'c', 'b'))
  assert not g.path_valid(('c', 'b', 'a'))
  assert not g.is_connected()
  g['b']['a'] = 1
  assert g.degree('b') == 1 and g.degree('a') == 2
  assert g.path_valid(('c', 'b', 'a'))
  assert g.path_length(('c', 'b', 'a')) == 7
  assert g.are_connected('c', 'd')  # Regression case: deep linkage beyond neighbors c > b > a > d
  assert g.is_connected()
  del g['a']
  assert not g.is_connected()
  assert g.vertices() == set('bcd')
  assert g.degree('b') == 0
  g2 = g.copy()
  assert g2 == g
  g2['b']['e'] = 1
  assert g2 != g
  assert g2.vertices() == set('bcde')
  g2['e']['d'] = 15
  assert g2.is_connected()
  assert g2.path_length(('e', 'd', 'c', 'b')) == 23
  del g2['e']['d']
  assert g2.degree('e') == 0
  assert g2.vertices() == set('bcde')
  assert not g2.is_connected()
  g.clear()
  assert len(g) == 0
  assert len(g2) == 4
