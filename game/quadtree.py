
import pyray as pr

class Quadtree:
    """
    Uma implementação de Quadtree para detecção de colisão 2D eficiente.
    """
    def __init__(self, boundary: pr.Rectangle, capacity: int, level: int = 0):
        """
        Cria uma Quadtree.
        :param boundary: O retângulo que define os limites deste nó da árvore.
        :param capacity: O número máximo de objetos que um nó pode conter antes de se subdividir.
        :param level: O nível de profundidade atual deste nó.
        """
        self.boundary = boundary
        self.capacity = capacity
        self.level = level
        self.objects = []  # Lista de tuplas (objeto, retângulo)
        self.nodes = []    # Nós filhos

    def clear(self):
        """Limpa a quadtree recursivamente."""
        self.objects.clear()
        for node in self.nodes:
            node.clear()
        self.nodes.clear()

    def subdivide(self):
        """Divide o nó em quatro sub-nós."""
        x, y, w, h = self.boundary.x, self.boundary.y, self.boundary.width, self.boundary.height
        half_w, half_h = w / 2, h / 2
        next_level = self.level + 1

        # As ordens são importantes para o get_index
        self.nodes.append(Quadtree(pr.Rectangle(x + half_w, y, half_w, half_h), self.capacity, next_level))  # Nordeste
        self.nodes.append(Quadtree(pr.Rectangle(x, y, half_w, half_h), self.capacity, next_level))          # Noroeste
        self.nodes.append(Quadtree(pr.Rectangle(x, y + half_h, half_w, half_h), self.capacity, next_level))  # Sudoeste
        self.nodes.append(Quadtree(pr.Rectangle(x + half_w, y + half_h, half_w, half_h), self.capacity, next_level)) # Sudeste

    def get_index(self, rect: pr.Rectangle) -> int:
        """
        Determina em qual quadrante um retângulo se encaixa completamente.
        Retorna -1 se ele não se encaixar completamente em nenhum filho (ou seja, se sobrepõe a limites).
        """
        index = -1
        vertical_midpoint = self.boundary.x + (self.boundary.width / 2)
        horizontal_midpoint = self.boundary.y + (self.boundary.height / 2)

        top_quadrant = (rect.y < horizontal_midpoint and rect.y + rect.height < horizontal_midpoint)
        bottom_quadrant = (rect.y > horizontal_midpoint)

        if rect.x < vertical_midpoint and rect.x + rect.width < vertical_midpoint:
            if top_quadrant:
                index = 1  # Noroeste
            elif bottom_quadrant:
                index = 2  # Sudoeste
        elif rect.x > vertical_midpoint:
            if top_quadrant:
                index = 0  # Nordeste
            elif bottom_quadrant:
                index = 3  # Sudeste
        return index

    def insert(self, obj, rect: pr.Rectangle):
        """
        Insere um objeto na quadtree.
        """
        # Se o nó tiver filhos, tenta passar o objeto para o filho apropriado.
        if self.nodes:
            index = self.get_index(rect)
            if index != -1:
                self.nodes[index].insert(obj, rect)
                return

        # Se não, armazena o objeto neste nó.
        self.objects.append((obj, rect))

        # Se a capacidade for excedida, subdivide e tenta mover os objetos para os filhos.
        if len(self.objects) > self.capacity and self.level < 8:  # Limite de profundidade para evitar recursão infinita
            if not self.nodes:
                self.subdivide()

            i = 0
            while i < len(self.objects):
                o, r = self.objects[i]
                index = self.get_index(r)
                if index != -1:
                    self.nodes[index].insert(o, r)
                    self.objects.pop(i)
                else:
                    i += 1

    def query(self, range_rect: pr.Rectangle) -> list:
        """
        Consulta a quadtree para encontrar todos os objetos dentro de um determinado retângulo de alcance.
        """
        found = []
        # Adiciona objetos deste nó se eles colidirem com o alcance
        for obj, rect in self.objects:
            if pr.check_collision_recs(range_rect, rect):
                found.append(obj)

        # Se não houver filhos, termina aqui
        if not self.nodes:
            return found

        # Se houver filhos, consulta-os recursivamente
        for node in self.nodes:
            if pr.check_collision_recs(node.boundary, range_rect):
                found.extend(node.query(range_rect))
                
        # Remove duplicatas mantendo a ordem e sem exigir que os objetos sejam hasheáveis.
        unique_found = []
        seen_ids = set()
        for item in found:
            item_id = id(item)
            if item_id not in seen_ids:
                unique_found.append(item)
                seen_ids.add(item_id)
        return unique_found
