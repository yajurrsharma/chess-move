from flask import Flask, request, jsonify
from english_words import get_english_words_set
import math
from collections import defaultdict

app = Flask(__name__)

class WordleSolver:
    def __init__(self):
        self.possible_words = list(get_english_words_set(["web2"], lower=True))
        self.word_length = 5
        self.green_letters = {}  # {position: letter}
        self.yellow_letters = defaultdict(list)  # {letter: [positions]}
        self.gray_letters = set()
        self.filter_words()
    
    def reset(self):
        self.__init__()

    def filter_words(self):
        """Filter possible words based on current constraints"""
        filtered = []
        for word in self.possible_words:
            if len(word) != self.word_length:
                continue
            
            # Check green letters (correct position)
            match = True
            for pos, letter in self.green_letters.items():
                if word[pos] != letter:
                    match = False
                    break
            if not match:
                continue
                
            # Check yellow letters (present but wrong position)
            for letter, positions in self.yellow_letters.items():
                if letter not in word:
                    match = False
                    break
                for pos in positions:
                    if word[pos] == letter:
                        match = False
                        break
                if not match:
                    break
            if not match:
                continue
                
            # Check gray letters (not present)
            for letter in self.gray_letters:
                if letter in word and letter not in self.green_letters.values() and letter not in self.yellow_letters:
                    match = False
                    break
            if not match:
                continue
                
            filtered.append(word)
            
        self.possible_words = filtered
    
    def update_constraints(self, row_data):
        """Update constraints based on user input"""
        for i, box in enumerate(row_data):
            letter = box['letter'].lower()
            color = box['color']
            
            if color == 'green':
                self.green_letters[i] = letter
            elif color == 'yellow':
                self.yellow_letters[letter].append(i)
            elif color == 'gray':
                self.gray_letters.add(letter)
        
        self.filter_words()
    
    def get_suggestions(self):
        """Get suggested next guesses based on letter frequency"""
        if not self.possible_words:
            return []
            
        # Calculate letter frequencies
        letter_scores = defaultdict(int)
        for word in self.possible_words:
            for letter in set(word):
                letter_scores[letter] += 1
        
        # Score words based on unique letter frequencies
        word_scores = []
        for word in self.possible_words:
            score = sum(letter_scores[letter] for letter in set(word))
            word_scores.append((word, score))
        
        # Sort by score (descending) and return top 10
        word_scores.sort(key=lambda x: -x[1])
        return [word for word, score in word_scores[:10]]

@app.route('/solve_wordle', methods=['POST'])
def solve_wordle():
    data = request.json
    solver = WordleSolver()
    
    for row in data['rows']:
        solver.update_constraints(row)
    
    suggestions = solver.get_suggestions()
    return jsonify({
        'possible_words': solver.possible_words,
        'suggestions': suggestions,
        'count': len(solver.possible_words)
    })

if __name__ == '__main__':
    app.run(debug=True)