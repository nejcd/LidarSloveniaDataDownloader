# -*- coding: utf-8 -*-
"""
/***************************************************************************
 LidarSloveniaDataDownloader
                                 A QGIS plugin
 Plugin for downloading data from Lidar Scanning of Slovenia (LSS)
                              -------------------
        begin                : 2017-01-21
        git sha              : $Format:%H$
        copyright            : (C) 2017 by Nejc Dougan
        email                : nejc.dougan@gmail.com
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""
from PyQt4.QtCore import QSettings, QTranslator, qVersion, QCoreApplication, Qt
from PyQt4.QtGui import QAction, QIcon, QFileDialog, QProgressBar
from qgis.gui import QgsMessageBar
from qgis.core import QgsMapLayerRegistry
import qgis

# Initialize Qt resources from file resources.py
import resources

# Import the code for the DockWidget
from LidarSloveniaDataDownloader_dockwidget import LidarSloveniaDataDownloaderDockWidget
import os.path
import os
import datetime
import requests
import sys
import time

class LidarSloveniaDataDownloader:
    """QGIS Plugin Implementation."""

    def __init__(self, iface):
        """Constructor.

        :param iface: An interface instance that will be passed to this class
            which provides the hook by which you can manipulate the QGIS
            application at run time.
        :type iface: QgsInterface
        """
        # Save reference to the QGIS interface
        self.iface = iface
        self.msgBar = iface.messageBar()

        # initialize plugin directory
        self.plugin_dir = os.path.dirname(__file__)

        # initialize locale
        locale = QSettings().value('locale/userLocale')[0:2]
        locale_path = os.path.join(
            self.plugin_dir,
            'i18n',
            'LidarSloveniaDataDownloader_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)

            if qVersion() > '4.3.3':
                QCoreApplication.installTranslator(self.translator)

        # Declare instance attributes
        self.actions = []
        self.menu = self.tr(u'&Lidar Slovenia Data Downloader')
        self.toolbar = self.iface.addToolBar(u'LidarSloveniaDataDownloader')
        self.toolbar.setObjectName(u'LidarSloveniaDataDownloader')

        #print "** INITIALIZING LidarSloveniaDataDownloader"

        self.pluginIsActive = False
        self.dockwidget = None

        #Constants
        self.crs = ['D96TM', 'D48GK']
        self.product =['OTR(zlas)', 'OTR(laz) ', 'GKOT(zlas)', 'GKOT(laz) ',  'DMR']


    # noinspection PyMethodMayBeStatic
    def tr(self, message):
        """Get the translation for a string using Qt translation API.

        We implement this ourselves since we do not inherit QObject.

        :param message: String for translation.
        :type message: str, QString

        :returns: Translated version of message.
        :rtype: QString
        """
        # noinspection PyTypeChecker,PyArgumentList,PyCallByClass
        return QCoreApplication.translate('LidarSloveniaDataDownloader', message)


    def add_action(
        self,
        icon_path,
        text,
        callback,
        enabled_flag=True,
        add_to_menu=True,
        add_to_toolbar=True,
        status_tip=None,
        whats_this=None,
        parent=None):
        """Add a toolbar icon to the toolbar.

        :param icon_path: Path to the icon for this action. Can be a resource
            path (e.g. ':/plugins/foo/bar.png') or a normal file system path.
        :type icon_path: str

        :param text: Text that should be shown in menu items for this action.
        :type text: str

        :param callback: Function to be called when the action is triggered.
        :type callback: function

        :param enabled_flag: A flag indicating if the action should be enabled
            by default. Defaults to True.
        :type enabled_flag: bool

        :param add_to_menu: Flag indicating whether the action should also
            be added to the menu. Defaults to True.
        :type add_to_menu: bool

        :param add_to_toolbar: Flag indicating whether the action should also
            be added to the toolbar. Defaults to True.
        :type add_to_toolbar: bool

        :param status_tip: Optional text to show in a popup when mouse pointer
            hovers over the action.
        :type status_tip: str

        :param parent: Parent widget for the new action. Defaults None.
        :type parent: QWidget

        :param whats_this: Optional text to show in the status bar when the
            mouse pointer hovers over the action.

        :returns: The action that was created. Note that the action is also
            added to self.actions list.
        :rtype: QAction
        """

        icon = QIcon(icon_path)
        action = QAction(icon, text, parent)
        action.triggered.connect(callback)
        action.setEnabled(enabled_flag)

        if status_tip is not None:
            action.setStatusTip(status_tip)

        if whats_this is not None:
            action.setWhatsThis(whats_this)

        if add_to_toolbar:
            self.toolbar.addAction(action)

        if add_to_menu:
            self.iface.addPluginToMenu(
                self.menu,
                action)

        self.actions.append(action)

        return action


    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""

        icon_path = ':/plugins/LidarSloveniaDataDownloader/icon.png'
        self.add_action(
            icon_path,
            text=self.tr(u'Lidar Slovenia Data Downloader'),
            callback=self.run,
            parent=self.iface.mainWindow())

    #--------------------------------------------------------------------------

    def onClosePlugin(self):
        """Cleanup necessary items here when plugin dockwidget is closed"""

        #print "** CLOSING LidarSloveniaDataDownloader"

        # disconnects
        self.dockwidget.closingPlugin.disconnect(self.onClosePlugin)

        # remove this statement if dockwidget is to remain
        # for reuse if plugin is reopened
        # Commented next statement since it causes QGIS crashe
        # when closing the docked window:
        # self.dockwidget = None

        self.pluginIsActive = False


    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""

        #print "** UNLOAD LidarSloveniaDataDownloader"

        for action in self.actions:
            self.iface.removePluginMenu(
                self.tr(u'&Lidar Slovenia Data Downloader'),
                action)
            self.iface.removeToolBarIcon(action)
        # remove the toolbar
        del self.toolbar

    #--------------------------------------------------------------------------
    def unloadGrid(self, layername):
        """Unload Grid"""
        layers = self.iface.legendInterface().layers()
        for layer in layers:
            if layer.name() == layername:
                QgsMapLayerRegistry.instance().removeMapLayer(layer.id())

    def getLayerNames(self):
        """"Get layer names"""
        layers = self.iface.legendInterface().layers()
        layer_list = []
        for layer in layers:
            layer_list.append(layer.name())
        return layer_list

    def loadGrid(self):
        """"Load vector layer"""
        layer_names = ['Tiles LIDAR D96', 'Tiles LIDAR D48']

        # Check if grid already loaded
        layerlist = []
        layerlist = self.getLayerNames()
        for layer in layerlist:
            if layer == layer_names[0]:
                self.unloadGrid(layer_names[0])
            elif layer == layer_names[1]:
                self.unloadGrid(layer_names[1])

        # Load grid

        grid_layer_path = [os.path.dirname(__file__) + "/data/LIDAR_FISHNET_D96.shp",
                           os.path.dirname(__file__) + "/data/LIDAR_FISHNET_D48GK.shp"]
        index = self.dockwidget.comboBoxGridLayer.currentIndex()
        layer = self.iface.addVectorLayer(grid_layer_path[index], layer_names[index], "ogr")
        if not layer:
            print "Layer failed to load!"

    def getTileNames(self):
        tileNames = []
        layer = qgis.utils.iface.activeLayer()
        selected_features = layer.selectedFeatures()
        for feature in selected_features:
            tile_name = feature['NAME']
            tile_block = feature['BLOK']
            [tileE, tileN] = tile_name.split("_")
            [b, block_number] = tile_block.split("_")
            tileNames.append([int(tileE), int(tileN), int(block_number)])
        return tileNames

    def getUrlAndFilename(self, tile, CRS, product):
        if product == 'OTR(zlas)':
            productname = 'OTR'
            extension = 'zlas'
            fileprefix = 'R'
        elif product == 'OTR(laz) ':
            productname = 'OTR/laz'
            extension = 'laz'
            fileprefix = 'R'
        elif product == 'GKOT(zlas)':
            productname = 'GKOT'
            extension = 'zlas'
            fileprefix = ''
        elif product == 'GKOT(laz) ':
            productname = 'GKOT/laz'
            extension = 'laz'
            fileprefix = ''
        elif product == 'DMR':
            productname = 'dmr1'
            extension = 'asc'
            fileprefix = '1'

        [tileE, tileN, block_number] = tile
        filename = '{0}{1}_{2}_{3}.{4}'.format(CRS[-2:], fileprefix, tileE, tileN, extension)
        url = 'http://gis.arso.gov.si/lidar/{0}/b_{1}/{2}/{3}'.format(productname, block_number, CRS, filename)
        return url, filename


    def downloadLSS(self, url, filename, destination, n, ntiles):
        msg = "Downloading file ({0}/{1}): {2}".format(n + 1, ntiles, filename)
        progressMessageBar = self.msgBar.createMessage(msg)
        progress = QProgressBar()
        progress.setMaximum(100)
        progress.setAlignment(Qt.AlignLeft|Qt.AlignVCenter)
        progressMessageBar.layout().addWidget(progress)
        self.msgBar.pushWidget(progressMessageBar, level=QgsMessageBar.INFO)
        downloaded = False

        with open(destination + '/' + filename, "wb") as file:
            print "Downloading: " + filename
            response = requests.get(url, stream=True)
            total_length = response.headers.get('content-length')
    
            if total_length is None: 
                file.write(response.content)
            else:
                dl = 0
                total_length = int(total_length)
                for data in response.iter_content(chunk_size=4096):
                    dl += len(data)
                    file.write(data)
                    done = int(100 * dl / total_length)
                    progress.setValue(done)
                    print done
            downloaded = True    
        if downloaded:
            print '\nDone downloading: ' + filename
            time.sleep(1)
        else:
            print 'Download failed: ' + filename
    
        return downloaded

    def download(self):
        tileNames = self.getTileNames()
        indexCRS = self.dockwidget.comboBoxGridLayer.currentIndex()
        indexProduct = self.dockwidget.comboBoxProduct.currentIndex()

        if self.dockwidget.lineOutput.text():
            destination = self.dockwidget.lineOutput.text()
        else:
            self.select_output_folder()
            destination = self.dockwidget.lineOutput.text()

        n = 0
        ntiles = len(tileNames)
        downloaded = False

        self.msgBar.pushMessage("Start downloading {0} files...".format(ntiles), level=QgsMessageBar.INFO)

        for tile in tileNames:
            t0 = datetime.datetime.now()
            url, filename = self.getUrlAndFilename(tile, self.crs[indexCRS], self.product[indexProduct])
            downloaded = self.downloadLSS(url, filename, destination, n, ntiles)
            n += 1
            time = datetime.datetime.now() - t0
            if downloaded:
                self.msgBar.pushMessage("{0} of {1} files. Estimate time to finish: {2}".format(n, ntiles,
                                    (ntiles - n) * time),
                                    level=QgsMessageBar.INFO)
            else:
                self.msgBar.pushMessage("Download of tile {0}_{1} failed!".format(tile[0], tile[1]),
                                        level=QgsMessageBar.WARNING)

        self.msgBar.clearWidgets()
        self.msgBar.pushMessage("Finished!", level=QgsMessageBar.SUCCESS)

    def select_output_folder(self):
        """Select output folder"""
        folder = QFileDialog.getExistingDirectory(self.dockwidget, "Select folder")
        self.dockwidget.lineOutput.setText(folder)

    def run(self):
        """Run method that loads and starts the plugin"""
        grid_layer_name = ['Lidar D96/TM', 'Lidar D48/GK']

        if not self.pluginIsActive:
            self.pluginIsActive = True

            print "** STARTING LidarSloveniaDataDownloader"

            # dockwidget may not exist if:
            #    first run of plugin
            #    removed on close (see self.onClosePlugin method)
            if self.dockwidget == None:
                # Create the dockwidget (after translation) and keep reference
                self.dockwidget = LidarSloveniaDataDownloaderDockWidget()
                self.dockwidget.comboBoxGridLayer.clear()

                self.dockwidget.comboBoxGridLayer.addItems(grid_layer_name)
                self.dockwidget.comboBoxProduct.addItems(self.product)
                self.dockwidget.loadLayer.clicked.connect(self.loadGrid)

                self.dockwidget.pushButtonOutput.clicked.connect(self.select_output_folder)
                self.dockwidget.pushButtonDownload.clicked.connect(self.download)

            # connect to provide cleanup on closing of dockwidget
            self.dockwidget.closingPlugin.connect(self.onClosePlugin)

            # show the dockwidget
            self.iface.addDockWidget(Qt.RightDockWidgetArea, self.dockwidget)
            self.dockwidget.show()

