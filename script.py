from pathlib import Path
import getpass
import shutil
import tempfile
import urllib.request
import zipfile
import sys


MOD_ZIP_URL = "https://github.com/dejianh-cmu-F25/slaythespire2-mod-installer/raw/main/mods.zip"


def get_windows_username() -> str:
    return getpass.getuser()


def get_sts2_steam_folder() -> Path:
    username = get_windows_username()
    return Path(fr"C:\Users\{username}\AppData\Roaming\SlayTheSpire2\steam")


def list_steam_id_folders(steam_root: Path) -> list[Path]:
    if not steam_root.exists():
        raise FileNotFoundError(f"Steam folder not found: {steam_root}")

    folders = [p for p in steam_root.iterdir() if p.is_dir()]
    if not folders:
        raise FileNotFoundError(f"No Steam ID folders found in: {steam_root}")

    return sorted(folders, key=lambda p: p.name)


def choose_steam_id_folder() -> Path:
    steam_root = get_sts2_steam_folder()
    folders = list_steam_id_folders(steam_root)

    print("Available Steam ID folders:")
    for i, folder in enumerate(folders, start=1):
        print(f"{i}. {folder.name}")

    while True:
        choice = input("Select a Steam ID by number: ").strip()

        if not choice.isdigit():
            print("Please enter a valid number.")
            continue

        index = int(choice) - 1
        if 0 <= index < len(folders):
            return folders[index]

        print("Invalid selection. Try again.")


def copy_profile_to_modded(steam_id_folder: Path) -> None:
    source = steam_id_folder / "profile1"
    modded_root = steam_id_folder / "modded"
    destination = modded_root / "profile1"

    if not source.exists():
        raise FileNotFoundError(f"Source folder not found: {source}")

    modded_root.mkdir(exist_ok=True)
    shutil.copytree(source, destination, dirs_exist_ok=True)

    print("Copied profile1 to modded/profile1")
    print(f"From: {source}")
    print(f"To:   {destination}")


def find_steam_install_paths() -> list[Path]:
    possible_paths = [
        Path(r"C:\Program Files (x86)\Steam\steamapps\common\Slay the Spire 2"),
        Path(r"C:\Program Files\Steam\steamapps\common\Slay the Spire 2"),
    ]
    return [p for p in possible_paths if p.exists()]


def choose_game_install_folder() -> Path:
    found = find_steam_install_paths()

    if len(found) == 1:
        print(f"Found game folder: {found[0]}")
        return found[0]

    if len(found) > 1:
        print("Found multiple possible game folders:")
        for i, folder in enumerate(found, start=1):
            print(f"{i}. {folder}")

        while True:
            choice = input("Select the game folder by number: ").strip()
            if not choice.isdigit():
                print("Please enter a valid number.")
                continue

            index = int(choice) - 1
            if 0 <= index < len(found):
                return found[index]

            print("Invalid selection. Try again.")

    print("Could not automatically find the Slay the Spire 2 install folder.")
    manual_path = input(
        "Paste the full Slay the Spire 2 local files path here: "
    ).strip().strip('"')

    game_path = Path(manual_path)
    if not game_path.exists():
        raise FileNotFoundError(f"Game folder not found: {game_path}")

    return game_path


def download_file(url: str, destination: Path) -> None:
    print(f"Downloading mod zip from:\n{url}")
    urllib.request.urlretrieve(url, destination)
    print(f"Downloaded to: {destination}")


def extract_zip_to_folder(zip_path: Path, extract_to: Path) -> None:
    print(f"Extracting {zip_path} to {extract_to}")
    with zipfile.ZipFile(zip_path, "r") as zip_ref:
        zip_ref.extractall(extract_to)
    print("Extraction complete.")


def main() -> None:
    try:
        steam_id_folder = choose_steam_id_folder()
        copy_profile_to_modded(steam_id_folder)

        game_folder = choose_game_install_folder()

        with tempfile.TemporaryDirectory() as temp_dir:
            temp_dir_path = Path(temp_dir)
            zip_path = temp_dir_path / "mods.zip"

            download_file(MOD_ZIP_URL, zip_path)
            extract_zip_to_folder(zip_path, game_folder)

        print("\nMod installation files copied successfully.")
        print(f"Game folder: {game_folder}")
        print("You can now start the game.")

    except Exception as e:
        print(f"\nError: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()