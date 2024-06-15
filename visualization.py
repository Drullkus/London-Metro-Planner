#!/usr/bin/env python
"""
Extra credit of AS13: Visualizing the London Tube

Longitude Range: -0.224301, 0.251
Latitude Range: 51.4022, 51.7052
"""

__author__ = 'Drullkus'

import as13 as metro_data
import dearpygui.dearpygui as dpg
from subway_lib import Station


def hex_to_color(hex_str: str, transparency: int = 255):
  if hex_str == 'NULL':
    return 0, 0, 0, 0  # Full transparency
  hex_str = f'{hex_str[:6]:>06}'
  return int(hex_str[0:2], 16), int(hex_str[2:4], 16), int(hex_str[4:6], 16), transparency


padding = 0.025
frame_x_min, frame_y_min = metro_data.min_lon - padding, metro_data.min_lat - padding
frame_x_max, frame_y_max = metro_data.max_lon + padding, metro_data.max_lat + padding
frame_min, frame_max = (frame_x_min, frame_y_min), (frame_x_max, frame_y_max)

_text_width = 350

st_coords: list[float] = []  # Sequentially alternates x, y components
station_datas: list[tuple[tuple[int, int, int, int], str]] = []
for station in metro_data.id_stations.values():
  st_coords.extend(station.coords())

  adjoined_rails = '\n'.join(map(lambda s: f'\t{s}', map(str, metro_data.st_routes[station])))

  st_color = hex_to_color(list(metro_data.st_routes[station])[0].color)
  st_tooltip = f'{station.name}\n\nConnected Lines:\n{adjoined_rails}'
  station_datas.append((st_color, st_tooltip))

node_radius = 4
node_diam = node_radius * 2
node_and_half = node_diam * 1.5
node_double = node_diam * 2

first_station, second_station = None, None


def _draw_stations(sender, plot_data):
  """
  Live code: rendered every frame
  """
  global first_station, second_station, instr_panel  # These variables need binding to outer scope
  do_chart = False

  _helper_data = plot_data[0]
  # Coordinates, transformed by user behavior with the plot
  transformed_x, transformed_y = plot_data[1], plot_data[2]
  mouse_x_pixel_space = _helper_data['MouseX_PixelSpace']
  mouse_y_pixel_space = _helper_data['MouseY_PixelSpace']

  dpg.delete_item(sender, children_only=True, slot=2)
  dpg.push_container_stack(sender)
  dpg.configure_item('stations', tooltip=False)

  # For some reason, is_mouse_button_clicked() doesn't work so is_mouse_button_down() must be used
  is_clicked = dpg.is_mouse_button_down(dpg.mvMouseButton_Left)

  for st_enum in range(0, len(transformed_x)):
    a_station: Station = metro_data.enum_stations[st_enum][1]

    # Draw station label text to the right of the node
    label_offset = (transformed_x[st_enum] + node_and_half, transformed_y[st_enum] - node_and_half)
    dpg.draw_text(label_offset, a_station.display_name, size=node_and_half)

    # Draw node for the station
    st_data: tuple[tuple[int, int, int, int] | str] = station_datas[st_enum]
    dpg.draw_circle((transformed_x[st_enum], transformed_y[st_enum]), node_diam, fill=st_data[0])

    is_hovered = transformed_x[st_enum] + node_radius > mouse_x_pixel_space > transformed_x[st_enum
                 ] - node_radius and transformed_y[st_enum] - node_radius < mouse_y_pixel_space < \
                 transformed_y[st_enum] + node_radius

    # Draw additional circle to distinguish station for being hovered or selected
    if is_hovered or a_station in (first_station, second_station):
      dpg.draw_circle((transformed_x[st_enum], transformed_y[st_enum]), node_and_half)

    if is_hovered:
      # Render tooltip only if the station is hovered
      dpg.configure_item('stations', tooltip=True)
      dpg.set_value('station_tooltip', st_data[1])

      # If the mouse is clicked whilst the station is being hovered, then commit it for routing
      if is_clicked and a_station != second_station:  # Prevent redundant re-selection
        first_station, second_station = second_station, a_station
        is_clicked = False  # "Consume" click, prevent selecting overlapped stations instantly
        if first_station and second_station:
          do_chart = True  # Finally, charting time!

  # Convenience: Press X to swap direction between stations
  if dpg.is_key_pressed(dpg.mvKey_X) and first_station and second_station:
    first_station, second_station = second_station, first_station
    do_chart = True  # Also flag for re-charting route

  if do_chart:
    dpg.delete_item(instr_panel, children_only=True)

    instructions = metro_data.gen_route_instr(first_station, second_station)
    # Since ImGui doesn't support Ansicolors, ImGui tables are used instead for Background colors
    with (dpg.table(header_row=False, row_background=False, parent=instr_panel, delay_search=True)
          as table_id):
      dpg.add_table_column()

      if isinstance(instructions, tuple):
        # Simple Route: Stays only in one Metro line
        with dpg.table_row():
          dpg.add_text(instructions[1])

        dpg.highlight_table_cell(table_id, 0, 0, hex_to_color(instructions[0].st_color))
      else:
        # Disjoint Route: Route requires crossing of multiple Metro lines
        for idx, row_info in enumerate(instructions):
          with dpg.table_row():
            if isinstance(row_info, str):  # Instructs which Metro line to switch to
              dpg.add_text(row_info, wrap=_text_width)
            else:  # Instructs which stops to wait through until a desired stop for disembarking
              dpg.add_text(row_info[1], wrap=_text_width)
              dpg.highlight_table_cell(table_id, idx, 0, hex_to_color(row_info[0].color))

  dpg.pop_container_stack()


dpg.create_context()
dpg.create_viewport(title='Metro Route Planner', x_pos=0, y_pos=0)
dpg.setup_dearpygui()

dpg.maximize_viewport()  # Make window as big as the screen

window_config: dict = {
  'label': 'London Tube Planner',
  'no_close': True,
  'no_move': True,
  'no_resize': True,
  'no_saved_settings': True,
  'no_scroll_with_mouse': True,
  'no_scrollbar': True,
  'no_title_bar': True
}

with dpg.window(**window_config) as window:
  dpg.set_primary_window(window, True)

  with dpg.group(horizontal=True):
    with dpg.child_window(width=_text_width + 50):
      dpg.add_text("""
Welcome to the London Metro Planner! Click any two stations to chart a route between them. \
Press X on the keyboard to swap order of station endpoints.

Drag the metro map to move view. Scroll with the Cursor over the Metro Map to zoom in or out. \
Double-click to reset view.
""", wrap=_text_width, indent=False)

      instr_panel = dpg.add_child_window()  # Container to populate with metro route instructions

      dpg.add_text('Click any two stations to chart a route between them.', wrap=_text_width,
                   indent=False, parent=instr_panel)

    with dpg.plot(label='London Metro Map', no_title=True, height=-1, width=-1, equal_aspects=True):
      dpg.add_plot_legend()

      dpg.draw_rectangle(frame_min, frame_max, thickness=0.001, fill=(255, 255, 255, 64))

      for line, segments in metro_data.line_edges.items():
        segment_color = hex_to_color(line.color, 64)
        for edge in segments:
          dpg.draw_line(
            edge[0].geo_coords, edge[1].geo_coords,
            thickness=0.001, color=segment_color, label=line.name
          )

      x_axis = dpg.add_plot_axis(dpg.mvXAxis, label='Longitude')
      with dpg.plot_axis(dpg.mvYAxis, label='Latitude'):
        with dpg.custom_series(st_coords[0::2], st_coords[1::2], 2, callback=_draw_stations,
                               tag='stations'):
          dpg.add_text('', tag='station_tooltip')

        dpg.fit_axis_data(dpg.top_container_stack())
      dpg.fit_axis_data(x_axis)

dpg.show_viewport(maximized=True)
dpg.start_dearpygui()
dpg.destroy_context()
