import os
import json


def create_game_data():
    base_path = "assets/game_data"
    os.makedirs(base_path, exist_ok=True)
    chars_path = os.path.join(base_path, "characters")
    scenes_path = os.path.join(base_path, "scenes")
    stats_path = os.path.join(base_path, "stats")
    player_path = os.path.join(base_path, "player")
    os.makedirs(chars_path, exist_ok=True)
    os.makedirs(scenes_path, exist_ok=True)
    os.makedirs(stats_path, exist_ok=True)
    os.makedirs(player_path, exist_ok=True)
    items_path = os.path.join(base_path, "items")
    os.makedirs(os.path.join(items_path, "consumables"), exist_ok=True)
    os.makedirs(os.path.join(items_path, "equipment"), exist_ok=True)
    os.makedirs(os.path.join(items_path, "materials"), exist_ok=True)
    os.makedirs(os.path.join(items_path, "key_items"), exist_ok=True)
    maps_path = os.path.join(base_path, "maps")
    os.makedirs(os.path.join(maps_path, "regions"), exist_ok=True)
    actions_data = [
        {
            "id": "explore",
            "name": "Explore",
            "description": "Trigger random scenarios or events.",
            "icon": "/placeholder.svg",
            "time_cost": 2,
        },
        {
            "id": "gather",
            "name": "Gather",
            "description": "Collect resources with random rewards.",
            "icon": "/placeholder.svg",
            "time_cost": 3,
        },
        {
            "id": "travel",
            "name": "Travel",
            "description": "Return to the regional or world map.",
            "icon": "/placeholder.svg",
            "time_cost": 0,
        },
        {
            "id": "train",
            "name": "Train",
            "description": "Increase stats through training.",
            "icon": "/placeholder.svg",
            "time_cost": 4,
        },
        {
            "id": "craft",
            "name": "Craft",
            "description": "Combine materials into new items.",
            "icon": "/placeholder.svg",
            "time_cost": 2,
        },
        {
            "id": "rest",
            "name": "Rest",
            "description": "Advance time and restore health/stamina.",
            "icon": "/placeholder.svg",
            "time_cost": 4,
        },
    ]
    with open(os.path.join(base_path, "actions.json"), "w") as f:
        json.dump(actions_data, f, indent=2)
    characters = {
        "narrator": {
            "id": "narrator",
            "name": "Narrator",
            "color": "#9CA3AF",
            "sprites": {"default": "/placeholder.svg"},
        },
        "elara": {
            "id": "elara",
            "name": "Elara",
            "color": "#3B82F6",
            "sprites": {
                "neutral": "/placeholder.svg",
                "happy": "/placeholder.svg",
                "sad": "/placeholder.svg",
            },
        },
        "kain": {
            "id": "kain",
            "name": "Kain",
            "color": "#EF4444",
            "sprites": {
                "neutral": "/placeholder.svg",
                "happy": "/placeholder.svg",
                "angry": "/placeholder.svg",
            },
        },
    }
    for key, data in characters.items():
        with open(os.path.join(chars_path, f"character_{key}.json"), "w") as f:
            json.dump(data, f, indent=2)
    scenes = {
        "scene_001": {
            "id": "scene_001",
            "background": "/placeholder.svg",
            "characters": [],
            "dialogue": [
                {
                    "character": "narrator",
                    "text": "Welcome to the Kingdom of Aetheria, a land of magic and mystery.",
                },
                {
                    "character": "narrator",
                    "text": "Your journey begins at the crossroads of destiny. Two paths lie before you...",
                },
                {"character": "narrator", "text": "Which path will you choose?"},
            ],
            "choices": [
                {
                    "text": "Take the forest path (Meet Elara)",
                    "nextScene": "scene_002",
                    "set_vars": {"chosen_path": "forest"},
                },
                {
                    "text": "Take the mountain path (Meet Kain)",
                    "nextScene": "scene_003",
                    "set_vars": {"chosen_path": "mountain"},
                },
            ],
            "nextScene": None,
        },
        "scene_002": {
            "id": "scene_002",
            "background": "/placeholder.svg",
            "characters": [{"id": "elara", "position": "right", "sprite": "happy"}],
            "dialogue": [
                {
                    "character": "elara",
                    "text": "Greetings, traveler! I am Elara, guardian of the Emerald Forest.",
                },
                {
                    "character": "elara",
                    "text": "The forest whispers of dark forces gathering in the north. Will you help me investigate?",
                },
            ],
            "choices": [
                {
                    "text": "Accept Elara's quest",
                    "nextScene": "scene_004",
                    "set_vars": {"ally": "elara"},
                },
                {
                    "text": "Politely decline",
                    "nextScene": "scene_005",
                    "set_vars": {"ally": "none"},
                },
            ],
            "nextScene": None,
        },
        "scene_003": {
            "id": "scene_003",
            "background": "/placeholder.svg",
            "characters": [{"id": "kain", "position": "left", "sprite": "neutral"}],
            "dialogue": [
                {
                    "character": "kain",
                    "text": "Well, well... another wanderer braves the mountain pass.",
                },
                {
                    "character": "kain",
                    "text": "I am Kain. I seek a legendary artifact said to be hidden in these peaks. What brings you here?",
                },
            ],
            "choices": [
                {
                    "text": "Offer to help Kain",
                    "nextScene": "scene_006",
                    "set_vars": {"ally": "kain"},
                },
                {
                    "text": "Claim you're just passing through",
                    "nextScene": "scene_007",
                    "set_vars": {"ally": "none"},
                },
            ],
            "nextScene": None,
        },
        "scene_004": {
            "id": "scene_004",
            "background": "/placeholder.svg",
            "characters": [{"id": "elara", "position": "center", "sprite": "happy"}],
            "dialogue": [
                {
                    "character": "elara",
                    "text": "Wonderful! With your help, we'll surely uncover the source of this darkness.",
                },
                {
                    "character": "narrator",
                    "text": "You and Elara journey north, facing many challenges and strengthening your bond.",
                },
                {
                    "character": "elara",
                    "text": "This has been a worthy adventure. Thank you.",
                },
            ],
            "choices": [],
            "nextScene": "action_menu",
        },
        "scene_005": {
            "id": "scene_005",
            "background": "/placeholder.svg",
            "characters": [{"id": "elara", "position": "right", "sprite": "sad"}],
            "dialogue": [
                {
                    "character": "elara",
                    "text": "I see... I respect your decision. I must face this threat alone, then.",
                },
                {
                    "character": "narrator",
                    "text": "You part ways with Elara, wondering what might have been.",
                },
            ],
            "choices": [],
            "nextScene": "action_menu",
        },
        "scene_006": {
            "id": "scene_006",
            "background": "/placeholder.svg",
            "characters": [{"id": "kain", "position": "center", "sprite": "happy"}],
            "dialogue": [
                {
                    "character": "kain",
                    "text": "Hah! With two of us, this artifact will be ours in no time.",
                },
                {
                    "character": "narrator",
                    "text": "Your combined efforts lead you to a hidden chamber where the artifact lies.",
                },
                {
                    "character": "kain",
                    "text": "An excellent partnership. I'll not forget this.",
                },
            ],
            "choices": [],
            "nextScene": "action_menu",
        },
        "scene_007": {
            "id": "scene_007",
            "background": "/placeholder.svg",
            "characters": [{"id": "kain", "position": "left", "sprite": "angry"}],
            "dialogue": [
                {
                    "character": "kain",
                    "text": "Just passing through, eh? Fine. Don't get in my way.",
                },
                {
                    "character": "narrator",
                    "text": "You continue your journey alone, leaving the brooding warrior to his solitary quest.",
                },
            ],
            "choices": [],
            "nextScene": "action_menu",
        },
    }
    for key, data in scenes.items():
        with open(os.path.join(scenes_path, f"{key}.json"), "w") as f:
            json.dump(data, f, indent=2)
    stats_configs = {
        "fantasy_stats": [
            {
                "id": "str",
                "name": "Strength",
                "description": "Physical power and melee damage.",
                "icon": "sword",
            },
            {
                "id": "dex",
                "name": "Dexterity",
                "description": "Agility, accuracy, and initiative.",
                "icon": "fast-forward",
            },
            {
                "id": "con",
                "name": "Constitution",
                "description": "Health, stamina, and resilience.",
                "icon": "shield",
            },
            {
                "id": "int",
                "name": "Intelligence",
                "description": "Magical power and knowledge.",
                "icon": "brain-circuit",
            },
            {
                "id": "wis",
                "name": "Wisdom",
                "description": "Perception and magical resistance.",
                "icon": "book-open",
            },
            {
                "id": "cha",
                "name": "Charisma",
                "description": "Social interactions and leadership.",
                "icon": "gem",
            },
        ],
        "sci-fi_stats": [
            {
                "id": "pwr",
                "name": "Power",
                "description": "Energy output and combat effectiveness.",
                "icon": "zap",
            },
            {
                "id": "agi",
                "name": "Agility",
                "description": "Speed, evasion, and reflexes.",
                "icon": "move-3d",
            },
            {
                "id": "end",
                "name": "Endurance",
                "description": "System durability and resistance.",
                "icon": "battery-full",
            },
            {
                "id": "tec",
                "name": "Tech",
                "description": "Hacking, repairs, and drone control.",
                "icon": "cpu",
            },
            {
                "id": "psy",
                "name": "Psionics",
                "description": "Mental abilities and psychic force.",
                "icon": "sparkles",
            },
            {
                "id": "cha",
                "name": "Charm",
                "description": "Negotiation and crew morale.",
                "icon": "heart-handshake",
            },
        ],
        "modern_stats": [
            {
                "id": "phy",
                "name": "Physique",
                "description": "Overall physical fitness and strength.",
                "icon": "dumbbell",
            },
            {
                "id": "agi",
                "name": "Agility",
                "description": "Coordination and quickness.",
                "icon": "footprints",
            },
            {
                "id": "vit",
                "name": "Vitality",
                "description": "Health and resistance to illness.",
                "icon": "heart-pulse",
            },
            {
                "id": "int",
                "name": "Intellect",
                "description": "Problem-solving and learning.",
                "icon": "lightbulb",
            },
            {
                "id": "wil",
                "name": "Willpower",
                "description": "Mental fortitude and focus.",
                "icon": "user-check",
            },
            {
                "id": "soc",
                "name": "Social",
                "description": "Communication and influence.",
                "icon": "users",
            },
        ],
    }
    for key, data in stats_configs.items():
        with open(os.path.join(stats_path, f"{key}.json"), "w") as f:
            json.dump(data, f, indent=2)
    player_data = {
        "level": 1,
        "xp": 0,
        "xp_to_next_level": 100,
        "class_name": "Adventurer",
        "race": "Human",
        "stats": {"str": 10, "dex": 12, "con": 11, "int": 8, "wis": 9, "cha": 13},
    }
    with open(os.path.join(player_path, "character.json"), "w") as f:
        json.dump(player_data, f, indent=2)
    items_data = {
        "consumables/health_potion.json": {
            "id": "health_potion",
            "name": "Health Potion",
            "description": "A simple potion that restores a small amount of health.",
            "icon": "/placeholder.svg",
            "item_type": "Consumable",
            "stackable": True,
            "max_stack": 99,
            "properties": {},
            "effects": {"heal": 50},
        },
        "consumables/mana_potion.json": {
            "id": "mana_potion",
            "name": "Mana Potion",
            "description": "Restores a small amount of mana.",
            "icon": "/placeholder.svg",
            "item_type": "Consumable",
            "stackable": True,
            "max_stack": 99,
            "properties": {},
            "effects": {"restore_mana": 30},
        },
        "equipment/ancient_sword.json": {
            "id": "ancient_sword",
            "name": "Ancient Sword",
            "description": "An old sword, it still seems sharp.",
            "icon": "/placeholder.svg",
            "item_type": "Equipment",
            "stackable": False,
            "max_stack": 1,
            "properties": {"slot": "main_hand", "damage": 10},
            "effects": {"stat_boost": {"str": 2}},
        },
        "materials/iron_ore.json": {
            "id": "iron_ore",
            "name": "Iron Ore",
            "description": "A chunk of raw iron ore. Can be used for crafting.",
            "icon": "/placeholder.svg",
            "item_type": "Material",
            "stackable": True,
            "max_stack": 99,
            "properties": {},
            "effects": {},
        },
        "key_items/cellar_key.json": {
            "id": "cellar_key",
            "name": "Cellar Key",
            "description": "An old, rusty key. Seems to unlock something important.",
            "icon": "/placeholder.svg",
            "item_type": "Key Item",
            "stackable": False,
            "max_stack": 1,
            "properties": {},
            "effects": {"unlocks": "castle_cellar"},
        },
    }
    for path, data in items_data.items():
        full_path = os.path.join(items_path, path)
        with open(full_path, "w") as f:
            json.dump(data, f, indent=2)
    world_map_data = [
        {
            "id": "emerald_forest",
            "name": "Emerald Forest",
            "description": "A vast, ancient forest teeming with life and secrets.",
            "icon": "trees",
            "x": 25,
            "y": 60,
            "unlock_condition": "true",
        },
        {
            "id": "ironpeak_mountains",
            "name": "Ironpeak Mountains",
            "description": "Treacherous peaks known for their rich mineral veins.",
            "icon": "mountain",
            "x": 45,
            "y": 30,
            "unlock_condition": "true",
        },
        {
            "id": "silverwind_city",
            "name": "Silverwind City",
            "description": "A bustling metropolis and the kingdom's capital.",
            "icon": "castle",
            "x": 35,
            "y": 50,
            "unlock_condition": "true",
        },
    ]
    with open(os.path.join(maps_path, "world_map.json"), "w") as f:
        json.dump(world_map_data, f, indent=2)
    regional_maps_data = {
        "region_emerald_forest": {
            "id": "region_emerald_forest",
            "name": "Emerald Forest",
            "major_location_id": "emerald_forest",
            "background": "/placeholder.svg",
            "locations": [
                {
                    "id": "whispering_glade",
                    "name": "Whispering Glade",
                    "type": "Exploration",
                    "description": "A tranquil clearing where the wind sounds like whispers.",
                    "available_actions": ["explore", "gather", "rest", "travel"],
                    "unlock_condition": "true",
                },
                {
                    "id": "ancient_oak",
                    "name": "Ancient Oak",
                    "type": "Story",
                    "description": "A colossal tree said to be as old as the kingdom itself.",
                    "available_actions": ["explore", "train", "travel"],
                    "unlock_condition": "true",
                },
            ],
        },
        "region_ironpeak_mountains": {
            "id": "region_ironpeak_mountains",
            "name": "Ironpeak Mountains",
            "major_location_id": "ironpeak_mountains",
            "background": "/placeholder.svg",
            "locations": [
                {
                    "id": "miners_camp",
                    "name": "Miner's Camp",
                    "type": "Social",
                    "description": "A rugged camp at the base of the mountains.",
                    "available_actions": ["explore", "craft", "rest", "travel"],
                    "unlock_condition": "true",
                },
                {
                    "id": "crystal_cave",
                    "name": "Crystal Cave",
                    "type": "Dungeon",
                    "description": "A glittering cave filled with valuable crystals and danger.",
                    "available_actions": ["explore", "gather", "travel"],
                    "unlock_condition": "game_vars.ally == 'kain'",
                },
            ],
        },
    }
    for key, data in regional_maps_data.items():
        with open(os.path.join(maps_path, "regions", f"{key}.json"), "w") as f:
            json.dump(data, f, indent=2)