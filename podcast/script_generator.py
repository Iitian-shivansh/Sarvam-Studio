import json
import re
from typing import List, Dict, Any, Optional
from sarvamai import SarvamAI


class PodcastScriptGenerator:
    """
    Generates natural, multi-speaker podcast scripts using Sarvam AI (sarvam-105b-conversations).
    """

    def __init__(self, client: Optional[SarvamAI] = None):
        self.client = client or SarvamAI()

    def generate(
        self,
        topic: str,
        source_text: Optional[str] = None,
        language: str = "English",
        num_turns: int = 8,
        host_1_name: str = "Rohan",
        host_2_name: str = "Priya",
        tone: str = "conversational, engaging, and lively",
    ) -> List[Dict[str, str]]:
        """
        Generate a multi-speaker podcast script as a list of dialogue turns.
        Each turn is a dict: {"speaker": "...", "text": "..."}
        """

        context_block = ""
        if source_text:
            context_block = f"""
SOURCE MATERIAL / REFERENCE NOTES:
\"\"\"
{source_text[:4000]}
\"\"\"
Incorporate key insights and facts from the source material above into the discussion.
"""

        system_prompt = (
            "You are an award-winning podcast producer and scriptwriter. "
            "You write dynamic, hyper-realistic, 2-host audio podcast scripts."
        )

        user_prompt = f"""Write a compelling podcast conversation between two hosts:
- Host 1: **{host_1_name}** (Host, energetic, curious, hooks the listener, asks thought-provoking questions)
- Host 2: **{host_2_name}** (Co-host, domain specialist, insightful, explains ideas with vivid analogies)

TOPIC: "{topic}"
LANGUAGE: {language}
TONE: {tone}
APPROXIMATE TURNS: {num_turns} exchanges total
{context_block}

RULES FOR REALISTIC DIALOGUE:
1. Make it sound like two friends who love talking about this topic. Use natural conversational rhythm, quick reactions ("Wait, really?", "Exactly!", "Here's the crazy part..."), and casual phrasing.
2. Avoid robotic bullet points or lecture-style monologues. Keep each turn between 1 and 3 sentences.
3. Start with an attention-grabbing hook and end with a memorable sign-off.
4. Output MUST BE strictly valid JSON in the following schema, with no markdown formatting outside the JSON:

[
  {{"speaker": "{host_1_name}", "text": "..."}},
  {{"speaker": "{host_2_name}", "text": "..."}}
]
"""

        response = self.client.chat.completions(
            model="sarvam-105b-conversations",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.7,
        )

        content = response.choices[0].message.content.strip()
        return self._parse_json(content, host_1_name, host_2_name)

    def _parse_json(self, raw_content: str, host_1: str, host_2: str) -> List[Dict[str, str]]:
        """Safely parses JSON script from the LLM output."""
        # Remove markdown code blocks if present
        clean_text = raw_content
        if "```" in clean_text:
            match = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", clean_text)
            if match:
                clean_text = match.group(1).strip()

        try:
            data = json.loads(clean_text)
            # If wrapped in a dict e.g. {"dialogue": [...]} or {"script": [...]}
            if isinstance(data, dict):
                for key in ["dialogue", "script", "turns", "conversation", "episodes", "items"]:
                    if key in data and isinstance(data[key], list):
                        data = data[key]
                        break
                else:
                    for val in data.values():
                        if isinstance(val, list) and len(val) > 0 and isinstance(val[0], dict):
                            data = val
                            break

            if isinstance(data, list) and len(data) > 0:
                validated = []
                for item in data:
                    if not isinstance(item, dict):
                        continue
                    speaker = item.get("speaker", host_1).strip()
                    text = item.get("text", "").strip()
                    if text:
                        validated.append({"speaker": speaker, "text": text})
                if validated:
                    return validated
        except json.JSONDecodeError:
            pass

        # Fallback regex parser for line-by-line speaker: text
        lines = raw_content.splitlines()
        fallback_script = []
        for line in lines:
            line = line.strip()
            if not line:
                continue
            for host in [host_1, host_2]:
                if line.lower().startswith(f"{host.lower()}:"):
                    text = line[len(host) + 1 :].strip().strip('"')
                    if text:
                        fallback_script.append({"speaker": host, "text": text})
                    break

        if fallback_script:
            return fallback_script

        raise ValueError(f"Could not parse valid script from Sarvam response:\n{raw_content}")
