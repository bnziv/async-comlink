import aiohttp
import asyncio
from urllib.parse import urlparse
from items import Items

class Comlink:
    """
    Async wrapper for Comlink API
    """
    def __init__(self, 
                 url: str = "http://localhost:3000",
                 host: str | None = None,
                 port: int = 3000):
        """
        Initialize

        Args:
            url (str): The URL of the Comlink API. Defaults to "http://localhost:3000"
            host (str, optional): The host of the Comlink API
            port (int, optional): The port of the Comlink API. Defaults to 3000
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
        try:
            async with self.session.post(endpoint, json=payload) as response:
                response = await response.json()
            return response
        except Exception as e:
            raise e
    
    async def get_game_data(self,
                            version: str = None,
                            include_pve_units: bool = False,
                            request_segment: int = 0,
                            items: str | list = None,
                            enums: bool = False):
        """
        Get game data

        Args:
            version (str, optional): The version of the game data to get. Automatically gets the latest version if not provided.
            include_pve_units (bool, optional): If the response should include PVE units. Defaults to False.
            request_segment (int, optional): The segment of the game data to get (see Comlink documentation). Defaults to 0.
            items (str | list, optional): The items to include in the response (see Items class). Defaults to None.
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

        if items:
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
        if allycode:
            payload["payload"]["allyCode"] = str(allycode)
        elif playerId:
            payload["payload"]["playerId"] = str(playerId)
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
            recent_tb (list[str], optional): An arra of Territory Battle ids that the guild has recently done. Defaults to [].
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

        if leaderboard_type == 4:
            payload["payload"]["eventInstanceId"] = event_instance_id
            payload["payload"]["groupId"] = group_id
        elif leaderboard_type == 6:
            payload["payload"]["league"] = league
            payload["payload"]["division"] = division

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
        if self.session and not self.session.closed:
            if asyncio.get_event_loop().is_running():
                asyncio.create_task(self.close())
            else:
                asyncio.run(self.close())