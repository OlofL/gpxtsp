# gpxtsp

Optimize waypoint order in gpx file for a fast route through all of them.
It is a python program that uses the python_tsp library for optimization and the gpxpy library for gpx file handling. It needs access to an instance of the osrm routing engine to calculate distances.
It does not guarantee that it is the optimal route. Travelling Salesman Problem grows exponentially in computing time for the optimal solution. The code is easy to change for optimal solution, but it is only solvable for a limited number of waypoints. The non optimal solution have been tested with a gpx file of 590 waypoints with a total solving time about 10 minutes (Intel Core i5 8:th gen).

# Prerequistes (Important!)

For distance calculation it uses https://project-osrm.org/ 
The demo instance of project-osrm can be used for simple and personal distances. The demo server can only calculate distances for car travel.
The proper way to set this up is to run your own local instance of the server. This is fairly easy to do in Windows 11 (or in any linux environment), see below.

# Usage

>python gpxtsp.py yourwaypointfile.gpx [-o newwaypointfile.gpx]

# Installation

You will probably want to create a virtual environment for this
>python -m venv .venv

Then install required libaries
>pip install -r requirements.txt

# Setting up your own OSRM

The description below is for setting up your own instance of routing server with the following configuration
* Windows 11
* Fastest bicycle travel between waypoints

Note that this setup only supports one mode of travel profile, you can't switch between bicycle and car, you would need two instances.

The first part is to get wsl to work on Windows 11 (Windows Subsystem for Linux). Follow some generic instructions and install for example ubuntu. Wsl is already installed in Windows 11 so it is quite straight forward.

Download and install Docker Desktop for Windows. Follow the guide and make sure that you can get a container to run.

Restart a termial and start wsl.
Create a folder (under your home directory in wsl) and cd into it
>mkdir osrm
>cd osrm

Get mapping data from OSM. In this case for Sweden.
>wget http://download.geofabrik.de/europe/sweden-latest.osm.pbf

Choose what profile (mode of transport) you want to use from the list below and remember its name. We will use bicycle.lua.
>https://github.com/Project-OSRM/osrm-backend/tree/master/profiles

Next we will fetch a copy of the docker container for osrm and do some preparations of the OSM-data before we can start
the server. First step. It took some minutes on a PC with Core i5 8:th gen and used 6,5 GB memory.
>docker run -t -v "${PWD}:/data" ghcr.io/project-osrm/osrm-backend osrm-extract -p /opt/bicycle.lua /data/sweden-latest.osm.pbf

Second step is faster.
>docker run -t -v "${PWD}:/data" ghcr.io/project-osrm/osrm-backend osrm-partition /data/sweden-latest.osm.pbf

Final step in preparation is even faster.
>docker run -t -v "${PWD}:/data" ghcr.io/project-osrm/osrm-backend osrm-customize /data/sweden-latest.osm.pbf

Start the routing server on port 5000 and expose port 5000 on you Windows server.
>docker run -t -i -p 5000:5000 -v "${PWD}:/data" ghcr.io/project-osrm/osrm-backend osrm-routed --algorithm mld /data/sweden-latest.osrm

Test access from a new wsl terminal with this. Ignore driving in the url, it doesn't care, it only uses the profile that you assigned earlier.
>curl "http://127.0.0.1:5000/route/v1/driving/13.218255,55.703265;13.22082,55.702969?steps=true"

Optionally you can run you own frontend in another docker container and test it out. This step is not neccessary.
>docker run -p 9966:9966 osrm/osrm-frontend

If you start your own frontend, open your browser to this url and select map openstreetmap.org.
>http://127.0.0.1:9966

Now you are ready to run gpxtsp. It defaults to http://localhost:5000 which usually is the same as http://127.0.0.1:5000, that is the host pc port 5000 which is forwarded to the docker container running the server.
