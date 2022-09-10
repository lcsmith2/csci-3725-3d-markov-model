import numpy as np
import math
import bpy

class MarkovCity:
    
    def __init__(self, transition_matrix):
        """
        Uses a Markov model to generate a small-scale city in Blender.
        Args:
            transition_matrix (dict): transition probabilities for the Markov model
        """
        self.transition_matrix = transition_matrix
        self.heights = list(transition_matrix.keys())


    def get_next_height(self, current_height):
        """
        Determines the height of the next building based on the height of the current one.
        Args:
            current_height (int): the height of the current building
        """
        return np.random.choice(
            self.heights, 
            p=[self.transition_matrix[current_height][next_height] for next_height in self.heights] 
        )

    
    def get_building_heights(self, num_rows, num_cols):
        """
        Returns a 2D array containing the heights for each building in the grid.
        Args:
            num_rows (int): the number of rows in the grid
            num_cols (int): the number of columns in the grid
        """
        building_heights = [[0] * num_cols for r in range(num_rows)]

        current_height = 0
        for r in range(num_rows):
            for c in range(num_cols):
                next_height = self.get_next_height(current_height)
                building_heights[r][c] = next_height
                current_height = next_height

        return building_heights


def main():
    city = MarkovCity({
        0: {0: 0.5, 1: 0.2, 2: 0.15, 3: 0.15},
        1: {0: 0.1, 1: 0.5, 2: 0.2, 3: 0.2},
        2: {0: 0.1, 1: 0.1, 2: 0.5, 3: 0.3},
        3: {0: 0.1, 1: 0.2, 2: 0.2, 3: 0.5}
    })
    
    plane_size = 50
    num_rows = plane_size // 10
    cell_width = 10
    
    building_heights = city.get_building_heights(num_rows, num_rows)

    
    # Delete all objects in the scene that aren't cameras or lights
    bpy.ops.object.mode_set(mode = 'OBJECT')
    skip_delete_objects = set(['CAMERA', 'LIGHT'])

    for o in bpy.context.scene.objects:
        if o.type in skip_delete_objects:
            o.select_set(False)
        else:
            o.select_set(True)

    bpy.ops.object.delete() 
    
    for r in range(num_rows):
        for c in range(num_rows):
            current_height = building_heights[r][c] * 5
            current_num_sides = building_heights[r][c]
            if current_height == 0:
                continue
            bpy.ops.mesh.primitive_cylinder_add(location=(r * cell_width - (plane_size / 2 - 5), c * cell_width - (plane_size / 2 - 5), current_height / 2.0), vertices = current_num_sides * 3 , radius = 4.0, depth = current_height, rotation = (0, 0, math.pi / 4))
            
            # Make and assign new material for current building
            mat = bpy.data.materials.new('Material' + str(r) + str(c))
            mat.diffuse_color = (current_num_sides / 4, current_num_sides / 4, current_num_sides / 4, 1)    
            bpy.context.object.data.materials.append(mat)
            
    # Create the base and add color to it
    bpy.ops.mesh.primitive_plane_add(size = plane_size, location = (0, 0, 0))
    mat = bpy.data.materials.new('Base')
    mat.diffuse_color = (0.1, 0.1, 0.1, 1)    
    bpy.context.object.data.materials.append(mat)


if __name__ == '__main__':
    main()
    
                
