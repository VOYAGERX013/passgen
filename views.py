from celestis.view import templates
from celestis.controller.request import redirect
from celestis.model import auth
from celestis.model.crud import Table
import os
import dotenv
import jwt
from urllib.parse import unquote
import random
import string

dotenv.load_dotenv()

def home(request):
    generated_password = ""
    strength = 0
    color = "Danger"

    if request["cookies"] is not None:
        for cookie in request["cookies"]:
            if cookie[0] == "auth":
                token = cookie[1]
                try:
                    print(token)
                    payload = jwt.decode(token.replace("\r", ""), os.getenv("SECRET_KEY"), algorithms=["HS256"])
                    email_id = payload["email"]
                    return templates.render_template(request, "/dashboard.html", {
                        "email": email_id
                    })
                except jwt.ExpiredSignatureError:
                    return templates.render_template(request, "/index.html")
            
            if cookie[0] == "random_pass":
                generated_password = cookie[1]
            
            if cookie[0] == "strength":
                strength = cookie[1]
                if float(strength) > 40 and float(strength) <= 60:
                    color = "Warning"
                elif float(strength) > 60:
                    color = "Success"

    return templates.render_template(request, "/index.html", {"password": generated_password, "strength": strength, "color": color})

def login(request):
    if request["method"] == "GET":
        return templates.render_template(request, "/login.html")
    
    elif request["method"] == "POST":
        users = Table("users", os.getcwd())
        record = users.find({
            "email": unquote(request["body"]["email"])
        })
        if record:
            if record["password"] == unquote(request["body"]["password"]):
                token = auth.gen_token(os.getenv("SECRET_KEY"), unquote(request["body"]["email"]))
                return redirect("/", [("auth", token)])

def register(request):
    if request["method"] == "GET":
        return templates.render_template(request, "/register.html")
    elif request["method"] == "POST":
        print(request["body"])
        users = Table("users", os.getcwd())
        users.add({
            "email": unquote(request["body"]["email"]),
            "password": request["body"]["password"]
        })

        return redirect("/login")

def get_strength(chars, conditions):
    print(chars * conditions * (100 / 400))
    return chars * conditions * (100 / 400)

def get_num_conditions(tup):
    count = 4
    for item in tup:
        if not item:
            count -= 1

    return count

def get_password(request):
    if request["method"] == "POST":
        has_numbers = "hasNumbers" in request["body"]
        has_lower = "hasLower" in request["body"]
        has_upper = "hasUpper" in request["body"]
        has_special = "hasSpecial" in request["body"]
        chars = int(request["body"]["characters"])

        password = ""
        pool = ""
        special_chars = "@!^%()<>"

        if has_numbers:
            pool += string.digits
        if has_lower:
            pool += string.ascii_lowercase
        if has_upper:
            pool += string.ascii_uppercase
        if has_special:
            pool += special_chars

        for i in range(chars):
            random_choice = random.choice(pool)
            password += str(random_choice)

        num_conditions = get_num_conditions((has_numbers, has_lower, has_upper, has_special))
        strength = get_strength(chars, num_conditions)

        return redirect("/", [("random_pass", password), ("strength", strength)])