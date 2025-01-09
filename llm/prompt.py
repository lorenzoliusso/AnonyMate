# Description: Prompt template for the task.
DETECTION_INSTRUCTION_V8 = (
"""Your task is to identify only the sensible information in the text.

Nothing else should be identified. If you are not sure just output None.
The assistant response must only include the identified values in a comma separated order."""
)

# Examples of interaction user-assistant feeded to the model (few-shot learning)
EXAMPLES_ARR = [
    {"user": "My name is John Doe, and my email is john.doe@example.com.", 
     "assistant": "John Doe, john.doe@example.com"},
    {"user": "The credit card number is 1234-5678-9101-1121 and the CVV is 321.", 
     "assistant": "1234-5678-9101-1121, 321"},
    {"user": "My phone number is (555) 123-4567.", 
     "assistant": "(555) 123-4567"},
    {"user": "This document was created on January 1, 2023.", 
     "assistant": "January 1, 2023"},
    {"user": "The bank account number is 0987654321.", 
     "assistant": "0987654321"},
    {"user": "Hello, how are you today?", 
     "assistant": "None"},
    {"user": "My social security number is 123-45-6789.", 
     "assistant": "123-45-6789"},
    {"user": "Please meet me at 1234 Elm Street at 3 PM.", 
     "assistant": "1234 Elm Street, 3 PM"},
    {"user": "I will call you tomorrow.", 
     "assistant": "None"},
    {"user": "The meeting password is superSecret123!", 
     "assistant": "superSecret123!"}
]


# Prompt template for the word obfuscation.
REDACTION_INSTRUCTION_V1 = (
"""Your task is generate a similar output to the provided user input.
The assistant must never reponde with the same text as the user input."""
)

# Examples of interaction user-assistant feeded to the model (few-shot learning)
EXAMPLES_ARR_REDACTION = [
  {"user": "John Doe", "assistant": "Alice Adams"},
  {"user": "(555) 123-4567", "assistant": "(666) 987-6543"},
  {"user": "Not given", "assistant": "Not provided"},
  {"user": "01 January 1948", "assistant": "26 May 1955"},
  {"user": "superSecret123!", "assistant": "unknown1468!"},
]

