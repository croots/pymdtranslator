from openai import OpenAI
from tempfile import TemporaryDirectory
from time import sleep
import json
from collections import defaultdict


def openai_format(
    id: str, model: str, language: str, dialect: str, content: str
) -> dict:
    if dialect:
        system_message = f"You are a translation backend. Translate the user input into {language} using a {dialect} dialect. Only return the translation preserving the markdown structure. It is possible that you are starting mid-code block."
    else:
        system_message = f"You are a translation backend. Translate the user input into {language}. Only return the translation in the matching markdown format. It is possible that you are starting mid-code block."
    formatted_prompt = {
        "custom_id": id,
        "method": "POST",
        "url": "/v1/chat/completions",
        "body": {
            "model": model,
            "messages": [
                {"role": "system", "content": system_message},
                {"role": "user", "content": content},
            ],
            "temperature": 0.1,
        },
    }

    return formatted_prompt


def bulk_openai_format(id: str, model: str, language: str, dialect: str, sections):
    batches = []
    originals = {}
    for i, section in enumerate(sections):
        id_itter = id + f"_{i}"
        formatted_prompt = openai_format(
            id=id_itter,
            model=model,
            language=language,
            dialect=dialect,
            content=section,
        )
        batches.append(formatted_prompt)
        originals[id_itter] = section
    return batches, originals


def send_openai_batch(formatted_prompts: list, description=None):
    key = get_openapi_key()
    client = OpenAI(api_key=key)
    if not description:
        description = "Markdown translation batch"
    with TemporaryDirectory() as tmpdirname:
        with open(f"{tmpdirname}/batchinput.json", "a") as f:
            for prompt in formatted_prompts:
                f.write(json.dumps(prompt) + "\n")

        batch_input_file = client.files.create(
            file=open(f"{tmpdirname}/batchinput.json", "rb"), purpose="batch"
        )

        batch_input_file_id = batch_input_file.id

        batch = client.batches.create(
            input_file_id=batch_input_file_id,
            endpoint="/v1/chat/completions",
            completion_window="24h",
            metadata={"description": description},
        )
    return batch


def get_openapi_key() -> str:
    """Get the OpenAI API key from the environment."""
    with open(".keys") as f:
        for line in f:
            if line.startswith("OPENAI_API_KEY"):
                return line.split("=")[1].strip()
    raise ValueError("OPENAI_API_KEY not found in .keys")


def openai_check_results(batch_id: str):
    key = get_openapi_key()
    client = OpenAI(api_key=key)
    result = client.batches.retrieve(batch_id)
    return result


def wait_for_openai(batch_id: str):
    while True:
        result = openai_check_results(batch_id)
        if result.status in ["validating", "in_progress"]:
            print(f"Waiting on OpenAI (batch is {result.status})")
            sleep(5)
            continue
        else:
            break
    if result.status in ["failed", "expired", "canceling", "canceled"]:
        raise ValueError(f"OpenAI batch {batch_id} failed")


def build_openai_results(batch_id: str):
    key = get_openapi_key()
    client = OpenAI(api_key=key)
    result = openai_check_results(batch_id)

    file_response = client.files.content(result.output_file_id).text.split("\n")

    result_dict = defaultdict(dict)

    for json_str in file_response:
        if json_str == "":
            continue
        result = json.loads(json_str)
        language = result["custom_id"].split("_")[1]
        number = int(result["custom_id"].split("_")[2])
        result_dict[language][number] = result["response"]["body"]["choices"][0][
            "message"
        ]["content"]

    for language in result_dict:
        num_parts = len(result_dict[language])
        final_md = result_dict[language][0]
        for i in range(1, num_parts):
            final_md += f"\n\n{result_dict[language][i]}"
        result_dict[language] = final_md

    return result_dict


def test_openai_key():
    """Test if the OpenAI API key is valid."""
    key = get_openapi_key()
    client = OpenAI(api_key=key)

    completion = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": "You are a health-check API. Simply reply 'OK'",
            },
            {"role": "user", "content": "Check"},
        ],
    )
    if completion.choices[0].message.content == "OK":
        print("OpenAI key is valid and working")
    else:
        print(completion.choices[0].message)
