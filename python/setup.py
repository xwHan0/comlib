from setuptools import setup

setup(
    name='comlib',
    version='1.0.1',
    description='Common Extent Library',
    author='Leo.xwHan',
    author_email='xwhan_@163.com',
    maintainer='',
    maintainer_email='',
    url='',
    packages=[
        'comlib', 
         'comlib.ex',
    ],
    package_dir={
        'comlib':'comlib',
        'comlib.ex':'comlib/ex',
    },
    long_description="",
    license='Public domain',
    platforms=['any']
)