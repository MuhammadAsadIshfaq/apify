from apify import Actor
import asyncio
from src.selenium_scraper import main as selenium_main

async def main():
    async with Actor:
        input_data = await Actor.get_input() or {}
        start_date = input_data.get("start_date")  # e.g. "May 18, 2025 - 12:00 PM"

        # Run selenium_main with input param in a separate thread
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(None, selenium_main, start_date)

        # Push filtered results to dataset
        await Actor.push_data(result)

if __name__ == "__main__":
    Actor.run(main)