# -*- coding: utf-8 -*-

import ConfigParser

__author__ = 'hao'


def get_items_in_cfg(section,option,configFile):
        cf = ConfigParser.ConfigParser()
        cf.read(configFile)
        items = cf.get(section,option)
        return items

def get_package_parent_local(package_parent):
        return package_parent.__file__.replace('__init__.pyc','')

def get_uri_relative_parent_package(package_parent, relative_path):
        return package_parent.__file__.replace('__init__.pyc', '').replace('__init__.py', '')+relative_path
