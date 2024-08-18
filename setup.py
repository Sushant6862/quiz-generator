from setuptools import find_packages,setup

setup(
    name='mcqgenrator',
    version='0.0.1',
    author='Sushant Dongare',
    author_email='sushantdongare11@gmail.com',
    install_requires=["openai","langchain","streamlit","python-dotenv","PyPDF2","Groq"],
    packages=find_packages()
)