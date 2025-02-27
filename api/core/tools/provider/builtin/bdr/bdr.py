from core.tools.errors import ToolProviderCredentialValidationError
from core.tools.provider.builtin.bdr.tools.gen_pdf import GenPDFTool
from core.tools.provider.builtin_tool_provider import BuiltinToolProviderController


class BDRProvider(BuiltinToolProviderController):
    def _validate_credentials(self, credentials: dict) -> None:
        try:
            GenPDFTool().fork_tool_runtime(
                runtime={
                    "credentials": credentials,
                }
            ).invoke(
                user_id="",
                tool_parameters={
                    "texts": ["hello", "world"]
                },
            )
        except Exception as e:
            raise ToolProviderCredentialValidationError(str(e))
