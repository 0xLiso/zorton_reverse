import json
import os
from pathlib import Path


class ConfigManager:
    """Gestiona la configuración de la aplicación"""

    def __init__(self, config_file="config.json"):
        self.config_file = config_file
        self.config = self._load_config()

    def _load_config(self):
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError) as e:
                print(f"Error al cargar configuración: {e}")
                return self._get_default_config()
        return self._get_default_config()

    def _get_default_config(self):
        return {
            "last_video_path": "",
            "last_json_path": "",
            "last_video_directory": str(Path.home()),
            "last_json_directory": str(Path.home()),
        }

    def save_config(self):
        try:
            with open(self.config_file, "w", encoding="utf-8") as f:
                json.dump(self.config, f, indent=4, ensure_ascii=False)
        except IOError as e:
            print(f"Error al guardar configuración: {e}")

    def get_last_video_path(self):
        return self.config.get("last_video_path", "")

    def get_last_json_path(self):
        return self.config.get("last_json_path", "")

    def get_last_video_directory(self):
        return self.config.get("last_video_directory", str(Path.home()))

    def get_last_json_directory(self):
        return self.config.get("last_json_directory", str(Path.home()))

    def set_last_video_path(self, path):
        self.config["last_video_path"] = path
        if path:
            self.config["last_video_directory"] = str(Path(path).parent)

    def set_last_json_path(self, path):
        self.config["last_json_path"] = path
        if path:
            self.config["last_json_directory"] = str(Path(path).parent)

    def set_paths(self, video_path, json_path):
        self.set_last_video_path(video_path)
        self.set_last_json_path(json_path)
        self.save_config()
