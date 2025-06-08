from typing import Dict, List, Optional, Any
import json
import datetime
import logging
from dataclasses import dataclass, asdict
import re

@dataclass
class Message:
    """Represents a single message in the conversation"""
    content: str
    sender: str  # 'user' or 'system'
    timestamp: str
    message_type: str  # 'text', 'quick_reply', 'form', etc.
    metadata: Dict[str, Any] = None

@dataclass
class ConversationState:
    """Represents the current state of the conversation"""
    current_topic: str
    collected_data: Dict[str, Any]
    completion_percentage: float
    last_question: str
    context: Dict[str, Any]
    validation_errors: List[str]

class ConversationManager:
    def __init__(self):
        """Initialize conversation manager"""
        self.conversation_history: List[Message] = []
        self.state = ConversationState(
            current_topic="",
            collected_data={},
            completion_percentage=0.0,
            last_question="",
            context={},
            validation_errors=[]
        )
        
        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
        
        # Load conversation flow configuration
        self.load_conversation_flow()

    def load_conversation_flow(self):
        """Load conversation flow configuration"""
        self.topics = {
            "initial_greeting": {
                "questions": [
                    {
                        "id": "name",
                        "text": "Hello! I'm your legal assistant. What is your name and what legal concern brings you here today?",
                        "validation": None,  # Accept any input for name and concern
                        "required": True
                    }
                ]
            },
            "case_details": {
                "questions": [
                    {
                        "id": "case_description",
                        "text": "Thank you. Could you please provide more details about your situation?",
                        "validation": r".{10,500}",
                        "error_message": "Please provide a description between 10 and 500 characters",
                        "required": True
                    },
                    {
                        "id": "case_type",
                        "text": "What type of legal case would you categorize this as?",
                        "quick_replies": ["Civil", "Criminal", "Family", "Property"],
                        "required": True
                    }
                ],
                "follow_up_questions": {
                    "case_type": {
                        "Criminal": "Have you filed a police report yet?",
                        "Family": "Are there any children involved in this case?",
                        "Property": "Do you have all the relevant property documentation?",
                        "Civil": "Have you sent any legal notice to the other party?"
                    }
                }
            }
        }

    def add_message(self, content: str, sender: str, message_type: str = "text", metadata: Dict = None) -> Message:
        """
        Add a message to the conversation history
        :return: The created message object
        """
        message = Message(
            content=content,
            sender=sender,
            timestamp=datetime.datetime.now().isoformat(),
            message_type=message_type,
            metadata=metadata or {}
        )
        self.conversation_history.append(message)
        return message

    def get_next_question(self) -> Optional[Dict]:
        """
        Get the next question based on current state and collected data
        :return: Question dictionary or None if no more questions
        """
        current_topic_data = self.topics.get(self.state.current_topic)
        if not current_topic_data:
            # Move to next topic if current is completed
            for topic in self.topics:
                if not all(q["id"] in self.state.collected_data 
                          for q in self.topics[topic]["questions"]
                          if q["required"]):
                    self.state.current_topic = topic
                    current_topic_data = self.topics[topic]
                    break
            else:
                return None  # All topics completed

        # Check for follow-up questions based on previous answers
        for q_id, answer in self.state.collected_data.items():
            follow_ups = current_topic_data.get("follow_up_questions", {}).get(q_id)
            if follow_ups:
                if isinstance(follow_ups, dict):
                    if isinstance(follow_ups.get("condition"), type(lambda: None)):
                        if follow_ups["condition"](answer):
                            return {"id": f"follow_up_{q_id}", "text": follow_ups["question"]}
                    elif answer in follow_ups:
                        return {"id": f"follow_up_{q_id}", "text": follow_ups[answer]}

        # Get next unanswered required question
        for question in current_topic_data["questions"]:
            if question["id"] not in self.state.collected_data and question.get("required", False):
                return question

        return None

    def validate_answer(self, question_id: str, answer: str) -> List[str]:
        """
        Validate an answer against question rules
        :return: List of validation error messages
        """
        errors = []
        
        # Find question configuration
        question = None
        for topic in self.topics.values():
            for q in topic["questions"]:
                if q["id"] == question_id:
                    question = q
                    break
            if question:
                break

        if not question:
            return ["Question not found"]

        # Required field validation
        if question.get("required") and not answer:
            errors.append("This field is required")
            return errors

        # Pattern validation
        if "validation" in question and answer:
            pattern = question["validation"]
            if not re.match(pattern, answer):
                errors.append(question.get("error_message", "Invalid input"))

        # Quick reply validation
        if "quick_replies" in question and answer not in question["quick_replies"]:
            errors.append("Please select one of the provided options")

        return errors

    def process_user_input(self, user_input: str) -> Dict:
        """
        Process user input and update conversation state
        :return: Dictionary containing next action information
        """
        # Special handling for initial greeting
        if not self.state.current_topic:
            self.state.current_topic = "initial_greeting"
            
        current_question = self.state.last_question
        
        # For initial greeting, parse name and concern
        if self.state.current_topic == "initial_greeting" and current_question == "name":
            # Store the complete response
            self.state.collected_data["initial_response"] = user_input
            
            # Move to case details
            self.state.current_topic = "case_details"
            next_question = self.get_next_question()
            if next_question:
                self.state.last_question = next_question["id"]
                return {
                    "status": "success",
                    "next_question": next_question,
                    "completion_percentage": 25.0
                }
        
        # Regular input processing
        validation_errors = []
        if current_question and "validation" in self.topics[self.state.current_topic]["questions"][0]:
            validation_errors = self.validate_answer(current_question, user_input)
        
        if validation_errors:
            self.state.validation_errors = validation_errors
            return {
                "status": "error",
                "errors": validation_errors,
                "should_retry": True
            }

        # Store answer
        if current_question:
            self.state.collected_data[current_question] = user_input
        self.state.validation_errors = []

        # Update completion percentage
        total_required = sum(
            1 for topic in self.topics.values()
            for question in topic["questions"]
            if question.get("required")
        )
        completed = sum(
            1 for topic in self.topics.values()
            for question in topic["questions"]
            if question.get("required") and question["id"] in self.state.collected_data
        )
        self.state.completion_percentage = (completed / total_required) * 100

        # Get next question
        next_question = self.get_next_question()
        if next_question:
            self.state.last_question = next_question["id"]
            return {
                "status": "success",
                "next_question": next_question,
                "completion_percentage": self.state.completion_percentage
            }
        else:
            return {
                "status": "completed",
                "completion_percentage": 100.0
            }

    def export_data(self, format: str = "json") -> str:
        """
        Export collected data in specified format
        :param format: Export format (json, csv, etc.)
        :return: Formatted data string
        """
        if format == "json":
            export_data = {
                "collected_data": self.state.collected_data,
                "completion_percentage": self.state.completion_percentage,
                "timestamp": datetime.datetime.now().isoformat()
            }
            return json.dumps(export_data, indent=2)
        else:
            raise ValueError(f"Unsupported export format: {format}")

    def get_help_message(self, context: str = None) -> str:
        """
        Get contextual help message
        :param context: Optional context for specific help
        :return: Help message string
        """
        general_help = "I'm here to help you provide information about your legal case. "
        general_help += "You can type 'help' at any time to see this message, "
        general_help += "'back' to go to the previous question, or 'restart' to start over."

        if context == "personal_info":
            return general_help + "\nFor personal information, please provide accurate details as they will be used in legal documents."
        elif context == "case_details":
            return general_help + "\nWhen describing your case, include relevant dates, locations, and parties involved."
        else:
            return general_help

    def get_conversation_summary(self) -> Dict:
        """
        Get a summary of the current conversation
        :return: Dictionary containing conversation summary
        """
        return {
            "total_messages": len(self.conversation_history),
            "completion_percentage": self.state.completion_percentage,
            "current_topic": self.state.current_topic,
            "collected_data": self.state.collected_data,
            "last_interaction": self.conversation_history[-1].timestamp if self.conversation_history else None
        } 