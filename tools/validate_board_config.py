#!/usr/bin/env python3

import ast
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
AIRPORT_RE = re.compile(r"^[A-Z0-9]{3,4}$")


def read_constant(name):
	tree = ast.parse((ROOT / "metar.py").read_text())
	for node in tree.body:
		if isinstance(node, ast.Assign):
			for target in node.targets:
				if isinstance(target, ast.Name) and target.id == name:
					return ast.literal_eval(node.value)
	raise KeyError(name)


def read_airports():
	lines = (ROOT / "airports").read_text().splitlines()
	return [line.strip().upper() for line in lines if line.strip() and not line.strip().startswith("#")]


def main():
	airports = read_airports()
	led_count = read_constant("LED_COUNT")
	show_legend = read_constant("SHOW_LEGEND")
	offset_legend_by = read_constant("OFFSET_LEGEND_BY")
	wind_animation = read_constant("ACTIVATE_WINDCONDITION_ANIMATION")
	lightning_animation = read_constant("ACTIVATE_LIGHTNING_ANIMATION")
	high_winds_threshold = read_constant("HIGH_WINDS_THRESHOLD")

	errors = []
	warnings = []
	airport_leds = [airport for airport in airports if airport != "NULL"]

	for index, airport in enumerate(airports, start=1):
		if airport != "NULL" and not AIRPORT_RE.match(airport):
			errors.append(f"Line {index}: {airport} does not look like a valid station code.")

	legend_leds = 0
	if show_legend:
		legend_leds = 4
		if lightning_animation:
			legend_leds = max(legend_leds, 5)
		if wind_animation:
			legend_leds = max(legend_leds, 6)
			if high_winds_threshold != -1:
				legend_leds = max(legend_leds, 7)

	required_leds = len(airports) + offset_legend_by + legend_leds
	if required_leds > led_count:
		errors.append(
			f"LED_COUNT is {led_count}, but the airport list plus legend needs {required_leds} LEDs."
		)

	if len(set(airport_leds)) != len(airport_leds):
		seen = set()
		duplicates = sorted({airport for airport in airport_leds if airport in seen or seen.add(airport)})
		warnings.append("Duplicate airport codes: " + ", ".join(duplicates))

	unused_leds = led_count - required_leds
	print("METARMap board configuration")
	print(f"  LED_COUNT: {led_count}")
	print(f"  Airport positions in airports file: {len(airports)}")
	print(f"  Real airport LEDs: {len(airport_leds)}")
	print(f"  NULL/gap LEDs: {len(airports) - len(airport_leds)}")
	print(f"  Legend LEDs: {legend_leds}")
	print(f"  Unused LEDs after configured positions: {unused_leds}")

	if warnings:
		print()
		print("Warnings:")
		for warning in warnings:
			print("  - " + warning)

	if errors:
		print()
		print("Errors:")
		for error in errors:
			print("  - " + error)
		return 1

	print()
	print("Board configuration looks good.")
	return 0


if __name__ == "__main__":
	sys.exit(main())
