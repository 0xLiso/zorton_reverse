import json
import traceback

from .graph_processor import GraphProcessor


class SceneDataLoader:
    """Cargador de datos de escenas desde archivo JSON"""

    def __init__(self, json_path):
        self.json_path = json_path
        self.scenes = []
        self.paths = []
        self.graph_processor = GraphProcessor()

    def load_scenes(self):
        try:
            with open(self.json_path, encoding="utf-8") as f:
                data = json.load(f)

            self.scenes = []
            self.paths = []

            if isinstance(data, dict) and "chunks" in data:
                for scene_data in data["chunks"]:
                    scene = self._process_graph_data(scene_data)
                    self.scenes.append(scene)

            print(
                f"Cargado grafo con {len(self.scenes)} escenas y {sum(len(s.get('graph_paths', [])) for s in self.scenes)} paths totales"
            )

            return self.scenes

        except Exception as e:
            print(f"Error cargando JSON: {e}")

            traceback.print_exc()
            return self._get_default_scenes()

    def _frame_val(self, field):
        """
        Extraer frame integer de ptr_frame_*

        - está en el tercer elemento de la lista
        - ejemplo:

            "ptr_frame_start": [
                "0x0004731c",
                "0x0000751c",
                "10548"
                ]
        """

        if not isinstance(field, list) or len(field) < 3:
            return None
        s = field[2]
        try:
            return int(s)
        except Exception:
            return None

    def _process_graph_data(self, scene_data):
        """Procesa el grafo y extrae todos los caminos válidos usando GraphProcessor"""
        scene = {
            "id": scene_data.get("id", 0),
            "offset": scene_data.get("mem_offset", scene_data.get("file_offset", "")),
            "graph_paths": [],
        }

        nodes = scene_data.get("nodes", [])
        if not nodes:
            return scene

        G, mem_map = self.graph_processor.build_graph(nodes)

        priority_root = scene_data.get("mem_offset")
        roots = self.graph_processor.find_roots(G, priority_root)

        all_paths = self.graph_processor.find_all_paths(G, roots)

        # convertir paths a estructura de datos usada
        # se mantienen los hitboxes pero la lista de frames ya no es necesaria
        for path in all_paths:
            path_data = self._convert_path_to_data(path, mem_map)
            if path_data:
                scene["graph_paths"].append(path_data)

        return scene

    def _convert_path_to_data(self, path, mem_map):
        """Convierte un camino de NetworkX a la estructura de datos esperada"""
        nodes_data = []

        for mem in path:
            if mem not in mem_map:
                continue

            node = mem_map[mem]
            val = node.get("value", {})

            hitbox_frame_start = self._frame_val(val.get("ptr_frame_hitbox_start"))
            hitbox_frame_end = self._frame_val(val.get("ptr_frame_hitbox_end"))

            ptr_node_respawn = val.get("ptr_node_respawn", "0x00000000")

            # extraer info del nodo
            step = {
                "mem": mem,
                "frame_start": self._frame_val(val.get("ptr_frame_start")),
                "frame_end": self._frame_val(val.get("ptr_frame_end")),
                "ptr_node_respawn": ptr_node_respawn
                if ptr_node_respawn != "0x00000000"
                else None,
                "hitboxes": [],
            }

            # extraer hitboxes
            # los frames vienen del nodo, no del hitbox, se pasan aquí
            # para facilitar la carga en el visualizador
            for item in val.get("lista_hitboxes", []):
                hb = item.get("hitbox", {})
                if hb:
                    step["hitboxes"].append(
                        {
                            "x0": hb.get("x0", 0),
                            "y0": hb.get("y0", 0),
                            "x1": hb.get("x1", 0),
                            "y1": hb.get("y1", 0),
                            "points": hb.get("score", 0),
                            "frame_start": hitbox_frame_start,
                            "frame_end": hitbox_frame_end,
                        }
                    )

            nodes_data.append(step)

        if not nodes_data:
            return None

        return {
            "nodes": nodes_data,
            "total_frames": sum(
                (s["frame_end"] or 0) - (s["frame_start"] or 0) + 1
                for s in nodes_data
                if s["frame_start"] is not None and s["frame_end"] is not None
            ),
            "total_hitboxes": sum(len(s["hitboxes"]) for s in nodes_data),
        }

    def get_paths(self, scene_index=0):
        """Retorna todos los caminos de una escena específica"""
        if scene_index < len(self.scenes):
            return self.scenes[scene_index].get("graph_paths", [])
        return []

    def get_path_node(self, scene_index, path_idx, node_idx):
        """Obtiene un nodo específico de un camino"""
        paths = self.get_paths(scene_index)
        if path_idx < len(paths):
            nodes = paths[path_idx]["nodes"]
            if node_idx < len(nodes):
                return nodes[node_idx]
        return None

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
