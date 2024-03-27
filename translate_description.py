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
with open('bird_training_data_alpaca.json', 'r') as file:
    original_data = json.load(file)

# Iterate through the dictionary
for database_name, database_info in original_data.items():
    for table_name, table_info in database_info.items():
        schema = table_info["schema"]
        column_comments = table_info["column_comment"]

        # Iterate through the column comments
        for column_name, column_info in column_comments.items():
            column_description = column_info.get("column_description", "")
            value_description = column_info.get("value_description", "")
            data_format = column_info.get("data_format", "")

            # Construct the prompts
            prompt_translate_column_description = f"翻译成中文，只输出翻译结果: {column_description}" if column_description else ""
            prompt_translate_value_description = f"翻译成中文，只输出翻译结果: {value_description}" if value_description else ""

            # Call the LLM for column description translation
            if prompt_translate_column_description:
                messages = [
                    {"role": "user", "content": prompt_translate_column_description}
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

                translated_column_description = tokenizer.batch_decode(generated_ids, skip_special_tokens=True)[0]
                print(f"Column Description (English): {column_description}")
                print(f"Column Description (Chinese): {translated_column_description}")

                # Update the JSON data with the translated column description
                original_data[database_name][table_name]["column_comment"][column_name]["column_description_translated"] = translated_column_description

            # Call the LLM for value description translation
            if prompt_translate_value_description:
                messages = [
                    {"role": "user", "content": prompt_translate_value_description}
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

                translated_value_description = tokenizer.batch_decode(generated_ids, skip_special_tokens=True)[0]
                print(f"Value Description (English): {value_description}")
                print(f"Value Description (Chinese): {translated_value_description}")

                # Update the JSON data with the translated value description
                original_data[database_name][table_name]["column_comment"][column_name]["value_description_translated"] = translated_value_description

            # Write the updated JSON data to the new file
            with open('bird_training_data_alpaca_translated.json', 'w', encoding='utf-8') as output_file:
                json.dump(original_data, output_file, ensure_ascii=False, indent=2)

            print("---")
