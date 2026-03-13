"""CommitteeLoader: Skill Diagnostician, Adversarial Critic (Qwen2.5-7B)."""
from ..config import LLM_MODEL


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
