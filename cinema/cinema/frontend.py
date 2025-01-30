from django.shortcuts import render



def cienema_page(request):
    return render(request, "cinemas.html")



def halls(request):
    return render(request, "halls.html")


def moveies(request):
    return render(request,"movies.html")

def seats(request):
    return render(request , "seats.html")