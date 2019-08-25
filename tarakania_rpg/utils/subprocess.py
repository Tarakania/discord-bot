import logging

from typing import IO, Any, Tuple, AnyStr, Optional
from asyncio import subprocess

log = logging.getLogger(__name__)


async def create_subprocess_exec(
    *args: str,
    stdout: Optional[IO[AnyStr]] = None,
    stderr: Optional[IO[AnyStr]] = None,
) -> subprocess.Process:
    return await subprocess.create_subprocess_exec(
        *args,
        stdout=stdout or subprocess.PIPE,
        stderr=stderr or subprocess.PIPE,
    )


async def create_subprocess_shell(
    program: str,
    stdout: Optional[IO[AnyStr]] = None,
    stderr: Optional[IO[AnyStr]] = None,
) -> subprocess.Process:
    return await subprocess.create_subprocess_shell(
        program,
        stdout=stdout or subprocess.PIPE,
        stderr=stderr or subprocess.PIPE,
    )


async def run_subprocess_exec(
    *args: str, **kwargs: Any
) -> Tuple[bytes, bytes]:
    log.debug(f"Executing subprocess: {args}")
    process = await create_subprocess_exec(*args, **kwargs)

    return await process.communicate()


async def run_subprocess_shell(
    program: str, **kwargs: Any
) -> Tuple[bytes, bytes]:
    log.debug(f"Executing subprocess: {program}")
    process = await create_subprocess_shell(program, **kwargs)

    return await process.communicate()
