"""Run the file lifecycle cleanup once."""

import asyncio

from app.database import async_session_factory
from app.services.file import cleanup_expired_files


async def main() -> None:
    async with async_session_factory() as db:
        result = await cleanup_expired_files(db)
    print(
        f"Expired temporary files: {result['expired']}; "
        f"removed stored objects: {result['removed_content']}; "
        f"purged metadata: {result['purged_metadata']}"
    )


if __name__ == "__main__":
    asyncio.run(main())
