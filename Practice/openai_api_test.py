import os

from openai import AuthenticationError, OpenAI, RateLimitError


# No es necesario por que he configurado la llave con el nombre OPENAI_API_KEY en el .env
#key = os.getenv("OPENAI_API_KEY")
#
#if not key:
#    raise ValueError("OPENAI_API_KEY is not set")

print("welcome to the OpenAI API" + "\n" * 2)

client=OpenAI()

try:
    response = client.responses.create(
        model='gpt-5-mini',
        instructions='You are a english translator. You are given a text in spanish and you need to translate it to english.',
        input='Hola, como estas?'
    )
    print(response.output_text)
except (RateLimitError, AuthenticationError) as e:
    # e.body ya es el dict interior: {message, type, code, param}
    print(f"Error: {e.body['message']}")

