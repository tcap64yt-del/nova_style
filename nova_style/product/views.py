from django.shortcuts import render



def product_list(request):
    return render(request,'product/product_list.html')

def product_details(request):
    return render(request,"product/product_details.html")

