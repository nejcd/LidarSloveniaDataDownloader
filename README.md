# Lidar Slovenia Data Downloader
#### QGIS plugin for downloading Lidar Survey of Slovenia

This plugin is intended to make downloading of Lidar Scanning of Slovenia (LSS) easier. Especially it is handy when using for downloading larger areas or when you have another vector layer which can be used to make spatial selection of tiles you need.

## Data

[Ministry of the environment and spatial planning of Republic of Slovenia](http://evode.arso.gov.si/indexd022.html?q=node/12), has enabled to download data of Lidar Scanning of Slovenia via internet. It is possible to obtain following data:

- Georeferenced point cloud (OTR) - zlas, laz
- Georeferenced classified point cloud (GKOT) - zlas, laz
- Digital elevation model (DMR) 

Data is available in two different Coordinate Reference Systems:

- D48/GK ( [EPSG:3912](https://epsg.io/3912) )
- D96/TM ( [EPSG:3794](https://epsg.io/3794) )

[More information about data](http://evode.arso.gov.si/indexd697.html?q=node/32)

## How TO

Install plugin trough QGIS Manage and install plugins or download source from GitHub and add all files and folders to your local QGIS directory (.qgis2\python\plugins\LidarSloveniaDataDownloader )

Run plugin.

- Select Coordinate Reference System and then press Load tiles
- Select tiles you need; by hand, by attributes or by Spatial query (Install plugin Spatial query)
- Select product (OTR(zlas), OTR(laz), GKOT(zlas), GKOT(laz), DMR)
- Select download folder
- Start downloading

To monitor which tile is currently being downloaded open Python Console in QGIS (Plugins > Python Console). This should be done before you start downloading.
