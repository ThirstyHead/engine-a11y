"""Source document immutability and provenance tracking."""
import hashlib
from pathlib import Path
from typing import Optional, Tuple, Union


def sha256_file(path: Union[str, Path]) -> str:
    p = Path(path)
    hasher = hashlib.sha256()
    with open(p, "rb") as f:
        while chunk := f.read(65536):
            hasher.update(chunk)
    return hasher.hexdigest()


calculate_sha256 = sha256_file


def assert_source_unchanged(source_path: Union[str, Path], expected_hash: str) -> None:
    current_hash = sha256_file(source_path)
    if current_hash != expected_hash:
        raise RuntimeError(
            f"Document immutability violation: Source document was mutated during processing! "
            f"Expected SHA-256: {expected_hash}, Current SHA-256: {current_hash}"
        )


def verify_immutability(path: Union[str, Path], expected_sha256: str) -> bool:
    assert_source_unchanged(path, expected_sha256)
    return True


def assert_not_same_path(src: Union[str, Path], dest: Union[str, Path]) -> None:
    src_p = Path(src).resolve()
    dest_p = Path(dest).resolve()
    if src_p == dest_p:
        raise ValueError(
            "Destination path cannot equal source path. Source documents strictly "
            "remain untouched and immutable."
        )


def verify_remediation_output(source_path: Union[str, Path], dest_path: Union[str, Path]) -> Tuple[str, str]:
    assert_not_same_path(source_path, dest_path)
    return sha256_file(source_path), sha256_file(dest_path)


def get_remediated_path(
    input_path: Union[str, Path],
    out_path: Optional[Union[str, Path]] = None,
    suffix_tag: str = "-remediated",
) -> Path:
    in_p = Path(input_path)
    if out_path:
        return Path(out_path)
    stem = in_p.stem
    suffix = in_p.suffix
    return in_p.with_name(f"{stem}{suffix_tag}{suffix}")
