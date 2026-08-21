# BlenderArchipelago

## What is this?

A [Blender](https://www.blender.org) add-on for [Archipelago](https://archipelago.gg), a multiworld, multi-game randomizer.

Let's say I'm playing Blender, and my friend is playing Ocarina of Time. When I create a render that is similar enough to a target image, I find my friend's Hookshot, allowing them to reach several OoT chests they couldn't before. In one of those chests they find my Edit Mode, allowing me to make better models. I create a more similar-looking render to a target image, and find my friend's Ocarina. This continues until we both find enough of our items to finish our games.

## What does randomization do to this game?
Creating simple objects and lights in object mode is one of the only things you can do at first because the other modes, shaders, and modifiers are locked.

Render region size is restricted and will only expand when the Progressive Render Width and Progressive Render Height items are obtained.

Items are found based on similarity to a target image, measured as a percentage. Every threshold, spaced at equal intervals up
to a maximum set in the game options will send an item, and the game will be considered done when a certain target
percentage (set in the game options) is reached.

If deathlink is enabled, when you undo/redo, everyone with deathlink dies. When someone with deathlink dies, you will undo to the furthest undo in history. Blender's default setting is 32 undos max in history.
(Setting is in `Edit > Preferences > System > Memory & Limits > Undo Steps`)

# Installation

### Prerequisites

- Make sure you have Blender 4.2.0 or above installed (Any version lower is not guaranteed to work.)
- Install Archipelago from [Archipelago's Github Releases page](https://github.com/ArchipelagoMW/Archipelago/releases). On that page, scroll down to the `Assets` section for the release you want, click on the appropriate installer for your system to start downloading it (for most Windows users, that will be the file called `Setup.Archipelago.X.Y.Z.exe`), then run it.
  - The `Archipelago` folder can be found by opening the Archipelago Launcher and selecting `Browse Files`.
- Go to the [Releases page](https://github.com/GBFound/BlenderArchipelago/releases) of this repository and look at the latest release. Download `BlenderArchipelago.zip` and `blender.apworld`.

### Creating a `.yaml` file.

1. Install `blender.apworld`, either by double clicking the `.apworld` file, opening the Archipelago Launcher and selecting `Install APWorld`, or adding it to `Archipelago\custom_worlds`.
2. To create a `.yaml` file, select `Options Creator` in the Archipelago Launcher. You can then customize all of the options for Blender, and then save the `.yaml` file.
   - Alternatively, if you would prefer to manually edit the `.yaml` file in a text editor, you can select `Generate Template Options` instead.

### Generating a multiworld.

Only one player in the multiworld will need to generate. If the player who is generating is not yourself, they will also need to install the `.apworld` for Blender.
You can have multiple worlds of the same game (each with different options), as well as several different games, as long as each `.yaml` file has a unique player/slot name. It also doesn't matter who plays which game; it's common for one human player to play more than one game in a multiworld.

1. Place all `.yaml` files in `Archipelago\Players`.
2. Open the Archipelago Launcher and select `Generate`. You should see a console window appear and then disappear after a few seconds.
3. In `Archipelago\output` there should now be a file with a name like `AP_95887452552422108902.zip`.
4. Open https://archipelago.gg/uploads in your favorite web browser, and upload the output .zip you just generated. Click `Create New Room`.
5. The room page should give you a hostname and port number to connect to, e.g. "archipelago.gg:12345".

### Using the add-on in Blender.

- Open Blender and select `Edit > Preferences > Add-Ons`. Open `Install from Disk` and select `BlenderArchipelago.zip`.
- Now in `View 3D > Sidebar > Blender AP`, and you will be asked for connection info such as the host and port. Unless you edited `blender.yaml` (or used multiple `.yaml`s), your slot/player name will be "Blenderer". And by default, archipelago.gg rooms have no password.
