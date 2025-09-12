SIZE = 1464

HEADERS = ["X","Y","Z"]

HEADERS_V2 = ["structure_id","structure_acronym","structure_name","voxRowNum","X","Y","Z"]

HEADERS_V3 = ["structure_id","structure_acronym","structure_name","voxRowNum"]

HEADERS_V4 = ["structure_id","X","Y","Z"]

FILE_START = 1

FILE_END = 9

CHUNK_HEADERS = ["Voxel", "Section_Image"]

CHUNK_HEADERS_V2 = ["Voxel_x", "Voxel_y", "Voxel_z", "Section_Dataset", "Section_Image", "Seed_x", "Seed_y"]

CHUNK_HEADERS_V3 = ["Voxel_x", "Voxel_y", "Voxel_z", "Section_Dataset", "Section_Image", "Seed_x", "Seed_y", "Gene_Expression"]

DENSITY = 2500

DISTRIBUTED = 259

P4_MOUSE_REFERENCE_ID = 6

P56_MOUSE_REFERENCE_ID = 10

P4_CONVERSION = 160

P56_CONVERSION = 200

AVAILABLE_MICE = {
    "P56": P56_MOUSE_REFERENCE_ID,
    "P4": P4_MOUSE_REFERENCE_ID
}