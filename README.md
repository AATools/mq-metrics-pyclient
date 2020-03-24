# IBM MQ metrics exporter

[![Build Status](https://travis-ci.com/AATools/mq-metrics-pyclient.svg?branch=master)](https://travis-ci.com/AATools/mq-metrics-pyclient) [![Coverage Status](https://coveralls.io/repos/github/AATools/mq-metrics-pyclient/badge.svg?branch=master)](https://coveralls.io/github/AATools/mq-metrics-pyclient?branch=master)

This is another python client for collecting IBM MQ metrics and exporting to [Prometheus pushgateway](https://github.com/prometheus/pushgateway).
The collected metrics can be explored in Prometheus or Grafana. This client is useful in cases when requiring to collect metrics from old MQ versions.

The metrics are collected using standard [`MQSC`](https://www.ibm.com/support/knowledgecenter/en/SSFKSJ_7.5.0/com.ibm.mq.ref.adm.doc/q085130_.htm) commands. So, you need to install `IBM MQ server`.

Tested for IBM MQ v7.5 and v8.0 and Python 2.6, 2.7, 3.6 on Linux.

## Collected metrics

By default, metrics are collected every 15 seconds.

The metrics provided by the client:

* `mq_manager_status...` - current status of MQ manager;
* `mq_listener_status...` - current status of MQ listener;
* `mq_channel_status...` - current status of MQ channel;
* `mq_channel_batches...` - number of completed batches during this session (since the channel was started);
* `mq_channel_buffers...` - number of transmission buffers received and sent;
* `mq_channel_bytes...` - number of bytes received and sent during this session (since the channel was started);
* `mq_channel_lmsg...` - timestamp on which the last message was sent or MQI call was handled;
* `mq_channel_msgs...` - number of messages sent or received during this session (since the channel was started);
* `mq_queue_curdepth...` - current depth of queue;
* `mq_queue_maxdepth...` - maximum depth of queue;<br> <br>
When [real-time monitoring](https://www.ibm.com/support/knowledgecenter/en/SSFKSJ_8.0.0/com.ibm.mq.mon.doc/q037990_.htm) for queues is enabled:
* `mq_queue_msgage...` - age of the oldest message on the queue;
* `mq_queue_lput...` -  timestamp on which the last message was put to the queue;
* `mq_queue_lget...` - timestamp on which the last message was retrieved from the queue;
* `mq_queue_qtime...` - interval between messages being put on the queue and then being destructively read.

See [detailed description of the metrics](#metrics-detailed-description) for an in-depth understanding.

You can run `MQ metrics pyclient` and [IB metrics pyclient](https://github.com/AATools/ib-metrics-pyclient) together. Metrics from both clients will be sent to the same pushgateway. Conflicts will not arise.

## Getting Started

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
nohup python3 mq_metrics_client.py &
```

After that, you should set up your Prometheus server to collect metrics from Pushgateway (`http://<hostname>:9091/metrics`).

## Grafana dashboard

The Grafana dashboard visualizes collected metrics. This is an example of a dashboard. You can create your own dashboards to analyze metrics.

## Simple process scheme

![mq_metrics_pyclient_scheme](../images/mq_metrics_pyclient_scheme.jpg?raw=true)

## Metrics detailed description

| Metric | Description |
|:---|:---|
| mq_manager_status | The metric shows current status of MQ manager.<br /> If there are several managers on host, there will be a own metric for each manager.<br> Possible values:<br> <span style="margin-left:2em">`0` - STOPPED;</span><br> <span style="margin-left:2em">`1` - RUNNING.</span><br> Example display in Pushgateway:<br> `mq_manager_status{default="no",instance="",instname="Installation1",instpath="/opt/mqm",instver="7.5.0.0",job="QM1",qmname="QM1",standby="Not permitted"} 1` |
| mq_listener_status | The metric shows current status of MQ listener.<br> If there are several listeners on mq manager, there will be a own metric for each listener.<br> The default listener `SYSTEM.DEFAULT.LISTENER.TCP` is **hidden**.<br> Possible values:<br> <span style="margin-left:2em">`0` - STOPPED;</span><br> <span style="margin-left:2em">`1` - STOPING;<br> <span style="margin-left:2em">`2` - STARTING;</span><br> <span style="margin-left:2em">`3` - RUNNING.</span><br> Example display  in Pushgateway:<br> `mq_listener_status{backlog="10000",control="QMGR",desc=" ",instance="",ipadd="*",job="QM1",listener="QM1.LST",pid="13111",port="1414",qmname="QM1",startda="2019-12-25",startti="12.00.00",trptype="TCP"} 3` |
| mq_channel_status | The metric shows current status of MQ channel.<br> If there are several channels on mq manager, there will be a own metric for each channel.<br> The default channels `SYSTEM.*` are **hidden**.<br> Possible values:<br> <span style="margin-left:2em">`0` - INACTIVE;</span><br> <span style="margin-left:2em">`1` - BINDING;<br> <span style="margin-left:2em">`2` - STARTING;</span><br> <span style="margin-left:2em">`3` - RUNNING;</span><br> <span style="margin-left:2em">`4` - STOPPING;</span><br> <span style="margin-left:2em">`5` - RETRYING;</span><br> <span style="margin-left:2em">`6` - STOPPED;</span><br> <span style="margin-left:2em">`7` - REQUESTING;</span><br> <span style="margin-left:2em">`8` - PAUSED;</span><br> <span style="margin-left:2em">`9` - DISCONNECTED;</span><br> <span style="margin-left:2em">`13` - INITIALIZING;</span><br> <span style="margin-left:2em">`14` - SWITCHING;</span><br> Example display in Pushgateway:<br> `mq_channel_status{channel="QM1.SVRCONN",chltype="SVRCONN",chstada="2020-02-28",chstati="11.23.21",conname="127.0.0.1",instance="",job="QM1",jobname="000010EC00000007",qmname="QM1",rqmname="",substate="RECEIVE",xmitq=""} 3` |
| mq_channel_batches | The metric shows number of transmission buffers received and sent. This includes transmissions to receive control information only.<br> If there are several channels on mq manager, there will be a own metric for each channel.<br> The default channels `SYSTEM.*` are **hidden**.<br> The metric is collected if current status or status of saved information is available.<br> Example display in Pushgateway:<br> `mq_channel_batches{channel="QM1.SVRCONN",chltype="SVRCONN",chstada="2020-02-28",chstati="11.23.21",conname="127.0.0.1",instance="",job="QM1",jobname="000010EC00000007",qmname="QM1",rqmname="",substate="RECEIVE",xmitq=""} 0` |
| mq_channel_buffers | The metric shows number of completed batches during this session (since the channel was started).<br> For each channel two value of metric are collected - `indicator="buffers_received"` and `indicator="buffers_sent"`.<br> If there are several channels on mq manager, there will be a own metric for each channel.<br> The default channels `SYSTEM.*` are **hidden**.<br> The metric is collected if current status or status of saved information is available.<br> Example display in Pushgateway:<br> `mq_channel_buffers{channel="QM1.SVRCONN",chltype="SVRCONN",chstada="2020-02-28",chstati="11.23.21",conname="127.0.0.1",indicator="buffers_received",instance="",job="QM1",jobname="000010EC00000007",qmname="QM1",rqmname="",substate="RECEIVE",xmitq=""} 8766`<br> `mq_channel_buffers{channel="QM1.SVRCONN",chltype="SVRCONN",chstada="2020-02-28",chstati="11.23.21",conname="127.0.0.1",indicator="buffers_sent",instance="",job="QM1",jobname="000010EC00000007",qmname="QM1",rqmname="",substate="RECEIVE",xmitq=""} 8765` |
| mq_channel_bytes | The metric shows number of bytes received and sent during this session (since the channel was started). This includes control information received by the message channel agent.<br> For each channel two value of metric are collected - `indicator="bytes_received"` and `indicator="bytes_sent"`.<br> If there are several channels on mq manager, there will be a own metric for each channel.<br> The default channels `SYSTEM.*` are **hidden**.<br> The metric is collected if current status or status of saved information is available.<br> Example display in Pushgateway:<br> `mq_channel_bytes{channel="QM1.SVRCONN",chltype="SVRCONN",chstada="2020-02-28",chstati="11.23.21",conname="127.0.0.1",indicator="bytes_received",instance="",job="QM1",jobname="000010EC00000007",qmname="QM1",rqmname="",substate="RECEIVE",xmitq=""} 32552`<br> `mq_channel_bytes{channel="QM1.SVRCONN",chltype="SVRCONN",chstada="2020-02-28",chstati="11.23.21",conname="127.0.0.1",indicator="bytes_sent",instance="",job="QM1",jobname="000010EC00000007",qmname="QM1",rqmname="",substate="RECEIVE",xmitq=""} 33812` |
| mq_channel_lmsg | The metric shows timestamp on which the last message was sent or MQI call was handled.<br> If there are several channels on mq manager, there will be a own metric for each channel.<br> The default channels `SYSTEM.*` are **hidden**.<br> The metric is collected if current status or status of saved information is available.<br> Example display in Pushgateway:<br> `mq_channel_lmsg{channel="QM1.SVRCONN",chltype="SVRCONN",chstada="2020-02-28",chstati="11.23.21",conname="127.0.0.1",instance="",job="QM1",jobname="000010EC00000007",qmname="QM1",rqmname="",substate="RECEIVE",xmitq=""} 1584965991` |
| mq_channel_msgs | The metric shows number of messages sent or received (or, for server-connection channels, the number of MQI calls handled) during this session (since the channel was started).br> If there are several channels on mq manager, there will be a own metric for each channel.<br> The default channels `SYSTEM.*` are **hidden**.<br> The metric is collected if current status or status of saved information is available.<br> Example display in Pushgateway:<br> `mq_channel_msgs{channel="QM1.SVRCONN",chltype="SVRCONN",chstada="2020-02-28",chstati="11.23.21",conname="127.0.0.1",instance="",job="QM1",jobname="000010EC00000007",qmname="QM1",rqmname="",substate="RECEIVE",xmitq=""} 1741` |
| mq_queue_curdepth | The metric shows current depth of local queue.<br> The metric is available for applications and `SYSTEM.*` queues.<br> Example display in Pushgateway:<br> `mq_queue_curdepth{instance="",job="QM1",qmname="QM1",queuename="DEV.QUEUE.1",type="QLOCAL"} 0` |
| mq_queue_maxdepth |  The metric shows maximum depth of local queue.<br> The metric is available for applications and `SYSTEM.*` queues.<br> Example display in Pushgateway:<br> `mq_queue_maxdepth{instance="",job="QM1",qmname="QM1",queuename="DEV.QUEUE.1",type="QLOCAL"} 5000` |
| mq_queue_msgage | If [real-time monitoring](https://www.ibm.com/support/knowledgecenter/en/SSFKSJ_8.0.0/com.ibm.mq.mon.doc/q037990_.htm) for queues is enabled, metric will be collected.<br> If not (`MONQ (OFF)`) or any data from real-time monitoring is blank, there is no metric collected. <br> <br> The metric shows age, in seconds, of the oldest message on the queue.<br> The [maximum value](https://www.ibm.com/support/knowledgecenter/en/SSFKSJ_8.0.0/com.ibm.mq.ref.adm.doc/q086260_.htm) is 999999999.<br> The metricis available for applications and `SYSTEM.*` queues.<br> Example display in Pushgateway:<br> `mq_queue_msgage{instance="",job="QM1",qmname="QM1",queuename="DEV.QUEUE.1"} 0` |
| mq_queue_lput | If [real-time monitoring](https://www.ibm.com/support/knowledgecenter/en/SSFKSJ_8.0.0/com.ibm.mq.mon.doc/q037990_.htm) for queues is enabled, metric will be collected.<br> If not (`MONQ (OFF)`) or any data from real-time monitoring is blank, there is no metric collected. <br> <br> The metric shows timestamp on which the last message was put to the queue since the queue manager started.<br> The metricis available for applications and `SYSTEM.*` queues.<br> Example display in Pushgateway:<br> `mq_queue_lput{instance="",job="QM1",qmname="QM1",queuename="DEV.QUEUE.1"} 1577181600` |
| mq_queue_lget | If [real-time monitoring](https://www.ibm.com/support/knowledgecenter/en/SSFKSJ_8.0.0/com.ibm.mq.mon.doc/q037990_.htm) for queues is enabled, metric will be collected.<br> If not (`MONQ (OFF)`) or any data from real-time monitoring is blank, there is no metric collected. <br> <br> The metric shows timestamp on which the last message was retrieved from the queue since the queue manager started.<br> A message being browsed does not count as a message being retrieved.<br> The metricis available for applications and `SYSTEM.*` queues.<br> Example display in Pushgateway:<br> `mq_queue_lget{instance="",job="QM1",qmname="QM1",queuename="DEV.QUEUE.1"} 1577181601` |
| mq_queue_qtime | If [real-time monitoring](https://www.ibm.com/support/knowledgecenter/en/SSFKSJ_8.0.0/com.ibm.mq.mon.doc/q037990_.htm) for queues is enabled, metric will be collected.<br> If not (`MONQ (OFF)`) or any data from real-time monitoring is blank, there is no metric collected. <br> <br> The metric shows interval, in microseconds, between messages being put on the queue and then being destructively read.<br> The [maximum value](https://www.ibm.com/support/knowledgecenter/en/SSFKSJ_8.0.0/com.ibm.mq.ref.adm.doc/q086260_.htm) is 999999999.<br> For each queue two value of metric are collected - `indicator="short_term"` and `indicator="long_term"`. <br> The metricis available for applications and `SYSTEM.*` queues.<br> Example display in Pushgateway:<br>  `mq_queue_qtime{indicator="short_term",instance="",job="QM1",qmname="QM1",queuename="DEV.QUEUE.1"} 1474`<br> `mq_queue_qtime{indicator="long_term",instance="",job="QM1",qmname="QM1",queuename="DEV.QUEUE.1"} 1486` |
