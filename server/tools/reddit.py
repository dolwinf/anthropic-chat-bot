import httpx


def get_reddit_threads():
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

    print(bard_thread_proccessed_data)


if __name__ == "__main__":
    get_reddit_threads()
