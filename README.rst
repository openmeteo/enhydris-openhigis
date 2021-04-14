==================================
Enhydris-openhigis - OpenHi layers
==================================

.. image:: https://travis-ci.org/openmeteo/enhydris-openhigis.svg?branch=master
    :alt: Build button
    :target: https://travis-ci.org/openmeteo/enhydris-openhigis

.. image:: https://codecov.io/github/openmeteo/enhydris-openhigis/coverage.svg?branch=master
    :alt: Coverage
    :target: https://codecov.io/gh/openmeteo/enhydris-openhigis

Overview
========

Enhydris-openhigis is an app that provides layers (such as water basins
and river networks) for the OpenHi project. In the repository there's
also MapServer configuration for serving these layers with WMS and WFS.

The app is specific to the OpenHi project and several things are
hardwired in the code.

The app contains geographical models such as ``RiverBasinDistrict``,
which inherit either ``Gentity`` or ``Garea``. So that gis people can
connect to the database with a GIS client and update the contents of
such tables, writeable database views (e.g. ``RiverBasinDistricts``)
are created in the ``openhigis`` database schema. Except for collecting
objects from several tables (that use multi-table inheritance) into a
single view, these views also use SRID=2100, transparently translating
to and from 4326, which is what is actually being used for geometry
storage in ``Gentity``.

Installing and configuring
==========================

- Install Enhydris 3 or later

- Make sure ``enhydris_openhigis`` is in the PYTHONPATH, or link to it
  from the top-level directory of Enhydris.

- Somewhere in the Python path, create file ``urls.py``, with contents
  such as this::

     from django.urls import include, path

     from enhydris import urls as enhydris_urls
     from enhydris_openhigis import urls as enhydris_openhigis_urls


     urlpatterns = [
         path("openhigis/", include(enhydris_openhigis_urls)),
         path("", include(enhydris_urls)),
     ]

- In the Enhydris ``enhydris_project/settings/local.py`` file, add
  ``enhydris_openhigis`` to ``INSTALLED_APPS``, specify the ``urls.py``
  file in ``ROOT_URLCONF``, add
  ``enhydris_openhigis.middleware.OpenHiGISMiddleware`` to
  ``MIDDLEWARE``, and specify the mapserver root url in
  ``ENHYDRIS_OWS_URL``.

- In the Enhydris configuration directory, execute ``python manage.py
  migrate``.

- Connect to PostgreSQL with ArcGIS or QGIS and add layers.

- Start MapServer and access these layers.

Meta
====

| Copyright (C) 2018-2021 National Technical University of Athens
| Copyright (C) 2018-2021 Institute of Communication and Computer Systems

Enhydris-openhigis is free software: you can redistribute it and/or
modify it under the terms of the GNU Affero General Public License, as
published by the Free Software Foundation; either version 3 of the
License, or (at your option) any later version.

The software is distributed in the hope that it will be useful, but
WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
licenses for more details.

You should have received a copy of the license along with this
program.  If not, see http://www.gnu.org/licenses/.

Enhydris-openhigis was funded by NTUA_ and ICCS_ as part of the OpenHi_
project.

.. _ntua: http://www.ntua.gr/
.. _iccs: https://www.iccs.gr
.. _openhi: https://openhi.net

