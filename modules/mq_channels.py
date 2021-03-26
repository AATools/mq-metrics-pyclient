# -*- coding: utf-8 -*-
"""Various functions for MQ channels."""
import re
import time
import datetime
from log.logger_client import set_logger
from modules.mq_api import (
    run_mq_command,
    add_annotation)


logger = set_logger()


def get_metric_name(metric_label):
    """Returns pushgateway formatted metric name."""
    return 'mq_channel_{0}'.format(metric_label)


def get_metric_annotation():
    """Returns dictionary with annotations `HELP` and `TYPE` for metrics."""
    annotations = {
        'status': ['# HELP {0} Current status of MQ channel.\n\
# TYPE {0} gauge\n'.format(get_metric_name('status')), 0],
        'buffers': ['# HELP {0} Number of transmission buffers received and sent.\n\
# TYPE {0} counter\n'.format(get_metric_name('buffers')), 1],
        'bytes': ['# HELP {0} Number of bytes received and sent during this session.\n\
# TYPE {0} counter\n'.format(get_metric_name('bytes')), 2],
        'lmsg': ['# HELP {0} Timestamp on which the last message was sent or MQI call was handled.\n\
# TYPE {0} gauge\n'.format(get_metric_name('lmsg')), 3],
        'msgs': ['# HELP {0} Number of messages sent or received during this session.\n\
# TYPE {0} counter\n'.format(get_metric_name('msgs')), 4],
        'batches': ['# HELP {0} Number of completed batches during this session.\n\
# TYPE {0} counter\n'.format(get_metric_name('batches')), 5]}
    return annotations


def channels_status(mqm, ssh_connect_string=None):
    """Returns dictionary with channels data."""
    channels = run_mq_command(task='get_channels', mqm=mqm, ssh_connect_string=ssh_connect_string)
    channels_list = get_channels(channels_data=channels)
    mq_channels_status = {}
    for channel in channels_list:
        channel_name = extract_channel_name(channel=channel)
        if channel_name:
            channel_data = run_mq_command(
                task='get_chstatus',
                mqm=mqm,
                channel=channel_name,
                ssh_connect_string=ssh_connect_string)
            labels_data = []
            stop_flag = "not found"
            if stop_flag in channel_data:
                channel_labels = run_mq_command(
                    task='get_channel',
                    mqm=mqm,
                    channel=channel_name,
                    ssh_connect_string=ssh_connect_string)
                labels_data = format_channel_output(data_to_format=channel_labels)
            else:
                labels_data = format_channel_output(data_to_format=channel_data)
            channel_status = get_channel_status(channel_data=channel_data, labels_data=labels_data)
            mq_channels_status[channel_name] = channel_status
    return mq_channels_status


def get_mq_channels_metrics(mq_channels, mq_manager):
    """Returns string with all metrics which ready to push to pushgateway."""
    metrics_annotation = get_metric_annotation()
    prometheus_data_list = list(list() for i in range(len(metrics_annotation)))
    prometheus_data_list_result = list()
    for channels in mq_channels:
        for channel_data in mq_channels[channels]:
            metric_data_stat = make_metric_for_mq_channels_status(
                channel_data=channel_data,
                mqm=mq_manager,
                metric_type='status')
            prometheus_data_list[metrics_annotation['status'][1]].append(metric_data_stat)
            if not channel_data['STATUS']:
                continue
            else:
                metric_data_buffers_received = make_metric_for_mq_channels_status(
                    channel_data=channel_data,
                    mqm=mq_manager,
                    metric_type='buffers_received')
                metric_data_buffers_sent = make_metric_for_mq_channels_status(
                    channel_data=channel_data,
                    mqm=mq_manager,
                    metric_type='buffers_sent')
                metric_data_bytes_received = make_metric_for_mq_channels_status(
                    channel_data=channel_data,
                    mqm=mq_manager,
                    metric_type='bytes_received')
                metric_data_bytes_sent = make_metric_for_mq_channels_status(
                    channel_data=channel_data,
                    mqm=mq_manager,
                    metric_type='bytes_sent')
                metric_data_lmsg = make_metric_for_mq_channels_status(
                    channel_data=channel_data,
                    mqm=mq_manager,
                    metric_type='lmsg')
                metric_data_msgs = make_metric_for_mq_channels_status(
                    channel_data=channel_data,
                    mqm=mq_manager,
                    metric_type='msgs')
                metric_data_batches = make_metric_for_mq_channels_status(
                    channel_data=channel_data,
                    mqm=mq_manager,
                    metric_type='batches')
                prometheus_data_list[metrics_annotation['buffers'][1]].extend([
                    metric_data_buffers_received,
                    metric_data_buffers_sent])
                prometheus_data_list[metrics_annotation['bytes'][1]].extend([
                    metric_data_bytes_received,
                    metric_data_bytes_sent])
                prometheus_data_list[metrics_annotation['lmsg'][1]].append(metric_data_lmsg)
                prometheus_data_list[metrics_annotation['msgs'][1]].append(metric_data_msgs)
                prometheus_data_list[metrics_annotation['batches'][1]].append(metric_data_batches)
    for key in sorted(metrics_annotation.keys()):
        add_annotation(prometheus_data_list[metrics_annotation[key][1]], metrics_annotation[key][0])
        prometheus_data_list_result.extend(prometheus_data_list[metrics_annotation[key][1]])
    prometheus_data_str = ''.join(prometheus_data_list_result)
    return prometheus_data_str


def get_channels(channels_data):
    """Gets data with channel names from the input string."""
    channel_str_regexp = r'CHANNEL\([^)]*\)'
    result = re.findall(channel_str_regexp, channels_data)
    return result


def extract_channel_name(channel):
    """Extracts channel name. Hiddens default system channels."""
    channel_name_regexp = r'\(([^}]+)\)'
    # Hidden default system channels
    channel_system_default_regexp = r'SYSTEM.'
    # Hidden default system channels for automatic definition of receiver and server-connection
    match = re.findall(channel_name_regexp, channel)
    channel_name = ''.join(match)
    if not (re.search(channel_system_default_regexp, channel_name)):
        return channel_name
    else:
        pass


def get_template():
    """Returns dictionary with labels template."""
    status_data_template = {
        'BATCHES': '',
        'BUFSRCVD': '',
        'BUFSSENT': '',
        'BYTSRCVD': '',
        'BYTSSENT': '',
        'CHANNEL': '',
        'CHLTYPE': '',
        'CHSTADA': '',
        'CHSTATI': '',
        'CONNAME': '',
        'JOBNAME': '',
        'LSTMSGDA': '',
        'LSTMSGTI': '',
        'MSGS': '',
        'RQMNAME': '',
        'XMITQ': '',
        'SUBSTATE': '',
        'STATUS': ''}
    return status_data_template


def get_channel_status(channel_data, labels_data):
    """Maps input string with data on template labels.
    Returns list with dictionaries, which contain parsed data."""
    status_data = list()
    for i in range(channel_data.count("AMQ84")):
        status_data.append(get_template())
        for key in status_data[i]:
            try:
                if key in labels_data[i]:
                    status_data[i][key] = labels_data[i][key]
            except IndexError as err:
                logger.error(err)
                logger.error("Error for key: {0} in status_data: {1}".format(key, labels_data))
    return status_data


def format_channel_output(data_to_format):
    """Searches `AMQ84` and `One MQSC`.
    Searches for data between these labels according to the regular expression.
    Returns list with data."""
    format_list = list(filter(None, data_to_format.split('\n')))
    nested_list = [re.split(r'\s{2,}', element.strip()) for element in format_list]
    flat_list = [item for sublist in nested_list for item in sublist]
    value_regex = r'\(([^}]+)\)'
    key_regex = r'.+?(?=\()'
    gather = False
    result = []
    date_result = {}
    for item in flat_list:
        if item.startswith("AMQ84"):
            if date_result:
                result.append(date_result)
            date_result = {}
            gather = True
        elif item.startswith("One MQSC"):
            result.append(date_result)
            gather = False
        elif item and gather:
            try:
                key = re.search(key_regex, item).group()
            except AttributeError:
                item = item + '( )'
                key = re.search(key_regex, item).group()
            value = re.search(value_regex, item).group(1)
            date_result[key] = value
    return result


def check_empty_value(value):
    """Replaces an empty value with 0."""
    try:
        value = int(value)
    except ValueError:
        value = '0'
    return int(value)


def make_metric_for_mq_channels_status(channel_data, mqm, metric_type):
    """Returns dictionary with all metrics for one channel in pushgateway format.
    Converts input dictionary with data to pushgateway formatted string."""
    value_lmsg = ' '.join([channel_data['LSTMSGDA'], channel_data['LSTMSGTI']])
    try:
        metric_value_lmsg = time.mktime(datetime.datetime.strptime(value_lmsg, "%Y-%m-%d %H.%M.%S").timetuple())
    except ValueError:
        metric_value_lmsg = ''
    channel_name = channel_data['CHANNEL']
    # Mapping status according to IBM specification:
    # https://www.ibm.com/support/knowledgecenter/en/SSFKSJ_9.0.0/com.ibm.mq.javadoc.doc/WMQJavaClasses/constant-values.html
    status_dict = {
        '': 0,
        'INACTIVE': 0,
        'BINDING': 1,
        'STARTING': 2,
        'RUNNING': 3,
        'STOPPING': 4,
        'RETRYING': 5,
        'STOPPED': 6,
        'REQUESTING': 7,
        'PAUSED': 8,
        'DISCONNECTED': 9,
        'INITIALIZING': 13,
        'SWITCHING': 14}
    template_string = 'qmname="{0}", conname="{1}", substate="{2}", xmitq="{3}", chltype="{4}", \
chstada="{5}", chstati="{6}", rqmname="{7}", jobname="{8}", channel="{9}"'.format(
        mqm,
        channel_data['CONNAME'],
        channel_data['SUBSTATE'],
        channel_data['XMITQ'],
        channel_data['CHLTYPE'],
        channel_data['CHSTADA'],
        channel_data['CHSTATI'],
        channel_data['RQMNAME'],
        channel_data['JOBNAME'],
        channel_name)
    metric_type_dict = {
        'status': '{0}{{{1}}} {2}\n'.format(
            get_metric_name('status'),
            template_string,
            status_dict[channel_data['STATUS']]),
        'buffers_received': '{0}{{{1}, indicator="buffers_received"}} {2}\n'.format(
            get_metric_name('buffers'),
            template_string,
            check_empty_value(channel_data['BUFSRCVD'])),
        'buffers_sent': '{0}{{{1}, indicator="buffers_sent"}} {2}\n'.format(
            get_metric_name('buffers'),
            template_string,
            check_empty_value(channel_data['BUFSSENT'])),
        'bytes_received': '{0}{{{1}, indicator="bytes_received"}} {2}\n'.format(
            get_metric_name('bytes'),
            template_string,
            check_empty_value(channel_data['BYTSRCVD'])),
        'bytes_sent': '{0}{{{1}, indicator="bytes_sent"}} {2}\n'.format(
            get_metric_name('bytes'),
            template_string,
            check_empty_value(channel_data['BYTSSENT'])),
        'lmsg': '{0}{{{1}}} {2}\n'.format(
            get_metric_name('lmsg'),
            template_string,
            check_empty_value(metric_value_lmsg)),
        'msgs': '{0}{{{1}}} {2}\n'.format(
            get_metric_name('msgs'),
            template_string,
            check_empty_value(channel_data['MSGS'])),
        'batches': '{0}{{{1}}} {2}\n'.format(
            get_metric_name('batches'),
            template_string,
            check_empty_value(channel_data['BATCHES']))}
    return metric_type_dict[metric_type]
