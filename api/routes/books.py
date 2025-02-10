from typing import OrderedDict

from fastapi import APIRouter, status
from fastapi.responses import JSONResponse

from api.db.schemas import Book, Genre, InMemoryDB

router = APIRouter()

db = InMemoryDB()

# Seed the database with initial data
db.add_book(Book(id=1, title="The Hobbit", author="J.R.R. Tolkien", publication_year=1937, genre=Genre.SCI_FI))
db.add_book(Book(id=2, title="The Lord of the Rings", author="J.R.R. Tolkien", publication_year=1954, genre=Genre.FANTASY))
db.add_book(Book(id=3, title="The Return of the King", author="J.R.R. Tolkien", publication_year=1955, genre=Genre.FANTASY))

@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_book(book: Book):
    if book.id < 0:
        return JSONResponse(
            status_code=400,
            content={"detail": "Invalid ID"}
        )
    db.add_book(book)
    return JSONResponse(
        status_code=status.HTTP_201_CREATED, content=book.model_dump()
    )

@router.get("/", response_model=OrderedDict[int, Book], status_code=status.HTTP_200_OK)
async def get_books() -> OrderedDict[int, Book]:
    return db.get_books()

@router.put("/{book_id}", response_model=Book, status_code=status.HTTP_200_OK)
async def update_book(book_id: int, book: Book) -> Book:
    # Validate book_id in the URL path
    if book_id < 0:
        return JSONResponse(
            status_code=400,
            content={"detail": "Invalid ID"}
        )

    # Ensure the ID in the request body matches the book_id in the URL path
    if book.id != book_id:
        return JSONResponse(
            status_code=400,
            content={"detail": "Invalid ID"}
        )

    # Check if the book exists
    existing_book = db.get_book(book_id)
    if not existing_book:
        return JSONResponse(
            status_code=404,
            content={"detail": "Book not found"}
        )

    # Update the book
    updated_book = db.update_book(book_id, book)
    return updated_book

@router.delete("/{book_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_book(book_id: int) -> None:
    if book_id < 0:
        return JSONResponse(
            status_code=400,
            content={"detail": "Invalid ID"}
        )
    existing_book = db.get_book(book_id)
    if not existing_book:
        return JSONResponse(
            status_code=404,
            content={"detail": "Book not found"}
        )
    db.delete_book(book_id)
    return None

@router.get("/{book_id}", response_model=Book)
async def get_book(book_id: int):
    if book_id < 0:
        return JSONResponse(
            status_code=400,
            content={"detail": "Invalid ID"}
        )
    book = db.get_book(book_id)
    if not book:
        return JSONResponse(
            status_code=404,
            content={"detail": "Book not found"}
        )
    return book