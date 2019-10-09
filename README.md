# IBM MQ metrics exporter

This is another python client for collecting IBM MQ metrics and exporting to [Prometheus pushgateway](https://github.com/prometheus/pushgateway). 
The collected metrics can be explored in Prometheus or Grafana. This client is useful in cases when requiring to collect metrics from old MQ versions.

The metrics are collected using standard [`MQSC`](https://www.ibm.com/support/knowledgecenter/en/SSFKSJ_7.5.0/com.ibm.mq.ref.adm.doc/q085130_.htm) commands. So, you need to install `IBM MQ server`.

Tested for IBM MQ v7.5 and v8.0 and Python 2.6 and 2.7 on Linux.

## Collected metrics

By default, metrics are collected every 15 seconds.

The metrics provided by the client:
* `mq_manager_status...` - current status of MQ managers;
* `mq_listener_status...` - current status of MQ listeners;
* `mq_channel_status...` - current status of MQ channels;
* `mq_channel_connection_count...` -  connections counts to the channels;
* `mq_queue_curdepth...` - current depth of queues;
* `mq_queue_maxdepth...` - maximum depth of queues.

## Getting Started

Python 2.6 or 2.7 should be already installed.

Download Prometheus Pushgateway from the [release page](https://github.com/prometheus/pushgateway/releases) and unpack the tarball.

### Run Prometheus Pushgateway

```bash
cd pushgateway
nohup ./pushgateway > pushgateway.log &
```

For Pushgateway the default port is used (":9091").

### Run mq-metrics-pyclient

```bash
git clone https://github.com/AATools/mq-metrics-pyclient
cd mq-metrics-pyclient
chmod u+x ./mq_metrics_client.py
nohup mq_metrics_client.py &
```

After that, you should set up your Prometheus server to collect metrics from Pushgateway (`http://<hostname>:9091/metrics`).

## Grafana dashboard

The Grafana dashboard visualizes collected metrics.

## Simple process scheme

![](../images/mq_metrics_pyclient_scheme.jpg?raw=true)
