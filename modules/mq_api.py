# -*- coding: utf-8 -*-
"""Various functions for client api."""
import subprocess


def run_mq_command(**kwargs):
    """Calls predefined MQSC commands and returns their result."""
    ssh_connect_string = kwargs.get("ssh_connect_string", None)
    if ssh_connect_string:
        # escaped command for going through ssh
        command_mapping = {
            'get_channels': 'display channel \(\*\)',
            'get_chstatus': 'display chstatus\({0}\) BATCHES BUFSRCVD BUFSSENT BYTSRCVD BYTSSENT CHSTADA CHSTATI JOBNAME LSTMSGDA LSTMSGTI MSGS',
            'get_channel': 'display channel\({0}\)',
            'get_listeners': 'display listener\(\*\)',
            'get_listener': 'display listener\({0}\)',
            'get_lsstatus': 'display lsstatus\({0}\)',
            'get_mq_manager_status': 'dspmq -m {0} -o all',
            'get_mq_managers': 'dspmq',
            'get_queues': 'display queue\(*\) TYPE\(QLOCAL\) CURDEPTH MAXDEPTH',
            'get_queues_monitor': 'display qstatus\(\*\) MONITOR'
        }
    else:
        command_mapping = {
            'get_channels': 'display channel (*)',
            'get_chstatus': 'display chstatus({0}) BATCHES BUFSRCVD BUFSSENT BYTSRCVD BYTSSENT CHSTADA CHSTATI JOBNAME LSTMSGDA LSTMSGTI MSGS',
            'get_channel': 'display channel({0})',
            'get_listeners': 'display listener(*)',
            'get_listener': 'display listener({0})',
            'get_lsstatus': 'display lsstatus({0})',
            'get_mq_manager_status': 'dspmq -m {0} -o all',
            'get_mq_managers': 'dspmq',
            'get_queues': 'display queue(*) TYPE(QLOCAL) CURDEPTH MAXDEPTH',
            'get_queues_monitor': 'display qstatus(*) MONITOR'
        }
    task_is_mq_manager_status = False
    mq_object = str()
    mq_manager = str()
    for arg_name, arg_value in kwargs.items():
        if arg_name == 'task':
            if arg_value == 'get_mq_manager_status':
                task_is_mq_manager_status = True
            mq_command = command_mapping[arg_value]
        elif arg_name == 'mqm':
            mq_manager = arg_value
        elif arg_name != 'ssh_connect_string':
            # channel or listener
            mq_object = arg_value
    if mq_object and mq_manager:
        if ssh_connect_string:
            command = "echo \"echo {0}\" \| runmqsc {1} > cmd && ssh -q '{2}' 'bash -s' < cmd".format(mq_command.format(mq_object), mq_manager, ssh_connect_string)
        else:
            command = 'echo "{0}"| runmqsc {1}'.format(mq_command.format(mq_object), mq_manager)
    elif not mq_object and (mq_manager):
        if ssh_connect_string:
            command = "echo \"echo {0}\" \| runmqsc {1} > cmd && ssh -q '{2}' 'bash -s' < cmd".format(mq_command, mq_manager, ssh_connect_string)
        else:
            command = 'echo "{0}"| runmqsc {1}'.format(mq_command, mq_manager)
    elif not mq_manager:
        command = mq_command
        if ssh_connect_string:
            command = "echo {0} > cmd && ssh -q '{1}' 'bash -s' < cmd".format(command, ssh_connect_string)
    if task_is_mq_manager_status:
        command = mq_command.format(mq_manager)
        if ssh_connect_string:
            command = "echo {0} > cmd && ssh -q '{1}' 'bash -s' < cmd".format(command, ssh_connect_string)
    output = execute_command(command=command)
    return output


def execute_command(command):
    """Executes in shell."""
    proc = subprocess.Popen(command,
                            shell=True,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.STDOUT,
                            universal_newlines=True)
    result = proc.communicate()[0]
    return result


def check_not_empty_list(lis1):
    """Checks for empty list.
    Returns 1 when the list is not empty."""
    if not lis1:
        return 0
    else:
        return 1


def add_annotation(lis1, annotation):
    """When the list is not empty inserts annotation at the top of the list."""
    if check_not_empty_list(lis1):
        lis1.insert(0, annotation)
    return lis1
