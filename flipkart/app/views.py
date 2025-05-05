from django.shortcuts import render, redirect, get_object_or_404
from .models import (
    UserProfile,
    Products,
    Carts,
    Orders,
    Payments,
    Categories,
    Wishlist,
    Address,
)
from django.contrib.auth.models import User

# Create your views here.


def index(req):
    allproducts = Products.objects.all()
    print(allproducts)
    allcategories = Categories.objects.all()
    print(allcategories)
    return render(
        req, "index.html", {"allproducts": allproducts, "allcategories": allcategories}
    )


from django.core.exceptions import ValidationError


def validate_password(password):
    if len(password) < 8 or len(password) > 128:
        raise ValidationError(
            "Password must be atleast 8 character long and less than 128"
        )

    has_upper = False
    has_lower = False
    has_digit = False
    has_special = False
    specialchars = "@$!%*?&"

    for char in password:
        if char.isupper():
            has_upper = True
        elif char.islower():
            has_lower = True
        elif char.isdigit():
            has_digit = True
        elif char in specialchars:
            has_special = True

    if not has_upper:
        raise ValidationError("Password must contain at least one uppercase letter")

    if not has_lower:
        raise ValidationError("Password must contain at least one lowercase letter")

    if not has_digit:
        raise ValidationError("Password must contain at least one digit letter")

    if not has_special:
        raise ValidationError(
            "Password must contain at least one special char (e.g. @$!%*?&)"
        )

    commonpassword = ["password", "123456", "qwerty", "abc123"]
    if password in commonpassword:
        raise ValidationError("This password is too common. Please choose another one.")


def signup(req):
    if req.method == "GET":
        print(req.method)  # GET
        return render(req, "signup.html")
    else:
        print(req.method)  # POST
        uname = req.POST["uname"]
        uemail = req.POST["uemail"]
        upass = req.POST["upass"]
        ucpass = req.POST["ucpass"]
        print(uname, upass, ucpass, uemail)
        context = {}
        try:
            validate_password(upass)
        except ValidationError as e:
            context["errmsg"] = str(e)
            return render(req, "signup.html", context)

        if upass != ucpass:
            errmsg = "Password and Confirm password must be same"
            context = {"errmsg": errmsg}
            return render(req, "signup.html", context)
        elif uname == upass:
            errmsg = "Password should not be same as email id"
            context = {"errmsg": errmsg}
            return render(req, "signup.html", context)
        else:
            try:
                userdata = User.objects.create(
                    username=uname, email=uemail, password=upass
                )
                userdata.set_password(upass)
                userdata.save()
                print(User.objects.all())
                return redirect("signin")
            except:
                errmsg = "User already exists. Try with different username"
                context = {"errmsg": errmsg}
                return render(req, "signup.html", context)


from django.contrib.auth import authenticate, login, logout


def signin(req):
    if req.method == "GET":
        print(req.method)
        return render(req, "signin.html")
    else:
        uname = req.POST.get("uname")
        uemail = req.POST.get("uemail")
        upass = req.POST["upass"]
        print(uname, uemail, upass)
        # userdata = User.objects.filter(email=uemail, password=upass)
        userdata = authenticate(username=uname, email=uemail, password=upass)
        print(userdata)  # if matched with user then it show its id
        if userdata is not None:
            login(req, userdata)
            # return render(req, "dashboard.html")
            return redirect("/")
        else:
            context = {}
            context["errmsg"] = "Invalid email or password"
            return render(req, "signin.html", context)


def userlogout(req):
    logout(req)
    return redirect("/")


from django.core.mail import send_mail
from django.conf import settings
import random
from django.contrib import messages


def req_password(req):
    if req.method == "POST":
        uemail = req.POST["uemail"]
        try:
            user = User.objects.get(email=uemail)
            print(user.email, user)

            userotp = random.randint(1111, 999999)
            req.session["otp"] = userotp  # store otp into session

            subject = "PetStore- OTP for Reset Password"
            msg = f"Hello {user}\n Your OTP to reset password is:{userotp}\n Thank You for using our services."
            emailfrom = settings.EMAIL_HOST_USER
            receiver = [user.email]
            send_mail(subject, msg, emailfrom, receiver)

            return redirect("reset_password", uemail=user.email)

        except User.DoesNotExist:
            messages.error(req, "No account found with this email id.")
            return render(req, "req_password.html")
    else:
        return render(req, "req_password.html")


def reset_password(req, uemail):
    user = User.objects.get(email=uemail)
    print(user)
    if req.method == "POST":
        otp_entered = req.POST["otp"]
        upass = req.POST["upass"]
        ucpass = req.POST["ucpass"]
        userotp = req.session.get("otp")
        print(userotp, type(userotp))
        print(otp_entered, type(otp_entered), upass, ucpass)

        if int(otp_entered) != int(userotp):
            messages.error(req, "OTP does not match! Try Again.")
            return render(req, "reset_password.html", {"uemail": uemail})

        elif upass != ucpass:
            messages.error(req, "Confirm password and password do not match.")
            return render(req, "reset_password.html", {"uemail": uemail})

        else:
            try:
                validate_password(upass)
                user.set_password(upass)
                user.save()
                return redirect("signin")
            except ValidationError as e:
                messages.error(req, str(e))
                return render(req, "reset_password.html", {"uemail": uemail})
    else:
        return render(req, "reset_password.html", {"uemail": uemail})


def about(req):
    return render(req, "about.html")


def contact(req):
    if req.method == "POST":
        uname = req.POST["uname"]
        umobile = req.POST["umobile"]
        uemail = req.POST["uemail"]
        msg = req.POST["msg"]
        print(uname, umobile, uemail, msg)

        subject = "My Query"
        msg = f"Hello Team, {msg}."
        emailfrom = settings.EMAIL_HOST_USER
        receiver = [uemail]
        send_mail(subject, msg, emailfrom, receiver)

        return redirect("/")
    else:
        return render(req, "contact.html")


from django.contrib import messages
from django.db.models import Q


def searchproduct(req):
    query = req.GET["q"]
    if query:
        allproducts = Products.objects.filter(
            Q(productname__icontains=query) | Q(description__icontains=query)
        )
        if len(allproducts) == 0:
            messages.error(req, "No result found!!")
    else:
        allproducts = Products.objects.all()

    context = {"allproducts": allproducts}
    return render(req, "index.html", context)


def electronics_search(req):
    if req.method == "GET":
        # ele_category = Categories.objects.filter(name="Electronics").first()
        # ele_category = Categories.objects.get(name="Electronics")  # (=) for single row
        # print("ele=", ele_category)
        # allproducts = Products.objects.filter(categories=ele_category)  # many rows
        # print("all ele=", allproducts)

        allproducts = Products.productmanager.electronics_list()
        print(allproducts)

        if len(allproducts) == 0:
            messages.error(req, "No result found!")

        allcategories = Categories.objects.all()
        print(allcategories)
        context = {"allproducts": allproducts, "allcategories": allcategories}
        return render(req, "index.html", context)


def cloths_search(req):
    if req.method == "GET":
        allproducts = Products.productmanager.cloths_list()
        print(allproducts)

        if len(allproducts) == 0:
            messages.error(req, "No result found!")

        allcategories = Categories.objects.all()
        print(allcategories)
        context = {"allproducts": allproducts, "allcategories": allcategories}
        return render(req, "index.html", context)


def shoes_search(req):
    if req.method == "GET":
        allproducts = Products.productmanager.shoes_list()
        print(allproducts)

        if len(allproducts) == 0:
            messages.error(req, "No result found!")

        allcategories = Categories.objects.all()
        print(allcategories)
        context = {"allproducts": allproducts, "allcategories": allcategories}
        return render(req, "index.html", context)


def serchby_pricerange(req):
    if req.method == "GET":
        return render(req, "index.html")
    else:
        r1 = req.POST["min"]
        r2 = req.POST["max"]
        print(r1, r2)
        if r1 is not None and r2 is not None and r1.isdigit() and r2.isdigit():
            allproducts = Products.productmanager.pricerange(r1, r2)
            # allproducts=Products.objects.filter(price__range=(r1,r2))
            allcategories = Categories.objects.all()
            print(allcategories)
            if len(allproducts) == 0:
                messages.error(req, "No result found!")
            context = {"allproducts": allproducts, "allcategories": allcategories}
            return render(req, "index.html", context)
        else:
            allproducts = Products.objects.all()
            allcategories = Categories.objects.all()
            context = {"allproducts": allproducts, "allcategories": allcategories}
            return render(req, "index.html", context)


def sortingbyprice(req):
    sortoption = req.GET["sort"]
    if sortoption == "low_to_high":
        allproducts = Products.objects.order_by("price")  # asc order
    elif sortoption == "high_to_low":
        allproducts = Products.objects.order_by("-price")  # desc order
    else:
        allproducts = Products.objects.all()

    allcategories = Categories.objects.all()
    context = {"allproducts": allproducts, "allcategories": allcategories}
    return render(req, "index.html", context)


def productdetail(req, productid):
    product = Products.objects.get(productid=productid)
    context = {"product": product}
    return render(req, "productdetail.html", context)


def showwishlist(req):
    if req.user.is_authenticated:
        userid = req.user
        wishlist_items = Wishlist.objects.filter(userid=userid)
        context = {"wishlist_items": wishlist_items}
        return render(req, "showwishlist.html", context)
    else:
        return redirect("signin")


def addtowishlist(req, productid):
    if req.user.is_authenticated:
        userid = req.user
        product = get_object_or_404(Products, productid=productid)

        if not Wishlist.objects.filter(userid=userid, productid=productid).exists():
            Wishlist.objects.create(userid=userid, productid=product)
            messages.success(req, "Product added to wishlist")
        else:
            messages.info(req, "Product is already in wishlist")

        return redirect("showwishlist")
    else:
        messages.error(req, "You need to log in to add product to your wishlist")
        return redirect("signin")


def removefromwishlist(req, productid):
    if req.user.is_authenticated:
        userid = req.user
        product = get_object_or_404(Products, productid=productid)
        wishlist_item = Wishlist.objects.filter(userid=userid, productid=product)
        wishlist_item.delete()
        messages.success(req, "Product removed from wishlist")
        return redirect("showwishlist")
    else:
        messages.error(req, "You need to log in to add product to your wishlist")
        return redirect("signin")


from django.utils import timezone
from datetime import timedelta


def showcarts(req):
    if req.user.is_authenticated:
        userid = req.user
        allcarts = Carts.objects.filter(userid=userid)

        totalitems = allcarts.count()
        totalamount = sum(x.productid.price * x.qty for x in allcarts)

        has_profile = UserProfile.objects.filter(userid=userid).exists()
        has_address = Address.objects.filter(userid=userid).exists()

        estimated_delivery = timezone.now().date() + timedelta(days=5)

        context = {
            "allcarts": allcarts,
            "userid": userid,
            "totalitems": totalitems,
            "totalamount": totalamount,
            "has_profile": has_profile,
            "has_address": has_address,
            "date": estimated_delivery,
        }
        return render(req, "showcarts.html", context)
    else:
        messages.error(req, "You need to log in to add product to your wishlist")
        return redirect("signin")


def updateqty(req, qv, productid):
    product = get_object_or_404(Products, productid=productid)
    allcarts = Carts.objects.filter(productid=productid, userid=req.user)

    cart_item = allcarts.first()
    if qv == 1:
        if cart_item.qty < product.quantity_available:
            cart_item.qty += 1
            cart_item.save()
        else:
            messages.error(req, "Only limited stock available")
    else:
        if cart_item.qty > 1:
            cart_item.qty -= 1
            cart_item.save()
        else:
            cart_item.delete()
    return redirect("showcarts")


def removefromcart(req, productid):
    if req.user.is_authenticated:
        userid = req.user
        product = get_object_or_404(Products, productid=productid)
        cart_item = Carts.objects.filter(userid=userid, productid=product)
        cart_item.delete()
        messages.success(req, "Product removed from carts")
        return redirect("showcarts")
    else:
        messages.error(req, "You need to log in to add product to your cart")
        return redirect("signin")


def addtocart(req, productid):
    if req.user.is_authenticated:
        userid = req.user
        product = get_object_or_404(Products, productid=productid)
        cartitem, created = Carts.objects.get_or_create(
            userid=userid, productid=product
        )
        new_qty = cartitem.qty + 1 if not created else 1

        if new_qty > product.quantity_available:
            messages.error(req, "Cannot add more items- only limited stock available")
            return redirect("showcarts")

        cartitem.qty = new_qty
        cartitem.save()
        return redirect("showcarts")
    else:
        messages.error(req, "You need to log in to add product to your cart")
        return redirect("signin")


from .forms import UserProfileForm, AddressForm

# def addprofile(req):
#     if req.method=="POST":
#         form=UserProfileForm(req.POST,req.FILES)
#         if form.is_valid():
#             profile=form.save(commit=False)
#             profile.userid=req.user
#             profile.save()
#             return redirect("showcarts")
#     else:
#         form=UserProfileForm()

#     return render(req,'addprofile.html',{'form':form})

from datetime import datetime


def addprofile(req):
    user = req.user
    if not user.is_authenticated:
        return redirect("signin")

    if req.method == "POST":
        mobile = req.POST["mobile"]
        gender = req.POST["gender"]
        dob = req.POST["dob"]
        photo = req.FILES["photo"]

        if dob:
            dob_date = datetime.strptime(dob, "%Y-%m-%d").date()
            today = timezone.now().date()
            if dob_date >= today:
                messages.error(req, "Date of Birth cannot be todays or future date")

            age = (
                today.year
                - dob_date.year
                - ((today.month, today.day) < (dob_date.month, dob_date.day))
            )
            print(age)
            if age < 18:
                messages.error(
                    req, "You must be at least 18 years old to create profile"
                )
                return render(req, "addprofile.html")

        UserProfile.objects.create(
            userid=user, mobile=mobile, gender=gender, dob=dob, photo=photo
        )
        return redirect("myprofile")
    else:
        return render(req, "addprofile.html")


def myprofile(req):
    user = req.user
    if not user.is_authenticated:
        return redirect("signin")

    userprofile = UserProfile.objects.filter(userid=user).first()
    addresses = Address.objects.filter(userid=user)
    context = {"userid": user, "userprofile": userprofile, "addresses": addresses}
    return render(req, "myprofile.html", context)


# def addaddress(req):
#     if req.method == "POST":
#         form = AddressForm(req.POST)
#         if form.is_valid():
#             address = form.save(commit=False)
#             address.userid = req.user
#             address.save()
#             return redirect("showcarts")
#     else:
#         form = AddressForm()

#     return render(req, "addaddress.html", {"form": form})


def editprofile(req, profileid):
    profile = get_object_or_404(UserProfile, id=profileid)
    if req.method == "POST":
        profile.mobile = req.POST["mobile"]
        profile.gender = req.POST["gender"]
        profile.dob = req.POST["dob"]
        if req.FILES["photo"]:
            profile.photo = req.FILES["photo"]
        profile.save()
        return redirect("myprofile")
    return render(req, "editprofile.html", {"userprofile": profile})


def deleteprofile(req, profileid):
    profile = get_object_or_404(UserProfile, id=profileid)
    profile.delete()
    return redirect("myprofile")


from .models import City, Country


def addaddress(req):
    user = req.user
    if not user.is_authenticated:
        return redirect("signin")

    if req.method == "POST":
        address = req.POST["address"]
        city = req.POST["city"]
        country = req.POST["country"]
        pincode = req.POST["pincode"]
        Address.objects.create(
            userid=user,
            address=address,
            city_id=city,
            country_id=country,
            pincode=pincode,
        )  # city_id(id is pk of city)
        return redirect("myprofile")

    cities = City.objects.all()
    countries = Country.objects.all()
    context = {"cities": cities, "countries": countries}
    return render(req, "addaddress.html", context)


def deleteaddress(req, addressid):
    address = get_object_or_404(Address, id=addressid)
    address.delete()
    return redirect("myprofile")


def editaddress(req, addressid):
    address = get_object_or_404(Address, id=addressid)
    if req.method == "POST":
        address.address = req.POST["address"]
        city_id = req.POST["city"]
        country_id = req.POST["country"]
        address.pincode = req.POST["pincode"]

        if city_id:
            address.city_id = city_id

        if country_id:
            address.country_id = country_id

        address.save()
        return redirect("myprofile")

    citites = City.objects.all()
    countries = Country.objects.all()
    context = {"address": address, "cities": citites, "countries": countries}
    return render(req, "editaddress.html", context)


def checkout(req):
    if not req.user.is_authenticated:
        return redirect("signin")

    cart_item = Carts.objects.filter(userid=req.user)
    if not cart_item.exists():
        return redirect("showcarts")

    cartdata = []
    total = 0
    for item in cart_item:
        subtotal = item.qty * item.productid.price
        cartdata.append(
            {
                "productname": item.productid.productname,
                "qty": item.qty,
                "price": item.productid.price,
                "subtotal": subtotal,
            }
        )

        total += subtotal

    req.session["total"] = total
    profile = UserProfile.objects.filter(userid=req.user).first()
    return render(
        req,
        "checkout.html",
        {
            "cartdata": cartdata,
            "profile": profile,
            "address": Address.objects.filter(userid=req.user),
            "total": total,
            "mobile": profile.mobile,
            "userid": req.user,
            "email": req.user.email,
        },
    )


def checkoutsingle(req, productid):
    user = req.user
    address = Address.objects.filter(userid=user)
    cartitem = Carts.objects.get(userid=user, productid__productid=productid)
    cartdata = [
        {
            "productid":cartitem.productid.productid,
            "productname": cartitem.productid.productname,
            "qty": cartitem.qty,
            "price": cartitem.productid.price,
            "subtotal": cartitem.qty * cartitem.productid.price,
        }
    ]
    total = cartdata[0]["subtotal"]
    req.session["total"] = total
    profile = UserProfile.objects.filter(userid=user).first()
    return render(
        req,
        "checkout.html",
        {
            "cartdata": cartdata,
            "profile": profile,
            "address": address,
            "total": total,
            "mobile": profile.mobile,
            "userid": req.user,
            "email": req.user.email,
        },
    )

import razorpay
from django.conf import settings
def placeorder(req):
    if req.method=="POST":
        user=req.user
        address_id=req.POST["address_id"]
        address=get_object_or_404(Address,id=address_id,userid=user)
        profile=UserProfile.objects.filter(userid=user).first()
        product_id = req.POST.get("product_id")
        cartdata=[]
        total=0
        if product_id:
            cartitem = get_object_or_404(Carts, userid=user, productid__productid=product_id)
            subtotal = cartitem.qty * cartitem.productid.price
            total += subtotal
            cartdata.append({
                "productname": cartitem.productid.productname,
                "qty": cartitem.qty,
                "price": cartitem.productid.price,
                "subtotal": subtotal,
            })
        else:
            cart_items = Carts.objects.filter(userid=user)
            for item in cart_items:
                subtotal = item.qty * item.productid.price
                total += subtotal
                cartdata.append({
                    "productname": item.productid.productname,
                    "qty": item.qty,
                    "price": item.productid.price,
                    "subtotal": subtotal,
                })
        amount_paise=total*100   
        client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID,settings.RAZORPAY_KEY_SECRET))
        razorpay_order = client.order.create({
            'amount':amount_paise,
            'currency':'INR',
            'payment_capture':1
        }
        ) # Amount is in currency subunits. Default currency is INR. Hence, 50000 refers to 50000 paise
        
        return render(req,'payment.html',
                      {
                       'profile':profile,
                       'address':address,
                       'cartdata':cartdata,
                       'total':total,
                       'razorpay_key':settings.RAZORPAY_KEY_ID,
                       'order_id':razorpay_order['id'],
                       'amount':amount_paise,
                       'user':user,
                       
                      })
    return redirect('checkout')



from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import json
from datetime import date
from .models import Orders, Payments, Carts


from razorpay.errors import SignatureVerificationError

@csrf_exempt
def payment(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            print("Parsed data:", data)

            # Extract values from payload
            payment_id = data.get("razorpay_payment_id")
            order_id = data.get("razorpay_order_id")
            razorpay_signature = data.get("razorpay_signature")  # ✅ Define it here

            if not all([payment_id, order_id, razorpay_signature]):
                return JsonResponse({"status": "missing_data"}, status=400)

            # Set up Razorpay client and verify signature
            client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
            params_dict = {
                'razorpay_order_id': order_id,
                'razorpay_payment_id': payment_id,
                'razorpay_signature': razorpay_signature
            }

            try:
                # Verify signature
                client.utility.verify_payment_signature(params_dict)
                user = request.user
                profile = UserProfile.objects.get(userid=user)
                address = Address.objects.filter(userid=user).first()
                cart_items = Carts.objects.filter(userid=user)

                for item in cart_items:
                    order = Orders.objects.create(
                        userid=user,
                        productid=item.productid,
                        qty=item.qty,
                        orderdate=datetime.now(),
                        address=address,
                        payment_status="PAID"
                    )
                    Payments.objects.create(
                        orderid=order,
                        userid=user,
                        productid=item.productid,
                        payment_mode="Online",
                        payment_status="DONE"
                    )
                request.session['order_id'] = order_id
                request.session['payment_id'] = payment_id
                request.session['amount'] = client.order.fetch(order_id)['amount']
                cart_items.delete()

                # return redirect('payment_success')
                return JsonResponse({"status": "success", "redirect_url": "/payment_success/"})
                # return redirect(f'/payment_success/?order_id={order_id}&payment_id={payment_id}&amount={amount}')

            except SignatureVerificationError:
                return JsonResponse({"status": "invalid_signature"}, status=400)

        except json.JSONDecodeError:
            return JsonResponse({"status": "invalid_json"}, status=400)

    return JsonResponse({"status": "invalid_method"}, status=405)


def payment_success(req):
    order_id = req.session.get('order_id')
    payment_id = req.session.get('payment_id')
    amount = req.session.get('amount')

    user = req.user

    return render(req, 'payment_success.html', {
        'order_id': order_id,
        'payment_id': payment_id,
        'amount': float(amount) / 100,  # convert paise to INR
        'user': user
    })

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import Orders

def showorders(request):
    user = request.user
    orders = Orders.objects.filter(userid=user).select_related('productid', 'address').order_by('-orderdate')

    # Add total price and payment details to each order
    for order in orders:
        order.total_price = order.qty * order.productid.price
        # Fetch related payment information (assuming 1-to-1 relation between Orders and Payments)
        payment = Payments.objects.filter(orderid=order).first()
        if payment:
            order.payment_mode = payment.payment_mode
            order.payment_status = payment.payment_status
        else:
            order.payment_mode = "Not Available"
            order.payment_status = "Not Paid"

    return render(request, 'showorders.html', {
        'orders': orders
    })
