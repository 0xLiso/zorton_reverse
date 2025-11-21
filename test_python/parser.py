"""
Parser para archivos binarios de Amiga 500 (Motorola 68000)
Analiza estructuras tree_logic_node y hitbox según zorton_structs.h
"""

import struct
import json
import sys
import re
from typing import List, Dict, Tuple, Optional


# Constantes
MEMORY_OFFSET = 0x3FE00  # Offset de memoria para los punteros
FRAME_PATTERN = rb'^\d{5}\x00$'  # Patrón para frames: 5 dígitos + null terminator
FRAME_SIZE = 6  # 5 caracteres + \0



class HitboxStruct:
    """Representa la estructura hitbox del archivo zorton_structs.h"""
    SIZE = 24  # 6 * 4 bytes

    def __init__(self, data: bytes, file_offset: int):
        """
        Parsea una estructura hitbox desde bytes

        Args:
            data: bytes conteniendo la estructura hitbox
            file_offset: posición en el archivo
        """
        # Big-endian (Motorola 68000): >
        # 4 ints (y0, y1, x0, x1), 4 bytes undefined, 1 int (score)
        unpacked = struct.unpack('>iiiiii', data[:self.SIZE])

        self.y0 = unpacked[0]
        self.y1 = unpacked[1]
        self.x0 = unpacked[2]
        self.x1 = unpacked[3]
        self.ptr_next_hitbox =unpacked[4]
        self.score = unpacked[5]
        self.file_offset = file_offset
        self.mem_offset = file_offset + MEMORY_OFFSET
    
    def to_dict(self) -> Dict:
        """Convierte la estructura a diccionario para JSON"""
        return {
            'file_offset': f'0x{self.file_offset:08x}',
            'mem_offset': f'0x{self.mem_offset:08x}',
            'hitbox': {
                'y0': self.y0,
                'y1': self.y1,
                'x0': self.x0,
                'x1': self.x1,
                'ptr_next_hitbox': f'0x{self.ptr_next_hitbox:08x}',
                'score': self.score
            }
        }
        
    

class TreeLogicNode:
    """Representa la estructura tree_logic_node con DATO inicial"""
    SIZE = int(0x2A)  # 30 bytes
    hitbox_struct = []
    lista_nodes = []
    num_sequences = 0
    is_death_and_destruction = False
    ptr_hitbox = 0x0

    def __init__(self, data: bytes, file_offset: int ):
        """
        Parsea una estructura tree_logic_node desde bytes

        Args:
            data: file in bytes
            file_offset: posición en el archivo
        """
        self.hitbox_struct = []
        self.lista_nodes = []
        self.num_sequences = 0
        self.is_death_and_destruction = False
        self.ptr_hitbox = 0x0
        
        self.file_offset = file_offset
        self.mem_offset = file_offset + MEMORY_OFFSET
        self.ptr_node_respawn=0x0
        
        if file_offset== 0xc9d2 or (file_offset+MEMORY_OFFSET)==0x4c7d2:
            self.is_death_and_destruction = True
            return
        start_pos = data[file_offset:]
        
        # Big-endian: 10 pointers + 10 undefined bytes + 1 int + 2 pointers
        unpacked = struct.unpack('>7I6BII', start_pos[:self.SIZE])

        self.ptr_frame_start = unpacked[0]
        self.ptr_frame_end = unpacked[1]
        self.ptr_frame_hitbox_start = unpacked[2]
        self.ptr_frame_hitbox_end = unpacked[3]
        self.ptr_hitbox = unpacked[4]
        self.ptr_frame_unk = unpacked[5]
        self.ptr_node_respawn = unpacked[6]
        
        self.fields = list(unpacked[7:9])
        self.type_a = unpacked[9]
        self.type_b = unpacked[10]
        self.num_sequences = unpacked[11]
        self.type_d = unpacked[12]
        self.ptr_fn_callback = unpacked[13]
        self.ptr_list_sequences = unpacked[14]

       

        
        if self.ptr_list_sequences!=0x0 and self.num_sequences!=0:
            seq_init = self.ptr_list_sequences-MEMORY_OFFSET
            
            unpacked = struct.unpack(f'>{self.num_sequences}I', data[seq_init:seq_init+4*self.num_sequences])
            for p in unpacked:
                self.lista_nodes.append(p)
           
            

    def to_dict(self, frames_map: Dict[int, str]) -> Dict:
        """Convierte la estructura a diccionario para JSON"""
        if self.is_death_and_destruction:
            result = {
            'type': "death_and_destruction☠️",
            'mem_offset': f'0x{self.mem_offset:08x}',
            'file_offset': f'0x{self.file_offset:08x}',
            'value': {"death":"destruction"}
            }
        else: 
            result = {
                'type': 'tree_logic_node' if not self.is_death_and_destruction else "death_and_destruction☠️",
                'mem_offset': f'0x{self.mem_offset:08x}',
                'file_offset': f'0x{self.file_offset:08x}',
                'value': {
                    'ptr_frame_start':  self._format_frame_ptr(self.ptr_frame_start, frames_map),
                    'ptr_frame_end':  self._format_frame_ptr(self.ptr_frame_end, frames_map),
                    'ptr_frame_hitbox_start':  self._format_frame_ptr(self.ptr_frame_hitbox_start, frames_map),
                    'ptr_frame_hitbox_end':  self._format_frame_ptr(self.ptr_frame_hitbox_end, frames_map),
                    'ptr_hitbox':  f'0x{self.ptr_hitbox:08x}',
                    'ptr_frame_unk':  self._format_frame_ptr(self.ptr_frame_unk, frames_map),
                    'ptr_node_respawn':f'0x{self.ptr_node_respawn:08x}',
                    'fields': [hex(b) for b in self.fields],
                    'type_a': self.type_a,
                    'type_b': self.type_b,
                    'num_sequences': self.num_sequences,
                    'type_d': self.type_d,      
                    'ptr_fn_callback': f'0x{self.ptr_fn_callback:08x}',
                    'lista_hitboxes': [x.to_dict() for x in self.hitbox_struct],
                    
                    'sequences': [ f'0x{p:08x}' for p in self.lista_nodes]
                    
                }
            }
        return result

    def _format_frame_ptr(self, mem_ptr: int, frames_map: Dict[int, str]) -> Tuple[str, str,str]:
        """Formatea un puntero a frame con su valor"""
        if mem_ptr==0x0:
            return (f'0x{mem_ptr:08x}', "","-----")
        ptr = mem_ptr - MEMORY_OFFSET
        for x in frames_map:
            if x[0]==ptr:
                return (f'0x{mem_ptr:08x}', f'0x{ptr:08x}', x[1])
        return (f'0x{mem_ptr:08x}',f'0x{ptr:08x}', "-----")


def find_frame_sequences(data: bytes) -> List[Tuple[int, str]]:
    """
    Encuentra todas las secuencias de frames (5 dígitos ASCII + null terminator)

    Args:
        data: datos binarios completos

    Returns:
        Lista de tuplas (offset, frame_string)
    """
    frames = []
    sframes=[] 
    ssize = 0
    i = 0
    n = 0 

    while i < len(data) - FRAME_SIZE:
        # Buscar patrón de frame: 5 dígitos + \0
        chunk = data[i:i+FRAME_SIZE]
        if (len(chunk) == FRAME_SIZE and
            chunk[5] == 0 and
            all(48 <= chunk[j] <= 57 for j in range(5))):
            frame_str = chunk[:5].decode('ascii')
            sframes.append((i, frame_str))
            i += FRAME_SIZE
            ssize += FRAME_SIZE
            n += 1
        else:
            if n>=2:
                frames.append(sframes)
            else:
                i -= ssize    
            sframes=[]
            ssize = 0    
            n =0 
            i += 1
            

    return frames





def detect_chunks(data: bytes, frames: List[Tuple[int, str]]) -> List[Dict]:
    """
    Detecta chunks de datos basándose en secuencias de frames

    Args:
        data: datos binarios completos
        frames: lista de frames encontrados

    Returns:
        Lista de chunks con su información
    """
    
    
    #TODO: en posicion 0x7d42 a 0x7d78 hay una estructura distinta que tiene 54 bytes , hay que arreglar esto.
    #para probar poner un breakpoint condicional en offset==32166
    
    
    if not frames:
        return []

    chunks = []
    current_chunk_frames = []
    last_offset = -1
    offset = frames[0][0]
    
    offset_nodes = [offset-TreeLogicNode.SIZE]

    while len(offset_nodes)>0:
        chunk_start = offset_nodes.pop() 
        new_struct = TreeLogicNode(data,chunk_start)
        for p in new_struct.lista_nodes:
            if p==0:
                print("WAT")
                continue
            offset_nodes.insert(0,p- MEMORY_OFFSET)
            
        if new_struct.ptr_node_respawn!=0x0:
            offset_nodes.insert(0,new_struct.ptr_node_respawn- MEMORY_OFFSET)
        
        
        if new_struct.ptr_hitbox !=0:
            hitbox_file_offset = new_struct.ptr_hitbox - MEMORY_OFFSET
            if 0 <= hitbox_file_offset < len(data) - HitboxStruct.SIZE:
                try:
                    new_hitbox= HitboxStruct(
                        data[hitbox_file_offset:],
                        hitbox_file_offset
                    )
                    new_struct.hitbox_struct.append(new_hitbox)
                    #buscar hitbox linked list
                    while new_hitbox.ptr_next_hitbox !=0:
                        next_hitbox_file_offset = new_hitbox.ptr_next_hitbox - MEMORY_OFFSET
                        if 0 <= next_hitbox_file_offset < len(data) - HitboxStruct.SIZE:
                            new_hitbox= HitboxStruct(
                                data[next_hitbox_file_offset:],
                                next_hitbox_file_offset
                            )
                            new_struct.hitbox_struct.append(new_hitbox)
                        else:
                            raise ValueError("Error al parsear hitbox linked list")
                except:
                    raise ValueError("Error al parsear hitbox")
        
        chunks.append({
                    'start': chunk_start,
                    "data_struct": new_struct                   
                    
                })
      
           

    return chunks



def parse_binary(binary_path: str) -> Dict :
    """
    Parsea el archivo binario completo y extrae todos los chunks

    Args:
        binary_path: ruta al archivo binario

    Returns:
        Lista de chunks parseados
    """
    try:
        with open(binary_path, 'rb') as f:
            data = f.read()
    except FileNotFoundError:
        print(f"Error: No se encontró el archivo {binary_path}")
        sys.exit(1)
    except Exception as e:
        print(f"Error al leer el archivo: {e}")
        sys.exit(1)

    print(f"Leyendo archivo binario: {binary_path} ({len(data)} bytes)")

    # Encontrar todos los frames
    print("Buscando frames...")
    frames = find_frame_sequences(data)
    print(f"Encontrados {len(frames)} frames")

    # Detectar chunks
    print("Detectando chunks de datos...")
    full_chunks = []
    chunk_id = 0
    result = []
    list_chunks = []
    list_frames = []
    for frame in frames:
        print(f"Frame en offset 0x{frame[0][0]:08x}: {frame[0][1]}")
        chunks = detect_chunks(data, frame)
        print(f"Detectados {len(chunks)} chunks")

    
        # Crear diccionario de chunk
        chunk_dict = {
            'id': chunk_id,
            'file_offset': f"0x{chunks[-1]['start']:08x}",
            'mem_offset': f"0x{(chunks[-1]['start'] + MEMORY_OFFSET):08x}",
            'frames': [{"file_offset":f"0x{f[0]:08x}","mem_offset":f"0x{(f[0]+ MEMORY_OFFSET):08x}", "frame":f"{f[1]}"} for f in frame],
            'nodes': [p['data_struct'].to_dict(frame) for p in chunks]
        }
        chunk_id += 1
        for p in chunks:
            list_chunks.append(p['data_struct'].mem_offset)
        for f in frame:
            list_frames.append(f)
        result.append(chunk_dict)
        
    # read full list of scenes
    # 0x0c4daa -> inicio de la lista a escenas.   44 ptrs
    init_list_scenes = int(0x0c4daa - MEMORY_OFFSET )&0x0000ffff
    buf = data[init_list_scenes:init_list_scenes+(44*4)]
    unpacked = struct.unpack('>44I', buf)
    scenes = [ p for p in unpacked]
    spare = []
    to_add = [ p for p in unpacked]
    # we need to fine tune this parse. We should read the list of sequences related and the hitboxes. 
    # I did not implement it to speed up the json creation, and also 
    # the num_sequences seems to be always 0.
    while len(to_add)>0:
        p = to_add.pop()
        if p not in list_chunks:
            init_pos = p - MEMORY_OFFSET
            new_struct = TreeLogicNode(data,init_pos)
            spare.append(new_struct.to_dict(list_frames))
            

    return {"scene_order":[f"0x{p:08x}" for p in scenes], "chunks":result, "spare_chunks":spare }


def main():
    """Función principal"""
    

    # Parsear el binario
    chunks = parse_binary("bin_data/picmatic_zb_v1.01_combined.bin")

    # Escribir resultado a JSON
    output_path = 'output.json'
    print(f"\nEscribiendo resultado a {output_path}...")

    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(chunks, f, indent=2, ensure_ascii=False)
        print(f"✓ Parseo completado exitosamente")
        print(f"  - Chunks procesados: {len(chunks)}")
        print(f"  - Salida: {output_path}")
    except Exception as e:
        print(f"Error al escribir el archivo de salida: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()


# 0x0c4daa -> inicio de la lista a escenas.   44 ptrs