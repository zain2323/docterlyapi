from api import ma

class TokenSchema(ma.SQLAlchemyAutoSchema):
    """Schema defining the attributes of token"""
    token = ma.String(required=True)