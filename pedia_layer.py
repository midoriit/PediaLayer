# -*- coding: utf-8 -*-
"""
/***************************************************************************
 PediaLayer
                                 A QGIS plugin
 Create a layer from DBpedia.
                              -------------------
        begin                : 2015-09-01
        git sha              : $Format:%H$
        copyright            : (C) 2015 by Midori IT Office, LLC.
        email                : info@midoriit.com
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
from PyQt4.QtCore import QSettings, QTranslator, qVersion, QCoreApplication
from PyQt4.QtGui import QAction, QIcon
# Initialize Qt resources from file resources.py
import resources
# Import the code for the dialog
from pedia_layer_dialog import PediaLayerDialog
import os.path

# IMPORT MODULES
from qgis.core import *
from qgis.gui import *
import json, urllib, urllib2
from PyQt4.QtCore import *

class PediaLayer:
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
        # initialize plugin directory
        self.plugin_dir = os.path.dirname(__file__)
        # initialize locale
        locale = QSettings().value('locale/userLocale')[0:2]
        locale_path = os.path.join(
            self.plugin_dir,
            'i18n',
            'PediaLayer_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)

            if qVersion() > '4.3.3':
                QCoreApplication.installTranslator(self.translator)

        # Create the dialog (after translation) and keep reference
        self.dlg = PediaLayerDialog()

        # Declare instance attributes
        self.actions = []
        self.menu = self.tr(u'&Pedia Layer')
        # TODO: We are going to let the user set this up in a future iteration
        self.toolbar = self.iface.addToolBar(u'PediaLayer')
        self.toolbar.setObjectName(u'PediaLayer')

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
        return QCoreApplication.translate('PediaLayer', message)


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
            self.iface.addPluginToWebMenu(
                self.menu,
                action)

        self.actions.append(action)

        return action

    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""

        icon_path = ':/plugins/PediaLayer/icon.png'
        self.add_action(
            icon_path,
            text=self.tr(u'Create a layer from DBpedia'),
            callback=self.run,
            parent=self.iface.mainWindow())


    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
        for action in self.actions:
            self.iface.removePluginWebMenu(
                self.tr(u'&Pedia Layer'),
                action)
            self.iface.removeToolBarIcon(action)
        # remove the toolbar
        del self.toolbar


    def run(self):
        """Run method that performs all the real work"""

        # PREPARE COMBO BOX
        self.dlg.comboBox.clear()
        layers = self.iface.legendInterface().layers()
        layer_list = []
        for layer in layers:
            if isinstance(layer, QgsVectorLayer) or isinstance(layer, QgsRasterLayer):
                layer_list.append(layer.name())
        self.dlg.comboBox.addItems(layer_list)

        # show the dialog
        self.dlg.show()
        # Run the dialog event loop
        result = self.dlg.exec_()
        # See if OK was pressed
        if result:

            # ADD LAYER FROM DBPEDIA
            # calculate coordinates
            if self.dlg.radioButton_l.isChecked() == True:
                index = self.dlg.comboBox.currentIndex()
                if index == -1:
                    return
                layer = layers[index]
                extent = layer.extent()
                srcCrs = layer.crs()
            elif self.dlg.radioButton_m.isChecked() == True:
                canvas = self.iface.mapCanvas()
                layers = self.iface.legendInterface().layers()
                if len(layers) == 0:
                    return
                extent = canvas.extent()
                srcCrs = canvas.mapSettings().destinationCrs()
            else:
                return
            destCrs = QgsCoordinateReferenceSystem(4326, QgsCoordinateReferenceSystem.EpsgCrsId)
            transform = QgsCoordinateTransform(srcCrs, destCrs)
            wgsExtent = transform.transform(extent)
            xMax = wgsExtent.xMaximum()
            xMin = wgsExtent.xMinimum()
            yMax = wgsExtent.yMaximum()
            yMin = wgsExtent.yMinimum()

            # prepare query
            sparql = "SELECT distinct ?name, ?abstract, ?lat, ?lon, ?url\n" \
            + "WHERE {\n" \
            + "?s rdfs:label ?name ;\n" \
            + "dbpedia-owl:abstract ?abstract ;\n" \
            + "foaf:isPrimaryTopicOf ?url ;\n" \
            + "geo:lat ?lat ;\n" \
            + "geo:long ?lon .\n" \
            + "FILTER ( " \
            + "?lon > \"" + str(xMin) + "\"^^xsd:float && ?lon < \"" + str(xMax) + "\"^^xsd:float && " \
            + "?lat > \"" + str(yMin) + "\"^^xsd:float && ?lat < \"" + str(yMax) + "\"^^xsd:float)\n" \
            + "FILTER (LANG(?name)='ja' && LANG(?abstract)='ja')" \
            + "\n} LIMIT " + str(self.dlg.spinBox.value())
            server = "http://ja.dbpedia.org/sparql"
            param = { "query" : sparql , "format" : "application/sparql-results+json" }

            # exec query
            request = urllib2.Request(server, urllib.urlencode(param))
            response = urllib2.urlopen(request)
            data = json.loads(response.read())
            list = data["results"]["bindings"]

            # add layer
            newLayer = QgsVectorLayer("Point?crs=epsg:4326", "pedialayer", "memory")
            newLayer.setProviderEncoding("UTF-8")
            QgsMapLayerRegistry.instance().addMapLayer(newLayer)
            newLayer.startEditing()
            newLayer.addAttribute(QgsField("name", QVariant.String))
            newLayer.addAttribute(QgsField("url", QVariant.String))
            newLayer.addAttribute(QgsField("abstract", QVariant.String))

            # add features
            for item in list:
                feature = QgsFeature(newLayer.pendingFields())
                feature.setGeometry(QgsGeometry.fromPoint(QgsPoint(float(item["lon"]["value"]), float(item["lat"]["value"]))))
                feature.setAttribute("name", unicode(item["name"]["value"]))
                feature.setAttribute("url", unicode(item["url"]["value"]))
                feature.setAttribute("abstract", unicode(item["abstract"]["value"]))
                newLayer.addFeature(feature)
            newLayer.commitChanges()
            newLayer.updateExtents()

            # Do something useful here - delete the line containing pass and
            # substitute with your code.

