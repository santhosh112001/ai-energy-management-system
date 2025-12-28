import google.generativeai as genai

def generate_ai_insights(summary_df, api_key):
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("gemini-pro")

    prompt = f"""
    You are a senior industrial energy engineer.

    Analyze this monthly equipment performance summary:
    {summary_df.to_string()}

    Provide:
    1. Major inefficiencies
    2. Probable root causes
    3. Engineering corrective actions
    4. Expected cost-saving opportunities
    """

    response = model.generate_content(prompt)
    return response.text

