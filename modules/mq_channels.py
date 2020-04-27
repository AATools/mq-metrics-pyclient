# -*- coding: utf-8 -*-
import re
import time
import datetime
from log.logger_client import set_logger


logger = set_logger()


def get_channels(channels_data):
    channel_str_regexp = r'CHANNEL\([^)]*\)'
    result = re.findall(channel_str_regexp, channels_data)
    return result


def extract_channel_name(channel):
    channel_name_regexp = r'\(([^}]+)\)'
    # Hidden default system channels
    channel_system_default_regexp = r'SYSTEM.'
    # Hidden default system channels for automatic definition of receiver
    # and server-connection
    match = re.findall(channel_name_regexp, channel)
    channel_name = ''.join(match)
    if not (re.search(channel_system_default_regexp, channel_name)):
        return channel_name
    else:
        pass


def get_template():
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
    status_data = []
    for i in range(channel_data.count("AMQ84")):
        status_data.append(get_template())
        for key in status_data[i]:
            try:
                if key in labels_data[i]:
                    status_data[i][key] = labels_data[i][key]
            except IndexError as err:
                logger.error(err)
                logger.error("Error for key: {0} in status_data: {1}".format(
                    key,
                    labels_data))
    return status_data


def format_channel_output(data_to_format):
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
                item = item+'( )'
                key = re.search(key_regex, item).group()
            value = re.search(value_regex, item).group(1)
            date_result[key] = value
    return result


def check_empty_value(value):
    try:
        value = int(value)
    except ValueError:
        value = '0'
    return int(value)


def make_metric_for_mq_channels_status(channel_data, mqm, metric_type):
    metric_name = 'mq_channel_{0}'.format(metric_type)
    metric_name_buffers = 'mq_channel_{0}'.format('buffers')
    metric_name_bytes = 'mq_channel_{0}'.format('bytes')
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
    metric_type_dict = {
        "status": '{0}\n{1}\n{2}{{qmname="{3}", conname="{4}", substate="{5}", xmitq="{6}", chltype="{7}", \
chstada="{8}", chstati="{9}", rqmname="{10}", jobname="{11}", channel="{12}"}} {13}\n'.format(
            '# HELP {0} Current status of MQ channel.'.format(metric_name),
            '# TYPE {0} gauge'.format(metric_name),
            metric_name,
            mqm,
            channel_data['CONNAME'],
            channel_data['SUBSTATE'],
            channel_data['XMITQ'],
            channel_data['CHLTYPE'],
            channel_data['CHSTADA'],
            channel_data['CHSTATI'],
            channel_data['RQMNAME'],
            channel_data['JOBNAME'],
            channel_name,
            status_dict[channel_data['STATUS']]),
        "buffers_received": '{0}\n{1}\n{2}{{qmname="{3}", conname="{4}", substate="{5}", xmitq="{6}", chltype="{7}", \
chstada="{8}", chstati="{9}", rqmname="{10}", indicator="buffers_received", jobname="{11}", channel="{12}"}} {13}\n'.format(
            '# HELP {0} Number of transmission buffers received and sent.'.format(metric_name_buffers),
            '# TYPE {0} counter'.format(metric_name_buffers),
            metric_name_buffers,
            mqm,
            channel_data['CONNAME'],
            channel_data['SUBSTATE'],
            channel_data['XMITQ'],
            channel_data['CHLTYPE'],
            channel_data['CHSTADA'],
            channel_data['CHSTATI'],
            channel_data['RQMNAME'],
            channel_data['JOBNAME'],
            channel_name,
            check_empty_value(channel_data['BUFSRCVD'])),
        "buffers_sent": '{0}\n{1}\n{2}{{qmname="{3}", conname="{4}", substate="{5}", xmitq="{6}", chltype="{7}", \
chstada="{8}", chstati="{9}", rqmname="{10}", indicator="buffers_sent", jobname="{11}", channel="{12}"}} {13}\n'.format(
            '# HELP {0} Number of transmission buffers received and sent.'.format(metric_name_buffers),
            '# TYPE {0} counter'.format(metric_name_buffers),
            metric_name_buffers,
            mqm,
            channel_data['CONNAME'],
            channel_data['SUBSTATE'],
            channel_data['XMITQ'],
            channel_data['CHLTYPE'],
            channel_data['CHSTADA'],
            channel_data['CHSTATI'],
            channel_data['RQMNAME'],
            channel_data['JOBNAME'],
            channel_name,
            check_empty_value(channel_data['BUFSSENT'])),
        "bytes_received": '{0}\n{1}\n{2}{{qmname="{3}", conname="{4}", substate="{5}", xmitq="{6}", chltype="{7}", \
chstada="{8}", chstati="{9}", rqmname="{10}", indicator="bytes_received", jobname="{11}", channel="{12}"}} {13}\n'.format(
            '# HELP {0} Number of bytes received and sent during this session.'.format(metric_name_bytes),
            '# TYPE {0} counter'.format(metric_name_bytes),
            metric_name_bytes,
            mqm,
            channel_data['CONNAME'],
            channel_data['SUBSTATE'],
            channel_data['XMITQ'],
            channel_data['CHLTYPE'],
            channel_data['CHSTADA'],
            channel_data['CHSTATI'],
            channel_data['RQMNAME'],
            channel_data['JOBNAME'],
            channel_name,
            check_empty_value(channel_data['BYTSRCVD'])),
        "bytes_sent": '{0}\n{1}\n{2}{{qmname="{3}", conname="{4}", substate="{5}", xmitq="{6}", chltype="{7}", \
chstada="{8}", chstati="{9}", rqmname="{10}", indicator="bytes_sent", jobname="{11}", channel="{12}"}} {13}\n'.format(
            '# HELP {0} Number of bytes received and sent during this session.'.format(metric_name_bytes),
            '# TYPE {0} counter'.format(metric_name_bytes),
            metric_name_bytes,
            mqm,
            channel_data['CONNAME'],
            channel_data['SUBSTATE'],
            channel_data['XMITQ'],
            channel_data['CHLTYPE'],
            channel_data['CHSTADA'],
            channel_data['CHSTATI'],
            channel_data['RQMNAME'],
            channel_data['JOBNAME'],
            channel_name,
            check_empty_value(channel_data['BYTSSENT'])),
        "lmsg": '{0}\n{1}\n{2}{{qmname="{3}", conname="{4}", substate="{5}", xmitq="{6}", chltype="{7}", \
chstada="{8}", chstati="{9}", rqmname="{10}", jobname="{11}", channel="{12}"}} {13}\n'.format(
            '# HELP {0} Timestamp on which the last message was sent or MQI call was handled.'.format(metric_name),
            '# TYPE {0} gauge'.format(metric_name),
            metric_name,
            mqm,
            channel_data['CONNAME'],
            channel_data['SUBSTATE'],
            channel_data['XMITQ'],
            channel_data['CHLTYPE'],
            channel_data['CHSTADA'],
            channel_data['CHSTATI'],
            channel_data['RQMNAME'],
            channel_data['JOBNAME'],
            channel_name,
            check_empty_value(metric_value_lmsg)),
        "msgs": '{0}\n{1}\n{2}{{qmname="{3}", conname="{4}", substate="{5}", xmitq="{6}", chltype="{7}", \
chstada="{8}", chstati="{9}", rqmname="{10}", jobname="{11}", channel="{12}"}} {13}\n'.format(
            '# HELP {0} Number of messages sent or received during this session.'.format(metric_name),
            '# TYPE {0} counter'.format(metric_name),
            metric_name,
            mqm,
            channel_data['CONNAME'],
            channel_data['SUBSTATE'],
            channel_data['XMITQ'],
            channel_data['CHLTYPE'],
            channel_data['CHSTADA'],
            channel_data['CHSTATI'],
            channel_data['RQMNAME'],
            channel_data['JOBNAME'],
            channel_name,
            check_empty_value(channel_data['MSGS'])),
        "batches": '{0}\n{1}\n{2}{{qmname="{3}", conname="{4}", substate="{5}", xmitq="{6}", chltype="{7}", \
chstada="{8}", chstati="{9}", rqmname="{10}", jobname="{11}", channel="{12}"}} {13}\n'.format(
            '# HELP {0} Number of completed batches during this session.'.format(metric_name),
            '# TYPE {0} counter'.format(metric_name),
            metric_name,
            mqm,
            channel_data['CONNAME'],
            channel_data['SUBSTATE'],
            channel_data['XMITQ'],
            channel_data['CHLTYPE'],
            channel_data['CHSTADA'],
            channel_data['CHSTATI'],
            channel_data['RQMNAME'],
            channel_data['JOBNAME'],
            channel_name,
            check_empty_value(channel_data['BATCHES']))
    }
    return metric_type_dict[metric_type]
