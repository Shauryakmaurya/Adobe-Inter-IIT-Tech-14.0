from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List
from llama_cpp import Llama
import uvicorn

# Initialize FastAPI app
app = FastAPI(
    title="LightArt Autocomplete API",
    description="Text autocomplete service using local Llama model with dynamic suggestions",
    version="1.0.0"
)

# Add CORS middleware to allow requests from web clients
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure this to specific origins in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Model configuration
MODEL_PATH = "./llama-3.2-3b-instruct-q4_k_m.gguf"

# Initialize Llama model
print(f"Loading model from {MODEL_PATH}...")
try:
    llm = Llama(
        model_path=MODEL_PATH,
        n_ctx=2048,
        n_gpu_layers=0,   
        verbose=False,
    )
    print("Model loaded successfully!")
except Exception as e:
    print(f"Error loading model: {e}")
    llm = None

# Pydantic models for request/response
class AutocompleteRequest(BaseModel):
    sentence: str = Field(..., description="The base sentence to autocomplete", example="soften the overall")
    suggestions: List[str] = Field(..., description="List of suggestions to use for autocompletion", min_length=1)

class AutocompleteResponse(BaseModel):
    completion: str = Field(..., description="The autocompleted text")
    full_text: str = Field(..., description="The base sentence + completion combined")

# Autocomplete function
def autocomplete_lightart(base_sentence: str, light_suggestions: List[str]) -> str:
    """
    Autocompletes a sentence using ONLY the given suggestions.
    """
    prompt = f"""
You are an AUTOCOMPLETE assistant.

Use ONLY these light_suggestions:
{light_suggestions}

RULES:
- Continue the sentence EXACTLY from where it ends.
- Do NOT change the base sentence.
- ONLY use provided light_suggestions to autocomplete.
- ONLY natural color/tone language.
- ONLY autocomplete using the light_suggestions.

Complete: {base_sentence}
"""

    response = llm.create_chat_completion(
        messages=[
            {"role": "system", "content": "Autocomplete using ONLY the allowed suggestions."},
            {"role": "user", "content": prompt},
        ],
        max_tokens=20,
        temperature=0.1,
        top_p=0.9,
    )

    return response["choices"][0]["message"]["content"].strip()

# API Endpoints
@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "LightArt Autocomplete API",
        "version": "1.0.0",
        "endpoints": {
            "/autocomplete": "POST - Generate text autocompletion",
            "/health": "GET - Check API health status",
            "/docs": "GET - Interactive API documentation"
        }
    }

@app.get("/health")
async def health_check():
    """Health check endpoint to verify model is loaded and ready"""
    if llm is None:
        raise HTTPException(
            status_code=503,
            detail="Model not loaded. Please check server logs."
        )
    
    return {
        "status": "healthy",
        "model_loaded": True,
        "model_path": MODEL_PATH
    }

@app.post("/autocomplete", response_model=AutocompleteResponse)
async def autocomplete(request: AutocompleteRequest):
    """
    Generate autocomplete suggestion for a given sentence using provided suggestions.
    
    - **sentence**: The base sentence to autocomplete
    - **suggestions**: List of allowed suggestions to use for autocompletion
    """
    if llm is None:
        raise HTTPException(
            status_code=503,
            detail="Model not loaded. Please restart the server."
        )
    
    if not request.sentence.strip():
        raise HTTPException(
            status_code=400,
            detail="Sentence cannot be empty"
        )
    
    try:
        # Generate autocomplete
        completion = autocomplete_lightart(
            base_sentence=request.sentence,
            light_suggestions=request.suggestions
        )
        
        # Combine base sentence with completion
        full_text = f"{request.sentence} {completion}".strip()
        
        return AutocompleteResponse(
            completion=completion,
            full_text=full_text
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error generating autocomplete: {str(e)}"
        )

# Refine function (longer response ~12 words)
def refine_lightart(base_sentence: str, light_suggestions: List[str]) -> str:
    """
    Refines a sentence with a longer completion (~12 words) using ONLY the given suggestions.
    """
    prompt = f"""
You are a REFINE assistant.

Use ONLY these light_suggestions:
{light_suggestions}

RULES:
- Continue the sentence EXACTLY from where it ends.
- Do NOT change the base sentence.
- ONLY use provided light_suggestions to refine.
- ONLY natural color/tone language.
- Generate approximately 12 words for the completion.
- ONLY refine using the light_suggestions.

Complete: {base_sentence}
"""

    response = llm.create_chat_completion(
        messages=[
            {"role": "system", "content": "Refine using ONLY the allowed suggestions. Generate approximately 12 words."},
            {"role": "user", "content": prompt},
        ],
        max_tokens=50,
        temperature=0.2,
        top_p=0.9,
    )

    return response["choices"][0]["message"]["content"].strip()

@app.post("/refine", response_model=AutocompleteResponse)
async def refine(request: AutocompleteRequest):
    """
    Generate a refined, longer completion (~12 words) for a given sentence using provided suggestions.
    
    - **sentence**: The base sentence to refine
    - **suggestions**: List of allowed suggestions to use for refinement
    """
    if llm is None:
        raise HTTPException(
            status_code=503,
            detail="Model not loaded. Please restart the server."
        )
    
    if not request.sentence.strip():
        raise HTTPException(
            status_code=400,
            detail="Sentence cannot be empty"
        )
    
    try:
        # Generate refined completion
        completion = refine_lightart(
            base_sentence=request.sentence,
            light_suggestions=request.suggestions
        )
        
        # Combine base sentence with completion
        full_text = f"{request.sentence} {completion}".strip()
        
        return AutocompleteResponse(
            completion=completion,
            full_text=full_text
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error generating refinement: {str(e)}"
        )

# Server startup
if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
