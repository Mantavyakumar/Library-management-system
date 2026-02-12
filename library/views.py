import logging
from datetime import timedelta

from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import redirect, render
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views.generic import View

from .forms import (
    AddBookForm,
    AddMemberForm,
    LendBookForm,
    LendMemberBookForm,
    PaymentForm,
    UpdateBorrowedBookForm,
    UpdateMemberForm,
)
from .models import Book, BorrowedBook, Member, Transaction

logger = logging.getLogger(__name__)


# ================= HOME =================

@method_decorator(login_required, name="dispatch")
class HomeView(View):

    def get(self, request, *args, **kwargs):
        members = Member.objects.all()
        books = Book.objects.all()
        borrowed_books = BorrowedBook.objects.filter(returned=False)
        overdue_books = BorrowedBook.objects.filter(
            return_date__lt=timezone.now().date(),
            returned=False,
        )

        context = {
            "total_members": members.count(),
            "total_books": books.count(),
            "total_borrowed_books": borrowed_books.count(),
            "total_overdue_books": overdue_books.count(),
            "recently_added_books": books.order_by("-created_at")[:4],
            "total_amount": sum([p.amount for p in Transaction.objects.all()]),
            "overdue_amount": sum([b.fine for b in overdue_books]),
        }

        return render(request, "index.html", context)


# ================= MEMBER =================

@method_decorator(login_required, name="dispatch")
class AddMemberView(View):

    def get(self, request, *args, **kwargs):
        return render(request, "members/add-member.html",
                      {"form": AddMemberForm()})

    def post(self, request, *args, **kwargs):
        form = AddMemberForm(request.POST)

        if form.is_valid():
            form.save()
            return redirect("members")

        return render(request, "members/add-member.html", {"form": form})


@method_decorator(login_required, name="dispatch")
class MembersListView(View):

    def get(self, request, *args, **kwargs):
        return render(request, "members/list-members.html",
                      {"members": Member.objects.all()})

    def post(self, request, *args, **kwargs):
        query = request.POST.get("query")
        members = Member.objects.filter(name__icontains=query)
        return render(request, "members/list-members.html",
                      {"members": members})


@method_decorator(login_required, name="dispatch")
class UpdateMemberDetailsView(View):

    def get(self, request, *args, **kwargs):
        member = Member.objects.get(pk=kwargs["pk"])
        form = UpdateMemberForm(instance=member)
        return render(request, "members/update-member.html",
                      {"form": form, "member": member})

    def post(self, request, *args, **kwargs):
        member = Member.objects.get(pk=kwargs["pk"])
        form = UpdateMemberForm(request.POST, instance=member)

        if form.is_valid():
            form.save()
            return redirect("members")

        return render(request, "members/update-member.html",
                      {"form": form, "member": member})


@method_decorator(login_required, name="dispatch")
class DeleteMemberView(View):

    def get(self, request, *args, **kwargs):
        Member.objects.get(pk=kwargs["pk"]).delete()
        return redirect("members")


# ================= BOOK =================

@method_decorator(login_required, name="dispatch")
class AddBookView(View):

    def get(self, request, *args, **kwargs):
        return render(request, "books/add-book.html",
                      {"form": AddBookForm()})

    def post(self, request, *args, **kwargs):
        form = AddBookForm(request.POST)

        if form.is_valid():
            book = form.save(commit=False)
            book.status = "available" if book.quantity > 0 else "not-available"
            book.save()
            return redirect("books")

        return render(request, "books/add-book.html", {"form": form})


@method_decorator(login_required, name="dispatch")
class BooksListView(View):

    def get(self, request, *args, **kwargs):
        return render(request, "books/list-books.html",
                      {"books": Book.objects.all()})

    def post(self, request, *args, **kwargs):
        query = request.POST.get("query")
        books = Book.objects.filter(
            Q(title__icontains=query) |
            Q(author__icontains=query)
        )
        return render(request, "books/list-books.html",
                      {"books": books})


# ================= ISSUE BOOK =================

@method_decorator(login_required, name="dispatch")
class LendBookView(View):

    def get(self, request, *args, **kwargs):
        return render(
            request,
            "books/lend-book.html",
            {"form": LendBookForm(), "payment_form": PaymentForm()},
        )

    def post(self, request, *args, **kwargs):
        form = LendBookForm(request.POST)
        payment_form = PaymentForm(request.POST)

        if form.is_valid() and payment_form.is_valid():

            lent_book = form.save(commit=False)

            issue_date = timezone.now().date()
            return_date = issue_date + timedelta(days=15)

            books_ids = request.POST.getlist("book")

            if not books_ids:
                return render(
                    request,
                    "books/lend-book.html",
                    {
                        "form": form,
                        "payment_form": payment_form,
                        "error": "Please select at least one book",
                    },
                )

            payment_method = payment_form.cleaned_data["payment_method"]

            amount = 0
            last_borrowed_book = None

            for book_id in books_ids:
                book = Book.objects.get(pk=book_id)

                borrowed_book = BorrowedBook.objects.create(
                    member=lent_book.member,
                    book=book,
                    issue_date=issue_date,
                    return_date=return_date,
                    fine=0,
                )

                last_borrowed_book = borrowed_book

                book.quantity -= 1
                book.save()

                amount += book.borrowing_fee

            Transaction.objects.create(
                member=lent_book.member,
                amount=amount,
                payment_method=payment_method,
            )

            return redirect("return-book-fine",
                            pk=last_borrowed_book.pk)

        return render(request, "books/lend-book.html",
                      {"form": form, "payment_form": payment_form})


# ================= RETURN BOOK =================

@method_decorator(login_required, name="dispatch")
class ReturnBookView(View):

    def get(self, request, *args, **kwargs):
        borrowed_book = BorrowedBook.objects.get(pk=kwargs["pk"])
        return redirect("return-book-fine", pk=borrowed_book.pk)


@method_decorator(login_required, name="dispatch")
class ReturnBookFineView(View):

    def get(self, request, *args, **kwargs):
        book = BorrowedBook.objects.get(pk=kwargs["pk"])
        return render(
            request,
            "books/return-book-fine.html",
            {"book": book, "form": PaymentForm()},
        )

    def post(self, request, *args, **kwargs):
        form = PaymentForm(request.POST)
        book = BorrowedBook.objects.get(pk=kwargs["pk"])

        if form.is_valid():

            if book.fine > 0:
                Transaction.objects.create(
                    member=book.member,
                    amount=book.fine,
                    payment_method=form.cleaned_data["payment_method"],
                )

            book.returned = True
            book.save()

            book.book.quantity += 1
            book.book.save()

            return redirect("lent-books")

        return render(
            request,
            "books/return-book-fine.html",
            {"book": book, "form": form},
        )

@method_decorator(login_required, name="dispatch")
class DeleteBookView(View):
    """
    Delete Book view for the library management system.
    """

    def get(self, request, *args, **kwargs):
        book = Book.objects.get(pk=kwargs["pk"])
        book.delete()
        logger.info("Book deleted successfully.")
        return redirect("books")
@method_decorator(login_required, name="dispatch")
class DeleteBorrowedBookView(View):

    def get(self, request, *args, **kwargs):
        borrowed_book = BorrowedBook.objects.get(pk=kwargs["pk"])

        book = borrowed_book.book
        book.quantity += 1
        book.save()

        borrowed_book.delete()

        return redirect("lent-books")
@method_decorator(login_required, name="dispatch")
class DeletePaymentView(View):
    """
    Delete Payment view for the library management system.
    """

    def get(self, request, *args, **kwargs):
        payment = Transaction.objects.get(pk=kwargs["pk"])
        payment.delete()
        return redirect("payments")
@method_decorator(login_required, name="dispatch")
class LentBooksListView(View):

    def get(self, request, *args, **kwargs):
        books = BorrowedBook.objects.select_related("member", "book")
        return render(request, "books/lent-books.html", {"books": books})

    def post(self, request, *args, **kwargs):
        query = request.POST.get("query")
        books = BorrowedBook.objects.filter(
            Q(book__title__icontains=query) |
            Q(book__author__icontains=query)
        ).select_related("member", "book")

        return render(request, "books/lent-books.html", {"books": books})
@method_decorator(login_required, name="dispatch")
class ListPaymentsView(View):

    def get(self, request, *args, **kwargs):
        payments = Transaction.objects.select_related("member")
        return render(request, "payments/list-payments.html", {"payments": payments})
