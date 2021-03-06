# Copyright 2013 Mirantis Inc.
# All Rights Reserved
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.
#
# @author: Ilya Shakhat, Mirantis Inc.
#

import logging

from neutronclient.neutron import v2_0 as neutronV20
from neutronclient.openstack.common.gettextutils import _


def _format_provider(pool):
    return pool.get('provider') or 'N/A'


class ListPool(neutronV20.ListCommand):
    """List pools that belong to a given tenant."""

    resource = 'pool'
    log = logging.getLogger(__name__ + '.ListPool')
    list_columns = ['id', 'name', 'provider', 'lb_method', 'protocol', 'timeout_connect', 'timeout_client', 'timeout_server', 'max_conn',
                    'admin_state_up', 'status']
    _formatters = {'provider': _format_provider}
    pagination_support = True
    sorting_support = True


class ShowPool(neutronV20.ShowCommand):
    """Show information of a given pool."""

    resource = 'pool'
    log = logging.getLogger(__name__ + '.ShowPool')


class CreatePool(neutronV20.CreateCommand):
    """Create a pool."""

    resource = 'pool'
    log = logging.getLogger(__name__ + '.CreatePool')

    def add_known_arguments(self, parser):
        parser.add_argument(
            '--admin-state-down',
            dest='admin_state', action='store_false',
            help=_('Set admin state up to false'))
        parser.add_argument(
            '--description',
            help=_('Description of the pool'))
        parser.add_argument(
            '--lb-method',
            required=True,
            choices=['ROUND_ROBIN', 'LEAST_CONNECTIONS', 'SOURCE_IP', 'URI_HASH'],
            help=_('The algorithm used to distribute load between the members '
                   'of the pool'))
        parser.add_argument(
            '--name',
            required=True,
            help=_('The name of the pool'))
        parser.add_argument(
            '--protocol',
            required=True,
            choices=['HTTP', 'HTTPS', 'TCP'],
            help=_('Protocol for balancing'))
        parser.add_argument(
            '--timeout_connect',
            help=_('maximum time(milliseconds) to wait for a connection attempt to a server to succeed (default:50000)'))
        parser.add_argument(
            '--timeout_client',
            help=_('maximum time(milliseconds) inactivity on the client side.(default:50000)'))
        parser.add_argument(
            '--timeout_server',
            help=_('maximum time(milliseconds) inactivity on the server side.(default:5000)'))
        parser.add_argument(
            '--max_conn',
            help=_('the maximum number of concurrent connections the frontend will accept to serve.'))
        parser.add_argument(
            '--subnet-id', metavar='SUBNET',
            required=True,
            help=_('The subnet on which the members of the pool will be '
                   'located'))
        parser.add_argument(
            '--provider',
            help=_('Provider name of loadbalancer service'))

    def args2body(self, parsed_args):
        _subnet_id = neutronV20.find_resourceid_by_name_or_id(
            self.get_client(), 'subnet', parsed_args.subnet_id)
        body = {
            self.resource: {
                'admin_state_up': parsed_args.admin_state,
                'subnet_id': _subnet_id,
            },
        }
        neutronV20.update_dict(parsed_args, body[self.resource],
                               ['description', 'lb_method', 'name',
                                'protocol',  'timeout_connect', 'timeout_client', 'timeout_server', 'max_conn', 'tenant_id', 'provider'])
        return body


class UpdatePool(neutronV20.UpdateCommand):
    """Update a given pool."""

    resource = 'pool'
    log = logging.getLogger(__name__ + '.UpdatePool')


class DeletePool(neutronV20.DeleteCommand):
    """Delete a given pool."""

    resource = 'pool'
    log = logging.getLogger(__name__ + '.DeletePool')


class RetrievePoolStats(neutronV20.ShowCommand):
    """Retrieve stats for a given pool."""

    resource = 'pool'
    log = logging.getLogger(__name__ + '.RetrievePoolStats')

    def get_data(self, parsed_args):
        self.log.debug('run(%s)' % parsed_args)
        neutron_client = self.get_client()
        neutron_client.format = parsed_args.request_format
        pool_id = neutronV20.find_resourceid_by_name_or_id(
            self.get_client(), 'pool', parsed_args.id)
        params = {}
        if parsed_args.fields:
            params = {'fields': parsed_args.fields}

        data = neutron_client.retrieve_pool_stats(pool_id, **params)
        self.format_output_data(data)
        stats = data['stats']
        if 'stats' in data:
            return zip(*sorted(stats.iteritems()))
        else:
            return None
