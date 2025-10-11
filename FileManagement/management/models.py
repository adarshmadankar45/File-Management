from django.db import models
# Create your models here.
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import AbstractUser
import datetime
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import get_user_model



class CustomUser(AbstractUser):
    DIVISION_CHOICES = [
        ('Mumbai', 'Mumbai'),
        ('Pune', 'Pune'),
        ('Nagpur', 'Nagpur'),
        ('Nashik', 'Nashik'),
        ('Aurangabad', 'Aurangabad'),
        ('Amravati', 'Amravati'),
        ('Konkan', 'Konkan'),
    ]

    division = models.CharField(
        _('विभाग / Division'),
        max_length=50,
        choices=DIVISION_CHOICES
    )
    district = models.CharField(
        _('जिल्हा / District'),
        max_length=100
    )
    taluka = models.CharField(
        _('तालुका / Taluka'),
        max_length=100
    )
    village = models.CharField(
        _('गाव / Village'),
        max_length=100
    )
    full_name = models.CharField(
        _('पूर्ण नाव / Full Name'),
        max_length=150
    )
    email = models.EmailField(
        _('ईमेल / Email'),
        unique=True
    )
    mobile_number = models.CharField(
        _('मोबाइल नंबर / Mobile Number'),
        max_length=15
    )

    def __str__(self):
        return self.username

class MasterWard(models.Model):
    ward_name = models.CharField(max_length=50)
    ward_number = models.CharField(max_length=50)
    description = models.TextField(max_length=200)



class MasterDrawer(models.Model):
    drawer_number = models.CharField(max_length=50, unique=True, verbose_name="Drawer Number")
    description = models.TextField(blank=True, null=True, verbose_name="Description")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Master Drawer"
        verbose_name_plural = "Master Drawers"
        ordering = ['drawer_number']

    def __str__(self):
        return f"Drawer {self.drawer_number}"

class Compartment(models.Model):
    drawer = models.ForeignKey(MasterDrawer, on_delete=models.CASCADE, related_name='compartments', verbose_name="Drawer")
    compartment_number = models.CharField(max_length=50, verbose_name="Compartment Number")
    description = models.TextField(blank=True, null=True, verbose_name="Description")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Compartment"
        verbose_name_plural = "Compartments"
        unique_together = ('drawer', 'compartment_number')
        ordering = ['drawer', 'compartment_number']

    def __str__(self):
        return f"Compartment {self.compartment_number} in {self.drawer}"




class RevenueSite(models.Model):
    # Existing fields
    nagar_bhumapan_kramank = models.CharField(
        _('नगर भूमापन क्रमांक / City Survey Number'),
        max_length=100
    )
    seat_no = models.CharField(
        _('सीट क्रमांक / Seat Number'),
        max_length=50
    )
    plot_no = models.CharField(
        _('प्लॉट क्रमांक / Plot Number'),
        max_length=50
    )
    square_feet = models.DecimalField(
        _('चौरस फुट / Square Feet'),
        max_digits=10,
        decimal_places=2
    )
    dharna_dhikhar = models.CharField(
        _('धरणा धिकार / Ownership Type'),
        max_length=100
    )
    file_no = models.CharField(
        _('फाईल क्रमांक / File Number'),
        max_length=50,
        unique=True,
        blank=True,  # Allow blank as we'll generate it automatically
        null=True
    )

    registration_date = models.DateField(
        _('नोंदणी तारीख / Registration Date'),
        auto_now_add=True
    )
    remarks = models.TextField(
        _('टिप्पण्या / Remarks'),
        blank=True,
        null=True
    )

    division = models.CharField(
        _('विभाग / Division'),
        max_length=50, null=True, blank=True,
        choices=CustomUser.DIVISION_CHOICES
    )
    district = models.CharField(
        _('जिल्हा / District'),
        max_length=100
    )
    taluka = models.CharField(
        _('तालुका / Taluka'),
        max_length=100
    )
    village = models.CharField(
        _('गाव / Village'),
        max_length=100
    )
    full_name = models.CharField(
        _('पूर्ण नाव / Full Name'),
        max_length=150
    )
    email = models.EmailField(
        _('ईमेल / Email')
    )
    mobile_number = models.CharField(
        _('मोबाइल नंबर / Mobile Number'),
        max_length=15
    )
    created_by = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_sites'
    )
    last_updated = models.DateTimeField(
        _('अंतिम अद्यतन / Last Updated'),
        auto_now=True
    )

    document_title = models.CharField(
        _('दस्तऐवजाचे शीर्षक / Document Title'),
        max_length=200,
        blank=True,
        null=True
    )
    document_file = models.FileField(
        _('फाइल / File'),
        upload_to='documents/revenue_sites/',
        blank=True,
        null=True
    )
    document_uploaded_at = models.DateTimeField(
        _('अपलोड तारीख / Upload Date'),
        auto_now_add=True,
        blank=True,
        null=True
    )

    # New foreign key relationships
    ward = models.ForeignKey(
        'MasterWard',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name=_('वार्ड / Ward')
    )

    drawer = models.ForeignKey(
        'MasterDrawer',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name=_('ड्रॉवर / Drawer')
    )

    compartment = models.ForeignKey(
        'Compartment',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name=_('कंपार्टमेंट / Compartment')
    )
    pdf_password = models.CharField(_('PDF Password'),max_length=8,blank=True,null=True,)



    class Meta:
        verbose_name = _('रेव्हेन्यू साइट / Revenue Site')
        verbose_name_plural = _('रेव्हेन्यू साइट्स / Revenue Sites')

    def __str__(self):
        return f"{self.nagar_bhumapan_kramank} - {self.plot_no}"

    def clean(self):
        # Add any custom validation here
        if self.square_feet and self.square_feet <= 0:
            raise ValidationError(_('Square feet must be greater than zero'))

    def save(self, *args, **kwargs):
        # Generate file number if it doesn't exist
        if not self.file_no:
            try:
                # Count all existing revenue sites to get the next number
                total_sites_count = RevenueSite.objects.count() + 1
                # Format as 4-digit number starting from 0101
                self.file_no = f"{total_sites_count:04d}"
            except Exception as e:
                # Fallback if counting fails - use timestamp
                self.file_no = f"{int(time.time())}"

        super().save(*args, **kwargs)

    def generate_pdf_password(self):
        import random
        return ''.join(random.choice('0123456789') for _ in range(8))
