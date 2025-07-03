import instructor
import openai
from settings import OPENAI_API_KEY


client = instructor.from_openai(openai.OpenAI(api_key=OPENAI_API_KEY))
