---
title: Docker 容器化技术入门指南
date: 2024-01-25
tags:
  - Docker
  - 容器化
  - DevOps
  - Linux
category: 开发工具
status: published
aliases:
  - Docker入门
  - 容器化指南
---

# Docker 容器化技术入门指南

![封面图](https://cdn.example.com/docker_cover.jpg)

> [!abstract] 核心要点
> Docker 是一个开源的容器化平台,让应用部署变得简单高效。本文将介绍:
> - Docker 的核心概念和优势
> - 在不同平台上的安装配置
> - 基础命令和实战案例
> - 常见问题的排查方法

---

## 什么是 Docker

Docker 是一个开源的容器化平台,用于开发、交付和运行应用程序。它将应用及其依赖打包到一个轻量级、可移植的容器中,确保应用在任何环境中都能一致运行。

### 核心概念

**镜像 (Image)**
- 只读的模板,包含运行应用所需的一切
- 基于 Dockerfile 构建
- 可以继承和扩展

**容器 (Container)**
- 镜像的运行实例
- 轻量级、可隔离的进程
- 可以启动、停止、删除

**仓库 (Registry)**
- 存储和分发镜像的服务
- Docker Hub 是最大的公共仓库
- 可以搭建私有仓库

### 容器 vs 虚拟机

| 特性 | Docker 容器 | 虚拟机 |
|------|-----------|--------|
| **启动时间** | 秒级 | 分钟级 |
| **资源占用** | 共享宿主机内核, MB 级别 | 完整操作系统, GB 级别 |
| **隔离性** | 进程级隔离 | 硬件级隔离 |
| **性能** | 接近原生 | 有性能损耗 |
| **可移植性** | 跨平台一致 | 依赖虚拟化层 |

---

## 安装与配置

### 前置要求

- **操作系统**: Ubuntu 20.04+, macOS 12+, Windows 10+
- **架构**: x86_64 或 ARM64
- **资源**: 至少 4GB 内存, 20GB 可用磁盘空间
- **权限**: sudo 或管理员权限

### Ubuntu/Debian 安装

```bash
# 官方文档: https://docs.docker.com/engine/install/ubuntu/

# 1. 更新软件包索引
sudo apt update

# 2. 安装依赖
sudo apt install -y \
    apt-transport-https \
    ca-certificates \
    curl \
    gnupg \
    lsb-release

# 3. 添加 Docker 官方 GPG key
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | \
    sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg

# 4. 添加 Docker 仓库
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu \
  $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# 5. 安装 Docker Engine
sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin

# 6. 验证安装
docker --version
# 预期输出: Docker version 24.0.x, build xxxxx
```

### macOS 安装

```bash
# 方法 1: Homebrew (推荐)
brew install --cask docker

# 方法 2: 下载 Docker Desktop
# 访问: https://www.docker.com/products/docker-desktop/

# 启动 Docker Desktop 应用

# 验证安装
docker --version
docker run hello-world
```

### Windows 安装

```powershell
# 1. 启用 WSL 2
wsl --install

# 2. 下载并安装 Docker Desktop
# 访问: https://www.docker.com/products/docker-desktop/

# 3. 启动 Docker Desktop

# 4. 验证安装
docker --version
docker run hello-world
```

### 配置非 root 用户 (Linux)

```bash
# 将当前用户添加到 docker 组
sudo usermod -aG docker $USER

# 重新登录使更改生效
newgrp docker

# 验证: 无需 sudo 运行 docker 命令
docker ps
```

> [!tip] 最佳实践
> - 使用非 root 用户运行 Docker 提高安全性
> - 定期更新 Docker 到最新稳定版本
> - 配置镜像加速器提升下载速度

---

## 基础命令

![节奏图1: Docker 基础命令](https://cdn.example.com/docker_pic1.jpg)

### 镜像管理

```bash
# 搜索镜像
docker search nginx

# 拉取镜像
docker pull nginx:latest

# 列出本地镜像
docker images

# 删除镜像
docker rmi nginx:latest

# 构建镜像
docker build -t my-app:1.0 .

# 导出/导入镜像
docker save -o nginx.tar nginx:latest
docker load -i nginx.tar
```

### 容器管理

```bash
# 运行容器
docker run -d --name my-nginx -p 80:80 nginx:latest

# 参数说明:
# -d: 后台运行
# --name: 指定容器名称
# -p 80:80: 端口映射 (宿主机:容器)

# 列出运行中的容器
docker ps

# 列出所有容器 (包括已停止)
docker ps -a

# 停止容器
docker stop my-nginx

# 启动容器
docker start my-nginx

# 重启容器
docker restart my-nginx

# 删除容器
docker rm my-nginx

# 强制删除运行中的容器
docker rm -f my-nginx

# 查看容器日志
docker logs my-nginx
docker logs -f my-nginx  # 实时跟踪日志

# 进入容器
docker exec -it my-nginx bash

# 查看容器详情
docker inspect my-nginx

# 查看容器资源使用
docker stats my-nginx
```

---

## 实战案例

![节奏图2: 实战部署流程](https://cdn.example.com/docker_pic2.jpg)

### 案例 1: 部署 Nginx Web 服务器

**需求**: 快速部署一个 Nginx 服务器,托管静态网站

```bash
# 1. 创建项目目录
mkdir ~/nginx-demo && cd ~/nginx-demo

# 2. 创建网站内容
cat > index.html << 'EOF'
<!DOCTYPE html>
<html>
<head>
    <title>Docker Nginx Demo</title>
</head>
<body>
    <h1>Hello from Docker!</h1>
    <p>This is a static website served by Nginx in Docker.</p>
</body>
</html>
EOF

# 3. 运行 Nginx 容器, 挂载网站目录
docker run -d \
  --name nginx-web \
  -p 8080:80 \
  -v $(pwd):/usr/share/nginx/html:ro \
  nginx:latest

# 4. 访问网站
curl http://localhost:8080
# 或在浏览器打开 http://localhost:8080

# 5. 查看日志
docker logs nginx-web

# 6. 清理
docker stop nginx-web
docker rm nginx-web
```

**验证结果**:
```bash
$ curl http://localhost:8080
<!DOCTYPE html>
<html>
<head>
    <title>Docker Nginx Demo</title>
...
```

---

### 案例 2: 自定义 Nginx 镜像

**需求**: 构建包含自定义配置的 Nginx 镜像

**步骤 1: 创建项目结构**

```bash
mkdir ~/custom-nginx && cd ~/custom-nginx
mkdir -p html conf
```

**步骤 2: 创建网站内容**

```bash
cat > html/index.html << 'EOF'
<!DOCTYPE html>
<html>
<head>
    <title>Custom Nginx</title>
    <style>
        body { font-family: Arial; text-align: center; padding: 50px; }
        h1 { color: #0066cc; }
    </style>
</head>
<body>
    <h1>Custom Nginx Container</h1>
    <p>Built with Docker</p>
</body>
</html>
EOF
```

**步骤 3: 创建 Nginx 配置**

```bash
cat > conf/nginx.conf << 'EOF'
server {
    listen 80;
    server_name localhost;

    location / {
        root /usr/share/nginx/html;
        index index.html;
    }

    # 启用 gzip 压缩
    gzip on;
    gzip_types text/plain text/css application/json;
}
EOF
```

**步骤 4: 创建 Dockerfile**

```dockerfile
# 文件: Dockerfile
FROM nginx:1.25-alpine

# 维护者信息
LABEL maintainer="your-email@example.com"

# 复制自定义配置
COPY conf/nginx.conf /etc/nginx/conf.d/default.conf

# 复制网站文件
COPY html /usr/share/nginx/html

# 暴露端口
EXPOSE 80

# 启动 Nginx (继承自基础镜像)
CMD ["nginx", "-g", "daemon off;"]
```

**步骤 5: 构建和运行**

```bash
# 构建镜像
docker build -t custom-nginx:1.0 .

# 验证镜像
docker images | grep custom-nginx

# 运行容器
docker run -d --name my-custom-nginx -p 8081:80 custom-nginx:1.0

# 测试
curl http://localhost:8081

# 清理
docker stop my-custom-nginx
docker rm my-custom-nginx
```

> [!success] 成功部署
> 自定义 Nginx 镜像已成功构建和运行
> - 镜像大小: ~25MB (基于 Alpine)
> - 启动时间: < 1 秒
> - 内存占用: ~2MB

---

## Docker Compose 多容器应用

![节奏图3: Docker Compose 架构](https://cdn.example.com/docker_pic3.jpg)

### 案例: WordPress + MySQL

**创建 docker-compose.yml**:

```yaml
version: '3.8'

services:
  # MySQL 数据库
  db:
    image: mysql:8.0
    container_name: wordpress-db
    restart: always
    environment:
      MYSQL_ROOT_PASSWORD: example_root_password
      MYSQL_DATABASE: wordpress
      MYSQL_USER: wordpress
      MYSQL_PASSWORD: wordpress_password
    volumes:
      - db_data:/var/lib/mysql
    networks:
      - wordpress-network

  # WordPress 应用
  wordpress:
    image: wordpress:latest
    container_name: wordpress-app
    restart: always
    ports:
      - "8082:80"
    environment:
      WORDPRESS_DB_HOST: db:3306
      WORDPRESS_DB_USER: wordpress
      WORDPRESS_DB_PASSWORD: wordpress_password
      WORDPRESS_DB_NAME: wordpress
    volumes:
      - wp_data:/var/www/html
    depends_on:
      - db
    networks:
      - wordpress-network

volumes:
  db_data:
  wp_data:

networks:
  wordpress-network:
```

**启动应用**:

```bash
# 启动所有服务
docker compose up -d

# 查看运行状态
docker compose ps

# 查看日志
docker compose logs -f

# 停止所有服务
docker compose down

# 停止并删除数据
docker compose down -v
```

**访问**: http://localhost:8082

---

## 最佳实践

![节奏图4: Docker 最佳实践](https://cdn.example.com/docker_pic4.jpg)

### 镜像构建

1. **使用多阶段构建减小镜像体积**

```dockerfile
# 构建阶段
FROM node:18 AS builder
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build

# 运行阶段
FROM nginx:alpine
COPY --from=builder /app/dist /usr/share/nginx/html
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

2. **使用 .dockerignore 排除不必要文件**

```
# .dockerignore
node_modules
.git
.env
*.log
```

3. **优化层缓存**

```dockerfile
# ❌ 不好: 每次修改代码都会重新安装依赖
COPY . .
RUN npm install

# ✅ 好: 利用缓存, 仅在依赖变化时重新安装
COPY package*.json ./
RUN npm install
COPY . .
```

### 容器运行

1. **使用健康检查**

```yaml
services:
  web:
    image: nginx
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost"]
      interval: 30s
      timeout: 10s
      retries: 3
```

2. **设置资源限制**

```bash
docker run -d \
  --memory="512m" \
  --cpus="1.0" \
  --name limited-app \
  nginx
```

3. **使用环境变量配置**

```bash
docker run -d \
  -e DATABASE_URL=postgres://db:5432/mydb \
  -e API_KEY=secret \
  my-app
```

### 安全性

1. **不要以 root 用户运行**

```dockerfile
FROM node:18-alpine

# 创建非 root 用户
RUN addgroup -S appgroup && adduser -S appuser -G appgroup

# 设置工作目录和权限
WORKDIR /app
COPY --chown=appuser:appgroup . .

# 切换用户
USER appuser

CMD ["node", "server.js"]
```

2. **扫描镜像漏洞**

```bash
# 使用 Docker Scout (Docker Desktop 内置)
docker scout cves nginx:latest

# 或使用 Trivy
docker run aquasec/trivy image nginx:latest
```

---

## 常见问题

### Q1: Docker 容器无法启动

**症状**: `docker start` 命令执行后容器立即退出

**排查步骤**:

```bash
# 1. 查看容器退出状态
docker ps -a

# 2. 查看容器日志
docker logs container_name

# 3. 查看详细错误信息
docker inspect container_name | grep -A 10 State
```

**常见原因**:
- 容器内主进程退出
- 端口冲突
- 挂载目录权限问题
- 配置文件错误

**解决方案**:

```bash
# 使用交互模式调试
docker run -it --entrypoint /bin/sh image_name

# 检查端口占用
sudo lsof -i :80

# 修复目录权限
sudo chown -R $USER:$USER /path/to/volume
```

---

### Q2: 无法连接到容器内的服务

**症状**: 从宿主机无法访问容器内运行的服务

**排查步骤**:

```bash
# 1. 检查端口映射
docker ps

# 2. 检查容器内服务是否运行
docker exec container_name netstat -tlnp

# 3. 测试容器内部连接
docker exec container_name curl localhost:80

# 4. 检查防火墙规则
sudo iptables -L -n
```

**解决方案**:

```bash
# 确保正确映射端口
docker run -d -p 8080:80 nginx

# 确保服务监听 0.0.0.0 而不是 127.0.0.1

# 检查 Docker 网络
docker network inspect bridge
```

---

### Q3: 磁盘空间不足

**症状**: `no space left on device` 错误

**排查磁盘使用**:

```bash
# 查看 Docker 磁盘使用
docker system df

# 详细信息
docker system df -v
```

**清理方案**:

```bash
# 清理未使用的容器
docker container prune

# 清理未使用的镜像
docker image prune -a

# 清理未使用的卷
docker volume prune

# 清理构建缓存
docker builder prune

# 一键清理所有未使用资源
docker system prune -a --volumes
```

> [!warning] 注意
> `docker system prune -a --volumes` 会删除所有未使用的资源,包括停止的容器、未使用的镜像和卷。执行前请确认数据已备份。

---

### Q4: 容器性能问题

**症状**: 容器运行缓慢或响应延迟

**性能分析**:

```bash
# 查看容器资源使用
docker stats

# 查看容器进程
docker top container_name

# 查看容器事件
docker events --filter container=container_name
```

**优化建议**:

1. **资源限制**
```bash
docker update --memory="1g" --cpus="2" container_name
```

2. **使用高性能存储驱动**
```bash
# 检查当前驱动
docker info | grep "Storage Driver"

# 推荐使用 overlay2
```

3. **优化网络**
```bash
# 使用 host 网络模式 (生产环境慎用)
docker run --network host nginx
```

---

## 参考链接

- **Docker 官方文档**: https://docs.docker.com/
- **Docker Hub**: https://hub.docker.com/
- **Dockerfile 最佳实践**: https://docs.docker.com/develop/develop-images/dockerfile_best-practices/
- **Docker Compose 文档**: https://docs.docker.com/compose/
- **Docker 安全指南**: https://docs.docker.com/engine/security/

---

**标签**: #Docker #容器化 #DevOps #Linux

**更新日期**: 2024-01-25
