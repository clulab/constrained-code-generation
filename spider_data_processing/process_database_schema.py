import json
import os
import re


def remove_line_trailing_space(line):

    idx = 0
    while idx < len(line) and (line[idx] == " " or line[idx] == "\t" or line[idx] == "\n"):
        idx += 1

    return line[idx:]


def clean_table_name(table_name_raw):
    if table_name_raw.startswith("\"") or \
         table_name_raw.startswith("\'") or \
         table_name_raw.startswith("`"):
        table_name = table_name_raw[1:-1]
    else:
        table_name = table_name_raw

    return table_name


def remove_double_newlines(line):
    return re.sub(r"\n{2,}", "\n", line)


def get_schema_one_database(
        database_dir,
        print_other_keywords_flag=False
):
    """
    Get and process the schema file
    No schema:
    chinook_1, company_1, epinions_1, flight_4, icfp_1, small_bank_1, twitter_1, voter_1, world_1

    Schema file not named as schema.sql:
    car_1, college_1, college_2, flight_2, formula_1, inn_1, student_1, wine_1, wta_1
    """

    schema_file_dir = os.path.join(database_dir, "schema.sql")
    if not os.path.exists(schema_file_dir):

        database_files = os.listdir(database_dir)
        schema_files = [x for x in database_files if x.endswith(".sql")]

        if len(schema_files) == 1:
            schema_file_dir = os.path.join(database_dir, schema_files[0])
        else:
            schema_file_dir = None

    if schema_file_dir:
        with open(schema_file_dir) as handle:
            file_plain_text = handle.read()

        # First step: remove the comments:
        file_plain_text_lines = file_plain_text.split("\n")
        file_plain_text_lines = [l for l in file_plain_text_lines if not l.startswith("/*") and not l.startswith("--")]
        file_plain_text = "\n".join(file_plain_text_lines)

        lines = file_plain_text.split(";\n")
        lines = [l for l in lines if l]  # remove empty line
        lines = [remove_line_trailing_space(l) for l in lines]
        lines = [l for l in lines if l]  # remove empty line
        lines = [f"{l};" for l in lines]

        # group lines by keywords:
        lines_by_keyword = {
            "pragma": [],
            "create table": [],
            "insert into": [],
            "others": []
        }
        for l in lines:

            if l.lower().startswith("pragma"):
                lines_by_keyword["pragma"].append(l)
            elif l.startswith("create table") or l.startswith("CREATE TABLE") or l.startswith("Create table"):
                lines_by_keyword["create table"].append(l)
            elif l.startswith("insert into") or l.startswith("INSERT INTO") or l.startswith("Insert into"):
                lines_by_keyword["insert into"].append(l)
            else:
                lines_by_keyword["others"].append(l)

                # Other keywords at least include the following:
                # - begin transaction
                # - commit
                # comment, such as /* --- */
                # delete from
                # -- drop table
                # DROP TABLE
                # -- or ---- (hr_1 database, sakila_1 database)
                # create index
                # create unique index (store_1 database)
                # CRloser_rank_pointsEATE TABLE players (wta_1 database, I think this is a mistake?)

        if print_other_keywords_flag:
            if len(lines_by_keyword["others"]) > 0:
                print("=" * 40)
                for l in lines_by_keyword["others"]:
                    print(f"\t{l}")

                print(database_dir)
                input("---")

        unique_tables_create = {}
        for l in lines_by_keyword["create table"]:
            e1 = re.findall(r"create table\s+([a-zA-Z0-9_\'\"`]+?)\s*\(", l)
            e2 = re.findall(r"CREATE TABLE\s+([a-zA-Z0-9_\'\"`]+?)\s*\(", l)
            e3 = re.findall(r"Create table\s+([a-zA-Z0-9_\'\"`]+?)\s*\(", l)
            e4 = re.findall(r"create table if not exists\s+([a-zA-Z0-9_\'\"`]+?)\s*\(", l)
            e5 = re.findall(r"CREATE TABLE IF NOT EXISTS\s+([a-zA-Z0-9_\'\"`]+?)\s*\(", l)
            e6 = re.findall(r"Create table if not exists\s+([a-zA-Z0-9_\'\"`]+?)\s*\(", l)

            if len(e1) > 0:
                table_name = clean_table_name(e1[0])

            elif len(e2) > 0:
                table_name = clean_table_name(e2[0])

            elif len(e3) > 0:
                table_name = clean_table_name(e3[0])

            elif len(e4) > 0:
                table_name = clean_table_name(e4[0])

            elif len(e5) > 0:
                table_name = clean_table_name(e5[0])

            elif len(e6) > 0:
                table_name = clean_table_name(e6[0])

            else:
                print(f"no extraction? line:{l}")
                input("--")
                table_name = "error"

            if table_name not in unique_tables_create:
                unique_tables_create[table_name] = []
            unique_tables_create[table_name].append(remove_double_newlines(l))

        unique_tables_insert = {}
        for l in lines_by_keyword["insert into"]:
            e1 = re.findall(r"insert into\s+([a-zA-Z0-9_\'\"`]+?)\s+values", l)
            e2 = re.findall(r"INSERT INTO\s+([a-zA-Z0-9_\'\"`]+?)\s+VALUES", l)
            e3 = re.findall(r"Insert into\s+([a-zA-Z0-9_\'\"`]+?)\s+values", l)
            e4 = re.findall(r"insert into\s+([a-zA-Z0-9_\'\"`]+?)\s*\(", l)
            e5 = re.findall(r"INSERT INTO\s+([a-zA-Z0-9_\'\"`]+?)\s*\(", l)
            e6 = re.findall(r"Insert into\s+([a-zA-Z0-9_\'\"`]+?)\s*\(", l)

            if len(e1) > 0:
                table_name = clean_table_name(e1[0])

            elif len(e2) > 0:
                table_name = clean_table_name(e2[0])

            elif len(e3) > 0:
                table_name = clean_table_name(e3[0])

            elif len(e4) > 0:
                table_name = clean_table_name(e4[0])

            elif len(e5) > 0:
                table_name = clean_table_name(e5[0])

            elif len(e6) > 0:
                table_name = clean_table_name(e6[0])

            else:
                table_name = "error"
                print(f"no extraction? line:{l}")
                input("--")

            if table_name not in unique_tables_insert:
                unique_tables_insert[table_name] = []
            unique_tables_insert[table_name].append(remove_double_newlines(l))

        # Table name: no quote, or `XXX`, or 'XXX', or "XXX"

        return {
            "create_table_commands": unique_tables_create,
            "insert_into_commands": unique_tables_insert
        }

    else:
        return {
            "create_table_commands": [],
            "insert_into_commands": []
        }


def get_schema_all_databases(
    database_folder="../data/spider/database"
):

    all_database_subfolders = os.listdir(database_folder)
    all_database_subfolders = list(sorted(all_database_subfolders))

    all_database_subfolders = [f for f in all_database_subfolders if not f.startswith(".")]
    all_database_dirs = [os.path.join(database_folder, d) for d in all_database_subfolders]

    print("=" * 40)
    print("total number of databases:", len(all_database_dirs))  # 166 databases

    database_schemas = {}

    for idx in list(range(len(all_database_subfolders))):

        database_name = all_database_subfolders[idx]
        database_dir = all_database_dirs[idx]
        database_schema = get_schema_one_database(database_dir)

        database_schemas[database_name] = database_schema

    return database_schemas
