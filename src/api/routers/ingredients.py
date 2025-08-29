from src.infrastructure.db import db_dependency
from fastapi import APIRouter
from starlette import status
from typing import Annotated

router = APIRouter()