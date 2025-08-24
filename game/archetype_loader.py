import json
import pyray as pr
from game.world import World
from game import components, player_states, weapon_states, enemy_states
from game.animation import AnimationManager
from game.animation_factory import setup_player_animations

# Mapeia nomes de string para as classes de componentes reais
COMPONENT_MAP = {
    name: cls for name, cls in components.__dict__.items() if isinstance(cls, type)
}
# Combina os dicionários de estados do jogador e do inimigo
STATE_MAP = {
    **{name: cls for name, cls in player_states.__dict__.items() if isinstance(cls, type)},
    **{name: cls for name, cls in enemy_states.__dict__.items() if isinstance(cls, type)}
}
WEAPON_STATE_MAP = {
    name: cls for name, cls in weapon_states.__dict__.items() if isinstance(cls, type)
}

def create_entity_from_archetype(world: World, archetype_path: str, x: float, y: float) -> int:
    """Carrega um arquétipo de um arquivo JSON e cria uma entidade com base nele."""
    try:
        with open(archetype_path, 'r') as f:
            archetype_data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Erro ao carregar o arquétipo {archetype_path}: {e}")
        return -1

    entity_id = world.create_entity()
    print(f"Creating entity {entity_id} from archetype {archetype_path} at ({x}, {y})")

    # Adiciona o TransformComponent primeiro, pois outros podem depender dele
    transform_data = archetype_data['components'].get('TransformComponent', {})
    transform_data['x'] = x
    transform_data['y'] = y
    world.add_component(entity_id, components.TransformComponent(**transform_data))

    for comp_name, comp_data in archetype_data['components'].items():
        if comp_name == 'TransformComponent':
            continue # Já foi criado

        # --- Casos Especiais para componentes complexos ---
        if comp_name == 'AnimationComponent':
            anim_manager = AnimationManager(comp_data['sprite_sheet'])
            # TODO: Generalizar a configuração de animação para não ser apenas do jogador
            setup_player_animations(anim_manager)
            world.add_component(entity_id, components.AnimationComponent(anim_manager=anim_manager))
            continue

        if comp_name == 'StateMachineComponent':
            initial_state_class = STATE_MAP.get(comp_data['state'])
            initial_weapon_state_class = WEAPON_STATE_MAP.get(comp_data['weapon_state'])

            if not initial_state_class or not initial_weapon_state_class:
                print(f"ERRO: Estado inicial não encontrado para {comp_name}")
                continue

            # A inicialização do estado precisa do mundo e do ID da entidade
            state_instance = initial_state_class(world, entity_id)
            weapon_state_instance = initial_weapon_state_class()
            world.add_component(entity_id, components.StateMachineComponent(state=state_instance, weapon_state=weapon_state_instance))
            continue
        
        if comp_name == 'CollisionComponent':
            transform = world.get_component(entity_id, components.TransformComponent)
            comp_data['collider_rect'] = pr.Rectangle(transform.x, transform.y, transform.width, transform.height)
            # continue para o proximo if

        # --- Componentes Padrão (baseados em dados) ---
        component_class = COMPONENT_MAP.get(comp_name)
        if component_class:
            instance = component_class(**comp_data)
            world.add_component(entity_id, instance)
        else:
            print(f"AVISO: Classe de componente '{comp_name}' não encontrada.")

    return entity_id
