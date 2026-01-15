from pydantic_ai import Agent
from pydantic_ai.providers.mistral import MistralProvider

# Initialize provider with API key
mistral_provider = MistralProvider(api_key="lenpipOpfSKOm57F8XyLxp0rvjh8wZHz")
agent = Agent('mistral:mistral-small-latest', model_provider=mistral_provider)

async def main():
    result = await agent.run("Hello")
    while True:
        print(f"\n{result.data}")
        user_input = input("\n> ")

        if user_input.lower() in ['exit', 'bye', 'quit']:
            break
        
        result = await agent.run(user_input, 
                                 message_history=result.new_messages(),
        )

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())


from pydantic import BaseModel
from pydantic_ai import Agent
from pydantic_ai.providers.mistral import MistralProvider


class MyModel(BaseModel):
    city: str
    country: str


# Reuse the provider from above
agent2 = Agent('mistral:mistral-small-latest', model_provider=mistral_provider)

if __name__ == '__main__':
    result = agent2.run_sync('The windy city in the US of A.')
    print(result.output)
    print(result.usage())