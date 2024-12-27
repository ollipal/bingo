import json
import sys
from bingo import generate_cards

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

    cards = generate_cards(language, num_cards)
    save_cards_to_json(cards, language)

    # Save to JSON
    print(f"Successfully generated {num_cards} bingo card(s) in {language}.json")
        


if __name__ == "__main__":
    main()