import openai
from openai import OpenAI
# from dotenv import load_dotenv
import os

# load_dotenv()

# open_ai_key = os.getenv('OPEN_AI_KEY_VALUE', '')
# openai.api_key = open_ai_key

OPEN_AI_KEY_VALUE="open_ai_key_value"  # Replace actual OpenAI API key

os.environ["OPENAI_API_KEY"] = OPEN_AI_KEY_VALUE

def openAI_response_details_list(response):
    # response_dict = response.to_dict()  # Convert response to dict
    # print("\nThe actual complete openai response\n")
    # print(json.dumps(response_dict, indent=4))  # Pretty-print the response

    # Print relevant parts of the response
    print("\n=== Response Details of OpeanAI API CALL for this roadmap generation ===")
    print(f"ID: {response.id}")
    print(f"Model: {response.model}")
    print(f"Created: {response.created}")
    
    usage = response.usage
    print(f"Usage - Completion Tokens: {usage.completion_tokens}, Prompt Tokens: {usage.prompt_tokens}, Total Tokens: {usage.total_tokens}")
    
    # Loop through each choice in the response
    for i, choice in enumerate(response.choices):
        print(f"\n--- Choice {i+1} ---")
        print(f"Finish Reason: {choice.finish_reason}")
        print(f"Message Role: {choice.message.role}")
        print(f"Refusal reason: {choice.message.refusal}")



def call_openai(messages):
    """Get the full response by handling truncation and sending 'continue' requests."""
    full_response = ""

    while True:
        try:
            response = openai.chat.completions.create(
            # model="gpt-4o-mini-2024-07-18",
            model="gpt-4o-mini",
            # model="gpt-3.5-turbo",
            messages=messages,
            max_tokens=16384,
            n=1,
            temperature=0.7,
        )
            openAI_response_details_list(response)

            new_text = response.choices[0].message.content
            full_response += new_text

            finish_reason = response.choices[0].finish_reason

            if finish_reason == "stop":
                break
            elif finish_reason == "length":
                # Append the latest response and instruct the model to continue
                messages.append({"role": "assistant", "content": new_text})
                messages.append({"role": "user", "content": "continue"})
            else:
                break

        except Exception as e:
            raise RuntimeError(f"OpenAI API request failed: {e}")

    return full_response