from fastapi import FastAPI, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from . import models, schemas
from .database import get_db, engine
from datetime import datetime

models.Base.metadata.create_all(bind=engine)

app = FastAPI()


@app.post("/advertisement/", response_model=schemas.Advertisement)
def create_advertisement(
        advertisement: schemas.AdvertisementCreate,
        db: Session = Depends(get_db)
):
    db_ad = models.Advertisement(**advertisement.model_dump())
    db.add(db_ad)
    db.commit()
    db.refresh(db_ad)
    return db_ad


@app.patch("/advertisement/{advertisement_id}", response_model=schemas.Advertisement)
def update_advertisement(
        advertisement_id: int,
        advertisement: schemas.AdvertisementUpdate,
        db: Session = Depends(get_db)
):
    db_ad = db.query(models.Advertisement).filter(models.Advertisement.id == advertisement_id).first()
    if not db_ad:
        raise HTTPException(status_code=404, detail="Advertisement not found")

    update_data = advertisement.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_ad, field, value)

    db.commit()
    db.refresh(db_ad)
    return db_ad


@app.delete("/advertisement/{advertisement_id}")
def delete_advertisement(advertisement_id: int, db: Session = Depends(get_db)):
    db_ad = db.query(models.Advertisement).filter(models.Advertisement.id == advertisement_id).first()
    if not db_ad:
        raise HTTPException(status_code=404, detail="Advertisement not found")

    db.delete(db_ad)
    db.commit()
    return {"message": "Advertisement deleted successfully"}


@app.get("/advertisement/{advertisement_id}", response_model=schemas.Advertisement)
def get_advertisement(advertisement_id: int, db: Session = Depends(get_db)):
    db_ad = db.query(models.Advertisement).filter(models.Advertisement.id == advertisement_id).first()
    if not db_ad:
        raise HTTPException(status_code=404, detail="Advertisement not found")
    return db_ad


@app.get("/advertisement/", response_model=List[schemas.Advertisement])
def search_advertisements(
        title: Optional[str] = Query(None),
        description: Optional[str] = Query(None),
        price_min: Optional[int] = Query(None),
        price_max: Optional[int] = Query(None),
        author: Optional[str] = Query(None),
        created_before: Optional[datetime] = Query(None),
        created_after: Optional[datetime] = Query(None),
        db: Session = Depends(get_db)
):
    query = db.query(models.Advertisement)

    if title:
        query = query.filter(models.Advertisement.title.contains(title))
    if description:
        query = query.filter(models.Advertisement.description.contains(description))
    if price_min is not None:
        query = query.filter(models.Advertisement.price >= price_min)
    if price_max is not None:
        query = query.filter(models.Advertisement.price <= price_max)
    if author:
        query = query.filter(models.Advertisement.author.contains(author))
    if created_after:
        query = query.filter(models.Advertisement.created_at >= created_after)
    if created_before:
        query = query.filter(models.Advertisement.created_at <= created_before)

    return query.all()