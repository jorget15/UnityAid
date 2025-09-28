"""
Integration module for the PrioritizerAgent to classify ticket priorities in UnityAid.
This version includes conversational follow-up questions when confidence is low.
"""
import json
import os
import sys
from pathlib import Path

class PrioritizerConversation:
    """Manages conversational priority classification with follow-up questions."""
    
    def __init__(self):
        self.conversation_history = []
        self.confidence_threshold = 0.7
        
    def get_clarifying_questions(self, initial_classification: dict, description: str) -> list:
        """Generate clarifying questions based on initial classification."""
        priority = initial_classification['priority']
        confidence = initial_classification['confidence']
        key_indicators = initial_classification.get('key_indicators', [])
        
        questions = []
        
        # Medical-related questions
        if any(word in description.lower() for word in ['medical', 'injury', 'hurt', 'pain', 'sick', 'health']):
            questions.extend([
                "Is the person conscious and responsive?",
                "Are they having difficulty breathing?",
                "Is there any bleeding? If yes, how severe?",
                "Does the person have any critical medical conditions (diabetes, heart condition, etc.)?",
                "Can they walk or move on their own?"
            ])
        
        # Safety and danger questions
        if priority >= 3 and confidence < self.confidence_threshold:
            questions.extend([
                "Are people in immediate physical danger?",
                "Is the location safe for responders to access?",
                "How many people are affected?",
                "Is this situation getting worse over time?"
            ])
        
        # Vulnerable population questions
        if any(word in description.lower() for word in ['child', 'baby', 'elderly', 'pregnant', 'disabled']):
            questions.extend([
                "Are there children, elderly, or pregnant individuals involved?",
                "Do they have access to necessary medications or supplies?",
                "Are they in a safe shelter or exposed to elements?"
            ])
        
        # Resource and urgency questions
        if priority == 3 and confidence < self.confidence_threshold:
            questions.extend([
                "How long can the situation wait without getting worse?",
                "Are there alternative resources available nearby?",
                "Is this preventing other emergency responses?"
            ])
        
        # Location and accessibility
        questions.extend([
            "Is the location easily accessible to emergency responders?",
            "Are there any hazards at the scene (fire, chemicals, unstable structures)?"
        ])
        
        # Remove duplicates and limit to most relevant
        unique_questions = list(dict.fromkeys(questions))
        
        # Prioritize questions based on initial classification
        if priority >= 4:
            # For high priority, focus on immediate danger and medical status
            priority_questions = [q for q in unique_questions if any(word in q.lower() for word in 
                                ['conscious', 'breathing', 'bleeding', 'danger', 'immediate'])]
            return priority_questions[:3]
        elif priority == 3:
            # For medium priority, focus on scope and timeline  
            return unique_questions[:4]
        else:
            # For low priority, focus on urgency and alternatives
            priority_questions = [q for q in unique_questions if any(word in q.lower() for word in 
                                ['wait', 'alternative', 'worse', 'time'])]
            return priority_questions[:2]
    
    def reclassify_with_answers(self, original_description: str, qa_pairs: list) -> dict:
        """Reclassify priority with additional context from Q&A."""
        
        # Build enhanced context
        enhanced_context = original_description + "\n\nAdditional Information:\n"
        for q, a in qa_pairs:
            enhanced_context += f"Q: {q}\nA: {a}\n"
        
        # Start with enhanced heuristic classification
        result = enhanced_priority_classification(enhanced_context)
        base_priority = result['priority']
        
        # Smart Q&A analysis for priority escalation
        priority_boost = self._analyze_qa_responses(qa_pairs, base_priority)
        
        # Apply boost but cap at 5
        final_priority = min(5, base_priority + priority_boost)
        
        # Update result
        result['priority'] = final_priority
        result['base_priority'] = base_priority
        result['qa_boost'] = priority_boost
        
        # Boost confidence since we have more information
        result['confidence'] = min(0.95, result['confidence'] + 0.2)
        result['source'] = 'enhanced_with_qa'
        result['qa_pairs'] = qa_pairs
        
        # Update reasoning to reflect Q&A impact
        if priority_boost > 0:
            result['reasoning'] += f" (Escalated +{priority_boost} based on Q&A responses)"
        
        return result
    
    def _analyze_qa_responses(self, qa_pairs: list, base_priority: int) -> int:
        """Analyze Q&A responses for priority escalation indicators."""
        boost = 0
        
        # Convert all answers to lowercase for analysis
        all_answers = " ".join([a.lower() for q, a in qa_pairs])
        
        # Critical escalation indicators (+2 priority)
        critical_patterns = [
            # Life-threatening situations
            ["unconscious", "not breathing", "no pulse", "cardiac", "heart attack"],
            ["trapped", "buried", "stuck under", "collapsed on", "pinned down"],
            ["severe bleeding", "lots of blood", "hemorrhaging", "bleeding heavily"],
            ["child", "baby", "infant", "pregnant"] + ["danger", "immediate", "critical"],
            ["multiple people", "many people", "several people", "group of"],
            ["getting worse", "deteriorating", "spreading", "unstable", "collapsing"]
        ]
        
        # High priority escalation indicators (+1 priority)
        high_patterns = [
            # Medical emergencies
            ["difficulty breathing", "can't breathe", "chest pain", "diabetic", "insulin"],
            ["injury", "hurt", "pain", "broken", "fractured"],
            # Safety concerns
            ["immediate danger", "unsafe", "hazardous", "dangerous"],
            ["elderly", "disabled", "wheelchair", "vulnerable"],
            # Urgency indicators
            ["urgent", "immediately", "asap", "help now", "emergency"],
            ["yes.*danger", "yes.*immediate", "yes.*critical"],  # Regex patterns
        ]
        
        # Check for critical patterns
        for pattern_group in critical_patterns:
            if self._check_pattern_group(all_answers, pattern_group):
                boost = max(boost, 2)  # Maximum boost of 2 for critical
                break
        
        # Check for high priority patterns if no critical found
        if boost < 2:
            for pattern_group in high_patterns:
                if self._check_pattern_group(all_answers, pattern_group):
                    boost = max(boost, 1)  # Boost of 1 for high priority
        
        # Special analysis for specific question types
        boost += self._analyze_specific_questions(qa_pairs)
        
        # Cap the total boost at 2
        return min(2, boost)
    
    def _check_pattern_group(self, text: str, patterns: list) -> bool:
        """Check if any patterns in the group match the text."""
        for pattern in patterns:
            if ".*" in pattern:
                # Regex pattern
                import re
                if re.search(pattern, text):
                    return True
            else:
                # Simple substring match
                if pattern in text:
                    return True
        return False
    
    def _analyze_specific_questions(self, qa_pairs: list) -> int:
        """Analyze answers to specific question types for additional context."""
        boost = 0
        
        for question, answer in qa_pairs:
            q_lower = question.lower()
            a_lower = answer.lower()
            
            # Immediate danger questions
            if "immediate" in q_lower and "danger" in q_lower:
                if any(word in a_lower for word in ["yes", "trapped", "stuck", "buried", "critical"]):
                    boost += 1
            
            # People count questions
            elif "how many" in q_lower or "people affected" in q_lower:
                # Look for multiple people indicators
                if any(word in a_lower for word in ["multiple", "several", "many", "group", "family"]):
                    boost += 1
                # Look for specific numbers > 1
                elif any(word in a_lower for word in ["two", "three", "four", "five", "2", "3", "4", "5"]):
                    boost += 1
                elif any(word in a_lower for word in ["child", "baby", "elderly", "pregnant"]):
                    boost += 1
            
            # Getting worse questions
            elif "getting worse" in q_lower or "deteriorating" in q_lower:
                if any(word in a_lower for word in ["yes", "worse", "unstable", "collapsing", "spreading"]):
                    boost += 1
            
            # Medical condition questions
            elif any(med_word in q_lower for med_word in ["conscious", "breathing", "medical", "condition"]):
                if any(word in a_lower for word in ["no", "unconscious", "difficulty", "struggling", "critical"]):
                    boost += 1
        
        return min(1, boost)  # Cap at 1 for specific question analysis

def classify_ticket_priority(ticket_description: str, additional_context: str = "") -> dict:
    """
    Classify a ticket's priority using enhanced heuristics.
    
    Args:
        ticket_description: The main description of the ticket
        additional_context: Any additional context (location, time, etc.)
    
    Returns:
        dict: Priority classification result with priority, confidence, reasoning, etc.
    """
    full_text = ticket_description
    if additional_context:
        full_text += f" {additional_context}"
    
    return enhanced_priority_classification(full_text)

def classify_with_conversation(ticket_description: str, additional_context: str = "") -> dict:
    """
    Enhanced classification that includes follow-up questions when confidence is low.
    
    Args:
        ticket_description: The main description of the ticket
        additional_context: Any additional context (location, time, etc.)
    
    Returns:
        dict: Priority classification with optional follow-up questions
    """
    conversation = PrioritizerConversation()
    
    # Initial classification
    initial_result = classify_ticket_priority(ticket_description, additional_context)
    
    # If confidence is high enough, return immediately
    if initial_result['confidence'] >= conversation.confidence_threshold:
        return initial_result
    
    # Generate clarifying questions
    questions = conversation.get_clarifying_questions(initial_result, ticket_description)
    
    # Add questions to the result
    initial_result['needs_clarification'] = True
    initial_result['clarifying_questions'] = questions
    initial_result['conversation_id'] = id(conversation)  # Simple ID for tracking
    
    return initial_result

def answer_questions_and_reclassify(original_description: str, qa_pairs: list, 
                                  conversation_id: int = None) -> dict:
    """
    Reclassify after receiving answers to clarifying questions.
    
    Args:
        original_description: The original ticket description
        qa_pairs: List of (question, answer) tuples
        conversation_id: ID to track conversation (optional)
    
    Returns:
        dict: Updated priority classification
    """
    conversation = PrioritizerConversation()
    return conversation.reclassify_with_answers(original_description, qa_pairs)

def enhanced_priority_classification(text: str) -> dict:
    """
    Enhanced heuristic classification with detailed analysis.
    """
    t = (text or "").lower()
    score = 3
    key_indicators = []
    reasoning = ""
    
    # Critical priority indicators (Priority 5)
    critical_indicators = {
        "life_threatening": ["unconscious", "not breathing", "cardiac arrest", "heart attack", 
                           "severe bleeding", "hemorrhaging", "choking", "overdose"],
        "missing_persons": ["child missing", "person missing", "lost child", "abducted"],
        "structural": ["building collapse", "trapped", "buried", "structure unstable"],
        "hazmat": ["chemical spill", "gas leak", "toxic", "radiation", "hazardous material"],
        "fire_explosion": ["fire", "explosion", "burning building", "smoke inhalation"]
    }
    
    # High priority indicators (Priority 4)  
    high_indicators = {
        "medical_urgent": ["injury", "broken bone", "diabetic emergency", "insulin", "asthma attack",
                          "seizure", "chest pain", "difficulty breathing", "allergic reaction"],
        "vulnerable": ["pregnant", "baby", "infant", "elderly", "disabled", "wheelchair"],
        "essential_needs": ["no water", "dehydration", "no food", "starving", "hypothermia"],
        "immediate_danger": ["flood rising", "evacuate now", "shelter collapsing", "unsafe"]
    }
    
    # Medium priority indicators (Priority 3)
    medium_indicators = {
        "medical_stable": ["cut", "bruise", "sprain", "minor injury", "headache"],
        "basic_needs": ["food needed", "water needed", "shelter needed", "clothing"],
        "utilities": ["power out", "no electricity", "no phone", "communication down"]
    }
    
    # Low priority indicators (Priority 2)
    low_indicators = {
        "property": ["property damage", "roof damage", "window broken", "fence down"],
        "non_urgent": ["when possible", "not urgent", "later", "minor"]
    }
    
    # Analyze for critical indicators
    critical_score = 0
    for category, keywords in critical_indicators.items():
        for keyword in keywords:
            if keyword in t:
                critical_score += 2
                key_indicators.append(keyword)
                if critical_score >= 2:
                    score = 5
                    reasoning = f"CRITICAL: Life-threatening situation detected ({category})"
                    break
        if score == 5:
            break
    
    # Analyze for high priority if not critical
    if score != 5:
        high_score = 0
        for category, keywords in high_indicators.items():
            for keyword in keywords:
                if keyword in t:
                    high_score += 1
                    key_indicators.append(keyword)
        
        if high_score >= 2:
            score = 4
            reasoning = "HIGH: Multiple urgent indicators present"
        elif high_score >= 1:
            score = 4
            reasoning = "HIGH: Urgent medical or safety concern"
    
    # Analyze urgency language
    urgency_boost = 0
    urgency_words = ["urgent", "immediately", "asap", "emergency", "help now", "critical"]
    for word in urgency_words:
        if word in t:
            urgency_boost += 1
            key_indicators.append(word)
    
    # Punctuation intensity
    if "!!!" in text:
        urgency_boost += 1
        key_indicators.append("multiple exclamation marks")
    
    # Apply urgency boost
    if urgency_boost >= 2 and score < 4:
        score = min(score + 1, 4)
        reasoning += " (boosted for urgency language)"
    
    # Check for low priority indicators
    if score == 3:  # Only downgrade if currently medium
        low_count = 0
        for category, keywords in low_indicators.items():
            for keyword in keywords:
                if keyword in t:
                    low_count += 1
        
        if low_count >= 2:
            score = 2
            reasoning = "LOW: Non-urgent property or administrative matter"
    
    # Default reasoning if not set
    if not reasoning:
        if score == 3:
            reasoning = "MEDIUM: Standard emergency response needed"
        elif score == 2:
            reasoning = "LOW: Non-urgent request"
        elif score == 1:
            reasoning = "MINIMAL: Information or administrative request"
    
    # Calculate confidence based on number of indicators
    confidence = min(0.9, 0.6 + (len(key_indicators) * 0.1))
    
    return {
        'priority': score,
        'confidence': confidence,
        'reasoning': reasoning,
        'key_indicators': key_indicators[:5],  # Limit to top 5
        'source': 'enhanced_heuristic',
        'recommendations': generate_recommendations(score, key_indicators)
    }

def generate_recommendations(priority: int, indicators: list) -> str:
    """Generate action recommendations based on priority and indicators."""
    if priority == 5:
        return "IMMEDIATE DISPATCH: Life-threatening emergency requiring immediate response"
    elif priority == 4:
        return "URGENT RESPONSE: High priority requiring rapid deployment"
    elif priority == 3:
        return "STANDARD RESPONSE: Deploy within normal emergency timeframes"
    elif priority == 2:
        return "SCHEDULED RESPONSE: Address during next available window"
    else:
        return "NON-EMERGENCY: Handle through standard administrative channels"

def test_prioritizer():
    """Test function to verify the prioritizer works correctly."""
    test_cases = [
        ("Person unconscious, not breathing, need immediate help!", 5),
        ("Child missing in flood zone, last seen 2 hours ago", 5),
        ("Building collapse, people trapped inside!", 5),
        ("Need insulin for diabetic patient, running low", 4),
        ("Elderly person with chest pain, difficulty breathing", 4),
        ("Family needs shelter, pregnant woman and baby", 4),
        ("Water supply contaminated, many people sick", 4),
        ("Shelter needed for family with children", 3),
        ("Power out in neighborhood for 6 hours", 3),
        ("Property damage assessment needed", 2),
        ("Roof damage from storm, not urgent", 2),
        ("Looking for information about evacuation routes", 1),
    ]
    
    print("Testing Enhanced PrioritizerAgent:")
    print("=" * 60)
    
    correct = 0
    for i, (case, expected) in enumerate(test_cases, 1):
        result = classify_ticket_priority(case)
        actual = result['priority']
        status = "✓" if actual == expected else "✗"
        if actual == expected:
            correct += 1
            
        print(f"\n{status} Test {i}: {case}")
        print(f"   Expected: {expected}, Got: {actual}")
        print(f"   Reasoning: {result['reasoning']}")
        print(f"   Key Indicators: {result['key_indicators']}")
        print(f"   Confidence: {result['confidence']:.2f}")
        print(f"   Recommendations: {result['recommendations']}")
    
    print(f"\n{'='*60}")
    print(f"Accuracy: {correct}/{len(test_cases)} ({correct/len(test_cases)*100:.1f}%)")

if __name__ == "__main__":
    test_prioritizer()