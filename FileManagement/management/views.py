from django.contrib.auth import login
from django.core.files.storage import default_storage
from django.core.paginator import Paginator
from django.http import HttpResponse
from .helperfunction import *
from .utility import *
from django.shortcuts import render, redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import CreateView, UpdateView, ListView, DetailView
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from .models import RevenueSite, MasterWard
from .forms import RevenueSiteForm, CustomUserCreationForm, MasterWardForm
from django.contrib import messages
from django.shortcuts import get_object_or_404
from django.http import HttpResponse
import shutil
import zipfile
import os
import io
import json
import tempfile
import hashlib
from datetime import datetime
from django.http import JsonResponse
from django.conf import settings
from PyPDF2 import PdfReader, PdfMerger
from pdf2docx import Converter
from PIL import Image
from django.utils.translation import gettext as _
from django.http import FileResponse, HttpResponseBadRequest
from PyPDF2 import PdfWriter
from django.shortcuts import render
from django.db.models import Count, Q
from .models import RevenueSite, CustomUser
from datetime import datetime, timedelta
import json
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from .models import MasterDrawer, Compartment
from .forms import MasterDrawerForm, CompartmentForm
from django.contrib import messages

def home(request):
    return render(request, 'index.html')

def dashboard(request):
    # Get all sites
    sites = RevenueSite.objects.all()

    # Search functionality
    query = request.GET.get('q')
    if query:
        sites = sites.filter(
            Q(nagar_bhumapan_kramank__icontains=query) |
            Q(plot_no__icontains=query) |
            Q(full_name__icontains=query) |
            Q(district__icontains=query) |
            Q(taluka__icontains=query) |
            Q(village__icontains=query)
        )

    # Filter by division
    division = request.GET.get('division')
    if division:
        sites = sites.filter(division=division)

    # Filter by district
    district = request.GET.get('district')
    if district:
        sites = sites.filter(district__icontains=district)

    # Filter by taluka
    taluka = request.GET.get('taluka')
    if taluka:
        sites = sites.filter(taluka__icontains=taluka)

    # Filter by village
    village = request.GET.get('village')
    if village:
        sites = sites.filter(village__icontains=village)

    # Date range filter
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')
    if date_from and date_to:
        try:
            date_from = datetime.strptime(date_from, '%Y-%m-%d')
            date_to = datetime.strptime(date_to, '%Y-%m-%d')
            sites = sites.filter(registration_date__range=[date_from, date_to])
        except ValueError:
            pass

    # Get counts for summary cards
    total_sites = RevenueSite.objects.count()
    sites_with_documents = RevenueSite.objects.exclude(document_file='').count()
    sites_without_documents = total_sites - sites_with_documents
    recent_sites = RevenueSite.objects.filter(
        registration_date__gte=datetime.now() - timedelta(days=7)
    ).count()

    # Get recent sites for the table
    recent_sites_list = RevenueSite.objects.order_by('-registration_date')[:10]

    # Prepare data for division chart
    division_data = RevenueSite.objects.values('division').annotate(
        count=Count('id')
    ).order_by('division')

    division_labels = []
    division_counts = []
    for choice in CustomUser.DIVISION_CHOICES:
        count = next((item['count'] for item in division_data if item['division'] == choice[0]), 0)
        division_labels.append(choice[1])
        division_counts.append(count)

    context = {
        'total_sites': total_sites,
        'sites_with_documents': sites_with_documents,
        'sites_without_documents': sites_without_documents,
        'recent_sites': recent_sites,
        'recent_sites_list': recent_sites_list,
        'division_choices': CustomUser.DIVISION_CHOICES,
        'division_labels': json.dumps(division_labels),
        'division_data': json.dumps(division_counts),
    }

    return render(request, 'dashboard.html', context)


def masterward_list(request):
    wards = MasterWard.objects.all()
    return render(request, 'MasterWard/masterward_list.html', {'wards': wards})

def masterward_create(request):
    if request.method == 'POST':
        form = MasterWardForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Ward was created successfully!")
            return redirect('search_ward')
        else:
            # Add this temporarily to see validation errors in console
            print("Form errors:", form.errors)
            print("Form data:", request.POST)
    else:
        form = MasterWardForm()
    return render(request, 'MasterWard/masterward_create.html', {'form': form})

def masterward_update(request, pk):
    ward = get_object_or_404(MasterWard, pk=pk)
    if request.method == 'POST':
        form = MasterWardForm(request.POST, instance=ward)
        if form.is_valid():
            form.save()
            messages.success(request, "Ward was updated successfully!")
            return redirect('search_ward')
    else:
        form = MasterWardForm(instance=ward)
    return render(request, 'MasterWard/masterward_update.html', {'form': form, 'object': ward})

def masterward_delete(request, pk):
    if request.method == 'POST':
        ward = get_object_or_404(MasterWard, pk=pk)
        ward.delete()
        messages.success(request, "Ward was deleted successfully!")
    return redirect('search_ward')


# Master Drawer Views
def masterdrawer_list(request):
    drawers = MasterDrawer.objects.all().order_by('drawer_number')
    return render(request, 'MasterDrawer/masterdrawer_list.html', {'drawers': drawers})

def masterdrawer_create(request):
    if request.method == 'POST':
        form = MasterDrawerForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Drawer was created successfully!")
            return redirect('search_drawers')
    else:
        form = MasterDrawerForm()
    return render(request, 'MasterDrawer/masterdrawer_create.html', {'form': form})

def masterdrawer_update(request, pk):
    drawer = get_object_or_404(MasterDrawer, pk=pk)
    if request.method == 'POST':
        form = MasterDrawerForm(request.POST, instance=drawer)
        if form.is_valid():
            form.save()
            messages.success(request, "Drawer was updated successfully!")
            return redirect('search_drawers')
    else:
        form = MasterDrawerForm(instance=drawer)
    return render(request, 'MasterDrawer/masterdrawer_update.html', {'form': form, 'object': drawer})

def masterdrawer_delete(request, pk):
    if request.method == 'POST':
        drawer = get_object_or_404(MasterDrawer, pk=pk)
        drawer.delete()
        messages.success(request, "Drawer was deleted successfully!")
    return redirect('search_drawers')

# Compartment Views
def compartment_list(request):
    compartments = Compartment.objects.all().order_by('drawer', 'compartment_number')
    return render(request, 'Compartment/compartment_list.html', {'compartments': compartments})

def compartment_create(request):
    drawers = MasterDrawer.objects.all()
    if request.method == 'POST':
        form = CompartmentForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Compartment was created successfully!")
            return redirect('search_compartments')
    else:
        form = CompartmentForm()
    return render(request, 'Compartment/compartment_create.html', {'form': form, 'drawers': drawers})

def compartment_update(request, pk):
    compartment = get_object_or_404(Compartment, pk=pk)
    drawers = MasterDrawer.objects.all()
    if request.method == 'POST':
        form = CompartmentForm(request.POST, instance=compartment)
        if form.is_valid():
            form.save()
            messages.success(request, "Compartment was updated successfully!")
            return redirect('search_compartments')
    else:
        form = CompartmentForm(instance=compartment)
    return render(request, 'Compartment/compartment_update.html', {
        'form': form,
        'object': compartment,
        'drawers': drawers
    })

def compartment_delete(request, pk):
    if request.method == 'POST':
        compartment = get_object_or_404(Compartment, pk=pk)
        compartment.delete()
        messages.success(request, "Compartment was deleted successfully!")
    return redirect('search_compartments')


def merge_files_view(request):
    if request.method == 'GET':
        return render(request, 'merge_files.html')

    if request.method == 'POST':
        uploaded_files = request.FILES.getlist('files')
        if not uploaded_files:
            return HttpResponse("No files uploaded", status=400)

        merger = PdfMerger()
        temp_files = []

        try:
            for uploaded_file in uploaded_files:
                # Save the uploaded file temporarily
                temp_path = os.path.join(settings.MEDIA_ROOT, 'temp', uploaded_file.name)
                os.makedirs(os.path.dirname(temp_path), exist_ok=True)
                with open(temp_path, 'wb+') as destination:
                    for chunk in uploaded_file.chunks():
                        destination.write(chunk)

                ext = os.path.splitext(uploaded_file.name)[1].lower()

                if ext == '.docx':
                    pdf_buffer = convert_docx_to_pdf(temp_path)
                elif ext == '.txt':
                    pdf_buffer = convert_txt_to_pdf(temp_path)
                elif ext in ['.jpg', '.jpeg', '.png']:
                    pdf_buffer = convert_image_to_pdf(temp_path)
                elif ext in ['.html', '.htm']:
                    pdf_buffer = convert_html_to_pdf(temp_path)
                elif ext == '.pdf':
                    with open(temp_path, 'rb') as f:
                        pdf_buffer = BytesIO(f.read())
                else:
                    continue

                pdf_buffer.seek(0)
                merger.append(pdf_buffer)
                pdf_buffer.close()
                temp_files.append(temp_path)

            output = BytesIO()
            merger.write(output)
            merger.close()

            # Clean up temp files
            for temp_file in temp_files:
                if os.path.exists(temp_file):
                    os.remove(temp_file)

            output.seek(0)
            return FileResponse(output, as_attachment=True, filename="merged_output.pdf")

        except Exception as e:
            # Clean up any remaining temp files
            for temp_file in temp_files:
                if os.path.exists(temp_file):
                    os.remove(temp_file)
            return HttpResponse(f"Error merging files: {str(e)}", status=500)


class RevenueSiteCreateView(LoginRequiredMixin, CreateView):
    model = RevenueSite
    form_class = RevenueSiteForm
    template_name = 'revenue_sites/create.html'
    success_url = reverse_lazy('list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Calculate the next file number
        try:
            total_sites_count = RevenueSite.objects.count() + 1
            next_file_no = f"{total_sites_count:04d}"
        except Exception as e:
            # Fallback in case of error
            next_file_no = "0101"

        context['next_file_no'] = next_file_no
        return context

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        print("Form is valid, saving data...")  # Debug
        form.instance.created_by = self.request.user

        # Generate password if it doesn't exist
        if not form.instance.pdf_password:
            form.instance.pdf_password = RevenueSite.generate_pdf_password(form.instance)
            print(f"Generated PDF password: {form.instance.pdf_password}")

        # Handle merged document if exists
        merged_path = self.request.POST.get('merged_document_path')
        print(f"Merged path from POST: {merged_path}")  # Debug

        if merged_path and os.path.exists(merged_path):
            print(f"Merged document found at: {merged_path}")  # Debug
            try:
                # Create user-specific folder
                user_folder = os.path.join(
                    'documents/revenue_sites',
                    form.cleaned_data['full_name'].replace(' ', '_')
                )
                os.makedirs(os.path.join(settings.MEDIA_ROOT, user_folder), exist_ok=True)

                # Generate final filename
                final_filename = f"{form.cleaned_data['document_title'] or 'document'}.pdf"
                final_path = os.path.join(user_folder, final_filename)
                final_full_path = os.path.join(settings.MEDIA_ROOT, final_path)

                # ENCRYPT THE MAIN PDF BEFORE SAVING (FOR QR CODE ACCESS)
                if form.instance.pdf_password:
                    try:
                        # Read the original PDF
                        with open(merged_path, 'rb') as original_file:
                            original_content = original_file.read()

                        # Encrypt the PDF
                        encrypted_content = encrypt_pdf_with_password(original_content, form.instance.pdf_password)

                        # Save the encrypted version
                        with open(final_full_path, 'wb') as encrypted_file:
                            encrypted_file.write(encrypted_content)

                        print(f"Main PDF encrypted with password: {form.instance.pdf_password}")

                    except Exception as e:
                        print(f"Failed to encrypt main PDF: {e}")
                        # Fallback: move the original file without encryption
                        shutil.move(merged_path, final_full_path)
                else:
                    # Move without encryption if no password
                    shutil.move(merged_path, final_full_path)

                # Move the metadata file if it exists
                meta_path = merged_path + '.meta.json'
                if os.path.exists(meta_path):
                    final_meta_path = os.path.join(settings.MEDIA_ROOT, final_path + '.meta.json')
                    shutil.move(meta_path, final_meta_path)

                # Save to model - use relative path for MEDIA_ROOT
                form.instance.document_file.name = final_path
                print(f"Document saved as: {final_path}")  # Debug

            except Exception as e:
                print(f"Error moving document: {str(e)}")  # Debug
                messages.warning(self.request, f'Document could not be saved: {str(e)}')
                # Clean up any temporary files
                if os.path.exists(merged_path):
                    os.remove(merged_path)
                if os.path.exists(merged_path + '.meta.json'):
                    os.remove(merged_path + '.meta.json')
        else:
            print("No merged document found or path doesn't exist")  # Debug

        # Save the form instance
        try:
            response = super().form_valid(form)
            print("Form saved successfully, redirecting...")  # Debug
            messages.success(self.request, _('Revenue site created successfully!'))
            return response
        except Exception as e:
            print(f"Error saving form: {str(e)}")  # Debug
            messages.error(self.request, f'Error saving data: {str(e)}')
            return self.form_invalid(form)

    def form_invalid(self, form):
        print("Form is invalid")  # Debug
        print("Form errors:", form.errors)  # Debug
        # Clean up any uploaded files if form is invalid
        merged_path = self.request.POST.get('merged_document_path')
        if merged_path and os.path.exists(merged_path):
            try:
                os.remove(merged_path)
                meta_path = merged_path + '.meta.json'
                if os.path.exists(meta_path):
                    os.remove(meta_path)
            except:
                pass
        return super().form_invalid(form)


def merge_documents(request):
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Invalid request method'}, status=400)

    if not request.FILES.getlist('files'):
        return JsonResponse({'success': False, 'error': 'No files uploaded'}, status=400)

    try:
        # Setup temporary workspace
        full_name = request.POST.get('full_name', 'unknown').replace(' ', '_')
        document_title = request.POST.get('document_title', 'merged_document')
        temp_dir = tempfile.mkdtemp()
        output_filename = f"{full_name}_{document_title}_merged.pdf"
        output_path = os.path.join(temp_dir, output_filename)

        merger = PdfMerger()
        file_meta = {
            "document_info": {
                "title": document_title,
                "full_name": full_name,
                "merge_date": datetime.now().isoformat(),
                "merged_by": request.user.username if request.user.is_authenticated else "anonymous"
            },
            "files": []
        }

        filenames = request.POST.getlist('filenames', [])

        for i, file in enumerate(request.FILES.getlist('files')):
            try:
                original_name = file.name
                custom_name = filenames[i] if i < len(filenames) else original_name
                ext = os.path.splitext(original_name)[1].lower()
                temp_file_path = os.path.join(temp_dir, f"temp_{i}{ext}")

                # Save the uploaded file temporarily
                with open(temp_file_path, 'wb+') as destination:
                    for chunk in file.chunks():
                        destination.write(chunk)

                # Convert to PDF if needed
                temp_pdf_path = os.path.join(temp_dir, f"converted_{i}.pdf")
                page_count = 0

                if ext == '.pdf':
                    # Validate PDF
                    with open(temp_file_path, 'rb') as f:
                        pdf_reader = PdfReader(f)
                        page_count = len(pdf_reader.pages)
                        merger.append(temp_file_path)

                elif ext in ['.jpg', '.jpeg', '.png', '.bmp', '.gif', '.tiff', '.tif']:
                    # Convert image to PDF using img2pdf
                    try:
                        import img2pdf
                        with open(temp_pdf_path, "wb") as f:
                            f.write(img2pdf.convert(temp_file_path))
                    except ImportError:
                        # Fallback to PIL if img2pdf not available
                        from PIL import Image
                        with Image.open(temp_file_path) as img:
                            if img.mode != 'RGB':
                                img = img.convert('RGB')
                            img.save(temp_pdf_path, "PDF", resolution=100.0)

                    with open(temp_pdf_path, 'rb') as f:
                        pdf_reader = PdfReader(f)
                        page_count = len(pdf_reader.pages)
                        merger.append(temp_pdf_path)

                elif ext in ['.docx', '.doc']:
                    # Convert DOCX to PDF
                    try:
                        cv = Converter(temp_file_path)
                        cv.convert(temp_pdf_path)
                        cv.close()
                    except Exception as e:
                        # Fallback: create a simple PDF with file info
                        from reportlab.pdfgen import canvas
                        from reportlab.lib.pagesizes import letter

                        c = canvas.Canvas(temp_pdf_path, pagesize=letter)
                        c.drawString(100, 750, f"File: {custom_name}")
                        c.drawString(100, 730, f"Original: {original_name}")
                        c.drawString(100, 710, f"Type: {ext}")
                        c.drawString(100, 690, "Could not convert document properly")
                        c.save()

                    with open(temp_pdf_path, 'rb') as f:
                        pdf_reader = PdfReader(f)
                        page_count = len(pdf_reader.pages)
                        merger.append(temp_pdf_path)

                else:
                    # Create a PDF with file info for unsupported types
                    from reportlab.pdfgen import canvas
                    from reportlab.lib.pagesizes import letter

                    c = canvas.Canvas(temp_pdf_path, pagesize=letter)
                    c.drawString(100, 750, f"File: {custom_name}")
                    c.drawString(100, 730, f"Original: {original_name}")
                    c.drawString(100, 710, f"Type: {ext}")
                    c.drawString(100, 690, "This file type cannot be converted to PDF")
                    c.save()

                    with open(temp_pdf_path, 'rb') as f:
                        pdf_reader = PdfReader(f)
                        page_count = len(pdf_reader.pages)
                        merger.append(temp_pdf_path)

                # Calculate file hash
                with open(temp_file_path, 'rb') as f:
                    file_hash = hashlib.md5(f.read()).hexdigest()

                # Record metadata
                file_meta['files'].append({
                    "original_name": original_name,
                    "custom_name": custom_name,
                    "type": ext,
                    "pages": page_count,
                    "hash": file_hash,
                    "offset": len(merger.pages) - page_count,  # Starting page
                    "length": page_count  # Pages contributed
                })

            except Exception as e:
                # Clean up temporary files
                for f in [temp_file_path, temp_pdf_path]:
                    if os.path.exists(f):
                        os.remove(f)
                raise e

        # Write merged PDF
        merger.write(output_path)
        merger.close()

        # Write metadata JSON
        meta_path = output_path + '.meta.json'
        with open(meta_path, 'w') as f:
            json.dump(file_meta, f, indent=2)

        return JsonResponse({
            'success': True,
            'merged_path': output_path,
            'meta_path': meta_path,
            'output_filename': output_filename,
            'message': 'Documents merged successfully'
        })

    except Exception as e:
        # Clean up temp directory
        if 'temp_dir' in locals() and os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)
        return JsonResponse({
            'success': False,
            'error': str(e),
            'detailed_error': f"Failed to process documents: {str(e)}"
        }, status=500)


def protected_pdf_view(request, pk):
    """
    View that serves password-protected PDFs with optional password verification
    """
    revenue_site = get_object_or_404(RevenueSite, pk=pk)

    if not revenue_site.document_file:
        return HttpResponseBadRequest("No document exists for this site")

    # Check if password is provided in URL or session
    provided_password = request.GET.get('password') or request.session.get(f'pdf_password_{pk}')

    if not provided_password:
        # Show password entry form
        if request.method == 'POST':
            entered_password = request.POST.get('password')
            if entered_password == revenue_site.pdf_password:
                # Store password in session for future requests
                request.session[f'pdf_password_{pk}'] = entered_password
                # Redirect to same URL with password in GET parameter
                return redirect(f'{request.path}?password={entered_password}')
            else:
                messages.error(request, 'Invalid password. Please try again.')

        # Render password entry form
        return render(request, 'revenue_sites/pdf_password.html', {
            'site': revenue_site,
            'redirect_url': request.get_full_path()
        })

    # Verify password
    if provided_password != revenue_site.pdf_password:
        messages.error(request, 'Invalid password. Please try again.')
        # Clear invalid password from session
        if f'pdf_password_{pk}' in request.session:
            del request.session[f'pdf_password_{pk}']
        return redirect('protected_pdf', pk=pk)

    # Serve the PDF file
    try:
        doc_path = revenue_site.document_file.path

        # Check if file exists
        if not os.path.exists(doc_path):
            return HttpResponseBadRequest("PDF file not found")

        # Read and serve the file
        with open(doc_path, 'rb') as f:
            response = HttpResponse(f.read(), content_type='application/pdf')
            response['Content-Disposition'] = f'inline; filename="{revenue_site.full_name}.pdf"'
            return response

    except Exception as e:
        return HttpResponseBadRequest(f"Error serving PDF: {str(e)}")

def unmerge_document(request, pk):
    revenue_site = get_object_or_404(RevenueSite, pk=pk)

    if not revenue_site.document_file:
        return HttpResponseBadRequest("No merged document exists for this site")

    # Find the metadata file
    doc_path = revenue_site.document_file.path
    meta_path = doc_path + '.meta.json'

    if not os.path.exists(meta_path):
        return HttpResponseBadRequest("Metadata file not found - cannot unmerge")

    try:
        # Load metadata
        with open(meta_path, 'r') as f:
            meta = json.load(f)

        # Create a temporary directory for unmerged files
        temp_dir = tempfile.mkdtemp()
        zip_filename = os.path.join(temp_dir, f"unmerged_{revenue_site.full_name}.zip")

        with zipfile.ZipFile(zip_filename, 'w') as zipf:
            # Read the merged PDF (which is now encrypted)
            with open(doc_path, 'rb') as f:
                # Create a BytesIO object for PDF reading
                pdf_content = f.read()

                # If PDF is encrypted, we need to decrypt it first
                try:
                    pdf_reader = PdfReader(BytesIO(pdf_content))

                    # Check if PDF is encrypted and decrypt if needed
                    if pdf_reader.is_encrypted:
                        if revenue_site.pdf_password:
                            try:
                                # Try to decrypt with the stored password
                                if pdf_reader.decrypt(revenue_site.pdf_password) == 0:
                                    raise Exception("Decryption failed - wrong password")
                                print("Successfully decrypted main PDF for unmerge")
                            except Exception as decrypt_error:
                                print(f"Failed to decrypt PDF: {decrypt_error}")
                                return HttpResponseBadRequest("Failed to decrypt PDF. Password mismatch.")
                        else:
                            return HttpResponseBadRequest("PDF is encrypted but no password available.")

                    # Extract each original file
                    for file_info in meta['files']:
                        output_pdf = os.path.join(temp_dir, file_info['custom_name'] + '.pdf')

                        # Create PDF writer for this file
                        pdf_writer = PdfWriter()

                        # Add the appropriate pages
                        start_page = file_info['offset']
                        end_page = start_page + file_info['length']
                        for page_num in range(start_page, end_page):
                            if page_num < len(pdf_reader.pages):
                                pdf_writer.add_page(pdf_reader.pages[page_num])

                        # Write the unencrypted PDF to temporary file
                        with open(output_pdf, 'wb') as out_f:
                            pdf_writer.write(out_f)

                        # NOW ENCRYPT THE INDIVIDUAL PDF WITH PASSWORD
                        if revenue_site.pdf_password:
                            try:
                                # Read the unencrypted PDF content
                                with open(output_pdf, 'rb') as pdf_file:
                                    unencrypted_content = pdf_file.read()

                                # Encrypt the PDF
                                encrypted_content = encrypt_pdf_with_password(unencrypted_content,
                                                                              revenue_site.pdf_password)

                                # Write the encrypted content back to the file
                                with open(output_pdf, 'wb') as encrypted_file:
                                    encrypted_file.write(encrypted_content)

                                print(f"PDF encrypted with password: {revenue_site.pdf_password}")

                            except Exception as e:
                                print(f"Failed to encrypt PDF: {e}")
                                # Continue with unencrypted version

                        # Add the PDF to zip
                        zipf.write(output_pdf, arcname=f"{file_info['custom_name']}.pdf")

                except Exception as pdf_error:
                    print(f"Error processing PDF: {pdf_error}")
                    return HttpResponseBadRequest(f"Error processing PDF file: {str(pdf_error)}")

        # Read the zip file into memory
        with open(zip_filename, 'rb') as f:
            zip_content = f.read()

        # Clean up temporary files immediately
        shutil.rmtree(temp_dir)

        # Create response
        response = HttpResponse(zip_content, content_type='application/zip')
        response['Content-Disposition'] = f'attachment; filename=unmerged_{revenue_site.full_name}.zip'

        if revenue_site.pdf_password:
            response['X-Password'] = revenue_site.pdf_password

        return response

    except Exception as e:
        if 'temp_dir' in locals() and os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)
        return HttpResponseBadRequest(f"Error unmerging document: {str(e)}")


def unmerge_options(request, pk):
    revenue_site = get_object_or_404(RevenueSite, pk=pk)

    if not revenue_site.document_file:
        return HttpResponseBadRequest("No merged document exists for this site")

    # Find the metadata file
    doc_path = revenue_site.document_file.path
    meta_path = doc_path + '.meta.json'

    if not os.path.exists(meta_path):
        return HttpResponseBadRequest("Metadata file not found - cannot unmerge")

    # Load metadata
    with open(meta_path, 'r') as f:
        meta = json.load(f)

    context = {
        'site': revenue_site,
        'documents': meta.get('files', []),
    }
    return render(request, 'revenue_sites/unmerge_options.html', context)


def unmerge_selected(request, pk):
    if request.method != 'POST':
        return HttpResponseBadRequest("Invalid request method")

    selected_files = request.POST.getlist('selected_files')
    if not selected_files:
        return HttpResponseBadRequest("No files selected for unmerge")

    revenue_site = get_object_or_404(RevenueSite, pk=pk)

    if not revenue_site.document_file:
        return HttpResponseBadRequest("No merged document exists for this site")

    # Find the metadata file
    doc_path = revenue_site.document_file.path
    meta_path = doc_path + '.meta.json'

    if not os.path.exists(meta_path):
        return HttpResponseBadRequest("Metadata file not found - cannot unmerge")

    try:
        # Load metadata
        with open(meta_path, 'r') as f:
            meta = json.load(f)

        # Create a temporary directory for unmerged files
        temp_dir = tempfile.mkdtemp()
        zip_filename = os.path.join(temp_dir, f"selected_files_{revenue_site.full_name}.zip")

        with zipfile.ZipFile(zip_filename, 'w') as zipf:
            # Read the merged PDF (which should be unencrypted)
            try:
                with open(doc_path, 'rb') as f:
                    pdf_reader = PdfReader(f)

                    # Check if PDF is encrypted and try to decrypt if needed
                    if pdf_reader.is_encrypted and revenue_site.pdf_password:
                        try:
                            pdf_reader.decrypt(revenue_site.pdf_password)
                            print("Successfully decrypted main PDF for selective unmerge")
                        except Exception as decrypt_error:
                            print(f"Failed to decrypt PDF: {decrypt_error}")

                    # Extract each selected file
                    for file_info in meta['files']:
                        if file_info['custom_name'] in selected_files:
                            output_pdf = os.path.join(temp_dir, file_info['custom_name'] + '.pdf')

                            # Create PDF writer for this file
                            pdf_writer = PdfWriter()

                            # Add the appropriate pages
                            start_page = file_info['offset']
                            end_page = start_page + file_info['length']
                            for page_num in range(start_page, end_page):
                                if page_num < len(pdf_reader.pages):
                                    pdf_writer.add_page(pdf_reader.pages[page_num])

                            # Write the PDF to temporary file
                            with open(output_pdf, 'wb') as out_f:
                                pdf_writer.write(out_f)

                            # ENCRYPT THE INDIVIDUAL PDF WITH PASSWORD
                            if revenue_site.pdf_password:
                                try:
                                    # Read the unencrypted PDF content
                                    with open(output_pdf, 'rb') as pdf_file:
                                        unencrypted_content = pdf_file.read()

                                    # Encrypt the PDF
                                    encrypted_content = encrypt_pdf_with_password(unencrypted_content,
                                                                                  revenue_site.pdf_password)

                                    # Write the encrypted content back to the file
                                    with open(output_pdf, 'wb') as encrypted_file:
                                        encrypted_file.write(encrypted_content)

                                    print(f"PDF encrypted with password: {revenue_site.pdf_password}")

                                except Exception as e:
                                    print(f"Failed to encrypt PDF: {e}")

                            # Add the PDF to zip
                            zipf.write(output_pdf, arcname=f"{file_info['custom_name']}.pdf")

            except Exception as pdf_error:
                print(f"Error reading main PDF: {pdf_error}")
                return HttpResponseBadRequest(f"Error reading PDF file: {str(pdf_error)}")

        # Read the zip file into memory
        with open(zip_filename, 'rb') as f:
            zip_content = f.read()

        # Clean up temporary files immediately
        shutil.rmtree(temp_dir)

        # Create response with the in-memory content
        response = HttpResponse(zip_content, content_type='application/zip')
        response['Content-Disposition'] = f'attachment; filename=selected_files_{revenue_site.full_name}.zip'

        # Add password information to response headers
        if revenue_site.pdf_password:
            response['X-Password'] = revenue_site.pdf_password
            print(f"Selected files zip created with password-protected PDFs. Password: {revenue_site.pdf_password}")

        return response

    except Exception as e:
        # Clean up if any files were created
        if 'temp_dir' in locals() and os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)
        return HttpResponseBadRequest(f"Error unmerging document: {str(e)}")

import time  # Add this import at the top with other imports
from django.utils import timezone  # Make sure this is imported


def upload_documents(request, pk):
    site = get_object_or_404(RevenueSite, pk=pk)

    if request.method == 'POST':
        try:
            merged_path = request.POST.get('merged_document_path')

            if merged_path and os.path.exists(merged_path):
                # Generate PDF password if it doesn't exist
                if not site.pdf_password:
                    site.pdf_password = site.generate_pdf_password()
                    print(f"Generated PDF password: {site.pdf_password}")

                # Create user-specific folder
                user_folder = os.path.join(
                    'documents/revenue_sites',
                    site.full_name.replace(' ', '_')
                )
                os.makedirs(os.path.join(settings.MEDIA_ROOT, user_folder), exist_ok=True)

                # Generate final filename with timestamp
                document_title = request.POST.get('document_title', 'document')
                final_filename = f"{document_title}_{int(time.time())}.pdf"
                final_path = os.path.join(user_folder, final_filename)
                final_full_path = os.path.join(settings.MEDIA_ROOT, final_path)

                # ENCRYPT THE PDF BEFORE SAVING (FOR QR CODE ACCESS)
                if site.pdf_password:
                    try:
                        # Read the original PDF
                        with open(merged_path, 'rb') as original_file:
                            original_content = original_file.read()

                        # Encrypt the PDF
                        encrypted_content = encrypt_pdf_with_password(original_content, site.pdf_password)

                        # Save the encrypted version
                        with open(final_full_path, 'wb') as encrypted_file:
                            encrypted_file.write(encrypted_content)

                        print(f"Main PDF encrypted with password: {site.pdf_password}")

                    except Exception as e:
                        print(f"Failed to encrypt main PDF: {e}")
                        # Fallback: move the original file without encryption
                        shutil.move(merged_path, final_full_path)
                else:
                    # Move without encryption if no password
                    shutil.move(merged_path, final_full_path)

                # Move the metadata file if it exists
                meta_path = merged_path + '.meta.json'
                if os.path.exists(meta_path):
                    final_meta_path = os.path.join(settings.MEDIA_ROOT, final_path + '.meta.json')
                    shutil.move(meta_path, final_meta_path)

                # Update the site
                site.document_file.name = final_path
                if request.POST.get('document_title'):
                    site.document_title = request.POST.get('document_title')
                if request.POST.get('remarks'):
                    site.remarks = request.POST.get('remarks')
                site.document_uploaded_at = timezone.now()
                site.save()

                # Clean up any remaining temporary files
                if os.path.exists(merged_path):
                    os.remove(merged_path)
                if os.path.exists(meta_path):
                    os.remove(meta_path)

                return JsonResponse({'success': True, 'message': 'Documents uploaded successfully!'})

            else:
                return JsonResponse({'success': False, 'error': 'No documents to upload or file not found'})

        except Exception as e:
            # Clean up any temporary files in case of error
            merged_path = request.POST.get('merged_document_path')
            if merged_path and os.path.exists(merged_path):
                try:
                    os.remove(merged_path)
                    meta_path = merged_path + '.meta.json'
                    if os.path.exists(meta_path):
                        os.remove(meta_path)
                except:
                    pass

            return JsonResponse({'success': False, 'error': str(e)})

    # GET request - show upload form
    context = {
        'site': site,
    }
    return render(request, 'revenue_sites/upload_documents.html', context)

class RevenueSiteListView(LoginRequiredMixin, ListView):
    model = RevenueSite
    template_name = 'revenue_sites/list.html'
    context_object_name = 'sites'
    paginate_by = 20

    def get_queryset(self):
        queryset = super().get_queryset()

        # Apply division filter for non-superusers
        if not self.request.user.is_superuser:
            queryset = queryset.filter(division=self.request.user.division)

        # Add search functionality
        search_query = self.request.GET.get('search', '')
        if search_query:
            queryset = queryset.filter(
                Q(full_name__icontains=search_query) |
                Q(file_no__icontains=search_query) |
                Q(nagar_bhumapan_kramank__icontains=search_query) |
                Q(plot_no__icontains=search_query) |
                Q(document_title__icontains=search_query) |
                Q(district__icontains=search_query) |
                Q(taluka__icontains=search_query)
            )

        return queryset.order_by('-last_updated')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Pass search query to template
        context['search_query'] = self.request.GET.get('search', '')
        return context

# class RevenueSiteDetailView(LoginRequiredMixin, DetailView):
#     model = RevenueSite
#     template_name = 'revenue_sites/detail.html'
#     context_object_name = 'site'


class RevenueSiteDetailView(LoginRequiredMixin, DetailView):
    model = RevenueSite
    template_name = 'revenue_sites/detail.html'
    context_object_name = 'object'  # Change from 'site' to 'object' to match your template

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        revenue_site = self.object

        documents = []
        # Load document metadata if available
        if revenue_site.document_file:
            doc_path = revenue_site.document_file.path
            meta_path = doc_path + '.meta.json'

            if os.path.exists(meta_path):
                try:
                    with open(meta_path, 'r') as f:
                        meta = json.load(f)
                        documents = meta.get('files', [])
                except Exception:
                    # If there's an error reading metadata, just continue without documents
                    documents = []

        context['documents'] = documents
        return context


class RevenueSiteUpdateView(LoginRequiredMixin, UpdateView):
    model = RevenueSite
    form_class = RevenueSiteForm
    template_name = 'revenue_sites/update.html'
    success_url = reverse_lazy('list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Get existing documents from metadata (the individual files that were merged)
        context['existing_documents'] = self.get_existing_documents_from_metadata()
        return context

    def get_existing_documents_from_metadata(self):
        """Get the individual files that were merged from the metadata"""
        existing_docs = []
        revenue_site = self.object

        if revenue_site.document_file and os.path.exists(revenue_site.document_file.path):
            # Check for metadata file
            meta_path = revenue_site.document_file.path + '.meta.json'

            if os.path.exists(meta_path):
                try:
                    with open(meta_path, 'r') as f:
                        meta = json.load(f)

                    # Get the individual files that were merged
                    for file_info in meta.get('files', []):
                        existing_docs.append({
                            'name': file_info['custom_name'],
                            'original_name': file_info['original_name'],
                            'type': file_info['type'],
                            'pages': file_info['pages'],
                            'offset': file_info['offset'],  # Starting page in merged PDF
                            'length': file_info['length'],  # Number of pages
                        })

                except Exception as e:
                    print(f"Error reading metadata: {e}")
                    # If metadata is corrupted, show at least the main document
                    existing_docs.append({
                        'name': revenue_site.document_title or 'Main Document',
                        'original_name': os.path.basename(revenue_site.document_file.name),
                        'type': '.pdf',
                        'pages': 'Unknown',
                        'offset': 0,
                        'length': 'Unknown'
                    })
            else:
                # No metadata found, show the main document
                existing_docs.append({
                    'name': revenue_site.document_title or 'Main Document',
                    'original_name': os.path.basename(revenue_site.document_file.name),
                    'type': '.pdf',
                    'pages': 'Unknown',
                    'offset': 0,
                    'length': 'Unknown'
                })

        return existing_docs

    def handle_file_replacements(self):
        """Handle replacement of individual files AND adding new files to the merged document"""
        request = self.request
        revenue_site = self.object

        print(f"DEBUG: Handling file replacements for {revenue_site}")
        print(f"DEBUG: FILES in request: {list(request.FILES.keys())}")
        print(f"DEBUG: POST data: {list(request.POST.keys())}")

        if not revenue_site.document_file or not os.path.exists(revenue_site.document_file.path):
            print("DEBUG: No document file exists")
            return

        meta_path = revenue_site.document_file.path + '.meta.json'

        if not os.path.exists(meta_path):
            print("DEBUG: No metadata file found for replacements")
            return

        try:
            # Load existing metadata
            with open(meta_path, 'r') as f:
                meta = json.load(f)

            print(f"DEBUG: Metadata files: {[f['custom_name'] for f in meta.get('files', [])]}")

            # Verify current PDF structure before any changes
            print("DEBUG: Verifying current PDF structure...")
            self.verify_pdf_structure(revenue_site.document_file.path, meta)

            replacements_made = False
            new_files_added = False

            # 1. Process file replacements
            for key, file_obj in request.FILES.items():
                print(f"DEBUG: Processing file key: {key}")
                if key.startswith('replace_file_'):
                    # Extract the custom name from the key
                    custom_name = key.replace('replace_file_', '')
                    print(f"DEBUG: Found replacement file for: {custom_name}")

                    # Find the file in metadata
                    found = False
                    for i, file_info in enumerate(meta['files']):
                        if file_info['custom_name'] == custom_name:
                            print(f"DEBUG: Found file at index {i}: {file_info}")
                            print(
                                f"DEBUG: File info - offset: {file_info['offset']}, length: {file_info['length']}, pages: {file_info['pages']}")

                            # Replace the file
                            self.replace_file_in_merged_pdf(revenue_site, meta, i, file_obj)
                            replacements_made = True
                            found = True
                            break

                    if not found:
                        print(f"DEBUG: File {custom_name} not found in metadata")

            # 2. Process NEW files to be added
            new_files_data = self.extract_new_files_from_request(request)
            if new_files_data:
                print(f"DEBUG: Found {len(new_files_data)} new files to add")
                self.add_new_files_to_pdf(revenue_site, meta, new_files_data)
                new_files_added = True
            else:
                print("DEBUG: No new files found in request")

            if replacements_made or new_files_added:
                # Verify the PDF structure after changes
                print("DEBUG: Verifying PDF structure after changes...")
                self.verify_pdf_structure(revenue_site.document_file.path, meta)
                print("DEBUG: File processing completed successfully")
            else:
                print("DEBUG: No file changes were made")

        except Exception as e:
            print(f"DEBUG: Error in handle_file_replacements: {e}")
            import traceback
            traceback.print_exc()

    def extract_new_files_from_request(self, request):
        """Extract new files and their names from the request"""
        new_files_data = []

        # Get all new filenames from POST data
        new_filenames = request.POST.getlist('new_filename[]')
        new_uploadfiles = request.FILES.getlist('new_uploadfile[]')

        print(f"DEBUG: New filenames: {new_filenames}")
        print(f"DEBUG: New upload files count: {len(new_uploadfiles)}")

        # Pair filenames with files
        for i, (filename, file_obj) in enumerate(zip(new_filenames, new_uploadfiles)):
            if filename.strip() and file_obj:  # Both filename and file must be provided
                new_files_data.append({
                    'custom_name': filename.strip(),
                    'file_obj': file_obj,
                    'original_name': file_obj.name
                })
                print(f"DEBUG: New file {i}: '{filename}' -> {file_obj.name}")

        return new_files_data

    def add_new_files_to_pdf(self, revenue_site, meta, new_files_data):
        """Add new files to the end of the existing PDF"""
        temp_dir = None
        try:
            # Create temporary directory
            temp_dir = tempfile.mkdtemp()

            # Paths
            original_pdf_path = revenue_site.document_file.path
            temp_pdf_path = os.path.join(temp_dir, 'temp_merged.pdf')
            meta_path = original_pdf_path + '.meta.json'

            print(f"DEBUG: Adding {len(new_files_data)} new files to PDF")

            # Create new PDF merger
            merger = PdfMerger()

            # 1. Add the entire existing PDF first
            merger.append(original_pdf_path)

            # Get current total pages to calculate offsets for new files
            with open(original_pdf_path, 'rb') as f:
                original_reader = PdfReader(f)
                current_total_pages = len(original_reader.pages)

            print(f"DEBUG: Current PDF has {current_total_pages} pages")

            # 2. Add each new file to the end
            for new_file_data in new_files_data:
                custom_name = new_file_data['custom_name']
                file_obj = new_file_data['file_obj']
                original_name = new_file_data['original_name']

                print(f"DEBUG: Adding new file: '{custom_name}' ({original_name})")

                # Save the uploaded file temporarily
                temp_file_path = os.path.join(temp_dir, file_obj.name)
                with open(temp_file_path, 'wb+') as destination:
                    for chunk in file_obj.chunks():
                        destination.write(chunk)

                # Convert to PDF if needed
                pdf_path = self.convert_to_pdf_if_needed(temp_file_path, temp_dir)

                # Add the new file to the merger
                with open(pdf_path, 'rb') as f:
                    new_reader = PdfReader(f)
                    new_page_count = len(new_reader.pages)
                    merger.append(pdf_path)

                    # Add to metadata
                    new_file_info = {
                        'custom_name': custom_name,
                        'original_name': original_name,
                        'type': os.path.splitext(original_name)[1].lower(),
                        'pages': new_page_count,
                        'length': new_page_count,
                        'offset': current_total_pages  # New files start at the end
                    }
                    meta['files'].append(new_file_info)

                    # Update current total pages for next file
                    current_total_pages += new_page_count

                    print(
                        f"DEBUG: Added '{custom_name}' at offset {new_file_info['offset']} with {new_page_count} pages")

            # Write new merged PDF
            merger.write(temp_pdf_path)
            merger.close()

            # Replace the original file
            shutil.copy2(temp_pdf_path, original_pdf_path)

            # Update metadata file
            with open(meta_path, 'w') as f:
                json.dump(meta, f, indent=2)

            print(f"DEBUG: Successfully added {len(new_files_data)} new files to PDF")

        except Exception as e:
            print(f"Error adding new files to PDF: {e}")
            import traceback
            traceback.print_exc()
            raise
        finally:
            # Cleanup
            if temp_dir and os.path.exists(temp_dir):
                shutil.rmtree(temp_dir)

    def verify_pdf_structure(self, pdf_path, meta):
        """Verify that the PDF structure matches the metadata"""
        try:
            with open(pdf_path, 'rb') as f:
                reader = PdfReader(f)
                total_pages = len(reader.pages)

            print(f"VERIFICATION: PDF has {total_pages} pages")

            # Verify each file's position in the PDF
            current_position = 0
            for i, file_info in enumerate(meta['files']):
                expected_start = file_info['offset']
                expected_length = file_info['length']
                expected_end = expected_start + expected_length

                if expected_start != current_position:
                    print(
                        f"VERIFICATION WARNING: File {i} ('{file_info['custom_name']}') starts at {expected_start}, but expected {current_position}")

                if expected_end > total_pages:
                    print(
                        f"VERIFICATION ERROR: File {i} ('{file_info['custom_name']}') ends at {expected_end}, but PDF only has {total_pages} pages")

                current_position = expected_end
                print(
                    f"VERIFICATION: File {i} ('{file_info['custom_name']}') - pages {expected_start} to {expected_end - 1} (length: {expected_length})")

            if current_position != total_pages:
                print(
                    f"VERIFICATION WARNING: PDF has {total_pages} pages, but metadata accounts for {current_position} pages")

            return current_position == total_pages

        except Exception as e:
            print(f"Error verifying PDF structure: {e}")
            return False

    def replace_file_in_merged_pdf(self, revenue_site, meta, file_index, new_file):
        """Replace a specific file in the merged PDF - Fixed version"""
        temp_dir = None
        try:
            # Create temporary directory
            temp_dir = tempfile.mkdtemp()

            # Paths
            original_pdf_path = revenue_site.document_file.path
            temp_pdf_path = os.path.join(temp_dir, 'temp_merged.pdf')
            meta_path = original_pdf_path + '.meta.json'

            # Get file info
            file_info = meta['files'][file_index]
            start_page = file_info['offset']  # Starting page index
            end_page = start_page + file_info['length']  # Ending page index (exclusive)

            print(f"DEBUG: Replacing file '{file_info['custom_name']}' at pages {start_page} to {end_page - 1}")

            # Read original PDF to get total pages
            with open(original_pdf_path, 'rb') as f:
                original_reader = PdfReader(f)
                total_pages = len(original_reader.pages)

            print(f"DEBUG: Original PDF has {total_pages} pages")
            print(
                f"DEBUG: File to replace spans from page {start_page} to {end_page - 1} (length: {file_info['length']})")

            # Validate page ranges
            if start_page < 0 or end_page > total_pages or start_page >= end_page:
                print(f"ERROR: Invalid page range: {start_page}-{end_page} for PDF with {total_pages} pages")
                raise ValueError(f"Invalid page range: {start_page}-{end_page}")

            # Create new PDF merger
            merger = PdfMerger()

            # 1. Add pages BEFORE the section to replace (from 0 to start_page)
            if start_page > 0:
                print(f"DEBUG: Adding pages 0 to {start_page}")
                merger.append(original_pdf_path, pages=(0, start_page))

            # 2. Convert and add the NEW file (this replaces the old content)
            temp_new_file_path = os.path.join(temp_dir, new_file.name)
            with open(temp_new_file_path, 'wb+') as destination:
                for chunk in new_file.chunks():
                    destination.write(chunk)

            new_pdf_path = self.convert_to_pdf_if_needed(temp_new_file_path, temp_dir)

            # Add the new file
            with open(new_pdf_path, 'rb') as f:
                new_reader = PdfReader(f)
                new_page_count = len(new_reader.pages)
                print(f"DEBUG: New file has {new_page_count} pages")
                merger.append(new_pdf_path)

                # Update metadata
                meta['files'][file_index]['pages'] = new_page_count
                meta['files'][file_index]['length'] = new_page_count
                meta['files'][file_index]['original_name'] = new_file.name

            # 3. Add pages AFTER the replaced section (from end_page to total_pages)
            if end_page < total_pages:
                print(f"DEBUG: Adding pages {end_page} to {total_pages}")
                merger.append(original_pdf_path, pages=(end_page, total_pages))
            else:
                print(f"DEBUG: No pages after the replaced section")

            # Write new merged PDF
            merger.write(temp_pdf_path)
            merger.close()

            # Calculate page difference for offset updates
            page_diff = new_page_count - file_info['length']
            print(f"DEBUG: Page difference: {page_diff}")

            # Update offsets for subsequent files
            if page_diff != 0:
                for i in range(file_index + 1, len(meta['files'])):
                    old_offset = meta['files'][i]['offset']
                    new_offset = old_offset + page_diff
                    meta['files'][i]['offset'] = new_offset
                    print(
                        f"DEBUG: Updated offset for file {i} ('{meta['files'][i]['custom_name']}'): {old_offset} -> {new_offset}")

            # Replace the original file with the new merged PDF
            shutil.copy2(temp_pdf_path, original_pdf_path)

            # Update metadata file
            with open(meta_path, 'w') as f:
                json.dump(meta, f, indent=2)

            # Verify the new PDF
            with open(original_pdf_path, 'rb') as f:
                new_reader = PdfReader(f)
                final_page_count = len(new_reader.pages)
                print(f"DEBUG: Final PDF has {final_page_count} pages")

            expected_pages = start_page + new_page_count + (total_pages - end_page)
            print(f"DEBUG: Expected pages: {expected_pages}, Actual pages: {final_page_count}")

            if final_page_count != expected_pages:
                print(f"WARNING: Page count mismatch! Expected {expected_pages}, got {final_page_count}")

            print(f"Successfully replaced file '{file_info['custom_name']}'. Final PDF has {final_page_count} pages")

        except Exception as e:
            print(f"Error replacing file in PDF: {e}")
            import traceback
            traceback.print_exc()
            raise
        finally:
            # Cleanup
            if temp_dir and os.path.exists(temp_dir):
                shutil.rmtree(temp_dir)

    def validate_page_ranges(self, meta, total_pages):
        """Validate that all page ranges in metadata are within bounds"""
        for i, file_info in enumerate(meta['files']):
            start_page = file_info['offset']
            end_page = start_page + file_info['length']

            if start_page < 0 or end_page > total_pages or start_page >= end_page:
                print(f"WARNING: Invalid page range for file {i}: {start_page}-{end_page} (total pages: {total_pages})")
                return False
        return True

    def convert_to_pdf_if_needed(self, file_path, temp_dir):
        """Convert various file types to PDF"""
        ext = os.path.splitext(file_path)[1].lower()
        pdf_path = os.path.join(temp_dir, 'converted.pdf')

        if ext == '.pdf':
            return file_path

        try:
            if ext in ['.jpg', '.jpeg', '.png', '.bmp', '.gif', '.tiff', '.tif']:
                # Convert image to PDF
                from PIL import Image
                with Image.open(file_path) as img:
                    if img.mode != 'RGB':
                        img = img.convert('RGB')
                    img.save(pdf_path, "PDF", resolution=100.0)

            elif ext in ['.docx', '.doc']:
                # Convert DOCX to PDF
                try:
                    from pdf2docx import Converter
                    cv = Converter(file_path)
                    cv.convert(pdf_path)
                    cv.close()
                except:
                    # Fallback: create simple PDF
                    self.create_simple_pdf(file_path, pdf_path)

            else:
                # Create simple PDF for unsupported types
                self.create_simple_pdf(file_path, pdf_path)

            return pdf_path

        except Exception as e:
            print(f"Error converting file to PDF: {e}")
            # Fallback to simple PDF
            self.create_simple_pdf(file_path, pdf_path)
            return pdf_path

    def create_simple_pdf(self, original_path, pdf_path):
        """Create a simple PDF with file information"""
        from reportlab.pdfgen import canvas
        from reportlab.lib.pagesizes import letter

        c = canvas.Canvas(pdf_path, pagesize=letter)
        c.drawString(100, 750, f"File: {os.path.basename(original_path)}")
        c.drawString(100, 730, "Original file could not be converted to PDF")
        c.save()

    def form_valid(self, form):
        try:
            # Save the form first
            self.object = form.save()

            # Handle file replacements
            self.handle_file_replacements()

            # Refresh the instance
            self.object.refresh_from_db()

            # Check if it's an AJAX request
            if self.request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': True,
                    'message': _('Revenue site updated successfully!'),
                    'document_url': self.object.document_file.url if self.object.document_file else '',
                    'document_name': os.path.basename(
                        self.object.document_file.name) if self.object.document_file else ''
                })

            messages.success(self.request, _('Revenue site updated successfully!'))
            return HttpResponseRedirect(self.get_success_url())

        except Exception as e:
            print(f"Error in form_valid: {e}")
            import traceback
            traceback.print_exc()

            if self.request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': False,
                    'message': _('Error updating document: ') + str(e)
                }, status=500)

            messages.error(self.request, _('Error updating document: ') + str(e))
            return self.form_invalid(form)

def update_additional_documents(request):
    """Handle additional documents during update"""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Invalid request method'}, status=400)

    try:
        site_id = request.POST.get('site_id')
        if not site_id:
            return JsonResponse({'success': False, 'error': 'Site ID is required'}, status=400)

        site = get_object_or_404(RevenueSite, pk=site_id)

        # Handle additional documents if any
        if request.FILES.getlist('files'):
            # For now, we'll just return success since the main form handles the primary document
            # In a real implementation, you might want to handle additional documents separately
            return JsonResponse({
                'success': True,
                'message': 'Additional documents processed successfully'
            })
        else:
            return JsonResponse({
                'success': True,
                'message': 'No additional documents to process'
            })

    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


def revenuesite_delete(request, pk):
    if request.method == 'POST':
        revenue_site = get_object_or_404(RevenueSite, pk=pk)

        # Check if user has permission to delete (optional: add permission checks)
        if not request.user.is_authenticated:
            messages.error(request, "You must be logged in to delete revenue sites.")
            return redirect('list')

        try:
            # Delete associated files if they exist
            if revenue_site.document_file:
                # Delete the main document file
                if os.path.exists(revenue_site.document_file.path):
                    os.remove(revenue_site.document_file.path)

                # Delete metadata file if it exists
                meta_path = revenue_site.document_file.path + '.meta.json'
                if os.path.exists(meta_path):
                    os.remove(meta_path)

            # Delete the revenue site record
            revenue_site.delete()

            messages.success(request, "Customer was deleted successfully!")

        except Exception as e:
            messages.error(request, f"Error deleting revenue site: {str(e)}")

        return redirect('list')

    # If not POST method, redirect to list
    return redirect('list')

from django.http import JsonResponse
from django.views.decorators.http import require_GET


@require_GET
def get_compartments(request):
    drawer_id = request.GET.get('drawer_id')

    if not drawer_id:
        return JsonResponse({'compartments': []})

    try:
        from .models import Compartment
        compartments = Compartment.objects.filter(drawer_id=drawer_id).order_by('compartment_number')

        compartments_data = [
            {
                'id': compartment.id,
                'compartment_number': compartment.compartment_number,
                'drawer_number': compartment.drawer.drawer_number
            }
            for compartment in compartments
        ]

        return JsonResponse({'compartments': compartments_data})

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('list')
    else:
        form = CustomUserCreationForm()

    return render(request, 'registration/register.html', {'form': form})


from django.shortcuts import get_object_or_404, reverse
from django.http import HttpResponse
import qrcode
from io import BytesIO
import base64

from django.shortcuts import get_object_or_404
from django.http import JsonResponse


def generate_qr_code(request, pk):
    site = get_object_or_404(RevenueSite, pk=pk)

    data = {
        'site_name': site.full_name,
        'document_url': site.document_file.url if site.document_file else reverse('detail', args=[site.pk]),
        'file_no': site.file_no or 'N/A',
        'doc_type': site.document_title or 'Revenue Site',
        'ward': site.ward.ward_number or 'N/A',
        'drawer': site.drawer.drawer_number or 'N/A',
        'compartment': site.compartment.compartment_number or 'N/A',
        'inward': site.registration_date.strftime('%d-%m-%Y'),
    }

    return JsonResponse(data)



from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from django.urls import reverse
from io import BytesIO
import qrcode
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.utils import ImageReader
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Image
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
from .models import RevenueSite
import base64
import json


def generate_all_qr_pdf(request):
    sites = RevenueSite.objects.all()
    if not request.user.is_superuser:
        sites = sites.filter(division=request.user.division)
    return generate_pdf_response(request, sites)


def generate_selected_qr_pdf(request):
    if request.method == 'POST':
        selected_ids = request.POST.getlist('selected_sites')
        sites = RevenueSite.objects.filter(pk__in=selected_ids)
        return generate_pdf_response(request, sites)
    return redirect('list')


def generate_pdf_response(request, sites):
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="client_qr_codes.pdf"'

    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=30, bottomMargin=30)
    elements = []
    styles = getSampleStyleSheet()

    # Create a custom style for the data
    data_style = styles['Normal']
    data_style.fontSize = 8
    data_style.leading = 10

    # Add password information to the PDF
    if sites.exists():
        first_site = sites.first()
        if first_site.pdf_password:
            password_note = Paragraph(
                f"<b>NOTE:</b> All individual PDFs are protected with password: {first_site.pdf_password}",
                styles['Normal']
            )
            elements.append(password_note)
            elements.append(Paragraph("<br/>", styles['Normal']))

    # Process sites in pairs for two-column layout
    site_pairs = []
    for i in range(0, len(sites), 2):
        pair = sites[i:i + 2]
        site_pairs.append(pair)

    for pair in site_pairs:
        row_data = []

        for site in pair:
            qr_img, qr_data = generate_qr_code_data(request, site)

            # Create temporary file for ReportLab
            temp_img = BytesIO()
            temp_img.write(qr_img)
            temp_img.seek(0)

            # Add password information to the data display
            password_info = f"<b>PDF Password:</b> {site.pdf_password}<br/>" if site.pdf_password else ""

            site_content = [
                [Image(temp_img, width=70, height=70),
                 Paragraph(f"""
                 {password_info}
                 <b>Client:</b> {site.full_name}<br/>
                 <b>File No:</b> {site.file_no or 'N/A'}<br/>
                 <b>Doc Type:</b> {site.document_title or 'Revenue Site'}<br/>
                 <b>Ward:</b> {site.ward.ward_number or 'N/A'}<br/>
                 <b>Drawer:</b> {site.drawer.drawer_number or 'N/A'}<br/>
                 <b>Compartment:</b> {site.compartment.compartment_number or 'N/A'}<br/>
                 <b>Inward:</b> {site.registration_date.strftime('%d-%m-%Y')}
                 """, data_style)]
            ]

            site_table = Table(site_content, colWidths=[80, 180])
            site_table.setStyle(TableStyle([
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('ALIGN', (0, 0), (0, 0), 'CENTER'),
                ('LEFTPADDING', (0, 0), (-1, -1), 5),
                ('RIGHTPADDING', (0, 0), (-1, -1), 5),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
            ]))

            row_data.append(site_table)

        # If odd number of sites, add an empty cell
        if len(pair) == 1:
            empty_content = Paragraph("", data_style)
            empty_table = Table([[empty_content]], colWidths=[260])
            row_data.append(empty_table)

        # Create a row with two columns
        row_table = Table([row_data], colWidths=[260, 260])
        row_table.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('LEFTPADDING', (0, 0), (-1, -1), 5),
            ('RIGHTPADDING', (0, 0), (-1, -1), 5),
        ]))

        elements.append(row_table)

    doc.build(elements)
    pdf_data = buffer.getvalue()
    buffer.close()

    # Encrypt the final PDF with a common password if needed
    # You can choose to encrypt this PDF too or leave it unencrypted
    # since it only contains QR codes, not the actual documents

    response.write(pdf_data)
    return response


def generate_qr_code_data(request, site):
    # Use the protected PDF view URL instead of direct media URL
    protected_url = request.build_absolute_uri(
        reverse('protected_pdf', args=[site.pk])
    )

    # QR code contains the protected URL
    qr_data = protected_url

    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=6,
        border=2,
    )

    qr.add_data(qr_data)
    qr.make(fit=True)
    qr_img = qr.make_image(fill_color="black", back_color="white")

    img_buffer = BytesIO()
    qr_img.save(img_buffer, format='PNG')

    # For display purposes, create the text data separately
    password_info = f"PDF Password: {site.pdf_password}\n" if site.pdf_password else ""

    display_data = f"""REVENUE DOCUMENT
{password_info}File No: {site.file_no or 'N/A'}
Client: {site.full_name}
Document Type: {site.document_title or 'Revenue Site'}
Ward: {site.ward.ward_number or 'N/A'}
Drawer: {site.drawer.drawer_number or 'N/A'}
Compartment: {site.compartment.compartment_number or 'N/A'}
Inward Date: {site.registration_date.strftime('%d-%m-%Y')}

PDF Link: {protected_url}"""

    return img_buffer.getvalue(), display_data


def get_qr_preview_data(request):
    if request.GET.get('type') == 'all':
        sites = RevenueSite.objects.all()
        if not request.user.is_superuser:
            sites = sites.filter(division=request.user.division)
    else:
        ids = request.GET.get('ids', '').split(',')
        sites = RevenueSite.objects.filter(pk__in=ids)

    preview_data = []
    for site in sites:
        document_url = request.build_absolute_uri(
            site.document_file.url if site.document_file else reverse('detail', args=[site.pk])
        )

        # QR code contains ONLY the URL
        qr_data = document_url  # ONLY the URL

        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=6,
            border=2,
        )

        qr.add_data(qr_data)
        qr.make(fit=True)
        qr_img = qr.make_image(fill_color="black", back_color="white")

        buffer = BytesIO()
        qr_img.save(buffer, format="PNG")
        qr_base64 = base64.b64encode(buffer.getvalue()).decode()

        # Display data is separate
        display_data = f"""REVENUE DOCUMENT
File No: {site.file_no or 'N/A'}
Client: {site.full_name}
Document Type: {site.document_title or 'Revenue Site'}
Ward: {site.ward.ward_number or 'N/A'}
Drawer: {site.drawer.drawer_number or 'N/A'}
Compartment: {site.compartment.compartment_number or 'N/A'}
Inward Date: {site.registration_date.strftime('%d-%m-%Y')}

PDF Link: {document_url}"""

        preview_data.append({
            'image': f"data:image/png;base64,{qr_base64}",
            'data': display_data,  # This is for display only
            'name': site.full_name,
            'id': site.pk
        })

    return JsonResponse({'previews': preview_data})
