import sys
import requests
from collections import defaultdict
from time import sleep

class Lemmy:
    
    _api_version = "v3"
    _api_base_url = f"api/{_api_version}"
    
    def __init__(self, url) -> None:
        self._site_url = url
        self._auth_token = None
        self._user_communities = defaultdict(dict)
        self._requests_total = 0
    
    def login(self, user, password):
        '''authenticate to instance'''
        payload = { 
                'username_or_email': user,
                'password': password
        }
        
        try:
            resp = requests.post(f"{self._site_url}/{self._api_base_url}/user/login",
                             json=payload)
            resp.raise_for_status()
            self._auth_token = resp.json()['jwt']
        except requests.exceptions.HTTPError as ex:
            print(f"   HTTP error: {ex.response}, while authenticating")
            raise Exception(f"HTTP error: {ex.response} while authenticating")
        except requests.exceptions.RequestException as ex:
            raise Exception(f"Error: {ex} while authenticating")

    def get_communities(self):
        '''Get list of currently subscribed communites'''
        try:
            payload = { 
                    'type_': 'Subscribed',
                    'auth': self._auth_token,
                    'limit': 50,
                    'page': 1
            }
            
            # iterate over each page if needed
            fetched = 50 #max limit
            while fetched == 50:
                self._requests_total += 1
                resp = requests.get(f"{self._site_url}/{self._api_base_url}/community/list",
                                    params=payload)
                fetched = len(resp.json()['communities'])
                #print(f"length: {fetched}")
                payload['page'] += 1

                for comm in resp.json()['communities']:
                    id = comm['community']['id']
                    url = comm['community']['actor_id']
                    self._user_communities[id]['name'] = url
        except Exception as err:
            print(f"error: {err}")
        
        return self._user_communities

    def subscribe(self, communities=None):
        '''Subscribe to a community. It will first attempt to fetch community.'''
        if communities:
            self._user_communities = communities
        else:
            self.get_communities()

        payload = {
                'community_id': None,
                'follow': True,
                'auth': self._auth_token
        }

        for cid,url in self._user_communities.items():
            try: 
                # resolve community first
                print(f"Fetching {url['name']}")
                comm_id = self.fetch_community(url['name'])
                
                if comm_id:
                    payload['community_id'] = comm_id
                    print(f"   Subscribing to {url['name']} ({comm_id})")
                    self._requests_total += 1
                    print(f"   Total request: {self._requests_total}")
                    self.rate_limit()
                    resp = requests.post(f"{self._site_url}/{self._api_base_url}/community/follow",
                                        json=payload)
                    resp.raise_for_status()
            except requests.exceptions.HTTPError as ex:
                print(f"   HTTP error: {ex.response}, while adding {cid}")
            except requests.exceptions.RequestException as ex:
                print(f"   Error: {ex}")

    def fetch_community(self, community):
        '''Fetch a communityt'''
        payload = {
                'q': community,
                'auth':self._auth_token
        }

        community_id = None
        try:
            self._requests_total += 1
            self.rate_limit()
            resp = requests.get(f"{self._site_url}/{self._api_base_url}/resolve_object",
                                params=payload)
            resp.raise_for_status()
            community_id = resp.json()['community']['community']['id']
        except requests.exceptions.HTTPError as ex:
            print(f"   HTTP error: {ex.response}, while fetching {community}")
        except requests.exceptions.RequestException as ex:
            print(f"   Error: {ex}")

        return community_id
    
    def rate_limit(self):
        #if self._requests_total >= 15:
        #    print("   Rate limited, sleep for 10s...")
        sleep(1)
        #    self._requests_total = 1
        
        return