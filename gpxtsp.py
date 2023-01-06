import argparse
import gpxpy
import numpy as np
from python_tsp.heuristics import solve_tsp_local_search
from python_tsp.distances import osrm_distance_matrix


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Optimize waypoint order in a gpx file"
    )
    parser.add_argument(
        "gpxfiles", metavar="gpx", type=str, default="", nargs="*", help="GPX file"
    )
    parser.add_argument(
        "-o",
        "--output",
        metavar="F",
        type=str,
        default="optimized.gpx",
        help="Output GPX file",
    )
    args = parser.parse_args()

    gpxfiles = args.gpxfiles
    outfile = args.output

    if not gpxfiles:
        print(
            "Optimize waypoint order in a gpx file. Put you preferred starting waypoint first in the input gpx file. Usage: gpxtsp infile.gpx -o outfile.gpx"
        )
        return

    for gpx_file in gpxfiles:
        infile_gpx = gpxpy.parse(open(gpx_file))  # ignore all but last file

    new_gpx = infile_gpx.clone()

    sources = np.zeros((len(new_gpx.waypoints), 2))
    for ix, wptx in enumerate(new_gpx.waypoints):
        sources[ix] = (wptx.latitude, wptx.longitude)

    print("Calculating distances between all waypoints")
    distance_matrix = osrm_distance_matrix(
        sources,
        osrm_server_address="http://localhost:5000",
        # sources, osrm_server_address="http://router.project-osrm.org", # public server only handles routing by car
        osrm_batch_size=50,
    )

    print("Solving TSP-problem using local minima")
    permutation, distance = solve_tsp_local_search(distance_matrix)

    print(f"Road distance after optimization {distance} m")

    print(f"Saving output file {outfile}")
    new_gpx.waypoints = [new_gpx.waypoints[i] for i in permutation]

    with open(outfile, "w") as f:
        f.write(new_gpx.to_xml())


main()
