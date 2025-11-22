import os
import time
from google import genai
from google.genai import types
from dotenv import load_dotenv
from PIL import Image
from io import BytesIO
from typing import Literal, List
from agents.prompt_agent import generate_prompts
from internal_prompts.image_gen_prompts import (
    base_prompt,
    infographic_prompt,
    product_highlight_prompt,
)
import json

load_dotenv()


class GoogleGenAI:
    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY")
        self.client = genai.Client(api_key=self.api_key)
        self.negative_prompt = "ugly, low quality"  # @param {type: "string"}
        self.aspect_ratio = (
            "16:9"  # "1:1","2:3","3:2","3:4","4:3","4:5","5:4","9:16","16:9","21:9"
        )
        self.resolution = "2K"  # "1K", "2K", "4K"
        self.VEO_MODEL_ID = "veo-3.1-generate-preview"  # @param ['veo-2.0-gen / veo-3.1-generate-preview / veo-3.0-fast-generate-001
        self.GEMINI_IMG_MODEL_ID = (
            "gemini-3-pro-image-preview"  # "gemini-2.5-flash-image"
        )
        self.number_of_videos = 1
        self.number_of_image_variations = 6
        self.agent_model = "google-gla:gemini-3-pro-preview"

        with open("brand_identity/myprotein.json", "r") as f:
            data = json.load(f)  # This gives you a dict
        self.brand_identity = json.dumps(data)

    def generate_all_prompts(self, product_description) -> List[str]:
        prompts = []
        prompts.extend(
            self._generate_product_prompts(
                self.number_of_image_variations, product_description
            )
        )
        prompts.extend(
            self._generate_infographic_prompts(
                self.number_of_image_variations, product_description
            )
        )
        prompts.extend(
            self._generate_highlight_prompts(
                self.number_of_image_variations, product_description
            )
        )
        return prompts

    def _generate_product_prompts(
        self, number_of_image_variations, product_description
    ) -> List[str]:
        if number_of_image_variations <= 0:
            raise ValueError("Image variations need to be 1 or more")

        prompt = (
            base_prompt.format(
                number_of_image_variations=number_of_image_variations,
                product_description=product_description,
            )
            + self.brand_identity
        )
        prompt_response = generate_prompts(prompt, self.agent_model)
        print(prompt_response)
        return [p for p in prompt_response.prompts]

    def _generate_infographic_prompts(
        self, number_of_image_variations, product_description
    ) -> List[str]:
        if number_of_image_variations <= 0:
            raise ValueError("Image variations need to be 1 or more")

        prompt = (
            infographic_prompt.format(
                number_of_image_variations=number_of_image_variations,
                product_description=product_description,
            )
            + self.brand_identity
        )
        prompt_response = generate_prompts(prompt, self.agent_model)
        print(prompt_response)
        return [p for p in prompt_response.prompts]

    def _generate_highlight_prompts(
        self, number_of_image_variations, product_description
    ) -> List[str]:
        if number_of_image_variations <= 0:
            raise ValueError("Image variations need to be 1 or more")

        prompt = (
            product_highlight_prompt.format(
                number_of_image_variations=number_of_image_variations,
                product_description=product_description,
            )
            + self.brand_identity
        )
        prompt_response = generate_prompts(prompt, self.agent_model)
        print(prompt_response)
        return [p for p in prompt_response.prompts]

    def generate_creative(
        self,
        creative_type: Literal["img", "video"],
        prompt: str,
        initial_image: str,  # path
        output_folder: str,
    ):
        if not initial_image and creative_type == "img":
            raise ValueError("You must provide an initial image to work from")

        # Create folder if it doesn't exist
        os.makedirs(f"output/{output_folder}", exist_ok=True)

        # Needed for Img generation

        im = Image.open(initial_image)
        # converting the image to bytes for video
        image_bytes_io = BytesIO()
        im.save(image_bytes_io, format=im.format)
        image_bytes = image_bytes_io.getvalue()

        # analyse image

        client = genai.Client()
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=[
                types.Part.from_bytes(
                    data=image_bytes,
                    mime_type="image/jpeg",
                ),
                "Caption this image with as much detail as possible",
            ],
        )

        print(response.text)
        image_description_text = response.text

        if creative_type == "video":
            operation = self.client.models.generate_videos(
                model=self.VEO_MODEL_ID,
                prompt=prompt,
                image=types.Image(image_bytes=image_bytes, mime_type=im.format),
                config=types.GenerateVideosConfig(
                    # At the moment the config must not be empty
                    aspect_ratio=self.aspect_ratio,
                    resolution=self.resolution,
                    number_of_videos=self.number_of_videos,  # 1 video generated per request
                    negative_prompt=self.negative_prompt,
                ),
            )
            # Waiting for the video(s) to be generated
            while not operation.done:
                time.sleep(20)
                operation = self.client.operations.get(operation)
                print(operation)

            print(operation.result.generated_videos)

            for n, generated_video in enumerate(operation.result.generated_videos):
                self.client.files.download(file=generated_video.video)
                generated_video.video.save(
                    f"output/{output_folder}/vid_{n}.mp4"
                )  # Saves the video(s)
        elif creative_type == "img":
            gen_prompts = self.generate_all_prompts(
                product_description=image_description_text
            )
            with open(f"internal_prompts/{output_folder}_prompts.py", "w") as f:
                f.write("prompts = [\n")
                for prompt in gen_prompts:
                    # Escape quotes and backslashes in the prompt text
                    escaped_prompt = prompt.replace("\\", "\\\\").replace("'", "\\'")
                    f.write(f"    '{escaped_prompt}',\n")
                f.write("]\n")

            # from internal_prompts.au_vodka_prompts import (
            #     prompts,
            # )

            # gen_prompts = prompts

            for i, prompt in enumerate(gen_prompts):
                split_threshold = len(gen_prompts) / 3
                if i <= split_threshold:
                    name = f"base_image_{i}.png"
                elif i > split_threshold and i <= 2 * split_threshold:
                    name = f"infographic_image_{i}.png"
                else:
                    name = f"product_highlight_image_{i}.png"

                response = self.client.models.generate_content(
                    model="gemini-2.5-flash-image",
                    contents=[prompt, im],
                )

                for part in response.candidates[0].content.parts:
                    if part.text is not None:
                        print(part.text)
                    elif part.inline_data is not None:
                        image = Image.open(BytesIO(part.inline_data.data))
                        image.save(f"output/{output_folder}/{name}")


if __name__ == "__main__":
    g = GoogleGenAI()
    prompt = """
{
  "scene_summary": "An excited humanoid alien creature gives a walking tour of a theathre's stage.",
  "character": {
    "type": "humanoid alien creature",
    "personality": [
      "expressive",
      "excited",
      "high energy"
    ],
    "features": {
      "eyes": "expressive amphibian eyes",
      "mouth": "expressive mouth",
      "face": "expressive lips and face",
      "movement": "expressive fluid gestures"
    },
    "accent": "gen z"
  },
  "environment": {
    "location": "theatre stage",
    "key_object": {
      "name": "glop perpetugooper",
      "description": "large machine emitting warm glowing light with glass cylinder filled with orange slime"
    }
  },
  "action_sequence": [
    {
      "camera": "tracks him as he walks",
      "dialogue": "And if you're hungry and you want some za we got the glop perpetu-gooper",
      "gesture": "Walks to screen left and touches a large machine."
    },
    {
      "dialogue": "You just think za and bloop!",
      "result": "A floating pizza forms inside the machine."
    },
    {
      "gesture": "He glances down at the pizza, then looks directly at the camera with excitement.",
      "dialogue": "Manifest your dinner bro!"
    }
  ],
  "visuals": {
    "lighting": [
      "diffuse studio lighting",
      "warm bounce light from machine",
      "soft shadows"
    ],
    "style": "soft cinematic color grading",
    "technique": "tonemapped HDR"
  },
  "render_settings": {
    "negative_prompt": {
      "exclude": [
        "music",
        "high contrast",
        "dark shadows",
        "underexposed"
      ]
    }
  }
} """

    g.generate_creative("img", "n", "input_img/myprotein.jpg", "my_protein_pro")
    # g.generate_creative("video", prompt, "input_img/said_stage.jpeg", "spike")
