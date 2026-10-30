from pydantic import BaseModel, ValidationError


def parse_input(model: type[BaseModel], **kwargs) -> BaseModel:
    try:
        return model.model_validate(kwargs)
    except ValidationError as exc:
        message = "; ".join(
            f"{'.'.join(str(part) for part in error['loc'])}: {error['msg']}"
            for error in exc.errors()
        )
        raise ValueError(message) from exc
