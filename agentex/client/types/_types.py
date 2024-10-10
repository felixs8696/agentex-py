from os import PathLike
from typing import Union, IO, Tuple, Optional, Mapping

Base64FileInput = Union[IO[bytes], PathLike]
FileContent = Union[IO[bytes], bytes, PathLike]  # PathLike is not subscriptable in Python 3.8.
FileTypes = Union[
    # file (or bytes)
    FileContent,
    # (filename, file (or bytes))
    Tuple[Optional[str], FileContent],
    # (filename, file (or bytes), content_type)
    Tuple[Optional[str], FileContent, Optional[str]],
    # (filename, file (or bytes), content_type, headers)
    Tuple[Optional[str], FileContent, Optional[str], Mapping[str, str]],
]
