import os
os.environ['CREWAI_STORAGE_DIR'] = '/app/crew_db'
import asyncio
from typing import Dict, Any
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
from crewai import Agent, LLM, Task, Crew
from crewai_tools import SerperDevTool
from crewai.flow.flow import Flow, listen, router, start
from crewai.flow.persistence import persist

load_dotenv()
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
SERPER_API_KEY = os.getenv('SerperKey')

if GOOGLE_API_KEY and SERPER_API_KEY:
    geminillm = LLM(
        model="gemini/gemini-2.0-flash",  # Or "gemini/gemini-2.0-flash" for newer models
        api_key=GOOGLE_API_KEY,
        temperature=0.7
    )

    print("✅ API keys set")
else:
    print("🚨 API keys not set")

class ContentState(BaseModel):
  """
  State model that tracks information throughout the content creation workflow.

  Think of this as a form that gets filled out as the workflow progresses:
  - Start: Only URL is filled
  - After routing: Content type is determined
  - After processing: Final content is ready
  - Throughout: Metadata can be added by any step
  """
  url: str = "" # The source website we're analyzing
  content_type: str = ""  # "blog", "newsletter", or "linkedin"
  final_content: str = ""  # The final content after processing
  metadata: Dict[str, Any] = {}  # Arbitrary metadata



def create_blog_agents():
    """Create agents specialized for blog content"""

    blog_researcher = Agent(
        role="Blog Content Researcher",
        goal="Extract and analyze web content to identify key insights for blog posts",
        backstory="""You are an expert content researcher who specializes in analyzing
        web content and identifying the most valuable insights for creating engaging blog posts.
        You excel at understanding complex topics and breaking them down into digestible content.""",
        tool=[SerperDevTool()],
        llm=geminillm,
        max_iter=5
    )

    blog_writer = Agent(
        role="Blog Content Writer",
        goal="Transform research into engaging, well-structured blog posts",
        backstory="""You are a skilled blog writer with expertise in creating compelling content
        that engages readers and drives meaningful discussions. You excel at taking complex
        information and making it accessible and interesting.""",
        llm=geminillm,
    )

    return blog_researcher, blog_writer
def create_newsletter_agents():
    """Create agents specialized for newsletter content"""

    newsletter_researcher = Agent(
        role="Newsletter Content Researcher",
        goal="Extract key insights from web content for newsletter format",
        backstory="""You are an expert at identifying the most newsworthy and actionable
        insights from web content. You understand what makes content valuable for newsletter
        subscribers and how to present information concisely.""",
        tool=[SerperDevTool()],
        llm=geminillm,
        max_iter=5
    )

    newsletter_writer = Agent(
        role="Newsletter Writer",
        goal="Create engaging newsletter content that provides immediate value",
        backstory="""You are a newsletter specialist who knows how to craft content that
        busy professionals want to read. You excel at creating scannable, actionable content
        with clear takeaways.""",
        llm=geminillm,
    )

    return newsletter_researcher, newsletter_writer

def create_linkedin_agents():
    """Create agents specialized for LinkedIn content"""

    linkedin_researcher = Agent(
        role="LinkedIn Content Researcher",
        goal="Extract professional insights suitable for LinkedIn audience",
        backstory="""You are an expert at identifying professional insights and industry
        trends that resonate with LinkedIn's professional audience. You understand what
        content drives engagement on professional networks.""",
        tool=[SerperDevTool()],
        llm=geminillm,
        max_iter=5
    )

    linkedin_writer = Agent(
        role="LinkedIn Content Writer",
        goal="Create engaging LinkedIn posts that drive professional engagement",
        backstory="""You are a LinkedIn content specialist who knows how to craft posts
        that get noticed in the professional feed. You excel at creating content that
        sparks meaningful professional discussions.""",
        verbose=True,
        llm=geminillm,
    )

    return linkedin_researcher, linkedin_writer



def create_facebook_agents():
    """Create agents specialized for Facebook content"""

    facebook_researcher = Agent(
        role="Facebook Content Researcher",
        goal="Extract and analyze web content to identify key insights for engaging Facebook posts",
        backstory="""You are an expert content researcher who specializes in analyzing
        web content and identifying the most shareable and discussion-worthy insights
        for creating engaging Facebook content that resonates with a broad audience.""",
        tools=[SerperDevTool()],
        llm=geminillm,
        max_iter=5
    )

    facebook_writer = Agent(
        role="Facebook Content Writer",
        goal="Transform research into engaging, shareable Facebook posts and updates",
        backstory="""You are a skilled Facebook writer with expertise in creating compelling content
        that captures attention and encourages interaction on the platform. You excel at crafting
        posts that are concise, visually appealing, and prompt engagement.""",
        llm=geminillm,
    )

    return facebook_researcher, facebook_writer


def create_x_agents():
    """Create agents specialized for X (formerly Twitter) content"""

    x_researcher = Agent(
        role="X Content Researcher",
        goal="Extract concise and trending insights from web content for X posts",
        backstory="""You are an expert at identifying the most impactful and tweetable
        insights from web content. You understand what trends on X and how to find
        information that can be distilled into short, engaging posts.""",
        tools=[SerperDevTool()],
        llm=geminillm,
        max_iter=5
    )

    x_writer = Agent(
        role="X Content Writer",
        goal="Create concise and engaging X posts that drive interaction",
        backstory="""You are an X content specialist who knows how to craft tweets
        that get retweeted, liked, and commented on. You excel at creating short,
        punchy content with relevant hashtags and calls to action.""",
        llm=geminillm,
    )

    return x_researcher, x_writer


def create_blog_tasks(researcher, writer, url, image_url=None):
    """Create tasks for blog content generation"""

    research_task = Task(
        description=f"""
        Analyze the content from {url} and extract key insights for a blog post.
        Your analysis should identify:
        1. Main themes and key points
        2. Interesting insights or data points
        3. Potential angles for blog content
        4. Target audience considerations
        5. SEO-worthy topics and keywords

        Provide a comprehensive research summary that will guide blog writing.
        """,
        expected_output="A detailed research summary with key insights, themes, and recommendations for blog content",
        agent=researcher
    )

    writing_task = Task(
        description=f"""
        Create an engaging blog post based on the research findings.

        Requirements:
        - 800-1200 words
        - Engaging headline
        - Clear introduction with hook
        - Well-structured body with subheadings
        - Actionable insights or takeaways
        - Strong conclusion
        - SEO-optimized content
        - Professional yet accessible tone
        - If an image URL is provided ({image_url}), suggest a suitable placement or way to incorporate it visually.

        Format the output in markdown.
        """,
        expected_output="A complete, well-structured blog post in markdown format",
        agent=writer,
        context=[research_task]
    )

    return [research_task, writing_task]

def create_newsletter_tasks(researcher, writer, url):
    """Create tasks for newsletter content generation"""

    research_task = Task(
        description=f"""
        Analyze the content from {url} and extract the most newsworthy insights for a newsletter.
        Focus on:
        1. Most important news or updates
        2. Actionable insights subscribers can use immediately
        3. Key statistics or data points
        4. Industry implications
        5. Quick takeaways for busy professionals

        Prioritize information that provides immediate value.
        """,
        expected_output="A focused research summary highlighting the most valuable and actionable insights",
        agent=researcher
    )

    writing_task = Task(
        description="""
        Create a compelling newsletter section based on the research.

        Requirements:
        - 400-600 words
        - Catchy subject line
        - Scannable format with bullet points
        - Clear action items or takeaways
        - Conversational yet professional tone
        - Include relevant links or resources
        - End with a clear call-to-action

        Format for easy reading in email.
        """,
        expected_output="A complete newsletter section with subject line and formatted content",
        agent=writer,
        context=[research_task]
    )

    return [research_task, writing_task]

def create_linkedin_tasks(researcher, writer, url):
    """Create tasks for LinkedIn content generation"""

    research_task = Task(
        description=f"""
        Analyze the content from {url} and extract insights suitable for LinkedIn audience.
        Consider what would engage LinkedIn's professional audience based on the content.
        """,
        expected_output="Research summary focused on professional insights and engagement opportunities",
        agent=researcher
    )

    writing_task = Task(
        description="""
        Create an engaging LinkedIn post based on the research.

        Requirements:
        - 150-300 words (optimal LinkedIn length)
        - Professional yet conversational tone
        - Include relevant hashtags (3-5)
        - Pose a question to encourage engagement
        - Share a key insight or lesson learned from the content
        - Use line breaks for readability
        - Include a call-to-action for comments

        Make it shareable and discussion-worthy.
        """,
        expected_output="A complete LinkedIn post with hashtags and engagement elements",
        agent=writer,
        context=[research_task]
    )

    return [research_task, writing_task]

def create_facebook_tasks(researcher, writer, url, image_url=None):
    """Create tasks for Facebook content generation"""

    research_task = Task(
        description=f"""
        Analyze the content from {url} and extract key insights suitable for engaging Facebook posts.
        Focus on identifying:
        1. Main points that would resonate with a general Facebook audience.
        2. Emotional or relatable angles.
        3. Potential visual hooks or ideas (if applicable).
        4. Insights that could spark discussion.

        Provide a research summary that highlights shareable moments and engagement opportunities for Facebook.
        """,
        expected_output="A research summary focused on insights for engaging and shareable Facebook content.",
        agent=researcher
    )

    writing_task = Task(
        description=f"""
        Create a compelling Facebook post based on the research findings.

        Requirements:
        - Engaging and conversational tone.
        - Keep it relatively concise, suitable for quick scrolling (aim for 100-300 words).
        - Use emojis appropriately to increase visual appeal and convey tone.
        - Include a clear call-to-action for likes, shares, or comments.
        - Consider using line breaks for readability.
        - The post should feel natural and engaging for a Facebook feed.
        - If an image URL is provided ({image_url}), include it at the beginning of the post.

        Format the output as a single Facebook post.
        """,
        expected_output="A complete, engaging Facebook post formatted for easy reading.",
        agent=writer,
        context=[research_task]
    )

    return [research_task, writing_task]

def create_x_tasks(researcher, writer, url, image_url=None):
    """Create tasks for X (formerly Twitter) content generation"""

    research_task = Task(
        description=f"""
        Analyze the content from {url} and extract concise, tweetable insights for X posts.
        Identify:
        1. The most impactful statistics or quotes.
        2. Key takeaways that can be summarized in a few sentences.
        3. Trending topics or hashtags related to the content.
        4. Potential angles for a punchy, attention-grabbing tweet.

        Provide a research summary focused on key points and potential hashtags for X posts.
        """,
        expected_output="A research summary with concise insights and relevant hashtags for X.",
        agent=researcher
    )

    writing_task = Task(
        description=f"""
        Create an engaging X post based on the research findings.

        Requirements:
        - Adhere to X's character limit (ensure the post is concise).
        - Use a punchy and attention-grabbing tone.
        - Include relevant hashtags (2-4).
        - Consider including a question to encourage replies and engagement.
        - Use line breaks sparingly for maximum impact.
        - The post should be highly shareable and concise.
        - If an image URL is provided ({image_url}), include it at the beginning of the post.

        Format the output as a single X post.
        """,
        expected_output="A complete, concise, and engaging X post with hashtags and engagement elements.",
        agent=writer,
        context=[research_task]
    )

    return [research_task, writing_task]


# Define the State Model for the Flow
class ContentState(BaseModel):
  """
  State model that tracks information throughout the content creation workflow.

  Think of this as a form that gets filled out as the workflow progresses:
  - Start: Only URL is filled
  - After routing: Content type is determined
  - After processing: Final content is ready
  - Throughout: Metadata can be added by any step
  """
  url: str = "" # The source website we're analyzing
  content_type: str = ""  # "blog", "newsletter", or "linkedin"
  final_content: str = ""  # The final content after processing
  metadata: Dict[str, Any] = {}  # Arbitrary metadata

@persist(verbose=True)
class ContentRouterFlow(Flow[ContentState]):
    """
    A dynamic workflow that routes content creation to specialized crews.

    Flow Overview:
    1. START: Get user input (URL + content type)
    2. ROUTE: Direct to appropriate content crew
    3. PROCESS: Execute specialized content creation
    4. FINISH: Return the final content

    This flow demonstrates:
    - Event-driven architecture with decorators
    - State management across workflow steps
    - Dynamic routing based on user input
    - Parallel processing capabilities
    """

    @start()
    def get_user_input(self):
        """Get URL and desired content type from user"""
        # The URL and content_type are already set in the state by the API endpoint
        # No need to ask for input since this is running via API
        
        # Validate that we have the required data
        if not self.state.url:
            raise ValueError("URL is required")
        if not self.state.content_type:
            raise ValueError("Content type is required")

        return "Input collected"

    @router(get_user_input)
    def route_to_crew(self, previous_result):
        """Route to appropriate crew based on content type"""
        return self.state.content_type

    @listen("blog")
    def process_blog_content(self):
        """Process content using blog crew"""
        # Create blog agents
        researcher, writer = create_blog_agents()

        # Create blog tasks
        tasks = create_blog_tasks(researcher, writer, self.state.url)

        # Create and run crew
        blog_crew = Crew(
            agents=[researcher, writer],
            tasks=tasks,
            verbose=True
        )

        result = blog_crew.kickoff()
        self.state.final_content = result

        return "Blog content created"

    @listen("newsletter")
    def process_newsletter_content(self):
        """Process content using newsletter crew"""

        # Create newsletter agents
        researcher, writer = create_newsletter_agents()

        # Create newsletter tasks
        tasks = create_newsletter_tasks(researcher, writer, self.state.url)

        # Create and run crew
        newsletter_crew = Crew(
            agents=[researcher, writer],
            tasks=tasks,
            verbose=True
        )

        result = newsletter_crew.kickoff()
        self.state.final_content = result

        return "Newsletter content created"

    @listen("linkedin")
    def process_linkedin_content(self):
        """Process content using LinkedIn crew"""

        # Create LinkedIn agents
        researcher, writer = create_linkedin_agents()

        # Create LinkedIn tasks
        tasks = create_linkedin_tasks(researcher, writer, self.state.url)

        # Create and run crew
        linkedin_crew = Crew(
            agents=[researcher, writer],
            tasks=tasks,
            verbose=True
        )

        result = linkedin_crew.kickoff()
        self.state.final_content = result

        return "LinkedIn content created"

    @listen("facebook")
    def process_facebook_content(self):
        """Process content using Facebook crew"""

        # Create Facebook agents
        researcher, writer = create_facebook_agents()

        # Create Facebook tasks
        tasks = create_facebook_tasks(researcher, writer, self.state.url)

        # Create and run crew
        facebook_crew = Crew(
            agents=[researcher, writer],
            tasks=tasks,
            verbose=True
        )

        result = facebook_crew.kickoff()
        self.state.final_content = result

        return "Facebook content created"

    @listen("x")
    def process_x_content(self):
        """Process content using X crew"""

        # Create X agents
        researcher, writer = create_x_agents()

        # Create X tasks
        tasks = create_x_tasks(researcher, writer, self.state.url)

        # Create and run crew
        x_crew = Crew(
            agents=[researcher, writer],
            tasks=tasks,
            verbose=True
        )

        result = x_crew.kickoff()
        self.state.final_content = result

        return "X content created"


app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # You can restrict to your frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
class ContentRequest(BaseModel):
    url: str
    content_type: str  # blog | newsletter | linkedin | facebook | x

@app.post("/generate-content")
async def generate_content(request: ContentRequest):
    try:
        if not geminillm:
            raise HTTPException(status_code=503, detail="LLM not initialized. Check API keys.")
            
        # Instantiate the ContentRouterFlow
        flow = ContentRouterFlow()
        
        # This is the new, correct way to pass arguments to the flow.
        # We explicitly set the state before kicking off the process.
        flow.state.url = request.url
        flow.state.content_type = request.content_type
        
        # Run the flow in a thread pool to avoid event loop conflicts
        import concurrent.futures
        loop = asyncio.get_event_loop()
        
        def run_flow():
            flow.kickoff()  # Run the flow
            return flow.state.final_content  # Return the actual content, not the flow result
            
        with concurrent.futures.ThreadPoolExecutor() as executor:
            flow_result = await loop.run_in_executor(executor, run_flow)
        
        return {
            "url": request.url,
            "content_type": request.content_type,
            "content": flow_result,
        }
    except Exception as e:
        # Your error handling is perfect for catching other unexpected issues.
        raise HTTPException(status_code=500, detail=str(e))








import re
import uuid
import pathlib
import base64
from io import BytesIO

# Optional deps used if available at runtime
try:
    import requests
    from bs4 import BeautifulSoup
except Exception:
    requests = None
    BeautifulSoup = None

# Optional Google Imagen 3 via google-generativeai
try:
    import google.generativeai as genai
    _GOOGLE_GENERATIVEAI_AVAILABLE = True
except Exception:
    _GOOGLE_GENERATIVEAI_AVAILABLE = False


# ---------- Utilities ----------

def _safe_filename() -> str:
    return f"{uuid.uuid4().hex}.png"

def _ensure_static_dir() -> str:
    out_dir = pathlib.Path("static/generated")
    out_dir.mkdir(parents=True, exist_ok=True)
    return str(out_dir)

def _extract_title_from_url(url: str) -> str:
    """
    Best-effort: fetch <title> from the URL for a more specific image prompt.
    Falls back to the URL host/path if requests/bs4 aren't available.
    """
    if requests and BeautifulSoup:
        try:
            r = requests.get(url, timeout=10)
            r.raise_for_status()
            soup = BeautifulSoup(r.text, "html.parser")
            title = (soup.title.string or "").strip() if soup.title else ""
            if title:
                return re.sub(r"\s+", " ", title)
        except Exception:
            pass
    # Fallback: strip protocol and use path
    return re.sub(r"^https?://", "", url).strip("/")


def _get_og_image(url: str) -> str | None:
    """
    Try to fetch the page's Open Graph image as a fallback if generation isn't available.
    Returns a direct URL (no local file) or None.
    """
    if not (requests and BeautifulSoup):
        return None
    try:
        r = requests.get(url, timeout=10)
        r.raise_for_status()
        soup = BeautifulSoup(r.text, "html.parser")
        tag = soup.find("meta", property="og:image")
        if tag and tag.get("content"):
            return tag["content"]
    except Exception:
        return None
    return None


def _build_image_prompt(url: str, override: str | None = None, aspect_ratio: str = "16:9") -> str:
    """
    Compose a high-quality, safe image prompt tuned for a 16:9 'cover' hero.
    """
    if override:
        core = override.strip()
    else:
        title = _extract_title_from_url(url)
        core = (f"Design a 16:9 editorial-style cover illustration that visually represents: '{title}'. "
                f"Style: clean, modern, high-contrast focal subject, subtle gradients, soft depth, "
                f"no text on image, appropriate for a blog/social header, coherent color palette.")
    return f"{core} Aspect ratio: {aspect_ratio}. Render photorealistic OR vector-illustrative depending on topic; avoid text on image."

def _find_any_image(url: str) -> str | None:
    """
    Finds and returns the URL of the first image found on a page.
    """
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')

        # Find the first <img> tag with a src attribute
        first_img = soup.find('img', src=True)
        if first_img:
            img_url = first_img['src']
            # Handle relative URLs
            if img_url.startswith('//'):
                return f"https:{img_url}"
            elif img_url.startswith('/'):
                return urljoin(url, img_url)
            return img_url

    except Exception:
        return None

    return None


def _save_bytes_png(data: bytes) -> str:
    out_dir = _ensure_static_dir()
    fname = _safe_filename()
    fpath = pathlib.Path(out_dir) / fname
    with open(fpath, "wb") as f:
        f.write(data)
    return str(fpath)


def _generate_image_via_google(prompt: str) -> str | None:
    """
    Attempts to generate an image using Google Imagen 3 models via google-generativeai.
    Returns local file path to PNG or None if unavailable.
    """
    if not (_GOOGLE_GENERATIVEAI_AVAILABLE and GOOGLE_API_KEY):
        print("google gen ai or api key missing")
        return None
    try:
        genai.configure(api_key=GOOGLE_API_KEY)
        # Prefer a fast Imagen model name if available; fall back to a general image-capable model.
        # Common names at time of writing: "imagen-3.0-generate" or "imagen-3.0-fast"
        model_names = ["imagen-3.0-fast", "imagen-3.0-generate"]
        image_bytes = None
        for name in model_names:
            try:
                model = genai.GenerativeModel(name)
                # Some SDK versions expose `generate_image` or `generate_images`.
                if hasattr(model, "generate_image"):
                    resp = model.generate_image(prompt=prompt)
                    # `resp.image` may be PIL, bytes, or base64 depending on SDK; handle robustly
                    if hasattr(resp, "image") and resp.image is not None:
                        if isinstance(resp.image, bytes):
                            image_bytes = resp.image
                        elif hasattr(resp.image, "to_bytes"):
                            image_bytes = resp.image.to_bytes()
                        elif hasattr(resp.image, "save"):
                            bio = BytesIO()
                            resp.image.save(bio, format="PNG")
                            image_bytes = bio.getvalue()
                    elif hasattr(resp, "images") and resp.images:
                        # If multiple images are returned
                        im = resp.images[0]
                        if isinstance(im, bytes):
                            image_bytes = im
                        elif hasattr(im, "to_bytes"):
                            image_bytes = im.to_bytes()
                        elif hasattr(im, "save"):
                            bio = BytesIO()
                            im.save(bio, format="PNG")
                            image_bytes = bio.getvalue()
                elif hasattr(model, "generate_images"):
                    resp = model.generate_images(prompt=prompt)
                    # Try to extract first image as bytes/base64
                    if hasattr(resp, "images") and resp.images:
                        candidate = resp.images[0]
                        if isinstance(candidate, bytes):
                            image_bytes = candidate
                        elif hasattr(candidate, "to_bytes"):
                            image_bytes = candidate.to_bytes()
                        elif isinstance(candidate, str):
                            # Some SDKs return base64 strings
                            try:
                                image_bytes = base64.b64decode(candidate)
                            except Exception:
                                pass
                if image_bytes:
                    return _save_bytes_png(image_bytes)
            except Exception:
                # Try next model name
                continue
    except Exception:
        return None
    return None


def generate_image_for_url(url: str, image_prompt_override: str | None = None, aspect_ratio: str = "16:9") -> str | None:
    """
    Public helper: builds a prompt from the URL, generates a cover image, and returns a local file path.
    Falls back to the page's Open Graph image URL if generation isn't available.
    """
    prompt = _build_image_prompt(url, image_prompt_override, aspect_ratio)
    local_path = _generate_image_via_google(prompt)
    if local_path:
        return local_path  # e.g., "static/generated/abc123.png"

    # Fallback to OG image (direct remote URL), if any
    og_image = _get_og_image(url)
    if og_image:
        return og_image

    # New fallback: find any other image on the page
    any_image = _find_any_image(url)
    if any_image:
        return any_image

    return None  # All attempts failed

# def _prepend_image_to_content(content_type: str, content: str, image_url: str | None) -> str:
#     """
#     Place the image at the top of the post intelligently per channel.
#     - blog/newsletter/linkedin: Markdown image at very top
#     - facebook/x: Show a clear 'Image:' line (platforms typically attach image separately)
#     """
#     if not image_url:
#         return content

#     if content_type in ("blog", "newsletter", "linkedin"):
#         return f"![Cover image]({image_url})\n\n{content}"

#     # For Facebook/X we keep content text clean but show the image reference first line.
#     return f"Image: {image_url}\n\n{content}"


# ---------- New endpoint that includes image at the top ----------

class ContentWithImageRequest(BaseModel):
    url: str
    content_type: str  # blog | newsletter | linkedin | facebook | x
    image_prompt_override: str | None = None
    aspect_ratio: str = "16:9"  # "16:9", "1:1", "4:5", etc.


@app.post("/generate-content-with-image")
async def generate_content_with_image(request: ContentWithImageRequest):
    """
    Generate content (using your existing flow) AND add a generated cover image at the top.
    - Builds a smart image prompt from the URL (or uses your override).
    - Tries Google Imagen 3 via google-generativeai when GOOGLE_API_KEY is set.
    - Falls back to the page's Open Graph image if generation isn't available.
    - Prepends the image to the returned content according to the target platform.
    """
    try:
        # Run the same flow you already have
        flow = ContentRouterFlow(url=request.url, content_type=request.content_type)
        await flow.kickoff_async()

        # Generate/collect an image
        image_url = generate_image_for_url(
            url=request.url,
            image_prompt_override=request.image_prompt_override,
            aspect_ratio=request.aspect_ratio
        )

        # # Put the image at the very top of the post
        # final_with_image = _prepend_image_to_content(
        #     content_type=request.content_type,
        #     content=flow.state.final_content,
        #     image_url=image_url
        # )

        return {
            "url": request.url,
            "content_type": request.content_type,
            "image_url": image_url,       # local path under /static or a remote OG URL
            "content": flow.state.final_content,  # image placed at the very top
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
