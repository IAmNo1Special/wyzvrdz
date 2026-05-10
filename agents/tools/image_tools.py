"""Image generation tools for the agents package."""

import time
import traceback

from google import genai
from google.adk.tools import ToolContext
from google.genai.types import (
    GenerateImagesConfig,
    GenerateImagesResponse,
    Part,
)


async def generate_images(
    img_desc: str, num_of_imgs: int, tool_context: ToolContext, **kwargs
) -> dict:
    """Generate images from a description.

    For best results, be descriptive and explicit with your image description.

    This is a long-running operation that yields intermediate updates.

    Args:
        img_desc: The description of the image(s) to generate.
        num_of_imgs: Number of images to generate.
        tool_context: The tool context for saving artifacts.
        **kwargs: Additional arguments for future compatibility.

    Yields:
        dict with 'status', 'message', and optionally 'data'.
    """
    try:
        print(f"Starting image generation with prompt: {img_desc}")

        genai_client = genai.Client()
        print("Connected to genai client")

        response: GenerateImagesResponse = genai_client.models.generate_images(
            model="imagen-4.0-generate-001",
            prompt=img_desc,
            config=GenerateImagesConfig(
                number_of_images=num_of_imgs, output_mime_type="image/png"
            ),
        )

        if not response.generated_images:
            error_msg = (
                "No images were generated. "
                "Please try again with a different prompt."
            )
            print(error_msg)
            return {"mime_type": "text/plain", "data": error_msg}

        generated_count = len(response.generated_images)
        print(
            f"Successfully generated {generated_count} image(s). Processing..."
        )

        # Process each image with individual progress tracking
        processed_count = 0
        for i, generated_image in enumerate(response.generated_images, 1):
            try:
                print(f"Processing image {i}")

                # Save the image as an Artifact
                artifact = Part.from_bytes(
                    data=generated_image.image.image_bytes,
                    mime_type=generated_image.image.mime_type,
                )

                # Generate a unique filename
                filename = f"generated_img_{int(time.time())}_{i}.png"
                await tool_context.save_artifact(
                    filename=filename, artifact=artifact
                )

                processed_count += 1
                print(f"Successfully processed image {i}")

            except Exception as img_error:
                error_msg = f"Error processing image {i}: {str(img_error)}"
                print(error_msg)
                return {"mime_type": "text/plain", "data": error_msg}

        # Final success result
        result = {
            "status": "completed",
            "message": (f"Generated and processed {processed_count} image(s)"),
            "progress": 3 + generated_count,  # All steps completed
            "total_images": generated_count,
            "processed_images": processed_count,
            "filename": filename,
            "timestamp": time.time(),
        }

        print(f"Image generation completed: {result}")
        return result

    except Exception as e:
        error_trace = traceback.format_exc()
        error_msg = f"Error in generate_images: {str(e)}"
        print(f"{error_msg}\n{error_trace}")

        error_result = {
            "status": "error",
            "message": "Failed to generate images",
            "error": str(e),
            "error_type": type(e).__name__,
            "timestamp": time.time(),
        }

        if "error_details" not in error_result:
            error_result["error_details"] = error_trace

        return error_result
