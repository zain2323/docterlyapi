from api import ma

class TokenSchema(ma.SQLAlchemyAutoSchema):
    """Schema defining the attributes of token"""
    class Meta:
        description = 'This schema represents a token.'
    token = ma.String(required=True)