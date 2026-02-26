import torch
from app.core.model_loader import model_loader


def generate_generative_answer(query: str, retrieved_chunks: list, max_chunks: int = 3):
    selected = retrieved_chunks[:max_chunks]
    context = "\n\n".join([chunk["text"] for chunk in selected])

    prompt = f"""
You are an AI tutor.

Use ONLY the context below to answer the question.
Explain clearly in 3-5 complete sentences.
If the answer is not in the context, say you don't know.

Context:
{context}

Question:
{query}

Answer:
"""

    tokenizer = model_loader.generator_tokenizer
    model = model_loader.generator_model

    inputs = tokenizer(
        prompt,
        return_tensors="pt",
        truncation=True,
        max_length=512
    )

    with torch.no_grad():
        outputs = model.generate(
            inputs["input_ids"],
            attention_mask=inputs["attention_mask"],
            max_new_tokens=150,
            temperature=0.7,
            top_p=0.9,
            do_sample=True
        )

    answer = tokenizer.decode(outputs[0], skip_special_tokens=True).strip()

    return {
        "answer": answer,
        "sources": selected
    }