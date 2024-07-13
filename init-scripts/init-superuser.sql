-- 創建超級用戶
CREATE USER example_user WITH PASSWORD '123456' SUPERUSER;

-- 創建數據庫
CREATE DATABASE memory_agent;

-- 授予用戶在 public schema 上的所有權限
GRANT ALL PRIVILEGES ON SCHEMA public TO example_user;

-- 授予用戶在 memory_agent 數據庫上的所有權限
GRANT ALL PRIVILEGES ON DATABASE memory_agent TO example_user;