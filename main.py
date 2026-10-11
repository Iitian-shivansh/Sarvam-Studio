import os
import sys
from dotenv import load_dotenv
from sarvamai import SarvamAI

load_dotenv()

api_key = os.getenv("SARVAM_API_KEY")
if not api_key:
    raise ValueError("SARVAM_API_KEY is not set. Please add your key to the .env file.")

client = SarvamAI(api_subscription_key=api_key)

def chat_cli():
    print("=" * 55)
    print(" Sarvam AI Terminal Chat (sarvam-105b-conversations)")
    print(" - Type your message and press Enter")
    print(" - Type '/clear' to reset conversation")
    print(" - Type 'exit' or 'quit' to exit")
    print("=" * 55 + "\n")

    messages = []

    while True:
        try:
            user_input = input("You > ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nExiting chat. Goodbye!")
            break

        if not user_input:
            continue

        if user_input.lower() in ("exit", "quit"):
            print("Goodbye!")
            break

        if user_input.lower() == "/clear":
            messages.clear()
            print("Chat history cleared.\n")
            continue

        messages.append({"role": "user", "content": user_input})

        print("Sarvam > ", end="", flush=True)
        assistant_reply = ""

        try:
            stream = client.chat.completions(
                model="sarvam-105b-conversations",
                messages=messages,
                stream=True,
            )

            for chunk in stream:
                if chunk.choices and chunk.choices[0].delta and chunk.choices[0].delta.content:
                    delta = chunk.choices[0].delta.content
                    print(delta, end="", flush=True)
                    assistant_reply += delta

            print("\n")
            messages.append({"role": "assistant", "content": assistant_reply})

        except Exception as e:
            print(f"\n[Error]: {e}\n")
            if messages and messages[-1]["role"] == "user":
                messages.pop()

if __name__ == "__main__":
    chat_cli()

