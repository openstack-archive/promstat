# Copyright (c) 2018 Red Hat, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

import time

import pbr.version
import prometheus_client
import statsd

__version__ = pbr.version.VersionInfo('promstat').version_string()


class Metric(object):
    _metric_class = None

    def __init__(
            self,
            name,
            documentation,
            registry,
            labelnames,
            template,
            statsd_client,
            statsd_key=None,
            prom_metric=None):
        self._name = name
        self._documentation = documentation
        self._registry = registry
        self._labelnames = labelnames
        self._template = template
        self._statsd_client = statsd_client
        self._stastd_key = statsd_key or template
        if not template and not statsd_key:
            # Blank out the client for this metric if there is no template
            self._statsd_client = None

        self._prom_metric = prom_metric
        if self._registry and not self._prom_metric:
            self._prom_metric = self._metric_class(
                name=self._name,
                documentation=self._documentation,
                registry=self._registry,
                labelnames=self._labelnames)

    def labels(self, **kwargs):
        if self.template:
            statsd_key = self.template.format(**kwargs)
        else:
            statsd_key = self._statsd_key
        prom_metric = self._prom_metric
        if prom_metric:
            prom_metric = prom_metric.labels(**kwargs)
        return self.__class__(
            name=self._name,
            documentation=self._documentation,
            registry=self._registry,
            labelnames=self._labelnames,
            template=self._template,
            statsd_client=self._statsd_client,
            statsd_key=statsd_key,
            prom_metric=prom_metric)


class Counter(Metric):
    _metric_class = prometheus_client.Counter

    def inc(self, amount=1):
        if self._prom_metric:
            return self._prom_metric.inc(amount=amount)
        if self._statsd_client:
            self._statsd_client.incr(self._statsd_key)


class Gauge(Metric):
    _metric_class = prometheus_client.Gauge

    def inc(self, amount=1):
        if self._prom_metric:
            return self._prom_metric.inc(amount=amount)
        if self._statsd_client:
            self._statsd_client.gauge(self._statsd_key, amount, delta=True)

    def dec(self, amount=1):
        if self._prom_metric:
            return self._prom_metric.dec(amount=amount)
        if self._statsd_client:
            self._statsd_client.gauge(self._statsd_key, -amount, delta=True)

    def set(self, value):
        if self._prom_metric:
            return self._prom_metric.set(value=value)
        if self._statsd_client:
            self._statsd_client.gauge(self._statsd_key, value, delta=False)

    def set_to_current_time(self):
        current_time = time.time()
        self.set(current_time)


class Summary(Metric):
    _metric_class = prometheus_client.Summary

    def observe(self, amount):
        pass


class Histogram(Metric):
    _metric_class = prometheus_client.Histogram

    def observe(self, amount):
        if self._prom_metric:
            return self._prom_metric.observe(amount=amount)
        if self._statsd_client:
            self._statsd_client.timing(self._statsd_key, amount)

    def _get_metric_class(self):
        return prometheus_client.Histogram


class Info(Metric):
    _metric_class = prometheus_client.Info

    def info(self, val):
        pass


class Enum(Metric):
    _metric_class = prometheus_client.Enum

    def state(self, state):
        pass


class DuplicateMetric(Exception):
    pass


class PromStat(object):

    def __init__(
            self,
            registry=None,
            statsd_client=None, statsd_prefix=None,
            statsd_host=None, statsd_port=None,
            use_prometheus=True, use_statsd=True):
        self._registry = registry
        if not self._registry and use_prometheus:
            self._registry = prometheus_client.CollectorRegistry()

        self._statsd_client = statsd_client
        if not self._statsd_client and use_statsd:
            statsd_args = {}
            if statsd_host:
                statsd_args['host'] = self._statsd_host
            if statsd_port:
                statsd_args['port'] = self._statsd_port
            if statsd_args:
                self._stats_client = statsd.StatsClient(**statsd_args)

        self._statsd_prefix = statsd_prefix
        self._metrics = {}

    def _get_metric(
            self, name, documentation, template,
            metric_class, labelnames, **kwargs):
        if not labelnames:
            labelnames = []
        if self._statsd_prefix:
            template = '.'.join([self._statsd_prefix, template])
        existing = self._metrics.get(name)
        if existing:
            if not isinstance(existing, metric_class):
                raise DuplicateMetric(
                    "Duplicate metric defined for {name} which is class"
                    "{existing_class}. Attempting to redefined as {new_class}."
                    "A metric with the same name must be the same.".format(
                        name=name,
                        existing_class=existing.__class__.__name__,
                        new_class=metric_class.__name__))
            if set(labelnames) != set(existing._labelnames):
                raise DuplicateMetric(
                    "Duplicate metric defined for {name} with mismatching"
                    " label names. Existing metric defined {existing_labels}"
                    " while new metric is defining {new_labels}.".format(
                        name=name,
                        existing_labels=existing._labelnames,
                        new_labels=labelnames))
            return existing

        self._metrics[name] = metric_class(
            name=name,
            documentation=documentation,
            registry=self._registry,
            labelnames=labelnames,
            template=template,
            statsd_client=self._statsd_client,
            **kwargs)
        return self._metrics[name]

    def gauge(self, name, documentation, template=None, labelnames=None):
        return self._get_metric(
            name=name, documentation=documentation,
            template=template, metric_class=Gauge,
            labelnames=labelnames)

    def incr_gauge(
            self, name, documentation, amount=1, template=None, **kwargs):
        metric = self.gauge(
            name, documentation, template=template, labelnames=kwargs.keys())
        return metric.labels(**kwargs).incr(amount)

    def histogram(self, name, documentation, template=None, labelnames=None):
        return self._get_metric(
            name=name, documentation=documentation,
            template=template, metric_class=Histogram,
            labelnames=labelnames)

    def observe_histogram(
            self, name, documentation, value, template=None, **kwargs):
        metric = self.histogram(
            name, documentation, template=template, labelnames=kwargs.keys())
        return metric.labels(**kwargs).observe(value)

    def start_http_server(self, port, addr=''):
        if prometheus_client:
            prometheus_client.start_http_server(
                port=port,
                addr=addr,
                registry=self._registry)

    def make_wsgi_app(self):
        if prometheus_client:
            prometheus_client.make_wsgi_app(registry=self._registry)
