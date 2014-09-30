Django InfluxDB Metrics
============

A reusable Django app that sends metrics about your project to InfluxDB

Installation
------------

To get the latest stable release from PyPi

.. code-block:: bash

    pip install django-influxdb-metrics

To get the latest commit from GitHub

.. code-block:: bash

    pip install -e git+git://github.com/bitmazk/django-influxdb-metrics.git#egg=influxdb_metrix

TODO: Describe further installation steps (edit / remove the examples below):

Add ``influxdb_metrix`` to your ``INSTALLED_APPS``

.. code-block:: python

    INSTALLED_APPS = (
        ...,
        'influxdb_metrix',
    )

Add the ``influxdb_metrix`` URLs to your ``urls.py``

.. code-block:: python

    urlpatterns = patterns('',
        ...
        url(r'^/', include('influxdb_metrix.urls')),
    )

Before your tags/filters are available in your templates, load them by using

.. code-block:: html

	{% load influxdb_metrix_tags %}


Don't forget to migrate your database

.. code-block:: bash

    ./manage.py migrate influxdb_metrix


Usage
-----

TODO: Describe usage or point to docs. Also describe available settings and
templatetags.


Contribute
----------

If you want to contribute to this project, please perform the following steps

.. code-block:: bash

    # Fork this repository
    # Clone your fork
    mkvirtualenv -p python2.7 django-influxdb-metrics
    make develop

    git co -b feature_branch master
    # Implement your feature and tests
    git add . && git commit
    git push -u origin feature_branch
    # Send us a pull request for your feature branch
