from dataclasses import dataclass
from typing import Tuple

@dataclass
class SchemaVersion:
    major: int
    minor: int
    patch: int

    @classmethod
    def from_string(cls, version_str: str) -> "SchemaVersion":
        """Create a SchemaVersion from a string like '1.0.0'"""
        major, minor, patch = map(int, version_str.split('.'))
        return cls(major=major, minor=minor, patch=patch)

    def to_tuple(self) -> Tuple[int, int, int]:
        """Convert version to tuple for comparison"""
        return (self.major, self.minor, self.patch)

    def __lt__(self, other: "SchemaVersion") -> bool:
        return self.to_tuple() < other.to_tuple()

    def __str__(self) -> str:
        return f"{self.major}.{self.minor}.{self.patch}" 