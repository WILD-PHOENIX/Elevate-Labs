import streamlit as st
import os
import json
import time
from datetime import datetime

# Page configuration
st.set_page_config(
    page_title="AI Dungeon Story Generator",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        text-align: center;
        color: #4A90E2;
        font-size: 3rem;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        text-align: center;
        color: #666;
        font-size: 1.2rem;
        margin-bottom: 2rem;
    }
    .story-container {
        background-color: #f8f9fa;
        padding: 20px;
        border-radius: 10px;
        border-left: 5px solid #4A90E2;
        margin: 10px 0;
        color: #333;
    }
    .continuation-box {
        background-color: #e8f4fd;
        padding: 15px;
        border-radius: 8px;
        margin: 10px 0;
        border: 1px solid #b3d9ff;
        color: #333;
    }
    .genre-tag {
        background-color: #4A90E2;
        color: white;
        padding: 5px 10px;
        border-radius: 15px;
        font-size: 0.8rem;
        margin-right: 5px;
    }
    .error-box {
        background-color: #ffebee;
        padding: 15px;
        border-radius: 8px;
        border-left: 4px solid #f44336;
        margin: 10px 0;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'story_history' not in st.session_state:
    st.session_state.story_history = []
if 'current_story' not in st.session_state:
    st.session_state.current_story = ""
if 'api_configured' not in st.session_state:
    st.session_state.api_configured = False
if 'client' not in st.session_state:
    st.session_state.client = None

def configure_gemini_api(api_key):
    """Configure Gemini API with the provided key using new SDK"""
    try:
        # Set environment variable for the API key
        os.environ['GEMINI_API_KEY'] = api_key
        
        # Import the new SDK
        from google import genai
        from google.genai import types
        
        # Create client
        client = genai.Client()
        
        # Test the API with a simple request
        response = client.models.generate_content(
            model="gemini-2.0-flash-exp",
            contents="Hello",
            config=types.GenerateContentConfig(
                max_output_tokens=10,
                temperature=0.1
            )
        )
        
        st.session_state.client = client
        return True, "API configured successfully!"
        
    except ImportError:
        return False, "Please install the Google GenAI package: pip install -q -U google-genai"
    except Exception as e:
        error_msg = str(e)
        if "429" in error_msg:
            return False, "Rate limit exceeded. Please wait a few minutes or check your API quota at https://ai.google.dev/gemini-api/docs/rate-limits"
        elif "401" in error_msg or "403" in error_msg:
            return False, "Invalid API key. Please check your API key and make sure it's active."
        elif "quota" in error_msg.lower():
            return False, "API quota exceeded. Please check your billing and quota limits."
        else:
            return False, f"API Error: {error_msg}"

def generate_story_continuation(prompt, genre, creativity_level, max_length):
    """Generate story continuation using new Gemini SDK"""
    try:
        from google.genai import types
        
        # Create genre-specific system prompt
        genre_prompts = {
            "Fantasy": "You are a master fantasy storyteller. Write in the style of epic fantasy novels with magic, mythical creatures, and heroic adventures.",
            "Mystery": "You are a skilled mystery writer. Create suspenseful narratives with clues, twists, and engaging detective work.",
            "Science Fiction": "You are a science fiction author. Craft stories with futuristic technology, space exploration, and scientific concepts.",
            "Horror": "You are a horror writer. Create atmospheric, suspenseful stories that build tension and fear.",
            "Romance": "You are a romance novelist. Write heartwarming stories focused on relationships and emotional connections.",
            "Adventure": "You are an adventure writer. Create exciting stories with thrilling journeys and daring exploits.",
            "Comedy": "You are a comedy writer. Create humorous, light-hearted stories that entertain and amuse.",
            "Drama": "You are a dramatic storyteller. Write emotionally engaging stories that explore human nature and relationships."
        }
        
        system_prompt = genre_prompts.get(genre, "You are a creative storyteller.")
        
        # Adjust creativity based on temperature
        temperature_map = {
            "Conservative": 0.3,
            "Balanced": 0.7,
            "Creative": 1.0,
            "Wild": 1.3
        }
        
        temperature = temperature_map.get(creativity_level, 0.7)
        
        full_prompt = f"""{system_prompt}

Continue the following story in approximately {max_length} words. 
Make it engaging, maintain consistency with the existing narrative, and end at a natural stopping point or cliffhanger.

Story so far:
{prompt}

Continue the story:"""
        
        # Use the new SDK
        response = st.session_state.client.models.generate_content(
            model="gemini-2.0-flash-exp",
            contents=full_prompt,
            config=types.GenerateContentConfig(
                temperature=temperature,
                max_output_tokens=max_length * 4,  # Rough token estimate
                thinking_config=types.ThinkingConfig(thinking_budget=0)  # Disable thinking for faster response
            )
        )
        
        return response.text.strip()
    
    except Exception as e:
        error_msg = str(e)
        if "429" in error_msg:
            st.error("⚠️ Rate limit reached. Please wait a moment before trying again.")
        elif "quota" in error_msg.lower():
            st.error("⚠️ API quota exceeded. Please check your billing settings.")
        else:
            st.error(f"Error generating story: {error_msg}")
        return None

def generate_multiple_continuations(prompt, genre, creativity_level, max_length, num_continuations):
    """Generate multiple story continuations with rate limiting"""
    continuations = []
    progress_bar = st.progress(0)
    
    for i in range(num_continuations):
        st.text(f"Generating option {i+1} of {num_continuations}...")
        continuation = generate_story_continuation(prompt, genre, creativity_level, max_length)
        if continuation:
            continuations.append(continuation)
        else:
            st.warning(f"Failed to generate option {i+1}")
        
        progress_bar.progress((i + 1) / num_continuations)
        
        # Add delay between requests to avoid rate limiting
        if i < num_continuations - 1:  # Don't wait after the last request
            time.sleep(2)  # Wait 2 seconds between requests
    
    progress_bar.empty()
    return continuations

def save_story_to_file(story_content, filename):
    """Save story to a text file"""
    try:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        full_filename = f"{filename}_{timestamp}.txt"
        
        with open(full_filename, 'w', encoding='utf-8') as f:
            f.write(f"AI Dungeon Story - Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("="*50 + "\n\n")
            f.write(story_content)
        
        return full_filename
    except Exception as e:
        st.error(f"Error saving file: {str(e)}")
        return None

# Main App Layout
st.markdown('<h1 class="main-header"> AI Dungeon Story Generator</h1>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">Create interactive fantasy stories using AI</p>', unsafe_allow_html=True)

# Sidebar for configuration
with st.sidebar:
    st.header(" Configuration")
    
    # API Key input
    api_key = st.text_input("Gemini API Key", type="password", help="Enter your Google Gemini API key")
    
    if api_key and not st.session_state.api_configured:
        with st.spinner("Testing API connection..."):
            success, message = configure_gemini_api(api_key)
            if success:
                st.session_state.api_configured = True
                st.success(f" {message}")
            else:
                st.session_state.api_configured = False
                st.error(f" {message}")
    
    if st.session_state.api_configured:
        st.success(" API Ready")
    
    # Instructions for getting API key
    with st.expander(" How to get API Key"):
        st.markdown("""
        1. Go to [Google AI Studio](https://aistudio.google.com/)
        2. Sign in with your Google account
        3. Click "Get API Key"
        4. Create a new API key
        5. Copy and paste it above
        
        **Note:** Make sure you have quota available. New accounts get free credits.
        """)
    
    st.divider()
    
    # Story settings
    st.header(" Story Settings")
    
    genre = st.selectbox(
        "Genre",
        ["Fantasy", "Mystery", "Science Fiction", "Horror", "Romance", "Adventure", "Comedy", "Drama"],
        help="Choose the genre for your story"
    )
    
    creativity_level = st.select_slider(
        "Creativity Level",
        options=["Conservative", "Balanced", "Creative", "Wild"],
        value="Balanced",
        help="Control how creative and unpredictable the AI responses are"
    )
    
    max_length = st.slider(
        "Response Length (words)",
        min_value=50,
        max_value=300,
        value=150,
        step=25,
        help="Maximum length of each story continuation"
    )
    
    num_continuations = st.slider(
        "Number of Continuations",
        min_value=1,
        max_value=3,  # Reduced to avoid rate limits
        value=2,
        help="Generate multiple options to choose from"
    )

# Main content area
if not st.session_state.api_configured:
    st.warning(" Please enter your Gemini API key in the sidebar to get started.")
    
    # Installation instructions
    st.info("""
    **Before you start, make sure you have the right package installed:**
    
    ```bash
    pip install -q -U google-genai
    ```
    
    **To get a Gemini API key:**
    1. Go to [Google AI Studio](https://aistudio.google.com/)
    2. Sign in with your Google account
    3. Click "Get API Key" 
    4. Create a new API key
    5. Copy and paste it in the sidebar
    """)
else:
    # Story input area
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.subheader(f" {genre} Story")
        story_input = st.text_area(
            "Start your story or continue from where you left off:",
            value=st.session_state.current_story,
            height=200,
            placeholder="Once upon a time, in a land far away..."
        )
    
    with col2:
        st.markdown(f'<span class="genre-tag">{genre}</span>', unsafe_allow_html=True)
        st.markdown(f"**Creativity:** {creativity_level}")
        st.markdown(f"**Length:** {max_length} words")
        st.markdown(f"**Options:** {num_continuations}")
    
    # Generate button
    if st.button(" Generate Story Continuations", type="primary", use_container_width=True):
        if story_input.strip():
            with st.spinner(" AI is crafting your story..."):
                continuations = generate_multiple_continuations(
                    story_input, genre, creativity_level, max_length, num_continuations
                )
            
            if continuations:
                st.success(f" Generated {len(continuations)} story continuation(s)!")
                
                # Display continuations
                for i, continuation in enumerate(continuations, 1):
                    with st.expander(f" Option {i}", expanded=True):
                        st.markdown(f'<div class="continuation-box">{continuation}</div>', unsafe_allow_html=True)
                        
                        col1, col2 = st.columns(2)
                        with col1:
                            if st.button(f" Choose Option {i}", key=f"choose_{i}"):
                                st.session_state.current_story = story_input + "\n\n" + continuation
                                st.session_state.story_history.append({
                                    'timestamp': datetime.now(),
                                    'genre': genre,
                                    'content': continuation
                                })
                                st.rerun()
                        
                        with col2:
                            if st.button(f" Save Option {i}", key=f"save_{i}"):
                                filename = save_story_to_file(story_input + "\n\n" + continuation, f"{genre.lower()}_story")
                                if filename:
                                    st.success(f"Story saved as {filename}")
            else:
                st.error("Failed to generate any continuations. Please try again.")
        else:
            st.warning("Please enter some text to start your story!")
    
    # Current story display
    if st.session_state.current_story:
        st.divider()
        st.subheader(" Your Current Story")
        st.markdown(f'<div class="story-container">{st.session_state.current_story}</div>', unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button(" Continue This Story"):
                story_input = st.session_state.current_story
                st.rerun()
        
        with col2:
            if st.button(" Save Complete Story"):
                filename = save_story_to_file(st.session_state.current_story, f"{genre.lower()}_complete_story")
                if filename:
                    st.success(f"Complete story saved as {filename}")
        
        with col3:
            if st.button(" Clear Story"):
                st.session_state.current_story = ""
                st.session_state.story_history = []
                st.rerun()
    
    # Story history
    if st.session_state.story_history:
        st.divider()
        st.subheader(" Story History")
        for i, entry in enumerate(reversed(st.session_state.story_history[-5:]), 1):
            with st.expander(f"Entry {len(st.session_state.story_history) - i + 1} - {entry['genre']} ({entry['timestamp'].strftime('%H:%M:%S')})"):
                st.write(entry['content'])

# Footer
st.divider()
st.markdown("""
<div style='text-align: center; color: #666; font-size: 0.9rem;'>
    🎭 AI Dungeon Story Generator | Powered by Google Gemini | Built with Streamlit
</div>
""", unsafe_allow_html=True)