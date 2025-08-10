from dataclasses import dataclass, asdict

@dataclass
class MediaItem:
    title: str
    creator: str
    year: int
    rating: float
    poster_url: str = ''
    plot: str = ''

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> 'MediaItem':
        return cls(
            title=data.get('title', ''),
            creator=data.get('creator', ''),
            year=int(data.get('year', 0)),
            rating=float(data.get('rating', 0.0)),
            poster_url=data.get('poster_url', ''),
            plot=data.get('plot', '')
        )
