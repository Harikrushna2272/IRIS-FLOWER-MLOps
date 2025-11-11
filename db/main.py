from dotenv import load_dotenv
from fastapi import FastAPI
from pydantic import BaseModel
from tortoise import fields
from tortoise.contrib.fastapi import register_tortoise
from tortoise.models import Model


class Prediction(Model):
    id = fields.IntField(primary_key=True, auto_increment=True)
    sepal_length = fields.FloatField(null=False)
    sepal_width = fields.FloatField(null=False)
    petal_length = fields.FloatField(null=False)
    petal_width = fields.FloatField(null=False)
    predicted_class = fields.CharField(max_length=50, null=False)


load_dotenv()
app = FastAPI()

register_tortoise(
    app,
    db_url="sqlite://data/db.sqlite3",
    modules={"models": ["main"]},
    generate_schemas=True,
    add_exception_handlers=True,
)


@app.get("/")
async def root():
    return {"message": "Hello from DB"}


@app.get("/health")
async def health():
    return {"status": "ok"}


class PredictionIn(BaseModel):
    sepal_length: float
    sepal_width: float
    petal_length: float
    petal_width: float
    predicted_class: str


@app.post("/prediction")
async def create_prediction(prediction: PredictionIn):
    return await Prediction.create(**prediction.dict())


# @app.delete("/prediction/{id}")
# async def delete_prediction(id: int):
#     prediction = await Prediction.filter(id=id).delete()
#     return prediction


# @app.get("/prediction/{id}")
# async def get_prediction(id: int):
#     prediction = await Prediction.get(id=id)
#     return prediction


@app.get("/prediction")
async def get_predictions():
    predictions = await Prediction.all()
    return predictions
