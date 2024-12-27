from typing import List, Dict, Tuple, Set
from schemas import BingoData, Translation, BingoCard, Quest, Phrase
import random

def generate_cards(data: BingoData, shuffle: bool = True) -> tuple[List[Dict[str, any]] | None, str | None]:
    """
    Generate bingo cards based on the provided data.
    
    Args:
        data: BingoData containing quests, phrases and difficulties pattern
        shuffle: Whether to shuffle the phrases or maintain order (for testing)
        
    Returns:
        Tuple of (cards, error) where:
        - cards is a list of dicts with quest name and card content if successful, None if failed
        - error is a string describing the error if failed, None if successful
    """
    cards = []
    
    for quest in data.quests:
        phrase_pools: Dict[str, Dict[str, List[str]]] = {}
        
        # Initialize pools for each phrase type
        for phrase_type in quest.types:
            phrase_pools[phrase_type] = {}
            type_phrases = [q for q in data.phrases if q.type == phrase_type]
            
            for q in type_phrases:
                valid_translations = [
                    trans.text 
                    for trans in q.translations 
                    if trans.language == quest.language
                ]
                if valid_translations:
                    if q.difficulty not in phrase_pools[phrase_type]:
                        phrase_pools[phrase_type][q.difficulty] = []
                    phrase_pools[phrase_type][q.difficulty].extend(valid_translations)

        # Count needed phrases by difficulty
        needed_by_difficulty = {}
        for diff in data.difficulties:
            if diff not in needed_by_difficulty:
                needed_by_difficulty[diff] = 0
            needed_by_difficulty[diff] += 1
            
        # Check availability before starting to fill card
        for required_difficulty in needed_by_difficulty:
            total_available = sum(
                len(phrase_pools.get(qtype, {}).get(required_difficulty, []))
                for qtype in quest.types
            )
            if total_available < needed_by_difficulty[required_difficulty]:
                by_type = {
                    qtype: len(phrase_pools.get(qtype, {}).get(required_difficulty, []))
                    for qtype in quest.types
                }
                type_counts = ", ".join(f"{qtype}: {count}" for qtype, count in by_type.items())
                or_types = "' or '".join(quest.types)
                return None, (
                    f"Could not generate a bingo card for quest {quest.name}: "
                    f"not enough {quest.language} phrases with difficulty '{required_difficulty}' and type '{or_types}'. "
                    f"{needed_by_difficulty[required_difficulty]} required, available by type: {type_counts}."
                )

        # Prepare card with empty slots
        card_size = len(data.difficulties)
        card = [None] * card_size
        
        # Group positions by difficulty for random assignment
        positions_by_difficulty = {}
        for pos, diff in enumerate(data.difficulties):
            if diff not in positions_by_difficulty:
                positions_by_difficulty[diff] = []
            positions_by_difficulty[diff].append(pos)

        # Fill card with phrases
        for difficulty in needed_by_difficulty:
            # Get all positions for this difficulty
            difficulty_positions = positions_by_difficulty[difficulty].copy()
            
            # For each position of this difficulty
            while difficulty_positions:
                if shuffle:
                    # Choose a random position for this difficulty
                    position = random.choice(difficulty_positions)
                else:
                    # Take the first position in testing mode
                    position = difficulty_positions[0]
                difficulty_positions.remove(position)
                
                # Try each type in order of preference (quest.types order)
                phrase_found = False
                for phrase_type in quest.types:
                    if (phrase_type in phrase_pools and 
                        difficulty in phrase_pools[phrase_type] and 
                        phrase_pools[phrase_type][difficulty]):
                        phrases = phrase_pools[phrase_type][difficulty]
                        if shuffle:
                            selected = random.choice(phrases)
                        else:
                            selected = phrases[0]
                        phrases.remove(selected)
                        card[position] = selected
                        phrase_found = True
                        break
                
                if not phrase_found:
                    raise RuntimeError(f"Failed to find phrase for {difficulty} despite availability check")

        # Verify no empty slots
        if None in card:
            raise RuntimeError("Card contains empty slots despite availability check")
            
        cards.append({
            'quest': quest.name,
            'card': card
        })
    
    return cards, None

if __name__ == '__main__':
    import unittest
    
    class TestGenerateCardsNoShuffle(unittest.TestCase):
        def setUp(self):
            # Create test data - generate translations with type in the text
            self.test_translations_en = [
                Translation(language="english", text=f"Type{t} {d} Phrase {i}")
                for t in range(1, 4)  # 3 types 
                for d in ["easy", "medium", "hard"]
                for i in range(100)  # 100 phrases per type-difficulty combo
            ]
            
            # Create phrases with different difficulties - 100 each type, evenly distributed
            def create_phrases(type_num: int) -> List[Phrase]:
                phrases = []
                idx = 0
                for difficulty in ["easy", "medium", "hard"]:
                    for _ in range(100):
                        trans_idx = (type_num - 1) * 300 + idx  # 300 = 3 difficulties * 100 phrases
                        phrases.append(Phrase(
                            translations=[self.test_translations_en[trans_idx]],
                            type=f"type{type_num}",
                            difficulty=difficulty
                        ))
                        idx += 1
                return phrases

            # Create test quests
            self.test_quests = [
                Quest(
                    name="Test Quest 1",
                    language="english",
                    types=["type1", "type2", "type3"]
                ),
                Quest(
                    name="Test Quest 2",
                    language="english",
                    types=["type2", "type3", "type1"]
                )
            ]
            
            # Create test data with repeated difficulty pattern
            self.test_difficulties = ["easy"] * 3 + ["medium"] * 3 + ["hard"] * 3
            
            # Create test phrases - 100 of each type/difficulty
            self.test_phrases = []
            for type_num in range(1, 4):
                self.test_phrases.extend(create_phrases(type_num))
            
            # Create test BingoData
            self.test_data = BingoData(
                quests=self.test_quests,
                phrases=self.test_phrases,
                difficulties=self.test_difficulties
            )

        def test_generate_cards_without_shuffle(self):
            # Generate cards without shuffling
            cards, error = generate_cards(self.test_data, shuffle=False)
            
            self.assertIsNone(error)
            self.assertIsNotNone(cards)
            
            # Test number of cards matches number of quests
            self.assertEqual(len(cards), len(self.test_quests))
            
            # Test first card
            first_card = cards[0]['card']
            first_quest = cards[0]['quest']
            self.assertEqual(len(first_card), 9)
            self.assertEqual(first_quest, "Test Quest 1")
            
            # Each phrase should contain "Type1" in text (preferred type)
            for text in first_card:
                self.assertIn("Type1", text)
            
            # Test second card
            second_card = cards[1]['card']
            second_quest = cards[1]['quest']
            self.assertEqual(len(second_card), 9)
            self.assertEqual(second_quest, "Test Quest 2")
            
            # Each phrase should contain "Type2" in text (preferred type)
            for text in second_card:
                self.assertIn("Type2", text)
            
            # No phrase should be repeated between cards
            all_phrases = set()
            for card_data in cards:
                for phrase in card_data['card']:
                    self.assertNotIn(phrase, all_phrases, "Phrase was repeated")
                    all_phrases.add(phrase)

    class TestGenerateCardsWithShuffle(unittest.TestCase):
        def test_randomized_positions_and_types(self):
            # Create test data with multiple types
            phrases = [
                *[Phrase(
                    translations=[Translation(language="english", text=f"Type1 Easy {i}")],
                    type="type1",
                    difficulty="easy"
                ) for i in range(5)],
                *[Phrase(
                    translations=[Translation(language="english", text=f"Type2 Easy {i}")],
                    type="type2",
                    difficulty="easy"
                ) for i in range(5)]
            ]
            
            quest = Quest(
                name="Test Quest",
                language="english",
                types=["type1", "type2"]  # type1 preferred
            )
            
            # Pattern with 5 easy slots
            test_data = BingoData(
                quests=[quest],
                phrases=phrases,
                difficulties=["easy"] * 5
            )
            
            # Generate multiple cards and check positions and type distributions
            position_sets = set()
            type1_counts = []  # Track how many Type1 phrases are used in each card
            num_trials = 50
            
            for _ in range(num_trials):
                cards, error = generate_cards(test_data, shuffle=True)
                self.assertIsNone(error)
                self.assertIsNotNone(cards)
                
                card = cards[0]['card']
                # Create a tuple of positions for comparison
                positions = tuple(card)
                position_sets.add(positions)
                
                # Count Type1 phrases
                type1_count = sum(1 for phrase in card if "Type1" in phrase)
                type1_counts.append(type1_count)
            
            # We should have multiple different arrangements
            self.assertGreater(len(position_sets), 1)
            
            # We should see variation in Type1 usage while maintaining preference
            self.assertTrue(all(count > 0 for count in type1_counts), 
                          "Type1 (preferred) should always be used")
    
    unittest.main()