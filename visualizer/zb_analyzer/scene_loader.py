import json
import traceback
from itertools import chain

class SceneDataLoader:
    """Cargador de datos de escenas desde archivo JSON"""

    def __init__(self, json_path="zb.json"):
        self.json_path = json_path
        self.scenes = []

    def load_scenes(self):
        try:
            with open(self.json_path, encoding="utf-8") as f:
                data = json.load(f)

            self.scenes = []
            for scene_data in data:
                scene = self._process_scene_data(scene_data)
                self.scenes.append(scene)

            print(f"Cargadas {len(self.scenes)} escenas del archivo JSON")
            return self.scenes

        except Exception as e:
            print(f"Error cargando JSON: {e}")

            traceback.print_exc()
            return self._get_default_scenes()

    def _process_scene_data_v0(self, scene_data):
        scene = {
            "id": scene_data.get("id", 0),
            "offset": scene_data.get("offset", ""),
            "hitboxes": [],
            "frames": [],
        }

        if "hitboxes" in scene_data:
            for hitbox in scene_data["hitboxes"]:
                rect = hitbox.get("rect", {})
                scene["hitboxes"].append(
                    {
                        "x0": rect.get("x0", 0),
                        "y0": rect.get("y0", 0),
                        "x1": rect.get("x1", 0),
                        "y1": rect.get("y1", 0),
                        "points": hitbox.get("points", 500),
                    }
                )

        if "frames" in scene_data:
            for frame in scene_data["frames"]:
                scene["frames"].append(
                    {"from": frame.get("from", 0), "to": frame.get("to", 0)}
                )

        return scene
    
    def _process_scene_data(self, scene_data):
        scene = {
            "id": scene_data.get("id", 0),
            "offset": scene_data.get("file_offset", ""),
            "hitboxes": [],
            "frames": [],
        }

        hitboxes_bad = [ x["value"]["ptr_hitbox"] for x in scene_data["nodes"] if len(x["value"]["ptr_hitbox"])>0 ]
        hitboxes = list(chain.from_iterable(hitboxes_bad))
        for hit in hitboxes:
            rect = hit["hitbox"]
            scene["hitboxes"].append(
                {
                    "x0": rect.get("x0", -1),
                    "y0": rect.get("y0", -1),
                    "x1": rect.get("x1", -1),
                    "y1": rect.get("y1", -1),
                    "points": rect.get("score", -1),
                }
            )

        if "frames" in scene_data:
            lst_frames = [x["frame"] for x in scene_data["frames"]]
            
            lst_pairs = [  (lst_frames[i],lst_frames[i+1]) for i in range(0,len(lst_frames)-1,2) ]
            for frame in lst_pairs:
                scene["frames"].append(
                    {"from": int(frame[0]), "to": int(frame[1])}
                )

        return scene

    def _get_default_scenes(self):
        """datos de ejemplo si falla la carga"""
        return [
            {
                "id": 0,
                "offset": "0x0000",
                "hitboxes": [
                    {"x0": 54, "y0": 34, "x1": 122, "y1": 73, "points": 500},
                    {"x0": 176, "y0": 35, "x1": 243, "y1": 78, "points": 500},
                ],
                "frames": [{"from": 10821, "to": 13405}, {"from": 10363, "to": 10427}],
            }
        ]

    def get_scenes(self):
        return self.scenes
