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

        card = []
        for required_difficulty in data.difficulties:
            for phrase_type in quest.types:
                if phrase_type not in phrase_pools:
                    continue
                
                pool = phrase_pools[phrase_type]
                if required_difficulty in pool and pool[required_difficulty]:
                    phrases = pool[required_difficulty]
                    if shuffle:
                        selected = random.choice(phrases)
                    else:
                        selected = phrases[0]
                    
                    card.append(selected)
                    phrases.remove(selected)
                    break
            else:
                raise RuntimeError(f"Failed to find phrase for {required_difficulty} despite availability check")
            
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

            # Create 100 phrases of each type-difficulty combination
            self.test_phrases = []
            for type_num in range(1, 4):  # type1, type2, type3
                self.test_phrases.extend(create_phrases(type_num))
            
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
            
            # Create test difficulties pattern with varied difficulties
            self.test_difficulties = ["easy"] * 3 + ["medium"] * 3 + ["hard"] * 3
            
            # Create test BingoData
            self.test_data = BingoData(
                quests=self.test_quests,
                phrases=self.test_phrases,
                difficulties=self.test_difficulties
            )

        def test_generate_cards_without_shuffle(self):
            # Generate cards without shuffling
            cards, error = generate_cards(self.test_data, shuffle=False)
            
            # Check no error occurred
            self.assertIsNone(error)
            self.assertIsNotNone(cards)
            
            # Test number of cards matches number of quests
            self.assertEqual(len(cards), len(self.test_quests))
            
            # Test first card (using type1 first)
            first_card = cards[0]['card']
            first_quest = cards[0]['quest']
            self.assertEqual(len(first_card), 9)  # 3 of each difficulty
            self.assertEqual(first_quest, "Test Quest 1")

            # Each phrase should contain "Type1" in text (preferring first type)
            for text in first_card:
                self.assertIn("Type1", text)
            
            # Test second card (using type2 first)
            second_card = cards[1]['card']
            second_quest = cards[1]['quest']
            self.assertEqual(len(second_card), 9)
            self.assertEqual(second_quest, "Test Quest 2")
            
            # Each phrase should contain "Type2" in text (preferring first type)
            for text in second_card:
                self.assertIn("Type2", text)
            
            # No phrase should be repeated between cards
            all_phrases = set()
            for card_data in cards:
                for phrase in card_data['card']:
                    self.assertNotIn(phrase, all_phrases, "Phrase was repeated")
                    all_phrases.add(phrase)

    class TestGenerateCardsInsufficientPhrases(unittest.TestCase):
        def test_multiple_types_needed(self):
            # Create test data where we need multiple types to fill the card
            phrases = [
                # type1: 3 easy phrases
                *[Phrase(
                    translations=[Translation(language="spanish", text=f"Type1 Easy {i}")],
                    type="type1",
                    difficulty="easy"
                ) for i in range(3)],
                # type2: 3 easy phrases
                *[Phrase(
                    translations=[Translation(language="spanish", text=f"Type2 Easy {i}")],
                    type="type2",
                    difficulty="easy"
                ) for i in range(3)]
            ]
            
            quest = Quest(
                name="Test Quest",
                language="spanish",
                types=["type1", "type2"]
            )
            
            # Pattern requires 5 easy phrases
            test_data = BingoData(
                quests=[quest],
                phrases=phrases,
                difficulties=["easy"] * 5
            )
            
            # Generate card
            cards, error = generate_cards(test_data, shuffle=False)
            
            # Should succeed by using both types
            self.assertIsNone(error)
            self.assertIsNotNone(cards)
            
            card = cards[0]['card']
            quest_name = cards[0]['quest']
            self.assertEqual(len(card), 5)
            self.assertEqual(quest_name, "Test Quest")
            
            # First 3 should be from type1
            for i in range(3):
                self.assertEqual(card[i], f"Type1 Easy {i}")
            
            # Last 2 should be from type2
            for i in range(3, 5):
                self.assertEqual(card[i], f"Type2 Easy {i-3}")

        def test_insufficient_phrases(self):
            # Create data with insufficient phrases of required difficulty
            insufficient_phrases = [
                Phrase(
                    translations=[Translation(language="english", text="Phrase 1")],
                    type="type1",
                    difficulty="easy"  # Only easy phrases when we need hard ones too
                )
            ]
            insufficient_data = BingoData(
                quests=[Quest(name="Test Quest", language="english", types=["type1"])],
                phrases=insufficient_phrases,
                difficulties=["hard"]  # Requires hard phrase but none exist
            )

            # Test that it returns appropriate error
            cards, error = generate_cards(insufficient_data, shuffle=False)
            
            self.assertIsNone(cards)
            self.assertEqual(
                error,
                "Could not generate a bingo card for quest Test Quest: "
                "not enough english phrases with difficulty 'hard' and type 'type1'. "
                "1 required, available by type: type1: 0."
            )

    unittest.main()