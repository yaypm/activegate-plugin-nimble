import json
import requests
from ruxit.api.base_plugin import RemoteBasePlugin
import logging
import random

logger = logging.getLogger(__name__)

class NimblePluginRemote(RemoteBasePlugin):
    def initialize(self, **kwargs):
        config = kwargs['config']
        logger.info("Config: %s", config)
        self.url = config["url"]
        self.username = config["username"]
        self.password = config["password"]

    def query(self, **kwargs):

        ## POST to get the auth token
        token_url = self.url + "/v1/tokens"
        jsonHeaders = {'Content-type': 'application/json'}

        data = {'data':{'username':self.username, 'password': self.password}}
        json_data = json.dumps(data)

        authList = json.loads(requests.post(token_url, data = json_data, headers=jsonHeaders, verify=False).content.decode())

        token = authList['data']['session_token']
        tokenHeaders = {'X-Auth-Token': token}

        ## GET list of volumes
        volume_list_url = self.url + "/v1/volumes"
        volumeList = json.loads(requests.get(volume_list_url, headers=tokenHeaders, verify=False).content.decode())
        
        ## Choose the first volume and get ID and name
        vol_id = volumeList['data'][0]['id']
        vol_name = volumeList['data'][0]['name']
        
        ## Build the URL for volume details
        volume_detail_url = self.url + "/v1/volumes/" + vol_id
        
        ## GET the volume details
        volumeDetails = json.loads(requests.get(volume_detail_url, headers=tokenHeaders, verify=False).content.decode())

        group = self.topology_builder.create_group("nimble", "Nimble")
        node = group.create_element(vol_id, vol_name)

        node.absolute(key='warn_level', value=volumeDetails['data']['warn_level'])

        if volumeDetails['data']['online'] is True:

            node.absolute(key='online', value=100)
        
        else:

            node.absolute(key='online', value=0)
