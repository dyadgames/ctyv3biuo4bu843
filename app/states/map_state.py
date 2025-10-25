import reflex as rx
import json
import os
import logging
from typing import TypedDict, Literal
from app.states.game_state import GameState

try:
    from assets.game_data.init_game_data import create_game_data
except ImportError:

    def create_game_data():
        logging.exception("create_game_data function not found.")


class MajorLocation(TypedDict):
    id: str
    name: str
    description: str
    icon: str
    x: int
    y: int
    unlock_condition: str


class MinorLocation(TypedDict):
    id: str
    name: str
    type: str
    description: str
    available_actions: list[str]
    unlock_condition: str


class RegionalMap(TypedDict):
    id: str
    name: str
    major_location_id: str
    background: str
    locations: list[MinorLocation]


MapMode = Literal["world", "region"]


class MapState(rx.State):
    world_map_data: list[MajorLocation] = []
    regional_maps: dict[str, RegionalMap] = {}
    map_mode: MapMode = "world"
    current_major_location_id: str | None = None
    current_minor_location_id: str | None = None

    def _load_world_map(self):
        world_map_path = "assets/game_data/maps/world_map.json"
        if not os.path.exists(world_map_path):
            logging.error(f"World map file not found: {world_map_path}")
            return
        try:
            with open(world_map_path, "r") as f:
                self.world_map_data = json.load(f)
        except Exception as e:
            logging.exception(f"Error loading world map: {e}")

    def _load_regional_maps(self):
        regional_maps_dir = "assets/game_data/maps/regions"
        if not os.path.exists(regional_maps_dir):
            logging.error(f"Regional maps directory not found: {regional_maps_dir}")
            return
        for filename in os.listdir(regional_maps_dir):
            if filename.endswith(".json"):
                try:
                    with open(os.path.join(regional_maps_dir, filename), "r") as f:
                        map_data: RegionalMap = json.load(f)
                        self.regional_maps[map_data["id"]] = map_data
                except Exception as e:
                    logging.exception(f"Error loading regional map {filename}: {e}")

    @rx.event
    async def on_load_map(self):
        create_game_data()
        self._load_world_map()
        self._load_regional_maps()

    @rx.event
    def select_major_location(self, location_id: str):
        self.current_major_location_id = location_id
        self.map_mode = "region"

    @rx.event
    def back_to_world_map(self):
        self.map_mode = "world"
        self.current_major_location_id = None

    @rx.event
    def select_minor_location(self, location_id: str):
        self.current_minor_location_id = location_id
        yield GameState.set_game_mode("context")

    @rx.var
    def current_regional_map(self) -> RegionalMap | None:
        if self.current_major_location_id:
            return self.regional_maps.get(f"region_{self.current_major_location_id}")
        return None