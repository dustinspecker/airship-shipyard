# Copyright 2017 AT&T Intellectual Property. All other rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
from unittest import mock
from unittest.mock import patch

import responses
import pytest

from shipyard_client.api_client.base_client import BaseClient
from shipyard_client.cli import cli_format_common
from shipyard_client.cli.get.actions import GetActions
from shipyard_client.cli.get.actions import GetConfigdocs
from shipyard_client.cli.get.actions import GetConfigdocsStatus
from shipyard_client.cli.get.actions import GetRenderedConfigdocs
from shipyard_client.cli.get.actions import GetSiteStatuses
from shipyard_client.cli.get.actions import GetWorkflows
from tests.unit.cli import stubs

GET_ACTIONS_API_RESP = """
[
  {
    "dag_status": "failed",
    "parameters": {},
    "steps": [
      {
        "id": "action_xcom",
        "url": "/actions/01BTP9T2WCE1PAJR2DWYXG805V/steps/action_xcom",
        "index": 1,
        "state": "success"
      },
      {
        "id": "concurrency_check",
        "url": "/actions/01BTP9T2WCE1PAJR2DWYXG805V/steps/concurrency_check",
        "index": 2,
        "state": "success",
        "notes": [
            {
                "assoc_id": "step/01BTP9T2WCE1PAJR2DWYXG805V/concurrency_check",
                "subject": "concurrency_check",
                "sub_type": "step metadata",
                "note_val": "This is a note for the concurrency check",
                "verbosity": 1,
                "note_id": "ABCDEFGHIJKLMNOPQRSTUVWXYZ",
                "note_timestamp": "2018-10-08 14:23:53.346534",
                "resolved_url_value": null
            }
        ]
      },
      {
        "id": "preflight",
        "url": "/actions/01BTP9T2WCE1PAJR2DWYXG805V/steps/preflight",
        "index": 3,
        "state": "failed"
      }
    ],
    "action_lifecycle": "Failed",
    "dag_execution_date": "2017-09-23T02:42:12",
    "id": "01BTP9T2WCE1PAJR2DWYXG805V",
    "dag_id": "deploy_site",
    "datetime": "2017-09-23 02:42:06.860597+00:00",
    "user": "shipyard",
    "context_marker": "416dec4b-82f9-4339-8886-3a0c4982aec3",
    "name": "deploy_site",
    "notes": [
        {
            "assoc_id": "action/01BTP9T2WCE1PAJR2DWYXG805V",
            "subject": "01BTP9T2WCE1PAJR2DWYXG805V",
            "sub_type": "action metadata",
            "note_val": "This is a note for some action",
            "verbosity": 1,
            "note_id": "ABCDEFGHIJKLMNOPQRSTUVWXYA",
            "note_timestamp": "2018-10-08 14:23:53.346534",
            "resolved_url_value": "Your lucky numbers are 1, 3, 5, and Q"
        }
    ]
  }
]
"""


@responses.activate
@mock.patch.object(BaseClient, 'get_endpoint', lambda x: 'http://shiptest')
@mock.patch.object(BaseClient, 'get_token', lambda x: 'abc')
def test_get_actions(*args):
    responses.add(
        responses.GET,
        'http://shiptest/actions',
        body=GET_ACTIONS_API_RESP,
        status=200)
    response = GetActions(stubs.StubCliContext()).invoke_and_return_resp()
    assert 'deploy_site' in response
    assert 'action/01BTP9T2WCE1PAJR2DWYXG805V' in response
    assert 'Lifecycle' in response
    assert '2/1/0' in response
    assert 'This is a note for the concurrency check' not in response
    assert "Action Footnotes" in response
    assert ("  - Info available with 'describe notedetails/"
            "ABCDEFGHIJKLMNOPQRSTUVWXYA'") in response


GET_ACTIONS_API_RESP_UNPARSEABLE_NOTE = """
[
  {
    "dag_status": "failed",
    "parameters": {},
    "steps": [
      {
        "id": "action_xcom",
        "url": "/actions/01BTP9T2WCE1PAJR2DWYXG805V/steps/action_xcom",
        "index": 1,
        "state": "success"
      }
    ],
    "action_lifecycle": "Failed",
    "dag_execution_date": "2017-09-23T02:42:12",
    "id": "01BTP9T2WCE1PAJR2DWYXG805V",
    "dag_id": "deploy_site",
    "datetime": "2017-09-23 02:42:06.860597+00:00",
    "user": "shipyard",
    "context_marker": "416dec4b-82f9-4339-8886-3a0c4982aec3",
    "name": "deploy_site",
    "notes": [
        {
            "assoc_id": "action/01BTP9T2WCE1PAJR2DWYXG805V",
            "subject": "01BTP9T2WCE1PAJR2DWYXG805V",
            "sub_type": "action metadata",
            "note_val": "This is the first note for some action",
            "verbosity": 1,
            "note_id": "ABCDEFGHIJKLMNOPQRSTUVWXA1",
            "note_timestamp": "2018-10-08 14:23:53.346534",
            "resolved_url_value": "Your lucky numbers are 1, 3, 5, and Q"
        },
        {
            "note_val": "This note is broken"
        },
        {
            "assoc_id": "action/01BTP9T2WCE1PAJR2DWYXG805V",
            "subject": "01BTP9T2WCE1PAJR2DWYXG805V",
            "sub_type": "action metadata",
            "note_val": "The previous note is bad. It is missing fields",
            "verbosity": 1,
            "note_id": "ABCDEFGHIJKLMNOPQRSTUVWXA2",
            "note_timestamp": "2018-10-08 14:23:53.346534",
            "resolved_url_value": null
        }
    ]
  }
]
"""


@responses.activate
@mock.patch.object(BaseClient, 'get_endpoint', lambda x: 'http://shiptest')
@mock.patch.object(BaseClient, 'get_token', lambda x: 'abc')
def test_get_actions_unparseable_note(*args):
    responses.add(
        responses.GET,
        'http://shiptest/actions',
        body=GET_ACTIONS_API_RESP_UNPARSEABLE_NOTE,
        status=200)
    response = GetActions(stubs.StubCliContext()).invoke_and_return_resp()
    assert 'deploy_site' in response
    assert 'action/01BTP9T2WCE1PAJR2DWYXG805V' in response
    assert 'Lifecycle' in response
    assert 'This is the first note for some action' in response
    assert "{'note_val': 'This note is broken'}" in response
    assert 'The previous note is bad' in response


@responses.activate
@mock.patch.object(BaseClient, 'get_endpoint', lambda x: 'http://shiptest')
@mock.patch.object(BaseClient, 'get_token', lambda x: 'abc')
def test_get_actions_empty(*args):
    responses.add(
        responses.GET, 'http://shiptest/actions', body="[]", status=200)
    response = GetActions(stubs.StubCliContext()).invoke_and_return_resp()
    assert 'None' in response
    assert 'Lifecycle' in response


GET_CONFIGDOCS_API_RESP = """
---
yaml: yaml
---
yaml2: yaml2
...
"""


@responses.activate
@mock.patch.object(BaseClient, 'get_endpoint', lambda x: 'http://shiptest')
@mock.patch.object(BaseClient, 'get_token', lambda x: 'abc')
def test_get_configdocs(*args):
    responses.add(
        responses.GET,
        'http://shiptest/configdocs/design?version=buffer',
        body=GET_CONFIGDOCS_API_RESP,
        status=200)
    response = GetConfigdocs(
        stubs.StubCliContext(), collection='design',
        version='buffer').invoke_and_return_resp()
    assert response == GET_CONFIGDOCS_API_RESP


@responses.activate
@mock.patch.object(BaseClient, 'get_endpoint', lambda x: 'http://shiptest')
@mock.patch.object(BaseClient, 'get_token', lambda x: 'abc')
def test_get_configdocs_not_found(*args):
    api_resp = stubs.gen_err_resp(
        message='Not Found',
        sub_error_count=0,
        sub_info_count=0,
        reason='It does not exist',
        code=404)

    responses.add(
        responses.GET,
        'http://shiptest/configdocs/design?version=buffer',
        body=api_resp,
        status=404)
    response = GetConfigdocs(
        stubs.StubCliContext(), collection='design',
        version='buffer').invoke_and_return_resp()
    assert 'Error: Not Found' in response
    assert 'Reason: It does not exist' in response


@responses.activate
@mock.patch.object(BaseClient, 'get_endpoint', lambda x: 'http://shiptest')
@mock.patch.object(BaseClient, 'get_token', lambda x: 'abc')
@pytest.mark.parametrize("test_input, expected", [("""
[
     {
        "collection_name": "Collection_1",
        "base_status": "present",
        "new_status": "unmodified",
        "base_version": "committed",
        "base_revision": 3,
        "new_version": "buffer",
        "new_revision": 5
     },
     {
        "collection_name": "Collection_2",
        "base_status": "present",
        "new_status": "modified",
        "base_version": "committed",
        "base_revision": 3,
        "new_version": "buffer",
        "new_revision": 5
     },
     {
        "collection_name": "Collection_3",
        "base_status": "not present",
        "new_status": "created",
        "base_version": "committed",
        "base_revision": 3,
        "new_version": "buffer",
        "new_revision": 5
     },
     {
        "collection_name": "Collection_A",
        "base_status": "present",
        "new_status": "deleted",
        "base_version": "committed",
        "base_revision": 3,
        "new_version": "buffer",
        "new_revision": 5
     }
]
""", [{
    "collection_name": "Collection_1",
    "base_status": "present",
    "new_status": "unmodified",
    "base_version": "committed",
    "base_revision": 3,
    "new_version": "buffer",
    "new_revision": 5
}, {
    "collection_name": "Collection_2",
    "base_status": "present",
    "new_status": "modified",
    "base_version": "committed",
    "base_revision": 3,
    "new_version": "buffer",
    "new_revision": 5
}, {
    "collection_name": "Collection_3",
    "base_status": "not present",
    "new_status": "created",
    "base_version": "committed",
    "base_revision": 3,
    "new_version": "buffer",
    "new_revision": 5
}, {
    "collection_name": "Collection_A",
    "base_status": "present",
    "new_status": "deleted",
    "base_version": "committed",
    "base_revision": 3,
    "new_version": "buffer",
    "new_revision": 5
}])])
def test_get_configdocs_status(test_input, expected, *args):
    responses.add(
        responses.GET,
        'http://shiptest/configdocs',
        body=test_input,
        status=200)

    with patch.object(cli_format_common,
                      'gen_collection_table') as mock_method:
        response = GetConfigdocsStatus(
            stubs.StubCliContext()).invoke_and_return_resp()
    mock_method.assert_called_once_with(expected)


GET_RENDEREDCONFIGDOCS_API_RESP = """
---
yaml: yaml
---
yaml2: yaml2
...
"""


@responses.activate
@mock.patch.object(BaseClient, 'get_endpoint', lambda x: 'http://shiptest')
@mock.patch.object(BaseClient, 'get_token', lambda x: 'abc')
def test_get_renderedconfigdocs(*args):
    responses.add(
        responses.GET,
        'http://shiptest/renderedconfigdocs?version=buffer',
        body=GET_RENDEREDCONFIGDOCS_API_RESP,
        status=200)
    response = GetRenderedConfigdocs(
        stubs.StubCliContext(), version='buffer').invoke_and_return_resp()
    assert response == GET_RENDEREDCONFIGDOCS_API_RESP


@responses.activate
@mock.patch.object(BaseClient, 'get_endpoint', lambda x: 'http://shiptest')
@mock.patch.object(BaseClient, 'get_token', lambda x: 'abc')
def test_get_renderedconfigdocs_not_found(*args):
    api_resp = stubs.gen_err_resp(
        message='Not Found',
        sub_error_count=0,
        sub_info_count=0,
        reason='It does not exist',
        code=404)

    responses.add(
        responses.GET,
        'http://shiptest/renderedconfigdocs?version=buffer',
        body=api_resp,
        status=404)
    response = GetRenderedConfigdocs(
        stubs.StubCliContext(), version='buffer').invoke_and_return_resp()
    assert 'Error: Not Found' in response
    assert 'Reason: It does not exist' in response


GET_WORKFLOWS_API_RESP = """
[
  {
    "execution_date": "2017-10-09 21:18:56",
    "end_date": null,
    "workflow_id": "deploy_site__2017-10-09T21:18:56.000000",
    "start_date": "2017-10-09 21:18:56.685999",
    "external_trigger": true,
    "dag_id": "deploy_site",
    "state": "failed",
    "run_id": "manual__2017-10-09T21:18:56"
  },
  {
    "execution_date": "2017-10-09 21:19:03",
    "end_date": null,
    "workflow_id": "deploy_site__2017-10-09T21:19:03.000000",
    "start_date": "2017-10-09 21:19:03.361522",
    "external_trigger": true,
    "dag_id": "deploy_site",
    "state": "failed",
    "run_id": "manual__2017-10-09T21:19:03"
  }
]
"""


@responses.activate
@mock.patch.object(BaseClient, 'get_endpoint', lambda x: 'http://shiptest')
@mock.patch.object(BaseClient, 'get_token', lambda x: 'abc')
def test_get_workflows(*args):
    responses.add(
        responses.GET,
        'http://shiptest/workflows',
        body=GET_WORKFLOWS_API_RESP,
        status=200)
    response = GetWorkflows(stubs.StubCliContext()).invoke_and_return_resp()
    assert 'deploy_site__2017-10-09T21:19:03.000000' in response
    assert 'deploy_site__2017-10-09T21:18:56.000000' in response
    assert 'State' in response
    assert 'Workflow' in response


@responses.activate
@mock.patch.object(BaseClient, 'get_endpoint', lambda x: 'http://shiptest')
@mock.patch.object(BaseClient, 'get_token', lambda x: 'abc')
def test_get_workflows_empty(*args):
    responses.add(
        responses.GET, 'http://shiptest/workflows', body="[]", status=200)
    response = GetWorkflows(stubs.StubCliContext()).invoke_and_return_resp()
    assert 'None' in response
    assert 'State' in response


GET_SITE_STATUSES_API_RESP = """
{
  "nodes_provision_status": [
      {
        "hostname": "xyz.abc.com",
        "status": "deployed"},
      {
        "hostname": "def.abc.com",
        "status": "provisioning"}
    ],
  "machines_powerstate": [
      {
        "hostname": "xyz.abc.com",
        "power_state": "on"},
      {
        "hostname": "def.abc.com",
        "power_state": "off"}
    ]}
"""


@responses.activate
@mock.patch.object(BaseClient, 'get_endpoint', lambda x: 'http://shiptest')
@mock.patch.object(BaseClient, 'get_token', lambda x: 'abc')
def test_get_site_statuses(*args):
    responses.add(
        responses.GET,
        'http://shiptest/site_statuses',
        body=GET_SITE_STATUSES_API_RESP,
        status=200)
    response = GetSiteStatuses(stubs.StubCliContext()).invoke_and_return_resp()
    assert 'xyz.abc.com' in response
    assert 'def.abc.com' in response
    assert 'deployed' in response
    assert 'on' in response
    assert 'off' in response
    assert 'provisioning' in response
    assert 'Nodes Provision Status:' in response
    assert 'Machines Power State:' in response


@responses.activate
@mock.patch.object(BaseClient, 'get_endpoint', lambda x: 'http://shiptest')
@mock.patch.object(BaseClient, 'get_token', lambda x: 'abc')
def test_get_site_statuses_with_filters(*args):
    responses.add(
        responses.GET,
        'http://shiptest/site_statuses',
        body=GET_SITE_STATUSES_API_RESP,
        status=200)
    response = GetSiteStatuses(stubs.StubCliContext(),
                               fltr="nodes-provision-status,"
                               "machines-power-state").invoke_and_return_resp()
    assert 'xyz.abc.com' in response
    assert 'def.abc.com' in response
    assert 'deployed' in response
    assert 'on' in response
    assert 'off' in response
    assert 'provisioning' in response
    assert 'Nodes Provision Status:' in response
    assert 'Machines Power State:' in response
