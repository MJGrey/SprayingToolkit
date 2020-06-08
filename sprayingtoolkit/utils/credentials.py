import asyncio
import pathlib
import logging
import csv

log = logging.getLogger("atomizer.utils.credentials")


async def automatic_cred_generator(credential):
    cred_file = pathlib.Path(credential)
    if cred_file.exists():
        if cred_file.suffix == ".csv":
            log.debug(f"Detected {cred_file} as a CSV file")
            # TO DO: Handle CSV files
            raise NotImplementedError
        else:
            # Assume its a txt file with an entry on each line
            log.debug(f"Detected {cred_file} as a txt file")
            with cred_file.open() as cf:
                for line in cf:
                    yield line.strip("\n")
    else:
        # If the file doesn't exist, assume it's a string
        log.debug(f"Detected {cred_file} as a string")
        yield credential
