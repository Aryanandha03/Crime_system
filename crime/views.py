from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.models import User
from django.db.models import Count
from django.http import HttpResponse
from reportlab.pdfgen import canvas
import json

from .forms import RegisterForm, ComplaintForm
from .models import Complaint


# ---------------- HOME ----------------
def home(request):
    return render(request, "home.html")


# ---------------- REGISTER ----------------
def register(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data["password"])
            user.save()
            return redirect("login")
    else:
        form = RegisterForm()

    return render(request, "register.html", {"form": form})


# ---------------- LOGIN ----------------
def user_login(request):
    if request.method == "POST":
        user = authenticate(
            request,
            username=request.POST.get("username"),
            password=request.POST.get("password")
        )

        if user:
            login(request, user)

            if user.is_superuser:
                return redirect("admin_dashboard")
            elif user.groups.filter(name="police").exists():
                return redirect("police_dashboard")
            else:
                return redirect("citizen_dashboard")   # FIXED

    return render(request, "login.html")


# ---------------- LOGOUT ----------------
def user_logout(request):
    logout(request)
    return redirect("home")


# ---------------- CITIZEN DASHBOARD ----------------
@login_required
def citizen_dashboard(request):
    complaints = Complaint.objects.filter(user=request.user)

    return render(request, "citizen_dashboard.html", {
        "complaints": complaints,
        "total": complaints.count(),
        "pending": complaints.filter(status="Pending").count(),
        "investigating": complaints.filter(status="Investigating").count(),
        "closed": complaints.filter(status="Closed").count(),
    })


# ---------------- DASHBOARD REDIRECT FIX ----------------
from django.shortcuts import render

def dashboard(request):

    return render(request, "dashboard.html", {
        "total": 102
    })

# ---------------- SUBMIT ----------------
@login_required
def submit_complaint(request):
    if request.method == "POST":
        form = ComplaintForm(request.POST, request.FILES)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.user = request.user
            obj.status = "Pending"
            obj.save()
            return redirect("citizen_dashboard")
    else:
        form = ComplaintForm()

    return render(request, "submit_complaint.html", {"form": form})


# ---------------- POLICE DASHBOARD ----------------
@login_required
def police_dashboard(request):
    if not request.user.groups.filter(name="police").exists():
        return redirect("home")

    complaints = Complaint.objects.filter(
        assigned_officer=request.user
    ).order_by("-created_at")

    return render(request, "police_dashboard.html", {
        "complaints": complaints,
        "total": complaints.count(),
        "pending": complaints.filter(status="Assigned").count(),
        "investigating": complaints.filter(status="Investigating").count(),
        "closed": complaints.filter(status="Closed").count(),
    })
# ---------------- OFFICER DASHBOARD ----------------
@login_required
def officer_dashboard(request):
    if not request.user.groups.filter(name="police").exists():
        return redirect("home")

    complaints = Complaint.objects.filter(
        assigned_officer=request.user
    ).order_by("-created_at")

    return render(request, "officer_dashboard.html", {
        "complaints": complaints,
        "total": complaints.count(),
        "pending": complaints.filter(status="Assigned").count(),
        "investigating": complaints.filter(status="Investigating").count(),
        "closed": complaints.filter(status="Closed").count(),
    })


# ---------------- UPDATE CASE ----------------
@login_required
def update_case(request, id):
    complaint = get_object_or_404(Complaint, id=id)

    if request.method == "POST":
        complaint.status = request.POST.get("status")
        complaint.remarks = request.POST.get("remarks")

        if complaint.status == "Closed":
            complaint.is_resolved = True

        complaint.save()

        # ✅ ROLE BASED REDIRECT
        if request.user.groups.filter(name="police").exists():
            return redirect("police_dashboard")

        elif request.user.is_superuser or request.user.groups.filter(name="admin").exists():
            return redirect("admin_dashboard")

        return redirect("home")
    
    return render(request, "update_case.html", {
        "complaint": complaint
    })


# ---------------- ADMIN DASHBOARD ----------------
from django.db.models import Q
from .models import Complaint

def admin_dashboard(request):

    complaints = Complaint.objects.all().order_by("-created_at")

    search = request.GET.get("search")
    status = request.GET.get("status")
    category = request.GET.get("category")

    
    
    if search:
        complaints = complaints.filter(
            Q(user__username__icontains=search) |
            Q(complaint_number__icontains=search) |
            Q(title__icontains=search) |
            Q(category__icontains=search) |
            Q(status__icontains=search) |
            Q(assigned_officer__username__icontains=search) |
            Q(remarks__icontains=search)
        )

    if status:
        complaints = complaints.filter(status=status)

    if category:
        complaints = complaints.filter(category=category)

    categories = (
        Complaint.objects
        .values_list("category", flat=True)
        .distinct()
        .order_by("category")
    )

    context = {
        "complaints": complaints,
        "categories": categories,
    }

    return render(request, "admin/dashboard.html", context)
# ---------------- ASSIGN OFFICER ----------------
@staff_member_required
def assign_officer(request, id):
    complaint = get_object_or_404(Complaint, id=id)

    if request.method == "POST":
        officer_id = request.POST.get("officer_id")

        officer = get_object_or_404(User, id=officer_id)

        complaint.assigned_officer = officer
        complaint.status = "Assigned"
        complaint.save()

        return redirect("admin_dashboard")

    police_users = User.objects.filter(groups__name="police")

    return render(request, "assign_officer.html", {
        "complaint": complaint,
        "police_users": police_users
    })


# ---------------- ANALYTICS ----------------
@staff_member_required
def analytics(request):
    data = {
        "Pending": Complaint.objects.filter(status="Pending").count(),
        "Assigned": Complaint.objects.filter(status="Assigned").count(),
        "Investigating": Complaint.objects.filter(status="Investigating").count(),
        "Closed": Complaint.objects.filter(status="Closed").count(),
    }

    return render(request, "analytics.html", {
        "data": json.dumps(data)
    })


# ---------------- REPORTS ----------------
@staff_member_required
def reports(request):
    return render(request, "reports.html", {
        "total": Complaint.objects.count(),
        "pending": Complaint.objects.filter(status="Pending").count(),
        "assigned": Complaint.objects.filter(status="Assigned").count(),
        "closed": Complaint.objects.filter(status="Closed").count(),
        "investigating": Complaint.objects.filter(status="Investigating").count(),
    })


# ---------------- COMPLAINT DETAIL ----------------
@login_required
def complaint_detail(request, id):

    if request.user.is_superuser or request.user.groups.filter(name="police").exists():
        complaint = get_object_or_404(Complaint, id=id)
    else:
        complaint = get_object_or_404(
            Complaint,
            id=id,
            user=request.user
        )

    return render(request, "complaint_detail.html", {
        "complaint": complaint
    })


# ---------------- DELETE ----------------

@login_required
def delete_complaint(request, id):
    complaint = get_object_or_404(Complaint, id=id)

    if request.method == "POST":
        complaint.delete()
        return redirect("history")

    return render(request, "delete_complaint.html", {
        "complaint": complaint
    })
# ---------------- EDIT ----------------

@login_required
def edit_complaint(request, id):
    complaint = get_object_or_404(Complaint, id=id)

    if request.method == "POST":
        form = ComplaintForm(request.POST, request.FILES, instance=complaint)
        if form.is_valid():
            form.save()
            return redirect("history")
    else:
        form = ComplaintForm(instance=complaint)

    return render(request, "edit_complaint.html", {
        "form": form,
        "complaint": complaint,
    })
# ---------------- PDF ----------------
@login_required
def download_pdf(request, id):

    if request.user.is_superuser or request.user.groups.filter(name="police").exists():
        complaint = get_object_or_404(Complaint, id=id)
    else:
        complaint = get_object_or_404(
            Complaint,
            id=id,
            user=request.user
        )

    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = f'attachment; filename="FIR_{complaint.id}.pdf"'

    p = canvas.Canvas(response)
    p.drawString(100, 800, f"Complaint No : {complaint.complaint_number}")
    p.drawString(100, 780, f"Title : {complaint.title}")
    p.drawString(100, 760, f"Status : {complaint.status}")
    p.drawString(100, 740, f"Location : {complaint.location}")

    p.showPage()
    p.save()

    return response


# ---------------- MAP ----------------
@login_required
def complaint_map(request, id):
    complaint = get_object_or_404(Complaint, id=id, user=request.user)

    return render(request, "complaint_map.html", {
        "complaint": complaint
    })


# ---------------- HEATMAP ----------------
@staff_member_required
def heatmap_dashboard(request):
    data = Complaint.objects.values('location').annotate(count=Count('id'))

    return render(request, "heatmap_dashboard.html", {
        "data": data
    })

@login_required
def complaint_history(request):
    complaints = Complaint.objects.filter(user=request.user)

    return render(request, "crime/complaint_history.html", {
        "complaints": complaints
    })



