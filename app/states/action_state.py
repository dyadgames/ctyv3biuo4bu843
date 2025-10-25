import reflex as rx
import json
import os
import logging
from typing import TypedDict, Literal
import datetime


class Action(TypedDict):
    id: str
    name: str
    description: str
    icon: str
    time_cost: int


class ActionState(rx.State):
    actions: dict[str, Action] = {}
    current_time: int = 8
    current_day: int = 1
    _current_location_id: str | None = None

    @rx.event
    async def on_load_context(self):
        from app.states.map_state import MapState

        map_state = await self.get_state(MapState)
        self._current_location_id = map_state.current_minor_location_id
        self._load_actions()

    def _load_actions(self):
        actions_path = "assets/game_data/actions.json"
        if not os.path.exists(actions_path):
            logging.error(f"Actions file not found: {actions_path}")
            return
        try:
            with open(actions_path, "r") as f:
                actions_list: list[Action] = json.load(f)
                self.actions = {action["id"]: action for action in actions_list}
        except Exception as e:
            logging.exception(f"Error loading actions: {e}")

    @rx.var
    async def current_location(self) -> dict | None:
        from app.states.map_state import MapState

        map_state = await self.get_state(MapState)
        if self._current_location_id is None:
            return None
        if map_state.current_regional_map is None:
            return None
        for loc in map_state.current_regional_map["locations"]:
            if loc["id"] == self._current_location_id:
                return loc
        return None

    @rx.var
    async def available_actions(self) -> list[str]:
        location = await self.current_location
        if location:
            return location.get("available_actions", [])
        return []

    @rx.var
    async def location_name(self) -> str:
        location = await self.current_location
        return location["name"] if location else "Unknown Location"

    @rx.var
    async def location_description(self) -> str:
        location = await self.current_location
        return location["description"] if location else ""

    @rx.var
    async def location_background(self) -> str:
        from app.states.map_state import MapState

        map_state = await self.get_state(MapState)
        if map_state.current_regional_map:
            return map_state.current_regional_map.get("background", "/placeholder.svg")
        return "/placeholder.svg"

    @rx.var
    def current_time_str(self) -> str:
        hour = self.current_time % 24
        am_pm = "AM" if hour < 12 else "PM"
        display_hour = hour % 12
        if display_hour == 0:
            display_hour = 12
        return f"Day {self.current_day}, {display_hour}:00 {am_pm}"

    @rx.event
    def perform_action(self, action_id: str):
        if action_id not in self.actions:
            return rx.toast(f"Action '{action_id}' not found.", duration=3000)
        action = self.actions[action_id]
        time_cost = action.get("time_cost", 0)
        if time_cost > 0:
            self.current_time += time_cost
            if self.current_time >= 24:
                days_passed = self.current_time // 24
                self.current_day += days_passed
                self.current_time %= 24
        if action_id == "explore":
            return rx.toast(
                "You explore the area and find nothing of interest.", duration=3000
            )
        elif action_id == "gather":
            return rx.toast("You gather some common herbs.", duration=3000)
        elif action_id == "travel":
            from app.states.game_state import GameState

            return GameState.set_game_mode("map")
        elif action_id == "train":
            return rx.toast("You spend some time training.", duration=3000)
        elif action_id == "craft":
            return rx.toast(
                "You don't have the required materials to craft anything.",
                duration=3000,
            )
        elif action_id == "rest":
            return rx.toast(f"You rest for {time_cost} hours.", duration=3000)
        else:
            return rx.toast(f"Performed action: {action['name']}", duration=3000)