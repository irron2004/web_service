from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

@router.get("/", response_class=HTMLResponse)
async def arcade_home(request: Request):
    """아케이드 게임 홈페이지"""
    return templates.TemplateResponse("arcade/index.html", {"request": request})

@router.get("/snake", response_class=HTMLResponse)
async def snake_game(request: Request):
    """스네이크 게임"""
    return templates.TemplateResponse("arcade/snake.html", {"request": request})

@router.get("/tetris", response_class=HTMLResponse)
async def tetris_game(request: Request):
    """테트리스 게임"""
    return templates.TemplateResponse("arcade/tetris.html", {"request": request})

@router.get("/puzzle", response_class=HTMLResponse)
async def puzzle_game(request: Request):
    """퍼즐 게임"""
    return templates.TemplateResponse("arcade/puzzle.html", {"request": request}) 