import os
import google.generativeai as genai
from dotenv import load_dotenv
import time

load_dotenv()

def test_image_generation():
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("Error: GEMINI_API_KEY not found in environment")
        return

    genai.configure(api_key=api_key)
    
    model_name = "models/nano-banana-pro-preview"
    prompt = "A futuristic city with flying cars and neon lights, cyberpunk style"
    
    print(f"Testing image generation with model: {model_name}")
    print(f"Prompt: {prompt}")
    
    try:
        # Attempt to instantiate the model. 
        # Note: The API might differ slightly depending on the SDK version, 
        # but this is the standard pattern for Imagen on Vertex/Gemini
        # If this fails, we might need to use the 'generative-ai' specific image method
        
        # Method 1: Standard GenerativeModel (sometimes supports images)
        # model = genai.GenerativeModel(model_name)
        # response = model.generate_content(prompt) # This usually returns text
        
        print("Calling generate_content...")
        model = genai.GenerativeModel(model_name)
        response = model.generate_content(prompt)
        
        print("Response received.")
        # print(response) # Verbose
        
        if response.parts:
            print(f"Number of parts: {len(response.parts)}")
            for i, part in enumerate(response.parts):
                print(f"Part {i}: {part}")
                # Check for inline data (image)
                if hasattr(part, 'inline_data'):
                    print("Found inline data!")
                    # Save image
                    import base64
                    img_data = part.inline_data.data
                    # mime_type = part.inline_data.mime_type
                    with open(f"test_image_{i}.png", "wb") as f:
                        f.write(img_data) # It's already bytes if using the SDK objects usually, or might need decoding
                    print(f"Saved test_image_{i}.png")
                elif hasattr(part, 'text'):
                    print(f"Text part: {part.text}")
        else:
            print("No parts in response.")
            print(response.candidates)

    except Exception as e:
        print(f"Error generating image: {e}")

if __name__ == "__main__":
    test_image_generation()

if __name__ == "__main__":
    test_image_generation()
