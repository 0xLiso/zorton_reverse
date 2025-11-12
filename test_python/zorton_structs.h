typedef unsigned char   undefined;

typedef unsigned char    byte;
typedef unsigned char    uchar;
typedef unsigned int    uint;
typedef unsigned long    ulong;
typedef unsigned char    undefined1;
typedef unsigned short    undefined2;
typedef unsigned int    undefined4;
typedef unsigned short    ushort;
 



struct struct header_chunk{
    pointer ptr_frame_init;
    pointer ptr_frame_end;
    pointer ptr_frame_ko_init;
    pointer ptr_frame_ko_end;

    pointer ptr_unk1;
    pointer ptr_unk2;
    pointer ptr_unk3;
    pointer ptr_unk4;

    undefined field1;
    undefined field2;
    undefined field3;
    undefined field4;
    undefined field5;
struct tree_logic_node_type_3{
    pointer ptr_hit_ok;
    pointer ptr_frame_ko_init;
    pointer ptr_frame_ko_end;
    pointer ptr_frame_hitbox_activo_init;
    pointer ptr_frame_hitbox_activo_end;
    pointer ptr_frame_hitbox2_activo_init;
    pointer ptr_frame_hitbox2_activo_end;
    pointer ptr_hitbox;

    byte end_chunk[10];
    byte type_a;
    byte type_b;
    byte type_chunk;
    byte type_d;
    pointer ptr_callback;
    pointer ptr_init_struct;


}
    undefined field6;


    pointer ptr_callback;

}




struct struct hitbox {
    int y0;
    int y1;
    int x0;
    int x1;
    pointer ptr_next_hitbox;
    int score;
};




struct tree_logic_node_type_0{
    pointer ptr_frame_init;
    pointer ptr_frame_end;
    pointer ptr_frame_ko_init;
    pointer ptr_frame_ko_end;

    pointer ptr_unk1;


    byte end_chunk[10];
    byte type_a;
    byte type_b;
    byte type_chunk;
    byte type_d;
    pointer ptr_callback;
    pointer ptr_init_struct;


}




struct tree_logic_node_type_1{
   pointer ptr_hit_ok;
    pointer ptr_frame_ko_init;
    pointer ptr_frame_ko_end;
    pointer ptr_frame_hitbox_activo_init;
    pointer ptr_frame_hitbox_activo_end;
    pointer ptr_frame_unk;


    byte end_chunk[10];
    byte type_a;
    byte type_b;
    byte type_chunk;
    byte type_d;
    pointer ptr_callback;
    pointer ptr_init_struct;


}


struct tree_logic_node_type_2{
       pointer DATO;
    pointer ptr_hit_ok;
    pointer ptr_frame_ko_init;
    pointer ptr_frame_ko_end;
    pointer ptr_frame_hitbox_activo_init;
    pointer ptr_frame_hitbox_activo_end;
    pointer ptr_hitbox;

    byte end_chunk[10];
    byte type_a;
    byte type_b;
    byte type_chunk;
    byte type_d;
    pointer ptr_callback;
    pointer ptr_init_struct;


}


struct tree_logic_node_type_3{
    pointer ptr_hit_ok;
    pointer ptr_frame_ko_init;
    pointer ptr_frame_ko_end;
    pointer ptr_frame_hitbox_activo_init;
    pointer ptr_frame_hitbox_activo_end;
    pointer ptr_frame_hitbox2_activo_init;
    pointer ptr_frame_hitbox2_activo_end;
    pointer ptr_hitbox;

    byte end_chunk[10];
    byte type_a;
    byte type_b;
    byte type_chunk;
    byte type_d;
    pointer ptr_callback;
    pointer ptr_init_struct;


}


struct tree_logic_node_type_4{
    pointer ptr_hit_ok;
    pointer ptr_frame_ko_init;
    pointer ptr_frame_ko_end;
    pointer ptr_frame_hitbox_activo_init;
    pointer ptr_frame_hitbox_activo_end;
    pointer ptr_frame_hitbox2_activo_init;
    pointer ptr_frame_hitbox2_activo_end;
    pointer ptr_idk;
    pointer ptr_hitbox;

    byte end_chunk[10];
    byte type_a;
    byte type_b;
    byte type_chunk;
    byte type_d;
    pointer ptr_callback;
    pointer ptr_init_struct;


}