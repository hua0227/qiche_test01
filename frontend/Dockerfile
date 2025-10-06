FROM nginx:alpine

# 1. 移除 Nginx 默认配置（避免冲突）
RUN rm /etc/nginx/conf.d/default.conf

# 2. 复制自定义 Nginx 配置到容器（关键步骤）
COPY nginx.conf /etc/nginx/conf.d/

# 3. 复制前端所有静态文件到 Nginx 静态目录
COPY . /usr/share/nginx/html

EXPOSE 8080:80