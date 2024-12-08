import sys
import csv
import json
import random

def read_words(filename, language):
    """Read words from CSV file for specified language."""
    words = []
    with open(filename, 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            if language in row:
                words.append(row[language])
    return words

def generate_bingo_card(words):
    """Generate a single randomized bingo card."""
    # Ensure we have exactly 25 words
    if len(words) != 25:
        raise ValueError(f"Expected 25 words, but got {len(words)}")
    
    # Create a copy and shuffle it
    card_words = words.copy()
    random.shuffle(card_words)
    
    return card_words

def generate_multiple_cards(words, num_cards):
    """Generate specified number of unique bingo cards."""
    cards = []
    for _ in range(num_cards):
        card = generate_bingo_card(words)
        cards.append(card)
    return cards

def save_cards_to_json(cards, language):
    """Save generated cards to JSON file."""
    data = {"cards": cards}
    with open(f"{language}.json", 'w', encoding='utf-8') as file:
        json.dump(data, file, indent=2, ensure_ascii=False)

def main():
    if len(sys.argv) != 3:
        print("Usage: python3 bingo.py <language> <number_of_cards>")
        sys.exit(1)
    
    language = sys.argv[1]
    try:
        num_cards = int(sys.argv[2])
    except ValueError:
        print("Error: Number of cards must be an integer")
        sys.exit(1)
    
    try:
        # Read questions from CSV file
        words = read_words('questions.csv', language)
        
        # Validate we have enough words
        if len(words) < 25:
            print(f"Error: Need at least 25 words, but only found {len(words)}")
            sys.exit(1)
        
        # Generate cards
        cards = generate_multiple_cards(words[:25], num_cards)
        
        # Save to JSON
        save_cards_to_json(cards, language)
        print(f"Successfully generated {num_cards} bingo card(s) in {language}.json")
        
    except FileNotFoundError:
        print("Error: words.csv file not found")
        sys.exit(1)
    except KeyError:
        print(f"Error: Language '{language}' not found in CSV file")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()