import reflex as rx
import json
from typing import Any, cast, TypedDict, Union, Literal
import asyncio
import logging
import os

try:
    from assets.game_data.init_game_data import create_game_data
except ImportError as e:

    def create_game_data():
        logging.exception(
            f"create_game_data not found, game data might be missing: {e}"
        )


class CharacterSprite(TypedDict):
    id: str
    position: str
    sprite: str


class DialogueLine(TypedDict):
    character: str
    text: str


class SaveSlot(TypedDict):
    slot_id: int
    scene_id: str
    timestamp: str
    game_vars: dict[str, Union[str, int, bool, float]]
    history: list[str]
    thumbnail: str


class Choice(TypedDict):
    text: str
    nextScene: str
    set_vars: dict[str, Union[str, int, bool, float]]


class Scene(TypedDict):
    id: str
    background: str
    characters: list[CharacterSprite]
    dialogue: list[DialogueLine]
    choices: list[Choice]
    nextScene: str | None


class CharacterData(TypedDict):
    id: str
    name: str
    color: str
    sprites: dict[str, str]


class StatConfig(TypedDict):
    id: str
    name: str
    description: str
    icon: str


class PlayerStats(TypedDict):
    level: int
    xp: int
    xp_to_next_level: int
    stats: dict[str, int]
    class_name: str
    race: str


class Item(TypedDict):
    id: str
    name: str
    description: str
    icon: str
    item_type: str
    stackable: bool
    max_stack: int
    properties: dict[str, Union[str, int, bool]]
    effects: dict[str, Union[int, str, dict[str, int]]]


class InventorySlot(TypedDict):
    item_id: str
    quantity: int


class GameState(rx.State):
    game_mode: Literal["novel", "map", "info", "context"] = "novel"
    current_scene_id: str = "scene_001"
    current_scene: Scene | None = None
    characters: dict[str, CharacterData] = {}
    stats_config: list[StatConfig] = []
    player_stats: PlayerStats | None = None
    dialogue_index: int = 0
    history: list[str] = []
    dialogue_history: list[DialogueLine] = []
    game_vars: dict[str, Union[str, int, bool, float]] = {}
    is_loading: bool = True
    is_skipping: bool = False
    is_auto_playing: bool = False
    menu_open: bool = False
    history_open: bool = False
    settings_open: bool = False
    stats_open: bool = False
    load_menu_open: bool = False
    inventory_open: bool = False
    inventory_tab: str = "All"
    info_tab: str = "World Map"
    text_speed: float = 1.0
    auto_play_speed: float = 2.0
    items: dict[str, Item] = {}
    inventory: list[InventorySlot | None] = []
    save_slots: str = rx.LocalStorage(json.dumps([None] * 15), name="save_slots")

    @rx.var
    def save_slots_data(self) -> list[SaveSlot | None]:
        try:
            return json.loads(self.save_slots)
        except (json.JSONDecodeError, TypeError) as e:
            logging.exception(f"Error decoding save_slots JSON: {e}")
            return [None] * 15

    @rx.event(background=True)
    async def on_load(self):
        async with self:
            self.is_loading = True
            create_game_data()
            self._load_characters()
            self._load_stats_config()
            self._load_player_stats()
            self._load_all_items()
            self._initialize_inventory()
            scene_data = self._load_scene(self.current_scene_id)
            if scene_data:
                self.current_scene = scene_data
                self.history.append(self.current_scene_id)
                if self.current_scene["dialogue"]:
                    self.dialogue_history.append(self.current_dialogue)
        await asyncio.sleep(0.1)
        async with self:
            self.is_loading = False

    def _load_characters(self):
        char_dir = "assets/game_data/characters"
        if not os.path.exists(char_dir):
            logging.warning(f"Character directory not found: {char_dir}")
            return
        character_files = [
            "character_elara.json",
            "character_kain.json",
            "character_narrator.json",
        ]
        for char_file in character_files:
            file_path = os.path.join(char_dir, char_file)
            if not os.path.exists(file_path):
                logging.warning(f"Character file not found: {file_path}")
                continue
            try:
                with open(file_path, "r") as f:
                    char_data: CharacterData = json.load(f)
                    self.characters[char_data["id"]] = char_data
            except Exception as e:
                logging.exception(f"Error loading character file {char_file}: {e}")

    def _load_all_items(self):
        items_dir = "assets/game_data/items"
        if not os.path.exists(items_dir):
            logging.warning(f"Items directory not found: {items_dir}")
            return
        for item_type_dir in os.listdir(items_dir):
            dir_path = os.path.join(items_dir, item_type_dir)
            if os.path.isdir(dir_path):
                for filename in os.listdir(dir_path):
                    if filename.endswith(".json"):
                        file_path = os.path.join(dir_path, filename)
                        try:
                            with open(file_path, "r") as f:
                                item_data: Item = json.load(f)
                                self.items[item_data["id"]] = item_data
                        except Exception as e:
                            logging.exception(f"Error loading item {filename}: {e}")

    def _initialize_inventory(self):
        initial_items = [
            {"item_id": "health_potion", "quantity": 5},
            {"item_id": "mana_potion", "quantity": 3},
            {"item_id": "iron_ore", "quantity": 12},
            {"item_id": "ancient_sword", "quantity": 1},
        ]
        self.inventory = [None] * 25
        for i, item in enumerate(initial_items):
            if i < len(self.inventory):
                self.inventory[i] = item

    def _load_stats_config(self, config_name: str = "fantasy"):
        config_path = f"assets/game_data/stats/{config_name}_stats.json"
        if not os.path.exists(config_path):
            logging.error(f"Stats config file not found: {config_path}")
            return
        try:
            with open(config_path, "r") as f:
                self.stats_config = json.load(f)
        except Exception as e:
            logging.exception(f"Error loading stats config {config_path}: {e}")

    def _load_player_stats(self):
        player_stats_path = "assets/game_data/player/character.json"
        if not os.path.exists(player_stats_path):
            logging.error(f"Player stats file not found: {player_stats_path}")
            return
        try:
            with open(player_stats_path, "r") as f:
                self.player_stats = json.load(f)
        except Exception as e:
            logging.exception(f"Error loading player stats: {e}")

    def _load_scene(self, scene_id: str) -> Scene | None:
        if scene_id == "action_menu":
            self.set_game_mode("context")
            return self.current_scene
        scene_path = f"assets/game_data/scenes/{scene_id}.json"
        if not os.path.exists(scene_path):
            logging.error(f"Scene file not found: {scene_path}")
            return None
        try:
            with open(scene_path, "r") as f:
                return json.load(f)
        except Exception as e:
            logging.exception(f"Error loading scene file {scene_id}.json: {e}")
            return None

    @rx.event
    def next_dialogue(self):
        if not self.current_scene:
            return
        if self.dialogue_index < len(self.current_scene["dialogue"]) - 1:
            self.dialogue_index += 1
            if self.current_dialogue:
                self.dialogue_history.append(self.current_dialogue)
        else:
            if self.is_skipping or self.is_auto_playing:
                self.is_skipping = False
                self.is_auto_playing = False
            next_scene_id = self.current_scene.get("nextScene")
            if next_scene_id and (not self.current_scene.get("choices")):
                return GameState.change_scene(next_scene_id)

    @rx.event
    def prev_dialogue(self):
        if self.dialogue_index > 0:
            self.dialogue_index -= 1
        elif len(self.history) > 1:
            self.history.pop()
            prev_scene_id = self.history[-1]
            return GameState.change_scene(prev_scene_id, at_end=True)

    @rx.event(background=True)
    async def make_choice(self, choice_data_str: str):
        async with self:
            self.is_skipping = False
            self.is_auto_playing = False
        choice: Choice = json.loads(choice_data_str)
        next_scene_id = choice["nextScene"]
        async with self:
            if "set_vars" in choice:
                for key, value in choice["set_vars"].items():
                    self.game_vars[key] = value
        yield GameState.change_scene(next_scene_id)

    @rx.event(background=True)
    async def change_scene(self, scene_id: str, at_end: bool = False):
        async with self:
            self.is_loading = True
        scene_data = self._load_scene(scene_id)
        async with self:
            if scene_data:
                self.current_scene = scene_data
                self.current_scene_id = scene_id
                self.dialogue_index = 0
                if self.current_scene["dialogue"]:
                    self.dialogue_history.append(self.current_dialogue)
                if at_end:
                    self.dialogue_index = len(self.current_scene["dialogue"]) - 1
                if not at_end:
                    self.history.append(scene_id)
            self.is_loading = False

    @rx.var
    def current_dialogue(self) -> DialogueLine | None:
        if self.current_scene and self.dialogue_index < len(
            self.current_scene["dialogue"]
        ):
            return self.current_scene["dialogue"][self.dialogue_index]
        return None

    @rx.var
    def current_character_name(self) -> str:
        if self.current_dialogue:
            char_id = self.current_dialogue["character"]
            if char_id in self.characters:
                return self.characters[char_id]["name"]
        return ""

    @rx.var
    def current_character_color(self) -> str:
        if self.current_dialogue:
            char_id = self.current_dialogue["character"]
            if char_id in self.characters:
                return self.characters[char_id]["color"]
        return "#FFFFFF"

    @rx.var
    def show_choices(self) -> bool:
        if self.current_scene:
            return self.dialogue_index == len(
                self.current_scene["dialogue"]
            ) - 1 and bool(self.current_scene.get("choices"))
        return False

    @rx.event
    def toggle_menu(self):
        self.menu_open = not self.menu_open
        self.history_open = False
        self.settings_open = False
        self.stats_open = False

    @rx.event
    def set_game_mode(self, mode: Literal["novel", "map", "info", "context"]):
        self.game_mode = mode
        self.menu_open = False

    @rx.event
    def set_info_tab(self, tab: str):
        self.info_tab = tab

    @rx.event
    def toggle_stats(self):
        self.stats_open = not self.stats_open
        self.history_open = False
        self.settings_open = False

    @rx.event
    def toggle_history(self):
        self.history_open = not self.history_open
        self.settings_open = False

    @rx.event
    def toggle_settings(self):
        self.settings_open = not self.settings_open
        self.history_open = False

    @rx.event
    def toggle_inventory(self):
        self.inventory_open = not self.inventory_open
        self.menu_open = False

    @rx.event
    def set_inventory_tab(self, tab: str):
        self.inventory_tab = tab

    @rx.event
    def toggle_load_menu(self):
        self.load_menu_open = not self.load_menu_open
        self.menu_open = False

    @rx.event
    def change_text_speed(self, speed: float):
        self.text_speed = speed

    @rx.event
    def change_auto_speed(self, speed: float):
        self.auto_play_speed = speed

    @rx.event
    def toggle_skip(self):
        self.is_skipping = not self.is_skipping
        if self.is_skipping:
            self.is_auto_playing = False
            return GameState.auto_advance

    @rx.event
    def toggle_auto_play(self):
        self.is_auto_playing = not self.is_auto_playing
        if self.is_auto_playing:
            self.is_skipping = False
            return GameState.auto_advance

    @rx.event(background=True)
    async def auto_advance(self):
        async with self as state:
            if not state.is_auto_playing and (not state.is_skipping):
                return
            if state.show_choices:
                state.is_auto_playing = False
                state.is_skipping = False
                return
            delay = 0.1 if state.is_skipping else state.auto_play_speed
        await asyncio.sleep(delay)
        yield GameState.next_dialogue
        yield GameState.auto_advance

    @rx.event
    def handle_key_down(self, key: str):
        if key.lower() == "i":
            return GameState.toggle_inventory
        if key.lower() == "c":
            return GameState.toggle_stats

    @rx.event
    def save_game(self, slot_id: int, thumbnail: str):
        import datetime

        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        save_data: SaveSlot = {
            "slot_id": slot_id,
            "scene_id": self.current_scene_id,
            "timestamp": timestamp,
            "game_vars": self.game_vars,
            "history": self.history,
            "thumbnail": thumbnail,
        }
        new_slots = self.save_slots_data
        if not isinstance(new_slots, list):
            new_slots = [None] * 15
        while len(new_slots) <= slot_id:
            new_slots.append(None)
        new_slots[slot_id] = save_data
        self.save_slots = json.dumps(new_slots)
        yield rx.toast(f"Game saved to slot {slot_id + 1}")

    @rx.event(background=True)
    async def load_game(self, slot_id: int):
        slots = self.save_slots_data
        if slot_id >= len(slots) or slots[slot_id] is None:
            yield rx.toast("Empty or invalid save slot.")
            return
        save_data: SaveSlot = cast(SaveSlot, slots[slot_id])
        async with self:
            self.game_vars = save_data["game_vars"]
            self.history = save_data["history"]
            self.load_menu_open = False
            self.is_loading = True
        yield rx.toast(f"Loading game from slot {slot_id + 1}...")
        yield GameState.change_scene(save_data["scene_id"])