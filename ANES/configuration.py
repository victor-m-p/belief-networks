import numpy as np 
import pandas as pd 
import random 

class Configuration: 
    def __init__(self, identifier, states, probabilities):
        self.id = identifier
        self.states = states # why does states[states <= 0] = 0 not work? 
        self.probabilities = probabilities
        self.configuration = states[self.id]
        self.p = probabilities[self.id]
        self.len = len(self.configuration)
        
        # things for caching
        self._neighbor_ids = None # cache 
        self._hamming_neighbors = None # cache
        self._neighbor_probabilities = None # cache 

    def to_string(self):
        return "".join([str(x) if x == 1 else str(0) for x in self.configuration])

    @staticmethod
    def normalize(array): 
        array = array / array.min()
        array = array / array.sum()
        return array 

    @staticmethod
    def flip(x): 
        return 0 if x == 1 else 1 
    
    def flip_at_index(self, index): 
        new_arr = np.copy(self.configuration)
        new_arr[index] = self.flip(new_arr[index])
        return new_arr 
    
    def flip_at_indices(self, indices): 
        new_arr = np.copy(self.configuration)
        for ind in indices: 
            new_arr[ind] = self.flip(new_arr[ind])
        return new_arr 

    @property # calculate lazy 
    def hamming_neighbors(self):
        if self._hamming_neighbors is None: 
             hamming_list = [self.flip_at_index(num) for num, _ in enumerate(self.configuration)]
             self._hamming_neighbors = np.array(hamming_list)     
        return self._hamming_neighbors
 
    @property # calculate lazy
    def neighbor_ids(self):
        if self._neighbor_ids is None: 
            hamming_array = self.hamming_neighbors # calls cached or computes
            self._neighbor_ids = np.array(
                [np.where((self.states == i).all(1))[0][0] for i in hamming_array]
            )
        return self._neighbor_ids
 
    @property # calculate lazy
    def neighbor_probabilities(self): 
        if self._neighbor_probabilities is None: 
            self._neighbor_probabilities = self.probabilities[self.neighbor_ids]
        return self._neighbor_probabilities 
    
    #def id_and_prob_of_neighbors(self):
    #    hamming_array = self.hamming_neighbors()
    #    self.id_neighbor = np.array([np.where((self.states == i).all(1))[0][0] for i in hamming_array])
    #    self.p_neighbor = self.probabilities[self.id_neighbor]
    #    return self.id_neighbor, self.p_neighbor
    
    def p_move(self, summary=True):
        prob_moves = 1 - (self.p / (self.p + self.neighbor_probabilities))
        return np.mean(prob_moves) if summary else prob_moves
   
    # some issue here where we get too many local maxima  
    def find_all_local_maxima(self):
        """
        Compute local maxima and basins of attraction for all configurations.
        Returns:
            local_maxima: Set of all local maxima indices.
            basin_map: Dictionary mapping each configuration index to its local maximum.
        """
        basin_map = {}  # Maps each configuration index to its local maximum
        local_maxima = set()  # Set of unique local maxima

        def find_local_max_with_cache(start_id):
            """
            Find the local maximum for a given configuration index using caching.
            """
            if start_id in basin_map:  # If already computed, return cached result
                return basin_map[start_id]

            current_id = start_id
            visited = []  # Track the path of visited configurations

            while True:
                neighbor_ids = self.neighbor_ids  # Neighbors of the current config
                neighbor_probs = self.probabilities[neighbor_ids]  # Probabilities of neighbors

                # Find the neighbor with the maximum probability
                max_index = np.argmax(neighbor_probs)

                # Check if the current configuration is better than the best neighbor
                if self.probabilities[current_id] >= neighbor_probs[max_index]:
                    local_maxima.add(current_id)  # It's a local maximum
                    break

                visited.append(current_id)  # Record the current configuration
                current_id = neighbor_ids[max_index]  # Move to the best neighbor

            # Cache results for all visited configurations
            for v in visited:
                basin_map[v] = current_id
            basin_map[start_id] = current_id  # Cache for the start configuration
            return current_id

        # Compute for all configurations
        for config_id in range(len(self.states)):
            find_local_max_with_cache(config_id)

        return local_maxima, basin_map

    
    def move(self, N): 
        targets = random.sample(range(self.len), N)
        prob_move = self.p_move(summary = False)
        prob_targets = prob_move[targets]
        move_bin = prob_targets >= np.array([random.uniform(0, 1) for _ in range(N)])
        
        if not any(move_bin):
            return Configuration(self.id, self.states, self.probabilities)
        if N == 1: 
            new_id = self.id_neighbor[targets][0]
            return Configuration(new_id, self.states, self.probabilities)
        else: 
            feature_changes = [x for x, y in zip(targets, move_bin) if y]
            new_configuration = self.flip_at_indices(feature_changes)
            new_id = np.where(np.all(self.states == new_configuration,
                                    axis = 1))[0][0]
            return Configuration(new_id, self.states, self.probabilities)

    def hamming_distance(self, other): 
        x = self.configuration 
        y = other.configuration
        array_difference = np.not_equal(x, y)
        h_distance = np.sum(array_difference)
        return h_distance

    def answer_comparison(self, other, question_reference):  
        answers = pd.DataFrame({self.id: self.configuration, other.id: other.configuration})
        answers = pd.concat([question_reference, answers], axis = 1)
        return answers

    def overlap(self, other, question_reference):
        answers = self.answer_comparison(other, question_reference)
        return answers[answers[self.id] == answers[other.id]]

    def diverge(self, other, question_reference):  
        answers = self.answer_comparison(other, question_reference)
        answers_diverge = answers[answers[self.id] != answers[other.id]]
        return answers_diverge
    
    def transition_probs_to_neighbors(self, question_reference):
        neighbor_ids, neighbor_probs = self.id_and_prob_of_neighbors()
        df = pd.DataFrame({'config_id': neighbor_ids, 'config_prob': neighbor_probs})
        df = pd.concat([df, question_reference], axis=1)
        df[self.id] = self.configuration
        df['transition_prob'] = df['config_prob'] / df['config_prob'].sum()
        return df.sort_values('transition_prob', ascending=False)