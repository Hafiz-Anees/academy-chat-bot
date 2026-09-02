import os
from dotenv import load_dotenv
load_dotenv()

token = os.getenv("INSTAGRAM_TOKEN")
print("Length:", len(token))
print("Repr:", repr(token))
print("Has newline:", "\n" in token)
print("Has space:", " " in token)