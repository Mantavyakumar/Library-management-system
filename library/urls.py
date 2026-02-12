from django.urls import path

from .views import (
    HomeView,
    AddMemberView,
    MembersListView,
    AddBookView,
    BooksListView,
    LendBookView,
    ReturnBookView,
    ReturnBookFineView,LentBooksListView
)

urlpatterns = [
    path("", HomeView.as_view(), name="home"),

    # MEMBER
    path("add-member/", AddMemberView.as_view(), name="add-member"),
    path("members/", MembersListView.as_view(), name="members"),

    # BOOK
    path("add-book/", AddBookView.as_view(), name="add-book"),
    path("books/", BooksListView.as_view(), name="books"),

    # ISSUE BOOK
    path("lend-book/", LendBookView.as_view(), name="lend-book"),
    path("lent-books/", LentBooksListView.as_view(), name="lent-books"),

    # RETURN + FINE
    path("return-book/<str:pk>/", ReturnBookView.as_view(), name="return-book"),
    path("return-book-fine/<str:pk>/", ReturnBookFineView.as_view(), name="return-book-fine"),
]
