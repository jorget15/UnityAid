#!/usr/bin/env python3
"""
Test script to demonstrate the conversational AI priority classification.
This script shows how the system asks follow-up questions when confidence is low.
"""
import sys
from pathlib import Path

# Add the PrioritizerAgent to path
prioritizer_path = Path(__file__).parent / "PrioritizerAgent"
sys.path.append(str(prioritizer_path))

from prioritizer_integration import classify_with_conversation, answer_questions_and_reclassify

def test_conversational_ai():
    """Test the conversational AI with various scenarios."""
    
    print("🧪 Testing Conversational AI Priority Classification\n")
    
    # Test cases with varying levels of detail
    test_cases = [
        {
            "description": "Someone needs help",
            "expected_clarification": True
        },
        {
            "description": "Person is unconscious and not breathing at downtown intersection",
            "expected_clarification": False  # Should be high confidence
        },
        {
            "description": "Need medical supplies for elderly person",
            "expected_clarification": True   # Ambiguous - could be routine or urgent
        },
        {
            "description": "Child is crying and says they're hungry",
            "expected_clarification": True   # Need more context about urgency
        },
        {
            "description": "Building collapsed with people trapped inside screaming for help",
            "expected_clarification": False  # Should be high confidence critical
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"📋 Test Case {i}: {test_case['description']}")
        print("-" * 60)
        
        # Initial classification
        result = classify_with_conversation(test_case['description'])
        
        print(f"Initial Priority: {result['priority']}/5")
        print(f"Confidence: {result['confidence']:.1%}")
        print(f"Source: {result['source']}")
        
        needs_clarification = result.get('needs_clarification', False)
        print(f"Needs Clarification: {needs_clarification}")
        
        if needs_clarification:
            questions = result.get('clarifying_questions', [])
            print(f"Follow-up Questions ({len(questions)}):")
            for j, question in enumerate(questions, 1):
                print(f"  {j}. {question}")
            
            # Simulate answering some questions for demo
            if "medical" in test_case['description'].lower():
                sample_qa = [
                    (questions[0] if questions else "Is this urgent?", "Yes, they need medication soon"),
                    (questions[1] if len(questions) > 1 else "Are they in danger?", "They seem stable but concerned")
                ]
            elif "child" in test_case['description'].lower():
                sample_qa = [
                    (questions[0] if questions else "How long since they ate?", "About 6 hours ago"),
                    (questions[1] if len(questions) > 1 else "Are they safe?", "Yes, with parent")
                ]
            else:
                # Generic answers
                sample_qa = [
                    (questions[0] if questions else "Is this urgent?", "Somewhat urgent"),
                    (questions[1] if len(questions) > 1 else "How many people?", "One person")
                ]
            
            print(f"\n🤖 Simulating answers:")
            for question, answer in sample_qa:
                print(f"  Q: {question}")
                print(f"  A: {answer}")
            
            # Reclassify with answers
            try:
                updated_result = answer_questions_and_reclassify(
                    test_case['description'], 
                    sample_qa,
                    result.get('conversation_id')
                )
                
                print(f"\n✅ Updated Classification:")
                print(f"Final Priority: {updated_result['priority']}/5")
                print(f"Final Confidence: {updated_result['confidence']:.1%}")
                print(f"Priority Change: {result['priority']} → {updated_result['priority']} ({updated_result['priority'] - result['priority']:+d})")
                
            except Exception as e:
                print(f"❌ Error in reclassification: {e}")
        
        print("\n" + "=" * 80 + "\n")

def test_confidence_threshold():
    """Test different confidence thresholds."""
    
    print("🎯 Testing Confidence Threshold Behavior\n")
    
    ambiguous_cases = [
        "Someone called about a problem",
        "Need assistance with supplies",
        "Person asking for help with food",
        "Medical situation needs attention",
        "Emergency at the location"
    ]
    
    for case in ambiguous_cases:
        result = classify_with_conversation(case)
        needs_clarification = result.get('needs_clarification', False)
        confidence = result.get('confidence', 0)
        
        print(f"📝 '{case}'")
        print(f"   Priority: {result['priority']}, Confidence: {confidence:.1%}, Clarification needed: {needs_clarification}")
        
        if needs_clarification and result.get('clarifying_questions'):
            print(f"   Questions: {len(result['clarifying_questions'])} follow-ups")
        print()

if __name__ == "__main__":
    try:
        test_conversational_ai()
        test_confidence_threshold()
        
        print("🎉 All tests completed!")
        print("\n💡 Key Features Demonstrated:")
        print("  • AI asks clarifying questions when confidence < 70%")
        print("  • Questions are tailored to the type of emergency")
        print("  • Priority can be updated based on additional information")
        print("  • System provides fallback for high-confidence cases")
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()