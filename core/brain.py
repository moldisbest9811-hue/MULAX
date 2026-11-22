from core.reasoning import analyze
from memory.long_term import MemoryStore


class MULAXBrain:
    def __init__(self, memory, language_model):
        self.memory = memory
        self.language_model = language_model
        self.history = []

    def respond(self, message: str) -> str:
        message = message.strip()
        if not message:
            return "I didn't receive a message."

        result = analyze(message)
        if result:
            return result

        memories = self.memory.find_relevant(message, limit=4)
        context_parts = []
        if memories:
            context_parts.append("Relevant notes from my local memory:\n" +
                                 "\n".join(f"- {item}" for item in memories))
        if self.history:
            recent = self.history[-6:]
            context_parts.append("Recent conversation:\n" + "\n".join(
                f"{role}: {content}" for role, content in recent
            ))
        context_parts.append(f"User: {message}")
        prompt = "\n\n".join(context_parts)

        if not self.language_model.available:
            return (
                "My local language model isn't loaded yet, so I can't generate "
                "a natural-language answer at this stage. I can still calculate, "
                "save memories, and retrieve matching notes. "
                "Use /model for setup status."
            )

        try:
            answer = self.language_model.generate(prompt)
        except Exception as exc:
            return f"I ran into a model error: {exc}"

        self.history.extend([("User", message), ("MULAX", answer)])
        self.history = self.history[-12:]
        return answer
