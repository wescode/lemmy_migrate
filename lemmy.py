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
    
    def login(self, user: str, password: str) -> None:
        """authenticate to instance"""
        payload = { 
            'username_or_email': user,
            'password': password
        }
        
        try:
            resp = self._request_it(
                f"{self._site_url}/{self._api_base_url}/user/login",
                method='POST', json=payload)
            self._auth_token = resp.json()['jwt']
        except Exception as e:
            raise Exception(f"Failed to authenticate: {e}")
            
    def get_communities(self) -> dict:
        """Get list of currently subscribed communites"""
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
            try:
                resp = self._request_it(
                    f"{self._site_url}/{self._api_base_url}/community/list",
                    params=payload)
                fetched = len(resp.json()['communities'])
                payload['page'] += 1

                for comm in resp.json()['communities']:
                    id = comm['community']['id']
                    url = comm['community']['actor_id']
                    self._user_communities[id]['name'] = url
            except Exception as err:
                print(f"error: {err}")
        
        return self._user_communities

    def subscribe(self, communities: dict = None) -> None:
        """Subscribe to a community. It will first attempt to fetch community."""
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
                    #print(f"   Total request: {self._requests_total}")
                    self._rate_limit()
                    resp = self._request_it(
                        f"{self._site_url}/{self._api_base_url}/community/follow",
                        json=payload, method='POST')
                    
                    if resp.status_code == 200:
                        print(f"   Succesfully subscribed to {url['name']} ({comm_id})")
            except Exception as e:
                print(f"   API error: {e}")

    def fetch_community(self, community: str) -> int | None:
        """Fetch a community"""
        payload = {
            'q': community,
            'auth':self._auth_token
        }

        community_id = None
        try:
            self._requests_total += 1
            self._rate_limit()
            resp = self._request_it(
                f"{self._site_url}/{self._api_base_url}/resolve_object",
                params=payload)
            community_id = resp.json()['community']['community']['id']
        except Exception as e:
            print(f"   Failed to fetch community {e}")

        return community_id
    
    def _rate_limit(self):
        #if self._requests_total >= 15:
        #    print("   Rate limited, sleep for 10s...")
        sleep(1)
        #    self._requests_total = 1
    
    def _request_it(
            self, endpoint: str, method: str = 'GET', params: str = None,
            json: dict = None) -> requests.Response:
        try:
            r = requests.request(method, url=endpoint, params=params, json=json)
            r.raise_for_status()
            return r
        except requests.exceptions.HTTPError as e:
            #raise Exception(f"Error at endpoint {endpoint}: {ex}")
            raise Exception("Error") from e
        except requests.exceptions.RequestException as e:
            raise Exception(e)
            #raise Exception(f"Error at endpoint {endpoint}: {ex}")