from pydantic import BaseModel


class GenerateVideoDTO(BaseModel):
    generation_id: str
    prompt: str
    model: str
    duration: int
    aspect_ratio: str


class UploadToS3DTO(BaseModel):
    generation_id: str
    source_url: str
    user_id: str


class SaveResultDTO(BaseModel):
    generation_id: str
    s3_url: str
    status: str


class DeductTokensDTO(BaseModel):
    amount: int
    user_id: str
    generation_id: str
    

class VideoGenerationWorkflowDTO(BaseModel):
    user_id: str
    generation_id: str
    prompt: str
    model: str
    duration: int
    aspect_ratio: str
    token_cost: int