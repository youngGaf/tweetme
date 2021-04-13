import random
from django.conf import settings
from django.http import HttpResponse, Http404, JsonResponse
from django.shortcuts import render, redirect
from django.utils.http import is_safe_url

from rest_framework.response import Response
from rest_framework.authentication import SessionAuthentication
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated

from .forms import TweetForm
from .models import Tweet
from .serializers import TweetSerializer, TweetActionSerializer

ALLOWED_HOSTS = settings.ALLOWED_HOSTS

# Create your views here.
def home_view(request, *args, **kwargs):
    return render(request, "pages/home.html", context={}, status=200)

@api_view(['POST']) # http method from client == POST
# @authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated]) # Set permissions to access API
def tweet_create_view(request, *args, **kwargs):
    serializer = TweetSerializer(data=request.POST)
    if(serializer.is_valid(raise_exception=True)):
        serializer.save(user=request.user)
        return Response(serializer.data, status=201)
    return Response({}, status=400)

@api_view(['GET'])
def tweet_list_view(request, *args, **kwargs):
    querySet = Tweet.objects.all()
    serializer = TweetSerializer(querySet, many=True)
    return Response(serializer.data, status=200)

@api_view(['GET'])
def tweet_detail_view(request, tweet_id, *args, **kwargs):
    qs = Tweet.objects.filter(id=tweet_id)
    if not qs.exists():
        return Response({}, status=404)
    obj = qs.first()
    serializer = TweetSerializer(obj)
    return Response(serializer.data, status=200)

@api_view(['DELETE', 'POST'])
@permission_classes([IsAuthenticated])
def tweet_delete_view(request, tweet_id, *args, **kwargs):
    qs = Tweet.objects.filter(id=tweet_id)
    if not qs.exists():
        return Response({}, status=404)
    qs = qs.filter(user=request.user)
    if not qs.exists():
        return Response({'message': 'You cannot delete this tweet'}, status=403)
    obj = qs.first()
    obj.delete()
    return Response({'message': 'Tweet successfully removed!'}, status=200)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def tweet_action_view(request, *args, **kwargs):
    '''
    id is required
    Action options are: like, unlike and retweet
    '''
    serializer = TweetActionSerializer(data=request.data)
    if serializer.is_valid(raise_exception=True):
        data =serializer.validated_data
        tweet_id = data.get('id')
        action = data.get('action')
        # check if tweet exists and set as obj
        qs = Tweet.objects.filter(id=tweet_id)
        if not qs.exists():
            return Response({}, status=404)
        obj = qs.first()

        # carryout specified action 
        if action == 'like':
            obj.likes.add(request.user)
            serializer = TweetSerializer(obj)
            return Response(serializer.data, status=200)
        elif action == 'unlike':
            obj.likes.remove(request.user)
        elif action == 'retweet':
            #Todo
            pass
        return Response({}, status=200)


# ======================= PURE DJANGO ================================#
def tweet_list_view_pure_django(request, *args, **kwargs):
    """
    REST API VIEW
    returns Json data
    """
    querySet = Tweet.objects.all()
    tweet_list = [ tweet.serialize() for tweet in querySet]

    data = {
        "isUser": False,
        "response": tweet_list,
        "status": 200,
    }
    return JsonResponse(data)

def tweet_create_view_pure_django(request, *args, **kwargs):
    user  = request.user

    if not request.user.is_authenticated:
        user = None
        if request.is_ajax():
            return JsonResponse({}, status=401)
        return redirect(settings.LOGIN_URL)

    form = TweetForm(request.POST or None)
    next_url = request.POST.get('next') or None

    if form.is_valid():
        obj = form.save(commit=False)
        obj.user = user
        obj.save()
        if request.is_ajax():
            return JsonResponse(obj.serialize(), status=201) #created status
        if next_url != None and is_safe_url(next_url, ALLOWED_HOSTS):
            return redirect(next_url)
        form = TweetForm()

    if(form.errors):
        if(request.is_ajax()):
            return JsonResponse(form.errors, status=400)
    return render(request, 'components/form.html', context={"form": form})

def tweet_detail_view_pure_django(request, tweet_id, *args, **kwargs):
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