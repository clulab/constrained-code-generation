"""Randomly select k few-shot examples from the training set and save the prompt as txt."""
import json
import random

from spider_data_processing.process_database_schema import get_schema_all_databases


def read_json(
    json_file_path="../data/spider/train_spider.json"
):

    with open(json_file_path, "r") as handle:
        json_file = json.load(handle)

    return json_file


def generate_prompt_one_instance(instance, db_schema):

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
    answer = instance["query"]

    task_instruction_prompt = "Translate the following question into SQL."
    few_shot_prompt = f"{schema_prompt_all_tables}\n{task_instruction_prompt}\nQuestion: {question}\nSQL: {answer}"

    return few_shot_prompt


def generate_prompt_all_instances(few_shot_instances, db_schema, debug_flag=False):

    if debug_flag:
        print("=" * 40)
        print("selected tables:")
        print([i["db_id"] for i in few_shot_instances])

    few_shot_prompts = []
    for instance in few_shot_instances:
        prompt_one_instance = generate_prompt_one_instance(instance, db_schema)
        few_shot_prompts.append(prompt_one_instance)

    few_shot_prompt = "\n\n".join(few_shot_prompts)

    return few_shot_prompt


def save_prompt(
        few_shot_prompt,
        prompt_file_save_path="few_shot_prompt.txt"
):

    with open(prompt_file_save_path, "w") as handle:
        handle.write(few_shot_prompt)


def generate_and_save_few_shot_prompt(
        train_instance_file_path="../data/spider/train_spider.json",
        db_schema_folder_path="../data/spider/database",
        n_few_shot=8,
        seed=42,
        debug_flag=False
):

    db_schemas = get_schema_all_databases(db_schema_folder_path)
    train_instances = read_json(train_instance_file_path)

    random.seed(seed)
    selected_instances = random.sample(train_instances, n_few_shot)
    few_shot_prompt = generate_prompt_all_instances(selected_instances, db_schemas, debug_flag=debug_flag)

    save_prompt(few_shot_prompt)

    return few_shot_prompt


if __name__ == "__main__":
    generate_and_save_few_shot_prompt(debug_flag=True)
