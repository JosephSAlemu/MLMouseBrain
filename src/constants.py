SIZE = 1464

HEADERS = ["X","Y","Z"]

HEADERS_V2 = ["Structure-ID","structure_acronym","structure_name","voxRowNum","X","Y","Z"]

HEADERS_V3 = ["Structure-ID","structure_acronym","structure_name","voxRowNum"]

HEADERS_V4 = ["Structure-ID","X","Y","Z"]

HEADERS_V5 =["Structure-ID","X","Y","Z", "voxRowNum"]

HEADERS_V6 = ["Structure-ID", "Section_Dataset", "X","Y","Z"]

HEADERS_V7 = ["Structure-ID", "Section_Dataset", "X","Y","Z", "voxRowNum"]

FILE_START = 1

FILE_END = 9

CHUNK_HEADERS = ["Voxel", "Section_Image"]

CHUNK_HEADERS_V2 = ["Voxel_x", "Voxel_y", "Voxel_z", "Section_Dataset", "Section_Image", "Seed_x", "Seed_y"]

CHUNK_HEADERS_V3 = ["Voxel_x", "Voxel_y", "Voxel_z", "Section_Dataset", "Section_Image", "Seed_x", "Seed_y", "Gene_Expression"]

CHUNK_HEADERS_V4 = ["Structure-ID", "Voxel_x", "Voxel_y", "Voxel_z", "Section_Dataset", "Section_Image", "Seed_x", "Seed_y"]

CHUNK_HEADERS_V5 = ["Structure-ID", "Section_Image", "Seed_x", "Seed_y"]

DENSITY = 2500

DISTRIBUTED = 259

P4_MOUSE_REFERENCE_ID = 6

P56_MOUSE_REFERENCE_ID = 10

P4_CONVERSION = 160

P56_CONVERSION = 200

AVAILABLE_MICE = {
    "From P56 Mouse to Other Mouse": P56_MOUSE_REFERENCE_ID,
    "From P4 Mouse to Other Mouse": P4_MOUSE_REFERENCE_ID
}

STRUCTURE_ID_ABBREVIATIONS = {
    773: "XII",
    136: "IRN",
    1098: "MDRNd",
    939: "AMBd",
    970: "PGRNd",
    235: "LRN",
    143: "AMBv",
    978: "PGRNl",
    1107: "MDRNv",
    852: "PARN",
    661: "VII",
    307: "MARN",
    1048: "GRN"
}

STRUCTURE_ID_CLUSTER_ANALYSIS_COLORS = {
    136: "#f26460",   
    143: "#c9dbfb",   
    235: "#98d494",   
    307: "#f9e285",   
    661: "#f4a3a3",   
    773: "#faae85",   
    852: "#a4e1e0",   
    939: "#f9e285", 
    970: "#86b6f2",   
    978: "#f98c45",   
    1048: "#c9dbfb",  
    1098: "#98d494",  
    1107: "#a4e1e0",  
}