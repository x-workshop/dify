import logging
from typing import Any, Union

from botocore.exceptions import BotoCoreError  # type: ignore
from pydantic import BaseModel, Field

from core.tools.entities.tool_entities import ToolInvokeMessage
from core.tools.tool.builtin_tool import BuiltinTool
from io import BytesIO
from reportlab.pdfbase import pdfmetrics
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer
from reportlab.lib.units import inch
from reportlab.pdfbase.cidfonts import UnicodeCIDFont

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class GenPDFTool(BuiltinTool):
    def _invoke(
        self, user_id: str, tool_parameters: dict[str, Any]
    ) -> Union[ToolInvokeMessage, list[ToolInvokeMessage]]:
        """
        Invoke the ApplyGuardrail tool
        """
        try:
            # Parse parameters
            texts = tool_parameters.get("texts", [])

            # Create buffer
            buffer = BytesIO()

            # Register Chinese font
            pdfmetrics.registerFont(UnicodeCIDFont("STSong-Light"))

            # Create document
            doc = SimpleDocTemplate(
                buffer,  # Use buffer instead of file path
                pagesize=A4,
                rightMargin=72,
                leftMargin=72,
                topMargin=72,
                bottomMargin=72,
            )

            # Define styles
            title_style = ParagraphStyle(
                "CustomTitle",
                fontName="STSong-Light",
                fontSize=16,
                spaceAfter=30,
                leading=20,
            )

            body_style = ParagraphStyle(
                "CustomBody",
                fontName="STSong-Light",
                fontSize=12,
                leading=18,
                spaceAfter=12,
            )

            # Build content
            story = []
            for text in texts:
                # Split into paragraphs
                paragraphs = text.split("\n\n")

                for p in paragraphs:
                    # Check if paragraph is a title (starts with Chinese number)
                    if any(
                        p.startswith(num)
                        for num in ["一、", "二、", "三、", "四、", "五、", "六、"]
                    ):
                        story.append(Paragraph(p, title_style))
                    else:
                        story.append(Paragraph(p, body_style))

                    story.append(Spacer(1, 12))

            # Build PDF
            doc.build(story)

            # Get PDF content
            pdf_content = buffer.getvalue()
            buffer.close()

            return self.create_blob_message(pdf_content, {"name": "report.pdf"})

        except Exception as e:
            error_message = f"An unexpected error occurred: {str(e)}"
            logger.error(error_message, exc_info=True)
            return self.create_text_message(text=error_message)
