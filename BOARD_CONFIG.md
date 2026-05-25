# Board Configuration

The `airports` file is the permanent map layout for this gift. Dad should never need to edit it.

Each non-empty line maps to one physical LED position, in order from the first LED in the strip to the last configured map LED.

Use:

- A station code like `KJFK`, `KLGA`, or `KHPN` for an airport LED.
- `NULL` for a physical LED that exists in the strip but should stay dark because it is between airports or hidden behind the board.

Before gifting the map, update `airports` to match the exact board wiring, then run:

```bash
python3 tools/validate_board_config.py
```

The validator checks:

- The number of configured positions against `LED_COUNT` in `metar.py`.
- Invalid-looking station codes.
- Duplicate airport codes.
- Extra LEDs needed if the legend is enabled.

If the validator passes and the map lights match the physical board, this file can be considered factory-set.
