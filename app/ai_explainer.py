from app.ollama_client import OllamaClient


class AIExplainer:
    def __init__(self):
        self.llm = OllamaClient()

    def explain(self, connections: dict) -> str:
        prompt = f"""
You are CineNexus, an AI assistant that explains movie graph connections.

Use ONLY the graph data below.
Do not invent facts.
If there are weak or no connections, say that clearly.

Graph data:
First movie: {connections.get("first_title")}
Second movie: {connections.get("second_title")}

Shared directors:
{connections.get("shared_directors")}

Shared actors:
{connections.get("shared_actors")}

Shared genres:
{connections.get("shared_genres")}

Shared keywords:
{connections.get("shared_keywords")}

Shared release years:
{connections.get("shared_years")}

Shortest graph path:
{connections.get("shortest_path")}

Write a concise explanation in 3-6 bullet points.

Rules:
- Do not contradict the graph data.
- If a list has values, mention them.
- If a list is empty or None, say there is no evidence for that connection type.
- Do not say there are no shared actors if shared_actors contains names.
"""

        return self.llm.generate(prompt)