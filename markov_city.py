import numpy as np
import math
import bpy

class MarkovCity:
    """
    Generates a small-scale city in Blender using a Markov model. The heights and number of sides of each building
    are based on a Markov model, and each building's color is set with a separate Markov model. In addition, shorter
    buildings are slightly lighter in color and taller buildings are a bit darker.
    """
    # Affects how much space is between each building
    PADDING_FACTOR = 10 
    # Controls how strong of an influence the height of a building has on the shade of its color. The smaller the value, 
    # the larger the influence.
    HEIGHT_FACTOR_FOR_COLOR_SHADE = 3 
    BASE_COLOR = (0.1, 0.1, 0.1, 1)
    
    def __init__(self, height_transition_matrix, height_prior_vector, color_transition_matrix, color_prior_vector):
        """
        Uses a Markov model to generate a small-scale city in Blender.
        Args:
            height_transition_matrix (dict): height transition probabilities for the Markov model 
            height_prior_vector (dict): the initial state vector for heights
            color_transition_matrix (dict): color transition probabilities for the Markov model
            color_prior_vector (dict): the initial state vector for color
        """
        self.height_transition_matrix = height_transition_matrix
        self.height_prior_vector = height_prior_vector
        self.heights = list(height_transition_matrix.keys())
        self.max_height = max(self.heights)
        self.color_transition_matrix = color_transition_matrix
        self.color_prior_vector = color_prior_vector
        self.colors = list(color_transition_matrix)


    def get_next_height(self, current_height):
        """
        Determines the height of the next building based on the height of the current one.
        Args:
            current_height (int): the height of the current building
        """
        return np.random.choice(
            self.heights, 
            p = [self.height_transition_matrix[current_height][next_height] for next_height in self.heights] 
        )

    
    def get_next_color(self, current_color):
        """
        Determines the color of the next building based on the color of the current one.
        Args:
            current_color (tuple(float, float, float)): the RGB value of the current color where each value is in the range [0, 1]
        """
        # Select the index of the color that should be returned since numpy expects the first argument to be a 1D array, and it is
        # not in this case.
        index = np.random.choice(
            range(len(self.colors)), 
            p = [self.color_transition_matrix[current_color][next_color] for next_color in self.colors] 
        )
        return self.colors[index]



    def get_building_info(self, num_rows, num_cols):
        """
        Returns a 2D array containing the heights and color for each building in the grid.
        Args:
            num_rows (int): the number of rows in the grid
            num_cols (int): the number of columns in the grid
        """
        building_info = [[None] * num_cols for r in range(num_rows)]

        # Get initial height and color
        current_height = np.random.choice(
            self.heights, 
            p = [self.height_prior_vector[next_height] for next_height in self.heights] 
        )
        current_color_index = np.random.choice(
            range(len(self.colors)), 
            p = [self.color_prior_vector[next_color] for next_color in self.colors] 
        )
        current_color = self.colors[current_color_index]

        for row in range(num_rows):
            for col in range(num_cols):
                next_height = self.get_next_height(current_height)
                next_color = self.get_next_color(current_color)
                building_info[row][col] = (next_height, next_color)
                current_height = next_height
                current_color = next_color

        return building_info

    
    def clear_city(self):
        """
        Removes the current city from the scene.
        """
        # Prevents an exception from being thrown if there are no active objects in the scene when clearing it
        try:
            bpy.ops.object.mode_set(mode = 'OBJECT')
        except:
            pass

        skip_delete_objects = set(['CAMERA', 'LIGHT'])

        # Delete all objects in the scene that aren't cameras or lights
        for o in bpy.context.scene.objects:
            if o.type in skip_delete_objects:
                o.select_set(False)
            else:
                o.select_set(True)

        bpy.ops.object.delete() 


    def add_building(self, x, y, radius, number_of_sides, height, color):
        """
        Adds a building the specified coordinates based on the parameter values.
        Args:
            x (float):  the x value for where the building should be created in the scene
            y (float): the y value for where the building should be created in the scene
            radius (float): the radius of the building
            number_of_sides (int): the number of sides on the top and bottom faces of the building
            height (float): the height of the building
            color (tuple(float, float, float)): the color of the building as an RGB value
        """
        # Create the building
        bpy.ops.mesh.primitive_cylinder_add(
            location = (x, y, height / 2), 
            vertices = number_of_sides, 
            radius = radius, 
            depth = height, 
            # Rotating by pi / 4 causes the rectangular buildings to line up with the grid
            rotation = (0, 0, math.pi / 4) 
        )
        
        # Create and assign new material for current building to set color
        red_value, green_value, blue_value = color
        mat = bpy.data.materials.new('Material' + str(len(bpy.data.materials) + 1))
        # Color value influences how dark or light the color is. A larger color value corresponds to a darker color.
        # Use number_of_sides to get the non-scaled height 
        color_value = number_of_sides / (self.max_height * MarkovCity.HEIGHT_FACTOR_FOR_COLOR_SHADE)
        mat.diffuse_color = (red_value - color_value, green_value - color_value, blue_value - color_value, 1)    
        bpy.context.object.data.materials.append(mat)


    def create_city(self, base_size, cell_width = 10, height_scale_factor = 2.5):
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
        displacement = base_size / 2 - (cell_width / 2)    
        building_info = self.get_building_info(num_rows, num_rows)
        
        for row in range(num_rows):
            for col in range(num_rows):
                current_height, current_color = building_info[row][col]
        
                # If current_height <= 0, don't place a building in this cell
                if current_height <= 0:
                    continue

                scaled_height = current_height * height_scale_factor
                x_coord = row * cell_width - displacement
                y_coord = col * cell_width - displacement
                current_radius = cell_width / 2 - building_padding
                # Create the building. Pass in current_height to be used as the building's number of sides
                self.add_building(x_coord, y_coord, current_radius, current_height, scaled_height, current_color)

        # Create the base and add color to it
        bpy.ops.mesh.primitive_plane_add(size = base_size, location = (0, 0, 0))
        mat = bpy.data.materials.new('Base')
        mat.diffuse_color = MarkovCity.BASE_COLOR  
        bpy.context.object.data.materials.append(mat)


def main():
    """
    The main method for the program. Initializes a MarkovCity object and uses it to create a city based on some
    transition matrix.
    """
    height_prior_vector = {0: 0.1, 1: 0.1, 2: 0.1, 3: 0.1, 4: 0.1, 5: 0.1, 6: 0.1, 7: 0.1, 8: 0.1, 9: 0.1}
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
    colors_prior_vector = {(0.9, 0.4, 0.4): 0.3, (0.16, 0.46, 0.9): 0.4, (1, 0.7, 0.07): 0.3}
    colors = {
        (0.9, 0.4, 0.4): {(0.9, 0.4, 0.4): 0.3, (0.16, 0.46, 0.9): 0.4, (1, 0.7, 0.07): 0.3},
        (0.16, 0.46, 0.9): {(0.9, 0.4, 0.4): 0.3, (0.16, 0.46, 0.9): 0.4, (1, 0.7, 0.07): 0.3},
        (1, 0.7, 0.07): {(0.9, 0.4, 0.4): 0.3, (0.16, 0.46, 0.9): 0.4, (1, 0.7, 0.07): 0.3}
    }

    city = MarkovCity(favor_mid_heights_9, height_prior_vector, colors, colors_prior_vector)

    city.create_city(100)
    
    
if __name__ == '__main__':
    main()
    