import torch



def summarize_chunk(query, chunk_text):
    tokenizer = model_loader.generator_tokenizer
    model = model_loader.generator_model

    prompt = f"""
Summarize the following section in 2-3 sentences
with respect to this question.

Question: {query}

Section:
{chunk_text}

Summary:
"""

    inputs = tokenizer(prompt, return_tensors="pt", truncation=True, max_length=512)

    with torch.no_grad():
        outputs = model.generate(
            inputs["input_ids"],
            attention_mask=inputs["attention_mask"],
            max_new_tokens=120,
            min_new_tokens=30,
            do_sample=True,
            temperature=0.7,
        )

    summary = tokenizer.decode(outputs[0], skip_special_tokens=True).strip()
    return summary

def generate_synthesis_answer(query: str, retrieved_chunks: list):
    tokenizer = model_loader.generator_tokenizer
    model = model_loader.generator_model

    # ---- MAP STAGE ----
    summaries = []

    for chunk in retrieved_chunks:
        summary = summarize_chunk(query, chunk["text"])
        summaries.append(summary)

    combined_summaries = "\n\n".join(summaries)

    # ---- REDUCE STAGE ----
    final_prompt = f"""
Using the summaries below, write a clear and structured
explanation in 4-6 sentences.

Avoid repetition.
Cover all important aspects.

Summaries:
{combined_summaries}

Final Answer:
"""

    inputs = tokenizer(final_prompt, return_tensors="pt", truncation=True, max_length=512)

    with torch.no_grad():
        outputs = model.generate(
            inputs["input_ids"],
            attention_mask=inputs["attention_mask"],
            max_new_tokens=200,
            min_new_tokens=80,
            do_sample=True,
            temperature=0.7,
            repetition_penalty=1.3,
            no_repeat_ngram_size=3
        )

    final_answer = tokenizer.decode(outputs[0], skip_special_tokens=True).strip()

    return {
        "answer": final_answer,
        "sources": retrieved_chunks
    }