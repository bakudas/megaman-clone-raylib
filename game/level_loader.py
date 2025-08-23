# game/level_loader.py
import json
import pyray as pr

from game.platforms import Platform
from game.hazards import Hazard
from game.enemy import Enemy
from game.checkpoints import Checkpoint

class LevelManager:
    def __init__(self, path: str):
        self.file_path: str = path
        self.level_data: dict = None
        self.tileset_path: str = 'assets/tileset/Subway_tiles.png'
        self.tileset_texture = pr.load_texture(self.tileset_path)

        with open(path, 'r') as f:
            self.level_data = json.load(f)

        # Dicionários para guardar os objetos criados
        self.level_objects = {
            "platforms": [],
            "hazards": [],
            "enemies": [],
            "checkpoints": [],
            "player_start": {},
        }

        self.source_objects = {
            "platforms": [],
            "hazards": [],
        }

        self.load_level()

    def load_level(self) -> dict:
        """
        Carrega um nível a partir de um arquivo JSON e retorna
        um dicionário com listas de todos os objetos do jogo.
        """
        # procura pelo level
        level = self.level_data.get('levels', [])

        # procura pelas camadas
        layers = level[0].get('layerInstances', [])
        layer_tile = layers[0]

        # procura pelos tiles
        tiles = layers[0].get('gridTiles', [])
        tileset_path = layers[0]['__tilesetRelPath']
        pr.load_image(tileset_path)

        # procura as entidades
        entities = layers[1]['entityInstances'] if layers[1]['__identifier'] == 'entities' else None


        # Cria os objetos
        for tile in tiles:
            self.source_objects['platforms'].append(tile)
            plat = Platform(x=tile['px'][0], y=tile['px'][1], width=layer_tile['__gridSize'], height=layer_tile['__gridSize'], p_type='solid')
            self.level_objects['platforms'].append(plat)

        for entity in entities:
            print(f'Entity: {entity}')
            if entity['__tags'][0] == 'player_start':
                self.level_objects['player_start']['x'], self.level_objects['player_start']['y'] = int(entity['px'][0]), int(entity['px'][1])
            elif entity['__tags'][0] == 'enemy':
                enemy = Enemy(x=entity['px'][0], y=entity['px'][1] - 16)
                self.level_objects['enemies'].append(enemy)
            elif entity['__tags'][0] == 'checkpoint':
                checkpoint = Checkpoint(x=entity['px'][0], y=entity['px'][1], width=16, height=32)
                self.level_objects['checkpoints'].append(checkpoint)


    def draw(self) -> None:
        """
        Desenha e atualiza o level
        """
        grid_size = (16, 16)
        level_data = self.source_objects['platforms']

        for tile in level_data:
            source_rec = pr.Rectangle(tile['src'][0], tile['src'][1], grid_size[0], grid_size[1])
            dest_rec = pr.Rectangle(tile['px'][0], tile['px'][1], grid_size[0], grid_size[1])
            origin = pr.Vector2(0, 0)
            pr.draw_texture_pro(self.tileset_texture, source_rec, dest_rec, origin, 0.0, pr.WHITE)