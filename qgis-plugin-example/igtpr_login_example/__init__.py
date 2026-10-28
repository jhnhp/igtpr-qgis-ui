# -*- coding: utf-8 -*-
"""Contoh plugin QGIS: halaman login IGT-PR sebagai dock widget."""


def classFactory(iface):  # pylint: disable=invalid-name
    from .plugin import IgtprLoginExample
    return IgtprLoginExample(iface)
