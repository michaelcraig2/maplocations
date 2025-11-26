File "/mount/src/maplocations/app5.py", line 112, in <module>
    st.session_state["map"] = generate_map(df, use_clusters)
                              ~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^
File "/home/adminuser/venv/lib/python3.13/site-packages/streamlit/runtime/caching/cache_utils.py", line 228, in __call__
    return self._get_or_create_cached_value(args, kwargs, spinner_message)
           ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
File "/home/adminuser/venv/lib/python3.13/site-packages/streamlit/runtime/caching/cache_utils.py", line 270, in _get_or_create_cached_value
    return self._handle_cache_miss(cache, value_key, func_args, func_kwargs)
           ~~~~~~~~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
File "/home/adminuser/venv/lib/python3.13/site-packages/streamlit/runtime/caching/cache_utils.py", line 329, in _handle_cache_miss
    computed_value = self._info.func(*func_args, **func_kwargs)
File "/mount/src/maplocations/app5.py", line 64, in generate_map
    folium.CircleMarker(
    ~~~~~~~~~~~~~~~~~~~^
        location=[row['latitude'], row['longitude']],
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    ...<4 lines>...
        popup=popup_info
        ^^^^^^^^^^^^^^^^
    ).add_to(fg)
    ^
File "/home/adminuser/venv/lib/python3.13/site-packages/folium/vector_layers.py", line 387, in __init__
    super().__init__(location, popup=popup, tooltip=tooltip)
    ~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
File "/home/adminuser/venv/lib/python3.13/site-packages/folium/map.py", line 451, in __init__
    self.location = validate_location(location) if location is not None else None
                    ~~~~~~~~~~~~~~~~~^^^^^^^^^^
File "/home/adminuser/venv/lib/python3.13/site-packages/folium/utilities.py", line 105, in validate_location
    raise ValueError(
    ...<2 lines>...
    )

