import abc
import requests
import six

from oslo_config import cfg
from oslo_log import log as logging


LOG = logging.getLogger(__name__)

OPTS = [
    cfg.StrOpt('cAdvisor_port',
               default='8080',
               help='Default port of cAdvisor.'), 
    cfg.StrOpt('cAdvisor_version',
               default='v1.3',
               help='Default version of cAdvisor.')
]

CONF = cfg.CONF
CONF.register_opts(OPTS)


class CadvisorAPIFailedException(Exception):
    pass


@six.add_metaclass(abc.ABCMeta)
class _BaseClient(object):
    
    @abc.abstractproperty
    def base_url(self):
        """Returns base url for each REST API."""

    def __init__(self, client):
        self.client = client

    def request(self, container_id=None):
        path = self.base_url
        if container_id is not None:
            path = path % {'container_id': container_id}
        return self.client.request(path)


class MachineAPIClient(_BaseClient):
    
    base_url = '/machine'
    
    def get_machine_info(self):
        return self.request()
    

class ContainerSpecAPIClient(_BaseClient):
    
    base_url = '/spec/%(container_id)s'
    
    def get_container_spec(self, container_id):
        return self.request(container_id)


class ContainerStatsAPIClient(_BaseClient):
    
    base_url = '/stats/%(container_id)s'
    
    def get_container_stats(self, container_id):
        return self.request(container_id)
    
    def get_all_stats(self):
        return self.request()


class CadvisorClient(object):
    def __init__(self, endpoint_url, port=cfg.CONF.cAdvisor_port,
                 version=cfg.CONF.cAdvisor_version):
        self._endpoint = '%(endpoint_url)s:%(port)s/%(version)s' % {
            'endpoint_url': endpoint_url, 'port': port, 'version': version}
        
        self.machine = MachineAPIClient(self)
        self.container_spec = ContainerSpecAPIClient(self)
        self.container_stats = ContainerStatsAPIClient(self)
    
    def _http_request(self, url):
        resp = requests.get(url)
        if resp.status_code // 100 != 2:
            raise CadvisorAPIFailedException('%(reason)s') % {
                'reason': resp.reason}
        return resp.json()
    
    def request(self, path):
        url = self._endpoint + path
        return self._http_request(url)


if __name__ == '__main__':
    pass