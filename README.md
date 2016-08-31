![WebZmap](http://www.webzmap.com/images/webzmap.png "WebZmap")

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
4. requests 2.9.1
5. djangorestframework 3.4.4

# Install

1. 安装 *zmap*, 安装方式请查看[zmap官方文档](https://zmap.io/download.html)

2. 克隆项目

    ```shell
    git clone https://github.com/fengyouchao/webzmap
    ```

3. 安装依赖

    ```shell
    cd webzmap
    sudo -H pip install -r requirments.txt
    ```

4. 初始化

    ```shell
    python manage.py migrate #创建数据库
    python manage.py createsuperuser #创建系统用户
    sudo python manage.py zmapd start #启动用于执行zmap任务的zmapd服务，必须以root权限执行
    ```

5. 确认zmap执行路径
    ```shell
    where zmap
    ```
    **WebZmap** 默认的zmap执行路径为 `/usr/local/sbin/zmap` 如果 `where zmap` 的路径不是该值, 编辑 `webzmap/settings.py`, 在文件最后添加以下内容:
    ```python
    ZMAP_PATH = 'your zmap bin path'
    ```

6. 运行

    ```shell
    python manage.py runserver #请勿在生产环境使用此方式运行
    ```

    访问 `http://localhost:8000`

# Deploy

如果要在生产环境中部署webzmap, 可以通过以下步骤完成:

1. 编辑`webzmap/settings.py`在文件最后添加以下内容

    ```python
    DEBUG = False
    ALLOWED_HOSTS = ['*'] # 设置允许访问该站点的host, * 表示任意host, 如果您希望只能通过域名访问,在这里设置域名
    ```

2. 查看[Deploying Django](https://docs.djangoproject.com/en/1.10/howto/deployment/)

# FAQ

1. 提交任务后任务一直处于Pending状态

    请检查是否启动了zmapd服务

    ```shell
    sudo python manage.py zmapd status
    ```

    启动zmapd
    ```shell
    sudo python manage.py zmapd start
    ```

2. 执行日志显示`[FATAL] csv: could not open output file (xxx/webzmap/workspace/xxx/status.txt)`

    目前测试发现，这应该是zmap的一个bug，测试版本号为`2.1.1`, 在指定`-u`参数时，有一定概率发生此问题，目前解决办法为重新创建任务。
