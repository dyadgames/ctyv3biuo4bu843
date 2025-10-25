import reflex as rx
import json
import os
from typing import Any, cast, TypedDict, Union
import logging
from app.states.game_state import Scene, CharacterData, DialogueLine, CharacterSprite


class FileData(TypedDict):
    path: str
    type: str
    name: str


class EditorState(rx.State):
    files: list[FileData] = []
    current_file_path: str = ""
    current_file_content: str = ""
    editor_error: str = ""
    preview_scene: Scene | None = None
    preview_characters: dict[str, CharacterData] = {}
    dialogue_index: int = 0

    @rx.event(background=True)
    async def on_load_editor(self):
        async with self:
            self.files.clear()
            self._scan_files("assets/game_data/scenes", "scene")
            self._scan_files("assets/game_data/characters", "character")
            self._load_all_characters_for_preview()
        if self.files:
            yield EditorState.load_file(self.files[0]["path"])

    def _scan_files(self, dir_path: str, file_type: str):
        if not os.path.exists(dir_path):
            return
        for filename in os.listdir(dir_path):
            if filename.endswith(".json"):
                self.files.append(
                    {
                        "path": os.path.join(dir_path, filename),
                        "type": file_type,
                        "name": filename,
                    }
                )

    def _load_all_characters_for_preview(self):
        self.preview_characters.clear()
        char_dir = "assets/game_data/characters"
        if not os.path.exists(char_dir):
            return
        for filename in os.listdir(char_dir):
            if filename.endswith(".json"):
                try:
                    with open(os.path.join(char_dir, filename), "r") as f:
                        char_data: CharacterData = json.load(f)
                        self.preview_characters[char_data["id"]] = char_data
                except Exception as e:
                    logging.exception(
                        f"Failed to load character {filename} for preview: {e}"
                    )

    @rx.event
    async def load_file(self, path: str):
        self.current_file_path = path
        try:
            with open(path, "r") as f:
                self.current_file_content = f.read()
            self.update_preview(self.current_file_content)
        except Exception as e:
            logging.exception(f"Error loading file: {e}")
            self.current_file_content = f"Error loading file: {e}"
            self.preview_scene = None

    @rx.event
    def on_editor_change(self, content: str):
        self.current_file_content = content
        self.update_preview(content)

    @rx.event
    def update_preview(self, content: str):
        self.editor_error = ""
        try:
            data = json.loads(content)
            if self.current_file_path.startswith("assets/game_data/scenes"):
                self.preview_scene = cast(Scene, data)
                self.dialogue_index = 0
            elif self.current_file_path.startswith("assets/game_data/characters"):
                char_data: CharacterData = cast(CharacterData, data)
                self.preview_characters[char_data["id"]] = char_data
                self._load_all_characters_for_preview()
        except json.JSONDecodeError as e:
            logging.exception(f"Invalid JSON: {e}")
            self.editor_error = f"Invalid JSON: {e}"
            self.preview_scene = None
        except Exception as e:
            logging.exception(f"Error updating preview: {e}")
            self.editor_error = f"Error updating preview: {e}"
            self.preview_scene = None

    @rx.event(background=True)
    async def save_current_file(self):
        if not self.current_file_path:
            yield rx.toast("No file selected to save.", duration=3000)
            return
        async with self:
            try:
                json.loads(self.current_file_content)
                self.editor_error = ""
            except json.JSONDecodeError as e:
                logging.exception(f"Invalid JSON: {e}")
                self.editor_error = f"Invalid JSON: {e}"
                yield rx.toast("Cannot save: Invalid JSON.", duration=3000)
                return
        try:
            with open(self.current_file_path, "w") as f:
                f.write(self.current_file_content)
            yield rx.toast(
                f"Saved {os.path.basename(self.current_file_path)}", duration=3000
            )
        except Exception as e:
            logging.exception(f"Error saving file: {e}")
            yield rx.toast(f"Error saving file: {e}", duration=3000)

    @rx.event
    def next_preview_dialogue(self):
        if (
            self.preview_scene
            and self.dialogue_index < len(self.preview_scene["dialogue"]) - 1
        ):
            self.dialogue_index += 1

    @rx.event
    def prev_preview_dialogue(self):
        if self.dialogue_index > 0:
            self.dialogue_index -= 1

    @rx.var
    def current_preview_dialogue(self) -> DialogueLine | None:
        if (
            self.preview_scene
            and self.preview_scene["dialogue"]
            and (self.dialogue_index < len(self.preview_scene["dialogue"]))
        ):
            return self.preview_scene["dialogue"][self.dialogue_index]
        return None

    @rx.var
    def current_dialogue_length(self) -> int:
        if self.preview_scene and self.preview_scene["dialogue"]:
            return len(self.preview_scene["dialogue"])
        return 0

    @rx.var
    def preview_character_name(self) -> str:
        if self.current_preview_dialogue:
            char_id = self.current_preview_dialogue["character"]
            if char_id in self.preview_characters:
                return self.preview_characters[char_id]["name"]
        return "Narrator"

    @rx.var
    def preview_character_color(self) -> str:
        if self.current_preview_dialogue:
            char_id = self.current_preview_dialogue["character"]
            if char_id in self.preview_characters:
                return self.preview_characters[char_id]["color"]
        return "#9CA3AF"