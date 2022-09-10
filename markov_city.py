import numpy as np

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
        0: {0: 0.3, 1: 0.2, 2: 0.3, 3: 0.2},
        1: {0: 0.3, 1: 0.2, 2: 0.3, 3: 0.2},
        2: {0: 0.3, 1: 0.2, 2: 0.3, 3: 0.2},
        3: {0: 0.3, 1: 0.2, 2: 0.3, 3: 0.2}
    })
    print(city.get_building_heights(3, 3))


if __name__ == '__main__':
    main()
    
                
