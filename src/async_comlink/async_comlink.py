import aiohttp
import asyncio
from urllib.parse import urlparse
from items import Items
from helpers import get_logger, get_hmac

class Comlink:
    """
    Async wrapper for Comlink API
    """
    def __init__(self, 
                 url: str = "http://localhost:3000",
                 host: str | None = None,
                 port: int = 3000,
                 secret_key: str | None = None,
                 access_key: str | None = None,
                 debug: bool = False):
        """
        Initialize

        Args:
            url (str): The URL of the Comlink API. Defaults to "http://localhost:3000"
            host (str, optional): The host of the Comlink API
            port (int, optional): The port of the Comlink API. Defaults to 3000
            debug (bool, optional): If debug mode should be enabled and stop exceptions from being raised on error. Defaults to False
        """

        if host:
            # Set the URL based on the host and port
            protocol = "https" if port == 443 else "http"
            port = port or (443 if protocol == "https" else 80)
            self.url = f"{protocol}://{host}:{port}"
        else:
            # Set the URL based on the provided URL
            parsed_url = urlparse(url.rstrip("/"))
            if not parsed_url.scheme:
                raise ValueError("URL must include a scheme (http or https)")
            
            self.url = url.rstrip("/")
            if not parsed_url.port:
                default_port = 443 if parsed_url.scheme == "https" else 80
                self.url = f"{parsed_url.scheme}://{parsed_url.hostname}:{default_port}"

        if secret_key and access_key:
            self.hmac = True
            self.secret_key = secret_key
            self.access_key = access_key
        else:
            self.hmac = False
        
        self.debug = debug
        if self.debug:
            self.logger = get_logger()

        self.session = None
        self.open()

    def open(self):
        """
        Open the session
        """
        if not self.session:
            self.session = aiohttp.ClientSession(base_url=self.url)

    async def _post(self,
                    endpoint: str,
                    payload: dict = None) -> dict:
        """
        Send a POST request to the Comlink URL

        Args:
            endpoint (str): The endpoint to send the request to
            payload (dict, optional): The payload to send. Defaults to None.

        Raises:
            e: Exception from aiohttp

        Returns:
            dict: The response
        """
        headers = {}
        if self.hmac:
            headers = get_hmac(endpoint, self.secret_key, self.access_key, payload)
        
        for _ in range(3):
            try:
                if self.debug:
                    self.logger.debug(f"POST {endpoint} {payload}")

                async with self.session.post(endpoint, json=payload, headers=headers) as response:
                    if self.debug:
                        self.logger.debug(f"{endpoint} {response.status}")
                    response = await response.json()
                return response
            
            except aiohttp.ClientError as e:
                if self.debug:
                    self.logger.debug(f"{e} - Retrying...")
                continue

            except Exception as e:
                await self._raise_exception(e)
        
        e = Exception(f"Failed to get response at {endpoint}")
        await self._raise_exception(e)
    
    async def get_game_data(self,
                            version: str = None,
                            include_pve_units: bool = False,
                            request_segment: int = 0,
                            items: str | list[str] = None,
                            enums: bool = False):
        """
        Get game data

        Args:
            version (str, optional): The version of the game data to get. Automatically gets the latest version if not provided.
            include_pve_units (bool, optional): If the response should include PVE units. Defaults to False.
            request_segment (int, optional): The segment of the game data to get (see Comlink documentation). Defaults to 0.
            items (str | list[str], optional): The items to include in the response (see Items class). Defaults to None.
            enums (bool, optional): If the response should use enum values instead of assigned integers. Defaults to False.

        Returns: dict
        """
        endpoint = "/data"
        if not version:
            version = await self.get_latest_game_version()
            version = version['game']
        
        payload = {
            "payload": {
                "version": f"{version}",
                "includePveUnits": include_pve_units
            },
            "enums": enums
        }

        if items and (isinstance(items, str) or isinstance(items, list)):
            value = Items.get_value(items)
            payload["payload"]["items"] = str(value)
        else:
            payload["payload"]["requestSegment"] = request_segment

        response = await self._post(endpoint=endpoint, payload=payload)
        return response

    async def get_player(self,
                         allycode: str | int = None,
                         playerId: str = None,
                         enums: bool = False):
        """
        Get a player's profile including roster

        Args:
            allycode (str | int, optional): The allycode of the player. Defaults to None.
            playerId (str, optional): The player ID of the player. Defaults to None.
            enums (bool, optional): If the response should use enum values instead of assigned integers. Defaults to False.

        Returns: dict
        """
        endpoint = "/player"
        payload = {
            "payload": {},
            "enums": enums
        }
        if playerId:
            payload["payload"]["playerId"] = str(playerId)
        elif allycode:
            payload["payload"]["allyCode"] = str(allycode)
        else:
            e = ValueError("allycode or playerId must be provided")
            await self._raise_exception(e)
        
        response = await self._post(endpoint=endpoint, payload=payload)
        return response
    
    async def get_player_arena(self,
                         allycode: str | int = None,
                         playerId: str = None,
                         player_details_only: bool = False,
                         enums: bool = False):
        """
        Get a player's arena profile

        Args:
            allycode (str | int, optional): The allycode of the player. Defaults to None.
            playerId (str, optional): The player ID of the player. Defaults to None.
            player_details_only (bool, optional): Get only arena details excluding arena squads. Defaults to False.
            enums (bool, optional): If the response should use enum values instead of assigned integers. Defaults to False.

        Returns: dict
        """
        endpoint = "/playerArena"
        payload = {
            "payload": {},
            "enums": enums
        }
        if playerId:
            payload["payload"]["playerId"] = str(playerId)
        elif allycode:
            payload["payload"]["allyCode"] = str(allycode)
        else:
            e = ValueError("allycode or playerId must be provided")
            await self._raise_exception(e)
        payload["payload"]["playerDetailsOnly"] = player_details_only

        response = await self._post(endpoint=endpoint, payload=payload)
        return response

    async def get_metadata(self,
                           enums: bool = False,
                           clientSpecs: dict = None):
        """
        Get metadata for the game

        Args:
            enums (bool, optional): If the response should use enum values instead of assigned integers. Defaults to False.
            clientSpecs (dict, optional): The client specs to return metadata for (see Comlink documentation). Defaults to None.

        Returns: dict
        """
        endpoint = "/metadata"
        payload = {
            "enums": enums
        }
        if clientSpecs and isinstance(clientSpecs, dict):
            payload["payload"] = {"clientSpecs": clientSpecs}
        elif clientSpecs and not isinstance(clientSpecs, dict):
            e = ValueError("clientSpecs must be a dictionary")
            await self._raise_exception(e)
        
        response = await self._post(endpoint=endpoint, payload=payload)
        return response
    
    async def get_latest_game_version(self):
        """
        Get the latest versions of the game and localization bundles

        Returns: dict
            key: game
            key: localization
        """
        metadata = await self.get_metadata()
        version = {
            "game": metadata['latestGamedataVersion'],
            "localization": metadata['latestLocalizationBundleVersion']
        }
        return version
    
    async def get_localization(self, 
                               id: str = None, 
                               unzip: bool = False, 
                               locale: str = None,
                               enums: bool = False):
        """
        Get localization values for the game

        Args:
            id (str, optional): The localization version to get. Automatically gets the latest version if not provided.
            unzip (bool, optional): Unzip the response from base64. Defaults to False.
            locale (str, optional): Get only values for the specified locale (e.g. ENG_US). Defaults to None.
            enums (bool, optional): If the response should use enum values instead of assigned integers. Defaults to False.

        Returns: dict 
        """
        endpoint = "/localization"
        if not id:
            version = await self.get_latest_game_version()
            id = version['localization']

        if locale:
            id = f"{id}:{locale.upper()}"
        
        payload = {
            "payload": {
                "id": f"{id}"
            },
            "unzip": unzip,
            "enums": enums
        }
        response = await self._post(endpoint=endpoint, payload=payload)
        return response
    
    async def get_events(self,
                         enums: bool = False):
        """
        Get current and scheduled events in the game

        Args:
            enums (bool, optional): If the response should use enum values instead of assigned integers. Defaults to False.

        Returns: dict
        """
        endpoint = "/getEvents"
        payload = {
            "enums": enums
        }

        response = await self._post(endpoint=endpoint, payload=payload)
        return response
    
    async def get_guild(self,
                        guildId: str,
                        include_recent_activity: bool = False,
                        enums: bool = False):
        """
        Get a guild's profile

        Args:
            guildId (str): The ID of the guild.
            include_recent_activity (bool, optional): Include more info on members and recent guild events. Defaults to False.
            enums (bool, optional): If the response should use enum values instead of assigned integers. Defaults to False.

        Returns:
            _type_: _description_
        """
        endpoint = "/guild"
        payload = {
            "payload": {
                "guildId": guildId,
                "includeRecentGuildActivityInfo": include_recent_activity
            },
            "enums": enums
        }
        
        response = await self._post(endpoint=endpoint, payload=payload)
        return response
    
    async def get_guilds_by_name(self,
                                 name: str,
                                 start_index: int = 0,
                                 count: int = 10,
                                 enums: bool = False):
        """
        Search guilds by name

        Args:
            name (str): The name of the guild.
            start_index (int, optional): The index to start from (currently ignored by Comlink). Defaults to 0.
            count (int, optional): The number of guilds to return. Defaults to 10.
            enums (bool, optional): If the response should use enum values instead of assigned integers. Defaults to False.

        Returns: dict
        """
        endpoint = "/getGuilds"
        payload = {
            "payload": {
                "filterType": 4,
                "startIndex": start_index,
                "name": name,
                "count": count
            },
            "enums": enums
        }

        response = await self._post(endpoint=endpoint, payload=payload)
        return response

    async def get_guilds_by_criteria(self,
                                     start_index: int = 0,
                                     count: int = 10,
                                     min_member_count: int = 1,
                                     max_member_count: int = 50,
                                     include_invite_only: bool = False,
                                     min_galactic_power: int = 1,
                                     max_galactic_power: int = 500000000,
                                     recent_tb: list[str] = [],
                                     enums: bool = False
                                     ):
        """
        Search guilds by a criteria

        Args:
            start_index (int, optional): The index to start from (currently ignored by Comlink). Defaults to 0.
            count (int, optional): The number of guilds to return. Defaults to 10.
            min_member_count (int, optional): The minimum number of members already in the guild. Defaults to 1.
            max_member_count (int, optional): The maximum number of members allowed in the guild. Defaults to 50.
            include_invite_only (bool, optional): Include invite only guilds. Defaults to False.
            min_galactic_power (int, optional): The minimum total galactic power the guild has. Defaults to 1.
            max_galactic_power (int, optional): The maximum total galactic power the guild has. Defaults to 500000000.
            recent_tb (list[str], optional): An array of Territory Battle ids that the guild has recently done. Defaults to [].
            enums (bool, optional): If the response should use enum values instead of assigned integers. Defaults to False.

        Returns: dict
        """
        endpoint = "/getGuilds"
        payload = {
            "payload": {
                "filterType": 5,
                "startIndex": start_index,
                "count": count,
                "searchCriteria": {
                    "minMemberCount": min_member_count,
                    "maxMemberCount": max_member_count,
                    "includeInviteOnly": include_invite_only,
                    "minGuildGalacticPower": min_galactic_power,
                    "maxGuildGalacticPower": max_galactic_power,
                    "recentTbParticipatedIn": recent_tb
                }
            },
            "enums": enums
        }

        response = await self._post(endpoint=endpoint, payload=payload)
        return response
    
    async def get_leaderboard(self,
                              leaderboard_type: int,
                              event_instance_id: str = None,
                              group_id: str = None,
                              league: int = None,
                              division: int = None,
                              enums: bool = False):
        """
        Get the specified player leaderboard

        Args:
            leaderboard_type (int): The type of leaderboard to get (see Comlink documentation).
            event_instance_id (str, optional): The event instance id. Defaults to None.
            group_id (str, optional): Consists of event instance id along with league name and bracket number. Defaults to None.
            league (int, optional): The id of the league to get. Defaults to None.
            division (int, optional): The id of the division to get. Defaults to None.
            enums (bool, optional): If the response should use enum values instead of assigned integers. Defaults to False.

        Returns: dict
        """
        endpoint = "/getLeaderboard"
        payload = {
            "payload": {
                "leaderboardType": leaderboard_type
            },
            "enums": enums
        }

        leaderboard_requirements = {
            4: [("eventInstanceId", event_instance_id), ("groupId", group_id)],
            6: [("league", league), ("division", division)]
        }

        if leaderboard_type not in leaderboard_requirements:
            e = ValueError(f"Invalid leaderboard type: {leaderboard_type}")
            await self._raise_exception(e)

        for param, value in leaderboard_requirements[leaderboard_type]:
            if not value:
                e = ValueError(f"Leaderboard type {leaderboard_type} requires {param}")
                await self._raise_exception(e)
            payload["payload"][param] = value

        response = await self._post(endpoint=endpoint, payload=payload)
        return response

    async def get_guild_leaderboard(self,
                                    leaderboard_id: list[dict] = [],
                                    count: int = 200,
                                    enums: bool = False):
        """
        Get the specified guild leaderboard

        Args:
            leaderboard_id (list[dict], optional): Array of leaderboards to get (see Comlink documentation). Defaults to [].
            count (int, optional): The number of guilds to return. Defaults to 200.
            enums (bool, optional): If the response should use enum values instead of assigned integers. Defaults to False.

        Returns: dict
        """
        endpoint = "/getGuildLeaderboard"
        payload = {
            "payload": {
                "leaderboardId": leaderboard_id,
                "count": count
            },
            "enums": enums
        }

        response = await self._post(endpoint=endpoint, payload=payload)
        return response
    
    async def get_enums(self):
        """
        Get the enums for the API responses

        Returns: dict
        """
        endpoint = "/enums"
        async with self.session.get(endpoint) as response:
            response = await response.json()
        return response

    async def close(self):
        """
        Close the session
        """
        if self.session:
            await self.session.close()
            self.session = None

    def __del__(self):
        """
        Close the session when the object is deleted
        """
        try:
            if self.session and not self.session.closed:
                if asyncio.get_event_loop().is_running():
                    asyncio.create_task(self.close())
        except Exception:
            asyncio.run(self.close())
    
    async def _raise_exception(self, e):
        """
        Close the session and raise the exception or log the exception if debugging 
        """
        if not self.debug:
            await self.close()
            raise e
        else:
            self.logger.error(e)