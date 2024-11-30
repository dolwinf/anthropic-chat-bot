import httpx
import anthropic
import os
import json

client = anthropic.Anthropic(api_key=os.getenv("SONNET_API_KEY"))


def get_bard_reddit_threads():
    bard_thread_proccessed_data = []
    bard = httpx.get('https://www.reddit.com/r/Bard.json')
    bard_threads = bard.json()

    for thread in bard_threads["data"]["children"]:
        thread_title = thread["data"]["title"]
        thread_sub_data_url = thread["data"]["permalink"].rsplit(
            '/', 1)[0] + '.json'

        thread_sub_data_request = httpx.get(
            f'https://www.reddit.com{thread_sub_data_url}')

        thread_sub_data_content = thread_sub_data_request.json()
        thread_sub_data_content_body = thread_sub_data_content[
            0]["data"]["children"][0]["data"]["selftext"]

        bard_thread_proccessed_data.append(
            {"title": thread_title, "content": thread_sub_data_content_body})

    with client.messages.stream(
        max_tokens=1024,
        messages=[{
            "role": "user",
                    "content": json.dumps(bard_thread_proccessed_data)
        }],
        model="claude-3-5-sonnet-20241022",
        system="You are a summary agent and have been provided with data from reddit. Analyse the information in the array and summarise the data"
    ) as stream:
        for text in stream.text_stream:

            yield text
