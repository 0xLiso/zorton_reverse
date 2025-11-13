# posible lógica de los chunks

Nx4bytes_ptr, 2x4byte_null, 0x0000, 1byte type_a, 1byte type_b, 1byte type_chunk, 1byte type_d, 4bytes_ptr_callback, 4bytes_posible_init.


|type_chunk|  N|
|__________|___|
|       0x0|  5|
|       0x1|  6|
|       0x2|  7|
|       0x3|  8|
|       0x4|  9|
|       0x5| 10|
|       0x6| 11|

mirar si los hitboxes van siempre junto al treenode que los usa.