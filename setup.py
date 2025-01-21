from setuptools import setup, find_packages

setup(
    name="medicai",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "fastapi",
        "sqlalchemy",
        "alembic",
        "psycopg2-binary",
    ],
)
