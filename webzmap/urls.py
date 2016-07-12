"""webzmap URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.9/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url, include
from django.contrib import admin

from core.models import Job, WhiteListFile, BlackListFile, Command
from rest_framework import routers, serializers, viewsets


# Serializers define the API representation.
class JobSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Job
        fields = (
            'url', 'id', 'name', 'port', 'status', 'bandwidth', 'verbosity', 'priority', 'creation_time', 'pid',
            'read_time',
            'time_elapsed',
            'time_remaining', 'percent_complete', 'active_send_threads', 'sent_total', 'sent_last_one_sec',
            'sent_avg_per_sec', 'recv_success_total', 'recv_success_last_one_sec', 'recv_success_avg_per_sec',
            'recv_total',
            'recv_total_last_one_sec', 'recv_total_avg_per_sec', 'pcap_drop_total', 'drop_last_one_sec',
            'drop_avg_per_sec',
            'sendto_fail_total', 'sendto_fail_last_one_sec', 'sendto_fail_avg_per_sec', 'white_list_file',
            'black_list_file')
        # fields = '__all__'
        # exclude = ('output_path', 'log_path', 'status_path')
        read_only_fields = (
            'id', 'status', 'creation_time', 'pid', 'read_time', 'time_elapsed', 'time_remaining', 'percent_complete',
            'active_send_threads', 'sent_total', 'sent_last_one_sec', 'sent_avg_per_sec',
            'recv_success_total',
            'recv_success_last_one_sec', 'recv_success_avg_per_sec', 'recv_total',
            'recv_total_last_one_sec',
            'recv_total_avg_per_sec', 'pcap_drop_total', 'drop_last_one_sec', 'drop_avg_per_sec',
            'sendto_fail_total', 'sendto_fail_last_one_sec', 'sendto_fail_avg_per_sec')


class WhiteListFileSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = WhiteListFile
        fields = "__all__"
        read_only_fields = ('size',)
        extra_kwargs = {'file': {'write_only': True}}


class BlackListFileSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = BlackListFile
        fields = "__all__"
        read_only_fields = ('size',)
        extra_kwargs = {'file': {'write_only': True}}


class CommandSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Command
        fields = "__all__"
        read_only_fields = ('creation_time',)


# ViewSets define the view behavior.
class JobViewSet(viewsets.ModelViewSet):
    queryset = Job.objects.all().order_by('-creation_time')
    serializer_class = JobSerializer


class WhiteListFileViewSet(viewsets.ModelViewSet):
    queryset = WhiteListFile.objects.all()
    serializer_class = WhiteListFileSerializer


class BlackListFileViewSet(viewsets.ModelViewSet):
    queryset = BlackListFile.objects.all()
    serializer_class = BlackListFileSerializer


class CommandViewSet(viewsets.ModelViewSet):
    queryset = Command.objects.all()
    serializer_class = CommandSerializer


# Routers provide an easy way of automatically determining the URL conf.
router = routers.DefaultRouter()
router.register(r'jobs', JobViewSet)
router.register(r'whitelistfiles', WhiteListFileViewSet)
router.register(r'blacklistfiles', BlackListFileViewSet)
router.register(r'commands', CommandViewSet)

urlpatterns = [
    url(r'^', include("core.urls")),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^api/', include(router.urls)),
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework'))
]
