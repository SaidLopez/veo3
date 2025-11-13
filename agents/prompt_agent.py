from pydantic import BaseModel
from pydantic_ai import Agent
from pydantic import Field
from typing import List


class PromptResponse(BaseModel):
    prompts: List[str] = Field(description="List of generated prompts")


def generate_prompts(prompt: str, model: str):
    prompt_generator_agent = Agent(
        f"{model}",
        output_type=PromptResponse,
        system_prompt=(
            f"""{prompt}
            """
        ),
        retries=3,
    )

    # print(f"Enquiry: {enquiry}")
    response = prompt_generator_agent.run_sync()
    return response.output
