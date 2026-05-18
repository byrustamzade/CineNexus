from app.ai_explainer import AIExplainer


class _FakeLLM:
    def __init__(self) -> None:
        self.last_prompt = ""

    def generate(self, prompt: str) -> str:
        self.last_prompt = prompt
        return "ok"


def test_explain_embeds_connection_data_in_prompt() -> None:
    explainer = AIExplainer()
    fake_llm = _FakeLLM()
    explainer.llm = fake_llm

    result = explainer.explain(
        {
            "first_title": "Inception",
            "second_title": "Interstellar",
            "shared_directors": ["Christopher Nolan"],
            "shared_actors": ["Michael Caine"],
            "shared_genres": ["Science Fiction"],
            "shared_keywords": ["space travel"],
            "shared_years": [],
            "shortest_path": ["Movie:Inception", "Person:Christopher Nolan"],
        }
    )

    assert result == "ok"
    assert "First movie: Inception" in fake_llm.last_prompt
    assert "Second movie: Interstellar" in fake_llm.last_prompt
    assert "Christopher Nolan" in fake_llm.last_prompt
