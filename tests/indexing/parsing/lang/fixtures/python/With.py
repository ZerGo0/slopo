def read_file(path):
    content = ""
    with open(path) as f:
        content = f.read()
        content = content.strip()
    return content


async def fetch_data(session, url):
    data = None
    async with session.get(url) as resp:
        data = await resp.json()
        data = data["result"]
    return data
