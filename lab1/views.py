from django.shortcuts import redirect, render, get_object_or_404
from .models import URL
from lab1.forms import URLForm
from django.http import HttpResponseRedirect
import requests
from bs4 import BeautifulSoup
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth import views as auth_views
import datetime
from memento_client import MementoClient
from django.conf import settings
import requests
from lab1.models import URL
from urllib import request as urllibreq
import json
import boto3
from ratelimit.decorators import ratelimit
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from lab1.serializers import URLSerializer

mc = MementoClient()
api_key = ''

@ratelimit(key="ip", rate="10/m", block=True)
@login_required(login_url="/lab3/accounts/login/")
def url_list(request):
	if request.method == "POST":
		form = URLForm(request.POST)
		if form.is_valid():
			post = form.save(commit = False)
			# Runs when URL is correct
			try:
				response = requests.get(post)
				page = BeautifulSoup(response.content)
				if page.title is not None:
					title = page.title.string
				else:
					title = "No Title Available"
				post.status = response.status_code
				post.final_url = response.url
				post.title = title
				# Wayback storing
				current_date = datetime.datetime.now()
				mc = MementoClient()
				wayback_res = mc.get_memento_info(response.url, current_date).get("mementos").get("closest")
				post.wayback = wayback_res.get("uri")[0]
				if wayback_res.get("datetime") is not None:
					post.wayback_date = str(wayback_res.get("datetime"))
				else:
					post.wayback_date = str(current_date)
				s3connection = boto3.resource("s3")
				# For image with PhahtomJS
				data = json.dumps({"url":response.url, "renderType":"jpeg"}).encode("utf-8")
				headers = {"content-type": "application/json"}
				api_url = "http://PhantomJScloud.com/api/browser/v2/" + api_key + "/"
				req = urllibreq.Request(url=api_url, data=data, headers=headers)
				res = urllibreq.urlopen(req)
				result = res.read()
				s3connection.Bucket("stants5lab3").put_object(Key=str(current_date) + ".jpg", Body=result, ACL="public-read", ContentType="image/jpeg")
				# publicly accessible link to the image
				pic_url = "http://s3.amazonaws.com/stants5lab3/" + str(current_date) + ".jpg"
				post.archive_link = pic_url
			# Sets up error message
			except Exception as e:
				post.status = "None"
				post.final_url = "Does not exist"
				post.title = "This webpage does not exist"
				post.wayback = "Not available"
				post.wayback_date = "Not available"
				post.archive_link = e
			finally:
				post.save()
				return redirect('url_detail', pk = post.pk)
	else:
		urls = URL.objects.all()
		form = URLForm
	return render(request, 'lab1/url_list.html', {'urls': urls, 'form': URLForm})


@ratelimit(key="ip", rate="10/m", block=True)
@login_required(login_url="/lab3/accounts/login/")
def url_detail(request, pk):
	url = get_object_or_404(URL, pk = pk)
	return render(request, 'lab1/url_detail.html', {'url': url})

@ratelimit(key="ip", rate="10/m", block=True)
@login_required(login_url="/lab3/accounts/login/")
def url_delete(request, pk):
	url = get_object_or_404(URL, pk = pk)
	url_key = url.archive_link

	s3connection = boto3.client("s3")
	exists = False
	try:
		s3connection.get_object(Bucket="stants5lab3", Key=url_key)
	except:
		exists = False
	finally:
		if exists is not False:
			exists = True
	# If the img exists within the bucket, delete it from S3
	if exists is True:
		s3connection.delete_object(Bucket="stants5lab3", Key=url_key)
	# Remove the URL data from the database
	url.delete()
	return	HttpResponseRedirect('../')

# Handles logging a user out
def logout_view(request):
	logout(request)
	return redirect('login')

# GET a list of all current URLs or POST a new URL
@ratelimit(key="ip", rate="10/m", block=True)
@login_required(login_url="/lab3/accounts/login/")
@api_view(["GET", "POST"])
def list_urls(request, format=None):
	if request.method == "GET":
		urls = URL.objects.all()
		serializer = URLSerializer(urls, many = True)
		return Response(serializer.data)
	elif request.method == "POST":
		serializer = URLSerializer(data = request.data)
		if serializer.is_valid():
			serializer.save()
			return Response(serializer.data, status = status.HTTP_201_CREATED)
	else:
		return Response(status = status.HTTP_400_BAD_REQUEST)

# GET a specific URL or DELETE a specific URL
@ratelimit(key="ip", rate="10/m", block=True)
@login_required(login_url="/lab3/accounts/login/")
@api_view(["GET", "DELETE"])
def detail_url(request, pk, format=None):
	try:
		url = URL.objects.get(pk = pk)
	except URL.DoesNotExist:
		return Response(status = status.HTTP_404_NOT_FOUND)
	if request.method == "GET":
		serializer = URLSerializer(url, many = True)
		return Response(serializer.data)
	elif request.method == "DELETE":
		url.delete()
		return Response(status = status.HTTP_204_NO_CONTENT)
	else:
		return Response(status = status.HTTP_400_BAD_REQUEST)


