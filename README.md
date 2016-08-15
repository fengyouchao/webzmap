# WebZmap

**WebZmap** 是一个通过web方式管理运行zmap扫描任务， 并提供 **RESTful API** 方便第三方程序调用控制zmap任务

目前该项目还在开发中,很多功能待完善, 由于个人时间精力有限, 开发进度有点慢, 有兴趣的朋友可以fork, 并给我PR

# Goal

1. 通过Web管理zmap任务(70%)
2. 通过RESTful API为第三方程序提供接口(60%)
3. 分布式扫描(0%)

# Dependency

1. zmap
2. Python 2.7
3. django 1.10
4. django-crontab 0.7.1
5. requests 2.9.1
6. djangorestframework 3.4.4

# Install

安装 *zmap*, 安装方式请查看[zmap官方文档](https://zmap.io/download.html)

克隆项目

```shell
git clone https://github.com/fengyouchao/webzmap
```

安装依赖

```shell
cd webzmap
sudo -H pip install -r requirments.txt
```

初始化

```shell
python manage.py migrate #创建数据库
python manage.py createsuperuser #创建系统用户
sudo python manage.py crontab add #添加用于执行zmap任务的crontab任务，必须以root权限执行
```

确认zmap执行路径
```shell
where zmap
```
**WebZmap** 默认的zmap执行路径为 `/usr/local/sbin/zmap` 如果 `where zmap` 的路径不是该值, 编辑 `webzmap/settings.py` 找到以下内容并修改 `PATH`值
```python
ZMAP = {
    "PATH": "/usr/local/sbin/zmap",
    "CWD": WORK_DIR,
    "MAX_BANDWIDTH": 100,
    "DEFAULT_BANDWIDTH": 1,
}
```

运行

```shell
python manage.py runserver
```

访问 `http://localhost:8000`

# FAQ

1. 提交任务后任务一直处于Pending状态

由于 **WebZmap** 通过crontab检查新任务并执行, crontab最小执行周期为1分钟, 任务创建后, 会在一分钟以内自动执行。如果超过一分钟后任务仍然为Pending状态, 可能是您没有添加crontab任务, 请执行以下命令添加crontab任务

```shell
sudo python manage.py crontab add
```