import os
import io
import base64
import json
from dotenv import load_dotenv
from PIL import Image
from typing import List, Optional
from pydantic import BaseModel, Field, conlist
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.output_parsers import PydanticOutputParser

# --- Setup ---
load_dotenv()
API_KEY = os.getenv("GOOGLE_API_KEY")
if not API_KEY:
    # In a real environment, handle this gracefully
    pass 

# Initialize Gemini Model
gemini = ChatGoogleGenerativeAI(
    model="gemini-2.5-pro", # Strong model for complex structured output
    google_api_key=API_KEY
)

# --- Updated Pydantic Schema for 4 Main + 15 Normal Suggestions ---

SuggestionType = str # Single natural language suggestion string

class MainSuggestions(BaseModel):
    """Exactly 4 suggestions, one for each main category."""
    movie_style_suggestion: SuggestionType = Field(
        ..., 
        description="A single, natural language suggestion for a specific movie or cinematic aesthetic (e.g., 'Give it the look of a 70s Western film')."
    )
    mood_suggestion: SuggestionType = Field(
        ..., 
        description="A single, natural language suggestion targeting a specific emotional mood (e.g., 'Inject a strong sense of serenity and calm')."
    )
    color_focus_suggestion: SuggestionType = Field(
        ..., 
        description="A single, natural language suggestion focusing on a specific color or palette (e.g., 'Emphasize the deep, cool blue tones throughout the image')."
    )
    other_main_suggestion: SuggestionType = Field(
        ..., 
        description="A single, natural language, high-level suggestion not covered by the other categories (e.g., 'Apply a classic portrait finish')."
    )

class CombinedSuggestions(BaseModel):
    """Contains the 4 main suggestions and the 15 general suggestions."""
    main_suggestions: MainSuggestions = Field(
        ...,
        description="Exactly 4 high-level, categorized suggestions."
    )
    normal_suggestions: conlist(SuggestionType, min_length=15, max_length=15) = Field(
        ..., 
        description="Exactly 15 general, natural language enhancement suggestions."
    )

# --- Functions ---

parser = PydanticOutputParser(pydantic_object=CombinedSuggestions)
format_instructions = parser.get_format_instructions()

def pil_to_data_uri(img, fmt="JPEG"):
    """Converts a PIL Image object to a base64 Data URI."""
    buf = io.BytesIO()
    img.save(buf, format=fmt, quality=90)
    return "data:image/jpeg;base64," + base64.b64encode(buf.getvalue()).decode()

def gemini_user_style_suggestions(image: Image.Image):
    """
    Analyzes the image and returns exactly 4 main and 15 normal human-style suggestions, structured in JSON.
    """
    prompt = (
        "Analyze the image carefully and return ONLY a single JSON object "
        "containing exactly 4 main suggestions (one for each category: Movie Style, Mood, Color Focus, Other) "
        "and exactly 15 general suggestions, all in natural human language.\n\n"

        "*STRICT FORMAT INSTRUCTIONS*:\n"
        + format_instructions +
        "\n\n"

        "*RULES FOR ALL 19 SUGGESTIONS*:\n"
        "- The output MUST contain exactly one main_suggestions object with 4 fields, and one normal_suggestions list with exactly 15 elements.\n"
        "- Keep each suggestion short and natural, as if a user wrote it.\n"
        "- NO numbers, NO technical terms, NO percentages, NO stops.\n"
        "- NO crop or composition instructions.\n"
        "- Suggestions MUST relate only to exposure, contrast, tone, temperature, tint, "
        "highlights, shadows, whites, blacks, saturation, vibrance, or general color feel.\n"
        "- Style should match examples like:\n"
        "  • Main: 'Give this photo a dark, cinematic grade like a Christopher Nolan film.'\n"
        "  • Normal: 'Slightly reduce the overall exposure to add drama.'\n"
    )

    data_uri = pil_to_data_uri(image)

    msg = {
        "role": "user",
        "content": [
            {"type": "text", "text": prompt},
            {"type": "image_url", "image_url": data_uri}
        ]
    }

    # invoke Gemini
    resp = gemini.invoke([msg])

    # Extract and clean raw output
    raw = getattr(resp, "content", "")
    raw = raw.strip() if isinstance(raw, str) else str(resp).strip()

    if raw.startswith("```"):
        raw = raw.strip().strip("`").replace("json", "").strip()

    # Parse using Pydantic parser
    try:
        return parser.parse(raw)
    except Exception as e:
        # Fallback to direct json load if parser fails
        print(f"Pydantic parsing failed: {e}. Attempting direct JSON load.")
        return CombinedSuggestions.model_validate(json.loads(raw))


# ===== Example Use =====
if _name_ == "_main_":
    # NOTE: Update this path to a real image on your system
    try:
        image_path = "/home/logan78/Desktop/autocompletion_local/images/cityline.jpg"
        print(f"Attempting to load image from: {image_path}")
        img = Image.open(image_path).convert("RGB")
        
        print("\n--- Generating 4 Main + 15 Normal Suggestions ---")
        result = gemini_user_style_suggestions(img)
        
        # Display the JSON output
        print(result.model_dump_json(indent=2))
        
        # Confirmation of total count
        total_count = len(result.normal_suggestions) + 4
        print(f"\nTotal suggestions generated: {total_count} (4 Main + 15 Normal)")
        
    except FileNotFoundError:
        print("\nERROR: Image file not found.")
        print("Please replace the placeholder path in image_path with a real image path on your system.")
    except RuntimeError as e:
        print(f"\nRuntime Error: {e}")
    except Exception as e:
        print(f"\nAn unexpected error occurred during execution: {e}")