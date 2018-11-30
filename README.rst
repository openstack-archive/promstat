========
promstat
========

Library for reporting stats to both statsd and prometheus.

`statsd`_ and `prometheus`_ are both popular metrics collecting systems,
but they operate quite differently from each other. ``promstat`` is a
wrapper abstraction library around the statsd and prometheus clients
that allows instrumenting code once so that operators can integrate with
either system.

prometheus has a more structured reporting system, so the calling semantics
of `prometheus_client`_ are used. Each metric reporter has an additional
field, ``template`` which is a statsd metric name template to be used for
the statsd reporting.

``promstat`` does not have a global ``Registry`` like prometheus_client
defaults to using. If you want to use the global Registry object with
``promstat``, pass ``prometheus_client.REGISTRY`` to the ``registry``
parameter of the ``PromStat`` constructor.

* Free software: Apache license
* Documentation: https://docs.openstack.org/promstat/latest
* Source: https://git.openstack.org/cgit/openstack/promstat
* Bugs: https://storyboard.openstack.org/#!/project/openstack/promstat

.. _statsd: https://github.com/etsy/statsd
.. _prometheus: https://prometheus.io/
.. _prometheus_client: https://pypi.org/project/prometheus_client/
