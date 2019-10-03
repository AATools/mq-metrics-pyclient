# -*- coding: utf-8 -*-
import re
import os
from log.logger_client import set_logger

logger = set_logger()


def get_channels(channels_data):
    channel_str_regexp = 'CHANNEL\([^)]*\)'
    result = re.findall(channel_str_regexp, channels_data)
    return result


def extract_channel_name(channel):
    channel_name_regexp = '\(([^}]+)\)'
    # Hidden default system channels
    channel_system_default_regexp = 'SYSTEM.'
    # Hidden default system channels for automatic definition of receiver and server-connection
    match = re.findall(channel_name_regexp, channel)
    channel_name = ''.join(match)
    if not (re.search(channel_system_default_regexp, channel_name)):
        return channel_name
    else:
        pass


def get_template():
    status_data_template = {
        'CHANNEL': '',
        'CHLTYPE': '',
        'CONNAME': '',
        'RQMNAME': '',
        'XMITQ': '',
        'SUBSTATE': '',
        'STATUS': ''
        }
    return status_data_template


def get_channel_status(channel_data, labels_data):
    status_data = []
    for i in range(channel_data.count("AMQ84")):
        status_data.append(get_template())
        for key in status_data[i]:
            try:
                if key in labels_data[i]:
                    status_data[i][key] = labels_data[i][key]
            except IndexError, e:
                logger.error(e)
                logger.error("Error for key: {0} in status_data: {1}".format(key, labels_data))
    return status_data


def format_channel_output(data_to_format):
    format_list = filter(None, data_to_format.split('\n'))
    nested_list = [re.split(r'\s{2,}', element.strip()) for element in format_list]
    flat_list = [item for sublist in nested_list for item in sublist]
    value_regex = '\(([^}]+)\)'
    key_regex = '.+?(?=\()'
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


def make_metric_for_mq_channels_status(channel_data, mqm, metric_type, conn_count=0):
    metric_name = 'mq_channel_{0}'.format(metric_type)
    channel_name = channel_data['CHANNEL']
    # Mapping status according to IBM specification:
    # https://www.ibm.com/support/knowledgecenter/en/SSFKSJ_9.0.0/com.ibm.mq.javadoc.doc/WMQJavaClasses/constant-values.html
    status_dict = {
       'INACTIVE': 0,
       'BINDING': 1,
       'STARTING': 2,
       'RUNNING': 3,
       'STOPPING': 4,
       'RETRYING': 5,
       'STOPPED': 6,
       '': 6,
       'REQUESTING': 7,
       'PAUSED': 8,
       'DISCONNECTED': 9,
       'INITIALIZING': 13,
       'SWITCHING': 14
       }
    metric_type_dict = {
        "connection_count": '%s{qmname="%s", conname="%s", substate="%s", xmitq="%s", chltype="%s", rqmname="%s", channel="%s"} %d\n' % (
            metric_name,
            mqm,
            channel_data['CONNAME'],
            channel_data['SUBSTATE'],
            channel_data['XMITQ'],
            channel_data['CHLTYPE'],
            channel_data['RQMNAME'],
            channel_name,
            conn_count),
        "status": '%s{qmname="%s", conname="%s", substate="%s", xmitq="%s", chltype="%s", rqmname="%s", channel="%s"} %d\n' % (
            metric_name,
            mqm,
            channel_data['CONNAME'],
            channel_data['SUBSTATE'],
            channel_data['XMITQ'],
            channel_data['CHLTYPE'],
            channel_data['RQMNAME'],
            channel_name,
            status_dict[channel_data['STATUS']]
            )
    }
    return metric_type_dict[metric_type]
