from google import genai
from google.genai.errors import ClientError


def generate_ai_insights(summary_df, api_key):
    client = genai.Client(api_key=api_key)

    prompt = f"""
You are an industrial energy consultant.

Generate the report using EXACT section tags shown below.
Do NOT repeat headings.
Do NOT use markdown.
Do NOT add extra sections.

[EXEC_SUMMARY]
(3–4 lines, management friendly)

[KEY_FINDINGS]
(bulleted points)

[ROOT_CAUSES]
(bulleted points)

[CORRECTIVE_ACTIONS]
(bulleted, priority based)

[COST_SAVINGS]
(monthly and annual Rs values)

DATA:
{summary_df.to_string(index=False)}
"""

    try:
        response = client.models.generate_content(
            model="models/gemini-flash-latest",
            contents=prompt
        )
        return response.text

    except ClientError as e:
        return (
            "[EXEC_SUMMARY]\nAI service temporarily unavailable.\n\n"
            "[KEY_FINDINGS]\n- Free tier quota exhausted.\n\n"
            "[ROOT_CAUSES]\n- API rate limit.\n\n"
            "[CORRECTIVE_ACTIONS]\n- Retry later or use another API key.\n\n"
            "[COST_SAVINGS]\n- Not calculated.\n"
        )
