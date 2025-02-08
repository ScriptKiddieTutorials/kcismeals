"""ASP.NET Request Utilities"""

from bs4 import BeautifulSoup


def post(s, url, **kwargs):
    """Wrapper function for session POST requests for ASP.NET"""
    login_page = s.get(url)
    soup = BeautifulSoup(login_page.text, "html.parser")

    def get_hidden_field(name):
        tag = soup.find("input", {"name": name})
        return tag["value"] if tag else ""

    s.headers.update(
        {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Safari/537.36",
            "Referer": url,
            "Origin": url,
        }
    )

    # Extract hidden fields
    viewstate = get_hidden_field("__VIEWSTATE")
    viewstategenerator = get_hidden_field("__VIEWSTATEGENERATOR")
    eventvalidation = get_hidden_field("__EVENTVALIDATION")

    # Prepare login data
    data = {
        "__VIEWSTATE": viewstate,
        "__VIEWSTATEGENERATOR": viewstategenerator,
        "__EVENTVALIDATION": eventvalidation,
        **kwargs,
    }

    return s.post(url, data=data)
