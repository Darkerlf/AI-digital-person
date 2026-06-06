"""初始化数据库：建表 + 创建默认管理员账号
运行: python init_db.py
"""
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from app.core.database import engine, SessionLocal, Base
from app.models import load_all_models
from app.models.admin_user import AdminUser
from app.core.security import hash_password


def main():
    print("正在加载模型...")
    load_all_models()

    print("正在创建数据表...")
    Base.metadata.create_all(bind=engine)
    print("数据表创建完成。")

    db = SessionLocal()
    try:
        existing = db.query(AdminUser).filter(AdminUser.username == "admin").first()
        if existing:
            print("默认管理员 'admin' 已存在，跳过创建。")
        else:
            admin = AdminUser(
                username="admin",
                password_hash=hash_password("admin123"),
                role="super_admin",
                status="active",
            )
            db.add(admin)
            db.commit()
            print("默认管理员创建成功：admin / admin123")
    finally:
        db.close()

    print("初始化完成！")


if __name__ == "__main__":
    main()
