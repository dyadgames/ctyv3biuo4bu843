# Visual Novel Game Data Documentation

Welcome to the documentation for the Reflex Visual Novel template. This guide explains how to create your own game content, including characters, scenes, and story branches, by editing and creating simple JSON files.

## 1. Folder Structure

All your game's content resides within the `assets/game_data/` directory. The engine expects a specific structure to find and load your assets correctly.


assets/
└── game_data/
    └── characters/      # Character definition files
    │   └── character_elara.json
    │   └── ...
    └── scenes/          # Scene files
        └── scene_001.json
        └── ...


- **`/characters`**: This folder contains JSON files, each defining a single character in your game. The filename is for organization, but the `id` inside the file is what the game engine uses.
- **`/scenes`**: This folder contains JSON files, each representing a single scene. The filename **must** match the `id` inside the file (e.g., `scene_001.json` for `"id": "scene_001"`).
- **Other Asset Folders**: You should place your background images and character sprites in a folder like `assets/backgrounds/` and `assets/sprites/` respectively (you'll need to create these). Then, reference them using their path from the `assets` directory, e.g., `/backgrounds/forest.png`.

## 2. JSON Data Formats

### Character JSON Format (`assets/game_data/characters/character_*.json`)

Each character file defines their identity, name color, and available sprite images.

**Schema:**

on
{
  "id": "string",
  "name": "string",
  "color": "string (hex color)",
  "sprites": {
    "sprite_key": "path/to/image.png",
    ...
  }
}


**Field Descriptions:**

- `id` (string, **required**): A unique identifier for the character. This is used in scene files to specify who is speaking or appearing on screen. Best practice is to use a simple, lowercase name (e.g., `"elara"`, `"kain"`). A special `"narrator"` ID is used for dialogue with no specific character speaking.
- `name` (string, **required**): The display name of the character shown in the dialogue box.
- `color` (string, **required**): The hex color code for the character's name in the UI (e.g., `"#3B82F6"`).
- `sprites` (object, **required**): A dictionary where keys are sprite identifiers (e.g., `"neutral"`, `"happy"`) and values are the paths to the corresponding image files. The path should be relative to the root of your project's `assets` folder (e.g., `"/sprites/elara/happy.png"`).

**Example (`character_elara.json`):**

on
{
  "id": "elara",
  "name": "Elara",
  "color": "#3B82F6",
  "sprites": {
    "neutral": "/sprites/elara/neutral.png",
    "happy": "/sprites/elara/happy.png",
    "sad": "/sprites/elara/sad.png"
  }
}


### Scene JSON Format (`assets/game_data/scenes/scene_*.json`)

Each scene file defines a segment of your story, including the background, characters present, dialogue, and player choices.

**Schema:**

on
{
  "id": "string",
  "background": "path/to/image.png",
  "characters": [
    {
      "id": "string",
      "position": "string ('left', 'center', 'right')",
      "sprite": "string"
    }
  ],
  "dialogue": [
    {
      "character": "string",
      "text": "string"
    }
  ],
  "choices": [
    {
      "text": "string",
      "nextScene": "string",
      "set_vars": {
        "variable_name": "value"
      }
    }
  ],
  "nextScene": "string | null"
}


**Field Descriptions:**

- `id` (string, **required**): A unique identifier for the scene. The filename **must** match this ID (e.g., `scene_001.json`).
- `background` (string, **required**): The path to the background image for this scene, relative to the `assets` folder.
- `characters` (array of objects, **required**): A list of characters that are visible in this scene. Each object has:
    - `id` (string): The ID of the character (must match an ID from a character file).
    - `position` (string): The on-screen position (`"left"`, `"center"`, or `"right"`).
    - `sprite` (string): The key of the sprite to display (must match a key in the character's `sprites` object).
- `dialogue` (array of objects, **required**): A sequence of dialogue lines that make up the scene. Each object has:
    - `character` (string): The ID of the speaking character. Use `"narrator"` for narration.
    - `text` (string): The dialogue text to display.
- `choices` (array of objects, **optional**): A list of choices presented to the player at the **end** of the dialogue sequence. If this field is present, `nextScene` should usually be `null`. Each choice object has:
    - `text` (string): The text displayed on the choice button.
    - `nextScene` (string): The `id` of the scene to transition to if this choice is selected.
    - `set_vars` (object, optional): A dictionary of game variables to set when this choice is made. This is useful for tracking player decisions (e.g., `{"ally": "elara"}`).
- `nextScene` (string or `null`, **optional**): The `id` of the scene to automatically transition to after the dialogue finishes. This is used for linear scenes without choices. If `choices` are present, this should be `null`.

## 3. How to Create New Content

### Step 1: Create a New Character
1.  Create a new file, e.g., `character_liam.json`, in `assets/game_data/characters/`.
2.  Add your character's sprites to an appropriate asset folder, e.g., `assets/sprites/liam/`.
3.  Fill out the JSON file with the character's details, referencing the sprite paths.

    on
    {
      "id": "liam",
      "name": "Liam",
      "color": "#10B981",
      "sprites": {
        "default": "/sprites/liam/default.png"
      }
    }
    

### Step 2: Create a New Scene
1.  Create a new file, e.g., `scene_008.json`, in `assets/game_data/scenes/`.
2.  Ensure you have a background image ready in your assets folder.
3.  Define the scene in the JSON file. You can now use the `"liam"` character ID you created.

    on
    {
      "id": "scene_008",
      "background": "/backgrounds/tavern.jpg",
      "characters": [
        { "id": "liam", "position": "center", "sprite": "default" }
      ],
      "dialogue": [
        { "character": "liam", "text": "Welcome to my tavern, traveler." },
        { "character": "narrator", "text": "The tavern is warm and inviting." }
      ],
      "choices": [],
      "nextScene": "scene_009"
    }
    

### Step 3: Link Scenes Together
To create a story, link scenes using the `nextScene` property for linear progression or the `choices` array for branching paths. For example, to make a scene lead to `scene_008`, you would set its `nextScene` to `"scene_008"` or add it as a choice.

## 4. How the Data Flows

1.  **Game Start**: The game loads the initial scene specified in the `GameState` (default is `"scene_001"`). It also pre-loads all character data from the `assets/game_data/characters/` directory.
2.  **Scene Load**: The engine reads the current scene's JSON file (e.g., `scene_001.json`).
3.  **Rendering**: The `background` image is displayed. The characters listed in the `characters` array are rendered on screen at their specified `position` using their specified `sprite`.
4.  **Dialogue Progression**: The game steps through the `dialogue` array one by one. For each line, it finds the character's `name` and `color` using the `character` ID and displays the `text`.
5.  **Scene End**: 
    - If `nextScene` has a value, the game automatically loads the specified scene.
    - If the `choices` array is not empty, the dialogue pauses and buttons for each choice are displayed to the player.
6.  **Player Choice**: When the player clicks a choice, the engine reads the `nextScene` from that choice object, sets any variables in `set_vars`, and loads the new scene. The story continues.
