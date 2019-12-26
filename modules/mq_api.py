# -*- coding: utf-8 -*-
import os


def run_mq_command(**kwargs):
    command_mapping = {
        'get_channels': 'display channel (*)',
        'get_chstatus': 'dis chstatus({0})',
        'get_channel': 'display channel({0})',
        'get_listeners': 'display listener(*)',
        'get_listener': 'display listener({0})',
        'get_lsstatus': 'dis lsstatus({0})',
        'get_mq_manager_status': 'dspmq -m {0} -o all',
        'get_mq_managers': 'dspmq',
        'get_queues': 'display queue(*) TYPE(QLOCAL) CURDEPTH MAXDEPTH',
        'get_queues_monitor': 'display qstatus(*) MONITOR'
    }
    task_is_mq_manager_status = False
    mq_object = ''
    mq_manager = ''
    for arg_name, arg_value in kwargs.items():
        if arg_name == 'task':
            if arg_value == 'get_mq_manager_status':
                task_is_mq_manager_status = True
            mq_command = command_mapping[arg_value]
        elif arg_name == 'mqm':
            mq_manager = arg_value
        else:
            mq_object = arg_value
    if mq_object and mq_manager:
        command = 'echo "{0}"| runmqsc {1}'.format(mq_command.format(mq_object), mq_manager)
    elif not mq_object and (mq_manager):
        command = 'echo "{0}"| runmqsc {1}'.format(mq_command, mq_manager)
    elif not mq_manager:
        command = mq_command
    if task_is_mq_manager_status:
        command = mq_command.format(mq_manager)
    output = os.popen(command).read()
    return output
