import json

from spider_data_processing.process_database_schema import get_schema_all_databases


def read_json(file_path):
    with open(file_path, "r") as handle:
        json_file = json.load(handle)

    return json_file


def read_txt(file_path):
    with open(file_path, "r") as handle:
        text_file = handle.read()

    return text_file


def build_prompt_one_instance(
        instance,
        db_schema,
        few_shot_prompt,
        task_instruction_prompt="Translate the following question into SQL."
):

    db_id = instance["db_id"]
    schema_create_table = db_schema[db_id]["create_table_commands"]
    schema_insert_into = db_schema[db_id]["insert_into_commands"]

    schema_prompts = []
    for table_name in schema_create_table:
        if table_name in schema_insert_into:
            schema_prompt = f"{schema_create_table[table_name][0]}\n{schema_insert_into[table_name][0]}"
        else:
            schema_prompt = f"{schema_create_table[table_name][0]}"

        schema_prompts.append(schema_prompt)

    schema_prompt_all_tables = "\n".join(schema_prompts)

    question = instance["question"]

    test_instance_prompt = (
        f"{few_shot_prompt}\n\n"
        f"{schema_prompt_all_tables}\n{task_instruction_prompt}\nQuestion: {question}\nSQL:"
    )

    return test_instance_prompt


def generate_inference_prompt_all_instances(
        dev_instances_path="../data/spider/dev.json",
        few_shot_prompt_path="few_shot_prompt.txt",
        database_folder="../data/spider/database"
):

    dev_prompts = []
    dev_instances = read_json(dev_instances_path)
    db_schema = get_schema_all_databases(database_folder)
    few_shot_prompt = read_txt(few_shot_prompt_path)
    for dev_instance in dev_instances:
        dev_prompts.append(build_prompt_one_instance(dev_instance, db_schema, few_shot_prompt))

    return dev_prompts


if __name__ == "__main__":
    dev_prompts = generate_inference_prompt_all_instances()

    for dev_prompt in dev_prompts:
        print("=" * 40)
        print(dev_prompt)
        input("----")
