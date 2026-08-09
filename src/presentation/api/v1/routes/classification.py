from fastapi import APIRouter, HTTPException, Request

from presentation.api.v1.schemas.classification import CategorizeRequest, CategorizeResponse
from shared.utils import logger

router = APIRouter(tags=["classification"])


@router.post("/categorize", response_model=CategorizeResponse)
def categorize(payload: CategorizeRequest, request: Request) -> CategorizeResponse:
    service = request.app.state.categorization_service
    if service is None:
        raise HTTPException(status_code=503, detail="Categorization service not ready")

    try:
        result = service.categorize(payload.text)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Categorization failed for text={payload.text!r}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to categorize text")

    return CategorizeResponse(**result.to_dict())
