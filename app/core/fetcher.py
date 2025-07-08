import json


def create_browser_fetcher(driver, base_url):
    def make_request(endpoint, payload, method='POST'):
        cookie = driver.run_js("return document.cookie;")
        user_agent = driver.run_js("return navigator.userAgent;")

        script = f'''
        return new Promise((resolve) => {{
            fetch("{endpoint}", {{
                method: "{method}",
                headers: {{
                    "Content-Type": "application/json",
                    "Accept": "application/json, text/plain, */*",
                    "X-Requested-With": "XMLHttpRequest",
                    "Referer": "{base_url}/",
                    "Origin": "{base_url}",
                    "User-Agent": "{user_agent}",
                    "Cookie": "{cookie}"
                }},
                body: JSON.stringify({json.dumps(payload)})
            }})
            .then(resp => resp.text())
            .then(txt => {{
                try {{
                    resolve({{success: true, data: JSON.parse(txt)}})
                }} catch (e) {{
                    resolve({{success: false, error: "JSON parse error", html_snippet: txt.slice(0, 300)}})
                }}
            }})
            .catch(err => {{
                resolve({{success: false, error: err.toString()}})
            }});
        }});
        '''

        try:
            result = driver.run_js(script)
            if result and result.get("success"):
                return result["data"]
            else:
                raise Exception(f"Request failed: {result}")
        except Exception as e:
            return {"error": str(e)}

    return make_request
