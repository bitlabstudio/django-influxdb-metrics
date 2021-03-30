# Django InfluxDB Metrics

A reusable Django app that sends metrics about your project to InfluxDB.

IMPORTANT NOTE: This release only supports InfluxDB >= 0.9. We have also dropped
a few measurements like CPU, memory and disk-space because
[Telegraf](https://github.com/influxdb/telegraf) can collect these in a much
much better way.

## Prerequisites

This module has celery support but you don't have to use it, if you don't want
to.

## Installation

To get the latest stable release from PyPi

.. code-block:: bash

    pip install django-influxdb-metrics

To get the latest commit from GitHub

.. code-block:: bash

    pip install -e git+git://github.com/bitmazk/django-influxdb-metrics.git#egg=influxdb_metrics

Add `influxdb_metrics` to your `INSTALLED_APPS`

.. code-block:: python

    INSTALLED_APPS = (
        ...,
        'influxdb_metrics',
    )

## Settings

You need to set the following settings::

    INFLUXDB_HOST = 'your.influxdbhost.com'
    INFLUXDB_PORT = '8086'
    INFLUXDB_USER = 'youruser'
    INFLUXDB_PASSWORD = 'yourpassword'
    INFLUXDB_DATABASE = 'yourdatabase'

    # This is for tagging the data sent to your influxdb instance so that you
    # can query by host
    INFLUXDB_TAGS_HOST = 'your_hostname'

    # Seconds to wait for the request to the influxdb server before timing out
    INFLUXDB_TIMEOUT = 5

    # Set this to True if you are using Celery
    INFLUXDB_USE_CELERY = True

    # Set this to True if you are not using Celery
    INFLUXDB_USE_THREADING = False

If you would like to disable sending of metrics (i.e. for local development),
you can set::

    INFLUXDB_DISABLED = True

If you are having trouble getting the postgresql database size, you might need
to set::

    INFLUXDB_POSTGRESQL_USE_LOCALHOST = True

Use ssl with INFLUXDB_HOST::

    INFLUXDB_SSL = True # default is False

Optional with ssl::

    INFLUXDB_VERIFY_SSL = True # default is False

Specify a prefix for metric measurement names (default is `django_`, E.g. `django_request`)

    INFLUXDB_PREFIX = "my_app"     # measurement name == 'my_app_request'
    INFLUXDB_PREFIX = ""           # measurement name == 'request'
    INFLUXDB_PREFIX = None         # measurement name == 'request'

## Usage

The app comes with several management commands which you should schedule via
crontab.

### influxdb_get_postgresql_size

Collects the total disk usage for the given database.

You can run it like this::

    ./manage.py influxdb_get_postgresql_size db_role db_name

You should provide role and name for the database you want to measure. Make
sure that you have a `.pgpass` file in place so that you don't need to enter
a password for this user.

You could schedule it like this::

    0 */1 * * * cd /path/to/project/ && /path/to/venv/bin/python /path/to/project/manage.py influxdb_get_postgresql_size db_role db_name > $HOME/mylogs/cron/influxdb-get-postgresql-size.log 2>&1

The measurement created in your InfluxDB will be named `postgresql_size` and
will have the following fields:

- `value`: The total database size in bytes

### InfluxDbEmailBackend

If you would like to track the number of emails sent, you can set your
`EMAIL_BACKEND`::

    EMAIL_BACKEND = 'influxdb_metrics.email.InfluxDbEmailBackend'

When the setting is set, metrics will be sent every time you run `.manage.py send_mail`.

The measurement created in your InfluxDB will be named `django_email_sent`
and will have the following fields:

- `value`: The number of emails sent

### InfluxDBRequestMiddleware

If you would like to track the number and speed of all requests, you can add
the `InfluxDBRequestMiddleware` at the top of your `MIDDLEWARE_CLASSES`::

    MIDDLEWARE_CLASSES = [
        'influxdb_metrics.middleware.InfluxDBRequestMiddleware',
        ...
    ]

The measurement created in your InfluxDB will be named `django.request` and
will have the following fields:

- `value`: The request time in milliseconds.

Additionally, it will have the following tags:

- `is_ajax`: `true` if it was an AJAX request, otherwise `false`
- `is_authenticated`: `true` if user was authenticated, otherwise `false`
- `is_staff`: `true` if user was a staff user, otherwise `false`
- `is_superuser`: `true` user was a superuser, otherwise `false`
- `method`: The request method (`GET` or `POST`)
- `module`: The python module that handled the request
- `view`: The view class or function that handled the request
- `referer`: The full URL from `request.META['HTTP_REFERER']`
- `referer_tld`: The top level domain of the referer. It tries to be smart
  and regards `google.co.uk` as a top level domain (instead of `co.uk`)
- `full_path`: The full path that was requested
- `path`: The path without GET params that was requested
- `campaign`: A value that is extracted from the GET-parameter `campaign`,
  if present. You can change the name of this keyword from `campaign` to
  anything via the setting `INFLUXDB_METRICS_CAMPAIGN_KEYWORD`.

If you have a highly frequented site, this table could get big really quick.
You should make sure to create a shard with a low retention time for this
series (i.e. 7d) and add a continuous query to downsample the data into
hourly/daily averages. When doing that, you will obviously lose the detailed
information like `referer` and `referer_tld` but it might make sense to
create a second continuous query to count and downsample at least the
`referer_tld` values.

NOTE: I don't know what impact this has on overall request time or how much
stress this would put on the InfluxDB server if you get thousands of requests.
It would probably wise to consider something like statsd to aggregate the
requests first and then send them to InfluxDB in bulk.

### Tracking Users

This app's `models.py` contains a `post_save` and a `post_delete` handler
which will detect when a user is created or deleted.

It will create three measurements in your InfluxDB:

The first one will be named `django_auth_user_create` and will have the
following fields:

- `value`: 1

The second one will be named `django_auth_user_delete` and will have the
following fields:

- `value`: 1

The third one will be named `django_auth_user_count` and will have the
following fields:

- `value`: The total number of users in the database

### Tracking User Logins

This app's `models.py` contains a handler for the `user_logged_in` signal.

The measurement created in your InfluxDB will be named
`django_auth_user_login` and will have the following fields:

- `value`: 1

### Making Queries

If you need to get data out of your InfluxDB instance, you can easily do it
like so::

from influxdb_metrics.utils import query
query('select \* from series.name', time_precision='s', chunked=False)

The method declaration is the same as the one in `InfluxDBClient.query()`.
This wrapper simply instanciates a client based on your settings.

## Contribute

If you want to contribute to this project, please perform the following steps

.. code-block:: bash

    # Fork this repository
    # Clone your fork
    mkvirtualenv -p python3.5 django-influxdb-metrics
    make develop

    git co -b feature_branch master
    # Implement your feature and tests
    git add . && git commit
    git push -u origin feature_branch
    # Send us a pull request for your feature branch

## Runing tests

For running the tests [Docker](https://docs.docker.com/) and
[Docker compose](https://www.docker.com/products/docker-compose) is required.

The test setup a Influxdb database for testing against real queries.

In order to run the tests just run the command::

    ./run_tests_with_docker.sh
