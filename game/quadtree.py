# game/quadtree.py
import pyray as pr

class Quadtree:
    """
    A Quadtree implementation for efficient 2D spatial partitioning and collision detection.
    """
    def __init__(self, level: int, bounds: pr.Rectangle):
        self.level = level
        self.bounds = bounds
        self.objects = []
        self.nodes = [None, None, None, None]
        self.max_objects = 10  # Max objects before a node splits
        self.max_levels = 5    # Max depth of the tree

    def clear(self):
        """Clears the quadtree."""
        self.objects.clear()
        for i in range(len(self.nodes)):
            if self.nodes[i] is not None:
                self.nodes[i].clear()
                self.nodes[i] = None

    def split(self):
        """Splits the node into 4 sub-nodes."""
        sub_width = self.bounds.width / 2
        sub_height = self.bounds.height / 2
        x = self.bounds.x
        y = self.bounds.y

        self.nodes[0] = Quadtree(self.level + 1, pr.Rectangle(x + sub_width, y, sub_width, sub_height)) # Top right
        self.nodes[1] = Quadtree(self.level + 1, pr.Rectangle(x, y, sub_width, sub_height))             # Top left
        self.nodes[2] = Quadtree(self.level + 1, pr.Rectangle(x, y + sub_height, sub_width, sub_height)) # Bottom left
        self.nodes[3] = Quadtree(self.level + 1, pr.Rectangle(x + sub_width, y + sub_height, sub_width, sub_height)) # Bottom right

    def get_index(self, rect: pr.Rectangle) -> int:
        """Determine which node the object belongs to. -1 means object cannot completely fit within a child node and is part of the parent node."""
        index = -1
        vertical_midpoint = self.bounds.x + (self.bounds.width / 2)
        horizontal_midpoint = self.bounds.y + (self.bounds.height / 2)

        top_quadrant = (rect.y < horizontal_midpoint and rect.y + rect.height < horizontal_midpoint)
        bottom_quadrant = (rect.y > horizontal_midpoint)

        if rect.x < vertical_midpoint and rect.x + rect.width < vertical_midpoint:
            if top_quadrant:
                index = 1
            elif bottom_quadrant:
                index = 2
        elif rect.x > vertical_midpoint:
            if top_quadrant:
                index = 0
            elif bottom_quadrant:
                index = 3
        return index

    def insert(self, obj_with_rect):
        """Insert an object with a bounding box into the quadtree."""
        rect = pr.Rectangle(obj_with_rect.x, obj_with_rect.y, obj_with_rect.width, obj_with_rect.height)
        if self.nodes[0] is not None:
            index = self.get_index(rect)
            if index != -1:
                self.nodes[index].insert(obj_with_rect)
                return

        self.objects.append(obj_with_rect)

        if len(self.objects) > self.max_objects and self.level < self.max_levels:
            if self.nodes[0] is None:
                self.split()
            
            i = 0
            while i < len(self.objects):
                obj_rect = pr.Rectangle(self.objects[i].x, self.objects[i].y, self.objects[i].width, self.objects[i].height)
                index = self.get_index(obj_rect)
                if index != -1:
                    self.nodes[index].insert(self.objects.pop(i))
                else:
                    i += 1

    def retrieve(self, return_objects: list, rect: pr.Rectangle) -> list:
        """Return all objects that could collide with the given object."""
        index = self.get_index(rect)
        if index != -1 and self.nodes[0] is not None:
            self.nodes[index].retrieve(return_objects, rect)
        
        return_objects.extend(self.objects)
        return return_objects