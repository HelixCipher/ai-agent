import os
import dotenv
import requests
import trafilatura
from groq import Groq
from agent_system.core.base_tool import BaseTool
from diskcache import Cache


class NewsTool(BaseTool):
    """
    Tool for fetching and answering news-related queries using multiple search APIs and Groq's Llama model.
    """

    def __init__(self, api_key: str, cache_path: str = ".cache/news_tool"):
        dotenv.load_dotenv()
        self.groq_api_key = os.getenv("GROQ_API_KEY")
        self.rapidapi_key = os.getenv("RAPIDAPI_KEY")
        self.google_api_key = os.getenv("GOOGLE_CUSTOM_SEARCH_JSON_API")
        self.google_cx = os.getenv("GOOGLE_CX")
        self.serp_stack_key = os.getenv("SERP_STACK_API_KEY")
        self.serp_api_key = os.getenv("SERP_API_KEY")

        if not self.groq_api_key:
            raise ValueError("GROQ_API_KEY is not set. Check your .env file or environment variables.")

        # Initialize the Groq client
        self.client = Groq(api_key=self.groq_api_key)

        # Model name
        self.LLAMA_FULL_MODEL_NAME = "llama3-8b-8192"

        # Bing API Endpoint
        self.bing_search_endpoint = "https://bing-web-search1.p.rapidapi.com/search"
        self.max_retries = 3  # Max retries for API calls

        # Ensure the cache directory exists with robust handling
        try:
            os.makedirs(cache_path, exist_ok=True)
        except Exception as e:
            print(f"Error creating cache directory '{cache_path}': {e}")
            raise

        # Initialize DiskCache
        self.cache = Cache(cache_path)

    def name(self) -> str:
        return "News Tool"

    def description(self) -> str:
        return "Fetches news and answers questions using multiple APIs and Groq's Llama model."

    def cached_search(self, query: str, search_function):
        """Search with caching. Uses the provided search function."""
        if query in self.cache:
            print(f"Cache hit for query: {query}")
            return self.cache[query]

        print(f"Cache miss for query: {query}. Fetching from API...")
        results = search_function(query)
        self.cache.set(query, results, expire=7 * 24 * 60 * 60)  # Cache for 1 week
        return results

    def search_bing(self, query: str):
        """Search using Bing API."""
        try:
            headers = {
                'X-RapidAPI-Key': self.rapidapi_key,
                'X-RapidAPI-Host': 'bing-web-search1.p.rapidapi.com'
            }
            params = {'q': query, 'mkt': 'en-US'}
            response = requests.get(self.bing_search_endpoint, headers=headers, params=params)
            response.raise_for_status()
            return [
                {'name': result['name'], 'url': result['url'], 'snippet': result['snippet']}
                for result in response.json().get('webPages', {}).get('value', [])
            ]
        except requests.RequestException as e:
            print(f"Error during Bing search: {e}")
            return []

    def search_google(self, query: str):
        """Search using Google Custom Search JSON API."""
        try:
            endpoint = "https://www.googleapis.com/customsearch/v1"
            params = {
                'q': query,
                'key': self.google_api_key,
                'cx': self.google_cx
            }
            response = requests.get(endpoint, params=params)
            response.raise_for_status()
            return [
                {'name': item['title'], 'url': item['link'], 'snippet': item['snippet']}
                for item in response.json().get('items', [])
            ]
        except requests.RequestException as e:
            print(f"Error during Google Custom Search: {e}")
            return []

    def search(self, query: str):
        """Perform search using multiple APIs with fallback logic and caching."""
        apis = [
            lambda q: self.cached_search(q, self.search_bing),
            lambda q: self.cached_search(q, self.search_google),
        ]
        for api in apis:
            for _ in range(self.max_retries):
                results = api(query)
                if results:  # Return if results are found
                    return results
        print("All APIs failed to provide results.")
        return []  # Return empty list if all APIs fail

    def add_website_content(self, result: dict) -> dict:
        """Fetches and adds website content to a search result using Trafilatura."""
        try:
            result['content'] = trafilatura.extract(url=result['url'])
            return result
        except Exception as e:
            print(f"Error extracting content for {result['url']}: {e}")
            return result

    def use(self, *args, **kwargs) -> str:
        """Answers a question by fetching related news and generating a response."""
        if not args:
            return "Error: A question is required."

        question = args[0]

        try:
            # Perform a search to get results
            results = self.search(question)

            # Prepare sources for the Llama model prompt
            sources = '\n\n'.join(
                f"Source:\nTitle: {result['name']}\nURL: {result['url']}\nContent: {result['snippet']}"
                for result in results
            )

            # Construct the prompt for the Llama model
            prompt = f"Use the following sources to answer the question:\n\n{sources}\n\nQuestion: {question}\n\nAnswer:"

            # Generate response using Groq's Llama model
            completion = self.client.chat.completions.create(
                model=self.LLAMA_FULL_MODEL_NAME,
                messages=[
                    {"role": "system", "content": "You are an AI assistant designed to answer questions based on provided context."},
                    {"role": "user", "content": prompt},
                ],
                max_tokens=1024,
                temperature=0.7,
            )

            # Parse and return the response text
            response_message = completion.choices[0].message
            if isinstance(response_message, dict) and 'content' in response_message:
                return response_message['content'].strip()
            elif hasattr(response_message, 'content'):
                return response_message.content.strip()
            else:
                return "Unable to parse the response format."
        except Exception as e:
            print(f"Error generating answer: {e}")
            return "Unable to generate an answer at this time."


            # Parse and return the response text
            if hasattr(completion.choices[0].message, 'content'):
                return completion.choices[0].message.content.strip()
            elif isinstance(completion.choices[0].message, dict) and 'content' in completion.choices[0].message:
                return completion.choices[0].message['content'].strip()
            else:
                return "Unable to parse the response format."
        except Exception as e:
            print(f"Error generating answer: {e}")
            return "Unable to generate an answer at this time."
