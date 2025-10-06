from __future__ import annotations

from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import OwnerProfile
from app.schemas import ProfileCreateRequest, ProfileResponse
from app.utils.auth import extract_owner_key

router = APIRouter(prefix="/v1", tags=["profile"])


@router.post("/profile", response_model=ProfileResponse, status_code=201)
def create_or_update_profile(
    payload: ProfileCreateRequest,
    request: Request,
    db: Session = Depends(get_db),
):
    owner_key = extract_owner_key(request)

    profile = (
        db.query(OwnerProfile)
        .filter(OwnerProfile.owner_key == owner_key)
        .one_or_none()
    )

    if profile is None:
        profile = OwnerProfile(owner_key=owner_key)
        db.add(profile)

    profile.display_name = payload.display_name
    profile.avatar_url = str(payload.avatar_url) if payload.avatar_url else None
    profile.mbti_source = payload.mbti_source
    profile.mbti_value = payload.mbti_value
    profile.show_public = payload.show_public

    db.commit()
    db.refresh(profile)

    return ProfileResponse(
        profile_id=profile.id,
        display_name=profile.display_name,
        avatar_url=profile.avatar_url,
        mbti_source=profile.mbti_source,
        mbti_value=profile.mbti_value,
        show_public=profile.show_public,
        created_at=profile.created_at,
        updated_at=profile.updated_at,
    )
