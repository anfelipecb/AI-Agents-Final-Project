"""CommitteeLoader: Skill Diagnostician, Adversarial Critic, Committee (Qwen2.5-7B)."""
from ..config import COMPETENCY_DIMENSIONS, LLM_MODEL

# Five agent personas for committee deliberation (each can "cover" 1–2 competency dimensions)
AGENT_PERSONAS = [
    {"name": "Methodologist", "dimension": "methodological_reasoning", "covers": ["methodological_reasoning", "evidence_evaluation"], "system_prompt": "You are a methodologist. Focus on design choices, validity threats, scope conditions, and evidence quality. Be direct and constructive."},
    {"name": "Theorist", "dimension": "theoretical_integration", "covers": ["theoretical_integration"], "system_prompt": "You are a theorist. Focus on how well the work connects to frameworks and concepts beyond mere pattern description. Be constructive."},
    {"name": "Devil's Advocate", "dimension": "receptivity_to_critique", "covers": ["receptivity_to_critique"], "system_prompt": "You are a devil's advocate. Challenge claims and evidence so the author can strengthen their reasoning. Be sharp but fair."},
    {"name": "Encourager", "dimension": "self_reflexivity", "covers": ["self_reflexivity"], "system_prompt": "You are an encourager. Highlight assumptions and positionality; encourage awareness of limitations. Be supportive."},
    {"name": "Clarity Coach", "dimension": "argument_construction", "covers": ["argument_construction"], "system_prompt": "You are a clarity coach. Focus on logical coherence, warrants, and claim-evidence alignment. Be clear and constructive."},
]


class CommitteeLoader:
    """Loads Qwen2.5-7B; provides generate, skill_diagnostician, adversarial_critic."""

    def __init__(self, model_name: str = LLM_MODEL):
        self.model_name = model_name
        self._llm = None
        self._tokenizer = None

    @property
    def llm(self):
        if self._llm is None:
            import torch
            from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig
            qconfig = BitsAndBytesConfig(
                load_in_4bit=True,
                bnb_4bit_compute_dtype=torch.float16,
                bnb_4bit_quant_type="nf4",
                bnb_4bit_use_double_quant=True,
            )
            self._tokenizer = AutoTokenizer.from_pretrained(self.model_name)
            self._llm = AutoModelForCausalLM.from_pretrained(
                self.model_name,
                quantization_config=qconfig,
                device_map="auto",
                torch_dtype=torch.float16,
            )
        return self._llm

    @property
    def tokenizer(self):
        _ = self.llm
        return self._tokenizer

    def generate(
        self,
        prompt: str,
        system_prompt: str | None = None,
        max_new_tokens: int = 512,
        temperature: float = 0.7,
        do_sample: bool = True,
    ) -> str:
        """Generate a response from the language model."""
        import torch
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        text = self.tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
        inputs = self.tokenizer(text, return_tensors="pt").to(self.llm.device)

        gen_kwargs = dict(max_new_tokens=max_new_tokens, do_sample=do_sample, pad_token_id=self.tokenizer.eos_token_id)
        if do_sample:
            gen_kwargs.update(dict(temperature=temperature, top_p=0.9))

        with torch.no_grad():
            output_ids = self.llm.generate(**inputs, **gen_kwargs)
        response = self.tokenizer.decode(output_ids[0][inputs.input_ids.shape[1]:], skip_special_tokens=True)
        return response.strip()

    def skill_diagnostician(self, thesis: str) -> str:
        """Identify 1-2 research skill gaps; return Socratic questions."""
        prompt = f"""As a Skill Diagnostician, identify 1-2 research skill gaps in this thesis (hedging, methodology, evidence-claim alignment). Return 1-2 Socratic questions. Thesis: {thesis[:500]}"""
        return self.generate(prompt, system_prompt="You are a thesis advisor. Be constructive.", max_new_tokens=200)

    def adversarial_critic(self, thesis: str, questions: str) -> str:
        """Give targeted critique challenging framing and evidence."""
        prompt = f"""Thesis: {thesis[:400]}
Diagnostic questions: {questions}
As an Adversarial Critic, give targeted critique challenging framing and evidence. Be direct but constructive."""
        return self.generate(prompt, system_prompt="You are a critical but constructive reviewer.", max_new_tokens=250)

    def assemble_committee(self, profile: dict) -> list[dict]:
        """Select 3 agents from persona pool based on lowest-scoring competency dimensions.

        profile: From diagnose_competencies(); keys are dimension names, values are {score, justification}.
        Returns list of 3 persona dicts (name, dimension, covers, system_prompt).
        """
        dim_scores = []
        for dim in COMPETENCY_DIMENSIONS:
            val = profile.get(dim, {})
            score = val.get("score", 3) if isinstance(val, dict) else 3
            dim_scores.append((dim, score))
        dim_scores.sort(key=lambda x: x[1])
        lowest_dims = [d[0] for d in dim_scores[:3]]
        agents = []
        used = set()
        for dim in lowest_dims:
            for persona in AGENT_PERSONAS:
                if persona in agents:
                    continue
                covers = persona.get("covers", [persona["dimension"]])
                if dim in covers:
                    agents.append(persona)
                    used.add(persona["name"])
                    break
        while len(agents) < 3:
            for p in AGENT_PERSONAS:
                if p["name"] not in used:
                    agents.append(p)
                    used.add(p["name"])
                    break
            if len(agents) >= 3:
                break
        return agents[:3]

    def committee_deliberation(self, thesis: str, agents: list[dict]) -> str:
        """Each agent reviews the thesis independently; synthesize into consolidated feedback."""
        thesis_excerpt = thesis[:600]
        reviews = []
        for agent in agents:
            prompt = f"""Review this thesis excerpt and provide brief, targeted feedback from your perspective. Thesis: {thesis_excerpt}"""
            rev = self.generate(
                prompt,
                system_prompt=agent["system_prompt"],
                max_new_tokens=200,
            )
            reviews.append(f"[{agent['name']}]: {rev}")
        synthesis_prompt = "Synthesize the following committee reviews into one consolidated feedback paragraph (3-5 sentences) for the student.\n\n" + "\n\n".join(reviews)
        return self.generate(synthesis_prompt, system_prompt="You produce clear, actionable consolidated feedback.", max_new_tokens=300)
