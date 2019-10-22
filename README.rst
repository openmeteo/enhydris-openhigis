==================================
Enhydris-openhigis - OpenHI layers
==================================

.. image:: https://travis-ci.org/openmeteo/enhydris-openhigis.svg?branch=master
    :alt: Build button
    :target: https://travis-ci.org/openmeteo/enhydris-openhigis

.. image:: https://codecov.io/github/openmeteo/enhydris-openhigis/coverage.svg?branch=master
    :alt: Coverage
    :target: https://codecov.io/gh/openmeteo/enhydris-openhigis

Enhydris-openhigis is an app that provides layers (such as water basins
and river networks) for the OpenHI project. In the repository there's
also MapServer configuration for serving these layers with WMS and WFS.

The app is specific to the OpenHI project and several things are
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

© 2019 National Technical University of Athens

Enhydris-openhigis is free software, available under the GNU Affero
General Public License.

**Installing and configuring**

- Install Enhydris 3 or later

- Make sure ``enhydris_openhigis`` is in the PYTHONPATH, or link to it
  from the top-level directory of Enhydris.

- In the Enhydris ``enhydris_project/settings/local.py`` file, add
  ``enhydris_openhigis`` to ``INSTALLED_APPS``.

- In the Enhydris configuration directory, execute ``python manage.py
  migrate``.

- Connect to PostgreSQL with ArcGIS or QGIS and add layers.

- Start MapServer and access these layers.
