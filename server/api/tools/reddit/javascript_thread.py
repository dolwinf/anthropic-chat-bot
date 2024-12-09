import httpx
import anthropic
import os
import json
import time

client = anthropic.Anthropic(api_key=os.getenv("SONNET_API_KEY"))

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}


def get_javascript_reddit_threads():
    javascript_thread_proccessed_data = []
    yield "\n\n Fetching top 7 titles from r/javascript"
    javascript_res = httpx.get(
        'https://www.reddit.com/r/javascript.json', headers=headers)
    javascript_threads = javascript_res.json()

    for thread in javascript_threads["data"]["children"][0:8]:
        thread_title = thread["data"]["title"]
        yield f"\n\n Content: {thread_title}"
        thread_sub_data_url = thread["data"]["permalink"].rsplit(
            '/', 1)[0] + '.json'

        time.sleep(1)

        thread_sub_data_request = httpx.get(
            f'https://www.reddit.com{thread_sub_data_url}', headers=headers)

        thread_sub_data_content = thread_sub_data_request.json()
        thread_sub_data_content_body = thread_sub_data_content[
            0]["data"]["children"][0]["data"]["selftext"]

        javascript_thread_proccessed_data.append(
            {"title": thread_title, "content": thread_sub_data_content_body})

    yield "\n\n Collected data, summarising content....."

    with client.messages.stream(
        max_tokens=1024,
        messages=[{
            "role": "user",
                    "content": json.dumps(javascript_thread_proccessed_data)
        }],
        model="claude-3-5-sonnet-20241022",
        system="You are a summary agent and have been provided with data from reddit. Analyse the information in the array and summarise the data"
    ) as stream:
        for text in stream.text_stream:

            yield text
