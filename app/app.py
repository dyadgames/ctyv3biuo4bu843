import reflex as rx
import reflex_enterprise as rxe
from reflex_enterprise import dnd
from app.states.game_state import GameState, DialogueLine, StatConfig
from app.states.editor_state import EditorState
from app.states.map_state import MapState, MajorLocation, MinorLocation, RegionalMap
from app.states.action_state import ActionState
from reflex_monaco import monaco


def character_sprite(char_sprite: rx.Var[dict]) -> rx.Component:
    char_id = char_sprite["id"]
    sprite_key = char_sprite["sprite"]
    sprite_src = rx.cond(
        GameState.characters.contains(char_id),
        rx.cond(
            GameState.characters[char_id]["sprites"].contains(sprite_key),
            GameState.characters[char_id]["sprites"][sprite_key],
            "/placeholder.svg",
        ),
        "/placeholder.svg",
    )
    position_class = rx.match(
        char_sprite["position"],
        ("left", "bottom-0 left-[-5%] md:left-[5%]"),
        ("right", "bottom-0 right-[-5%] md:right-[5%]"),
        ("center", "bottom-0 left-1/2 -translate-x-1/2"),
        "bottom-0 left-1/2 -translate-x-1/2",
    )
    is_speaking = GameState.current_dialogue["character"] == char_id
    return rx.el.div(
        rx.image(
            src=sprite_src,
            class_name="h-[80vh] md:h-[95vh] object-contain transition-all duration-500 ease-in-out",
            style={
                "transform": rx.cond(is_speaking, "scale(1.05)", "scale(1)"),
                "filter": rx.cond(is_speaking, "brightness(1)", "brightness(0.8)"),
            },
        ),
        class_name=f"absolute transition-opacity duration-500 opacity-100 {position_class}",
    )


def dialogue_box() -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.cond(
                GameState.current_character_name != "Narrator",
                rx.el.h2(
                    GameState.current_character_name,
                    class_name="font-bold text-2xl mb-2",
                    style={"color": GameState.current_character_color},
                ),
                None,
            ),
            rx.el.p(
                rx.cond(
                    GameState.current_dialogue,
                    GameState.current_dialogue["text"],
                    "...",
                ),
                class_name="text-lg text-gray-200 font-['Roboto']",
                key=GameState.current_dialogue.to_string(),
            ),
            class_name="min-h-[120px]",
        ),
        rx.cond(
            GameState.show_choices,
            rx.el.div(
                rx.foreach(
                    GameState.current_scene["choices"],
                    lambda choice: rx.el.button(
                        choice["text"],
                        on_click=lambda: GameState.make_choice(choice.to_string()),
                        class_name="w-full text-left p-4 bg-sky-500/20 hover:bg-sky-500/40 text-white rounded-lg transition-all duration-200 border border-sky-400/30 shadow-md hover:shadow-sky-500/20",
                    ),
                ),
                class_name="grid grid-cols-1 gap-4 mt-4",
            ),
            rx.el.div(
                rx.el.button(
                    rx.icon("arrow-left", class_name="h-6 w-6"),
                    on_click=GameState.prev_dialogue,
                    class_name="p-3 bg-white/10 rounded-full hover:bg-white/20 transition-colors disabled:opacity-50",
                    disabled=(GameState.dialogue_index <= 0)
                    & (GameState.history.length() <= 1),
                ),
                rx.el.button(
                    rx.icon("arrow-right", class_name="h-6 w-6"),
                    on_click=GameState.next_dialogue,
                    class_name="p-3 bg-white/10 rounded-full hover:bg-white/20 transition-colors",
                ),
                class_name="flex justify-end gap-4 mt-4",
            ),
        ),
        class_name="absolute bottom-5 left-5 right-5 md:left-1/4 md:right-1/4 bg-black/70 backdrop-blur-md p-6 rounded-xl border border-gray-700/50 shadow-2xl transition-opacity duration-500 ease-in-out",
    )


def loading_overlay() -> rx.Component:
    return rx.cond(
        GameState.is_loading,
        rx.el.div(
            rx.spinner(class_name="text-sky-400", size="3"),
            rx.el.p("Loading...", class_name="text-white mt-4 font-semibold"),
            class_name="absolute inset-0 bg-black/80 flex flex-col items-center justify-center z-[99]",
        ),
        None,
    )


def top_left_hud() -> rx.Component:
    xp_percentage = rx.cond(
        GameState.player_stats["xp_to_next_level"] > 0,
        f"{(GameState.player_stats['xp'] / GameState.player_stats['xp_to_next_level'] * 100).to_string()}%",
        "0%",
    )
    return rx.el.div(
        rx.el.div(
            rx.el.button(
                rx.image(
                    src="/placeholder.svg",
                    class_name="h-20 w-20 rounded-full border-2 border-sky-400 object-cover bg-gray-700",
                ),
                on_click=GameState.toggle_stats,
                class_name="p-0 rounded-full hover:scale-105 transition-transform",
            ),
            rx.el.div(
                rx.el.div(
                    rx.icon("heart", class_name="h-4 w-4 text-red-400 mr-2"),
                    rx.el.div(
                        rx.el.div(
                            class_name="bg-red-500 h-full rounded-full transition-all duration-500",
                            style={"width": "70%"},
                        ),
                        class_name="w-full bg-red-900/50 h-3 rounded-full overflow-hidden",
                    ),
                    class_name="flex items-center",
                ),
                rx.el.div(
                    rx.icon("sparkles", class_name="h-4 w-4 text-blue-400 mr-2"),
                    rx.el.div(
                        rx.el.div(
                            class_name="bg-blue-500 h-full rounded-full transition-all duration-500",
                            style={"width": "85%"},
                        ),
                        class_name="w-full bg-blue-900/50 h-3 rounded-full overflow-hidden",
                    ),
                    class_name="flex items-center",
                ),
                class_name="flex-1 flex flex-col justify-center gap-2",
            ),
            class_name="flex items-center gap-4",
        ),
        rx.el.div(
            rx.el.div(
                rx.el.p(
                    f"LVL {GameState.player_stats['level'].to_string()}",
                    class_name="text-xs font-bold text-yellow-300",
                ),
                rx.el.div(
                    rx.el.div(
                        class_name="bg-yellow-400 h-full rounded-full transition-all duration-500",
                        style={"width": xp_percentage},
                    ),
                    class_name="flex-1 bg-yellow-800/50 h-2 rounded-full overflow-hidden",
                ),
                class_name="flex items-center gap-2 w-full",
            ),
            class_name="mt-2",
        ),
        class_name="absolute top-5 left-5 bg-black/50 backdrop-blur-md p-4 rounded-xl border border-gray-700/50 shadow-lg w-80",
    )


def top_right_hud() -> rx.Component:
    return rx.el.div(
        rx.el.button(
            rx.icon("backpack", class_name="h-6 w-6"),
            on_click=GameState.toggle_inventory,
            class_name="p-3 bg-white/10 rounded-full hover:bg-white/20 transition-colors",
        ),
        rx.el.button(
            rx.icon("settings", class_name="h-6 w-6"),
            on_click=GameState.toggle_settings,
            class_name="p-3 bg-white/10 rounded-full hover:bg-white/20 transition-colors",
        ),
        rx.el.button(
            rx.icon("book-open", class_name="h-6 w-6"),
            on_click=lambda: GameState.set_game_mode("info"),
            class_name="p-3 bg-white/10 rounded-full hover:bg-white/20 transition-colors",
        ),
        class_name="absolute top-5 right-5 flex items-center gap-3 z-40",
    )


def info_screen_overlay() -> rx.Component:
    tabs = ["World Map", "Quests", "Codex"]

    def info_tab_button(tab_name: str) -> rx.Component:
        return rx.el.button(
            tab_name,
            on_click=lambda: GameState.set_info_tab(tab_name),
            class_name=rx.cond(
                GameState.info_tab == tab_name,
                "px-6 py-3 text-lg font-semibold text-sky-300 bg-sky-500/20 border-b-2 border-sky-400",
                "px-6 py-3 text-lg font-semibold text-gray-400 hover:bg-white/10 border-b-2 border-transparent",
            ),
        )

    def map_tab() -> rx.Component:
        return rx.el.div(
            world_map_view(), class_name="w-full h-full p-4 bg-black/20 rounded-b-lg"
        )

    def quests_tab() -> rx.Component:
        return rx.el.div(
            rx.el.p("Quest log coming soon...", class_name="text-gray-400"),
            class_name="w-full h-full p-8 bg-black/20 rounded-b-lg flex items-center justify-center",
        )

    def codex_tab() -> rx.Component:
        return rx.el.div(
            rx.el.p("Codex of game lore coming soon...", class_name="text-gray-400"),
            class_name="w-full h-full p-8 bg-black/20 rounded-b-lg flex items-center justify-center",
        )

    return rx.el.div(
        rx.el.div(
            rx.el.div(
                rx.el.div(class_name="w-16"),
                rx.el.div(
                    rx.foreach(tabs, info_tab_button),
                    class_name="flex justify-center border-b border-gray-700",
                ),
                rx.el.button(
                    rx.icon("x", class_name="h-6 w-6"),
                    on_click=lambda: GameState.set_game_mode("novel"),
                    class_name="p-3 rounded-full hover:bg-white/20 transition-colors",
                ),
                class_name="flex items-center justify-between bg-black/50 p-2",
            ),
            rx.match(
                GameState.info_tab,
                ("World Map", map_tab()),
                ("Quests", quests_tab()),
                ("Codex", codex_tab()),
                rx.el.div("Select a tab"),
            ),
            class_name="w-full h-full flex flex-col",
        ),
        class_name="absolute inset-0 bg-gray-900/90 backdrop-blur-md z-50",
    )


def history_overlay() -> rx.Component:
    def history_entry(dialogue: DialogueLine) -> rx.Component:
        char_name = rx.cond(
            GameState.characters.contains(dialogue["character"]),
            GameState.characters[dialogue["character"]]["name"],
            "",
        )
        char_color = rx.cond(
            GameState.characters.contains(dialogue["character"]),
            GameState.characters[dialogue["character"]]["color"],
            "#FFFFFF",
        )
        return rx.el.div(
            rx.el.p(
                rx.el.span(
                    char_name, class_name="font-bold", style={"color": char_color}
                ),
                f": {dialogue['text']}",
            ),
            class_name="mb-2 text-gray-300",
        )

    return rx.cond(
        GameState.history_open,
        rx.el.div(
            rx.el.div(
                rx.el.h2("Dialogue History", class_name="text-3xl font-bold mb-6"),
                rx.el.div(
                    rx.foreach(GameState.dialogue_history, history_entry),
                    class_name="overflow-y-auto h-[60vh] p-4 bg-black/30 rounded-lg",
                ),
                rx.el.button(
                    "Close",
                    on_click=GameState.toggle_history,
                    class_name="mt-6 px-6 py-2 bg-sky-500/50 hover:bg-sky-500/70 rounded-lg font-semibold",
                ),
                class_name="w-full max-w-2xl p-8 bg-black/70 rounded-xl",
            ),
            class_name="absolute inset-0 bg-black/80 backdrop-blur-md flex items-center justify-center z-40",
        ),
        None,
    )


def settings_overlay() -> rx.Component:
    def slider_setting(
        label: str,
        value: rx.Var,
        on_change: rx.event.EventHandler,
        min_val: float,
        max_val: float,
        step: float,
    ) -> rx.Component:
        return rx.el.div(
            rx.el.label(label, class_name="font-semibold mb-2"),
            rx.el.div(
                rx.el.input(
                    type="range",
                    min=min_val,
                    max=max_val,
                    step=step,
                    default_value=value.to_string(),
                    on_change=on_change.throttle(50),
                    class_name="w-full h-2 bg-gray-600 rounded-lg appearance-none cursor-pointer accent-sky-500",
                    key=label,
                ),
                rx.el.span(f"{value:.1f}x", class_name="w-12 text-right"),
                class_name="flex items-center gap-4",
            ),
            class_name="w-full",
        )

    return rx.cond(
        GameState.settings_open,
        rx.el.div(
            rx.el.div(
                rx.el.h2("Settings", class_name="text-3xl font-bold mb-6"),
                rx.el.div(
                    slider_setting(
                        "Text Speed",
                        GameState.text_speed,
                        GameState.change_text_speed,
                        0.5,
                        2.0,
                        0.1,
                    ),
                    slider_setting(
                        "Auto-Play Speed",
                        GameState.auto_play_speed,
                        GameState.change_auto_speed,
                        1.0,
                        5.0,
                        0.5,
                    ),
                    class_name="flex flex-col gap-6",
                ),
                rx.el.button(
                    "Close",
                    on_click=GameState.toggle_settings,
                    class_name="mt-8 px-6 py-2 bg-sky-500/50 hover:bg-sky-500/70 rounded-lg font-semibold",
                ),
                class_name="w-full max-w-md p-8 bg-black/70 rounded-xl",
            ),
            class_name="absolute inset-0 bg-black/80 backdrop-blur-md flex items-center justify-center z-40",
        ),
        None,
    )


def load_menu_overlay() -> rx.Component:
    def save_slot_button(slot: rx.Var[dict | None], index: int) -> rx.Component:
        return rx.el.button(
            rx.cond(
                slot,
                rx.el.div(
                    rx.image(
                        src=slot["thumbnail"],
                        class_name="w-full h-24 object-cover rounded-t-lg bg-gray-700",
                    ),
                    rx.el.div(
                        rx.el.span(f"Save Slot {index + 1}", class_name="font-bold"),
                        rx.el.span(
                            slot["timestamp"], class_name="text-xs text-gray-400"
                        ),
                        class_name="p-2 flex flex-col items-start",
                    ),
                    class_name="w-full h-full flex flex-col",
                ),
                rx.el.div(
                    rx.el.div(
                        rx.icon("save", class_name="h-8 w-8 text-gray-600"),
                        rx.el.p(
                            f"Empty Slot {index + 1}",
                            class_name="text-sm font-semibold text-gray-500 mt-2",
                        ),
                        class_name="flex flex-col items-center justify-center",
                    ),
                    class_name="w-full h-full flex items-center justify-center",
                ),
            ),
            on_click=lambda: GameState.load_game(index),
            disabled=slot.is_none(),
            class_name="w-full aspect-[4/3] bg-black/50 hover:bg-sky-500/20 ring-1 ring-inset ring-gray-700 hover:ring-sky-500 transition-all duration-200 rounded-lg disabled:opacity-50 disabled:cursor-not-allowed overflow-hidden",
        )

    return rx.cond(
        GameState.load_menu_open,
        rx.el.div(
            rx.el.div(
                rx.el.h2("Load Game", class_name="text-4xl font-bold mb-8 text-center"),
                rx.el.div(
                    rx.foreach(
                        GameState.save_slots_data,
                        lambda slot, index: save_slot_button(slot, index),
                    ),
                    class_name="grid grid-cols-2 md:grid-cols-3 gap-4 w-full max-w-4xl",
                ),
                rx.el.button(
                    "Close",
                    on_click=GameState.toggle_load_menu,
                    class_name="mt-8 px-6 py-2 bg-sky-500/50 hover:bg-sky-500/70 rounded-lg font-semibold",
                ),
                class_name="flex flex-col items-center justify-center p-8",
            ),
            class_name="absolute inset-0 bg-black/80 backdrop-blur-md flex items-center justify-center z-40 overflow-y-auto",
        ),
        None,
    )


def stats_overlay() -> rx.Component:
    def stat_row(stat_config: StatConfig) -> rx.Component:
        stat_id = stat_config["id"]
        return rx.el.div(
            rx.el.div(
                rx.icon(stat_config["icon"], class_name="h-6 w-6 mr-3 text-sky-400"),
                rx.el.div(
                    rx.el.p(stat_config["name"], class_name="font-bold text-lg"),
                    rx.el.p(
                        stat_config["description"], class_name="text-sm text-gray-400"
                    ),
                ),
                class_name="flex items-center",
            ),
            rx.el.p(
                GameState.player_stats["stats"].get(stat_id, 0).to_string(),
                class_name="text-2xl font-bold text-white",
            ),
            class_name="flex justify-between items-center p-4 bg-white/5 rounded-lg",
        )

    return rx.cond(
        GameState.stats_open,
        rx.el.div(
            rx.el.div(
                rx.el.div(
                    rx.el.div(
                        rx.el.h2("Character", class_name="text-3xl font-bold"),
                        rx.el.div(
                            rx.el.p(
                                f"Level: {GameState.player_stats['level']}",
                                class_name="font-semibold text-yellow-300",
                            ),
                            rx.el.p(
                                f"{GameState.player_stats['race']} {GameState.player_stats['class_name']}",
                                class_name="text-gray-400",
                            ),
                        ),
                    ),
                    rx.el.button(
                        rx.icon("x", class_name="w-5 h-5"),
                        on_click=GameState.toggle_stats,
                        class_name="p-2 rounded-full hover:bg-white/20 transition-colors",
                    ),
                    class_name="flex justify-between items-start mb-4",
                ),
                rx.el.p(
                    f"XP: {GameState.player_stats['xp']} / {GameState.player_stats['xp_to_next_level']}",
                    class_name="text-xs text-gray-400 text-right mb-1",
                ),
                rx.el.div(
                    rx.el.div(
                        class_name="bg-sky-500 h-2 rounded-full",
                        style={
                            "width": f"{(GameState.player_stats['xp'] / GameState.player_stats['xp_to_next_level'] * 100).to_string()}%"
                        },
                    ),
                    class_name="w-full bg-gray-600 rounded-full h-2 mb-6",
                ),
                rx.el.h3("Attributes", class_name="text-xl font-bold mb-3"),
                rx.el.div(
                    rx.foreach(GameState.stats_config, stat_row),
                    class_name="grid grid-cols-1 md:grid-cols-2 gap-4 overflow-y-auto max-h-[40vh] pr-2",
                ),
                rx.el.h3("Skills", class_name="text-xl font-bold mt-6 mb-3"),
                rx.el.div(
                    rx.el.p("Skills system coming soon.", class_name="text-gray-500"),
                    class_name="flex items-center justify-center p-8 bg-black/20 rounded-lg",
                ),
                class_name="w-full max-w-4xl p-6 bg-black/80 backdrop-blur-xl rounded-xl border border-gray-700 shadow-2xl",
            ),
            class_name="absolute inset-0 bg-gray-900/90 backdrop-blur-md flex items-center justify-center z-50",
        ),
        None,
    )


def inventory_overlay() -> rx.Component:
    def item_details(slot: dict) -> rx.Component:
        item = GameState.items.get(slot["item_id"], {})
        return rx.fragment(
            rx.image(
                src=item.get("icon", "/placeholder.svg"),
                class_name="w-16 h-16 object-contain p-2",
            ),
            rx.el.div(
                rx.el.p(
                    item.get("name", "Unknown Item"),
                    class_name="font-bold text-xs truncate",
                ),
                class_name="absolute bottom-0 left-0 right-0 p-1 bg-black/50 text-center",
            ),
            rx.cond(
                item.get("stackable", False),
                rx.el.div(
                    rx.el.span(slot["quantity"], class_name="text-xs font-bold"),
                    class_name="absolute top-1 right-1 px-1.5 py-0.5 bg-sky-600 rounded-full text-white",
                ),
                None,
            ),
        )

    def item_card(slot: dict | None) -> rx.Component:
        return rx.el.div(
            rx.cond(slot, item_details(slot), rx.el.div()),
            class_name="relative w-full aspect-square bg-white/5 rounded-lg flex items-center justify-center border border-transparent hover:border-sky-500 hover:bg-white/10 transition-all",
        )

    return rx.cond(
        GameState.inventory_open,
        rx.el.div(
            rx.el.div(
                rx.el.div(
                    rx.el.h2("Inventory", class_name="text-xl font-bold"),
                    rx.el.button(
                        rx.icon("x", class_name="w-5 h-5"),
                        on_click=GameState.toggle_inventory,
                        class_name="p-2 rounded-full hover:bg-white/20 transition-colors",
                    ),
                    class_name="flex justify-between items-center p-4 border-b border-gray-700 cursor-move",
                ),
                rx.el.div(
                    rx.foreach(GameState.inventory, lambda slot: item_card(slot)),
                    class_name="grid grid-cols-5 gap-2 p-4",
                ),
                class_name="w-[480px] bg-black/80 backdrop-blur-xl rounded-xl border border-gray-700 shadow-2xl flex flex-col",
            ),
            class_name="absolute inset-0 bg-gray-900/90 backdrop-blur-md flex items-center justify-center z-[60]",
        ),
        None,
    )


def novel_view() -> rx.Component:
    return rx.el.div(
        rx.image(
            src=rx.cond(
                GameState.current_scene,
                GameState.current_scene["background"],
                "/placeholder.svg",
            ),
            class_name="absolute inset-0 w-full h-full object-cover transition-opacity duration-1000 ease-in-out",
            key=rx.cond(
                GameState.current_scene, GameState.current_scene["id"], "loading"
            ),
        ),
        rx.el.div(
            class_name="absolute inset-0 bg-gradient-to-t from-black/50 to-transparent"
        ),
        rx.cond(
            GameState.current_scene,
            rx.foreach(GameState.current_scene["characters"], character_sprite),
            None,
        ),
        dialogue_box(),
        top_left_hud(),
        top_right_hud(),
        loading_overlay(),
        rx.cond(GameState.history_open, history_overlay(), None),
        rx.cond(GameState.settings_open, settings_overlay(), None),
        rx.cond(GameState.load_menu_open, load_menu_overlay(), None),
        stats_overlay(),
        inventory_overlay(),
        id="game-viewport",
        class_name="relative w-screen h-screen bg-gray-900 overflow-hidden pointer-events-none",
    )


def map_view() -> rx.Component:
    return rx.el.div(
        rx.match(
            MapState.map_mode,
            ("world", world_map_view()),
            ("region", regional_map_view()),
            rx.el.div("Invalid map mode"),
        ),
        on_mount=MapState.on_load_map,
        class_name="w-screen h-screen bg-gray-800 text-white",
    )


def world_map_view() -> rx.Component:
    def location_marker(location: MajorLocation) -> rx.Component:
        return rx.el.div(
            rx.el.button(
                rx.icon(location["icon"], class_name="h-6 w-6"),
                on_click=lambda: MapState.select_major_location(location["id"]),
                class_name="p-2 rounded-full bg-sky-500 hover:bg-sky-400 hover:scale-110 transition-all shadow-lg",
            ),
            rx.el.div(
                rx.el.p(location["name"], class_name="font-bold"),
                rx.el.p(location["description"], class_name="text-xs"),
                class_name="absolute bottom-full left-1/2 -translate-x-1/2 mb-2 w-48 p-2 bg-black/70 rounded-md text-center opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none",
            ),
            class_name="absolute group",
            style={"left": f"{location['x']}%", "top": f"{location['y']}%"},
        )

    return rx.el.div(
        rx.el.div(
            rx.el.h1("World Map", class_name="text-3xl font-bold"),
            rx.el.button(
                "Back to Game",
                on_click=lambda: GameState.set_game_mode("novel"),
                class_name="px-4 py-2 bg-sky-600/50 hover:bg-sky-600/80 rounded-lg font-semibold",
            ),
            class_name="absolute top-5 left-5 right-5 flex justify-between items-center z-10",
        ),
        rx.image(
            src="/placeholder.svg",
            class_name="absolute inset-0 w-full h-full object-cover",
        ),
        rx.foreach(MapState.world_map_data, location_marker),
        class_name="relative w-full h-full",
    )


def regional_map_view() -> rx.Component:
    def minor_location_card(location: MinorLocation) -> rx.Component:
        return rx.el.button(
            rx.el.p(location["name"], class_name="font-bold"),
            rx.el.p(location["type"], class_name="text-xs text-sky-300"),
            rx.el.p(location["description"], class_name="text-sm mt-2 text-gray-400"),
            on_click=lambda: MapState.select_minor_location(location["id"]),
            class_name="p-4 bg-black/30 hover:bg-black/50 rounded-lg text-left w-full border border-gray-700 hover:border-sky-500 transition-all",
        )

    return rx.el.div(
        rx.cond(
            MapState.current_regional_map.is_not_none(),
            rx.el.div(
                rx.image(
                    src=MapState.current_regional_map["background"],
                    class_name="absolute inset-0 w-full h-full object-cover opacity-30",
                ),
                rx.el.div(
                    rx.el.button(
                        rx.icon("arrow-left", class_name="mr-2"),
                        "World Map",
                        on_click=MapState.back_to_world_map,
                        class_name="flex items-center px-4 py-2 bg-sky-600/50 hover:bg-sky-600/80 rounded-lg font-semibold mb-6",
                    ),
                    rx.el.h1(
                        MapState.current_regional_map["name"],
                        class_name="text-4xl font-bold mb-6 text-center",
                    ),
                    rx.el.div(
                        rx.foreach(
                            MapState.current_regional_map["locations"],
                            minor_location_card,
                        ),
                        class_name="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4",
                    ),
                    class_name="relative p-8 w-full max-w-7xl mx-auto",
                ),
                class_name="relative w-full h-full overflow-y-auto",
            ),
            rx.el.div(
                rx.el.p("Loading region..."),
                rx.el.button("Back", on_click=MapState.back_to_world_map),
                class_name="flex flex-col items-center justify-center h-full",
            ),
        ),
        class_name="w-full h-full",
    )


def index() -> rx.Component:
    return rx.el.main(
        rx.window_event_listener(
            on_key_down=lambda key: GameState.handle_key_down(key)
        ),
        rx.match(
            GameState.game_mode,
            ("novel", novel_view()),
            ("map", map_view()),
            ("info", info_screen_overlay()),
            ("context", context_menu_overlay()),
            rx.el.div("Loading..."),
        ),
        on_mount=GameState.on_load,
        class_name="font-['Roboto'] text-white bg-gray-900",
    )


def editor_preview_character_sprite(char_sprite: rx.Var[dict]) -> rx.Component:
    char_id = char_sprite["id"]
    sprite_key = char_sprite["sprite"]
    sprite_src = rx.cond(
        EditorState.preview_characters.contains(char_id),
        rx.cond(
            EditorState.preview_characters[char_id]["sprites"].contains(sprite_key),
            EditorState.preview_characters[char_id]["sprites"][sprite_key],
            "/placeholder.svg",
        ),
        "/placeholder.svg",
    )
    position_class = rx.match(
        char_sprite["position"],
        ("left", "bottom-0 left-[-5%] md:left-[5%]"),
        ("right", "bottom-0 right-[-5%] md:right-[5%]"),
        ("center", "bottom-0 left-1/2 -translate-x-1/2"),
        "bottom-0 left-1/2 -translate-x-1/2",
    )
    is_speaking = EditorState.current_preview_dialogue.is_not_none() & (
        EditorState.current_preview_dialogue["character"] == char_id
    )
    return rx.el.div(
        rx.image(
            src=sprite_src,
            class_name="h-[80vh] md:h-[95vh] object-contain transition-all duration-300 ease-in-out",
            style={
                "transform": rx.cond(is_speaking, "scale(1.05)", "scale(1)"),
                "filter": rx.cond(is_speaking, "brightness(1)", "brightness(0.8)"),
            },
            key=sprite_src,
        ),
        class_name=f"absolute transition-opacity duration-300 opacity-100 {position_class}",
    )


def editor() -> rx.Component:
    file_browser = rx.el.div(
        rx.el.h2(
            "Game Files", class_name="text-lg font-bold p-4 border-b border-gray-700"
        ),
        rx.el.div(
            rx.foreach(
                EditorState.files,
                lambda file: rx.el.button(
                    rx.icon("file-json-2", class_name="h-4 w-4 mr-2"),
                    file["name"],
                    on_click=lambda: EditorState.load_file(file["path"]),
                    class_name=rx.cond(
                        EditorState.current_file_path == file["path"],
                        "w-full text-left p-2 flex items-center bg-sky-500/20 text-sky-300 rounded-md",
                        "w-full text-left p-2 flex items-center hover:bg-white/10 rounded-md",
                    ),
                ),
            ),
            class_name="p-2 flex flex-col gap-1 overflow-y-auto",
        ),
        class_name="h-full bg-gray-900/80 border-r border-gray-700 flex flex-col",
    )
    json_editor = rx.el.div(
        rx.el.div(
            rx.el.div(
                rx.el.p(EditorState.current_file_path, class_name="font-mono text-sm"),
                rx.el.button(
                    rx.icon("save", class_name="h-4 w-4 mr-2"),
                    "Save",
                    on_click=EditorState.save_current_file,
                    class_name="flex items-center px-3 py-1 bg-green-600 hover:bg-green-700 rounded-md text-sm font-semibold",
                ),
                class_name="flex justify-between items-center p-2 border-b border-gray-700 bg-gray-800",
            ),
            monaco(
                value=EditorState.current_file_content,
                language="json",
                theme="vs-dark",
                on_change=EditorState.on_editor_change.debounce(300),
                options={"automaticLayout": True},
                height="100%",
            ),
            rx.cond(
                EditorState.editor_error != "",
                rx.el.div(
                    rx.el.p(
                        EditorState.editor_error,
                        class_name="font-mono text-sm text-red-400",
                    ),
                    class_name="absolute bottom-0 left-0 right-0 p-2 bg-red-900/80 backdrop-blur-sm",
                ),
                None,
            ),
            class_name="h-full relative",
        ),
        class_name="h-full bg-gray-800",
    )
    live_preview = rx.el.div(
        rx.el.h2(
            "Live Preview",
            class_name="text-lg font-bold p-4 text-center border-b border-gray-700 bg-gray-900",
        ),
        rx.el.div(
            rx.cond(
                EditorState.preview_scene.is_not_none(),
                rx.el.div(
                    rx.image(
                        src=EditorState.preview_scene["background"],
                        class_name="absolute inset-0 w-full h-full object-cover transition-opacity duration-500 ease-in-out",
                        key=EditorState.preview_scene["id"],
                    ),
                    rx.el.div(
                        class_name="absolute inset-0 bg-gradient-to-t from-black/50 to-transparent"
                    ),
                    rx.foreach(
                        EditorState.preview_scene["characters"],
                        editor_preview_character_sprite,
                    ),
                    rx.el.div(
                        rx.el.div(
                            rx.cond(
                                EditorState.preview_character_name != "Narrator",
                                rx.el.h2(
                                    EditorState.preview_character_name,
                                    class_name="font-bold text-xl mb-1",
                                    style={
                                        "color": EditorState.preview_character_color
                                    },
                                ),
                                None,
                            ),
                            rx.el.p(
                                rx.cond(
                                    EditorState.current_preview_dialogue.is_not_none(),
                                    EditorState.current_preview_dialogue["text"],
                                    "...",
                                ),
                                class_name="text-base text-gray-200 font-['Roboto']",
                                key=EditorState.current_preview_dialogue.to_string(),
                            ),
                            class_name="min-h-[80px]",
                        ),
                        rx.el.div(
                            rx.el.button(
                                rx.icon("arrow-left", class_name="h-5 w-5"),
                                on_click=EditorState.prev_preview_dialogue,
                                disabled=EditorState.dialogue_index <= 0,
                                class_name="p-2 bg-white/10 rounded-full hover:bg-white/20 transition-colors disabled:opacity-50",
                            ),
                            rx.el.button(
                                rx.icon("arrow-right", class_name="h-5 w-5"),
                                on_click=EditorState.next_preview_dialogue,
                                class_name="p-2 bg-white/10 rounded-full hover:bg-white/20 transition-colors",
                                disabled=EditorState.dialogue_index
                                >= EditorState.current_dialogue_length - 1,
                            ),
                            class_name="flex justify-end gap-2 mt-2",
                        ),
                        class_name="absolute bottom-4 left-4 right-4 bg-black/70 backdrop-blur-md p-4 rounded-xl border border-gray-700/50 shadow-lg",
                    ),
                    class_name="relative w-full h-full overflow-hidden bg-gray-900",
                    key=EditorState.preview_scene.to_string(),
                ),
                rx.el.div(
                    rx.el.div(
                        rx.icon("image-off", class_name="h-16 w-16 text-gray-500"),
                        rx.el.p(
                            "Edit a scene file to see a preview.",
                            class_name="text-gray-400 mt-4",
                        ),
                        class_name="flex flex-col items-center justify-center",
                    ),
                    class_name="flex items-center justify-center h-full bg-gray-800",
                ),
            ),
            class_name="flex-1 bg-gray-800",
        ),
        class_name="h-full bg-gray-900/50 flex flex-col",
    )
    return rx.el.main(
        rx.el.div(
            file_browser,
            json_editor,
            live_preview,
            class_name="grid grid-cols-[300px_1fr_1fr] min-h-screen min-w-screen text-white bg-gray-800",
        ),
        class_name="font-['Roboto']",
        on_mount=EditorState.on_load_editor,
    )


def context_menu_overlay() -> rx.Component:
    def action_button(action_id: str, angle: int) -> rx.Component:
        action = ActionState.actions[action_id]
        position_classes = {
            0: "top-0 -translate-y-1/2",
            60: "top-1/4 -translate-y-1/2 right-0 translate-x-1/2",
            120: "bottom-1/4 translate-y-1/2 right-0 translate-x-1/2",
            180: "bottom-0 translate-y-1/2",
            240: "bottom-1/4 translate-y-1/2 left-0 -translate-x-1/2",
            300: "top-1/4 -translate-y-1/2 left-0 -translate-x-1/2",
        }
        return rx.el.div(
            rx.el.button(
                rx.image(src=action["icon"], class_name="w-12 h-12 object-contain"),
                class_name="w-24 h-24 bg-sky-500/80 hover:bg-sky-400/90 transition-all duration-200 flex items-center justify-center",
                style={
                    "clipPath": "polygon(50% 0%, 100% 25%, 100% 75%, 50% 100%, 0% 75%, 0% 25%)"
                },
                on_click=lambda: ActionState.perform_action(action_id),
            ),
            rx.el.div(
                rx.el.p(action["name"], class_name="font-bold"),
                class_name="absolute bottom-full left-1/2 -translate-x-1/2 mb-2 p-2 bg-black/70 rounded-md text-center opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none w-32",
            ),
            class_name=f"absolute group {position_classes.get(angle, '')}",
        )

    return rx.el.div(
        rx.image(
            src=ActionState.location_background,
            class_name="absolute inset-0 w-full h-full object-cover opacity-30 blur-sm",
        ),
        rx.el.div(
            rx.el.h2(
                ActionState.location_name,
                class_name="text-5xl font-bold mb-4 text-center",
            ),
            rx.el.p(
                ActionState.location_description,
                class_name="text-lg text-gray-300 mb-12 text-center max-w-2xl",
            ),
            rx.el.div(
                rx.foreach(
                    ActionState.available_actions,
                    lambda action_id, index: action_button(action_id, index * 60),
                ),
                class_name="relative w-72 h-72",
            ),
            rx.el.div(
                rx.el.div(
                    rx.el.p("Current Time: ", class_name="font-semibold"),
                    rx.el.p(ActionState.current_time_str),
                    class_name="flex gap-2",
                ),
                rx.el.button(
                    "Return to Map",
                    on_click=lambda: GameState.set_game_mode("map"),
                    class_name="mt-4 px-6 py-2 bg-sky-500/50 hover:bg-sky-500/70 rounded-lg font-semibold",
                ),
                class_name="absolute bottom-10 flex flex-col items-center",
            ),
            class_name="relative w-full h-full flex flex-col items-center justify-center",
            on_mount=ActionState.on_load_context,
        ),
        class_name="absolute inset-0 bg-black/80 backdrop-blur-md flex items-center justify-center z-40",
    )


app = rxe.App(
    theme=rx.theme(appearance="light", accent_color="sky"),
    head_components=[
        rx.el.script(
            src="https://cdnjs.cloudflare.com/ajax/libs/html2canvas/1.4.1/html2canvas.min.js"
        ),
        rx.el.link(rel="preconnect", href="https://fonts.googleapis.com"),
        rx.el.link(rel="preconnect", href="https://fonts.gstatic.com", cross_origin=""),
        rx.el.link(
            href="https://fonts.googleapis.com/css2?family=Roboto:wght@400;500;700&display=swap",
            rel="stylesheet",
        ),
    ],
)
app.add_page(index)
app.add_page(editor, route="/editor")