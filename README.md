# web-ssh
### 使用说明

0. 前置条件

- 没有安装docker，使用本地数据库与内存缓存，在django配置文件中修改
- 安装docker，使用mysql与redis，无需修改，只需要在docker-compose中运行对应容器

1. 项目目录

```bash
cd .../web-ssh
```

2. 初始化前端

```bash
cd frontend
```

```bash
npm init
```

```bash
npm install
```

3. 启动前端开发服务器

```bash
npm run dev
```

4. 回到项目目录

```bash
cd .../web-ssh
```

5. 初始化后端

```bash
pip install -r requirement.txt
```

```bash
python manage.py makemigrations
python manage.py migrate
```

6. 启动后端服务器

```
python manage.py runserver
```

