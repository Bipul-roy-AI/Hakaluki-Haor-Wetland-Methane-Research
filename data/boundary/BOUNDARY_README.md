# Boundary audit — required before final area statistics

Candidate source: https://github.com/aburaihan21/Bangladesh-All-GIS-Shapefile-Data/tree/main/Hakaluki%20Haor

The third-party polygon's originating agency, production date, and exact mapping definition are not established. Notebook 00 downloads the source files and compares its bounds and area against an officially reported approximate extent (Sylhet District Government page, ~181.15 km²; 24°35′–24°44′ N, 92°01′–92°09′ E). A mismatch is **not** proof that either mapping is wrong; different wetland definitions and seasonal conditions can alter area. Research maps must describe the chosen definition.

Preferred replacement: a vetted official GIS polygon, appropriately documented, saved as `data/boundary/hakaluki_verified.geojson`. The notebooks prefer this file when present.

Do not publish outputs with the unverified candidate as a formally established Hakaluki Haor ECA boundary.
