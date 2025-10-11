import os
import json
import tempfile
import zipfile
import shutil
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, HttpResponseBadRequest, JsonResponse
from PyPDF2 import PdfReader, PdfWriter
from io import BytesIO


def encrypt_pdf_with_password(pdf_content, password):
    """
    Encrypt PDF content with password protection using PyPDF2
    """
    try:
        # Create a BytesIO object for the input PDF
        input_buffer = BytesIO(pdf_content)

        # Read the PDF
        try:
            reader = PdfReader(input_buffer)
        except Exception as e:
            print(f"Error reading PDF: {e}")
            return pdf_content

        writer = PdfWriter()

        # Add all pages to the writer
        for page in reader.pages:
            writer.add_page(page)

        # Encrypt the PDF with the password
        writer.encrypt(password)

        # Write to output buffer
        output_buffer = BytesIO()
        writer.write(output_buffer)
        output_buffer.seek(0)

        return output_buffer.getvalue()

    except Exception as e:
        print(f"PDF encryption failed: {e}")
        # Return original content if encryption fails
        return pdf_content