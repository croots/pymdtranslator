import re
import json
import random
import uuid
import datetime
import pathlib

from .openai_wrapper import *
from time import sleep


def yield_blog_post_sections(file, word_limit):
    file_string = ""
    with open(file, "r") as f:
        for line in f:
            file_string += line
            if line != "\n":
                continue
            content_split = re.split(r"\n| ", file_string)
            content_split = [x for x in content_split if x]
            if len(content_split) >= word_limit:
                yield file_string
                file_string = ""
    if file_string:
        yield file_string


def request_translation(file, word_limit=250):
    language_config = json.load(open(".languagesettings.json"))

    batch_UUID = str(uuid.uuid4())

    openai_batches = []
    openai_originals = {}

    for language in language_config:
        if language_config[language]["provider"] == "openai":
            if language_config[language]["dialect"]:
                dialect = language_config[language]["dialect"]
            else:
                dialect = ""
            formatted_prompts = bulk_openai_format(
                id=f"{batch_UUID}_{language}",
                model=language_config[language]["model"],
                language=language,
                dialect=dialect,
                sections=yield_blog_post_sections(file, word_limit),
            )
            openai_batches += formatted_prompts[0]
            openai_originals.update(formatted_prompts[1])

    if openai_batches:
        batch = send_openai_batch(openai_batches)
        batch_id = batch.id
    else:
        batch_id = None

    run_information = {
        "batch_UUID": batch_UUID,
        "openai_batch_id": batch_id,
        "openai_original": openai_originals,
        "file_name": file,
    }

    json.dump(run_information, open(f"batch_{batch_UUID}.json", "w"))

    print(f"Batch {batch_UUID} created")

    build_batch(batch_UUID)


def build_batch(batch_id):
    run_information = json.load(open(f"batch_{batch_id}.json"))
    language_config = json.load(open(".languagesettings.json"))

    orignal_file = pathlib.Path(run_information["file_name"])

    file_type = orignal_file.suffix
    file_name = orignal_file.stem

    results = {}

    if run_information["openai_batch_id"]:
        wait_for_openai(run_information["openai_batch_id"])
        openai_data = build_openai_results(run_information["openai_batch_id"])
        results.update(openai_data)

    for language in results:
        language_data = language_config[language]
        destination_file = f"{file_name}.{language_data["code"]}{file_type}"
        with open(destination_file, "w") as f:
            f.write(results[language])
        print(f"Translation for {language} saved to {destination_file}")
