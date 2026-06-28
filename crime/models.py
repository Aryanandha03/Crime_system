from django.db import models
from django.contrib.auth.models import User
from django.db.models import Max
import datetime


class Complaint(models.Model):

    # ---------------- Complaint Number ----------------

    complaint_number = models.CharField(
        max_length=25,
        unique=True,
        blank=True
    )

    # ---------------- Choices ----------------

    CATEGORY = [
        ("Theft", "Theft"),
        ("Assault", "Assault"),
        ("Cyber Crime", "Cyber Crime"),
        ("Domestic Violence", "Domestic Violence"),
        ("Missing Person", "Missing Person"),
        ("Drug Crime", "Drug Crime"),
        ("Traffic Violation", "Traffic Violation"),
        ("Fraud", "Fraud"),
        ("Robbery", "Robbery"),
        ("Other", "Other"),
    ]

    STATUS = [
        ("Pending", "Pending"),
        ("Assigned", "Assigned"),
        ("Investigating", "Investigating"),
        ("Closed", "Closed"),
    ]

    PRIORITY = [
        ("Low", "Low"),
        ("Medium", "Medium"),
        ("High", "High"),
        ("Emergency", "Emergency"),
    ]

    # ---------------- Citizen ----------------

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=15, blank=True)
    anonymous = models.BooleanField(default=False)

    # ---------------- Complaint Info ----------------

    category = models.CharField(max_length=50, choices=CATEGORY, default="Other")
    title = models.CharField(max_length=200)
    description = models.TextField()
    location = models.CharField(max_length=255)

    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)

    crime_date = models.DateField()

    # ---------------- Evidence ----------------

    evidence = models.FileField(upload_to="evidence/", blank=True, null=True)

    # ---------------- Investigation ----------------

    priority = models.CharField(max_length=20, choices=PRIORITY, default="Medium")
    status = models.CharField(max_length=20, choices=STATUS, default="Pending")

    # 👮 Better than CharField (OPTIONAL UPGRADE)
    assigned_officer = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="assigned_complaints"
    )

    remarks = models.TextField(blank=True)

    fir_generated = models.BooleanField(default=False)

    # 🧠 Extra tracking (IMPORTANT UPGRADE)
    is_read = models.BooleanField(default=False)
    is_resolved = models.BooleanField(default=False)

    # ---------------- Dates ----------------

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # ---------------- Meta ----------------

    class Meta:
        ordering = ["-created_at"]

        indexes = [
            models.Index(fields=["status"]),
            models.Index(fields=["category"]),
            models.Index(fields=["priority"]),
            models.Index(fields=["created_at"]),
        ]

    # ---------------- SAVE LOGIC ----------------

    def save(self, *args, **kwargs):

        # Generate complaint number safely
        if not self.complaint_number:

            today = datetime.datetime.now().year

            last_id = Complaint.objects.aggregate(
                max_id=Max("id")
            )["max_id"] or 0

            self.complaint_number = f"CR-{today}-{last_id + 1:05d}"

        # Auto sync email
        if self.user and not self.email:
            self.email = self.user.email

        # Auto flags
        if self.status == "Closed":
            self.is_resolved = True

        super().save(*args, **kwargs)

    # ---------------- STRING ----------------

    def __str__(self):
        return f"{self.complaint_number} | {self.title}"
    

from django.contrib.auth.models import User
from django.db import models

class Profile(models.Model):
    USER_TYPES = (
        ('admin', 'Admin'),
        ('police', 'Police Officer'),
        ('citizen', 'Citizen'),
    )

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=USER_TYPES, default='citizen')

    def __str__(self):
        return self.user.username