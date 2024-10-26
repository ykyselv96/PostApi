import vertexai
from vertexai.generative_models import GenerativeModel
from core.config.system_config import settings


def policy_check(title: str, text: str) -> bool:
    """
    Checks the provided title and text for inappropriate language or offensive expressions.

    Args:
        title (str): The title to analyze.
        text (str): The text to analyze.

    Returns:
        bool: A response indicating whether inappropriate language is present (True or False).
    """
    vertexai.init(project=settings.google_cloud_project_id, location="us-central1")

    model = GenerativeModel("gemini-1.5-flash-002")

    response = model.generate_content(
        f"Are there any vulgar language, racism, or offensive expressions (all languages) in the '{title}' or in the '{text}'? Answer: 'yes/no'"
    )

    if response.text == 'yes\n' or response.text == 'Yes\n':
        return True

    return False
