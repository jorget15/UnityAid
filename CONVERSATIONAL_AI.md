# 🤖 Conversational AI Priority Classification

## Overview

UnityAid now features intelligent conversational AI that asks clarifying questions when its confidence in priority classification is below 70%. This ensures more accurate triage and better resource allocation during disaster response.

## How It Works

### 1. Initial Assessment
When you submit a ticket description, the AI:
- Analyzes the text using enhanced heuristics and pattern recognition
- Calculates a confidence score (0-100%)
- Assigns an initial priority (1-5 scale)

### 2. Confidence Threshold Check
If confidence is **≥ 70%**: 
- ✅ Ticket is created immediately with the assigned priority
- Example: "Person is unconscious and not breathing" → Priority 5, 90% confidence

If confidence is **< 70%**:
- ❓ AI asks 2-4 targeted clarifying questions
- Questions are tailored to the type of emergency detected
- Example: "Someone needs help" → Priority 3, 60% confidence + 4 questions

### 3. Question Generation
The AI generates contextual questions based on:
- **Medical emergencies**: Consciousness, breathing, bleeding, mobility
- **Safety situations**: Immediate danger, accessibility, scope
- **Vulnerable populations**: Children, elderly, pregnant, disabled individuals
- **Resource needs**: Urgency timeline, alternatives available

### 4. Reclassification
After receiving answers:
- AI analyzes the enhanced context
- Updates priority based on new information
- Confidence typically increases to 80-95%
- Ticket is created with improved classification

## Examples

### Example 1: Ambiguous Initial Report
**Input**: "Someone needs help"
- **Initial**: Priority 3/5, 60% confidence
- **Questions Asked**:
  1. Are people in immediate physical danger?
  2. Is the location safe for responders to access?
  3. How many people are affected?
  4. Is this situation getting worse over time?

**High Urgency Answers**:
- Q1: "Yes, someone is trapped under debris"
- Q2: "Structure is unstable but accessible"
- Q3: "Three people, including a child" 
- Q4: "Yes, we hear groaning and the structure is unstable"

**Result**: Priority upgraded to **5/5**, 90% confidence

**Low Urgency Answers**:
- Q1: "No, just need some supplies"
- Q2: "Safe location"
- Q3: "Just one person"
- Q4: "No, it's stable"

**Result**: Priority remains **3/5**, 80% confidence

### Example 2: Clear Emergency
**Input**: "Person is unconscious and not breathing at downtown intersection"
- **Result**: Priority 5/5, 90% confidence → **No questions needed**

### Example 3: Medical Ambiguity
**Input**: "Need medical supplies for elderly person"
- **Initial**: Priority 3/5, 65% confidence
- **Questions Asked**:
  1. Is the person conscious and responsive?
  2. Does the person have any critical medical conditions?
  3. Can they walk or move on their own?
  4. How long can the situation wait without getting worse?

## User Interface

### In the Streamlit App:
1. **Ticket Agent Tab**: Submit your description
2. **AI Analysis**: If confidence is high, ticket is created immediately
3. **Follow-up Questions**: If confidence is low, Q&A section appears
4. **Three Options**:
   - ✅ **Submit Answers**: Reclassify with enhanced information
   - ⏭️ **Skip Questions**: Use original priority (with warning)
   - ❌ **Cancel**: Start over

### Question Interface:
- Clear, specific questions displayed one by one
- Text input fields for each answer
- Real-time validation
- Progress indication

## Benefits

### 🎯 **Improved Accuracy**
- Reduces misclassification of urgent vs. non-urgent cases
- Contextual questions reveal critical details
- Confidence scores provide transparency

### ⚡ **Efficient Triage**
- Only asks questions when needed (confidence < 70%)
- Tailored questions based on emergency type
- Quick resolution for clear cases

### 🛡️ **Safety Focus**
- Prioritizes life-threatening situations appropriately
- Identifies vulnerable populations (children, elderly)
- Considers accessibility and safety factors

### 📊 **Data Quality**
- Enhanced ticket descriptions with Q&A context
- Trackable confidence metrics
- Audit trail for priority decisions

## Technical Implementation

### Core Components:
- **PrioritizerConversation**: Manages Q&A logic
- **classify_with_conversation()**: Initial assessment with question generation
- **answer_questions_and_reclassify()**: Enhanced classification with answers
- **Enhanced heuristics**: Pattern matching with confidence scoring

### Integration Points:
- Seamless integration with existing Streamlit UI
- Session state management for conversation flow
- Fallback to simple classification if needed

## Configuration

### Confidence Threshold:
- Default: 70%
- Adjustable in `PrioritizerConversation.confidence_threshold`
- Higher threshold = more questions asked
- Lower threshold = fewer questions, faster processing

### Question Limits:
- High priority (4-5): Maximum 3 questions (focus on immediate danger)
- Medium priority (3): Maximum 4 questions (comprehensive assessment)
- Low priority (1-2): Maximum 2 questions (efficiency focused)

## Testing Results

Based on test scenarios:
- **Clear emergencies**: 90%+ confidence, no questions needed
- **Ambiguous cases**: 60-70% confidence, 2-4 questions asked
- **Post-Q&A confidence**: Typically 80-95% with improved accuracy
- **Priority adjustments**: Range from -2 to +2 based on additional context

## Future Enhancements

### Planned Features:
- **Learning system**: Improve questions based on historical accuracy
- **Multi-language support**: Questions in local languages
- **Voice integration**: Audio questions and responses
- **Confidence calibration**: Dynamic threshold adjustment
- **Question prioritization**: Most impactful questions first

## Usage Tips

### For Operators:
- Provide detailed initial descriptions when possible
- Answer questions completely and accurately
- Use "Skip Questions" sparingly - additional context improves outcomes
- Review confidence scores as quality indicators

### For System Administrators:
- Monitor confidence distributions in analytics
- Adjust threshold based on operational needs
- Review Q&A patterns for training opportunities
- Use audit trails for system improvement

---

*This conversational AI feature represents a significant advancement in automated emergency triage, balancing speed with accuracy through intelligent questioning.*