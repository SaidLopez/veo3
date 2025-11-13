import os
import time
from google import genai
from google.genai import types
from dotenv import load_dotenv
from PIL import Image
from io import BytesIO
from typing import Literal, List
from agents.openai_prompt_agent import generate_openai_prompts
from internal_prompts.image_gen_prompts import (
    base_prompt,
    infographic_prompt,
    product_highlight_prompt,
)
import json

load_dotenv()


class GoogleGenAI:
    def __init__(self):
        self.api_key = os.getenv("GOOGLE_API_KEY")
        self.client = genai.Client(api_key=self.api_key)
        self.negative_prompt = "ugly, low quality"  # @param {type: "string"}
        self.aspect_ratio = "16:9"  # @param ["16:9","9:16"]
        self.resolution = "1080p"  # @param ["720p","1080p"]
        self.VEO_MODEL_ID = "veo-3.1-generate-preview"  # @param ['veo-2.0-gen / veo-3.1-generate-preview / veo-3.0-fast-generate-001
        self.GEMINI_IMG_MODEL_ID = "gemini-2.5-flash-image"
        self.number_of_videos = 1
        self.number_of_image_variations = 6

        with open("brand_identity/barebells.json", "r") as f:
            data = json.load(f)  # This gives you a dict
        self.brand_identity = json.dumps(data)

    def generate_all_prompts(self) -> List[str]:
        prompts = []
        prompts.extend(self._generate_product_prompts(self.number_of_image_variations))
        prompts.extend(
            self._generate_infographic_prompts(self.number_of_image_variations)
        )
        prompts.extend(
            self._generate_highlight_prompts(self.number_of_image_variations)
        )
        return prompts

    def _generate_product_prompts(self, number_of_image_variations) -> List[str]:
        if number_of_image_variations <= 0:
            raise ValueError("Image variations need to be 1 or more")

        prompt = (
            base_prompt.format(number_of_image_variations=number_of_image_variations)
            + self.brand_identity
        )
        prompt_response = generate_openai_prompts(prompt)
        print(prompt_response)
        return [p for p in prompt_response.prompts]

    def _generate_infographic_prompts(self, number_of_image_variations) -> List[str]:
        if number_of_image_variations <= 0:
            raise ValueError("Image variations need to be 1 or more")

        prompt = (
            infographic_prompt.format(
                number_of_image_variations=number_of_image_variations
            )
            + self.brand_identity
        )
        prompt_response = generate_openai_prompts(prompt)
        print(prompt_response)
        return [p for p in prompt_response.prompts]

    def _generate_highlight_prompts(self, number_of_image_variations) -> List[str]:
        if number_of_image_variations <= 0:
            raise ValueError("Image variations need to be 1 or more")

        prompt = (
            product_highlight_prompt.format(
                number_of_image_variations=number_of_image_variations
            )
            + self.brand_identity
        )
        prompt_response = generate_openai_prompts(prompt)
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
            # gen_prompts = self.generate_all_prompts()
            # with open(f"internal_prompts/{output_folder}_prompts.py", "w") as f:
            #     f.write("prompts = [\n")
            #     for prompt in gen_prompts:
            #         # Escape quotes and backslashes in the prompt text
            #         escaped_prompt = prompt.replace("\\", "\\\\").replace("'", "\\'")
            #         f.write(f"    '{escaped_prompt}',\n")
            #     f.write("]\n")

            from internal_prompts.au_vodka_prompts import (
                prompts,
            )

            gen_prompts = prompts

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
  "video_duration": "8 seconds",
  "image_input": "Home.png",
  "animation_concept": "Dynamic 3D geometric shapes rotating and floating in space, creating a sense of innovation and forward-thinking design for a digital marketing agency landing page",
  
  "detailed_timeline": {
    "second_0_to_1": {
      "description": "Gentle camera orbit begins clockwise around the composition center",
      "camera_movement": "Slow 15-degree clockwise rotation around Y-axis, slight zoom in (3%)",
      "shape_behavior": {
        "orange_loop": "Subtle rotation on its own axis (5 degrees clockwise)",
        "blue_circle": "Gentle floating upward motion (2px)",
        "purple_frame": "Slight tilt forward (3 degrees)",
        "teal_ribbon": "Minimal wave motion, establishing depth",
        "spheres": "Micro-bobbing motion, creating life"
      },
      "effects": "Fade in from white/light gray (0% to 100% opacity)",
      "motion_intensity": "Low, elegant introduction"
    },
    
    "second_1_to_2": {
      "description": "Parallax depth becomes apparent, shapes move at different speeds",
      "camera_movement": "Continue clockwise orbit (20 degrees total), zoom reaches 5%",
      "shape_behavior": {
        "orange_loop": "Continues rotation, now 12 degrees total, slight scale pulse (102%)",
        "gray_sphere_top": "Drifts right and slightly down (5px), creating independence",
        "blue_circle": "Continues upward float, total 5px movement",
        "purple_frame": "Rotates counter-clockwise (5 degrees) creating dynamic tension",
        "pink_arrow": "Subtle forward tilt (2 degrees), suggesting direction",
        "orange_coins_bottom": "Gentle rotation as a group (3 degrees)"
      },
      "effects": "Shadows become more pronounced, depth increases",
      "motion_intensity": "Low-medium, building spatial awareness"
    },
    
    "second_2_to_3": {
      "description": "Peak of individual shape animation, maximum visual interest",
      "camera_movement": "Orbit continues (35 degrees total), slight upward tilt (5 degrees)",
      "shape_behavior": {
        "orange_loop": "Rotation accelerates slightly (20 degrees total), scale pulse to 104%",
        "teal_ribbon": "Unfurls with wave motion, creating fluid movement",
        "purple_frame": "Tilts on multiple axes, showcasing 3D depth (8 degrees rotation)",
        "pink_arrow": "Subtle bounce animation, draws eye through composition",
        "small_white_sphere": "Orbits around orange loop (15 degrees of arc)",
        "all_spheres": "Coordinated bobbing creates rhythm"
      },
      "effects": "Lighting shifts subtly, highlights move across surfaces",
      "motion_intensity": "Medium-high, most dynamic individual movements"
    },
    
    "second_3_to_4": {
      "description": "Shapes begin coordinated group motion, creating unity",
      "camera_movement": "Orbit reaches 50 degrees, zoom peaks at 8%, slight downward tilt begins",
      "shape_behavior": {
        "entire_composition": "Begins slow collective rotation (5 degrees clockwise as group)",
        "orange_loop": "Continues individual rotation (30 degrees total)",
        "purple_frame": "Rotates in opposite direction to composition (counter-clockwise 10 degrees)",
        "teal_ribbon": "Flows with enhanced wave motion, peak amplitude",
        "spheres": "Synchronized floating pattern emerges"
      },
      "effects": "Color saturation increases by 10%, making shapes more vibrant",
      "motion_intensity": "High, choreographed complexity"
    },
    
    "second_4_to_5": {
      "description": "Camera begins settling, shapes start returning to harmony",
      "camera_movement": "Orbit slows (60 degrees total), zoom holds at 8%, camera stabilizes",
      "shape_behavior": {
        "entire_composition": "Collective rotation continues (12 degrees total as group)",
        "orange_loop": "Rotation decelerates, scale returns to 100%",
        "purple_frame": "Begins settling back toward original orientation",
        "teal_ribbon": "Wave motion amplitude decreases, becoming calmer",
        "pink_arrow": "Settles into final position with gentle ease-out",
        "spheres": "Floating motion becomes more subtle and synchronized"
      },
      "effects": "Lighting normalizes, preparing for text overlay",
      "motion_intensity": "Medium, transitioning to calm"
    },
    
    "second_5_to_6": {
      "description": "Composition finds near-final position, background preparation for text",
      "camera_movement": "Orbit completes at 70 degrees, very slow drift continues, zoom holds",
      "shape_behavior": {
        "entire_composition": "Gentle collective rotation (18 degrees total), slowing significantly",
        "all_shapes": "Individual movements become micro-adjustments only",
        "orange_loop": "Subtle breathing motion (scale 100-101%)",
        "spheres": "Minimal floating, creating ambient life"
      },
      "effects": "Subtle vignette begins (5% edge darkening), background slightly defocuses (2% blur) to prepare for text, overall brightness reduces by 8%",
      "motion_intensity": "Low, settling phase",
      "text_animation": "Text 'THE SHAPE OF THINGS TO COME' begins fade-in at 0% opacity, positioned lower-third or center-bottom"
    },
    
    "second_6_to_7": {
      "description": "Near-static composition, focus shifts to text reveal",
      "camera_movement": "Minimal drift only (75 degrees total orbit), essentially locked",
      "shape_behavior": {
        "entire_composition": "Barely perceptible rotation (20 degrees total), almost static",
        "all_shapes": "Micro-movements only - subtle breathing and floating",
        "orange_loop": "Gentle scale pulse 100-101% maintains life"
      },
      "effects": "Vignette increases to 15%, background blur increases to 5%, brightness reduced by 12% total, creating clear contrast for text",
      "motion_intensity": "Minimal, ambient motion only",
      "text_animation": "Text fades from 0% to 65% opacity, Montserrat Bold, white color with subtle shadow, letter-spacing increased for impact"
    },
    
    "second_7_to_8": {
      "description": "Final hold frame, text fully revealed, professional end state",
      "camera_movement": "Locked position (80 degrees total), completely stable",
      "shape_behavior": {
        "entire_composition": "Subtle breathing motion only (scale 100-100.5%)",
        "all_shapes": "Minimal ambient floating maintains visual interest without distraction"
      },
      "effects": "Final vignette at 20%, background blur at 8%, brightness reduced by 15% total, optimal text legibility achieved",
      "motion_intensity": "Minimal, clean professional ending",
      "text_animation": "Text reaches 100% opacity, fully bold and impactful, 'THE SHAPE OF THINGS TO COME' in Montserrat Bold, perfectly readable"
    }
  },
  
  "text_overlay_specifications": {
    "text_content": "THE SHAPE OF THINGS TO COME",
    "font_family": "Montserrat Bold",
    "font_weight": "700",
    "timing": "Fade in from seconds 5.0 to 8.0 (3-second fade)",
    "animation_style": "Smooth ease-in fade (slow start, accelerates)",
    "positioning": "Center-bottom or lower-third, centered horizontally",
    "color": "#FFFFFF (white)",
    "text_effects": "Drop shadow: 0px 4px 12px rgba(0,0,0,0.4) for depth and readability",
    "size": "Large and impactful, 72-90pt",
    "letter_spacing": "Increased tracking (+100-150) for modern, premium feel",
    "line_height": "1.2 if text wraps to two lines",
    "opacity_keyframes": {
      "5.0s": "0%",
      "6.0s": "35%",
      "7.0s": "65%",
      "8.0s": "100%"
    }
  },
  
  "overall_motion_style": {
    "aesthetic": "Premium 3D motion graphics, sophisticated and modern",
    "inspiration": "Apple product reveals, high-end tech branding, architectural visualization",
    "easing": "Ease-in-out throughout, smooth bezier curves, no linear motion",
    "parallax_depth": "Strong - foreground elements move faster than background",
    "coherence": "Choreographed dance of shapes, each with personality but working as ensemble",
    "purpose": "Communicate innovation, creativity, dimensional thinking, and forward vision for digital marketing agency",
    "mood": "Confident, premium, innovative, dynamic yet controlled"
  },
  
  "technical_specifications": {
    "motion_blur": "Enabled, 180-degree shutter for natural cinematic blur",
    "frame_rate": "30fps (smooth web playback) or 60fps (premium option)",
    "resolution": "1920x1080 (Full HD) minimum, 4K preferred for landing page hero",
    "aspect_ratio": "16:9 for web, or 1:1 for social media variant",
    "file_format": "MP4 (H.264 codec, high quality)",
    "file_size_target": "Under 5MB for fast web loading",
    "loop_capability": "Designed to loop seamlessly if needed (remove text for loop version)",
    "background": "Maintain white/light background throughout, no color shifts"
  },
  
  "key_animation_principles": {
    "depth_layering": "Orange loop and gray sphere in foreground, blue circle mid-ground, purple frame and teal ribbon background",
    "rotation_choreography": "Shapes rotate in opposing directions to create visual tension and interest",
    "color_harmony": "Maintain vibrant orange, teal, purple, pink palette - increase saturation mid-animation",
    "focal_point": "Orange loop is primary focal point, camera orbits around it",
    "text_integration": "Background darkens and blurs progressively to ensure text pops without competing with shapes"
  }
}"""

    g.generate_creative("img", "n", "input_img/barebells.png", "barebells")
    # g.generate_creative("video", prompt, "input_img/PR&Outreach.png", "spike")
