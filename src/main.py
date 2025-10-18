# from apify import Actor
# import asyncio
# from selenium_scraper import main as selenium_main

# async def main():
#     async with Actor:
#         input_data = await Actor.get_input() or {}
#         start_date = input_data.get("start_date")  # e.g. "May 18, 2025 - 12:00 PM"

#         # Run selenium_main with input param in a separate thread
#         loop = asyncio.get_event_loop()
#         result = await loop.run_in_executor(None, selenium_main, start_date)

#         # Push filtered results to dataset
#         await Actor.push_data(result)

# if __name__ == "__main__":
#     Actor.run(main)


from apify import Actor
import asyncio
from selenium_scraper import main as selenium_main

async def main():
    async with Actor:
        input_data = await Actor.get_input() or {}
        start_date = input_data.get("start_date")  # e.g. "May 18, 2025 - 12:00 PM"
        if not start_date:
            start_date = "2025-10-03T00:00:00.000Z"  # Default to today at midnight UTC

        # Run selenium_main with input param in a separate thread
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(None, selenium_main, start_date)

        # Push filtered results to dataset
        await Actor.push_data(result)

if __name__ == "__main__":
    asyncio.run(main())