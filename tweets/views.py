from django.http import HttpResponse, Http404, JsonResponse
from django.shortcuts import render

from .models import Tweet

# Create your views here.
def home_view(request, *args, **kwargs):
    return render(request, "pages/home.html", context={}, status=200)

def tweet_list_view(request, *args, **kwargs):
    """
    REST API VIEW
    returns Json data
    """
    querySet = Tweet.objects.all()
    tweet_list = [{ "id": tweet.id, "content": tweet.content} for tweet in querySet]

    data = {
        "response": tweet_list,
        "status": 200,
    }
    return JsonResponse(data)

def tweet_detail_view(request, tweet_id, *args, **kwargs):
    """
    REST API VIEW
    returns Json data
    """
    data = {"id": tweet_id, }
    try:
        obj = Tweet.objects.get(id=tweet_id)
        data['content'] = obj.content
        status = 200
    except:
        data['message'] = 'Not found'
        status = 404
    return JsonResponse(data, status=status)