from rgb_colour import RgbColour

print("Long way of getting hex colour:")
purp = RgbColour(130, 4, 124)
print(f"#{purp.red:02X}{purp.green:02X}{purp.blue:02X}")

print("Short way of getting hex colour:")
purp = RgbColour(130, 4, 124)
print(f"{purp.for_css()}")

