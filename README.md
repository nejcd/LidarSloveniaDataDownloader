# Lidar Slovenia Data Downloader
#### QGis plugin for downloading Lidar Survey of Slovenia

This plugin is intended to make downloading of Lidar Scanning of Slovenia (LSS) easier. Espacaily it is handy when using for downloading larger areas or when you have another vector layer which can be used to make spatial selection of tiles you need.

## Data

[Ministry of the enviroment and spatial planning of Republic of Slovenia](http://evode.arso.gov.si/indexd022.html?q=node/12), has enabled to download data of Lidar Scanning of Slovenia via internet. It is possiable to obtain following data:

- Georeferenced point cloud (OTR)
- Georeferenced classifeid point cloud (GKOT)
- Digital elevevation model (DMR) 

Data is avalibale in two different Corrdinate Refrence Systems:

- D48/GK ( [EPSG:2170](http://spatialreference.org/ref/epsg/2170/) )
- D96/TM ( [EPSG:3794](http://spatialreference.org/ref/epsg/3794/) )

[More information about data](http://evode.arso.gov.si/indexd697.html?q=node/32)

## Tutorial

Install plugin trough QGIS Manage and install plugins or download source from GitHub and add all files and folders to your local QGIS directory (C:\Users\USER\.qgis2\python\plugins\GetLSSplugin )

Run plugin.

- Select Cordinate Refrence System and then press Load tiles
- Select tiles you need; by hand, by attributes or by Spatial query (Install plugin Spatial query)
- Select product (OTR, GKOT, DMR)
- Select download folder
- Start downloading

To monitor which tile is currently being downloaded open Python Console in QGIS (Plugins > Python Console). This should be done before you start downloading. 
