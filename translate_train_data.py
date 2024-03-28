import json
from transformers import AutoModelForCausalLM, AutoTokenizer

# Load the LLM model and tokenizer
device = "cuda"  # the device to load the model onto

model = AutoModelForCausalLM.from_pretrained(
    "/var/run/media/star/dataset7/LLM/Storage/Qwen_Qwen1.5-14B-Chat",
    torch_dtype="auto",
    device_map="auto",
    local_files_only=True
)
tokenizer = AutoTokenizer.from_pretrained("/var/run/media/star/dataset7/LLM/Storage/Qwen_Qwen1.5-14B-Chat")

# Open the original JSON file
with open('train.json', 'r') as file:
    data = json.load(file)

# Open the output file for writing
with open('train_translated.json', 'w', encoding='utf-8') as output_file:
    output_file.write('[')  # Start with an opening bracket

    # Iterate through the data
    for i, item in enumerate(data):
        db_id = item["db_id"]
        question = item["question"]
        evidence = item["evidence"]
        sql = item["SQL"]

        # Translate the question
        messages = [
            {"role": "user", "content": f"Translate the following text to Chinese: {question}"}
        ]
        text = tokenizer.apply_chat_template(
            messages,
            tokenize=False,
            add_generation_prompt=True
        )
        model_inputs = tokenizer([text], return_tensors="pt").to(device)

        generated_ids = model.generate(
            model_inputs.input_ids,
            max_new_tokens=512
        )
        generated_ids = [
            output_ids[len(input_ids):] for input_ids, output_ids in zip(model_inputs.input_ids, generated_ids)
        ]

        question_translated = tokenizer.batch_decode(generated_ids, skip_special_tokens=True)[0]

        # Translate the evidence
        messages = [
            {"role": "user", "content": f"Translate the following text to Chinese: {evidence}"}
        ]
        text = tokenizer.apply_chat_template(
            messages,
            tokenize=False,
            add_generation_prompt=True
        )
        model_inputs = tokenizer([text], return_tensors="pt").to(device)

        generated_ids = model.generate(
            model_inputs.input_ids,
            max_new_tokens=512
        )
        generated_ids = [
            output_ids[len(input_ids):] for input_ids, output_ids in zip(model_inputs.input_ids, generated_ids)
        ]

        evidence_translated = tokenizer.batch_decode(generated_ids, skip_special_tokens=True)[0]

        # Create a new dictionary with the translated data
        translated_item = {
            "db_id": db_id,
            "question": question,
            "question_translated": question_translated,
            "evidence": evidence,
            "evidence_translated": evidence_translated,
            "SQL": sql
        }

        # Write the translated item to the output file
        json.dump(translated_item, output_file, ensure_ascii=False, indent=4)

        # Add a comma after each item, except for the last one
        if i < len(data) - 1:
            output_file.write(',')

        output_file.write('\n')  # Add a newline for better readability

    output_file.write(']')  # Close the JSON array
