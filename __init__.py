# -*- coding: utf-8 -*-
"""
/***************************************************************************
 WikipediaLayer
                                 A QGIS plugin
 Add a layer of Wikipedia.
                             -------------------
        begin                : 2015-09-01
        copyright            : (C) 2015 by Midori IT Office, LLC.
        email                : info@midoriit.com
        git sha              : $Format:%H$
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
 This script initializes the plugin, making it known to QGIS.
"""


# noinspection PyPep8Naming
def classFactory(iface):  # pylint: disable=invalid-name
    """Load WikipediaLayer class from file WikipediaLayer.

    :param iface: A QGIS interface instance.
    :type iface: QgsInterface
    """
    #
    from .wikipedia_layer import WikipediaLayer
    return WikipediaLayer(iface)
