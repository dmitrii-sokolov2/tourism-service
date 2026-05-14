from pydantic import BaseModel, Field, model_validator, ConfigDict
from typing import Optional
from datetime import datetime

class PromoCreateSchema(BaseModel):
    code: str

    discount_percent: Optional[int] = Field(default=None, ge=1, le=100)
    discount_amount: Optional[int] = Field(default=None, ge=0)

    usage_limit: Optional[int] = Field(default=None, ge=1)

    expires_at: Optional[datetime] = None

    min_price: Optional[int] = Field(default=None, ge=0)

    @model_validator(mode='after')
    def validate_discount(self):
        if (
            self.discount_percent is None
            and self.discount_amount is None
        ):
            raise ValueError(
                'Either `discount_percent` or `discount_amount` must be provided'
            )

        return self

class PromoUpdateSchema(BaseModel):
    code: Optional[str] = None

    discount_percent: Optional[int] = Field(default=None, ge=1, le=100)
    discount_amount: Optional[int] = Field(default=None, ge=0)

    usage_limit: Optional[int] = Field(default=None, ge=1)

    expires_at: Optional[datetime] = None

    min_price: Optional[int] = Field(default=None, ge=0)

    @model_validator(mode='after')
    def validate_discount(self):
        if (
            self.discount_percent is not None
            and self.discount_amount is not None
        ):
            raise ValueError(
                'Use either discount_percent or discount_amount'
            )

        return self

class PromoResponseSchema(BaseModel):
    id: int
    code: str

    discount_percent: int | None
    discount_amount: int | None

    usage_limit: int | None

    expires_at: datetime | None

    min_price: int | None

    model_config = ConfigDict(from_attributes=True)