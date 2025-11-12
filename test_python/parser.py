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




class HeaderChunkStruct:
    """Representa la estructura header chunk del archivo zorton_structs.h"""
    SIZE = 42  #0x2A 

    def __init__(self, data: bytes, file_offset: int):
        """
        Parsea una estructura header chunk desde bytes

        Args:
            data: bytes conteniendo la estructura header chunk
            file_offset: posición en el archivo
        """
        # Big-endian (Motorola 68000): >
        # 4 ints (y0, y1, x0, x1), 4 bytes undefined, 1 int (score)
        unpacked = struct.unpack('>iiiiiiii6si', data[:self.SIZE])

        self.ptr_frame_init = unpacked[0]
        self.ptr_frame_end = unpacked[1]
        self.ptr_frame_ko_init = unpacked[2]
        self.ptr_frame_ko_end = unpacked[3]
        self.ptr_unk1 =unpacked[4]
        self.ptr_unk2 =unpacked[5]
        self.ptr_unk3 =unpacked[6]
        self.ptr_unk4 =unpacked[7]
        self.fields = unpacked[8]
        self.ptr_callback = unpacked[9]
        
        self.file_offset = file_offset
        self.mem_offset = file_offset + MEMORY_OFFSET

    def to_dict(self, frames_map: Dict[int, str]) -> Dict:
        """Convierte la estructura a diccionario para JSON"""
        return {
            'type': 'header_chunk',
            'file_offset': f'0x{self.file_offset:08x}',
            'mem_offset': f'0x{self.mem_offset:08x}',
            'value': {
                'ptr_frame_init':  self._format_frame_ptr(self.ptr_frame_init, frames_map),
                'ptr_frame_end': self._format_frame_ptr(self.ptr_frame_end, frames_map),
                'ptr_frame_ko_init': self._format_frame_ptr(self.ptr_frame_ko_init, frames_map),
                'ptr_frame_ko_end':self._format_frame_ptr(self.ptr_frame_ko_end, frames_map),
                'ptr_unk1':  f'0x{self.ptr_unk1:08x}',
                'ptr_unk2': f'0x{self.ptr_unk2:08x}',
                'ptr_unk3':  f'0x{self.ptr_unk3:08x}',
                'ptr_unk4':  f'0x{self.ptr_unk4:08x}',
                'fields': [hex(b) for b in self.fields],
                'ptr_callback':  f'0x{self.ptr_callback:08x}'
            }
        }
        
    def _format_frame_ptr(self, mem_ptr: int, frames_map: Dict[int, str]) -> Tuple[str, str]:
        """Formatea un puntero a frame con su valor"""
        ptr = mem_ptr - MEMORY_OFFSET
        for x in frames_map:
            if x[0]==ptr:
                return (f'0x{mem_ptr:08x}', f'0x{ptr:08x}', x[1])
        return (f'0x{ptr:08x}', "-----")




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
                'fields': f'0x{self.ptr_next_hitbox:08x}',
                'score': self.score
            }
        }
        
    


class TreeLogicNode:
    """Representa la estructura tree_logic_node con DATO inicial"""
    SIZE = 50  # 10 punteros (40 bytes) + 10 fields (10 bytes)

    def __init__(self, data: bytes, file_offset: int ):
        """
        Parsea una estructura tree_logic_node desde bytes

        Args:
            data: bytes conteniendo la estructura
            file_offset: posición en el archivo
            binary_data: datos binarios completos para resolver punteros
        """
        # Big-endian: 10 pointers + 10 undefined bytes + 1 int + 2 pointers
        unpacked = struct.unpack('>IIIIIII10sIII', data[:self.SIZE])

        self.dato = unpacked[0]
        self.ptr_hit_ok = unpacked[1]
        self.ptr_frame_ko_init = unpacked[2]
        self.ptr_frame_ko_end = unpacked[3]
        self.ptr_frame_hitbox_activo_init = unpacked[4]
        self.ptr_frame_hitbox_activo_end = unpacked[5]
        self.ptr_hitbox = unpacked[6]
        self.fields = list(unpacked[7])
        self.dos_cero_dos_cero = unpacked[8]
        self.ptr_fn_callback = unpacked[9]
        self.ptr_init_struct = unpacked[10]

        self.file_offset = file_offset
        self.mem_offset = file_offset + MEMORY_OFFSET
        self.binary_data = None
        self.hitbox_struct = []


    def to_dict(self, frames_map: Dict[int, str]) -> Dict:
        """Convierte la estructura a diccionario para JSON"""
        result = {
            'type': 'tree_logic_node',
            'file_offset': f'0x{self.file_offset:08x}',
            'mem_offset': f'0x{self.mem_offset:08x}',
            'value': {
                'DATO': f'0x{self.dato:08x}',
                'ptr_hit_ok':  (f'0x{self.ptr_hit_ok:08x}' , f'0x{(self.ptr_hit_ok-MEMORY_OFFSET):08x}'),
                'ptr_frame_ko_init': self._format_frame_ptr(self.ptr_frame_ko_init, frames_map),
                'ptr_frame_ko_end': self._format_frame_ptr(self.ptr_frame_ko_end, frames_map),
                'ptr_frame_hitbox_activo_init': self._format_frame_ptr(self.ptr_frame_hitbox_activo_init, frames_map),
                'ptr_frame_hitbox_activo_end': self._format_frame_ptr(self.ptr_frame_hitbox_activo_end, frames_map),
                'ptr_hitbox': [ x.to_dict() for x in self.hitbox_struct] ,
                'fields': [hex(b) for b in self.fields],
                'dos_cero_dos_cero': f'0x{self.dos_cero_dos_cero:08x}',
                'ptr_fn_callback': f'0x{self.ptr_fn_callback:08x}',
                'ptr_init_struct': f'0x{self.ptr_init_struct:08x}'
            }
        }
        return result

    def _format_frame_ptr(self, mem_ptr: int, frames_map: Dict[int, str]) -> Tuple[str, str]:
        """Formatea un puntero a frame con su valor"""
        ptr = mem_ptr - MEMORY_OFFSET
        for x in frames_map:
            if x[0]==ptr:
                return (f'0x{mem_ptr:08x}', f'0x{ptr:08x}', x[1])
        return (f'0x{ptr:08x}', "-----")


class TreeLogicNodeNoHitbox:
    """Representa la estructura tree_logic_node_no_hitbox sin DATO inicial"""
    SIZE = 46  # 9 punteros (36 bytes) + 10 fields (10 bytes)

    def __init__(self, data: bytes, file_offset: int):
        """
        Parsea una estructura tree_logic_node_no_hitbox desde bytes

        Args:
            data: bytes conteniendo la estructura
            file_offset: posición en el archivo
            binary_data: datos binarios completos para resolver punteros
        """
        # Big-endian: 9 pointers + 10 undefined bytes + 1 int + 2 pointers
        unpacked = struct.unpack('>IIIIII10sIII', data[:self.SIZE])

        self.ptr_hit_ok = unpacked[0]
        self.ptr_frame_ko_init = unpacked[1]
        self.ptr_frame_ko_end = unpacked[2]
        self.ptr_frame_hitbox_activo_init = unpacked[3]
        self.ptr_frame_hitbox_activo_end = unpacked[4]
        self.ptr_hitbox = unpacked[5]
        self.fields =  list(unpacked[6])
        self.dos_cero_dos_cero = unpacked[7]
        self.ptr_fn_callback = unpacked[8]
        self.ptr_init_struct = unpacked[9]

        self.file_offset = file_offset
        self.mem_offset = file_offset + MEMORY_OFFSET
        self.binary_data = None
        self.hitbox_struct = []


    def to_dict(self, frames_map: Dict[int, str]) -> Dict:
        """Convierte la estructura a diccionario para JSON"""
        result = {
            'type': 'tree_logic_node_no_hitbox',
            'file_offset': f'0x{self.file_offset:08x}',
            'mem_offset': f'0x{self.mem_offset:08x}',
            'value': {
                'ptr_hit_ok': (f'0x{self.ptr_hit_ok:08x}' , f'0x{(self.ptr_hit_ok-MEMORY_OFFSET):08x}'),
                'ptr_frame_ko_init': self._format_frame_ptr(self.ptr_frame_ko_init, frames_map),
                'ptr_frame_ko_end': self._format_frame_ptr(self.ptr_frame_ko_end, frames_map),
                'ptr_frame_hitbox_activo_init': self._format_frame_ptr(self.ptr_frame_hitbox_activo_init, frames_map),
                'ptr_frame_hitbox_activo_end': self._format_frame_ptr(self.ptr_frame_hitbox_activo_end, frames_map),
                'ptr_hitbox': [ x.to_dict() for x in self.hitbox_struct] ,
                'fields': [hex(b) for b in self.fields],
                'dos_cero_dos_cero': f'0x{self.dos_cero_dos_cero:08x}',
                'ptr_fn_callback': f'0x{self.ptr_fn_callback:08x}',
                'ptr_init_struct': f'0x{self.ptr_init_struct:08x}'
            }
        }
        return result

    def _format_frame_ptr(self, mem_ptr: int, frames_map: Dict[int, str]) -> Tuple[str, str]:
        """Formatea un puntero a frame con su valor"""
        ptr = mem_ptr - MEMORY_OFFSET
        for x in frames_map:
            if x[0]==ptr:
                return (f'0x{mem_ptr:08x}', f'0x{ptr:08x}', x[1])
        return (f'0x{ptr:08x}', "-----")


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
    

    while True:
        chunk_start = offset
        ptr_init_struct = struct.unpack('>I', data[offset-4:offset])[0]
       
        file_offset_struct = ptr_init_struct - MEMORY_OFFSET
        struct_size = offset - file_offset_struct 
        new_struct = None
        if struct_size == TreeLogicNode.SIZE :
            new_struct = TreeLogicNode(data[file_offset_struct:],file_offset_struct)
            
        elif struct_size == TreeLogicNodeNoHitbox.SIZE:
            new_struct = TreeLogicNodeNoHitbox(data[file_offset_struct:],file_offset_struct)
            
        elif struct_size == HeaderChunkStruct.SIZE or ptr_init_struct == 0x00000000:
            new_struct = HeaderChunkStruct(data[chunk_start-HeaderChunkStruct.SIZE:],chunk_start-HeaderChunkStruct.SIZE)
            chunks.append({
                    'start': chunk_start-HeaderChunkStruct.SIZE,
                    "data_struct": new_struct                   
                    
                })
            break
        else:
            raise ValueError(f"Estructura desconocida en offset 0x{file_offset_struct:08x} con tamaño {struct_size} bytes")
        chunk_start-=struct_size
        
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
                    tmp_chunk_start=hitbox_file_offset
                    while new_hitbox.ptr_next_hitbox !=0:
                        next_hitbox_file_offset = new_hitbox.ptr_next_hitbox - MEMORY_OFFSET
                        if 0 <= next_hitbox_file_offset < len(data) - HitboxStruct.SIZE:
                            new_hitbox= HitboxStruct(
                                data[next_hitbox_file_offset:],
                                next_hitbox_file_offset
                            )
                            new_struct.hitbox_struct.append(new_hitbox)
                            tmp_chunk_start=next_hitbox_file_offset
                        else:
                            raise ValueError("Error al parsear hitbox linked list")
                    previous_ptr = struct.unpack('>I', data[chunk_start-4:chunk_start])[0]
                    if previous_ptr & 0xffff0000 == 0:
                        chunk_start=tmp_chunk_start
                except:
                    raise ValueError("Error al parsear hitbox")
        
        chunks.append({
                    'start': chunk_start,
                    "data_struct": new_struct                   
                    
                })
        #move offset to next struct
        offset = chunk_start
           

    return chunks


 


def parse_binary(binary_path: str) -> List[Dict]:
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

        result.append(chunk_dict)

    return result


def main():
    """Función principal"""
    

    # Parsear el binario
    chunks = parse_binary("picmatic_zb_v1.01_combined.bin")

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
