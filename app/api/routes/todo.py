from fastapi import APIRouter, HTTPException, Depends, status, Header
from sqlmodel import Session, select, func
from ...database import get_session
from ...models import Todo, TodoCreate, TodoUpdate, TodoPublic, TodosResponse
import math

router = APIRouter(prefix="/todo", tags=["todo"])

@router.get("/", response_model=TodosResponse)
def read_todos(
    session: Session = Depends(get_session), 
    page_index: int = 0,
    sort_by: str = None,
    sort_order: str = None,
    user_id: str = Header()
):
    """
    Get all todos with optional single-field sorting
    - sort_by: Field to sort by (e.g. "priority")
    - sort_order: Sort order ("asc" or "desc")
    """
    count_statement = select(func.count()).select_from(Todo).where(Todo.user_id == user_id)
    count = session.exec(count_statement).one()
    page_limit = 5
    skip = page_index * page_limit
    
    statement = select(Todo.id, Todo.task, Todo.deadline, Todo.priority, Todo.is_done).where(Todo.user_id == user_id)
    
    if sort_by:
        valid_fields = {"task", "deadline", "priority", "is_done"}
        
        # Validate field
        if sort_by not in valid_fields:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid sort field: {sort_by}. Valid fields: {', '.join(valid_fields)}"
            )
        
        # Validate sort order
        valid_orders = {"asc", "desc"}
        if sort_order not in valid_orders:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid sort order: {sort_order}. Valid orders: asc, desc"
            )
        
        sort_field = getattr(Todo, sort_by)
        if sort_order == "desc":
            statement = statement.order_by(sort_field.desc())
        elif sort_order == "asc":
            statement = statement.order_by(sort_field.asc())
    
    statement = statement.offset(skip).limit(page_limit)
    todos = session.exec(statement).all()
    
    return {
        "todos": todos,
        "todos_total": count,
        "todos_pages": math.ceil(count/page_limit)
    }

@router.get("/{todo_id}", response_model=TodoPublic)
def read_todo(
    todo_id: str,
    session: Session = Depends(get_session),
    user_id: str = Header()
):
    """
    Get a specific todo by ID
    """
    statement = select(Todo).where(Todo.id == todo_id, Todo.user_id == user_id)
    todo = session.exec(statement).first()
    if not todo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Todo not found"
        )
    return todo

@router.post("/", response_model=TodoPublic, status_code=status.HTTP_201_CREATED)
def create_todo(
    todo: TodoCreate,
    session: Session = Depends(get_session),
    user_id: str = Header()
):
    """
    Create a new todo
    """
    todo_data = todo.model_dump()
    todo_data["user_id"] = user_id
    db_todo = Todo.model_validate(todo_data)
    session.add(db_todo)
    session.commit()
    session.refresh(db_todo)
    return db_todo

@router.put("/{todo_id}", response_model=TodoPublic)
def update_todo(
    todo_id: str,
    todo: TodoUpdate,
    session: Session = Depends(get_session),
    user_id: str = Header()
):
    """
    Update a todo
    """
    statement = select(Todo).where(Todo.id == todo_id, Todo.user_id == user_id)
    db_todo = session.exec(statement).first()
    if not db_todo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Todo not found"
        )
    
    todo_data = todo.model_dump(exclude_unset=True)
    for field, value in todo_data.items():
        if hasattr(db_todo, field):
            # Get the actual validated value from the TodoUpdate instance
            validated_value = getattr(todo, field)
            setattr(db_todo, field, validated_value)
    session.add(db_todo)
    session.commit()
    session.refresh(db_todo)
    return db_todo

@router.delete("/{todo_id}")
def delete_todo(
    todo_id: str,
    session: Session = Depends(get_session),
    user_id: str = Header()
):
    """
    Delete a todo
    """
    statement = select(Todo).where(Todo.id == todo_id, Todo.user_id == user_id)
    todo = session.exec(statement).first()
    if not todo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Todo not found"
        )
    
    session.delete(todo)
    session.commit()
    return {"message": "Todo deleted successfully"}
