import httpx

class CountryAPIClient:
    def __init__(self, base_url: str):
        self.base_url = base_url

    async def fetch_countries(self):

        async with httpx.AsyncClient(
            timeout=30.0,
            follow_redirects=True,
        ) as client:

            response = await client.get(
                f"{self.base_url}/countries"
            )

            response.raise_for_status()

            data = response.json()

            if not isinstance(data, list):
                raise ValueError(
                    "Expected a list of countries"
                )

            return data