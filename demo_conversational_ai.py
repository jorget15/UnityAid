#!/usr/bin/env python3
"""
Demo script showing the conversational AI feature in action.
Run this to see examples of how the system behaves with different inputs.
"""

print("🆘 UnityAid Conversational AI Demo")
print("=" * 50)

try:
    import sys
    from pathlib import Path
    
    # Add the PrioritizerAgent to path
    prioritizer_path = Path(__file__).parent / "PrioritizerAgent"
    sys.path.append(str(prioritizer_path))
    
    from prioritizer_integration import classify_with_conversation, answer_questions_and_reclassify
    
    def demo_case(title, description, simulate_answers=None):
        print(f"\n📋 {title}")
        print(f"Input: '{description}'")
        print("-" * 40)
        
        # Initial classification
        result = classify_with_conversation(description)
        
        print(f"Initial Assessment:")
        print(f"  Priority: {result['priority']}/5")
        print(f"  Confidence: {result['confidence']:.1%}")
        print(f"  Source: {result['source']}")
        
        if result.get('needs_clarification') and result.get('clarifying_questions'):
            print(f"\nAI asks {len(result['clarifying_questions'])} questions:")
            for i, q in enumerate(result['clarifying_questions'], 1):
                print(f"  {i}. {q}")
            
            if simulate_answers:
                print(f"\nSimulated answers ({simulate_answers['type']}):")
                qa_pairs = []
                for i, answer in enumerate(simulate_answers['answers']):
                    if i < len(result['clarifying_questions']):
                        question = result['clarifying_questions'][i]
                        qa_pairs.append((question, answer))
                        print(f"  Q: {question}")
                        print(f"  A: {answer}")
                
                # Reclassify
                if qa_pairs:
                    updated = answer_questions_and_reclassify(description, qa_pairs)
                    print(f"\nUpdated Assessment:")
                    print(f"  Priority: {updated['priority']}/5")
                    print(f"  Confidence: {updated['confidence']:.1%}")
                    print(f"  Change: {result['priority']} → {updated['priority']} ({updated['priority'] - result['priority']:+d})")
        else:
            print("✅ High confidence - no questions needed!")
    
    # Demo cases
    demo_case(
        "Case 1: Clear Emergency", 
        "Person is unconscious and not breathing at downtown intersection"
    )
    
    demo_case(
        "Case 2: Ambiguous - High Urgency Answers",
        "Someone needs help",
        {
            "type": "HIGH URGENCY",
            "answers": [
                "Yes, someone is trapped under debris",
                "Three people, including a child", 
                "Yes, we can hear groaning and the structure is becoming unstable",
                "No, it's in a construction zone"
            ]
        }
    )
    
    demo_case(
        "Case 3: Ambiguous - Low Urgency Answers", 
        "Someone needs help",
        {
            "type": "LOW URGENCY", 
            "answers": [
                "No, just need some supplies",
                "Just one person",
                "No, it's stable", 
                "Yes, easy access"
            ]
        }
    )
    
    demo_case(
        "Case 4: Medical Ambiguity",
        "Need medical supplies for elderly person",
        {
            "type": "MODERATE URGENCY",
            "answers": [
                "Yes, but seems disoriented", 
                "Diabetes and high blood pressure",
                "With assistance, yes",
                "Maybe 2-3 hours safely"
            ]
        }
    )
    
    demo_case(
        "Case 5: Child Emergency",
        "Child is crying and says they're hungry", 
        {
            "type": "CONCERNED PARENT",
            "answers": [
                "The child is with their mother",
                "They haven't eaten since yesterday morning",
                "They're in a safe shelter but no food available"
            ]
        }
    )
    
    print("\n🎉 Demo Complete!")
    print("\n💡 Key Insights:")
    print("• Clear emergencies get immediate high-priority classification")
    print("• Ambiguous descriptions trigger 2-4 targeted questions") 
    print("• Answers significantly impact final priority (±2 levels)")
    print("• Confidence scores reflect classification certainty")
    print("• Medical/safety/vulnerable population questions are context-specific")
    
    print(f"\n🌐 Try it yourself in the web app:")
    print(f"   http://localhost:8502")
    print(f"   → Go to 'Ticket Agent' tab")
    print(f"   → Enter an ambiguous description")
    print(f"   → Answer the AI's questions!")

except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Make sure you're running from the UnityAid directory")
    print("and that PrioritizerAgent is properly set up.")

except Exception as e:
    print(f"❌ Error running demo: {e}")
    import traceback
    traceback.print_exc()