class Items:
    """
    Contains information about the items parameter for the /data endpoint.
    
    Each item name maps to a bitwise value for determining collections returned by the endpoint.
    """
    _items = {
        "ALL": -1,
        "category": 1,
        "unlockAnnounmentDefinition": 2,
        "skill": 4,
        "equipment": 8,
        "effect": 16,
        "tables": 32,  # xpTable, table
        "battleEnvironments": 64,
        "eventSampling": 128,
        "targetingSet": 256,
        "requirement": 512,
        "powerUpBundle": 1024,
        "guildBanner": 2048,
        "battleTargetingRule": 4096,
        "persistentVfx": 8192,
        "material": 16384,
        "playerTitle": 32768,
        "playerPortrait": 65536,
        "timeZoneChangeConfig": 131072,
        "enviromentCollection": 262144,
        "effectIconPriority": 524288,
        "socialStatus": 1048576,
        "ability": 2097152,
        "statProgression": 4194304,
        "challenge": 8388608,  # challenge, challengeStyle
        "warDefinition": 16777216,
        "statMod": 33554432,  # statMod, statModSet
        "recipe": 67108864,
        "modRecommendation": 134217728,
        "scavengerConversionSet": 268435456,
        "guild": 536870912,  # guildRaid, raidConfig, etc.
        "mystery": 1073741824,
        "cooldown": 2147483648,
        "dailyActionCap": 4294967296,
        "energyReward": 8589934592,
        "unitGuideDefinition": 17179869184,
        "galacticBundle": 34359738368,
        "relicTierDefinition": 68719476736,
        "units": 137438953472,
        "campaign": 274877906944,
        "conquest": 549755813888,
        "recommendedSquad": 2199023255552,
        "unitGuideLayout": 4398046511104,
        "dailyLoginRewardDefinition": 8796093022208,
        "calendarCategoryDefinition": 17592186044416,
        "territoryTournamentDailyRewardTable": 35184372088832,
        "datacron": 70368744177664,
        "displayableEnemy": 140737488355328,
        "segment1": 2097151,
        "segment2": 68717379584,
        "segment3": 206158430208,
        "segment4": 281200098803712,
        "battleinfo": 2150109456,
    }

    @classmethod
    def get_value(cls, value: str | list[str]):
        """
        Get the bitwise value of an item or list of items.
        
        Args:
            value (str | list[str]): The item name or list of item names.
        """
        if isinstance(value, str):
            return cls._items.get(value, -1)
        elif isinstance(value, list):
            return sum(cls._items.get(item, 0) for item in value)
        return -1

    @classmethod
    def get_items(cls):
        """
        Get a list of all item names.
        """
        return list(cls._items.keys())