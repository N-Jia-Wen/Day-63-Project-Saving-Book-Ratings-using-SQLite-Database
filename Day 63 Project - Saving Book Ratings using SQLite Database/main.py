from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Integer, String, Float
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


app = Flask(__name__)


class Base(DeclarativeBase):
    pass


app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///new-books-collection.db"
database = SQLAlchemy(model_class=Base)
database.init_app(app)


class Book(database.Model):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(250), unique=True, nullable=False)
    author: Mapped[str] = mapped_column(String(250), nullable=False)
    rating: Mapped[float] = mapped_column(Float, nullable=False)


with app.app_context():
    database.create_all()


@app.route('/')
def home():
    result = database.session.execute(database.select(Book).order_by(Book.title))
    all_books = result.scalars()
    return render_template("index.html", books_data=all_books)


@app.route("/add", methods=["GET", "POST"])
def add():
    if request.method == "POST":
        new_book = Book(title=request.form["title"], author=request.form["author"], rating=request.form["rating"])
        database.session.add(new_book)
        database.session.commit()

        return redirect(url_for('home'))
    else:
        return render_template("add.html")


@app.route("/edit", methods=["GET", "POST"])
def edit():
    if request.method == "POST":
        book_id = request.form["book_id"]
        book_to_update = database.get_or_404(Book, book_id)
        book_to_update.rating = request.form["new_rating"]
        database.session.commit()
        return redirect(url_for('home'))
    else:
        book_id = request.args["book_id"]
        book_to_update = database.get_or_404(Book, book_id)
        return render_template("edit.html", book=book_to_update)


@app.route("/delete")
def delete():
    book_id = request.args["book_id"]
    book_to_delete = database.get_or_404(Book, book_id)
    database.session.delete(book_to_delete)
    database.session.commit()
    return redirect(url_for('home'))


if __name__ == "__main__":
    app.run()
