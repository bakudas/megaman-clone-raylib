# game/level_loader.py
import json
import pyray as pr
from typing import TYPE_CHECKING

from game.quadtree import Quadtree
from game.platforms import Platform
from game.enemy import Enemy
from game.checkpoints import Checkpoint

if TYPE_CHECKING:
    from game.camera import Camera

class LevelManager:
    def __init__(self, path: str):
        self.file_path: str = path
        self.level_data: dict = None
        self.tileset_path: str = 'assets/tileset/Subway_tiles.png'
        self.tileset_texture = pr.load_texture(self.tileset_path)
        self.quadtree: Quadtree = None

        with open(path, 'r') as f:
            self.level_data = json.load(f)

        self.level_objects = {
            "platforms": [],
            "hazards": [],
            "enemies": [],
            "checkpoints": [],
            "player_start": {},
        }
        self.load_level()

    def load_level(self):
        level_json = self.level_data.get('levels', [])[0]
        layers = level_json.get('layerInstances', [])
        
        tiles_layer = next((layer for layer in layers if layer['__identifier'] == 'tiles'), None)
        entities_layer = next((layer for layer in layers if layer['__identifier'] == 'entities'), None)

        if not tiles_layer:
            return

        grid_size = tiles_layer['__gridSize']
        
        all_tiles_data = tiles_layer.get('gridTiles', [])
        if not all_tiles_data:
            return

        min_x = min(t['px'][0] for t in all_tiles_data)
        min_y = min(t['px'][1] for t in all_tiles_data)
        max_x = max(t['px'][0] + grid_size for t in all_tiles_data)
        max_y = max(t['px'][1] + grid_size for t in all_tiles_data)
        level_boundary = pr.Rectangle(min_x, min_y, max_x - min_x, max_y - min_y)
        
        self.quadtree = Quadtree(level_boundary, capacity=4)

        # Criar objetos Platform unificados e inseri-los em todos os lugares necessários
        for tile_data in all_tiles_data:
            dest_rect = pr.Rectangle(float(tile_data['px'][0]), float(tile_data['px'][1]), float(grid_size), float(grid_size))
            source_rect = pr.Rectangle(float(tile_data['src'][0]), float(tile_data['src'][1]), float(grid_size), float(grid_size))
            
            # Criar o objeto unificado
            platform = Platform(x=dest_rect.x, y=dest_rect.y, width=dest_rect.width, height=dest_rect.height, p_type='solid', source_rec=source_rect)
            
            # Adicionar à lista para a física
            self.level_objects['platforms'].append(platform)
            # Adicionar à Quadtree para renderização e física otimizada
            self.quadtree.insert(platform, dest_rect)

        # Criar Entidades Dinâmicas (não vão para a quadtree de geometria estática)
        if entities_layer:
            for entity in entities_layer['entityInstances']:
                tags = entity.get('__tags', [])
                if not tags: continue

                tag = tags[0]
                x, y = float(entity['px'][0]), float(entity['px'][1])

                if tag == 'player_start':
                    self.level_objects['player_start'] = {'x': x, 'y': y}
                elif tag == 'enemy':
                    self.level_objects['enemies'].append(Enemy(x=x, y=y - 16))
                elif tag == 'checkpoint':
                    self.level_objects['checkpoints'].append(Checkpoint(x=x, y=y, width=16, height=32))

    def draw(self, camera: 'Camera') -> None:
        if not self.quadtree:
            return

        view_rect = camera.get_world_view_rect()
        view_rect_buffered = pr.Rectangle(
            view_rect.x - 16, view_rect.y - 16,
            view_rect.width + 32, view_rect.height + 32
        )

        drawable_platforms = self.quadtree.query(view_rect_buffered)

        for platform in drawable_platforms:
            platform.draw(self.tileset_texture)

