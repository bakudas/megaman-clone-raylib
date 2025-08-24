# game/world.py
from typing import Dict, Any, List, Type

class World:
    def __init__(self):
        self.next_entity_id = 0
        # Um dicionário onde a chave é o tipo do componente e o valor é outro dicionário
        # mapeando entity_id para a instância do componente.
        self.components: Dict[Type, Dict[int, Any]] = {}

    def create_entity(self) -> int:
        entity_id = self.next_entity_id
        self.next_entity_id += 1
        return entity_id

    def add_component(self, entity_id: int, component_instance: Any):
        component_type = type(component_instance)
        if component_type not in self.components:
            self.components[component_type] = {}
        self.components[component_type][entity_id] = component_instance

    def get_entities_with_components(self, *component_types: Type) -> List[int]:
        # Retorna uma lista de IDs de entidades que possuem TODOS os tipos de componentes especificados.
        try:
            entity_ids = set(self.components[component_types[0]].keys())
            for component_type in component_types[1:]:
                entity_ids.intersection_update(self.components[component_type].keys())
            return list(entity_ids)
        except KeyError:
            return []

    def get_component(self, entity_id: int, component_type: Type) -> Any:
        # Retorna a instância do componente para uma dada entidade e tipo.
        return self.components.get(component_type, {}).get(entity_id)

    def remove_component(self, entity_id: int, component_type: Type):
        """Remove um componente de uma entidade."""
        if component_type in self.components and entity_id in self.components[component_type]:
            del self.components[component_type][entity_id]