from fastapi import Depends
from typing import Annotated
from .services import ZatcaPhase1Service

def get_zatca_phase1_service() -> ZatcaPhase1Service:
    return ZatcaPhase1Service()