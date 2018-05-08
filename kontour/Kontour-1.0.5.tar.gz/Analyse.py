from music21 import clef, stream, humdrum, note, editorial, metadata
from suffix_trees import STree
from Score import Score


class Analyse:

    def __init__(self, export, parsed_score):
        self.viewers = export
        self.score = parsed_score

    def score_refresh(self, score):
        self.score = score

    # Returns the indexs of the begining of all substring instances
    def find_sequence(self, sub_string):
        # Define list of lists that will store the start index of found substrings
        listindex = []
        # Show the user each pattern that was found by common_patterns
        print(sub_string)
        # For the length of the main string
        for i in range(0, len(self.score.contour_abstract)):
            # Convert self.score.contour_abstract to string from list
            string = ''.join(self.score.contour_abstract[i])
            # Declare listindex_tmp list which will hold the indexes
            listindex_tmp = []
            # Pattern length
            pattern_length = len(sub_string)+1
            # If the pattern is found return the index
            j = string.find(sub_string)
            # While find is finding substrings
            while j >= 0:
                # If the match hasn't been found already
                if (not(listindex_tmp)):
                    # Append (start, end) of substring
                    listindex_tmp.append((j, j + pattern_length))
                # Call find() recurively
                j = string.find(sub_string, j + 1)
            # Append the found matches as a list to listindex
            listindex.append(listindex_tmp)

        return len(sub_string), listindex

    # Print the found sequences in the music
    def Search_Score(self, filename, sequence):
        # Get the series of notes
        voice_notes = self.score.voice_notes
        # Get the start indexs of the matching substrings in the sequence
        seq_len, match_index = self.find_sequence(sequence)
        # Get a copy of the score
        match_composition = self.score.parsed_score
        # Edit the title of the score to indicate the sequence
        match_composition.metadata.title = match_composition.metadata.title + ': ' + sequence
        print(match_index)
        # For each match
        for i in range(0, len(match_index)):
            # keep_note_index = []
            # for boundary in match_index[i]:
            #     keep_note_index += list(range(boundary[0], boundary[1]))
            for elem in voice_notes[i]:
                if not(any(lower <= voice_notes[i].index(elem) < upper for (lower, upper) in match_index[i])):
                # if voice_notes[i].index(elem) not in keep_note_index:
                    r = note.SpacerRest(type=elem.duration.type)
                    loc = voice_notes[i].index(elem)
                    match_composition.parts[i].flat.replace(elem, r)
        if len(self.viewers) == 2:
            match_composition.write('lily.pdf', fp = 'Results/' + self.score.name + '_' + sequence)
            match_composition.show()
        elif self.viewers[0] == "MuseScore":
            match_composition.show()
        elif self.viewers[0] == "LillyPond":
            match_composition.write('lily.pdf', fp = 'Results/' + self.score.name + '_' + sequence)

    def common_patterns(self, sequences):

        list_of_sequences = []
        # Just a bit of house keeping, the scores are in the form of lists but
        # I need them as strings in only this function. Hence the "hack-ish" code
        for sequence in sequences:
            voice = "".join(sequence)
            list_of_sequences.append(voice)

        # To be as fast as possible we window search the smallest string
        list_of_sequences = sorted(list_of_sequences, key=len)
        # Construct the genralised suffix tree
        suffix_tree = STree.STree(list_of_sequences)
        # List of common sequences
        matches = []
        # stores potential window size for next itteration
        potential_window_sizes = []
        # search window size
        window_size = len(suffix_tree.lcs())
        # Lower bound of the search window
        window_lower = 0
        # Upper bound of the search window
        window_upper = window_lower + window_size
        # If window size is 0 then suffix_tree.lcs() returned ""
        if window_size == 0:
            print('no match')
        elif suffix_tree.lcs() == list_of_sequences[0]:
            matches.append(suffix_tree.lcs())
            return matches
        # If there was a match then append it
        else:
            matches.append(suffix_tree.lcs())

        # Do this until the window size is 0
        while window_size != 0:
            # Create a copy of the sequence list
            list_of_sequences_copy = list_of_sequences[:]
            # Redefine the first element of the copy to only the elements in the window
            list_of_sequences_copy[0] = list_of_sequences[0][window_lower:window_upper]
            # Rebuild the suffix tree
            suffix_tree = STree.STree(list_of_sequences_copy)
            # If an unseen match is found and is not empty then append it
            if not suffix_tree.lcs() in matches and suffix_tree.lcs() != "" and len(suffix_tree.lcs())>= 5:
                matches.append(suffix_tree.lcs())
                potential_window_sizes.append(len(suffix_tree.lcs()))
            # Shift the window one to the right
            window_lower += 1
            window_upper += 1
            # Once the upper bound of the window touches the end or the string
            if window_upper == len(list_of_sequences[0]) - 1:
                # Decrease the window size by one
                window_size -= 1
                if potential_window_sizes:
                    if max(potential_window_sizes) < window_size:
                        window_size = max(potential_window_sizes)
                # Reset the window back to the start
                window_lower = 0
                window_upper = window_lower + window_size
        return matches
