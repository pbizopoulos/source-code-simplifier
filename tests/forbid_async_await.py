import asyncio


async def sleep():
    await asyncio.sleep(1)


def main():
    asyncio.run(sleep())


if __name__ == '__main__':
    main()
