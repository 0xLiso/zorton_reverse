import networkx as nx


class GraphProcessor:
    """Procesador de grafos de secuencias de animación usando NetworkX"""

    TERMINATION_ADDRESSES = ["0x00000000"]

    def __init__(self):
        pass

    def build_graph(self, nodes):
        """
        Construye un grafo dirigido a partir de nodos de escena.

        Args:
            nodes: Lista de nodos con mem_offset y sequences

        Returns:
            tuple: (DiGraph, dict) - Grafo de NetworkX y mapa mem_offset -> nodo
        """
        G = nx.DiGraph()
        mem_map = {n.get("mem_offset"): n for n in nodes if "mem_offset" in n}

        for n in nodes:
            mem = n.get("mem_offset")
            if not mem:
                continue

            G.add_node(mem, data=n)
            v = n.get("value", {})
            seqs = v.get("sequences", []) or []
            for s in seqs:
                if s and s not in self.TERMINATION_ADDRESSES:
                    G.add_edge(mem, s)

        return G, mem_map

    def find_roots(self, G, priority_root=None):
        """
        Encuentra nodos raíz (sin predecesores) en el grafo.

        Args:
            G: Grafo de NetworkX
            priority_root: Nodo que debe ser raíz prioritaria si existe

        Returns:
            list: Lista de nodos raíz
        """
        roots = [n for n in G.nodes() if G.in_degree(n) == 0]

        if priority_root and priority_root in G and priority_root not in roots:
            roots.insert(0, priority_root)

        # Si no hay raíces, usar el primer nodo
        if not roots and G.nodes():
            roots = [list(G.nodes())[0]]

        return roots

    def find_all_paths(self, G, roots, max_depth=50):
        """
        Encuentra todos los caminos simples desde las raíces hasta las hojas:
        - Si no hay hojas, el grafo podría tener ciclos o ser un solo nodo
        - TODO: Ignorar grafos con un solo nodo¿?

        Args:
            G: Grafo de NetworkX
            roots: Lista de nodos raíz
            max_depth: Profundidad máxima de búsqueda

        Returns:
            list: Lista de caminos (cada camino es una lista de mem_offsets)
        """
        all_paths = []
        leaf_nodes = [n for n in G.nodes() if G.out_degree(n) == 0]

        for root in roots:
            if root not in G:
                continue

            if not leaf_nodes:
                all_paths.append([root])
            else:
                for leaf in leaf_nodes:
                    # NetworkX encuentra todos los caminos simples (sin ciclos)
                    try:
                        for path in nx.all_simple_paths(
                            G, root, leaf, cutoff=max_depth
                        ):
                            all_paths.append(path)
                    except nx.NetworkXNoPath:
                        continue

        return all_paths

    def get_graph_stats(self, G):
        """
        Obtiene estadísticas del grafo.

        Args:
            G: Grafo de NetworkX

        Returns:
            dict: Diccionario con estadísticas
        """
        return {
            "num_nodes": G.number_of_nodes(),
            "num_edges": G.number_of_edges(),
            "is_dag": nx.is_directed_acyclic_graph(G),
            "num_cycles": (
                len(list(nx.simple_cycles(G)))
                if not nx.is_directed_acyclic_graph(G)
                else 0
            ),
        }


def main():
    import json
    import sys
    from pathlib import Path

    JSON_FILE = "Zorton_brothes_v1.01.json"

    json_path = Path(__file__).parent.parent.parent / JSON_FILE

    if not json_path.exists():
        print(f"Error: No se encuentra el archivo {json_path}")
        sys.exit(1)

    print(f"Cargando {json_path.name}...")

    with open(json_path, encoding="utf-8") as f:
        data = json.load(f)

    processor = GraphProcessor()

    if not isinstance(data, dict) or "chunks" not in data:
        print("Error: Formato de JSON no válido")
        sys.exit(1)

    chunks = data["chunks"]
    print(f"Total de chunks/escenas: {len(chunks)}", end="\n\n")

    total_paths = 0

    for i, chunk in enumerate(chunks):
        nodes = chunk.get("nodes", [])
        if not nodes:
            print(f"Chunk {i}: Sin nodos")
            continue

        G, mem_map = processor.build_graph(nodes)
        stats = processor.get_graph_stats(G)
        priority_root = chunk.get("mem_offset")
        roots = processor.find_roots(G, priority_root)
        paths = processor.find_all_paths(G, roots)
        total_paths += len(paths)

        print(f"Chunk {i} (offset: {chunk.get('mem_offset', 'N/A')})")
        print(f"  Nodos: {stats['num_nodes']}, Aristas: {stats['num_edges']}")
        print(f"  Es DAG: {stats['is_dag']}, Ciclos: {stats['num_cycles']}")
        print(
            f"  Raíces: {len(roots)}, Hojas: {len([n for n in G.nodes() if G.out_degree(n) == 0])}"
        )
        print(f"  Paths encontrados: {len(paths)}")

        # paths de ejemplo
        if paths and len(paths) <= 3:
            for j, path in enumerate(paths[:3]):
                print(f"    path {j + 1}: {' -> '.join([str(p)[-8:] for p in path])}")
        elif len(paths) > 3:
            print(f"    Primer path: {' -> '.join([str(p)[-8:] for p in paths[0]])}")
            print(f"    (... {len(paths) - 1} paths más)")
        print()

    print(f"{'=' * 60}")
    print(f"Total de paths en todas las escenas: {total_paths}")
    print(f"{'=' * 60}")


if __name__ == "__main__":
    main()
