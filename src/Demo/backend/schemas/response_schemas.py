from pydantic import BaseModel

from ..core.config import logger


class IdentifyResult(BaseModel):
    registered_id: str  # searched result id
    uid: str  # searched face uid
    name: str
    time: str
    score: float

    @classmethod
    def from_matched_result(cls, matched_result):
        logger.debug(f"matched_result:{matched_result}")
        return cls(
            registered_id=matched_result.registered_id,
            uid=matched_result.uid,
            name=matched_result.name,
            time=matched_result.time,
            score=matched_result.score,
        )
