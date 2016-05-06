FROM python:2.7

MAINTAINER Adrián Ribao adrian@adrima.es

# You can force a daily or weekly upgrade of all your 
# packages changing REFRESHED_AT date, from time to time 
# otherwise the first lines would be cached by docker and  
# you would always use non up-to-date versions of your OS

ENV REFRESHED_AT 2016-05-06-12:00


ADD requirements.txt /tmp/requirements.txt
RUN pip install -r /tmp/requirements.txt

ADD test_requirements.txt /tmp/test_requirements.txt
RUN pip install -r /tmp/test_requirements.txt
