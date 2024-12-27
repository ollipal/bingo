from typing import List, Dict, Tuple, Set
from schemas import BingoData, Translation, BingoCard, Quest, Question
import random

def generate_cards(data: BingoData, shuffle: bool = True) -> tuple[List[BingoCard] | None, str | None]:
    """
    Generate bingo cards based on the provided data.
    
    Args:
        data: BingoData containing quests, questions and difficulties pattern
        shuffle: Whether to shuffle the questions or maintain order (for testing)
        
    Returns:
        Tuple of (cards, error) where:
        - cards is a list of BingoCard if successful, None if failed
        - error is a string describing the error if failed, None if successful
    """
    cards = []
    
    for quest in data.quests:
        question_pools: Dict[str, Dict[str, List[str]]] = {}
        
        for question_type in quest.types:
            question_pools[question_type] = {}
            type_questions = [q for q in data.questions if q.type == question_type]
            
            for q in type_questions:
                valid_translations = [
                    trans.text 
                    for trans in q.translations 
                    if trans.language == quest.language
                ]
                if valid_translations:
                    if q.difficulty not in question_pools[question_type]:
                        question_pools[question_type][q.difficulty] = []
                    question_pools[question_type][q.difficulty].extend(valid_translations)

        needed_by_difficulty = {}
        for diff in data.difficulties:
            if diff not in needed_by_difficulty:
                needed_by_difficulty[diff] = 0
            needed_by_difficulty[diff] += 1
            
        # Check availability before starting to fill card
        for required_difficulty in needed_by_difficulty:
            total_available = sum(
                len(question_pools.get(qtype, {}).get(required_difficulty, []))
                for qtype in quest.types
            )
            if total_available < needed_by_difficulty[required_difficulty]:
                by_type = {
                    qtype: len(question_pools.get(qtype, {}).get(required_difficulty, []))
                    for qtype in quest.types
                }
                type_counts = ", ".join(f"{qtype}: {count}" for qtype, count in by_type.items())
                or_types = "' or '".join(quest.types)
                return None, (
                    f"Could not generate a bingo card for quest {quest.name}: "
                    f"not enough {quest.language} questions with difficulty '{required_difficulty}' and type '{or_types}'. "
                    f"{needed_by_difficulty[required_difficulty]} required, available by type: {type_counts}."
                )

        card = []
        for required_difficulty in data.difficulties:
            for question_type in quest.types:
                if question_type not in question_pools:
                    continue
                
                pool = question_pools[question_type]
                if required_difficulty in pool and pool[required_difficulty]:
                    questions = pool[required_difficulty]
                    if shuffle:
                        selected = random.choice(questions)
                    else:
                        selected = questions[0]
                    
                    card.append(selected)
                    questions.remove(selected)
                    break
            else:
                raise RuntimeError(f"Failed to find question for {required_difficulty} despite availability check")
            
        cards.append(card)
    
    return cards, None

if __name__ == '__main__':
    import unittest
    
    class TestGenerateCardsNoShuffle(unittest.TestCase):
        def setUp(self):
            # Create test data - generate translations with type in the text
            self.test_translations_en = [
                Translation(language="english", text=f"Type{t} {d} Question {i}")
                for t in range(1, 4)  # 3 types 
                for d in ["easy", "medium", "hard"]
                for i in range(100)  # 100 questions per type-difficulty combo
            ]
            
            # Create questions with different difficulties - 100 each type, evenly distributed
            def create_questions(type_num: int) -> List[Question]:
                questions = []
                idx = 0
                for difficulty in ["easy", "medium", "hard"]:
                    for _ in range(100):
                        trans_idx = (type_num - 1) * 300 + idx  # 300 = 3 difficulties * 100 questions
                        questions.append(Question(
                            translations=[self.test_translations_en[trans_idx]],
                            type=f"type{type_num}",
                            difficulty=difficulty
                        ))
                        idx += 1
                return questions

            # Create 100 questions of each type-difficulty combination
            self.test_questions = []
            for type_num in range(1, 4):  # type1, type2, type3
                self.test_questions.extend(create_questions(type_num))
            
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
                questions=self.test_questions,
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
            first_card = cards[0]
            self.assertEqual(len(first_card), 9)  # 3 of each difficulty

            # Each question should contain "Type1" in text (preferring first type)
            for text in first_card:
                self.assertIn("Type1", text)
            
            # Test second card (using type2 first)
            second_card = cards[1]
            self.assertEqual(len(second_card), 9)
            
            # Each question should contain "Type2" in text (preferring first type)
            for text in second_card:
                self.assertIn("Type2", text)
            
            # No question should be repeated between cards
            all_questions = set()
            for card in cards:
                for question in card:
                    self.assertNotIn(question, all_questions, "Question was repeated")
                    all_questions.add(question)

    class TestGenerateCardsInsufficientQuestions(unittest.TestCase):
        def test_multiple_types_needed(self):
            # Create test data where we need multiple types to fill the card
            questions = [
                # type1: 3 easy questions
                *[Question(
                    translations=[Translation(language="spanish", text=f"Type1 Easy {i}")],
                    type="type1",
                    difficulty="easy"
                ) for i in range(3)],
                # type2: 3 easy questions
                *[Question(
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
            
            # Pattern requires 5 easy questions
            test_data = BingoData(
                quests=[quest],
                questions=questions,
                difficulties=["easy"] * 5
            )
            
            # Generate card
            cards, error = generate_cards(test_data, shuffle=False)
            
            # Should succeed by using both types
            self.assertIsNone(error)
            self.assertIsNotNone(cards)
            
            card = cards[0]
            self.assertEqual(len(card), 5)
            
            # First 3 should be from type1
            for i in range(3):
                self.assertEqual(card[i], f"Type1 Easy {i}")
            
            # Last 2 should be from type2
            for i in range(3, 5):
                self.assertEqual(card[i], f"Type2 Easy {i-3}")

        def test_insufficient_questions(self):
            # Create data with insufficient questions of required difficulty
            insufficient_questions = [
                Question(
                    translations=[Translation(language="english", text="Question 1")],
                    type="type1",
                    difficulty="easy"  # Only easy questions when we need hard ones too
                )
            ]
            insufficient_data = BingoData(
                quests=[Quest(name="Test Quest", language="english", types=["type1"])],
                questions=insufficient_questions,
                difficulties=["hard"]  # Requires hard question but none exist
            )

            # Test that it returns appropriate error
            cards, error = generate_cards(insufficient_data, shuffle=False)

            print(error)
            
            self.assertIsNone(cards)
            self.assertEqual(
                error,
                "Could not generate a bingo card for quest Test Quest: "
                "not enough english questions with difficulty 'hard' and type 'type1'. "
                "1 required, available by type: type1: 0."
            )

    unittest.main()