Django InfluxDB Metrics
=======================

A reusable Django app that sends metrics about your project to InfluxDB.

Installation
------------

To get the latest stable release from PyPi

.. code-block:: bash

    pip install django-influxdb-metrics

To get the latest commit from GitHub

.. code-block:: bash

    pip install -e git+git://github.com/bitmazk/django-influxdb-metrics.git#egg=influxdb_metrics

Add ``influxdb_metrics`` to your ``INSTALLED_APPS``

.. code-block:: python

    INSTALLED_APPS = (
        ...,
        'influxdb_metrics',
    )

Settings
--------

You need to set the following settings::

    INFLUXDB_HOST = 'your.influxdbhost.com'
    INFLUXDB_PORT = '8086'
    INFLUXDB_USER = 'youruser'
    INFLUXDB_PASSWORD = 'yourpassword'
    INFLUXDB_DATABASE = 'yourdatabase'

    # Optional:
    INFLUXDB_SERIES_PREFIX = 'yourservername.'
    INFLUXDB_SERIES_POSTFIX = '.whatever'

If you would like to disable sending of metrics (i.e. for local development),
you can set::

    INFLUXDB_DISABLED = True


Usage
-----

The app comes with several management commands which you should schedule via
crontab.


influxdb_get_memory_usage
+++++++++++++++++++++++++

Collects the total memory of your user, plus the memory and name of the largest
process.

You can run it like this::

    ./manage.py influxdb_get_memory_usage
    ./manage.py influxdb_get_memory_usage username

If you don't provide a username, total memory for all users will be collected.
This might not be desirable on a shared hosting environment where you can see
all user's processes.

You could schedule it like this::

    * * * * * cd /path/to/project/ && /path/to/venv/bin/python /path/to/project/manage.py influxdb_get_memory_usage username > $HOME/mylogs/cron/influxdb-get-memory-usage.log 2>&1

The series created in your InfluxDB will be named
``<prefix>default.server.memory.usage<postfix>`` and will have the following columns:

* ``value``: The total memory usage in bytes
* ``largest_process``: Memory usage of the largest process in bytes
* ``largest_process_name``: String representing the largest process name


influxdb_get_cpu_usage
++++++++++++++++++++++

Collects the total %CPU for the given user, plus the %CPU and name of the
largest process.

You can run it like this::

    ./manage.py influxdb_get_cpu_usage
    ./manage.py influxdb_get_cpu_usage username

If you don't provide a username, total %CPU for all users will be collected.
This might not be desirable on a shared hosting environment where you can see
all user's processes.

You could schedule it like this::

    * * * * * cd /path/to/project/ && /path/to/venv/bin/python /path/to/project/manage.py influxdb_get_cpu_usage username > $HOME/mylogs/cron/influxdb-get-cpu-usage.log 2>&1

The series created in your InfluxDB will be named
``<prefix>default.server.cpu.usage<postfix>`` and will have the following
columns:

* ``value``: The total %CPU
* ``largest_process``: %CPU of the largest process
* ``largest_process_name``: String representing the largest process name


influxdb_get_cpu_memory_usage
+++++++++++++++++++++++++++++

This is a wrapper around the two commands above. You will usually want to
schedule them every minute. Since crontab cannot handle schedules by seconds
both commands would always start at the same time. As a result, the CPU command
would measure the CPU usage of the memory command and that would mostly be the
near 100%. This compound command will execute both the others one after another
and therefore only appear as one process.

You could schedule it like this::

    * * * * * cd /path/to/project/ && /path/to/venv/bin/python /path/to/project/manage.py influxdb_get_cpu_memory_usage username_cpu username_memory > $HOME/mylogs/cron/influxdb-get-cpu-memory-usage.log 2>&1


influxdb_get_disk_usage
+++++++++++++++++++++++

Collects the total disk usage for the given path.

NOTE: This faciliates the ``du`` command with the ``--block-size`` flag,
therefore it doesn't work on OSX.

You can run it like this::

    ./manage.py influxdb_get_disk_usage $HOME

You should give an absolute path to the folder which you want to measure. On a
shared hosting environment this would probably be your home folder.

You could schedule it like this::

    0 */1 * * * cd /path/to/project/ && /path/to/venv/bin/python /path/to/project/manage.py influxdb_get_disk_usage $HOME > $HOME/mylogs/cron/influxdb-get-disk-usage.log 2>&1

The series created in your InfluxDB will be named
``<prefix>default.server.disk.usage<postfix>`` and will have the following columns:

* ``value``: The total memory usage in bytes


influxdb_get_postgresql_size
++++++++++++++++++++++++++++

Collects the total disk usage for the given database.

You can run it like this::

    ./manage.py influxdb_get_postgresql_size db_role db_name

You shoudl provide role and name for the database you want to measure. Make
sure that you have a ``.pgpass`` file in place so that you don't need to enter
a password for this user.

You could schedule it like this::

    0 */1 * * * cd /path/to/project/ && /path/to/venv/bin/python /path/to/project/manage.py influxdb_get_postgresql_size db_role db_name > $HOME/mylogs/cron/influxdb-get-postgresql-size.log 2>&1

The series created in your InfluxDB will be named
`<prefix>default.server.postgresql.size<postfix>` and will have the following columns:

* ``value``: The total database size in bytes


InfluxDBEmailBackend
++++++++++++++++++++

If you would like to track tne number of emails sent, you can set your
`EMAIL_BACKEND`::

    EMAIL_BACKEND = 'influxdb_metrics.email.InfluxDBEmailBackend'

When the setting is set, metrics will be sent every time you run ``.manage.py
send_mail``.

The series created in your InfluxDB will be named
``<prefix>default.django.email.sent<postfix>`` and will have the following columns:

* ``value``: The number of emails sent


InfluxDBRequestMiddleware
+++++++++++++++++++++++++

If you would like to track the number and speed of all requests, you can add
the ``InfluxDBRequestMiddleware`` at the top of your ``MIDDLEWARE_CLASSES``::

    MIDDLEWARE_CLASSES = [
        'influxdb_metrics.middleware.InfluxDBRequestMiddleware',
        ...
    ]

The series created in your InfluxDB will be named
``<prefix>default.django.request<postfix>`` and will have the following columns:

* ``value``: The request time in milliseconds.
* ``is_ajax``: `true` if it was an AJAX request, otherwise `false`
* ``is_authenticated``: `true` if user was authenticated, otherwise `false`
* ``is_staff``: `true` if user was a staff user, otherwise `false`
* ``is_superuser``: `true` user was a superuser, otherwise `false`
* ``method``: The request method (`GET` or `POST`)
* ``module``: The python module that handled the request
* ``view``: The view class or function that handled the request
* ``referer``: The full URL from `request.META['HTTP_REFERER']`
* ``referer_tld``: The top level domain of the referer. It tries to be smart
     and regards ``google.co.uk`` as a top level domain (instead of ``co.uk``)
* ``full_path``: The full path that was requested
* ``path``: The path without GET params that was requested

If you have a highly frequented site, this table could get big really quick.
You should make sure to create a shard with a low retention time for this
series (i.e. 7d) and add a continuous query to downsample the data into
hourly/daily averages. When doing that, you will obviously lose the detailed
information like ``referer`` and ``referer_tld`` but it might make sense to
create a second continuous query to count and downsample at least the
``referer_tld`` values.

NOTE: I don't know what impact this has on overall request time or how much
stress this would put on the InfluxDB server if you get thousands of requests.
It would probably wise to consider something like statsd to aggregate the
requests first and then send them to InfluxDB in bulk.


Tracking User Count
+++++++++++++++++++

This app's ``models.py`` contains a ``post_save`` and a ``post_delete`` handler
which will detect when a user is created or deleted.

It will create three series in your InfluxDB:

The first one will be named
``<prefix>default.django.auth.user.create<postfix>`` and will have the
following columns:

* ``value``: 1 

The second one will be named
``<prefix>default.django.auth.user.delete<postfix>`` and will have the
following columns:

* ``value``: 1

The third one will be named ``<prefix>default.django.auth.user.count<postfix>``
and will have the following columns:

* ``value``: The total number of users in the database


Tracking User Logins
++++++++++++++++++++

This app's ``models.py`` contains a handler for the ``user_logged_in`` signal.

The series created in your InfluxDB will be named
``<prefix>default.django.auth.user.login<postfix>`` and will have the following
columns:

* ``value``: 1


Making Queries
++++++++++++++

If you need to get data out of your InfluxDB instance, you can easily do it
like so::

   from influxdb_metrics.utils import query
   query('select * from series.name', time_precision='s', chunked=False)

The method declaration is the same as the one in ``InfluxDBClient.query()``.
This wrapper simply instanciates a client based on your settings.


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
