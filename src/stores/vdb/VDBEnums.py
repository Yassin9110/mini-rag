from enum import Enum

class VDBEnums(Enum):
    QDRANT = "QDRANT"


class DistanceMethodEnums(Enum):
    COSINE = "cosine"
    DOT = "dot"