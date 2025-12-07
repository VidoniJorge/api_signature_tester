from api_signature_tester.config import API_CONFIG_CONTENT_TYPE, Settings, get_logger
from api_signature_tester.pipeline.sync_process import ApiSignatureTesterSynchBase
from api_signature_tester.validator.pipeline_api_validaror import PipelineApiValidaror
from api_signature_tester.validator.pipeline_json_api import (
    PipelineFullJsonApiValidator,
    PipelineJsonApiParcialValidator,
)


def run():
    settings = Settings()

    p = definePipelineValidator(
        content_type=None, path_to_validate=None, settings=settings
    )
    ApiSignatureTesterSynchBase(p, get_logger(), settings).execute()


def definePipelineValidator(
    settings: Settings, content_type: str, path_to_validate: str | None
) -> PipelineApiValidaror:
    content_type = (
        content_type
        if content_type is not None
        else settings.get_properties(API_CONFIG_CONTENT_TYPE)
    )

    if content_type == "application/json":
        if path_to_validate is not None:
            return PipelineJsonApiParcialValidator(path_to_validate)

        if path_to_validate is None:
            # Implementar y retornar un validador para HTML cuando esté disponible
            return PipelineFullJsonApiValidator()

    raise ValueError(
        "No se pudo definir un validador adecuado para los parámetros proporcionados."
    )


if __name__ == "__main__":
    run()
