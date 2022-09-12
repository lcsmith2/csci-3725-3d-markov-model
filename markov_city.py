import numpy as np
import math
import bpy

class MarkovCity:
    """
    Generates a small-scale city in Blender using a Markov model.
    """
    PADDING_FACTOR = 10 # Affects how much space is between each building
    
    def __init__(self, transition_matrix):
        """
        Uses a Markov model to generate a small-scale city in Blender.
        Args:
            transition_matrix (dict): transition probabilities for the Markov model
        """
        self.transition_matrix = transition_matrix
        self.heights = list(transition_matrix.keys())
        self.max_height = max(self.heights)


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

    
    def clear_city(self):
        """
        Removes the current city from the scene.
        """
        bpy.ops.object.mode_set(mode = 'OBJECT')
        skip_delete_objects = set(['CAMERA', 'LIGHT'])

        # Delete all objects in the scene that aren't cameras or lights
        for o in bpy.context.scene.objects:
            if o.type in skip_delete_objects:
                o.select_set(False)
            else:
                o.select_set(True)

        bpy.ops.object.delete() 


    def create_city(self, base_size, cell_width = 10, height_scale_factor = 3.0):
        """
        Creates a city in Blender where the heights are based off of the transition matrix. Each cell contains
        a building, and there are (base_size // cell_width) by (base_size // cell_width) buildings in the city.
        Args:
            base_size (int): the width (and height) of the square city base
            cell_width (int): the width of each square cell within the grid
            height_scale_factor (float): the factor each building height will be scaled by
        """
        self.clear_city()
        num_rows = base_size // cell_width
        building_padding = cell_width / MarkovCity.PADDING_FACTOR
        
        building_heights = self.get_building_heights(num_rows, num_rows)
        
        for row in range(num_rows):
            for col in range(num_rows):
                current_height = building_heights[row][col] * height_scale_factor
                # The number of sides for the current building is equal to its generated height
                current_num_sides = building_heights[row][col] 
                if current_height == 0:
                    continue
                bpy.ops.mesh.primitive_cylinder_add(
                    location = (
                        row * cell_width - (base_size / 2 - (cell_width / 2)), 
                        col * cell_width - (base_size / 2 - (cell_width / 2)), 
                        current_height / 2
                    ), 
                    vertices = current_num_sides, 
                    radius = cell_width / 2 - building_padding, 
                    depth = current_height, 
                    rotation = (0, 0, math.pi / 4) # Rotating by pi / 4 causes the rectangular buildings to line up with the grid
                )
                
                # Create and assign new material for current building to set color
                mat = bpy.data.materials.new('Material' + str(row) + str(col))
                color_value = current_num_sides / self.max_height
                mat.diffuse_color = (color_value, color_value, color_value, 1)    
                bpy.context.object.data.materials.append(mat)
            
        # Create the base and add color to it
        bpy.ops.mesh.primitive_plane_add(size = base_size, location = (0, 0, 0))
        mat = bpy.data.materials.new('Base')
        mat.diffuse_color = (0.1, 0.1, 0.1, 1)    
        bpy.context.object.data.materials.append(mat)


def main():
    """
    The main method for the program. Initializes a MarkovCity object and uses it to create a city based on some
    transition matrix.
    """
    equal_prob_height_9 = {
        0: {0: 0.1, 1: 0.1, 2: 0.1, 3: 0.1, 4: 0.1, 5: 0.1, 6: 0.1, 7: 0.1, 8: 0.1, 9: 0.1},
        1: {0: 0.1, 1: 0.1, 2: 0.1, 3: 0.1, 4: 0.1, 5: 0.1, 6: 0.1, 7: 0.1, 8: 0.1, 9: 0.1},
        2: {0: 0.1, 1: 0.1, 2: 0.1, 3: 0.1, 4: 0.1, 5: 0.1, 6: 0.1, 7: 0.1, 8: 0.1, 9: 0.1},
        3: {0: 0.1, 1: 0.1, 2: 0.1, 3: 0.1, 4: 0.1, 5: 0.1, 6: 0.1, 7: 0.1, 8: 0.1, 9: 0.1},
        4: {0: 0.1, 1: 0.1, 2: 0.1, 3: 0.1, 4: 0.1, 5: 0.1, 6: 0.1, 7: 0.1, 8: 0.1, 9: 0.1},
        5: {0: 0.1, 1: 0.1, 2: 0.1, 3: 0.1, 4: 0.1, 5: 0.1, 6: 0.1, 7: 0.1, 8: 0.1, 9: 0.1},
        6: {0: 0.1, 1: 0.1, 2: 0.1, 3: 0.1, 4: 0.1, 5: 0.1, 6: 0.1, 7: 0.1, 8: 0.1, 9: 0.1},
        7: {0: 0.1, 1: 0.1, 2: 0.1, 3: 0.1, 4: 0.1, 5: 0.1, 6: 0.1, 7: 0.1, 8: 0.1, 9: 0.1},
        8: {0: 0.1, 1: 0.1, 2: 0.1, 3: 0.1, 4: 0.1, 5: 0.1, 6: 0.1, 7: 0.1, 8: 0.1, 9: 0.1},
        9: {0: 0.1, 1: 0.1, 2: 0.1, 3: 0.1, 4: 0.1, 5: 0.1, 6: 0.1, 7: 0.1, 8: 0.1, 9: 0.1}
    }
    favor_mid_heights_9 = {
        0: {0: 0, 1: 0.15, 2: 0.2, 3: 0.1, 4: 0.15, 5: 0.1, 6: 0.1, 7: 0.08, 8: 0.07, 9: 0.05},
        1: {0: 0.15, 1: 0, 2: 0.15, 3: 0.1, 4: 0.1, 5: 0.2, 6: 0.1, 7: 0.08, 8: 0.07, 9: 0.05},
        2: {0: 0.1, 1: 0.15, 2: 0, 3: 0.15, 4: 0.2, 5: 0.1, 6: 0.1, 7: 0.08, 8: 0.07, 9: 0.05},
        3: {0: 0.1, 1: 0.1, 2: 0.15, 3: 0, 4: 0.15, 5: 0.1, 6: 0.2, 7: 0.08, 8: 0.07, 9: 0.05},
        4: {0: 0.1, 1: 0.1, 2: 0.15, 3: 0.2, 4: 0, 5: 0.15, 6: 0.1, 7: 0.08, 8: 0.07, 9: 0.05},
        5: {0: 0.1, 1: 0.1, 2: 0.1, 3: 0.15, 4: 0.2, 5: 0, 6: 0.15, 7: 0.08, 8: 0.07, 9: 0.05},
        6: {0: 0.1, 1: 0.1, 2: 0.1, 3: 0.1, 4: 0.15, 5: 0.18, 6: 0, 7: 0.15, 8: 0.07, 9: 0.05},
        7: {0: 0.1, 1: 0.1, 2: 0.1, 3: 0.1, 4: 0.13, 5: 0.2, 6: 0.15, 7: 0, 8: 0.07, 9: 0.05},
        8: {0: 0.1, 1: 0.1, 2: 0.15, 3: 0.15, 4: 0.1, 5: 0.1, 6: 0.1, 7: 0.15, 8: 0, 9: 0.05},
        9: {0: 0.1, 1: 0.1, 2: 0.1, 3: 0.1, 4: 0.15, 5: 0.1, 6: 0.1, 7: 0.1, 8: 0.15, 9: 0}
    }

    city = MarkovCity(favor_mid_heights_9)

    city.create_city(100)
    
    
if __name__ == '__main__':
    main()
    