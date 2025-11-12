typedef unsigned char   undefined;

typedef unsigned char    byte;
typedef unsigned char    uchar;
typedef unsigned int    uint;
typedef unsigned long    ulong;
typedef unsigned char    undefined1;
typedef unsigned short    undefined2;
typedef unsigned int    undefined4;
typedef unsigned short    ushort;
typedef struct struct tree_logic_node struct tree_logic_node, *Pstruct tree_logic_node;



struct struct tree_logic_node_no_hitbox {
    pointer ptr_hit_ok;
    pointer ptr_frame_ko_init;
    pointer ptr_frame_ko_end;
    pointer ptr_frame_hitbox_activo_init;
    pointer ptr_frame_hitbox_activo_end;
    pointer ptr_hitbox;
    undefined field6_0x18;
    undefined field7_0x19;
    undefined field8_0x1a;
    undefined field9_0x1b;
    undefined field10_0x1c;
    undefined field11_0x1d;
    undefined field12_0x1e;
    undefined field13_0x1f;
    undefined field14_0x20;
    undefined field15_0x21;
    int dos_cero_dos_cero;
    pointer ptr_fn_callback;
    pointer ptr_init_struct;
};






struct struct tree_logic_node {
    pointer DATO;
    pointer ptr_hit_ok;
    pointer ptr_frame_ko_init;
    pointer ptr_frame_ko_end;
    pointer ptr_frame_hitbox_activo_init;
    pointer ptr_frame_hitbox_activo_end;
    pointer ptr_hitbox;
    undefined field7_0x1c;
    undefined field8_0x1d;
    undefined field9_0x1e;
    undefined field10_0x1f;
    undefined field11_0x20;
    undefined field12_0x21;
    undefined field13_0x22;
    undefined field14_0x23;
    undefined field15_0x24;
    undefined field16_0x25;
    int dos_cero_dos_cero;
    pointer ptr_fn_callback;
    pointer ptr_init_struct;
};

struct struct hitbox {
    int y0;
    int y1;
    int x0;
    int x1;
    pointer ptr_next_hitbox;
    int score;
};



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
    undefined field6;


    pointer ptr_callback;

}