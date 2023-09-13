# Spider Data Processing
This folder contains the script to generate the few-shot prompt for few-shot natural language to SQL.

To generate the few-shot inference example, follow these steps:

1, Download the spider data so that the data has the following directory:
`constrained-code-generation/data/spider/`

2, Run `generate_fewshot_prompt.py`. This will call the `process_database_schema.py` and generate the prompt of the few-shot exemplars of a few selected database. Currently the exemplars are randomly chosen from all databases. 8 exemplars are chosen, but you can change the strategy to select the few-shot exemplars.

After running, a `few_shot_prompt.txt` will be saved the current folder. The format of the prompt resembles the paper [Teaching Large Language Models to Self-Debug](https://arxiv.org/abs/2304.05128).

3, Run `generate_inference_prompt.py` or import this module in another script to get the prompt for each dev example. It will read the `few_shot_prompt.txt` and concatenate it with each dev example to form the dev prompt.