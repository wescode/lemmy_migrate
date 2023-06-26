import sys
import requests
from collections import defaultdict
from time import sleep
from urllib.parse import urlparse


class Lemmy:
    
    _api_version = "v3"
    _api_base_url = f"api/{_api_version}"
    
    def __init__(self, url) -> None:
        parsed_url = urlparse(url)
        url_path = parsed_url.netloc if parsed_url.netloc else parsed_url.path
        self._site_url = urlparse(url_path)._replace(scheme='https',
                                                     netloc=url_path,
                                                     path='').geturl()
        self._auth_token = None
        self._user_communities = defaultdict(dict)
    
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
          #raise Exception(f"Failed to authenticate: {e}")
          self._println(1, f"[ERROR]: login() failed for {user} on {self._site_url}")
          self._println(2, f"-Details: {e}")
          sys.exit(1)
            
    def get_communities(self, type: str = "Subscribed") -> dict:
        """Get list of currently subscribed communites"""
        payload = { 
            'type_': type,
            'auth': self._auth_token,
            'limit': 50,
            'page': 1
        }
            
        # iterate over each page if needed
        fetched = 50 #max limit
        while fetched == 50:
            try:
                resp = self._request_it(
                    f"{self._site_url}/{self._api_base_url}/community/list",
                    params=payload)
                fetched = len(resp.json()['communities'])
                payload['page'] += 1

                for comm in resp.json()['communities']:
                    id = comm['community']['id']
                    url = comm['community']['actor_id']
                    self._user_communities[url]['id'] = id
            except Exception as err:
                print(f"error: {err}")
        
        return self._user_communities

    def subscribe(self, communities: dict = None) -> None:
        """Subscribe to a community. It will first attempt to resolve community."""
        if communities:
            self._user_communities = communities
        else:
            self.get_communities()

        payload = {
            'community_id': None,
            'follow': True,
            'auth': self._auth_token
        }

        for url,cid in self._user_communities.items():
            try: 
                # resolve community first
                comm_id = self.resolve_community(url)
                
                if comm_id:
                    payload['community_id'] = comm_id
                    self._println(2, f"> Subscribing to {url} ({comm_id})")
                    resp = self._request_it(
                        f"{self._site_url}/{self._api_base_url}/community/follow",
                        json=payload, method='POST')
                    
                    if resp.status_code == 200:
                        self._println(3, f"> Succesfully subscribed to {url} ({comm_id})")
            except Exception as e:
                print(f"   API error: {e}")

    def resolve_community(self, community: str) -> int | None:
        """resolve a community"""
        payload = {
            'q': community,
            'auth':self._auth_token
        }

        community_id = None
        self._println(1, f"> Resolving {community}")
        try:
            resp = self._request_it(
                f"{self._site_url}/{self._api_base_url}/resolve_object",
                params=payload)
            community_id = resp.json()['community']['community']['id']
        except Exception as e:
            self._println(2, f"> Failed to resolve community {e}")

        return community_id
    
    def get_comments(
            self, post_id: str, max_depth: int = 1,
            limit: int = 1000) -> dict:

        payload = {
            'post_id': post_id,
            'max_depth': max_depth,
            'limit': limit,
        }

        try:
            r = self._request_it(
                f"{self._site_url}/{self._api_base_url}/comment/list",
                params=payload)
        except Exception as e:
            self._println(2, f"> Failed to get comment list")

        return r.json()['comments']

    def _rate_limit(self):
        sleep(1)
    
    def _request_it(
            self, endpoint: str, method: str = 'GET', params: str = None,
            json: dict = None) -> requests.Response:
            
        self._rate_limit()
        try:
            r = requests.request(method, url=endpoint, params=params, json=json)
            r.raise_for_status()
            return r
        except requests.exceptions.HTTPError as e:
            raise
        except requests.exceptions.RequestException as e:
            raise

    def _println(self, indent, line):
        print(f"{' ' * indent}{line}")