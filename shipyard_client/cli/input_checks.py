# Copyright 2017 AT&T Intellectual Property.  All other rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-1.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
import arrow
from arrow.parser import ParserError


def check_action_command(ctx, action_command):
    """Verifies the action command is valid"""
    if action_command not in ['deploy_site', 'update_site', 'redeploy_server']:
        ctx.fail('Invalid action command.  The action commands available are '
                 'deploy_site, update_site, and redeploy_server.')


def check_control_action(ctx, action):
    """Verifies the control action is valid"""
    if action not in ['pause', 'unpause', 'stop']:
        ctx.fail('Invalid action.  Please enter pause, unpause, or stop.')


def check_id(ctx, action_id):
    """Verifies a ULID id is in a valid format"""
    if action_id is None:
        ctx.fail('Invalid ID. None is not a valid action ID.')
    if len(action_id) != 26:
        ctx.fail('Invalid ID. ID can only be 26 characters.')
    if not action_id.isalnum():
        ctx.fail('Invalid ID. ID can only contain letters and numbers.')


def check_workflow_id(ctx, workflow_id):
    """Verifies that a workflow id matches the desired format"""
    if workflow_id is None:
        ctx.fail('Invalid ID. None is not a valid workflow ID.')
    if '__' not in workflow_id:
        ctx.fail('Invalid ID. The ID must cotain a double underscore '
                 'separating the workflow name from the execution date')
    input_date_string = workflow_id.split('__')[1]
    date_format_ok = True
    try:
        parsed_dt = arrow.get(input_date_string)
        if input_date_string != parsed_dt.format('YYYY-MM-DDTHH:mm:ss.SSSSSS'):
            date_format_ok = False
    except ParserError:
        date_format_ok = False

    if not date_format_ok:
        ctx.fail('Invalid ID. The date portion of the ID must conform to '
                 'YYYY-MM-DDTHH:mm:ss.SSSSSS')


def validate_auth_vars(ctx, auth_vars):
    """Checks that the required authurization varible have been entered"""

    required_auth_vars = ['auth_url']
    err_txt = ""
    for var in required_auth_vars:
        if auth_vars[var] is None:
            err_txt += (
                'Missing the required authorization variable: '
                '--os_{}\n'.format(var))
    if err_txt != "":
        err_txt += ('\nMissing the following additional authorization '
                    'options: ')
        for var in auth_vars:
            if auth_vars[var] is None and var not in required_auth_vars:
                err_txt += '\n--os_{}'.format(var)
        ctx.fail(err_txt)


def check_reformat_parameter(ctx, param):
    """Checks for <name>=<value> format"""
    param_dictionary = {}
    try:
        for p in param:
            values = p.split('=')
            param_dictionary[values[0]] = values[1]
    except Exception:
        ctx.fail(
            "Invalid parameter or parameter format for " + p +
            ".  Please utilize the format: <parameter name>=<parameter value>")
    return param_dictionary