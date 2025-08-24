# game/level_loader.py
import json
import pyray as pr

from game.camera import Camera
from game.platforms import Platform
from game.hazards import Hazard
from game.checkpoints import Checkpoint
from game.quadtree import Quadtree
from game.archetype_loader import create_entity_from_archetype


class LevelManager:
    def __init__(self, path: str):
        self.file_path: str = path
        self.level_data: dict = None
        self.tileset_path: str = 'assets/tileset/Subway_tiles.png'
        self.tileset_texture = pr.load_texture(self.tileset_path)

        self.tile_grid = []
        self.map_width_in_tiles = 0
        self.map_height_in_tiles = 0
        self.tile_size = 16

        with open(path, 'r') as f:
            self.level_data = json.load(f)

        self.level_objects = {
            "platforms": [],
            "hazards": [],
            "enemies": [],
            "checkpoints": [],
            "player_start": {},
            "quadtree": None,
        }
        self.source_objects = {
            "platforms": [],
            "hazards": [],
        }

    def load_level(self, world: 'World') -> dict:
        enemy_archetype_map = {
            "patrol": "levels/archetypes/patrol_enemy.json",
            "jumper": "levels/archetypes/jumper_enemy.json"
        }

        level = self.level_data.get('levels', [])[0]
        layers = level.get('layerInstances', [])
        
        tiles_layer = None
        entities_layer = None
        for layer in layers:
            if layer['__identifier'] == 'tiles':
                tiles_layer = layer
            elif layer['__identifier'] == 'entities':
                entities_layer = layer

        if not tiles_layer or not entities_layer:
            raise ValueError("Camadas essenciais 'tiles' ou 'entities' não encontradas no JSON do nível.")

        map_px_width = tiles_layer['__cWid'] * tiles_layer['__gridSize']
        map_px_height = tiles_layer['__cHei'] * tiles_layer['__gridSize']
        self.level_objects["quadtree"] = Quadtree(0, pr.Rectangle(0, 0, map_px_width, map_px_height))

        self.map_width_in_tiles = tiles_layer['__cWid']
        self.map_height_in_tiles = tiles_layer['__cHei']
        self.tile_size = tiles_layer['__gridSize']
        self.tile_grid = [[None for _ in range(self.map_width_in_tiles)] for _ in range(self.map_height_in_tiles)]

        #tileset_path = tiles_layer.get('__tilesetRelPath', '').replace("../", "", 1)
        # pr.load_image(tileset_path) # A textura já é carregada no __init__

        tile_id_to_type = {}
        for tileset_def in self.level_data['defs']['tilesets']:
            for enum_tag in tileset_def.get('enumTags', []):
                enum_type = enum_tag.get('enumValueId')
                if enum_type in ["solid", "pass_through", "no_collision"]:
                    for tile_id in enum_tag.get('tileIds', []):
                        tile_id_to_type[tile_id] = enum_type
        #import ipdb; ipdb.set_trace()
        for toc_entry in self.level_data.get('toc', []):
            if toc_entry['identifier'] == 'player_start':
                instance_data = toc_entry['instancesData'][0]
                self.level_objects['player_start']['x'] = instance_data['worldX']
                self.level_objects['player_start']['y'] = instance_data['worldY']
                break

        for tile in tiles_layer.get('gridTiles', []):
            tile_id = tile['t']
            platform_type = tile_id_to_type.get(tile_id)

            grid_x = tile['px'][0] // self.tile_size
            grid_y = tile['px'][1] // self.tile_size
            if 0 <= grid_y < self.map_height_in_tiles and 0 <= grid_x < self.map_width_in_tiles:
                self.tile_grid[grid_y][grid_x] = tile

            if platform_type:
                self.source_objects['platforms'].append(tile)
                plat = Platform(x=tile['px'][0], y=tile['px'][1],
                                width=self.tile_size,
                                height=self.tile_size,
                                p_type=platform_type)
                self.level_objects['platforms'].append(plat)
                self.level_objects['quadtree'].insert(plat)

        for entity in entities_layer.get('entityInstances', []):
            if entity['__identifier'] == 'enemy':
                enemy_type = next((f['__value'] for f in entity['fieldInstances'] if f['__identifier'] == 'e_type'), None)
                if world and enemy_type in enemy_archetype_map:
                    archetype_path = enemy_archetype_map[enemy_type]
                    create_entity_from_archetype(world, archetype_path, x=entity['px'][0], y=entity['px'][1] - 16)
                else:
                    print(f"AVISO: Tipo de inimigo '{enemy_type}' desconhecido ou não mapeado.")
            elif entity['__identifier'] == 'checkpoint':
                checkpoint = Checkpoint(x=entity['px'][0], y=entity['px'][1], width=16, height=32)
                self.level_objects['checkpoints'].append(checkpoint)

        return self.level_objects

    def draw(self, camera_rect: pr.Rectangle):
        start_col = max(0, int(camera_rect.x / self.tile_size))
        end_col = min(self.map_width_in_tiles, int((camera_rect.x + camera_rect.width) / self.tile_size) + 1)
        start_row = max(0, int(camera_rect.y / self.tile_size))
        end_row = min(self.map_height_in_tiles, int((camera_rect.y + camera_rect.height) / self.tile_size) + 1)

        for y in range(start_row, end_row):
            for x in range(start_col, end_col):
                tile_data = self.tile_grid[y][x]
                if tile_data:
                    source_rec = pr.Rectangle(tile_data['src'][0], tile_data['src'][1], self.tile_size, self.tile_size)
                    pr.draw_texture_rec(self.tileset_texture, source_rec, (tile_data['px'][0], tile_data['px'][1]), pr.WHITE)

    def unload(self):
        pr.unload_texture(self.tileset_texture)
